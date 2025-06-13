import os
import sys
import json
from datetime import datetime

# Add the parent directory to the path so we can import from the root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from flask import Flask, render_template, request, jsonify, send_file
    from googleapiclient.discovery import build
    import anthropic
    from io import BytesIO, StringIO
except ImportError as e:
    print(f"Import error: {e}")
    # Create a minimal error response
    def app(environ, start_response):
        status = '500 Internal Server Error'
        response_headers = [('Content-type', 'text/html')]
        start_response(status, response_headers)
        return [f'Import Error: {str(e)}'.encode()]

app = Flask(__name__, template_folder='../templates')

# Configuration - Environment variables
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')

# Check if we're in a test environment or missing keys
if not YOUTUBE_API_KEY or not ANTHROPIC_API_KEY:
    print(f"Missing environment variables - YouTube: {bool(YOUTUBE_API_KEY)}, Anthropic: {bool(ANTHROPIC_API_KEY)}")
    
    @app.route('/')
    def index():
        return '''
        <html>
        <head><title>Configuration Error</title></head>
        <body>
        <h1>Configuration Error</h1>
        <p>Missing required environment variables. Please configure:</p>
        <ul>
        <li>YOUTUBE_API_KEY: {}</li>
        <li>ANTHROPIC_API_KEY: {}</li>
        </ul>
        <p>Please set these in your Vercel dashboard under Settings > Environment Variables</p>
        </body>
        </html>
        '''.format("✅ Set" if YOUTUBE_API_KEY else "❌ Missing", "✅ Set" if ANTHROPIC_API_KEY else "❌ Missing")
    
    @app.route('/analyze', methods=['POST'])
    def analyze():
        return jsonify({'error': 'Environment variables not configured'})
    
    @app.route('/export-report', methods=['POST'])
    def export_report():
        return jsonify({'error': 'Environment variables not configured'})

else:
    # Initialize clients only if we have the keys
    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    except Exception as e:
        print(f"Error initializing clients: {e}")
        youtube = None
        claude_client = None

    def extract_video_id(url):
        """Extract video ID from YouTube URL"""
        if "youtube.com/watch?v=" in url:
            return url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in url:
            return url.split("youtu.be/")[1].split("?")[0]
        return None

    def get_video_comments(video_id, max_results=50):
        """Fetch comments from a YouTube video"""
        if not youtube:
            return []
        try:
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=max_results,
                order="relevance"
            )
            response = request.execute()
            
            comments = []
            for item in response['items']:
                comment = item['snippet']['topLevelComment']['snippet']
                comments.append({
                    'text': comment['textDisplay'],
                    'author': comment['authorDisplayName'],
                    'likes': comment['likeCount'],
                    'published': comment['publishedAt']
                })
            
            return comments
        except Exception as e:
            print(f"Error fetching comments: {e}")
            return []

    def analyze_competitive_intelligence(comments, competitor_name):
        """Analyze comments for competitive intelligence using Claude"""
        if not claude_client:
            return "Claude client not initialized"
        try:
            comments_text = "\n".join([f"Comment: {comment['text']}" for comment in comments[:30]])
            
            prompt = f"""You are a competitive intelligence analyst for a marketing team. Analyze these YouTube comments about {competitor_name} and provide strategic insights.

Comments to analyze:
{comments_text}

Please provide a comprehensive competitive analysis in the following structure:

**WHAT CUSTOMERS LOVE ABOUT {competitor_name.upper()}:**
- List specific features, benefits, or aspects customers praise
- Include direct quotes when relevant

**PAIN POINTS & CUSTOMER FRUSTRATIONS:**
- Identify complaints, issues, or negative feedback
- Look for recurring problems or unmet needs

**{competitor_name.upper()}'S KEY SELLING POINTS:**
- What value propositions are customers responding to?
- What differentiators are mentioned?

**{competitor_name.upper()}'S VULNERABILITIES:**
- Areas where they're failing customers
- Gaps in their offering or service

**STRATEGIC MARKETING OPPORTUNITIES:**
- How can we position against these weaknesses?
- What customer needs are unmet?

**HOW YOU CAN DIFFERENTIATE:**
- Specific recommendations for competitive advantage
- Areas to focus product development or marketing

Keep insights actionable and business-focused. Use bullet points for clarity."""

            response = claude_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text
        except Exception as e:
            return f"Error analyzing competitive intelligence: {str(e)}"

    def generate_text_report(analysis_result, competitor_name, video_url, total_comments):
        """Generate a text report of the competitive analysis"""
        try:
            report = f"""
COMPETITOR INTELLIGENCE REPORT
========================================

Competitor Analyzed: {competitor_name}
Source Video: YouTube Analysis  
Comments Analyzed: {total_comments}
Report Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

========================================
COMPETITIVE INTELLIGENCE ANALYSIS
========================================

{analysis_result}

========================================
Generated by Competitor Intelligence Analyzer
"""
            return report
        except Exception as e:
            print(f"Report generation error: {e}")
            return None

    @app.route('/')
    def index():
        try:
            return render_template('index.html')
        except Exception as e:
            return f'''
            <html>
            <head><title>Competitor Intelligence Analyzer</title></head>
            <body>
            <h1>🕵️ Competitor Intelligence Analyzer</h1>
            <p>Template loading error: {str(e)}</p>
            <p>Please check that templates/index.html exists</p>
            </body>
            </html>
            '''

    @app.route('/analyze', methods=['POST'])
    def analyze():
        try:
            data = request.json
            video_url = data.get('video_url', '')
            competitor_name = data.get('competitor_name', '')
            
            if not video_url or not competitor_name:
                return jsonify({'error': 'Please provide both video URL and competitor name'})
            
            # Extract video ID
            video_id = extract_video_id(video_url)
            if not video_id:
                return jsonify({'error': 'Invalid YouTube URL'})
            
            # Get comments
            comments = get_video_comments(video_id)
            if not comments:
                return jsonify({'error': 'Could not fetch comments from this video'})
            
            # Analyze competitive intelligence
            analysis = analyze_competitive_intelligence(comments, competitor_name)
            
            return jsonify({
                'analysis': analysis,
                'total_comments': len(comments),
                'competitor_name': competitor_name,
                'video_url': video_url
            })
        except Exception as e:
            return jsonify({'error': f'Analysis error: {str(e)}'})

    @app.route('/export-report', methods=['POST'])
    def export_report():
        try:
            data = request.json
            analysis_result = data.get('analysis', '')
            competitor_name = data.get('competitor_name', '')
            video_url = data.get('video_url', '')
            total_comments = data.get('total_comments', 0)
            
            if not analysis_result:
                return jsonify({'error': 'No analysis data to export'})
            
            # Generate text report
            report_text = generate_text_report(analysis_result, competitor_name, video_url, total_comments)
            
            if not report_text:
                return jsonify({'error': 'Failed to generate report'})
            
            filename = f"competitor_analysis_{competitor_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            # Create a BytesIO buffer for the text file
            buffer = BytesIO()
            buffer.write(report_text.encode('utf-8'))
            buffer.seek(0)
            
            return send_file(
                buffer,
                as_attachment=True,
                download_name=filename,
                mimetype='text/plain'
            )
        
        except Exception as e:
            return jsonify({'error': f'Error generating report: {str(e)}'})

# For Vercel serverless deployment
def handler(event, context):
    """Vercel serverless handler"""
    try:
        from werkzeug.wrappers import Request, Response
        from werkzeug.serving import WSGIRequestHandler
        
        # Create a WSGI environ from the event
        environ = {
            'REQUEST_METHOD': event.get('httpMethod', 'GET'),
            'PATH_INFO': event.get('path', '/'),
            'QUERY_STRING': event.get('queryStringParameters', ''),
            'CONTENT_TYPE': event.get('headers', {}).get('content-type', ''),
            'CONTENT_LENGTH': str(len(event.get('body', ''))),
            'wsgi.input': BytesIO(event.get('body', '').encode()),
            'wsgi.errors': sys.stderr,
            'wsgi.version': (1, 0),
            'wsgi.multithread': False,
            'wsgi.multiprocess': True,
            'wsgi.run_once': False,
            'wsgi.url_scheme': 'https',
        }
        
        response_data = []
        def start_response(status, headers):
            response_data.append((status, headers))
        
        result = app(environ, start_response)
        
        return {
            'statusCode': int(response_data[0][0].split()[0]),
            'headers': dict(response_data[0][1]),
            'body': b''.join(result).decode()
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Handler error: {str(e)}'
        }

# Export the Flask app for Vercel
# This is the standard way Vercel expects Flask apps to be exported
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app)

# Standard WSGI app for Vercel
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080) 