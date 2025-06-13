from flask import Flask, request, render_template, jsonify, send_file
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build

# Load environment variables from .env file
load_dotenv()
import anthropic
import json
import re
from urllib.parse import urlparse, parse_qs
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import io
from datetime import datetime

app = Flask(__name__)

# API Keys
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')

# Validate API keys
if not YOUTUBE_API_KEY:
    raise ValueError("YOUTUBE_API_KEY environment variable is required")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY environment variable is required")

# Initialize APIs
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def extract_video_id(url):
    """Extract video ID from YouTube URL"""
    parsed_url = urlparse(url)
    if 'youtube.com' in parsed_url.netloc:
        return parse_qs(parsed_url.query).get('v', [None])[0]
    elif 'youtu.be' in parsed_url.netloc:
        return parsed_url.path[1:]
    return None

def get_video_info(video_id):
    """Get video title and description"""
    try:
        response = youtube.videos().list(
            part='snippet',
            id=video_id
        ).execute()
        
        if response['items']:
            snippet = response['items'][0]['snippet']
            return {
                'title': snippet['title'],
                'description': snippet['description']
            }
    except Exception as e:
        print(f"Error getting video info: {e}")
    return None

def get_comments(video_id, max_results=50):
    """Fetch top comments from a YouTube video"""
    comments = []
    try:
        response = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=max_results,
            order='relevance'
        ).execute()
        
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            comments.append({
                'text': comment['textDisplay'],
                'author': comment['authorDisplayName'],
                'likes': comment['likeCount'],
                'published': comment['publishedAt']
            })
            
    except Exception as e:
        print(f"Error fetching comments for video {video_id}: {e}")
    
    return comments

def analyze_sentiment_with_claude(comments, product_name):
    """Analyze sentiment and extract insights using Anthropic Claude"""
    
    # Prepare comments text
    comments_text = "\n".join([f"Comment {i+1}: {comment['text']}" for i, comment in enumerate(comments)])
    
    prompt = f"""
    Analyze these YouTube comments about the competitor product: {product_name}
    
    Provide competitive intelligence insights for a marketing team that wants to understand how this competitor is being perceived by customers.

    Comments:
    {comments_text}

    Please provide a comprehensive competitive analysis in the following JSON format:

    {{
        "sentiment_summary": {{
            "positive_count": 0,
            "negative_count": 0,
            "neutral_count": 0,
            "total_comments": 0
        }},
        "key_themes": {{
            "positive_aspects": [
                {{"theme": "what customers love about this competitor", "mentions": 0, "sample_comments": ["comment1", "comment2"]}}
            ],
            "negative_aspects": [
                {{"theme": "customer pain points and frustrations", "mentions": 0, "sample_comments": ["comment1", "comment2"]}}
            ]
        }},
        "product_insights": {{
            "strengths": [
                {{"feature": "competitor's key selling point", "description": "why customers choose this competitor", "frequency": 0}}
            ],
            "weaknesses": [
                {{"feature": "competitor vulnerability", "description": "where this competitor falls short", "frequency": 0}}
            ],
            "suggestions": [
                "how your company can differentiate and compete",
                "market opportunities to exploit"
            ]
        }},
        "marketing_insights": [
            "strategic opportunities for competitive positioning",
            "messaging gaps you can exploit",
            "market segments where competitor is weak"
        ]
    }}

    Focus on competitive intelligence: competitor strengths to be aware of, weaknesses to exploit, customer expectations, pricing perceptions, and opportunities for differentiation. Frame everything from the perspective of helping a marketing team compete against this product.
    """
    
    try:
        response = claude_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse the JSON response
        analysis_text = response.content[0].text
        
        # Extract JSON from the response
        json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
        if json_match:
            analysis = json.loads(json_match.group())
            return analysis
        else:
            # Fallback if JSON parsing fails
            return {
                "error": "Could not parse analysis",
                "raw_response": analysis_text
            }
            
    except Exception as e:
        print(f"Error analyzing sentiment: {e}")
        return {"error": str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    urls = data.get('urls', [])
    product_name = data.get('product_name', '')
    
    if not urls or not product_name:
        return jsonify({"error": "Please provide URLs and product name"}), 400
    
    all_comments = []
    video_info = []
    
    # Fetch comments from all videos
    for url in urls:
        video_id = extract_video_id(url.strip())
        if not video_id:
            continue
            
        # Get video info
        info = get_video_info(video_id)
        if info:
            video_info.append({
                'url': url,
                'title': info['title'],
                'video_id': video_id
            })
        
        # Get comments
        comments = get_comments(video_id)
        all_comments.extend(comments)
    
    if not all_comments:
        return jsonify({"error": "No comments found for the provided URLs"}), 400
    
    # Analyze sentiment
    analysis = analyze_sentiment_with_claude(all_comments, product_name)
    
    # Prepare response
    result = {
        "product_name": product_name,
        "total_videos": len(video_info),
        "total_comments": len(all_comments),
        "video_info": video_info,
        "analysis": analysis
    }
    
    return jsonify(result)

def generate_pdf_report(product_name, analysis, total_videos, total_comments):
    """Generate a PDF report of the competitive intelligence analysis"""
    
    # Create a BytesIO buffer to hold the PDF
    buffer = io.BytesIO()
    
    # Create the PDF document
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, 
                           topMargin=72, bottomMargin=18)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#333333'),
        spaceAfter=15,
        spaceBefore=20
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#666666'),
        spaceAfter=10
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        spaceAfter=8
    )
    
    # Build the PDF content
    story = []
    
    # Title and metadata
    story.append(Paragraph("🕵️ Competitive Intelligence Report", title_style))
    story.append(Spacer(1, 20))
    
    # Report metadata
    date_str = datetime.now().strftime("%B %d, %Y")
    story.append(Paragraph(f"<b>Competitor Product:</b> {product_name}", normal_style))
    story.append(Paragraph(f"<b>Report Generated:</b> {date_str}", normal_style))
    story.append(Paragraph(f"<b>Videos Analyzed:</b> {total_videos}", normal_style))
    story.append(Paragraph(f"<b>Comments Analyzed:</b> {total_comments}", normal_style))
    story.append(Spacer(1, 30))
    
    # Summary Statistics
    if 'sentiment_summary' in analysis:
        sentiment = analysis['sentiment_summary']
        story.append(Paragraph("📊 Sentiment Overview", heading_style))
        
        # Create summary table
        summary_data = [
            ['Metric', 'Count'],
            ['Positive Comments', str(sentiment.get('positive_count', 0))],
            ['Negative Comments', str(sentiment.get('negative_count', 0))],
            ['Neutral Comments', str(sentiment.get('neutral_count', 0))],
        ]
        
        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
    
    # What Customers Love
    if 'key_themes' in analysis and 'positive_aspects' in analysis['key_themes']:
        story.append(Paragraph("🏆 What Customers Love About This Competitor", heading_style))
        for theme in analysis['key_themes']['positive_aspects']:
            story.append(Paragraph(f"<b>{theme.get('theme', 'N/A')}</b>", subheading_style))
            story.append(Paragraph(f"Mentioned {theme.get('mentions', 0)} times", normal_style))
            if 'sample_comments' in theme and theme['sample_comments']:
                for comment in theme['sample_comments'][:2]:  # Show top 2 comments
                    story.append(Paragraph(f"• \"{comment}\"", normal_style))
            story.append(Spacer(1, 10))
    
    # Pain Points & Frustrations
    if 'key_themes' in analysis and 'negative_aspects' in analysis['key_themes']:
        story.append(Paragraph("💥 Pain Points & Customer Frustrations", heading_style))
        for theme in analysis['key_themes']['negative_aspects']:
            story.append(Paragraph(f"<b>{theme.get('theme', 'N/A')}</b>", subheading_style))
            story.append(Paragraph(f"Mentioned {theme.get('mentions', 0)} times", normal_style))
            if 'sample_comments' in theme and theme['sample_comments']:
                for comment in theme['sample_comments'][:2]:
                    story.append(Paragraph(f"• \"{comment}\"", normal_style))
            story.append(Spacer(1, 10))
    
    # Competitor's Key Selling Points
    if 'product_insights' in analysis and 'strengths' in analysis['product_insights']:
        story.append(Paragraph("🎯 Competitor's Key Selling Points", heading_style))
        for strength in analysis['product_insights']['strengths']:
            story.append(Paragraph(f"<b>{strength.get('feature', 'N/A')}</b>", subheading_style))
            story.append(Paragraph(strength.get('description', 'N/A'), normal_style))
            story.append(Paragraph(f"Frequency: {strength.get('frequency', 0)}", normal_style))
            story.append(Spacer(1, 10))
    
    # Competitor's Vulnerabilities
    if 'product_insights' in analysis and 'weaknesses' in analysis['product_insights']:
        story.append(Paragraph("🎪 Competitor's Vulnerabilities", heading_style))
        for weakness in analysis['product_insights']['weaknesses']:
            story.append(Paragraph(f"<b>{weakness.get('feature', 'N/A')}</b>", subheading_style))
            story.append(Paragraph(weakness.get('description', 'N/A'), normal_style))
            story.append(Paragraph(f"Frequency: {weakness.get('frequency', 0)}", normal_style))
            story.append(Spacer(1, 10))
    
    # Strategic Marketing Opportunities
    if 'marketing_insights' in analysis:
        story.append(Paragraph("💡 Strategic Marketing Opportunities", heading_style))
        for insight in analysis['marketing_insights']:
            story.append(Paragraph(f"• {insight}", normal_style))
        story.append(Spacer(1, 15))
    
    # How You Can Differentiate
    if 'product_insights' in analysis and 'suggestions' in analysis['product_insights']:
        story.append(Paragraph("🚀 How You Can Differentiate", heading_style))
        for suggestion in analysis['product_insights']['suggestions']:
            story.append(Paragraph(f"• {suggestion}", normal_style))
    
    # Build the PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

@app.route('/export-pdf', methods=['POST'])
def export_pdf():
    """Export the analysis results as a PDF"""
    data = request.json
    product_name = data.get('product_name', 'Unknown Product')
    analysis = data.get('analysis', {})
    total_videos = data.get('total_videos', 0)
    total_comments = data.get('total_comments', 0)
    
    try:
        # Generate the PDF
        pdf_buffer = generate_pdf_report(product_name, analysis, total_videos, total_comments)
        
        # Create filename
        safe_product_name = re.sub(r'[^\w\-_.]', '_', product_name)
        filename = f"Competitive_Intelligence_{safe_product_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return jsonify({"error": "Failed to generate PDF"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080) 