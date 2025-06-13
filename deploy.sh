#!/bin/bash

echo "🚀 Deploying Competitor Intelligence Analyzer to Vercel..."

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI is not installed. Installing now..."
    npm install -g vercel
fi

# Deploy to Vercel
echo "📦 Starting deployment..."
vercel --prod

echo "✅ Deployment complete!"
echo ""
echo "🔧 Don't forget to configure your environment variables in Vercel:"
echo "   - YOUTUBE_API_KEY"
echo "   - ANTHROPIC_API_KEY"
echo ""
echo "📖 See README-VERCEL.md for detailed instructions." 