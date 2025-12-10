#!/usr/bin/env python3
"""
Convert REPORT.md to PDF with images support
Uses pandoc or Chrome headless
"""

import os
import sys
import subprocess
from pathlib import Path

def check_pandoc():
    """Check if pandoc is installed"""
    try:
        result = subprocess.run(['pandoc', '--version'], 
                              capture_output=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def check_chrome():
    """Check if Chrome is available"""
    chrome_paths = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ]
    for path in chrome_paths:
        if os.path.exists(path):
            return path
    return None

def convert_with_pandoc(md_file, pdf_file):
    """Convert Markdown to PDF using pandoc"""
    try:
        print("📄 Converting with pandoc...")
        
        # Convert images to absolute paths in markdown
        md_content = Path(md_file).read_text(encoding='utf-8')
        project_root = Path(md_file).parent.absolute()
        
        # Replace relative image paths with absolute paths
        import re
        def replace_image_path(match):
            img_path = match.group(1)
            if not img_path.startswith('/'):
                abs_path = project_root / img_path
                return f'![{match.group(2)}]({abs_path})'
            return match.group(0)
        
        md_content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_image_path, md_content)
        
        # Write temporary markdown with absolute paths
        temp_md = project_root / 'REPORT_temp.md'
        temp_md.write_text(md_content, encoding='utf-8')
        
        # Convert with pandoc
        result = subprocess.run([
            'pandoc',
            str(temp_md),
            '-o', str(pdf_file),
            '--pdf-engine=xelatex',
            '--variable=geometry:margin=1in',
            '--variable=fontsize:11pt',
            '--variable=mainfont:DejaVu Sans',
            '--toc',
            '--toc-depth=3',
            '--highlight-style=tango',
            '--metadata=title:"GeoAI Assistant Pro - Enterprise Report"',
            '--metadata=author:"GeoAI Assistant Pro Development Team"',
            '--metadata=date:"December 2024"',
        ], capture_output=True, timeout=120, cwd=str(project_root))
        
        # Clean up temp file
        if temp_md.exists():
            temp_md.unlink()
        
        if result.returncode == 0 and os.path.exists(pdf_file):
            return True
        else:
            print(f"❌ Pandoc error: {result.stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Error with pandoc: {e}")
        return False

def convert_with_chrome(md_file, pdf_file):
    """Convert Markdown to PDF using Chrome (via HTML)"""
    try:
        print("📄 Converting with Chrome headless...")
        
        # First convert MD to HTML using markdown or pandoc
        html_file = Path(md_file).with_suffix('.html')
        project_root = Path(md_file).parent.absolute()
        
        # Try to convert MD to HTML
        if check_pandoc():
            subprocess.run(['pandoc', str(md_file), '-o', str(html_file), 
                          '--standalone', '--css=github-markdown.css'],
                         cwd=str(project_root), timeout=30)
        else:
            # Simple HTML wrapper
            md_content = Path(md_file).read_text(encoding='utf-8')
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>GeoAI Assistant Pro - Enterprise Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        img {{ max-width: 100%; height: auto; }}
        h1, h2, h3 {{ color: #2c3e50; }}
        code {{ background: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
        pre {{ background: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
    </style>
</head>
<body>
{md_content}
</body>
</html>"""
            html_file.write_text(html_content, encoding='utf-8')
        
        if not html_file.exists():
            print("❌ Failed to create HTML file")
            return False
        
        # Convert HTML to PDF with Chrome
        chrome = check_chrome()
        if not chrome:
            print("❌ Chrome not found")
            return False
        
        html_path = html_file.absolute()
        pdf_path = Path(pdf_file).absolute()
        
        result = subprocess.run([
            chrome,
            '--headless',
            '--disable-gpu',
            '--no-pdf-header-footer',
            f'--print-to-pdf={pdf_path}',
            f'file://{html_path}'
        ], capture_output=True, timeout=60)
        
        # Clean up HTML file
        if html_file.exists():
            html_file.unlink()
        
        if os.path.exists(pdf_file):
            return True
        else:
            print(f"❌ Chrome conversion error: {result.stderr.decode() if result.stderr else 'Unknown'}")
            return False
            
    except Exception as e:
        print(f"❌ Error with Chrome: {e}")
        return False

def main():
    """Main conversion function"""
    script_dir = Path(__file__).parent.absolute()
    project_root = script_dir.parent
    
    md_file = project_root / 'REPORT.md'
    pdf_file = project_root / 'REPORT.pdf'
    
    if not md_file.exists():
        print(f"❌ Error: {md_file} not found")
        return False
    
    print("🚀 Converting REPORT.md to PDF...")
    print("="*60)
    print(f"📄 Input:  {md_file}")
    print(f"📄 Output: {pdf_file}")
    print("="*60)
    
    # Try pandoc first
    if check_pandoc():
        print("\n✅ Pandoc found - using pandoc for conversion")
        if convert_with_pandoc(md_file, pdf_file):
            size = os.path.getsize(pdf_file) / 1024
            print(f"\n✅ PDF Report created successfully!")
            print(f"   File: {pdf_file}")
            print(f"   Size: {size:.1f} KB")
            print("="*60)
            return True
    
    # Try Chrome as fallback
    if check_chrome():
        print("\n✅ Chrome found - using Chrome headless for conversion")
        if convert_with_chrome(md_file, pdf_file):
            size = os.path.getsize(pdf_file) / 1024
            print(f"\n✅ PDF Report created successfully!")
            print(f"   File: {pdf_file}")
            print(f"   Size: {size:.1f} KB")
            print("="*60)
            return True
    
    # Manual instructions
    print("\n❌ No conversion tool found")
    print("\n💡 Manual conversion options:")
    print("   1. Install pandoc: brew install pandoc (macOS)")
    print("   2. Use online converter: https://www.markdowntopdf.com/")
    print("   3. Use VS Code with 'Markdown PDF' extension")
    print("   4. Use Chrome: Open REPORT.md → Print → Save as PDF")
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

