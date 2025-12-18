"""
LLM client for quiz generation and training image analysis
"""

from pathlib import Path
from typing import Dict, List, Optional
import base64
import json

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import httpx
except ImportError:
    httpx = None

from config import Config


class LLMClient:
    """Client for interacting with LLM services (Claude, OpenAI)"""

    def __init__(self, config: Config, proxies: Optional[Dict] = None):
        self.config = config
        self.provider = config.llm_provider
        self.proxies = proxies

        # Create http_client with proxies if needed
        http_client = None
        if proxies:
            if httpx is None:
                raise ImportError("httpx not installed. Install with: pip install httpx")
            http_client = httpx.Client(proxy=proxies)

        # Initialize appropriate client
        if self.provider == "claude":
            if Anthropic is None:
                raise ImportError("anthropic not installed. Install with: pip install anthropic")
            client_kwargs = {"api_key": config.anthropic_api_key}
            if http_client:
                client_kwargs["http_client"] = http_client
            self.client = Anthropic(**client_kwargs)
        elif self.provider == "openai":
            if OpenAI is None:
                raise ImportError("openai not installed. Install with: pip install openai")
            client_kwargs = {"api_key": config.openai_api_key}
            if http_client:
                client_kwargs["http_client"] = http_client
            self.client = OpenAI(**client_kwargs)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def _extract_json_from_response(self, text: str) -> dict:
        """Extract and parse JSON from LLM response text.

        Args:
            text: Response text that may contain JSON

        Returns:
            Parsed JSON dictionary

        Raises:
            json.JSONDecodeError: If JSON parsing fails
        """
        # Extract JSON if embedded in markdown code block
        if "```json" in text:
            json_start = text.find("```json") + 7
            json_end = text.find("```", json_start)
            text = text[json_start:json_end].strip()
        else:
            # Look for JSON object by finding first { and last }
            first_brace = text.find("{")
            last_brace = text.rfind("}")

            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                text = text[first_brace:last_brace + 1].strip()

        return json.loads(text)

    def analyze_quiz_image(self, image_path: Path) -> dict:
        """
        Analyze a handwritten quiz image to extract style information

        Args:
            image_path: Path to quiz image

        Returns:
            Dictionary with style analysis
        """
        # Read and encode image
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')

        # Determine image type
        ext = image_path.suffix.lower()
        media_type = f"image/{'jpeg' if ext in ['.jpg', '.jpeg'] else 'png'}"

        prompt = """Analyze this handwritten quiz image and extract the following information:

1. Overall format/layout (single column, two-column with answers, etc.)
2. How blanks are formatted (underscores, length of blanks)
3. Hint patterns (are first letters provided? ending letters? which words get hints?)
4. Word selection (what types of words are blanked out vs shown in full?)
5. Difficulty indicators you can observe
6. Any other stylistic patterns

Return your analysis as a structured JSON with these keys:
- layout_format
- blank_style
- hint_patterns
- word_selection_rules
- difficulty_markers
- other_observations

Be specific and detailed. This information will be used to generate new quizzes in the same style."""

        if self.provider == "claude":
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",  # Using Haiku - upgrade account for Sonnet/Opus
                max_tokens=4000,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }]
            )

            analysis_text = response.content[0].text

        elif self.provider == "openai":
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{image_data}"
                            }
                        }
                    ]
                }],
                max_tokens=2000
            )

            analysis_text = response.choices[0].message.content

        # Try to parse as JSON, fallback to text
        try:
            return self._extract_json_from_response(analysis_text)
        except json.JSONDecodeError:
            # Return as raw text if not valid JSON
            return {"raw_analysis": analysis_text}

    def generate_quiz_content(
        self,
        source_content: str,
        difficulty: str,
        style_info: dict
    ) -> dict:
        """
        Generate quiz content from source material

        Args:
            source_content: The text content to create quiz from
            difficulty: Easy, Medium, or Hard
            style_info: Style information from training

        Returns:
            Dictionary with quiz paragraphs and answer key
        """
        # Validate source content
        if not source_content or not source_content.strip():
            raise ValueError("Source content is empty or invalid")

        # Calculate max tokens based on content length
        # Claude 3 Haiku limit: 4096 tokens output
        # Claude 3.5 Sonnet limit: 8192 tokens output (when account upgraded)
        # Need headroom for JSON structure, so use conservative estimate
        content_length = len(source_content)

        # For Haiku with 4K limit, be very conservative
        # Rule of thumb: ~4 chars per token, plus JSON overhead
        estimated_tokens_needed = int(content_length / 3) + 500  # +500 for JSON structure
        max_tokens = min(4096, max(2000, estimated_tokens_needed))

        # Warn if content might be too large
        if estimated_tokens_needed > 3800:
            print(f"WARNING: Source document is large ({content_length} chars). Output may be truncated.")
            print(f"Consider using a shorter document or upgrading to Claude 3.5 Sonnet (8K output limit).")

        print(f"Generating quiz with max_tokens={max_tokens} for content length={content_length}")

        prompt = f"""You are a quiz generator that creates cloze-deletion study materials. Your task is to transform the ENTIRE source document into a quiz version by strategically blanking out key terms throughout.

SOURCE MATERIAL:
{source_content}

STYLE GUIDELINES:
{json.dumps(style_info, indent=2)}

DIFFICULTY: {difficulty}

CRITICAL REQUIREMENTS:
1. REPLICATE THE ENTIRE SOURCE DOCUMENT - Your output should be a full-text version of the source with blanks inserted
2. PRESERVE STRUCTURE - Keep all paragraphs, sections, headings, and organization from the original
3. PRESERVE FORMATTING - Maintain line breaks, paragraph breaks, lists, and document flow
4. DO NOT SUMMARIZE - Include all content from the source, not just selected portions
5. DO NOT NUMBER AS QUESTIONS - This is continuous text with blanks, not a numbered question list

BLANKING STRATEGY:
- Easy: Blank ~10-15% of key terms, ALWAYS provide 1-2 hint letters (first or last)
- Medium: Blank ~15-25% of key terms, provide hints for ~50% of blanks
- Hard: Blank ~25-35% of key terms, provide hints for ~20% of blanks

WHAT TO BLANK:
✓ Technical terms and vocabulary
✓ Key concepts and important nouns
✓ Significant verbs and descriptive adjectives
✓ Names of people, places, processes
✓ Numbers and quantities (when meaningful)

NEVER BLANK:
✗ Articles (a, an, the)
✗ Common prepositions (in, on, at, to, from)
✗ Common conjunctions (and, but, or)
✗ Structural words with no semantic meaning
✗ Headings or section titles (keep these intact for structure)

BLANK FORMAT - VERY IMPORTANT:
- Use TWO underscores per missing letter for handwriting space
- Short words (3-5 letters): "______" to "__________" (6-10 underscores)
- Medium words (6-8 letters): "____________" to "________________" (12-16 underscores)
- Long words (9+ letters): "________________" or longer (18+ underscores)
- For hints, keep the hint letter(s) and use underscores for the rest:
  * "m__________" (for "mitochondria" with first letter hint)
  * "__________a" (for "mitochondria" with last letter hint)
  * "c____________x" (for "complex" with first and last letters)
- DO NOT use just "___" for any word - blanks must be proportional to word length

Return a JSON object with this structure:
{{
  "quiz_title": "Title from source document",
  "paragraphs": [
    {{
      "text": "Full paragraph text with ___ inserted for blanked words. Keep all original sentences and structure.",
      "section_heading": "Section name if applicable, or null"
    }}
  ],
  "answer_key": [
    {{
      "answer": "the blanked word",
      "context": "brief surrounding text for context"
    }}
  ]
}}

IMPORTANT:
1. The paragraphs array should contain ALL content from the source document with blanks inserted throughout. Do not condense or summarize - replicate the full text.
2. Return ONLY the JSON object, with no explanatory text before or after it. Do not include phrases like "Here is..." or any other preamble."""

        if self.provider == "claude":
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",  # Using Haiku - upgrade account for Sonnet/Opus
                max_tokens=max_tokens,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            content = response.content[0].text

        elif self.provider == "openai":
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                max_tokens=4000
            )

            content = response.choices[0].message.content

        # Parse JSON response
        try:
            return self._extract_json_from_response(content)
        except json.JSONDecodeError as e:
            # Check if response was likely truncated (multiple indicators)
            is_truncated = (
                len(content) > 2500 or  # Substantial response
                not content.rstrip().endswith("}") or  # Doesn't end with closing brace
                '"answer_key"' not in content  # Missing expected key
            )

            if is_truncated:
                raise ValueError(
                    f"❌ OUTPUT TRUNCATED - Document Too Large\n\n"
                    f"The quiz generation hit Claude Haiku's 4,096 token output limit.\n"
                    f"Your source content was too large to generate a complete quiz.\n\n"
                    f"📏 RECOMMENDED LIMITS:\n"
                    f"  • For pasted text: ~2,500-3,000 characters (≈ 1-2 pages)\n"
                    f"  • For PDF files: 2-3 pages maximum\n\n"
                    f"💡 SOLUTIONS:\n"
                    f"  1. Reduce your source content by 30-50%\n"
                    f"  2. Split into multiple smaller sections\n"
                    f"  3. Use Easy difficulty (fewer blanks = less output)\n"
                    f"  4. Wait for Claude 3.5 Sonnet access (2x capacity)\n\n"
                    f"Technical: Hit {max_tokens} token limit\n"
                    f"Error: {e}"
                )
            else:
                raise ValueError(f"Failed to parse LLM response as JSON: {e}\nResponse: {content[:500]}")

