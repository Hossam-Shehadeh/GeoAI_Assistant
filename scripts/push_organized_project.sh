#!/bin/bash
# Push organized project to GitHub with commit message

set -e

echo "🚀 Pushing Organized Project to GitHub"
echo "========================================"
echo ""

# Navigate to project directory
cd "/Users/me/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/GeoAI_Assistant"

echo "📁 Working directory: $(pwd)"
echo ""

# Check git status
echo "📊 Current git status:"
git status --short
echo ""

# Branch name
BRANCH_NAME="feature/organize-project-structure"

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

echo ""
echo "📋 Files to be committed:"
git status --short | head -20
echo ""

# Commit message
COMMIT_MSG="docs: Organize project structure with comprehensive README

✨ Major Organization:
- Organized all documentation files into docs/ folder (35 files)
- Moved all utility scripts to scripts/ folder (13 files)
- Created media/ folder with renamed demo files (5 files)
- Removed duplicate and temporary files
- Cleaned up project structure

📚 Documentation:
- Created comprehensive README.md with workflow diagrams
- Added PROJECT_STRUCTURE.md documentation
- Added QUICK_START.md guide
- Organized all existing documentation files
- Included media files (screenshots & videos) in README

🔧 Scripts:
- Organized all .sh and utility .py scripts into scripts/
- Maintained all existing functionality

🎬 Media:
- Renamed and organized demo screenshots
- Renamed and organized workflow videos
- All media properly referenced in README

📁 Structure:
- docs/ - All documentation (35 files)
- scripts/ - All utility scripts (13 files)
- media/ - All media files (5 files)
- Clean root directory with essential files only

🎨 README Features:
- Beautiful header with badges
- Complete feature list
- Installation guide
- Quick start instructions
- Detailed workflow diagrams with media
- Architecture overview
- Usage examples
- Configuration guide
- Contributing guidelines

✅ Files Added:
- LICENSE (MIT)
- .env.example (environment template)
- Updated .gitignore
- Comprehensive README.md
- Organized folder structure"

# Commit
echo "💾 Committing changes..."
git commit -m "$COMMIT_MSG"

echo ""
echo "✅ Changes committed successfully!"
echo ""

# Check remote
REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")

if [ -z "$REMOTE_URL" ]; then
    echo "⚠️  No remote repository configured"
    echo ""
    echo "To add a remote repository, run:"
    echo "  git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
    echo ""
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
echo "========================================"

