# 📄 How to Create PDF and Word Documentation

## 🚀 Quickest Method (No Installation Required)

### Create PDF (2 minutes):

1. **Open** `documentation.html` in your web browser
   - Double-click the file, or
   - Right-click → Open With → Browser

2. **Print to PDF**:
   - Press `Cmd+P` (Mac) or `Ctrl+P` (Windows/Linux)
   - In the print dialog, select **"Save as PDF"**
   - Click **"Save"**
   - Name it `documentation.pdf`

✅ **Done! PDF created in 30 seconds!**

---

### Create Word Document (5 minutes):

#### Option A: Using pandoc (Best Quality)

1. **Install pandoc** (one-time):
   ```bash
   # macOS
   brew install pandoc
   
   # Windows (with Chocolatey)
   choco install pandoc
   
   # Linux
   sudo apt-get install pandoc
   ```

2. **Generate Word**:
   ```bash
   cd "/Users/me/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/spatial-projects/GeoAI_Assistant_Pro_Clean"
   pandoc README.md -o documentation.docx --toc --toc-depth=3
   ```

✅ **Done! Word document created!**

#### Option B: Using Markdown Editor (No Installation)

1. **Download Typora** (free): https://typora.io
2. **Open** `README.md` in Typora
3. **File** → **Export** → **Word (.docx)**
4. **Save** as `documentation.docx`

✅ **Done!**

#### Option C: Using LibreOffice (Free)

1. **Install LibreOffice** (if not installed)
2. **Open** `documentation.html` in LibreOffice Writer
3. **File** → **Save As** → **Word Document (.docx)**
4. **Save** as `documentation.docx`

---

## 📋 Step-by-Step Instructions

### For PDF:

#### Method 1: Browser (Recommended)
```
1. Navigate to folder:
   cd "/Users/me/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/spatial-projects/GeoAI_Assistant_Pro_Clean"

2. Open documentation.html:
   open documentation.html
   (or double-click the file)

3. In browser:
   - Press Cmd+P (Mac) or Ctrl+P (Windows)
   - Select "Save as PDF"
   - Save as "documentation.pdf"
```

#### Method 2: Command Line (Chrome)
```bash
cd "/Users/me/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/spatial-projects/GeoAI_Assistant_Pro_Clean"

/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless \
  --disable-gpu \
  --print-to-pdf=documentation.pdf \
  file://$(pwd)/documentation.html
```

#### Method 3: Using pandoc
```bash
# Install pandoc first: brew install pandoc
pandoc README.md -o documentation.pdf --pdf-engine=xelatex --toc
```

---

### For Word Document:

#### Method 1: Using pandoc (Best)
```bash
cd "/Users/me/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/spatial-projects/GeoAI_Assistant_Pro_Clean"

# Install pandoc: brew install pandoc
pandoc README.md -o documentation.docx --toc --toc-depth=3
```

#### Method 2: Using Typora
1. Download Typora: https://typora.io
2. Open `README.md`
3. File → Export → Word (.docx)
4. Save as `documentation.docx`

#### Method 3: Using Online Converter
1. Go to: https://cloudconvert.com/md-to-docx
2. Upload `README.md`
3. Convert
4. Download `documentation.docx`

---

## 🎯 Recommended Workflow

### Fastest (No Tools):
1. **PDF**: Open `documentation.html` → Print → Save as PDF ✅
2. **Word**: Use online converter or Typora

### Best Quality:
1. **Install pandoc**: `brew install pandoc`
2. **PDF**: `pandoc README.md -o documentation.pdf --pdf-engine=xelatex --toc`
3. **Word**: `pandoc README.md -o documentation.docx --toc`

---

## ✅ Verification

After creating files, verify:

```bash
cd "/Users/me/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/spatial-projects/GeoAI_Assistant_Pro_Clean"

# Check files exist
ls -lh documentation.pdf documentation.docx

# Should show:
# documentation.pdf  (should be 500KB - 2MB)
# documentation.docx (should be 100KB - 500KB)
```

---

## 🆘 Troubleshooting

### "pandoc: command not found"
- **Install**: `brew install pandoc` (macOS)
- **Or use**: Browser method for PDF, Typora for Word

### "Chrome not found"
- **Use**: Browser method (open HTML → Print → PDF)
- **Or install**: Chrome from google.com/chrome

### "LaTeX not found" (for PDF with pandoc)
- **Install**: `brew install --cask mactex` (large download)
- **Or use**: Browser method instead

### Files are empty or corrupted
- **Check**: Source files exist (README.md, documentation.html)
- **Try**: Different method
- **Verify**: File permissions

---

## 📦 File Sizes (Expected)

- **documentation.pdf**: 500KB - 2MB
- **documentation.docx**: 100KB - 500KB

---

## 💡 Pro Tips

1. **PDF Quality**: Browser Print method gives best quality
2. **Word Formatting**: pandoc preserves Markdown formatting best
3. **Quick Test**: Open files to verify they look good
4. **Backup**: Keep original README.md and documentation.html

---

## 🎉 Success!

Once you have both files:
- ✅ `documentation.pdf` - Professional PDF documentation
- ✅ `documentation.docx` - Editable Word document

You're ready to share your plugin documentation!

