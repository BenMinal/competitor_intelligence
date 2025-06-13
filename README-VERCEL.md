# Deploy to Vercel

This guide will help you deploy your Competitor Intelligence Analyzer to Vercel.

## Prerequisites

1. A [Vercel account](https://vercel.com) (free tier available)
2. Your API keys:
   - YouTube Data API key
   - Anthropic Claude API key

## Deployment Steps

### Option 1: Deploy via Vercel CLI (Recommended)

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy from your project directory**
   ```bash
   vercel
   ```

4. **Configure Environment Variables**
   During deployment or in the Vercel dashboard, add:
   - `YOUTUBE_API_KEY`: Your YouTube Data API key
   - `ANTHROPIC_API_KEY`: Your Anthropic Claude API key

### Option 2: Deploy via GitHub Integration

1. **Push your code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Connect to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Vercel will auto-detect the Flask app

3. **Configure Environment Variables**
   In the Vercel dashboard:
   - Go to your project settings
   - Navigate to "Environment Variables"
   - Add:
     - `YOUTUBE_API_KEY`: Your YouTube Data API key
     - `ANTHROPIC_API_KEY`: Your Anthropic Claude API key

## Important Notes

### API Keys Security
- **NEVER** commit your actual API keys to version control
- Always use environment variables in production
- The current code has hardcoded keys for development - these will be replaced by environment variables in production

### Vercel Limitations
- Serverless functions have a 10-second timeout limit
- Large PDF reports might hit memory limits
- Consider implementing pagination for large comment sets

### File Structure for Vercel
The project has been restructured for Vercel deployment:
```
├── api/
│   ├── __init__.py
│   └── index.py        # Main serverless function
├── templates/
│   └── index.html      # HTML template
├── vercel.json         # Vercel configuration
├── requirements.txt    # Python dependencies
└── README-VERCEL.md    # This file
```

## Environment Variables Setup

After deployment, configure these environment variables in Vercel:

1. Go to your Vercel project dashboard
2. Click on "Settings"
3. Click on "Environment Variables"
4. Add each variable:

| Variable | Description | Where to get it |
|----------|-------------|-----------------|
| `YOUTUBE_API_KEY` | YouTube Data API v3 key | [Google Cloud Console](https://console.cloud.google.com) |
| `ANTHROPIC_API_KEY` | Claude API key | [Anthropic Console](https://console.anthropic.com) |

## Testing Your Deployment

1. Visit your Vercel app URL (provided after deployment)
2. Test with a YouTube video URL and competitor name
3. Verify the analysis works correctly
4. Test PDF export functionality

## Troubleshooting

### Common Issues:

1. **Import Errors**: Make sure all dependencies are in `requirements.txt`
2. **API Timeouts**: Consider reducing the number of comments analyzed
3. **Memory Errors**: Implement pagination for large datasets
4. **CORS Issues**: Add CORS headers if needed for frontend/backend separation

### Getting Help:
- Check Vercel deployment logs in the dashboard
- Monitor function execution in Vercel's Functions tab
- Use Vercel's preview deployments for testing

## Production Considerations

1. **Rate Limiting**: Implement rate limiting for API calls
2. **Caching**: Add caching for repeated video analyses
3. **Error Handling**: Enhance error handling and user feedback
4. **Monitoring**: Set up monitoring and alerting
5. **Security**: Implement additional security measures for production use

Your Competitor Intelligence Analyzer should now be live and accessible worldwide via your Vercel URL! 