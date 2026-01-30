"""
Flask Application for UX Transcript Analysis System
Provides REST API for transcript management and AI analysis
"""
import os
import sys
import traceback
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from datetime import datetime

# Get the directory containing this script
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))

# Load environment variables from .env file in backend directory
env_path = os.path.join(BACKEND_DIR, '.env')
load_dotenv(env_path)

from transcript_parser import TranscriptParser
from ai_analyzer import AIAnalyzer
from insights_manager import InsightsManager

# Initialize Flask app with static folder for frontend
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend')
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Enable CORS for frontend
CORS(app)

# Configuration - use absolute paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRANSCRIPTS_DIR = os.path.join(BASE_DIR, 'Transcripts')
INSIGHTS_DIR = os.path.join(BASE_DIR, 'Insights')
AI_PROVIDER = os.getenv('AI_PROVIDER', 'openai')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o')

# Initialize components
transcript_parser = TranscriptParser(transcripts_dir=TRANSCRIPTS_DIR)
ai_analyzer = AIAnalyzer(provider=AI_PROVIDER)
insights_manager = InsightsManager(insights_dir=INSIGHTS_DIR)


# ============================================================================
# API Endpoints
# ============================================================================

@app.route('/')
def index():
    """Root endpoint - serve frontend"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api')
def api_info():
    """API info endpoint"""
    return jsonify({
        'app': 'UX Transcript Analysis System',
        'version': '1.0.0',
        'api_version': 'v1',
        'endpoints': {
            'transcripts': '/api/transcripts',
            'analyze': '/api/analyze',
            'insights': '/api/insights',
            'compare': '/api/compare',
            'statistics': '/api/statistics',
            'search': '/api/search'
        }
    })


@app.route('/api/transcripts', methods=['GET', 'POST'])
def transcripts():
    """
    GET: List all transcripts
    POST: Upload a new transcript
    """
    if request.method == 'GET':
        try:
            transcripts_list = transcript_parser.list_transcripts()
            return jsonify({
                'success': True,
                'count': len(transcripts_list),
                'transcripts': transcripts_list
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    elif request.method == 'POST':
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Empty filename'
            }), 400
        
        if not file.filename.endswith('.docx'):
            return jsonify({
                'success': False,
                'error': 'Only .docx files are supported'
            }), 400
        
        try:
            # Secure the filename
            filename = secure_filename(file.filename)
            
            # Save the file
            result = transcript_parser.save_transcript(file, filename)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'message': 'Transcript uploaded successfully',
                    'filename': filename,
                    'path': result['file_path']
                }), 201
            else:
                return jsonify(result), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500


@app.route('/api/transcripts/<name>', methods=['GET'])
def get_transcript(name):
    """Get a specific transcript by name"""
    try:
        transcript = transcript_parser.get_transcript_by_name(name)
        
        if transcript:
            return jsonify({
                'success': True,
                'transcript': transcript
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Transcript not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Analyze a transcript with AI
    
    Body parameters:
    - transcript_name: Name of transcript to analyze (without .docx)
    - depth: "quick" or "deep" (optional, default: "quick")
    """
    try:
        data = request.get_json()
        
        if not data or 'transcript_name' not in data:
            return jsonify({
                'success': False,
                'error': 'transcript_name is required'
            }), 400
        
        transcript_name = data['transcript_name']
        depth = data.get('depth', 'quick')
        
        print(f"[ANALYZE] Starting analysis for: {transcript_name}")
        
        # Parse the transcript
        transcript = transcript_parser.get_transcript_by_name(transcript_name)
        
        if not transcript or 'error' in transcript:
            error_msg = transcript.get('error', 'Unknown error') if transcript else 'Transcript not found'
            print(f"[ANALYZE] Transcript error: {error_msg}")
            return jsonify({
                'success': False,
                'error': f'Transcript not found or could not be parsed: {error_msg}'
            }), 404
        
        print(f"[ANALYZE] Transcript loaded, {transcript['word_count']} words")
        
        # Load existing insights for context
        existing_insights = insights_manager.load_master_insights()
        
        # Get current count
        stats = insights_manager.get_statistics()
        current_count = stats['total_interviews'] + 1
        
        print(f"[ANALYZE] Starting AI analysis with model: {OPENAI_MODEL}")
        print(f"[ANALYZE] API Key configured: {'Yes' if os.getenv('OPENAI_API_KEY') else 'NO!'}")
        
        # Analyze with AI
        analysis_result = ai_analyzer.analyze_transcript(
            transcript_text=transcript['content'],
            respondent_name=transcript['respondent_name'],
            existing_insights=existing_insights,
            transcript_number=current_count,
            total_transcripts=current_count,
            model=OPENAI_MODEL
        )
        
        if not analysis_result['success']:
            error_msg = analysis_result.get('error', 'Unknown AI error')
            print(f"[ANALYZE] AI Analysis failed: {error_msg}")
            return jsonify({
                'success': False,
                'error': f'AI Analysis error: {error_msg}'
            }), 500
        
        print(f"[ANALYZE] AI Analysis completed, {analysis_result['tokens_used']} tokens used")
        
        # Save individual report
        report_path = insights_manager.save_individual_report(
            respondent_name=transcript['respondent_name'],
            analysis=analysis_result['analysis'],
            metadata={
                'word_count': transcript['word_count'],
                'tokens_used': analysis_result['tokens_used'],
                'model': analysis_result['model']
            }
        )
        
        # Update master insights
        insights_manager.update_master_insights(
            new_analysis=analysis_result['analysis'],
            respondent_name=transcript['respondent_name'],
            transcript_number=current_count
        )
        
        print(f"[ANALYZE] Success! Report saved to: {report_path}")
        
        return jsonify({
            'success': True,
            'analysis': analysis_result['analysis'],
            'report_path': report_path,
            'tokens_used': analysis_result['tokens_used'],
            'model': analysis_result['model'],
            'timestamp': analysis_result['timestamp']
        })
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"[ANALYZE] Exception occurred: {str(e)}")
        print(f"[ANALYZE] Traceback:\n{error_trace}")
        return jsonify({
            'success': False,
            'error': f'{str(e)}'
        }), 500


@app.route('/api/analyze/batch', methods=['POST'])
def analyze_batch():
    """
    Analyze multiple transcripts in batch
    
    Body parameters:
    - transcript_names: List of transcript names (without .docx)
    """
    try:
        data = request.get_json()
        
        if not data or 'transcript_names' not in data:
            return jsonify({
                'success': False,
                'error': 'transcript_names array is required'
            }), 400
        
        transcript_names = data['transcript_names']
        
        # Parse all transcripts
        transcripts = []
        for name in transcript_names:
            transcript = transcript_parser.get_transcript_by_name(name)
            if transcript and 'error' not in transcript:
                transcripts.append(transcript)
        
        # Load existing insights
        existing_insights = insights_manager.load_master_insights()
        
        # Batch analyze
        results = ai_analyzer.batch_analyze(transcripts, existing_insights)
        
        # Save all reports and update master
        saved_reports = []
        stats = insights_manager.get_statistics()
        count = stats['total_interviews']
        
        for result in results:
            if result['success']:
                count += 1
                
                # Save report
                report_path = insights_manager.save_individual_report(
                    respondent_name=result['respondent_name'],
                    analysis=result['analysis']
                )
                
                # Update master
                insights_manager.update_master_insights(
                    new_analysis=result['analysis'],
                    respondent_name=result['respondent_name'],
                    transcript_number=count
                )
                
                saved_reports.append({
                    'respondent': result['respondent_name'],
                    'report_path': report_path
                })
        
        return jsonify({
            'success': True,
            'analyzed_count': len(saved_reports),
            'reports': saved_reports,
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/insights', methods=['GET', 'POST'])
def insights():
    """
    GET: Get master insights
    POST: Update master insights (manual update)
    """
    if request.method == 'GET':
        try:
            master_insights = insights_manager.load_master_insights()
            
            return jsonify({
                'success': True,
                'insights': master_insights,
                'statistics': insights_manager.get_statistics()
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            if not data or 'content' not in data:
                return jsonify({
                    'success': False,
                    'error': 'content is required'
                }), 400
            
            success = insights_manager.save_master_insights(data['content'])
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Master insights updated'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to save insights'
                }), 500
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500


@app.route('/api/insights/reports', methods=['GET'])
def list_reports():
    """List all individual analysis reports"""
    try:
        reports = insights_manager.list_reports()
        
        return jsonify({
            'success': True,
            'count': len(reports),
            'reports': reports
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/insights/reports/<filename>', methods=['GET'])
def get_report(filename):
    """Get a specific report by filename"""
    try:
        import os
        report_path = os.path.join(insights_manager.reports_dir, filename)
        
        if os.path.exists(report_path):
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return jsonify({
                'success': True,
                'filename': filename,
                'content': content
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Report not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/compare', methods=['POST'])
def compare():
    """
    Compare a transcript with existing insights
    
    Body parameters:
    - transcript_name: Name of transcript
    """
    try:
        data = request.get_json()
        
        if not data or 'transcript_name' not in data:
            return jsonify({
                'success': False,
                'error': 'transcript_name is required'
            }), 400
        
        transcript_name = data['transcript_name']
        transcript = transcript_parser.get_transcript_by_name(transcript_name)
        
        if not transcript or 'error' in transcript:
            return jsonify({
                'success': False,
                'error': 'Transcript not found'
            }), 404
        
        # Get master insights
        master_insights = insights_manager.load_master_insights()
        
        # Extract tags from transcript content (simple keyword matching)
        transcript_tags = insights_manager.extract_tags_from_analysis(
            transcript['content']
        )
        
        return jsonify({
            'success': True,
            'transcript': {
                'name': transcript['respondent_name'],
                'word_count': transcript['word_count'],
                'tags': transcript_tags
            },
            'master_insights_preview': master_insights[:500] + "..."
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/compare-insights', methods=['POST'])
def compare_insights():
    """
    Compare extracted insights from current analysis with other interviews
    
    Body parameters:
    - transcript_name: Name of current transcript
    - insights: List of insights to compare
    """
    try:
        data = request.get_json()
        
        if not data or 'insights' not in data:
            return jsonify({
                'success': False,
                'error': 'insights array is required'
            }), 400
        
        current_name = data.get('transcript_name', '')
        insights = data['insights']
        
        # Load all individual reports for comparison
        reports = insights_manager.list_reports()
        comparisons = []
        
        for insight in insights:
            insight_text = insight.get('text', '') if isinstance(insight, dict) else str(insight)
            insight_quote = insight.get('quote', '') if isinstance(insight, dict) else ''
            
            # Extract key words from insight for matching (words > 4 chars)
            keywords = [w.lower() for w in insight_text.split() if len(w) > 4]
            
            mentions = []
            
            # Search in other reports
            for report in reports:
                if report['respondent'] == current_name:
                    continue
                
                # Load report content
                report_content = insights_manager.load_report(report['respondent'])
                if not report_content:
                    continue
                
                report_lower = report_content.lower()
                
                # Check for keyword matches
                matched_keywords = [kw for kw in keywords if kw in report_lower]
                
                if len(matched_keywords) >= 2:  # At least 2 keywords match
                    # Try to extract a relevant quote
                    quote = extract_relevant_quote(report_content, matched_keywords)
                    mentions.append({
                        'respondent': report['respondent'],
                        'quote': quote,
                        'match_strength': len(matched_keywords)
                    })
            
            # Sort by match strength
            mentions.sort(key=lambda x: x['match_strength'], reverse=True)
            
            comparisons.append({
                'insight': insight_text,
                'quote': insight_quote,
                'mentions': mentions[:5]  # Top 5 mentions
            })
        
        return jsonify({
            'success': True,
            'comparisons': comparisons,
            'total_reports_checked': len(reports) - 1  # Exclude current
        })
        
    except Exception as e:
        import traceback
        print(f"[COMPARE-INSIGHTS] Error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def extract_relevant_quote(text, keywords):
    """Extract a relevant quote containing keywords"""
    lines = text.split('\n')
    
    for line in lines:
        line_lower = line.lower()
        # Check if line contains any keyword and looks like a quote
        if any(kw in line_lower for kw in keywords):
            if '«' in line or '"' in line or '>' in line:
                # Clean up the quote
                quote = line.strip()
                quote = quote.replace('>', '').strip()
                if len(quote) > 20 and len(quote) < 300:
                    return quote
    
    # Fallback: return first line with keyword match
    for line in lines:
        if any(kw in line.lower() for kw in keywords):
            if len(line.strip()) > 20 and len(line.strip()) < 300:
                return line.strip()[:200] + '...' if len(line) > 200 else line.strip()
    
    return ''


@app.route('/api/statistics', methods=['GET'])
def statistics():
    """Get system statistics"""
    try:
        stats = insights_manager.get_statistics()
        transcripts = transcript_parser.list_transcripts()
        
        return jsonify({
            'success': True,
            'statistics': {
                **stats,
                'total_transcript_files': len(transcripts)
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/search', methods=['POST'])
def search():
    """
    Search through insights
    
    Body parameters:
    - query: Search query string
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': 'query is required'
            }), 400
        
        query = data['query']
        results = insights_manager.search_insights(query)
        
        return jsonify({
            'success': True,
            'query': query,
            'results_count': len(results),
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'api_version': 'v1'
    })


# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


# ============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    # Check if API key is configured
    if not os.getenv('OPENAI_API_KEY') and not os.getenv('ANTHROPIC_API_KEY'):
        print("⚠️  WARNING: No API key configured!")
        print("Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env file")
    
    # Get configuration
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║   UX Transcript Analysis System - Backend API            ║
╚═══════════════════════════════════════════════════════════╝

Server: http://{host}:{port}
AI Provider: {AI_PROVIDER}
Model: {OPENAI_MODEL if AI_PROVIDER == 'openai' else 'claude-3-sonnet'}
Transcripts Directory: {TRANSCRIPTS_DIR}
Insights Directory: {INSIGHTS_DIR}

Available endpoints:
  - GET  /api/transcripts       List all transcripts
  - POST /api/transcripts       Upload new transcript
  - POST /api/analyze           Analyze a transcript
  - POST /api/analyze/batch     Batch analyze transcripts
  - GET  /api/insights          Get master insights
  - GET  /api/statistics        Get system statistics
  - POST /api/search            Search insights

Press Ctrl+C to stop the server
""")
    
    app.run(host=host, port=port, debug=debug)
