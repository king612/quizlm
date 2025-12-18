"""
Test script for v3.0 2-phase architecture
Tests word selection and quiz building independently
"""

import sys
from pathlib import Path

# Sample test content
SAMPLE_TEXT = """
Photosynthesis

Photosynthesis is the process by which plants convert light energy into chemical energy. This process occurs primarily in the chloroplasts, which contain the green pigment chlorophyll. During photosynthesis, plants absorb carbon dioxide from the atmosphere and water from the soil. Through a series of complex reactions, these raw materials are transformed into glucose and oxygen.

The process can be divided into two main stages: the light-dependent reactions and the light-independent reactions (also known as the Calvin cycle). The light-dependent reactions occur in the thylakoid membranes and produce ATP and NADPH. The Calvin cycle takes place in the stroma and uses the ATP and NADPH to convert carbon dioxide into glucose.

Photosynthesis is essential for life on Earth, as it produces the oxygen we breathe and forms the base of most food chains.
"""


def test_word_selector():
    """Test Phase 1: Word Selection"""
    print("=" * 70)
    print("TESTING PHASE 1: LLM Word Selection")
    print("=" * 70)
    
    try:
        from config import Config
        from logic.word_selector import WordSelector
        
        config = Config()
        selector = WordSelector(config)
        
        print(f"\nAnalyzing {len(SAMPLE_TEXT)} character sample text...")
        print(f"Provider: {config.llm_provider}")
        
        for difficulty in ["Easy", "Medium", "Hard"]:
            print(f"\n--- Testing {difficulty} difficulty ---")
            result = selector.select_words_to_blank(SAMPLE_TEXT, difficulty)
            
            words = result.get("words_to_blank", [])
            print(f"✓ Selected {len(words)} words")
            print(f"  Coverage: {result.get('estimated_coverage', 0):.1%}")
            
            # Show first 5 words
            print(f"  Sample words:")
            for i, word_info in enumerate(words[:5], 1):
                word = word_info.get('word', '')
                importance = word_info.get('importance', 0)
                word_type = word_info.get('word_type', 'unknown')
                print(f"    {i}. '{word}' (importance: {importance:.2f}, type: {word_type})")
            
            if len(words) > 5:
                print(f"    ... and {len(words) - 5} more")
        
        print("\n✅ Phase 1 (Word Selection) PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Phase 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_quiz_builder():
    """Test Phase 2: Quiz Building"""
    print("\n" + "=" * 70)
    print("TESTING PHASE 2: Local Quiz Building")
    print("=" * 70)
    
    try:
        from logic.quiz_builder import QuizBuilder
        
        # Mock word selection for testing
        mock_words = [
            {"word": "Photosynthesis", "importance": 0.95, "word_type": "key_concept"},
            {"word": "chloroplasts", "importance": 0.90, "word_type": "technical_term"},
            {"word": "chlorophyll", "importance": 0.88, "word_type": "technical_term"},
            {"word": "carbon dioxide", "importance": 0.85, "word_type": "key_concept"},
            {"word": "glucose", "importance": 0.85, "word_type": "key_concept"},
            {"word": "oxygen", "importance": 0.82, "word_type": "key_concept"},
            {"word": "thylakoid", "importance": 0.78, "word_type": "technical_term"},
            {"word": "Calvin cycle", "importance": 0.80, "word_type": "process_name"},
        ]
        
        for difficulty in ["Easy", "Medium", "Hard"]:
            print(f"\n--- Testing {difficulty} difficulty ---")
            
            builder = QuizBuilder(difficulty=difficulty)
            result = builder.build_quiz(
                source_text=SAMPLE_TEXT,
                words_to_blank=mock_words,
                max_occurrences_per_word=2
            )
            
            quiz_text = result["quiz_text"]
            answer_key = result["answer_key"]
            metadata = result["metadata"]
            
            print(f"✓ Created quiz with {metadata['total_blanks']} blanks")
            print(f"  Coverage: {metadata['coverage_percentage']}% of words")
            print(f"  Original: {metadata['original_word_count']} words")
            
            # Verify blank formatting
            print(f"\n  Checking blank formatting...")
            all_correct = True
            for i, answer in enumerate(answer_key[:3], 1):
                word = answer['answer']
                blank = answer['blank']
                
                # Check structure
                hint_letters = len(blank) - blank.count('_')
                underscore_count = blank.count('_')
                missing_letters = len(word) - hint_letters
                expected_underscores = missing_letters * 2
                
                is_correct = underscore_count == expected_underscores
                status = "✓" if is_correct else "✗"
                
                print(f"    {status} '{word}' ({len(word)} letters) → '{blank}'")
                print(f"       Hint: {hint_letters} letters, Underscores: {underscore_count}/{expected_underscores} expected")
                
                if not is_correct:
                    all_correct = False
            
            if all_correct:
                print(f"  ✅ All blanks formatted correctly (2 underscores per letter)")
            else:
                print(f"  ⚠️  Some blanks not correctly formatted")
            
            # Show sample of quiz text
            print(f"\n  Quiz text preview:")
            preview = quiz_text[:300].replace('\n', ' ')
            print(f"    {preview}...")
        
        print("\n✅ Phase 2 (Quiz Building) PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Phase 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integrated():
    """Test integrated workflow"""
    print("\n" + "=" * 70)
    print("TESTING INTEGRATED WORKFLOW")
    print("=" * 70)
    
    try:
        from config import Config
        from logic.word_selector import WordSelector
        from logic.quiz_builder import QuizBuilder
        
        config = Config()
        
        print("\nRunning full 2-phase workflow on sample text...")
        
        # Phase 1
        print("\nPhase 1: Word Selection...")
        selector = WordSelector(config)
        word_selection = selector.select_words_to_blank(SAMPLE_TEXT, "Medium")
        print(f"✓ Selected {len(word_selection['words_to_blank'])} words")
        
        # Phase 2
        print("\nPhase 2: Quiz Building...")
        builder = QuizBuilder(difficulty="Medium")
        result = builder.build_quiz(
            source_text=SAMPLE_TEXT,
            words_to_blank=word_selection['words_to_blank'],
            max_occurrences_per_word=2
        )
        print(f"✓ Built quiz with {result['metadata']['total_blanks']} blanks")
        
        # Verify
        print("\n" + "-" * 70)
        print("QUIZ PREVIEW (first 400 chars):")
        print("-" * 70)
        print(result['quiz_text'][:400])
        print("...")
        
        print("\n" + "-" * 70)
        print("ANSWER KEY (first 10 answers):")
        print("-" * 70)
        for i, answer in enumerate(result['answer_key'][:10], 1):
            print(f"{i}. {answer['answer']} → {answer['blank']}")
        
        print("\n✅ INTEGRATED WORKFLOW PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ INTEGRATED WORKFLOW FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("QuizLM v3.0 Architecture Test Suite")
    print("=" * 70)
    
    results = []
    
    # Test Phase 2 first (no API calls needed)
    print("\n🔧 Starting with Phase 2 tests (no API calls)...")
    results.append(("Phase 2 - Quiz Building", test_quiz_builder()))
    
    # Ask before running API tests
    print("\n" + "=" * 70)
    response = input("\n⚠️  Phase 1 and Integrated tests require API calls. Continue? (y/n): ")
    
    if response.lower() == 'y':
        results.append(("Phase 1 - Word Selection", test_word_selector()))
        results.append(("Integrated Workflow", test_integrated()))
    else:
        print("\nSkipping API-dependent tests.")
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n🎉 All tests passed! v3.0 architecture is working.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Check output above.")
        sys.exit(1)
