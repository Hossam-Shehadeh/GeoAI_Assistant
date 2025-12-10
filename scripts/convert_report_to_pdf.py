#!/usr/bin/env python3
"""
Convert REPORT.md to PDF with formal technical/scientific report formatting
Uses pandoc with LaTeX or Chrome headless with technical HTML template
"""

import os
import sys
import subprocess
import re
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

def create_technical_html_template(md_content, project_root):
    """Create HTML template for technical report"""
    
    # Convert markdown to HTML (simple conversion)
    html_content = md_content
    
    # Replace \newpage with page break
    html_content = html_content.replace('\\newpage', '<div style="page-break-before: always;"></div>')
    
    # Replace markdown headers
    html_content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html_content, flags=re.MULTILINE)
    
    # Replace markdown images
    html_content = re.sub(
        r'!\[([^\]]*)\]\(([^)]+)\)',
        lambda m: f'<figure style="text-align: center; margin: 20px 0; page-break-inside: avoid;"><img src="{m.group(2)}" alt="{m.group(1)}" style="max-width: 90%; height: auto; border: 1px solid #ddd; padding: 5px;"><figcaption style="font-style: italic; color: #666; margin-top: 10px;">{m.group(1)}</figcaption></figure>',
        html_content
    )
    
    # Replace markdown code blocks
    html_content = re.sub(
        r'```(\w+)?\n(.*?)```',
        lambda m: f'<pre style="background: #f5f5f5; border: 1px solid #ddd; padding: 15px; border-radius: 4px; overflow-x: auto; page-break-inside: avoid;"><code>{m.group(2)}</code></pre>',
        html_content,
        flags=re.DOTALL
    )
    
    # Replace inline code
    html_content = re.sub(r'`([^`]+)`', r'<code style="background: #f5f5f5; padding: 2px 4px; border-radius: 3px;">\1</code>', html_content)
    
    # Replace markdown tables
    def process_table(match):
        table_text = match.group(0)
        table_text = table_text.replace('|', '</td><td>')
        table_text = table_text.replace('\n', '</tr><tr>')
        return f'<table style="width: 100%; border-collapse: collapse; margin: 20px 0; page-break-inside: avoid;">{table_text}</table>'
    
    # Replace markdown lists
    html_content = re.sub(r'^- (.+)$', r'<li>\1</li>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^\d+\. (.+)$', r'<li>\1</li>', html_content, flags=re.MULTILINE)
    
    # Wrap lists
    html_content = re.sub(r'(<li>.*?</li>)', r'<ul>\1</ul>', html_content, flags=re.DOTALL)
    
    # Replace markdown bold
    html_content = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', html_content)
    
    # Replace markdown italic
    html_content = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', html_content)
    
    # Replace paragraphs
    html_content = re.sub(r'\n\n', '</p><p>', html_content)
    html_content = '<p>' + html_content + '</p>'
    
    technical_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>GeoAI Assistant Pro - Technical Report</title>
    <style>
        @page {{
            size: A4;
            margin: 2.5cm 2cm;
        }}
        
        body {{
            font-family: 'Times New Roman', Times, serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #000;
            max-width: 210mm;
            margin: 0 auto;
            padding: 0;
            background: white;
        }}
        
        h1 {{
            font-size: 18pt;
            font-weight: bold;
            margin-top: 24pt;
            margin-bottom: 12pt;
            page-break-after: avoid;
            border-bottom: 2px solid #000;
            padding-bottom: 6pt;
        }}
        
        h2 {{
            font-size: 14pt;
            font-weight: bold;
            margin-top: 18pt;
            margin-bottom: 10pt;
            page-break-after: avoid;
        }}
        
        h3 {{
            font-size: 12pt;
            font-weight: bold;
            margin-top: 14pt;
            margin-bottom: 8pt;
            page-break-after: avoid;
        }}
        
        h4 {{
            font-size: 11pt;
            font-weight: bold;
            margin-top: 12pt;
            margin-bottom: 6pt;
        }}
        
        p {{
            margin: 6pt 0;
            text-align: justify;
        }}
        
        ul, ol {{
            margin: 10pt 0;
            padding-left: 25pt;
        }}
        
        li {{
            margin: 4pt 0;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15pt 0;
            page-break-inside: avoid;
            font-size: 10pt;
        }}
        
        th {{
            background-color: #f0f0f0;
            border: 1px solid #000;
            padding: 8pt;
            text-align: left;
            font-weight: bold;
        }}
        
        td {{
            border: 1px solid #000;
            padding: 6pt;
        }}
        
        pre {{
            background: #f5f5f5;
            border: 1px solid #ddd;
            padding: 10pt;
            border-radius: 4px;
            overflow-x: auto;
            page-break-inside: avoid;
            font-family: 'Courier New', monospace;
            font-size: 9pt;
        }}
        
        code {{
            background: #f5f5f5;
            padding: 2pt 4pt;
            border-radius: 3pt;
            font-family: 'Courier New', monospace;
            font-size: 9pt;
        }}
        
        figure {{
            margin: 20pt 0;
            page-break-inside: avoid;
            text-align: center;
        }}
        
        img {{
            max-width: 90%;
            height: auto;
            border: 1px solid #ddd;
            padding: 5pt;
        }}
        
        figcaption {{
            font-style: italic;
            color: #666;
            margin-top: 8pt;
            font-size: 9pt;
        }}
        
        .page-break {{
            page-break-before: always;
        }}
        
        .cover-page {{
            page-break-after: always;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            padding: 40px;
            margin: 0;
        }}
        
        .cover-page h1 {{
            font-size: 32pt;
            font-weight: bold;
            margin: 0;
            padding: 0;
            border: none;
            color: #1a237e;
        }}
        
        .cover-page h2 {{
            font-size: 18pt;
            font-weight: normal;
            margin: 15px 0 0 0;
            padding: 0;
            color: #3949ab;
            font-style: italic;
        }}
        
        .cover-page h3 {{
            font-size: 14pt;
            font-weight: normal;
            margin: 10px 0 0 0;
            padding: 0;
            color: #5c6bc0;
        }}
        
        .cover-page img {{
            max-width: 70%;
            height: auto;
            border: 2px solid #ddd;
            padding: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            margin: 40px 0;
        }}
        
        .cover-page .footer {{
            margin-top: 60px;
            border-top: 2px solid #1a237e;
            padding-top: 30px;
            width: 80%;
        }}
        
        .cover-page .footer p {{
            margin: 10px 0;
            text-align: center;
        }}
        
        @media print {{
            body {{
                margin: 0;
                padding: 0;
            }}
            
            h1, h2, h3 {{
                page-break-after: avoid;
            }}
            
            figure, table, pre {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    {html_content}
</body>
</html>"""
    
    return technical_html

def convert_with_chrome_technical(md_file, pdf_file):
    """Convert Markdown to PDF using Chrome with technical HTML template"""
    try:
        print("📄 Converting with Chrome headless (Technical Report Format)...")
        
        project_root = Path(md_file).parent.absolute()
        md_content = Path(md_file).read_text(encoding='utf-8')
        
        # Create technical HTML
        html_content = create_technical_html_template(md_content, project_root)
        html_file = project_root / 'REPORT_technical.html'
        html_file.write_text(html_content, encoding='utf-8')
        
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
    
    print("🚀 Converting REPORT.md to PDF (Technical Report Format)...")
    print("="*60)
    print(f"📄 Input:  {md_file}")
    print(f"📄 Output: {pdf_file}")
    print("="*60)
    
    # Try Chrome with technical template
    if check_chrome():
        print("\n✅ Chrome found - using technical HTML template")
        if convert_with_chrome_technical(md_file, pdf_file):
            size = os.path.getsize(pdf_file) / 1024
            print(f"\n✅ PDF Report created successfully!")
            print(f"   File: {pdf_file}")
            print(f"   Size: {size:.1f} KB")
            print("="*60)
            return True
    
    # Manual instructions
    print("\n❌ No conversion tool found")
    print("\n💡 To create a formal technical PDF report:")
    print("   1. Install Chrome browser")
    print("   2. Or install pandoc + LaTeX for better quality")
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
