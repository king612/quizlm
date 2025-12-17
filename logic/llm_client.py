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
                model="claude-3-5-sonnet-latest",
                max_tokens=5000,
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
            Dictionary with quiz questions and answers
        """
        prompt = f"""You are an expert quiz generator. Create a fill-in-the-blank quiz from the following source material.

SOURCE MATERIAL:
{source_content[:3000]}  # Limit to avoid token limits

STYLE GUIDELINES:
{json.dumps(style_info, indent=2)}

DIFFICULTY: {difficulty}

REQUIREMENTS:
1. Create fill-in-the-blank questions by replacing key words with blanks
2. Each blank should be underscores matching the word length
3. For hints, you may include first/last letters based on difficulty:
   - Easy: More hints (1-2 starting letters), fewer blanks overall
   - Medium: Occasional first letter hints, moderate number of blanks
   - Hard: Few or no hints, more blanks
4. Never blank out: articles (a, an, the), prepositions, conjunctions, or meaningless common words
5. Prioritize blanking: nouns with semantic meaning, key concepts, technical terms, important verbs/adjectives
6. Never blank words in headings or titles
7. For each blank, provide the answer

Return a JSON object with this structure:
{{
  "quiz_title": "Quiz title based on content",
  "questions": [
    {{
      "text": "The ___ is the powerhouse of the cell.",
      "blank_word": "mitochondria",
      "hint_letters": "m",
      "answer": "mitochondria",
      "position": "word position in original text"
    }}
  ]
}}

Generate a high-quality, educationally valuable quiz. Return ONLY the JSON object."""

        if self.provider == "claude":
            response = self.client.messages.create(
                model="claude-3-5-sonnet-latest",
                max_tokens=4000,
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
            raise ValueError(f"Failed to parse LLM response as JSON: {e}\nResponse: {content[:500]}")

