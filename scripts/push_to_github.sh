#!/bin/bash
# Script to create new branch and push updates to GitHub

set -e

echo "🚀 Creating New Branch and Pushing to GitHub"
echo "=============================================="

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "📁 Working directory: $SCRIPT_DIR"
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "⚠️  Git repository not initialized"
    echo "Initializing git repository..."
    git init
    echo "✅ Git repository initialized"
    echo ""
fi

# Check current branch
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "")
if [ -z "$CURRENT_BRANCH" ]; then
    # No branch exists, create main
    git branch -M main
    CURRENT_BRANCH="main"
fi

echo "🌿 Current branch: $CURRENT_BRANCH"
echo ""

# Create new branch name
BRANCH_NAME="feature/pdf-documentation-updates"
echo "📝 Creating new branch: $BRANCH_NAME"

# Check if branch already exists
if git show-ref --verify --quiet refs/heads/$BRANCH_NAME; then
    echo "⚠️  Branch $BRANCH_NAME already exists"
    read -p "Switch to existing branch? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git checkout $BRANCH_NAME
    else
        echo "❌ Cancelled"
        exit 1
    fi
else
    git checkout -b $BRANCH_NAME
    echo "✅ Created and switched to branch: $BRANCH_NAME"
fi

echo ""

# Stage all changes
echo "📦 Staging changes..."
git add .

# Show what will be committed
echo ""
echo "📋 Files to be committed:"
git status --short

echo ""
read -p "Commit and push these changes? (y/n) " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cancelled"
    exit 1
fi

# Create commit message
COMMIT_MESSAGE="docs: Add PDF report and documentation updates

✨ Features:
- Created professional PDF report (documentation_report.html)
- Added PDF generation script (generate_pdf_report.py)
- Updated HTML documentation with download buttons in footer
- Enhanced print styles for better PDF output
- Added comprehensive documentation guides

📄 PDF Report:
- Professional cover page with gradient design
- Table of contents with page numbers
- Complete documentation sections
- Beautiful formatting optimized for PDF
- A4 page layout with proper margins

🔧 Scripts:
- generate_pdf_report.py - Automated PDF generation
- create_full_docs.py - Full documentation creation
- make_docs.py - Documentation generation utilities

📝 Documentation:
- CREATE_PDF_REPORT.txt - PDF report instructions
- CREATE_PDF_DOCX.txt - PDF/DOCX creation guide
- QUICK_CREATE_FILES.md - Quick file creation guide
- STEP_BY_STEP_CREATE_FILES.txt - Detailed instructions

🎨 UI Improvements:
- Download buttons moved to footer
- PDF button opens print dialog directly
- Enhanced print styles for professional output
- Better user experience for document generation"

# Commit changes
echo ""
echo "💾 Committing changes..."
git commit -m "$COMMIT_MESSAGE"

echo "✅ Changes committed successfully!"
echo ""

# Check if remote exists
REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")

if [ -z "$REMOTE_URL" ]; then
    echo "⚠️  No remote repository configured"
    echo ""
    echo "To add a remote repository, run:"
    echo "  git remote add origin <your-github-repo-url>"
    echo ""
    echo "Then run this script again to push."
    exit 0
fi

echo "🌐 Remote repository: $REMOTE_URL"
echo ""

# Push to GitHub
echo "📤 Pushing to GitHub..."
if git push -u origin $BRANCH_NAME 2>&1; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo ""
    echo "🔗 Branch: $BRANCH_NAME"
    echo "🔗 Repository: $REMOTE_URL"
    echo ""
    echo "💡 Next steps:"
    echo "   1. Go to GitHub and create a Pull Request"
    echo "   2. Review the changes"
    echo "   3. Merge to main branch"
    echo ""
else
    echo ""
    echo "⚠️  Push failed. You may need to:"
    echo "   1. Set up remote: git remote add origin <your-repo-url>"
    echo "   2. Or pull first: git pull origin $BRANCH_NAME --rebase"
    echo "   3. Or force push (if you're sure): git push -u origin $BRANCH_NAME --force"
fi

echo ""
echo "✅ Done!"
echo "=============================================="

