"""
Quick test to reproduce the Agent-intro-1 quiz issue
"""

from config import Config
from logic.word_selector import WordSelector
from logic.quiz_builder import QuizBuilder

SOURCE_TEXT = """After a few years of prompt engineering being the focus of attention in applied AI, a new term has come to prominence: context engineering. Building with language models is becoming less about finding the right words and phrases for your prompts, and more about answering the broader question of "what configuration of context is most likely to generate our model's desired behavior?"

Context refers to the set of tokens included when sampling from a large-language model (LLM). The engineering problem at hand is optimizing the utility of those tokens against the inherent constraints of LLMs in order to consistently achieve a desired outcome. Effectively wrangling LLMs often requires thinking in context — in other words: considering the holistic state available to the LLM at any given time and what potential behaviors that state might yield."""

def test_agent_intro():
    print("=" * 80)
    print("TESTING AGENT-INTRO QUIZ GENERATION")
    print("=" * 80)
    print(f"\nSource text: {len(SOURCE_TEXT)} characters, {len(SOURCE_TEXT.split())} words")
    print(f"\nFirst 150 chars: {SOURCE_TEXT[:150]}...")

    try:
        config = Config()

        # Phase 1: Word Selection
        print("\n--- Phase 1: Word Selection ---")
        selector = WordSelector(config)
        word_selection = selector.select_words_to_blank(SOURCE_TEXT, "Medium")

        words = word_selection.get("words_to_blank", [])
        print(f"✓ Selected {len(words)} words")
        print(f"  Estimated coverage: {word_selection.get('estimated_coverage', 0):.1%}")

        print("\n  Selected words:")
        for i, word_info in enumerate(words, 1):
            word = word_info.get('word', '')
            importance = word_info.get('importance', 0)
            word_type = word_info.get('word_type', 'unknown')
            print(f"  {i:2d}. '{word}' (importance: {importance:.2f}, type: {word_type})")

        # Phase 2: Quiz Building
        print("\n--- Phase 2: Quiz Building ---")
        builder = QuizBuilder(difficulty="Medium")
        result = builder.build_quiz(
            source_text=SOURCE_TEXT,
            words_to_blank=words,
            max_occurrences_per_word=2
        )

        print(f"✓ Built quiz with {result['metadata']['total_blanks']} blanks")
        print(f"  Coverage: {result['metadata']['coverage_percentage']}% of words")

        # Show the quiz
        print("\n" + "=" * 80)
        print("GENERATED QUIZ:")
        print("=" * 80)
        print(result['quiz_text'])

        print("\n" + "=" * 80)
        print("ANSWER KEY:")
        print("=" * 80)
        for i, answer in enumerate(result['answer_key'], 1):
            word = answer['answer']
            blank = answer['blank']
            # Check format
            hint_count = len(blank) - blank.count('_')
            underscore_count = blank.count('_')
            expected = (len(word) - hint_count) * 2
            status = "✓" if underscore_count == expected else f"✗ (expected {expected})"

            print(f"{i:2d}. {word:20s} → {blank:30s} {status}")

    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_agent_intro()
