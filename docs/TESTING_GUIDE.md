# GeoAI Assistant Pro - Testing Guide

## ⚠️ Rate Limit Notice

You're using Azure Computer Vision **Free (F0) tier** which has limits:
- **20 calls per minute**
- **5,000 calls per month**

If you see "429 Rate Limit" errors, wait 8-10 seconds between image analysis requests.

## 🧪 Testing Plan - Task by Task

### Task 1: Verify Plugin Installation ✅

**Goal**: Ensure plugin loads correctly

**Steps**:
1. Open QGIS
2. Go to **Plugins → Manage and Install Plugins**
3. Search for "GeoAI Assistant Pro"
4. Verify it's installed and enabled
5. Check toolbar for plugin icon

**Expected Result**: 
- ✅ Plugin appears in menu
- ✅ Toolbar icon visible
- ✅ No errors in Log Messages

**Check Log Messages**: View → Panels → Log Messages → Filter "GeoAI Pro"

---

### Task 2: Verify Azure Credentials ✅

**Goal**: Confirm Azure credentials are loaded

**Steps**:
1. Open GeoAI Assistant Pro plugin
2. Go to **⚙️ Settings** tab
3. Check if Azure credentials are displayed:
   - Endpoint should show: `https://qgisimage.cognitiveservices.azure.com/`
   - Subscription Key field should be filled (masked)
4. If empty, click "💾 Save Azure Credentials" and re-enter

**Expected Result**:
- ✅ Endpoint URL visible
- ✅ Key field has content (masked with dots)

**If credentials not showing**:
- Check `.env` file location
- Verify variable names: `AZURE_VISION_ENDPOINT` and `AZURE_VISION_SUBSCRIPTION_KEY`
- Restart QGIS

---

### Task 3: Test SQL Generator (No Azure Required) ✅

**Goal**: Test core SQL generation feature

**Steps**:
1. Go to **🔍 SQL Generator** tab
2. In the input box, type:
   ```
   Find all buildings within 500 meters of parks
   ```
3. Select a model from the top bar (e.g., Ollama/phi3)
4. Click **🚀 Generate SQL**
5. Wait for SQL to generate
6. Review the generated SQL in the output box

**Expected Result**:
- ✅ SQL code appears in output box
- ✅ SQL looks valid (has SELECT, FROM, WHERE, etc.)
- ✅ Status shows success message

**Test Variations**:
- Try different queries:
  - "Calculate total area by category"
  - "Select points that intersect with selected polygon"
  - "Find features where population > 10000"

**Check Log Messages**: Should see "Generating SQL with..."

---

### Task 4: Test SQL Execution (No Azure Required) ✅

**Goal**: Execute generated SQL queries

**Prerequisites**: 
- Have at least one layer loaded in QGIS
- Complete Task 3 first (generate SQL)

**Steps**:
1. In **🔍 SQL Generator** tab
2. Generate a simple SQL query (or use existing one)
3. Click **▶️ Execute** button
4. Wait for execution
5. Check Results table below

**Expected Result**:
- ✅ Results table shows data
- ✅ Status shows "Query executed: X rows"
- ✅ No error messages

**If Error Occurs**:
- Check if you have layers loaded
- Try simpler query
- Check Log Messages for SQL errors

---

### Task 5: Test Error Fixer (No Azure Required) ✅

**Goal**: Test automatic SQL error fixing

**Steps**:
1. Go to **🔧 Error Fixer** tab
2. Enter a SQL query with an intentional error:
   ```sql
   SELECT * FORM mytable WHERE id = 1
   ```
   (Note: "FORM" instead of "FROM")
3. Click **🔧 Fix Error** or **Auto-Fix**
4. Review the fixed SQL

**Expected Result**:
- ✅ Error is detected
- ✅ Fixed SQL is generated
- ✅ Explanation provided

**Test Variations**:
- Try different SQL errors
- Test with invalid table names
- Test with syntax errors

---

### Task 6: Test Smart Assistant (No Azure Required) ✅

**Goal**: Test intelligent QGIS suggestions

**Steps**:
1. Load some layers in QGIS (if not already loaded)
2. Go to **💡 Smart Assistant** tab
3. Select analysis type: "Project Overview"
4. Click **✨ Get Suggestions**
5. Review suggestions

**Expected Result**:
- ✅ Suggestions appear
- ✅ Suggestions are relevant to your project
- ✅ No errors

**Test Variations**:
- Try "Selected Layer" analysis
- Try "All Layers" analysis
- Try "Custom Query"

---

### Task 7: Test Model Converter (Azure Required - Rate Limited) ⚠️

**Goal**: Test image to code conversion

**⚠️ IMPORTANT**: Wait 8-10 seconds between tests to avoid rate limits!

**Steps**:
1. Go to **🖼️ Model Converter** tab
2. Click **📁 Browse** to select an image
   - Use a screenshot of QGIS Model Builder
   - Or any diagram/image
3. **Wait 10 seconds** (to avoid rate limit)
4. Select conversion type: "SQL" or "Python"
5. Click **🔄 Convert to Code**
6. Wait for processing (may take 30-60 seconds)
7. Review generated code

**Expected Result**:
- ✅ Image preview appears
- ✅ Azure analysis completes (check Log Messages)
- ✅ Code is generated
- ✅ Code appears in output box

**If Rate Limit Error (429)**:
- ⏳ **Wait 10 seconds** and try again
- Check Log Messages for "rate limit" message
- Consider upgrading to paid Azure tier for more calls

**Check Log Messages**:
- ✅ "Starting Azure analysis for: [image path]"
- ✅ "Azure analysis completed"
- ✅ "Generating SQL/Python code..."
- ❌ "429 Rate Limit" → Wait and retry

---

### Task 8: Test Query History (No Azure Required) ✅

**Goal**: Test query history management

**Steps**:
1. Generate a few SQL queries (Task 3)
2. Go to **📜 History** tab
3. Check if queries appear in history list
4. Select a query from history
5. Review query details
6. Try **♻️ Reuse** button
7. Try **⭐ Favorite** button

**Expected Result**:
- ✅ Queries appear in history
- ✅ Query details show when selected
- ✅ Reuse button works
- ✅ Favorite button works

---

### Task 9: Test Batch Processing (No Azure Required) ✅

**Goal**: Test processing multiple queries at once

**Steps**:
1. Go to **⚡ Batch Process** tab
2. Add multiple queries (one per line or separate entries)
3. Click **Process All**
4. Review results

**Expected Result**:
- ✅ Multiple queries processed
- ✅ Results shown for each query
- ✅ Success/failure status for each

---

### Task 10: Test Data Analysis (No Azure Required) ✅

**Goal**: Test data analysis features

**Steps**:
1. Load some layers with data
2. Go to **📊 Data Analysis** tab
3. Try quick analysis buttons (if available)
4. Or enter custom analysis query
5. Review results

**Expected Result**:
- ✅ Analysis completes
- ✅ Results displayed
- ✅ Relevant insights provided

---

### Task 11: Test Settings Panel ✅

**Goal**: Verify settings configuration

**Steps**:
1. Go to **⚙️ Settings** tab
2. Verify Azure credentials are loaded
3. Try updating credentials (if needed)
4. Click **💾 Save Azure Credentials**
5. Check Log Messages for confirmation

**Expected Result**:
- ✅ Credentials display correctly
- ✅ Save button works
- ✅ Success message appears
- ✅ Log shows "Azure credentials saved"

---

## 🐛 Troubleshooting Common Issues

### Issue: Rate Limit Error (429)

**Error Message**:
```
(429) Requests to the Analyze Image Operation under Computer Vision API (v3.2) have exceeded call rate limit
```

**Solution**:
1. ⏳ **Wait 10 seconds** between image analysis requests
2. Use Model Converter sparingly during testing
3. Consider upgrading to Azure **Standard (S1)** tier for higher limits
4. Test other features first (SQL Generator, Error Fixer, etc.)

### Issue: Azure Credentials Not Found

**Solution**:
1. Check `.env` file exists in plugin directory
2. Verify variable names are correct
3. Use Settings panel to save credentials
4. Restart QGIS

### Issue: SQL Generation Fails

**Solution**:
1. Check if LLM provider is configured (Ollama works locally)
2. Verify model is selected in top bar
3. Check Log Messages for specific error
4. Try simpler query

### Issue: SQL Execution Fails

**Solution**:
1. Ensure layers are loaded in QGIS
2. Check SQL syntax is valid
3. Verify table/layer names exist
4. Use Error Fixer to fix SQL errors

---

## 📊 Testing Checklist

Use this checklist to track your testing progress:

- [ ] Task 1: Plugin Installation
- [ ] Task 2: Azure Credentials Verification
- [ ] Task 3: SQL Generator
- [ ] Task 4: SQL Execution
- [ ] Task 5: Error Fixer
- [ ] Task 6: Smart Assistant
- [ ] Task 7: Model Converter (⚠️ Rate Limited)
- [ ] Task 8: Query History
- [ ] Task 9: Batch Processing
- [ ] Task 10: Data Analysis
- [ ] Task 11: Settings Panel

---

## 🎯 Recommended Testing Order

**Start with features that DON'T require Azure** (no rate limits):

1. ✅ Task 1: Plugin Installation
2. ✅ Task 2: Azure Credentials
3. ✅ Task 3: SQL Generator
4. ✅ Task 4: SQL Execution
5. ✅ Task 5: Error Fixer
6. ✅ Task 6: Smart Assistant
7. ✅ Task 8: Query History
8. ✅ Task 9: Batch Processing
9. ✅ Task 10: Data Analysis
10. ✅ Task 11: Settings Panel

**Then test Azure-dependent features** (with rate limit awareness):

11. ⚠️ Task 7: Model Converter (wait 10 sec between tests)

---

## 💡 Tips for Testing

1. **Test non-Azure features first** - No rate limits
2. **Wait between Azure calls** - 10 seconds minimum
3. **Check Log Messages** - Always check for errors/warnings
4. **Test with real data** - Load actual QGIS layers
5. **Try edge cases** - Invalid SQL, empty inputs, etc.
6. **Document issues** - Note any bugs or unexpected behavior

---

## 🔄 Rate Limit Workaround

If you need to test Model Converter more frequently:

1. **Upgrade Azure Tier**: 
   - Go to Azure Portal
   - Your Computer Vision resource → Pricing tier
   - Upgrade to Standard (S1) for higher limits

2. **Wait Between Calls**:
   - Always wait 10+ seconds between image analysis
   - Use a timer if needed

3. **Test Other Features**:
   - Most features don't require Azure
   - Test SQL Generator, Error Fixer, etc. first

---

## ✅ Success Criteria

Plugin is working correctly if:
- ✅ All tabs load without errors
- ✅ SQL Generator creates valid SQL
- ✅ SQL Execution returns results
- ✅ Error Fixer corrects SQL errors
- ✅ Model Converter works (when not rate limited)
- ✅ Settings panel saves credentials
- ✅ No critical errors in Log Messages

Good luck with testing! 🚀

