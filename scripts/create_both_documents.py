#!/usr/bin/env python3
"""
Create both PDF and Word documents
"""

import os
import sys
import subprocess
from pathlib import Path

def create_pdf():
    """Create PDF from HTML report"""
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    html_file = 'documentation_report.html'
    pdf_file = 'GeoAI_Assistant_Pro_Report.pdf'
    
    if not os.path.exists(html_file):
        print(f"❌ Error: {html_file} not found")
        return False
    
    print("📄 Creating PDF Report...")
    
    # Chrome paths
    chrome_paths = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ]
    
    chrome = None
    for path in chrome_paths:
        if os.path.exists(path):
            chrome = path
            break
    
    if not chrome:
        print("⚠️  Chrome not found - PDF creation skipped")
        print("💡 Manual: Open documentation_report.html → Print → Save as PDF")
        return False
    
    html_path = os.path.abspath(html_file)
    pdf_path = os.path.abspath(pdf_file)
    
    try:
        result = subprocess.run([
            chrome,
            '--headless',
            '--disable-gpu',
            '--no-pdf-header-footer',
            f'--print-to-pdf={pdf_path}',
            f'file://{html_path}'
        ], capture_output=True, timeout=60)
        
        if os.path.exists(pdf_file):
            size = os.path.getsize(pdf_file) / 1024
            print(f"✅ PDF created: {pdf_file} ({size:.1f} KB)")
            return True
        else:
            print("⚠️  PDF creation failed")
            return False
            
    except Exception as e:
        print(f"⚠️  Error: {e}")
        print("💡 Manual: Open documentation_report.html → Print → Save as PDF")
        return False

def create_word():
    """Create Word document from README.md"""
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    readme_file = 'README.md'
    word_file = 'GeoAI_Assistant_Pro_Documentation.docx'
    
    if not os.path.exists(readme_file):
        print(f"❌ Error: {readme_file} not found")
        return False
    
    print("\n📝 Creating Word Document...")
    
    # Check if pandoc is available
    try:
        subprocess.run(['pandoc', '--version'], 
                      capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("⚠️  pandoc not found - Word creation skipped")
        print("💡 Install: brew install pandoc")
        print("   Or use: Open README.md in Typora → Export → Word")
        return False
    
    try:
        result = subprocess.run([
            'pandoc',
            readme_file,
            '-o', word_file,
            '--toc',
            '--toc-depth=3',
            '--reference-doc=/System/Library/Templates/Blank.docx'
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0 and os.path.exists(word_file):
            size = os.path.getsize(word_file) / 1024
            print(f"✅ Word created: {word_file} ({size:.1f} KB)")
            return True
        else:
            # Try without reference doc
            result = subprocess.run([
                'pandoc',
                readme_file,
                '-o', word_file,
                '--toc',
                '--toc-depth=3'
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0 and os.path.exists(word_file):
                size = os.path.getsize(word_file) / 1024
                print(f"✅ Word created: {word_file} ({size:.1f} KB)")
                return True
            else:
                print(f"⚠️  Word creation failed: {result.stderr}")
                return False
                
    except Exception as e:
        print(f"⚠️  Error: {e}")
        print("💡 Manual: Use pandoc or Typora to convert README.md")
        return False

def main():
    print("🚀 Creating PDF and Word Documents")
    print("="*60)
    
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    print(f"📁 Working directory: {script_dir}\n")
    
    # Create PDF
    pdf_success = create_pdf()
    
    # Create Word
    word_success = create_word()
    
    # Summary
    print("\n" + "="*60)
    print("📊 Summary:")
    print("="*60)
    
    if pdf_success:
        print("✅ PDF: GeoAI_Assistant_Pro_Report.pdf")
    else:
        print("⚠️  PDF: Not created (use manual method)")
        print("   → Open documentation_report.html → Print → Save as PDF")
    
    if word_success:
        print("✅ Word: GeoAI_Assistant_Pro_Documentation.docx")
    else:
        print("⚠️  Word: Not created (install pandoc or use Typora)")
        print("   → Install: brew install pandoc")
        print("   → Or: Open README.md in Typora → Export → Word")
    
    print("="*60)
    
    if pdf_success and word_success:
        print("\n🎉 Both documents created successfully!")
        return 0
    elif pdf_success or word_success:
        print("\n⚠️  One document created. See instructions above for the other.")
        return 1
    else:
        print("\n❌ No documents created. Please use manual methods.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

