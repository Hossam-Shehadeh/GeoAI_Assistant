#!/usr/bin/env python3
"""
Generate PDF report from HTML using Chrome headless
"""

import os
import sys
import subprocess
from pathlib import Path

def generate_pdf():
    """Generate PDF from HTML report"""
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    html_file = 'documentation_report.html'
    pdf_file = 'GeoAI_Assistant_Pro_Report.pdf'
    
    if not os.path.exists(html_file):
        print(f"❌ Error: {html_file} not found")
        return False
    
    print("🚀 Generating PDF Report...")
    print("="*60)
    
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
        print("❌ Chrome not found")
        print("💡 Please install Chrome or use manual method:")
        print("   1. Open documentation_report.html in browser")
        print("   2. Press Cmd+P → Save as PDF")
        return False
    
    html_path = os.path.abspath(html_file)
    pdf_path = os.path.abspath(pdf_file)
    
    try:
        print(f"📄 Converting {html_file} to PDF...")
        print(f"📁 Output: {pdf_file}")
        
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
            print(f"\n✅ PDF Report created successfully!")
            print(f"   File: {pdf_file}")
            print(f"   Size: {size:.1f} KB")
            print("="*60)
            return True
        else:
            print("❌ PDF generation failed")
            print(f"Error: {result.stderr.decode() if result.stderr else 'Unknown error'}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Manual method:")
        print("   1. Open documentation_report.html in browser")
        print("   2. Press Cmd+P → Save as PDF")
        return False

if __name__ == "__main__":
    success = generate_pdf()
    sys.exit(0 if success else 1)

