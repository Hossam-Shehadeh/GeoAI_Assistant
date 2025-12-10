#!/usr/bin/env python3
"""
Create full PDF and Word documentation files
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("🚀 Creating Full PDF and Word Documentation\n")
    print("="*60)
    
    # Change to script directory
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    print(f"📁 Working directory: {script_dir}\n")
    
    # Check for source files
    if not os.path.exists('documentation.html'):
        print("❌ Error: documentation.html not found")
        return
    
    if not os.path.exists('README.md'):
        print("❌ Error: README.md not found")
        return
    
    # Create PDF
    print("📄 Creating PDF from HTML...")
    pdf_created = False
    
    # Method 1: Chrome headless
    chrome_paths = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ]
    
    for chrome in chrome_paths:
        if os.path.exists(chrome):
            try:
                html_path = os.path.abspath('documentation.html')
                pdf_path = os.path.abspath('documentation.pdf')
                
                result = subprocess.run([
                    chrome,
                    '--headless',
                    '--disable-gpu',
                    '--no-pdf-header-footer',
                    f'--print-to-pdf={pdf_path}',
                    f'file://{html_path}'
                ], capture_output=True, timeout=60)
                
                if os.path.exists('documentation.pdf'):
                    size = os.path.getsize('documentation.pdf') / 1024
                    print(f"✅ PDF created: documentation.pdf ({size:.1f} KB)")
                    pdf_created = True
                    break
            except Exception as e:
                print(f"⚠️ Chrome method failed: {e}")
                continue
    
    if not pdf_created:
        print("⚠️ PDF: Could not generate automatically")
        print("   💡 Manual: Open documentation.html → Print → Save as PDF")
    
    # Create Word
    print("\n📝 Creating Word document from README.md...")
    docx_created = False
    
    # Method 1: pandoc
    try:
        result = subprocess.run(
            ['pandoc', 'README.md', '-o', 'documentation.docx', 
             '--toc', '--toc-depth=3', '--reference-doc=/System/Library/Templates/Blank.docx'],
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0 and os.path.exists('documentation.docx'):
            size = os.path.getsize('documentation.docx') / 1024
            print(f"✅ Word created: documentation.docx ({size:.1f} KB)")
            docx_created = True
        else:
            # Try without reference doc
            result = subprocess.run(
                ['pandoc', 'README.md', '-o', 'documentation.docx', 
                 '--toc', '--toc-depth=3'],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode == 0 and os.path.exists('documentation.docx'):
                size = os.path.getsize('documentation.docx') / 1024
                print(f"✅ Word created: documentation.docx ({size:.1f} KB)")
                docx_created = True
    except FileNotFoundError:
        print("⚠️ pandoc not found")
    except Exception as e:
        print(f"⚠️ Error: {e}")
    
    if not docx_created:
        print("   💡 Install pandoc: brew install pandoc")
        print("   Or use: Open README.md in Typora → Export → Word")
    
    # Summary
    print("\n" + "="*60)
    print("📊 Summary:")
    print("="*60)
    
    files_created = []
    if os.path.exists('documentation.pdf'):
        size = os.path.getsize('documentation.pdf') / 1024
        files_created.append(f"✅ documentation.pdf ({size:.1f} KB)")
    else:
        files_created.append("⚠️ documentation.pdf (not created)")
    
    if os.path.exists('documentation.docx'):
        size = os.path.getsize('documentation.docx') / 1024
        files_created.append(f"✅ documentation.docx ({size:.1f} KB)")
    else:
        files_created.append("⚠️ documentation.docx (not created)")
    
    for file_info in files_created:
        print(f"   {file_info}")
    
    print("\n💡 Download buttons in HTML will work once files are created")
    print("="*60)

if __name__ == "__main__":
    main()

