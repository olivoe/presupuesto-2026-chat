#!/bin/bash

# Deploy Presupuesto 2026 Chat to GitHub + Vercel

echo "======================================================================"
echo "  Presupuesto 2026 AI Chat - GitHub + Vercel Deployment"
echo "======================================================================"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

echo "✅ Git found: $(git --version)"
echo ""

# Get GitHub username
echo "📝 Setup Information"
echo "===================="
echo ""
read -p "Enter your GitHub username: " GITHUB_USERNAME

if [ -z "$GITHUB_USERNAME" ]; then
    echo "❌ GitHub username is required"
    exit 1
fi

echo ""
echo "📋 Summary:"
echo "  GitHub Repository: https://github.com/$GITHUB_USERNAME/presupuesto-2026-chat"
echo ""
read -p "Continue? (y/N) " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "🚀 Initializing Git repository..."

# Initialize git if not already
if [ ! -d ".git" ]; then
    git init
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

# Add all files
echo "📦 Adding files..."
git add .

# Create first commit
echo "💾 Creating commit..."
git commit -m "Initial commit: Presupuesto 2026 AI Chat for Vercel" || echo "✅ No changes to commit"

# Set up remote
echo "🔗 Setting up GitHub remote..."
git remote remove origin 2>/dev/null
git remote add origin "https://github.com/$GITHUB_USERNAME/presupuesto-2026-chat.git"

echo ""
echo "======================================================================"
echo "✅ REPOSITORY READY!"
echo "======================================================================"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1️⃣  Create GitHub Repository:"
echo "   - Go to: https://github.com/new"
echo "   - Repository name: presupuesto-2026-chat"
echo "   - Visibility: Private (recommended)"
echo "   - DON'T initialize with README"
echo "   - Click 'Create repository'"
echo ""
echo "2️⃣  Push to GitHub:"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3️⃣  Deploy to Vercel:"
echo "   - Go to: https://vercel.com"
echo "   - Sign up/login with GitHub"
echo "   - Click 'Import Project'"
echo "   - Select 'presupuesto-2026-chat'"
echo "   - Add Environment Variable:"
echo "     OPENAI_API_KEY = your_api_key_here"
echo "   - Click 'Deploy'"
echo ""
echo "4️⃣  Add Custom Domain (optional):"
echo "   - In Vercel: Settings → Domains"
echo "   - Add: ai.protosapiens.me"
echo "   - Update DNS as instructed"
echo ""
echo "======================================================================"
echo ""
echo "📚 Full Guide: See VERCEL_DEPLOYMENT.md"
echo ""

