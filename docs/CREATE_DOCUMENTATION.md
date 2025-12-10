# 📄 Creating Documentation Files

This guide explains how to create PDF and Word documentation from the HTML and Markdown files.

---

## 📋 Available Documentation Files

- ✅ **README.md** - Complete Markdown documentation
- ✅ **documentation.html** - Beautiful HTML documentation
- 📄 **documentation.pdf** - PDF version (to be created)
- 📝 **documentation.docx** - Word version (to be created)

---

## 🔄 Creating PDF from HTML

### Method 1: Using Browser (Easiest)

1. **Open** `documentation.html` in your web browser
2. **Print** (Ctrl+P / Cmd+P)
3. **Select** "Save as PDF"
4. **Save** as `documentation.pdf`

### Method 2: Using Command Line (macOS)

```bash
# Using wkhtmltopdf (install: brew install wkhtmltopdf)
wkhtmltopdf documentation.html documentation.pdf

# Using Chrome/Chromium headless
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless --disable-gpu --print-to-pdf=documentation.pdf \
  documentation.html
```

### Method 3: Using Python

```python
# Install: pip install weasyprint
from weasyprint import HTML
HTML('documentation.html').write_pdf('documentation.pdf')
```

### Method 4: Using pandoc

```bash
# Install: brew install pandoc
pandoc README.md -o documentation.pdf --pdf-engine=xelatex
```

---

## 📝 Creating Word Document

### Method 1: Using pandoc (Recommended)

```bash
# Install: brew install pandoc
pandoc README.md -o documentation.docx

# With styling
pandoc README.md -o documentation.docx \
  --reference-doc=template.docx
```

### Method 2: Using Python (python-docx)

```python
# Install: pip install python-docx markdown
import markdown
from docx import Document
from docx.shared import Inches

# Read markdown
with open('README.md', 'r') as f:
    md_content = f.read()

# Convert to HTML
html = markdown.markdown(md_content)

# Create Word document
doc = Document()
doc.add_heading('GeoAI Assistant Pro', 0)

# Add content (simplified - you'd need to parse HTML properly)
doc.add_paragraph(html)

doc.save('documentation.docx')
```

### Method 3: Manual Conversion

1. **Open** `README.md` in a Markdown editor (Typora, Mark Text, etc.)
2. **Export** as Word (.docx)
3. **Save** as `documentation.docx`

### Method 4: Using LibreOffice

1. **Open** `documentation.html` in LibreOffice Writer
2. **File** → **Save As** → **Word Document (.docx)**
3. **Save** as `documentation.docx`

---

## 🎨 Creating Styled Word Template

For better Word document formatting, create a reference template:

1. **Create** a Word document with desired styles
2. **Save** as `template.docx`
3. **Use** with pandoc:
   ```bash
   pandoc README.md -o documentation.docx --reference-doc=template.docx
   ```

---

## 📦 Quick Script to Generate All Formats

Create `generate_docs.py`:

```python
#!/usr/bin/env python3
"""
Generate all documentation formats from README.md
"""

import subprocess
import sys
import os

def generate_pdf():
    """Generate PDF from HTML"""
    try:
        # Try Chrome headless
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if os.path.exists(chrome_path):
            subprocess.run([
                chrome_path,
                "--headless",
                "--disable-gpu",
                f"--print-to-pdf={os.path.join(os.getcwd(), 'documentation.pdf')}",
                f"file://{os.path.join(os.getcwd(), 'documentation.html')}"
            ])
            print("✅ PDF generated using Chrome")
            return True
    except Exception as e:
        print(f"⚠️ PDF generation failed: {e}")
        print("💡 Try opening documentation.html in browser and Print → Save as PDF")
    return False

def generate_docx():
    """Generate Word document from Markdown"""
    try:
        subprocess.run([
            "pandoc",
            "README.md",
            "-o", "documentation.docx",
            "--toc",
            "--toc-depth=3"
        ], check=True)
        print("✅ Word document generated using pandoc")
        return True
    except subprocess.CalledProcessError:
        print("⚠️ pandoc not found. Install: brew install pandoc")
        print("💡 Or use manual conversion method")
    except Exception as e:
        print(f"⚠️ Word generation failed: {e}")
    return False

if __name__ == "__main__":
    print("🚀 Generating documentation files...\n")
    
    pdf_success = generate_pdf()
    docx_success = generate_docx()
    
    print("\n" + "="*50)
    if pdf_success:
        print("✅ PDF: documentation.pdf")
    else:
        print("⚠️ PDF: Use browser Print → Save as PDF")
    
    if docx_success:
        print("✅ Word: documentation.docx")
    else:
        print("⚠️ Word: Use pandoc or manual conversion")
    print("="*50)
```

**Run:**
```bash
python3 generate_docs.py
```

---

## 📚 Recommended Tools

### For PDF:
- **Browser Print** (Easiest)
- **wkhtmltopdf** (Command line)
- **weasyprint** (Python library)
- **pandoc** (Universal converter)

### For Word:
- **pandoc** (Best option)
- **LibreOffice** (Free alternative)
- **Markdown editors** (Typora, Mark Text)
- **python-docx** (Programmatic)

---

## ✅ Checklist

- [ ] HTML documentation created (`documentation.html`)
- [ ] PDF documentation created (`documentation.pdf`)
- [ ] Word documentation created (`documentation.docx`)
- [ ] All files tested and readable
- [ ] Documentation is up-to-date

---

## 💡 Tips

1. **PDF Quality**: Use browser Print for best quality
2. **Word Formatting**: Use pandoc with reference template
3. **Keep Updated**: Regenerate docs when README changes
4. **Version Control**: Don't commit generated PDF/Word files (add to .gitignore)

---

## 🆘 Need Help?

- Check tool installation: `which pandoc`, `which wkhtmltopdf`
- Test HTML: Open `documentation.html` in browser
- Test Markdown: Open `README.md` in Markdown editor
- Use online converters if tools unavailable

