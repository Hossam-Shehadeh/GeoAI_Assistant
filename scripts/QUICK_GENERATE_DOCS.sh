#!/bin/bash
# Quick script to generate PDF and Word documentation

echo "🚀 Generating documentation files..."
echo "=================================="

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check for documentation.html
if [ ! -f "documentation.html" ]; then
    echo "❌ Error: documentation.html not found"
    exit 1
fi

# Generate PDF using Chrome (macOS)
if [ -f "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]; then
    echo ""
    echo "📄 Generating PDF from HTML..."
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
        --headless \
        --disable-gpu \
        --print-to-pdf="$SCRIPT_DIR/documentation.pdf" \
        "file://$SCRIPT_DIR/documentation.html" 2>/dev/null
    
    if [ -f "documentation.pdf" ]; then
        SIZE=$(du -h documentation.pdf | cut -f1)
        echo "✅ PDF created: documentation.pdf ($SIZE)"
    else
        echo "⚠️ PDF generation failed"
        echo "💡 Try: Open documentation.html → Print → Save as PDF"
    fi
else
    echo "⚠️ Chrome not found"
    echo "💡 Manual: Open documentation.html → Print → Save as PDF"
fi

# Generate Word using pandoc
if command -v pandoc &> /dev/null; then
    echo ""
    echo "📝 Generating Word document..."
    pandoc README.md -o documentation.docx --toc --toc-depth=3 2>/dev/null
    
    if [ -f "documentation.docx" ]; then
        SIZE=$(du -h documentation.docx | cut -f1)
        echo "✅ Word created: documentation.docx ($SIZE)"
    else
        echo "⚠️ Word generation failed"
    fi
else
    echo ""
    echo "⚠️ pandoc not found"
    echo "💡 Install: brew install pandoc"
    echo "   Or use: Open README.md in Typora → Export as Word"
fi

echo ""
echo "=================================="
echo "✅ Done!"
echo ""
echo "Files created:"
[ -f "documentation.pdf" ] && echo "  📄 documentation.pdf"
[ -f "documentation.docx" ] && echo "  📝 documentation.docx"

