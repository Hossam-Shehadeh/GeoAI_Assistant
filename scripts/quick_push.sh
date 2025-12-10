#!/bin/bash
# Quick push to GitHub on new branch

cd "/Users/me/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/spatial-projects/GeoAI_Assistant_Pro_Clean"

# Create new branch
git checkout -b feature/pdf-documentation-updates 2>/dev/null || git checkout feature/pdf-documentation-updates

# Add all files
git add .

# Commit
git commit -m "docs: Add PDF report and documentation updates

- Created professional PDF report
- Added PDF generation scripts
- Updated HTML documentation
- Added comprehensive guides"

# Push
git push -u origin feature/pdf-documentation-updates

echo "✅ Pushed to GitHub!"


