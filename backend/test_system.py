"""
System Test Script
Tests all components of the UX Transcript Analysis System
"""
import os
from dotenv import load_dotenv
from transcript_parser import TranscriptParser
from ai_analyzer import AIAnalyzer
from insights_manager import InsightsManager

# Load environment variables
load_dotenv()


def test_transcript_parser():
    """Test the transcript parser"""
    print("\n" + "=" * 70)
    print("TEST 1: Transcript Parser")
    print("=" * 70)
    
    parser = TranscriptParser(transcripts_dir="../Transcripts")
    
    # Test listing transcripts
    print("\n1.1 Listing transcripts...")
    transcripts = parser.list_transcripts()
    print(f"✓ Found {len(transcripts)} transcripts")
    
    if len(transcripts) > 0:
        print(f"  First transcript: {transcripts[0]['name']}")
    
    # Test parsing a single transcript
    if len(transcripts) > 0:
        print("\n1.2 Parsing first transcript...")
        first = transcripts[0]
        parsed = parser.parse_docx(first['path'])
        
        if 'error' not in parsed:
            print(f"✓ Successfully parsed: {parsed['respondent_name']}")
            print(f"  Paragraphs: {parsed['paragraph_count']}")
            print(f"  Words: {parsed['word_count']}")
            print(f"  Characters: {parsed['char_count']}")
            print(f"  Content preview: {parsed['content'][:100]}...")
            return True
        else:
            print(f"❌ Error parsing: {parsed['error']}")
            return False
    else:
        print("⚠️  No transcripts available to test")
        return True


def test_insights_manager():
    """Test the insights manager"""
    print("\n" + "=" * 70)
    print("TEST 2: Insights Manager")
    print("=" * 70)
    
    manager = InsightsManager(insights_dir="../Insights")
    
    # Test loading master insights
    print("\n2.1 Loading master insights...")
    master = manager.load_master_insights()
    print(f"✓ Loaded master insights: {len(master)} characters")
    
    # Test getting statistics
    print("\n2.2 Getting statistics...")
    stats = manager.get_statistics()
    print(f"✓ Statistics retrieved:")
    print(f"  Total interviews: {stats['total_interviews']}")
    print(f"  Reports: {stats['report_count']}")
    print(f"  Unique tags: {stats['unique_tags']}")
    
    # Test saving a report
    print("\n2.3 Testing report save...")
    test_analysis = """
## Краткое резюме
Тестовый анализ для проверки системы.

## Боли пользователя
- Тестовая боль 1
- Тестовая боль 2

## Теги
#test #system_check #banking
"""
    
    report_path = manager.save_individual_report(
        respondent_name="Тестовый Пользователь",
        analysis=test_analysis,
        metadata={'test': True}
    )
    
    if report_path:
        print(f"✓ Test report saved: {os.path.basename(report_path)}")
        
        # Clean up test report
        if os.path.exists(report_path):
            os.remove(report_path)
            print(f"✓ Test report cleaned up")
        
        return True
    else:
        print("❌ Failed to save test report")
        return False


def test_ai_analyzer():
    """Test the AI analyzer (requires API key)"""
    print("\n" + "=" * 70)
    print("TEST 3: AI Analyzer")
    print("=" * 70)
    
    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY') or os.getenv('ANTHROPIC_API_KEY')
    
    if not api_key:
        print("⚠️  No API key found - skipping AI test")
        print("   To test AI: set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env")
        return True
    
    provider = os.getenv('AI_PROVIDER', 'openai')
    print(f"\n3.1 Initializing AI analyzer (provider: {provider})...")
    analyzer = AIAnalyzer(provider=provider)
    print("✓ AI analyzer initialized")
    
    # Test with sample transcript
    print("\n3.2 Testing AI analysis with sample text...")
    sample_transcript = """
    Интервьюер: Расскажите о вашем опыте использования мобильного банка.
    
    Респондент: Я пользуюсь приложением около полугода. В целом удобно, 
    но бывают проблемы с входом - часто просит повторно ввести пароль, 
    даже когда я только что заходил. Это раздражает. 
    
    Также не всегда понятно, куда нажимать для перевода денег. 
    Но когда разобрался, то всё быстро.
    """
    
    print("  Sending request to AI API...")
    print("  (This may take 10-30 seconds)")
    
    try:
        result = analyzer.analyze_transcript(
            transcript_text=sample_transcript,
            respondent_name="Тестовый респондент",
            existing_insights="",
            transcript_number=1,
            total_transcripts=1
        )
        
        if result['success']:
            print(f"✓ AI analysis completed")
            print(f"  Tokens used: {result['tokens_used']}")
            print(f"  Model: {result['model']}")
            print(f"  Analysis preview: {result['analysis'][:200]}...")
            return True
        else:
            print(f"❌ AI analysis failed: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Error during AI analysis: {str(e)}")
        return False


def test_integration():
    """Test full workflow integration"""
    print("\n" + "=" * 70)
    print("TEST 4: Full Integration Test")
    print("=" * 70)
    
    # Check if we have API key for full test
    api_key = os.getenv('OPENAI_API_KEY') or os.getenv('ANTHROPIC_API_KEY')
    
    if not api_key:
        print("⚠️  No API key - skipping integration test")
        return True
    
    print("\n4.1 Initializing all components...")
    parser = TranscriptParser(transcripts_dir="../Transcripts")
    analyzer = AIAnalyzer(provider=os.getenv('AI_PROVIDER', 'openai'))
    manager = InsightsManager(insights_dir="../Insights")
    print("✓ All components initialized")
    
    # Get a transcript
    print("\n4.2 Loading a transcript...")
    transcripts = parser.list_transcripts()
    
    if len(transcripts) == 0:
        print("⚠️  No transcripts available for integration test")
        return True
    
    first = transcripts[0]
    parsed = parser.parse_docx(first['path'])
    
    if 'error' in parsed:
        print(f"❌ Error parsing transcript: {parsed['error']}")
        return False
    
    print(f"✓ Loaded: {parsed['respondent_name']}")
    
    # Analyze it (use only first 1000 words to save tokens)
    print("\n4.3 Analyzing transcript (partial)...")
    words = parsed['content'].split()[:1000]
    partial_content = ' '.join(words)
    
    existing_insights = manager.load_master_insights()
    
    print("  Sending to AI...")
    result = analyzer.analyze_transcript(
        transcript_text=partial_content,
        respondent_name=parsed['respondent_name'] + " (Test)",
        existing_insights=existing_insights[:500],  # Limit context
        transcript_number=1,
        total_transcripts=1
    )
    
    if not result['success']:
        print(f"❌ Analysis failed: {result['error']}")
        return False
    
    print(f"✓ Analysis completed ({result['tokens_used']} tokens)")
    
    # Save report
    print("\n4.4 Saving test report...")
    report_path = manager.save_individual_report(
        respondent_name=parsed['respondent_name'] + " (Test)",
        analysis=result['analysis'],
        metadata={'test': True, 'tokens': result['tokens_used']}
    )
    
    print(f"✓ Report saved: {os.path.basename(report_path)}")
    
    # Clean up
    print("\n4.5 Cleaning up test files...")
    if os.path.exists(report_path):
        os.remove(report_path)
        print("✓ Test files cleaned up")
    
    print("\n✓ Integration test completed successfully!")
    return True


def run_all_tests():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "UX TRANSCRIPT ANALYSIS SYSTEM" + " " * 24 + "║")
    print("║" + " " * 23 + "System Tests" + " " * 33 + "║")
    print("╚" + "=" * 68 + "╝")
    
    tests = [
        ("Transcript Parser", test_transcript_parser),
        ("Insights Manager", test_insights_manager),
        ("AI Analyzer", test_ai_analyzer),
        ("Integration", test_integration)
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    for name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{status:10} {name}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready to use.")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total


if __name__ == "__main__":
    import sys
    
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
        sys.exit(1)
