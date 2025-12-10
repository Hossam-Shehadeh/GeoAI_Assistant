# GeoAI Assistant Pro - User Guide

## Welcome! 👋

This guide will help you get started with GeoAI Assistant Pro and use all its features effectively.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [SQL Generator](#sql-generator)
3. [Model Converter](#model-converter)
4. [Smart Assistant](#smart-assistant)
5. [Error Fixer](#error-fixer)
6. [Data Analysis](#data-analysis)
7. [Query History](#query-history)
8. [Batch Processing](#batch-processing)
9. [Template Manager](#template-manager)
10. [Analytics Dashboard](#analytics-dashboard)
11. [Settings](#settings)
12. [Tips & Tricks](#tips--tricks)

---

## Getting Started

### First Time Setup

1. **Open the Plugin**
   - Click the GeoAI Assistant Pro icon in the toolbar
   - Or go to `Plugins → GeoAI Assistant Pro → Open GeoAI Assistant Pro`

2. **Configure Azure** (Optional but Recommended)
   - Go to **⚙️ Settings** tab
   - Enter your Azure Computer Vision credentials
   - Click **💾 Save Azure Credentials**
   - See [AZURE_SETUP.md](AZURE_SETUP.md) for detailed instructions

3. **Select a Model**
   - Use the model selector in the top bar
   - For local use: Select **Ollama** and a model (e.g., phi3)
   - For cloud: Select **OpenAI**, **Anthropic**, or **Google** (requires API keys)

4. **You're Ready!** Start using any feature

---

## SQL Generator

### What It Does

Converts natural language descriptions into SQL queries that work with your QGIS layers.

### How to Use

#### Step 1: Describe Your Query

Type what you want in plain English:
- ✅ "Find all buildings within 500 meters of parks"
- ✅ "Calculate total area by category"
- ✅ "Select points that intersect with selected polygon"
- ✅ "Join buildings table with addresses table"

#### Step 2: Select Model

Choose an LLM model from the dropdown:
- **Ollama/phi3** - Fast, local, free (recommended for beginners)
- **OpenAI/GPT-4o** - Best quality, requires API key
- **Claude 3.5 Sonnet** - Excellent quality, requires API key

#### Step 3: Generate SQL

1. Click **🚀 Generate SQL**
2. Wait 10-30 seconds
3. Review the generated SQL in the output box

#### Step 4: Execute (Optional)

1. Click **▶️ Execute** to run the SQL
2. View results in the results table below
3. Results show number of rows returned

### Quick Templates

Use the "Quick Start" dropdown for common operations:
- 📍 Find features near...
- 📊 Aggregate by category
- 🔍 Filter by attribute
- 📐 Calculate geometry
- 🔗 Join tables

### Tips

- **Be Specific**: Mention layer names and exact requirements
- **Include Context**: Describe relationships between layers
- **Review Before Execute**: Always check generated SQL
- **Use Auto-Fix**: If SQL has errors, click **🔧 Auto-Fix**

### Example Workflow

**Goal**: Find all restaurants within 1km of schools

1. Type: `Find all restaurants within 1 kilometer of schools`
2. Select model: Ollama/phi3
3. Click Generate SQL
4. Review SQL:
   ```sql
   SELECT r.*
   FROM restaurants r
   WHERE EXISTS (
       SELECT 1
       FROM schools s
       WHERE ST_DWithin(r.geometry, s.geometry, 1000)
   );
   ```
5. Click Execute
6. View results: 15 restaurants found

---

## Model Converter

### What It Does

Converts screenshots of QGIS Model Builder workflows into executable SQL or Python code.

### How to Use

#### Step 1: Prepare Your Image

- Take a screenshot of your QGIS Model Builder
- Save as PNG, JPG, or JPEG
- Ensure the image is clear and readable

#### Step 2: Upload Image

1. Go to **🖼️ Model Converter** tab
2. Click **📁 Browse**
3. Select your image file
4. Image preview will appear

#### Step 3: Select Output Type

Choose what you want:
- **SQL** - For database queries
- **Python** - For Python scripts
- **Both** - For both (currently defaults to SQL)

#### Step 4: Convert

1. Click **🔄 Convert to Code**
2. Wait 30-60 seconds (may take longer for complex images)
3. Review the generated code

#### Step 5: Use the Code

- **📋 Copy Code** - Copy to clipboard
- **💾 Save to File** - Save as .sql or .py file
- **➕ Add Image to QGIS Map** - Add image as raster layer

### Understanding the Output

The output shows:
1. **Analysis Method**: Which method was used (Azure or LLM)
2. **Image Analysis**: What was detected in the image
3. **Generated Code**: The actual SQL/Python code

### Example

**Input**: Screenshot showing:
- Input layer: "buildings"
- Process: Buffer 100m
- Output: "buffered_buildings"

**Output**:
```sql
-- Buffer analysis: Create 100m buffer around buildings
CREATE TABLE buffered_buildings AS
SELECT ST_Buffer(geometry, 100) AS geometry, *
FROM buildings;
```

### Tips

- **Clear Images**: Use high-quality screenshots
- **Complete Workflows**: Include entire Model Builder diagram
- **Wait Between Conversions**: Azure free tier has rate limits (20/min)
- **Check Analysis**: Review the analysis description to verify accuracy

---

## Smart Assistant

### What It Does

Provides intelligent suggestions and recommendations for your QGIS project.

### How to Use

#### Step 1: Load Layers

Make sure you have layers loaded in QGIS (the more, the better)

#### Step 2: Select Analysis Type

Choose what you want analyzed:
- **Project Overview** - Get suggestions for entire project
- **Selected Layer** - Analyze currently selected layer
- **All Layers** - Get recommendations for all layers
- **Custom Query** - Ask a specific question

#### Step 3: Get Suggestions

1. Click **✨ Get Suggestions**
2. Wait 10-30 seconds
3. Review suggestions in the output box

### Example Suggestions

**Project Overview** might suggest:
- "Consider adding a spatial index to improve query performance"
- "Your layers use different CRS - consider reprojecting for analysis"
- "You have point and polygon layers - consider spatial joins"

**Selected Layer** might suggest:
- "This layer has 10,000+ features - consider using spatial indexes"
- "Attribute 'category' has 5 unique values - good for grouping"
- "Consider calculating area for polygon features"

### Tips

- **Load Multiple Layers**: More context = better suggestions
- **Be Specific**: Use Custom Query for targeted questions
- **Review Regularly**: Get suggestions as you work

---

## Error Fixer

### What It Does

Automatically detects and fixes SQL errors using AI.

### How to Use

#### Step 1: Paste SQL with Error

Paste your SQL query (even if it has errors):
```sql
SELECT * FORM mytable WHERE id = 1
```

#### Step 2: Fix Error

1. Click **🔧 Fix Error** or **Auto-Fix**
2. Wait 10-30 seconds
3. Review the fixed SQL and explanation

#### Step 3: Execute Fixed SQL

1. Review the fixed SQL
2. Read the explanation
3. Click **Execute** if satisfied

### Example

**Input** (with error):
```sql
SELECT * FORM mytable WHERE id = 1
```

**Fixed SQL**:
```sql
SELECT * FROM mytable WHERE id = 1
```

**Explanation**:
"Changed 'FORM' to 'FROM' - this was a typo. The correct SQL keyword is 'FROM'."

### Supported Errors

- ✅ Syntax errors (typos, missing keywords)
- ✅ Missing clauses (WHERE, FROM, etc.)
- ✅ Invalid table/column names
- ✅ Type mismatches
- ✅ Logical errors

### Tips

- **Paste Exact Error**: Include the error message if possible
- **Review Fixes**: Always review before executing
- **Multiple Errors**: Fix one at a time for best results

---

## Data Analysis

### What It Does

Provides quick analysis tools and custom analysis queries.

### How to Use

#### Quick Analysis

1. Load a layer with data
2. Go to **📊 Data Analysis** tab
3. Click quick analysis buttons (if available)
4. View analysis results

#### Custom Analysis

1. Type your analysis question
2. Select model
3. Click **Analyze**
4. Review results

### Example Queries

- "What is the total area of all polygons?"
- "How many points are in each category?"
- "What is the average distance between points?"
- "Which features have the largest area?"

---

## Query History

### What It Does

Saves all your queries so you can reuse them later.

### How to Use

#### View History

1. Go to **📜 History** tab
2. All your queries appear in the list (left side)
3. Click a query to view details (right side)

#### Search History

1. Type in the search box
2. History filters automatically
3. Find queries by keyword

#### Use Previous Queries

1. Select a query from history
2. Click **♻️ Reuse**
3. Query is copied to SQL Generator

#### Mark Favorites

1. Select a query
2. Click **⭐ Favorite**
3. Favorite queries are marked with a star

#### Delete Queries

1. Select a query
2. Click **🗑️ Delete**
3. Query is removed from history

### Tips

- **Regular Cleanup**: Delete old queries you don't need
- **Use Favorites**: Mark frequently used queries
- **Search Often**: Use search to find specific queries quickly

---

## Batch Processing

### What It Does

Process multiple queries at the same time.

### How to Use

#### Step 1: Add Queries

1. Go to **⚡ Batch Process** tab
2. Add multiple queries (one per line or separate entries)
3. Example:
   ```
   Find buildings near parks
   Find buildings near schools
   Find buildings near hospitals
   ```

#### Step 2: Process

1. Click **Process All**
2. Monitor progress
3. Wait for all queries to complete

#### Step 3: Review Results

1. View results for each query
2. Check success/failure status
3. Export or save results

### Use Cases

- Process similar queries on different layers
- Generate reports for multiple areas
- Test query variations
- Analyze multiple datasets

### Tips

- **Similar Queries**: Batch works best with similar query types
- **Monitor Progress**: Watch for errors or timeouts
- **Save Results**: Export results for later review

---

## Template Manager

### What It Does

Create reusable query templates with variables.

### How to Use

#### Create Template

1. Go to **📝 Templates** tab
2. Click **New Template**
3. Enter template name
4. Write query with variables:
   ```sql
   SELECT * FROM {table_name} WHERE {field} = '{value}'
   ```
5. Define variables:
   - `table_name` - Table to query
   - `field` - Field name
   - `value` - Value to match
6. Save template

#### Use Template

1. Select template from list
2. Fill in variable values
3. Click **Insert** or **Use**
4. Template is inserted into SQL Generator

### Example Template

**Template Name**: "Find features near location"

**Query**:
```sql
SELECT * FROM {layer} 
WHERE ST_DWithin(
    geometry, 
    (SELECT geometry FROM locations WHERE name = '{location_name}'),
    {distance}
)
```

**Variables**:
- `layer` - Source layer name
- `location_name` - Name of location
- `distance` - Distance in meters

**Usage**:
- layer: buildings
- location_name: Central Park
- distance: 500

**Result**:
```sql
SELECT * FROM buildings 
WHERE ST_DWithin(
    geometry, 
    (SELECT geometry FROM locations WHERE name = 'Central Park'),
    500
)
```

### Tips

- **Common Patterns**: Create templates for operations you do often
- **Clear Names**: Use descriptive template names
- **Document Variables**: Add comments explaining variables

---

## Analytics Dashboard

### What It Does

Shows statistics and performance metrics for your usage.

### How to View

1. Go to **📈 Analytics** tab
2. View metrics:
   - Total queries executed
   - Success rate
   - Average response time
   - Most used features
   - Query types breakdown

### Metrics Explained

- **Total Queries**: Number of queries you've run
- **Success Rate**: Percentage of successful queries
- **Response Time**: Average time for SQL generation
- **Feature Usage**: Which features you use most
- **Model Usage**: Which LLM models you prefer

### Tips

- **Monitor Performance**: Check if certain models are faster
- **Track Success**: See which query types work best
- **Optimize Usage**: Use insights to improve workflow

---

## Settings

### What It Does

Configure Azure credentials, API keys, and plugin preferences.

### Azure Configuration

**Required for**: Model Converter image analysis

**Steps**:
1. Get Azure credentials from [Azure Portal](https://portal.azure.com/)
2. Enter **Endpoint URL**
3. Enter **Subscription Key**
4. Click **💾 Save Azure Credentials**
5. Restart QGIS

**See**: [AZURE_SETUP.md](AZURE_SETUP.md) for detailed instructions

### LLM Provider Configuration

**API Keys** (if using cloud providers):
1. Get API key from provider website
2. Enter in Settings tab (if available)
3. Or add to `.env` file

**Ollama** (local):
- No API key needed
- Just ensure Ollama is running
- Install models: `ollama pull phi3`

### Tips

- **Secure Storage**: Never share your API keys
- **Test After Config**: Try a simple query after configuring
- **Check Logs**: If issues, check Log Messages

---

## Tips & Tricks

### General Tips

1. **Start Simple**: Begin with simple queries, then try complex ones
2. **Use Templates**: Create templates for repeated operations
3. **Check Logs**: Always check Log Messages for errors
4. **Save Work**: Use History to save important queries
5. **Batch Process**: Use batch for similar operations

### SQL Generation Tips

1. **Be Descriptive**: More detail = better SQL
2. **Mention Layers**: Always mention layer names
3. **Specify Operations**: Clearly state what you want
4. **Review Always**: Never execute without reviewing
5. **Use Context**: Plugin uses your current QGIS layers

### Image Conversion Tips

1. **High Quality**: Use clear, high-resolution screenshots
2. **Complete Diagrams**: Include entire Model Builder workflow
3. **Good Lighting**: Ensure text is readable
4. **Wait Between**: Respect Azure rate limits (10 sec between)
5. **Verify Results**: Always test generated code

### Performance Tips

1. **Use Local Models**: Ollama is faster for local use
2. **Cache Queries**: Reuse queries from history
3. **Batch Process**: Process multiple queries together
4. **Optimize Images**: Use smaller images when possible
5. **Monitor Usage**: Check Analytics for insights

### Troubleshooting Tips

1. **Check Logs First**: Log Messages have detailed info
2. **Verify Config**: Check Settings and .env file
3. **Test Simple**: Try simple query first
4. **Restart Plugin**: Reload plugin if issues persist
5. **Check Internet**: Cloud providers need internet

---

## Common Workflows

### Workflow 1: Daily Analysis

1. Open plugin
2. Load your layers
3. Use SQL Generator for quick queries
4. Save important queries to History
5. Use templates for repeated operations

### Workflow 2: Model Builder Conversion

1. Create workflow in QGIS Model Builder
2. Take screenshot
3. Use Model Converter
4. Review generated code
5. Save code to file
6. Use in your project

### Workflow 3: Error Debugging

1. Get SQL error message
2. Paste SQL in Error Fixer
3. Review fix and explanation
4. Execute fixed SQL
5. Save to History if useful

### Workflow 4: Batch Analysis

1. Prepare list of similar queries
2. Use Batch Processor
3. Process all at once
4. Review results
5. Export for reporting

---

## Keyboard Shortcuts

- **Ctrl/Cmd + G**: Generate SQL (in SQL Generator)
- **Ctrl/Cmd + E**: Execute SQL
- **Ctrl/Cmd + C**: Copy code/output
- **Ctrl/Cmd + S**: Save code to file
- **F5**: Refresh/Reload

---

## Best Practices

### Do's ✅

- ✅ Review generated SQL before executing
- ✅ Use clear, descriptive natural language
- ✅ Save important queries to History
- ✅ Create templates for common operations
- ✅ Check Log Messages for errors
- ✅ Verify Azure credentials are correct
- ✅ Use appropriate models for tasks
- ✅ Test code before using in production

### Don'ts ❌

- ❌ Don't execute SQL without reviewing
- ❌ Don't share API keys publicly
- ❌ Don't ignore error messages
- ❌ Don't use unclear descriptions
- ❌ Don't skip configuration steps
- ❌ Don't process too many images quickly (rate limits)
- ❌ Don't use production data for testing without backup

---

## Getting Help

### Self-Help Resources

1. **Check Log Messages**: View → Panels → Log Messages
2. **Review Documentation**: See [DOCUMENTATION.md](DOCUMENTATION.md)
3. **Check Error Messages**: They often include solutions
4. **Try Examples**: Use provided examples as starting points

### Common Questions

**Q: Which model should I use?**
A: Start with Ollama/phi3 (free, local). For best quality, use GPT-4o or Claude 3.5 Sonnet.

**Q: Do I need Azure?**
A: Not required, but recommended for Model Converter. Plugin will use LLM fallback if Azure not configured.

**Q: Why is SQL generation slow?**
A: Depends on model. Local Ollama is fastest. Cloud providers depend on internet speed.

**Q: Can I use this offline?**
A: Yes, with Ollama (local models). Cloud providers need internet.

**Q: How do I save my queries?**
A: Use Query History - all queries are automatically saved.

---

## Next Steps

1. ✅ Complete first-time setup
2. ✅ Try SQL Generator with a simple query
3. ✅ Test Model Converter with a screenshot
4. ✅ Explore Smart Assistant suggestions
5. ✅ Create your first template
6. ✅ Review Analytics dashboard

---

**Happy Geospatial AI Processing!** 🚀

For technical details, see [DOCUMENTATION.md](DOCUMENTATION.md)
For Azure setup, see [AZURE_SETUP.md](AZURE_SETUP.md)

