"""
Initial Indexing Script
Performs first-time analysis of all existing transcripts
"""
import os
import sys
from dotenv import load_dotenv
from transcript_parser import TranscriptParser
from ai_analyzer import AIAnalyzer
from insights_manager import InsightsManager

# Load environment variables
load_dotenv()


def initial_indexing():
    """
    Perform initial analysis of all transcripts in the Transcripts/ folder
    This creates the baseline master_insights.md file
    """
    print("=" * 70)
    print("INITIAL INDEXING - UX Transcript Analysis System")
    print("=" * 70)
    print()
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY') and not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ ERROR: No API key found!")
        print("Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env file")
        return False
    
    # Initialize components
    print("Initializing components...")
    transcript_parser = TranscriptParser(transcripts_dir="../Transcripts")
    ai_analyzer = AIAnalyzer(provider=os.getenv('AI_PROVIDER', 'openai'))
    insights_manager = InsightsManager(insights_dir="../Insights")
    
    # List all transcripts
    print("\nScanning for transcripts...")
    transcripts = transcript_parser.list_transcripts()
    
    if len(transcripts) == 0:
        print("⚠️  No transcripts found in Transcripts/ folder")
        return False
    
    print(f"✓ Found {len(transcripts)} transcripts")
    print()
    
    # Confirm before proceeding
    print("This will analyze all transcripts using AI API.")
    print(f"Estimated time: {len(transcripts) * 0.5:.0f} minutes")
    print(f"Estimated cost: ${len(transcripts) * 0.10:.2f} (approximate)")
    print()
    
    response = input("Proceed with initial indexing? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("Indexing cancelled.")
        return False
    
    print()
    print("=" * 70)
    print("STARTING BATCH ANALYSIS")
    print("=" * 70)
    print()
    
    # Parse all transcripts first
    print("Parsing all transcripts...")
    parsed_transcripts = []
    for i, transcript_meta in enumerate(transcripts, 1):
        print(f"  [{i}/{len(transcripts)}] Parsing: {transcript_meta['name']}")
        parsed = transcript_parser.parse_docx(transcript_meta['path'])
        
        if 'error' not in parsed:
            parsed_transcripts.append(parsed)
        else:
            print(f"    ⚠️  Error parsing: {parsed['error']}")
    
    print(f"✓ Successfully parsed {len(parsed_transcripts)} transcripts")
    print()
    
    # Analyze each transcript
    print("Analyzing transcripts with AI...")
    print("-" * 70)
    
    existing_insights = insights_manager.load_master_insights()
    successful_analyses = 0
    failed_analyses = 0
    
    for i, transcript in enumerate(parsed_transcripts, 1):
        print(f"\n[{i}/{len(parsed_transcripts)}] Analyzing: {transcript['respondent_name']}")
        print(f"  Words: {transcript['word_count']}")
        
        try:
            # Analyze with AI
            result = ai_analyzer.analyze_transcript(
                transcript_text=transcript['content'],
                respondent_name=transcript['respondent_name'],
                existing_insights=existing_insights,
                transcript_number=i,
                total_transcripts=len(parsed_transcripts)
            )
            
            if result['success']:
                print(f"  ✓ Analysis completed ({result['tokens_used']} tokens)")
                
                # Save individual report
                report_path = insights_manager.save_individual_report(
                    respondent_name=transcript['respondent_name'],
                    analysis=result['analysis'],
                    metadata={
                        'word_count': transcript['word_count'],
                        'tokens_used': result['tokens_used'],
                        'model': result['model']
                    }
                )
                print(f"  ✓ Report saved: {os.path.basename(report_path)}")
                
                # Update master insights
                insights_manager.update_master_insights(
                    new_analysis=result['analysis'],
                    respondent_name=transcript['respondent_name'],
                    transcript_number=i
                )
                print(f"  ✓ Master insights updated")
                
                # Update existing insights for next iteration
                existing_insights += f"\n\n{result['analysis']}"
                
                successful_analyses += 1
            else:
                print(f"  ❌ Analysis failed: {result['error']}")
                failed_analyses += 1
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            failed_analyses += 1
        
        print("-" * 70)
    
    # Final summary
    print()
    print("=" * 70)
    print("INDEXING COMPLETE")
    print("=" * 70)
    print()
    print(f"✓ Successful analyses: {successful_analyses}")
    if failed_analyses > 0:
        print(f"❌ Failed analyses: {failed_analyses}")
    print()
    
    # Show statistics
    stats = insights_manager.get_statistics()
    print("Final Statistics:")
    print(f"  Total interviews analyzed: {stats['total_interviews']}")
    print(f"  Reports generated: {stats['report_count']}")
    print(f"  Unique tags: {stats['unique_tags']}")
    print(f"  Master insights file size: {stats['master_file_size'] / 1024:.1f} KB")
    print()
    
    if len(stats['tags']) > 0:
        print("Top tags:")
        for tag in stats['tags'][:10]:
            print(f"  {tag}")
    
    print()
    print("✓ Initial indexing completed successfully!")
    print()
    print("You can now:")
    print("  1. Start the backend: cd backend && python app.py")
    print("  2. Open the frontend: open frontend/index.html")
    print("  3. Explore insights in the Insights/ folder")
    
    return True


if __name__ == "__main__":
    try:
        success = initial_indexing()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nIndexing interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
