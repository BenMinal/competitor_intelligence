# 🕵️ Competitor Intelligence Analyzer

> **Analyze YouTube comments about your competitors to uncover strategic insights for your marketing team.**

A powerful web application that extracts YouTube comments and uses AI to provide competitive intelligence insights, helping you understand what customers love about your competitors, their pain points, and opportunities for differentiation.

## 🚀 Live Demo

**[Try the live app on Vercel →](https://competitor-intelligence.vercel.app)**

## ✨ Features

- 📺 **YouTube Comment Analysis**: Extract and analyze up to 50 top comments from any YouTube video
- 🤖 **AI-Powered Insights**: Uses Claude 4 to provide strategic competitive intelligence
- 📊 **Comprehensive Reports**: Get insights on what customers love, pain points, vulnerabilities, and opportunities
- 📄 **PDF Export**: Generate professional PDF reports for team sharing
- 🎯 **Marketing Focus**: Tailored specifically for marketing teams and competitive analysis
- 🔒 **Secure**: Environment-based API key management

## 🛠️ Tech Stack

- **Backend**: Flask (Python)
- **AI**: Anthropic Claude 4
- **APIs**: YouTube Data API v3
- **PDF Generation**: ReportLab
- **Deployment**: Vercel (Serverless)
- **Frontend**: HTML5, CSS3, JavaScript

## 📋 Prerequisites

1. **YouTube Data API Key** - Get from [Google Cloud Console](https://console.cloud.google.com)
2. **Anthropic Claude API Key** - Get from [Anthropic Console](https://console.anthropic.com)

## 🏃‍♂️ Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/BenMinal/competitor_intelligence.git
   cd competitor_intelligence
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv yt_sentiment_env
   source yt_sentiment_env/bin/activate  # On Windows: yt_sentiment_env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open in browser**
   ```
   http://localhost:8080
   ```

### Vercel Deployment

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Deploy with script**
   ```bash
   ./deploy.sh
   ```

3. **Configure environment variables** in Vercel dashboard:
   - `YOUTUBE_API_KEY`
   - `ANTHROPIC_API_KEY`

See [README-VERCEL.md](README-VERCEL.md) for detailed deployment instructions.

## 📖 How to Use

1. **Enter Competitor Information**
   - YouTube video URL (competitor's content)
   - Competitor name

2. **Analyze Comments**
   - Click "Analyze Comments" 
   - Wait for AI analysis (30-60 seconds)

3. **Review Insights**
   - What customers love about the competitor
   - Pain points and frustrations
   - Key selling points and vulnerabilities
   - Strategic opportunities for differentiation

4. **Export Report**
   - Click "Export PDF Report"
   - Share with your marketing team

## 🎯 Use Cases

- **Competitive Analysis**: Understand competitor strengths and weaknesses
- **Product Development**: Identify unmet customer needs
- **Marketing Strategy**: Find positioning opportunities
- **Content Strategy**: Understand what resonates with customers
- **Sales Enablement**: Arm sales teams with competitive insights

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `YOUTUBE_API_KEY` | YouTube Data API v3 key | Yes |
| `ANTHROPIC_API_KEY` | Claude API key | Yes |

### API Limits

- **YouTube API**: 10,000 requests/day (free tier)
- **Claude API**: Pay-per-use pricing
- **Comments**: Analyzes top 50 comments per video

## 📁 Project Structure

```
competitor_intelligence/
├── api/
│   ├── __init__.py
│   └── index.py           # Main serverless function
├── templates/
│   └── index.html         # Web interface
├── app.py                 # Local development server
├── requirements.txt       # Python dependencies
├── vercel.json           # Vercel configuration
├── deploy.sh             # Deployment script
├── README.md             # This file
├── README-VERCEL.md      # Deployment guide
└── env.example           # Environment variables template
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Issues & Support

- **Bug Reports**: [Open an issue](https://github.com/BenMinal/competitor_intelligence/issues)
- **Feature Requests**: [Open an issue](https://github.com/BenMinal/competitor_intelligence/issues)
- **Questions**: Check the [documentation](README-VERCEL.md) or open a discussion

## 🙏 Acknowledgments

- **Anthropic** for Claude AI capabilities
- **Google** for YouTube Data API
- **Vercel** for seamless deployment
- **ReportLab** for PDF generation

---

**Built with ❤️ for marketing teams who want to understand their competition better.** 