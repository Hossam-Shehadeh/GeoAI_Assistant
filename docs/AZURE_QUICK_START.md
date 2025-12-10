# Azure Setup - Quick Start

## 🚀 Fastest Way to Set Up Azure

### Method 1: Using Settings Panel (2 minutes)

1. **Get Azure Credentials**:
   - Go to https://portal.azure.com/
   - Create or open your Computer Vision resource
   - Go to "Keys and Endpoint"
   - Copy the **Endpoint URL** and **Key 1**

2. **Configure in Plugin**:
   - Open QGIS → GeoAI Assistant Pro
   - Go to **⚙️ Settings** tab
   - Paste your Endpoint and Key
   - Click **💾 Save Azure Credentials**
   - **Restart QGIS**

3. **Test It**:
   - Go to **🖼️ Model Converter** tab
   - Select an image and convert it
   - Check Log Messages for "Azure initialized successfully"

### Method 2: Manual .env File

1. **Create `.env` file** in plugin directory:
   ```
   /Users/me/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/GeoAI_Assistant_Pro/.env
   ```

2. **Add these lines** (replace with your actual values):
   ```env
   AZURE_VISION_ENDPOINT=https://your-resource-name.cognitiveservices.azure.com/
   AZURE_VISION_SUBSCRIPTION_KEY=your-actual-key-here
   ```

3. **Save and restart QGIS**

## 📝 Required Variables

The plugin expects these exact variable names in `.env`:

```env
AZURE_VISION_ENDPOINT=https://your-endpoint.cognitiveservices.azure.com/
AZURE_VISION_SUBSCRIPTION_KEY=your-subscription-key-here
```

## 🔍 How to Get Azure Credentials

1. **Azure Portal**: https://portal.azure.com/
2. **Create Computer Vision resource** (if needed):
   - Search "Computer Vision" → Create
   - Choose **Free (F0)** tier for testing
3. **Get credentials**:
   - Open resource → "Keys and Endpoint"
   - Copy **Endpoint URL**
   - Copy **Key 1** (or Key 2)

## ✅ Verify Setup

Check QGIS Log Messages (View → Panels → Log Messages):
- ✅ "Azure Computer Vision client initialized successfully"
- ❌ "Azure credentials not found" → Check your `.env` file or Settings

## 📚 Full Documentation

For detailed instructions and troubleshooting, see [AZURE_SETUP.md](AZURE_SETUP.md)

## 💡 Tips

- **Free Tier**: 20 calls/min, 5,000/month (perfect for testing)
- **Settings Panel**: Easiest way to configure (saves to `.env` automatically)
- **Restart Required**: Always restart QGIS after saving credentials
- **Keep Keys Secret**: Never share your Azure keys publicly

