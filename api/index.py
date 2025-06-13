import os
import json
from datetime import datetime
from io import BytesIO
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

# Configuration - Environment variables
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')

# Simple error page for missing environment variables
@app.route('/')
def index():
    if not YOUTUBE_API_KEY or not ANTHROPIC_API_KEY:
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Competitor Intelligence Analyzer</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                h1 {{ color: #2c3e50; }}
                .status {{ padding: 10px; margin: 10px 0; border-radius: 4px; }}
                .error {{ background: #fee; border: 1px solid #fcc; color: #c00; }}
                .success {{ background: #efe; border: 1px solid #cfc; color: #060; }}
                ul {{ background: #f9f9f9; padding: 20px; border-radius: 4px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🕵️ Competitor Intelligence Analyzer</h1>
                <div class="status error">
                    <strong>Configuration Error</strong><br>
                    Missing required environment variables. Please configure:
                </div>
                <ul>
                    <li><strong>YOUTUBE_API_KEY:</strong> {"✅ Set" if YOUTUBE_API_KEY else "❌ Missing"}</li>
                    <li><strong>ANTHROPIC_API_KEY:</strong> {"✅ Set" if ANTHROPIC_API_KEY else "❌ Missing"}</li>
                </ul>
                <p><strong>Instructions:</strong></p>
                <ol>
                    <li>Set environment variables in your deployment platform</li>
                    <li>Get YouTube Data API v3 key from Google Cloud Console</li>
                    <li>Get Anthropic Claude API key from Anthropic Console</li>
                    <li>Redeploy the application</li>
                </ol>
            </div>
        </body>
        </html>
        '''
    
    # Main application interface
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Competitor Intelligence Analyzer</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            h1 {{ color: #2c3e50; text-align: center; margin-bottom: 30px; }}
            .form-group {{ margin-bottom: 20px; }}
            label {{ display: block; margin-bottom: 5px; font-weight: 600; color: #2c3e50; }}
            input, textarea {{ width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 4px; font-size: 14px; box-sizing: border-box; }}
            input:focus, textarea:focus {{ outline: none; border-color: #3498db; }}
            button {{ background: #3498db; color: white; border: none; padding: 15px 30px; border-radius: 4px; cursor: pointer; font-size: 16px; font-weight: 600; width: 100%; }}
            button:hover {{ background: #2980b9; }}
            button:disabled {{ background: #bdc3c7; cursor: not-allowed; }}
            .result {{ margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 4px; border-left: 4px solid #3498db; }}
            .error {{ background: #fee; border-left-color: #e74c3c; color: #c0392b; }}
            .loading {{ text-align: center; color: #7f8c8d; }}
            .export-btn {{ background: #27ae60; margin-top: 10px; }}
            .export-btn:hover {{ background: #229954; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🕵️ Competitor Intelligence Analyzer</h1>
            <p style="text-align: center; color: #7f8c8d; margin-bottom: 30px;">
                Analyze YouTube comments about your competitors to uncover strategic insights for your marketing team.
            </p>
            
            <form id="analysisForm">
                <div class="form-group">
                    <label for="competitor_name">Competitor Name:</label>
                    <input type="text" id="competitor_name" name="competitor_name" placeholder="e.g., Apple, Tesla, Nike" required>
                </div>
                
                <div class="form-group">
                    <label for="video_url">YouTube Video URL:</label>
                    <input type="url" id="video_url" name="video_url" placeholder="https://www.youtube.com/watch?v=..." required>
                </div>
                
                <button type="submit" id="analyzeBtn">Analyze Comments</button>
            </form>
            
            <div id="result" style="display: none;"></div>
        </div>
        
        <script>
            document.getElementById('analysisForm').addEventListener('submit', async function(e) {{
                e.preventDefault();
                
                const analyzeBtn = document.getElementById('analyzeBtn');
                const result = document.getElementById('result');
                
                analyzeBtn.disabled = true;
                analyzeBtn.textContent = 'Analyzing...';
                
                result.style.display = 'block';
                result.className = 'result loading';
                result.innerHTML = '<p>🔍 Extracting comments and analyzing competitive intelligence...</p><p>This may take 30-60 seconds.</p>';
                
                try {{
                    const formData = new FormData(e.target);
                    const response = await fetch('/analyze', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{
                            competitor_name: formData.get('competitor_name'),
                            video_url: formData.get('video_url')
                        }})
                    }});
                    
                    const data = await response.json();
                    
                    if (data.error) {{
                        result.className = 'result error';
                        result.innerHTML = `<strong>Error:</strong> ${{data.error}}`;
                    }} else {{
                        result.className = 'result';
                        result.innerHTML = `
                            <h3>📊 Analysis Results for ${{data.competitor_name}}</h3>
                            <p><strong>Comments Analyzed:</strong> ${{data.total_comments}}</p>
                            <div style="white-space: pre-wrap; line-height: 1.6;">${{data.analysis}}</div>
                            <button class="export-btn" onclick="exportReport()">📄 Export Text Report</button>
                        `;
                        
                        // Store data for export
                        window.analysisData = data;
                    }}
                }} catch (error) {{
                    result.className = 'result error';
                    result.innerHTML = `<strong>Error:</strong> Failed to analyze. Please try again.`;
                }}
                
                analyzeBtn.disabled = false;
                analyzeBtn.textContent = 'Analyze Comments';
            }});
            
            async function exportReport() {{
                if (!window.analysisData) return;
                
                try {{
                    const response = await fetch('/export-report', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify(window.analysisData)
                    }});
                    
                    if (response.ok) {{
                        const blob = await response.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `competitor_analysis_${{window.analysisData.competitor_name.replace(/\\s+/g, '_')}}_${{new Date().toISOString().slice(0,10)}}.txt`;
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        window.URL.revokeObjectURL(url);
                    }}
                }} catch (error) {{
                    alert('Export failed. Please try again.');
                }}
            }}
        </script>
    </body>
    </html>
    '''

@app.route('/analyze', methods=['POST'])
def analyze():
    if not YOUTUBE_API_KEY or not ANTHROPIC_API_KEY:
        return jsonify({'error': 'Environment variables not configured'})
    
    try:
        # Import here to avoid loading if not needed
        import requests
        
        data = request.json
        video_url = data.get('video_url', '')
        competitor_name = data.get('competitor_name', '')
        
        if not video_url or not competitor_name:
            return jsonify({'error': 'Please provide both video URL and competitor name'})
        
        # Simple video ID extraction
        video_id = None
        if "youtube.com/watch?v=" in video_url:
            video_id = video_url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in video_url:
            video_id = video_url.split("youtu.be/")[1].split("?")[0]
        
        if not video_id:
            return jsonify({'error': 'Invalid YouTube URL'})
        
        # Get comments using direct API call
        youtube_url = f"https://www.googleapis.com/youtube/v3/commentThreads"
        params = {
            'part': 'snippet',
            'videoId': video_id,
            'maxResults': 50,
            'order': 'relevance',
            'key': YOUTUBE_API_KEY
        }
        
        youtube_response = requests.get(youtube_url, params=params)
        
        if youtube_response.status_code != 200:
            return jsonify({'error': 'Failed to fetch YouTube comments'})
        
        youtube_data = youtube_response.json()
        
        if 'items' not in youtube_data or not youtube_data['items']:
            return jsonify({'error': 'No comments found for this video'})
        
        # Extract comments
        comments = []
        for item in youtube_data['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            comments.append({
                'text': comment['textDisplay'],
                'author': comment['authorDisplayName'],
                'likes': comment['likeCount']
            })
        
        # Analyze using Anthropic API
        comments_text = "\\n".join([f"Comment: {comment['text']}" for comment in comments[:30]])
        
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

        # Call Anthropic API
        anthropic_url = "https://api.anthropic.com/v1/messages"
        headers = {
            'x-api-key': ANTHROPIC_API_KEY,
            'content-type': 'application/json',
            'anthropic-version': '2023-06-01'
        }
        
        anthropic_payload = {
            'model': 'claude-3-haiku-20240307',  # Using lighter model
            'max_tokens': 2000,
            'messages': [{'role': 'user', 'content': prompt}]
        }
        
        anthropic_response = requests.post(anthropic_url, json=anthropic_payload, headers=headers)
        
        if anthropic_response.status_code != 200:
            return jsonify({'error': f'AI analysis failed: {anthropic_response.text}'})
        
        anthropic_data = anthropic_response.json()
        analysis = anthropic_data['content'][0]['text']
        
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
        total_comments = data.get('total_comments', 0)
        
        if not analysis_result:
            return jsonify({'error': 'No analysis data to export'})
        
        # Generate text report
        report = f"""COMPETITOR INTELLIGENCE REPORT
========================================

Competitor Analyzed: {competitor_name}
Source: YouTube Comment Analysis  
Comments Analyzed: {total_comments}
Report Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

========================================
COMPETITIVE INTELLIGENCE ANALYSIS
========================================

{analysis_result}

========================================
Generated by Competitor Intelligence Analyzer
"""
        
        filename = f"competitor_analysis_{competitor_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        # Create a BytesIO buffer for the text file
        buffer = BytesIO()
        buffer.write(report.encode('utf-8'))
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='text/plain'
        )
    
    except Exception as e:
        return jsonify({'error': f'Error generating report: {str(e)}'})

# Export the Flask app for production deployment
# This works with Railway, Heroku, Render, etc.
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port) 