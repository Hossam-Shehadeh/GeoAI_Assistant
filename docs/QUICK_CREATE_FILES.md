# 🚀 Quick Guide: Create PDF and Word Files

## 📄 Create PDF (2 minutes)

### Method 1: Browser Print (Easiest)

1. **Open** `documentation.html` in your browser
   - Double-click the file
   - Or right-click → Open With → Chrome/Safari

2. **Print to PDF**:
   - Press `Cmd+P` (Mac) or `Ctrl+P` (Windows/Linux)
   - In the print dialog:
     - **Destination**: Select "Save as PDF"
     - **Layout**: Portrait
     - **Pages**: All
     - **More settings**: Uncheck "Headers and footers" (if available)
   - Click **"Save"**
   - **Name**: `documentation.pdf`
   - **Location**: Same folder as `documentation.html`

✅ **Done! PDF created!**

---

## 📝 Create Word Document (3 minutes)

### Method 1: Using pandoc (Best Quality)

1. **Install pandoc** (if not installed):
   ```bash
   brew install pandoc
   ```

2. **Open Terminal** and run:
   ```bash
   cd "/Users/me/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/spatial-projects/GeoAI_Assistant_Pro_Clean"
   pandoc README.md -o documentation.docx --toc --toc-depth=3
   ```

✅ **Done! Word document created!**

### Method 2: Using Typora (No Command Line)

1. **Download Typora**: https://typora.io
2. **Open** `README.md` in Typora
3. **File** → **Export** → **Word (.docx)**
4. **Save as**: `documentation.docx`
5. **Location**: Same folder as `README.md`

✅ **Done!**

### Method 3: Online Converter

1. Go to: https://cloudconvert.com/md-to-docx
2. **Upload** `README.md`
3. Click **"Convert"**
4. **Download** the file
5. **Rename** to `documentation.docx`
6. **Move** to the same folder as `README.md`

✅ **Done!**

---

## 📍 File Locations

**Source Files:**
- `documentation.html` → Use for PDF
- `README.md` → Use for Word

**Output Files (to be created):**
- `documentation.pdf` → Must be in same folder as HTML
- `documentation.docx` → Must be in same folder as HTML

**Current Folder:**
```
/Users/me/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/spatial-projects/GeoAI_Assistant_Pro_Clean/
```

---

## ✅ Verification

After creating files, verify they exist:

```bash
cd "/Users/me/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/spatial-projects/GeoAI_Assistant_Pro_Clean"
ls -lh documentation.pdf documentation.docx
```

You should see both files with reasonable sizes:
- `documentation.pdf`: ~500KB - 2MB
- `documentation.docx`: ~100KB - 500KB

---

## 🎯 Quick Steps Summary

### For PDF:
1. Open `documentation.html` in browser
2. `Cmd+P` → Save as PDF
3. Save as `documentation.pdf` in same folder
4. ✅ Done!

### For Word:
1. Install pandoc: `brew install pandoc`
2. Run: `pandoc README.md -o documentation.docx --toc`
3. ✅ Done!

---

## 💡 Tips

- **PDF Quality**: Browser print method gives best quality
- **Word Formatting**: pandoc preserves Markdown formatting best
- **File Names**: Must be exactly `documentation.pdf` and `documentation.docx`
- **Same Folder**: Files must be in the same folder as `documentation.html`

---

## 🆘 Troubleshooting

**"File not found" error:**
- Make sure files are named exactly: `documentation.pdf` and `documentation.docx`
- Make sure files are in the same folder as `documentation.html`
- Check file permissions

**"pandoc not found":**
- Install: `brew install pandoc`
- Or use Typora/online converter instead

**Download button still not working:**
- Refresh the page after creating files
- Check browser console for errors
- Make sure files are in the correct location

---

**🎉 Once both files are created, the download buttons will work automatically!**

