#!/usr/bin/env python3
"""
Generate PDF and Word documentation from README.md and documentation.html
"""

import subprocess
import sys
import os

def check_tool(tool_name, install_cmd=None):
    """Check if a tool is available"""
    try:
        subprocess.run([tool_name, "--version"], 
                      capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        if install_cmd:
            print(f"⚠️ {tool_name} not found. Install: {install_cmd}")
        return False

def generate_pdf_from_html():
    """Generate PDF from HTML using Chrome headless"""
    html_path = os.path.join(os.getcwd(), 'documentation.html')
    pdf_path = os.path.join(os.getcwd(), 'documentation.pdf')
    
    # Try different Chrome paths
    chrome_paths = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "google-chrome",
        "chromium-browser"
    ]
    
    for chrome_path in chrome_paths:
        if os.path.exists(chrome_path) or check_tool(chrome_path.split('/')[-1]):
            try:
                subprocess.run([
                    chrome_path,
                    "--headless",
                    "--disable-gpu",
                    f"--print-to-pdf={pdf_path}",
                    f"file://{html_path}"
                ], check=True, capture_output=True)
                print(f"✅ PDF generated: {pdf_path}")
                return True
            except Exception as e:
                continue
    
    print("⚠️ Could not generate PDF automatically")
    print("💡 Manual method: Open documentation.html in browser → Print → Save as PDF")
    return False

def generate_pdf_from_markdown():
    """Generate PDF from Markdown using pandoc"""
    if not check_tool("pandoc", "brew install pandoc"):
        return False
    
    try:
        subprocess.run([
            "pandoc",
            "README.md",
            "-o", "documentation.pdf",
            "--pdf-engine=xelatex",
            "--toc",
            "--toc-depth=3"
        ], check=True)
        print("✅ PDF generated from Markdown: documentation.pdf")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️ PDF generation failed: {e}")
        print("💡 Try: pandoc README.md -o documentation.pdf --pdf-engine=wkhtmltopdf")
        return False

def generate_docx():
    """Generate Word document from Markdown using pandoc"""
    if not check_tool("pandoc", "brew install pandoc"):
        return False
    
    try:
        subprocess.run([
            "pandoc",
            "README.md",
            "-o", "documentation.docx",
            "--toc",
            "--toc-depth=3"
        ], check=True)
        print("✅ Word document generated: documentation.docx")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Word generation failed: {e}")
        return False

def main():
    print("🚀 Generating documentation files...\n")
    print("="*60)
    
    # Generate PDF
    print("\n📄 Generating PDF...")
    pdf_success = generate_pdf_from_html()
    if not pdf_success:
        pdf_success = generate_pdf_from_markdown()
    
    # Generate Word
    print("\n📝 Generating Word document...")
    docx_success = generate_docx()
    
    # Summary
    print("\n" + "="*60)
    print("📊 Summary:")
    print("="*60)
    
    if pdf_success:
        print("✅ PDF: documentation.pdf")
    else:
        print("⚠️ PDF: Use browser Print → Save as PDF")
        print("   Or: pandoc README.md -o documentation.pdf")
    
    if docx_success:
        print("✅ Word: documentation.docx")
    else:
        print("⚠️ Word: Use pandoc or manual conversion")
        print("   Or: pandoc README.md -o documentation.docx")
    
    print("\n💡 See CREATE_DOCUMENTATION.md for detailed instructions")
    print("="*60)

if __name__ == "__main__":
    main()

