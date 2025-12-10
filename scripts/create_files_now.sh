#!/bin/bash
# Script to create PDF and Word files immediately

echo "🚀 Creating PDF and Word Documentation Files"
echo "============================================"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "📁 Working directory: $SCRIPT_DIR"
echo ""

# Create PDF
echo "📄 Creating PDF from HTML..."
if [ -f "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]; then
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
        --headless \
        --disable-gpu \
        --no-pdf-header-footer \
        --print-to-pdf="$SCRIPT_DIR/documentation.pdf" \
        "file://$SCRIPT_DIR/documentation.html" 2>/dev/null
    
    if [ -f "documentation.pdf" ]; then
        SIZE=$(du -h documentation.pdf | cut -f1)
        echo "✅ PDF created: documentation.pdf ($SIZE)"
    else
        echo "⚠️ PDF creation failed"
        echo "💡 Manual method: Open documentation.html → Print → Save as PDF"
    fi
else
    echo "⚠️ Chrome not found"
    echo "💡 Manual method: Open documentation.html → Print → Save as PDF"
fi

echo ""

# Create Word
echo "📝 Creating Word document from README.md..."
if command -v pandoc &> /dev/null; then
    pandoc README.md -o documentation.docx --toc --toc-depth=3 2>/dev/null
    
    if [ -f "documentation.docx" ]; then
        SIZE=$(du -h documentation.docx | cut -f1)
        echo "✅ Word created: documentation.docx ($SIZE)"
    else
        echo "⚠️ Word creation failed"
    fi
else
    echo "⚠️ pandoc not found"
    echo "💡 Install: brew install pandoc"
    echo "   Or use: Open README.md in Typora → Export → Word"
fi

echo ""
echo "============================================"
echo "📊 Summary:"
echo "============================================"

if [ -f "documentation.pdf" ]; then
    SIZE=$(du -h documentation.pdf | cut -f1)
    echo "✅ documentation.pdf ($SIZE)"
else
    echo "⚠️ documentation.pdf (not created)"
fi

if [ -f "documentation.docx" ]; then
    SIZE=$(du -h documentation.docx | cut -f1)
    echo "✅ documentation.docx ($SIZE)"
else
    echo "⚠️ documentation.docx (not created)"
fi

echo ""
echo "💡 If files were created, refresh the HTML page and try the download buttons!"
echo "============================================"

