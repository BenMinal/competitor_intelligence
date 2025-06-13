import os
import sys
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, send_file
from googleapiclient.discovery import build
import anthropic
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.colors import HexColor

# Add the parent directory to the path so we can import from the root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__, template_folder='../templates')

# Configuration
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')

# Validate API keys
if not YOUTUBE_API_KEY:
    raise ValueError("YOUTUBE_API_KEY environment variable is required")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY environment variable is required")

# Initialize clients
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def extract_video_id(url):
    """Extract video ID from YouTube URL"""
    if "youtube.com/watch?v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    return None

def get_video_comments(video_id, max_results=50):
    """Fetch comments from a YouTube video"""
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

def generate_pdf_report(analysis_result, competitor_name, video_url, total_comments):
    """Generate a PDF report of the competitive analysis"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=1*inch)
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=HexColor('#34495e'),
        spaceAfter=20,
        spaceBefore=20
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=HexColor('#2980b9'),
        spaceAfter=12,
        spaceBefore=16,
        fontName='Helvetica-Bold'
    )
    
    # Title
    story.append(Paragraph("Competitor Intelligence Report", title_style))
    story.append(Spacer(1, 12))
    
    # Report metadata
    story.append(Paragraph(f"<b>Competitor Analyzed:</b> {competitor_name}", styles['Normal']))
    story.append(Paragraph(f"<b>Source Video:</b> YouTube Analysis", styles['Normal']))
    story.append(Paragraph(f"<b>Comments Analyzed:</b> {total_comments}", styles['Normal']))
    story.append(Paragraph(f"<b>Report Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Analysis content
    story.append(Paragraph("Competitive Intelligence Analysis", subtitle_style))
    
    # Split the analysis by sections and format
    sections = analysis_result.split('**')
    current_text = ""
    
    for section in sections:
        if section.strip():
            if section.strip().endswith(':'):
                # This is a header
                if current_text.strip():
                    # Add previous content
                    for line in current_text.strip().split('\n'):
                        if line.strip():
                            story.append(Paragraph(line.strip(), styles['Normal']))
                    story.append(Spacer(1, 8))
                
                # Add the header
                header_text = section.strip().replace(':', '')
                story.append(Paragraph(header_text, header_style))
                current_text = ""
            else:
                current_text += section
    
    # Add any remaining content
    if current_text.strip():
        for line in current_text.strip().split('\n'):
            if line.strip():
                story.append(Paragraph(line.strip(), styles['Normal']))
    
    story.append(Spacer(1, 30))
    story.append(Paragraph("Generated by Competitor Intelligence Analyzer", styles['Italic']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
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

@app.route('/export-pdf', methods=['POST'])
def export_pdf():
    try:
        data = request.json
        analysis_result = data.get('analysis', '')
        competitor_name = data.get('competitor_name', '')
        video_url = data.get('video_url', '')
        total_comments = data.get('total_comments', 0)
        
        if not analysis_result:
            return jsonify({'error': 'No analysis data to export'})
        
        # Generate PDF
        pdf_buffer = generate_pdf_report(analysis_result, competitor_name, video_url, total_comments)
        
        filename = f"competitor_analysis_{competitor_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
    
    except Exception as e:
        return jsonify({'error': f'Error generating PDF: {str(e)}'}), 500

# For Vercel serverless deployment
def handler(request):
    return app(request.environ, lambda status, headers: None)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080) 