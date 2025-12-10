#!/bin/bash
# Script to commit changes and push to GitHub

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Git Commit and Push Script${NC}"
echo "=================================="

# Navigate to project directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "\n${BLUE}📁 Working directory:${NC} $SCRIPT_DIR"

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo -e "\n${YELLOW}⚠️  Git repository not initialized${NC}"
    echo "Initializing git repository..."
    git init
    echo -e "${GREEN}✅ Git repository initialized${NC}"
fi

# Check git status
echo -e "\n${BLUE}📊 Checking git status...${NC}"
git status --short

# Check if there are changes
if [ -z "$(git status --porcelain)" ]; then
    echo -e "\n${YELLOW}⚠️  No changes to commit${NC}"
    exit 0
fi

# Check if .gitignore exists
if [ ! -f ".gitignore" ]; then
    echo -e "\n${YELLOW}⚠️  .gitignore not found${NC}"
    echo "Creating .gitignore..."
    cat > .gitignore << 'EOF'
# Environment variables
.env

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
db_env/

# QGIS temporary files
*.qgs~
*.qgz~
*.sqlite-journal
*.bak
*.log

# Documentation outputs
*.pdf
*.docx
# Exclude all .html except the main documentation.html
*.html
!documentation.html

# Test results
TEST_RESULTS.md
EOF
    echo -e "${GREEN}✅ .gitignore created${NC}"
fi

# Stage all changes
echo -e "\n${BLUE}📦 Staging changes...${NC}"
git add .

# Show what will be committed
echo -e "\n${BLUE}📋 Files to be committed:${NC}"
git status --short

# Create commit message
COMMIT_MESSAGE="docs: Update documentation with fixed navbar and create PDF/DOCX guides

✨ Features:
- Updated documentation.html with fixed navbar and modern design
- Added smooth scrolling navigation
- Improved responsive layout with beautiful gradients
- Added back-to-top button and active section highlighting

📄 Documentation:
- Created comprehensive guides for PDF/DOCX generation
- Added INSTRUCTIONS_CREATE_DOCS.txt for quick reference
- Created HOW_TO_CREATE_DOCS.md with detailed methods
- Added README_DOCS.md for quick reference
- Created make_docs.py script for automated generation

🎨 UI Improvements:
- Fixed navbar stays visible when scrolling
- Modern gradient design with animations
- Professional styling and better UX
- Mobile-responsive layout

📝 Scripts:
- make_docs.py - Python script for automated doc generation
- create_docs.py - Alternative Python script
- QUICK_GENERATE_DOCS.sh - Bash script for quick generation

This update provides users with clear instructions and tools to create
professional PDF and Word documentation from the project files."

# Commit changes
echo -e "\n${BLUE}💾 Committing changes...${NC}"
git commit -m "$COMMIT_MESSAGE"

echo -e "\n${GREEN}✅ Changes committed successfully!${NC}"

# Check if remote exists
REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")

if [ -z "$REMOTE_URL" ]; then
    echo -e "\n${YELLOW}⚠️  No remote repository configured${NC}"
    echo "To add a remote repository, run:"
    echo "  git remote add origin <your-github-repo-url>"
    echo ""
    echo "Then run this script again to push."
    exit 0
fi

echo -e "\n${BLUE}🌐 Remote repository:${NC} $REMOTE_URL"

# Get current branch
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "main")

# If no branch exists, create main
if [ -z "$CURRENT_BRANCH" ]; then
    echo -e "\n${BLUE}🌿 Creating main branch...${NC}"
    git branch -M main
    CURRENT_BRANCH="main"
fi

echo -e "\n${BLUE}🌿 Current branch:${NC} $CURRENT_BRANCH"

# Ask for confirmation before pushing
echo -e "\n${YELLOW}⚠️  Ready to push to GitHub${NC}"
read -p "Push to origin/$CURRENT_BRANCH? (y/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "\n${BLUE}📤 Pushing to GitHub...${NC}"
    
    # Push to remote
    if git push -u origin "$CURRENT_BRANCH" 2>&1; then
        echo -e "\n${GREEN}✅ Successfully pushed to GitHub!${NC}"
        echo -e "${GREEN}🔗 Repository: $REMOTE_URL${NC}"
    else
        echo -e "\n${YELLOW}⚠️  Push failed. You may need to:${NC}"
        echo "  1. Set up remote: git remote add origin <your-repo-url>"
        echo "  2. Or pull first: git pull origin $CURRENT_BRANCH --rebase"
        echo "  3. Or force push (if you're sure): git push -u origin $CURRENT_BRANCH --force"
    fi
else
    echo -e "\n${YELLOW}⏭️  Push cancelled${NC}"
    echo "You can push manually later with:"
    echo "  git push -u origin $CURRENT_BRANCH"
fi

echo -e "\n${GREEN}✅ Done!${NC}"

