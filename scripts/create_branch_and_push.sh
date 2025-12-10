#!/bin/bash
# Create new branch and push to GitHub

set -e

echo "🚀 Creating New Branch and Pushing to GitHub"
echo "============================================"

# Navigate to project directory
cd "/Users/me/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/spatial-projects/GeoAI_Assistant_Pro_Clean"

echo "📁 Working directory: $(pwd)"
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "⚠️  Git repository not initialized"
    echo "Initializing git repository..."
    git init
    echo "✅ Git repository initialized"
    echo ""
fi

# Check current status
echo "📊 Current git status:"
git status --short
echo ""

# Branch name
BRANCH_NAME="feature/pdf-documentation-updates"

# Check if branch exists
if git show-ref --verify --quiet refs/heads/$BRANCH_NAME; then
    echo "⚠️  Branch $BRANCH_NAME already exists"
    echo "Switching to existing branch..."
    git checkout $BRANCH_NAME
else
    echo "🌿 Creating new branch: $BRANCH_NAME"
    git checkout -b $BRANCH_NAME
fi

echo ""

# Stage all changes
echo "📦 Staging all changes..."
git add .

# Show what will be committed
echo ""
echo "📋 Files to be committed:"
git status --short
echo ""

# Commit message
COMMIT_MSG="docs: Add PDF report and documentation updates

✨ Features:
- Created professional PDF report (GeoAI_Assistant_Pro_Report.pdf)
- Added PDF generation script (create_both_documents.py)
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
- create_both_documents.py - Automated PDF/Word generation
- generate_pdf_report.py - PDF generation
- push_new_branch.sh - GitHub push automation
- quick_push.sh - Quick push script

📝 Documentation:
- CREATE_PDF_REPORT.txt - PDF report instructions
- CREATE_PDF_DOCX.txt - PDF/DOCX creation guide
- QUICK_CREATE_FILES.md - Quick file creation guide
- GENERATE_PDF_AND_PUSH.md - Complete guide
- PUSH_GITHUB_SIMPLE.txt - Simple push instructions

🎨 UI Improvements:
- Download buttons moved to footer
- PDF button opens print dialog directly
- Enhanced print styles for professional output
- Better user experience for document generation"

# Commit
echo "💾 Committing changes..."
git commit -m "$COMMIT_MSG"

echo "✅ Changes committed successfully!"
echo ""

# Check if remote exists
REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")

if [ -z "$REMOTE_URL" ]; then
    echo "⚠️  No remote repository configured"
    echo ""
    echo "To add a remote repository, run:"
    echo "  git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
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
    echo "   1. Go to GitHub: $REMOTE_URL"
    echo "   2. You'll see a banner to create a Pull Request"
    echo "   3. Click 'Compare & pull request'"
    echo "   4. Review the changes"
    echo "   5. Merge to main branch when ready"
    echo ""
else
    echo ""
    echo "⚠️  Push failed. Possible solutions:"
    echo ""
    echo "1. If remote doesn't exist:"
    echo "   git remote add origin <your-repo-url>"
    echo ""
    echo "2. If branch exists on remote:"
    echo "   git pull origin $BRANCH_NAME --rebase"
    echo "   Then push again"
    echo ""
    echo "3. Check your internet connection and GitHub access"
fi

echo ""
echo "✅ Done!"
echo "============================================"


