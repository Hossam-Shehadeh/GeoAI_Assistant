# Azure Computer Vision Setup Guide

This guide will help you set up Azure Computer Vision API for the GeoAI Assistant Pro plugin.

## 📋 Prerequisites

- An Azure account (sign up at https://azure.microsoft.com/free/)
- Access to Azure Portal

## 🔧 Step-by-Step Setup

### Step 1: Create Azure Computer Vision Resource

1. **Log in to Azure Portal**
   - Go to https://portal.azure.com/
   - Sign in with your Azure account

2. **Create Computer Vision Resource**
   - Click "Create a resource" (top left)
   - Search for "Computer Vision"
   - Click on "Computer Vision" from Microsoft
   - Click "Create"

3. **Configure the Resource**
   - **Subscription**: Select your subscription
   - **Resource Group**: Create new or use existing
   - **Region**: Choose closest region (e.g., East US, West Europe)
   - **Name**: Give it a unique name (e.g., `geoai-vision-001`)
   - **Pricing Tier**: 
     - **Free (F0)**: 20 calls/min, 5,000 calls/month (good for testing)
     - **Standard (S1)**: Pay-as-you-go (for production)
   - Click "Review + create" then "Create"

### Step 2: Get Your Credentials

1. **Navigate to Your Resource**
   - Go to "All resources" in Azure Portal
   - Click on your Computer Vision resource

2. **Get Endpoint and Key**
   - In the left menu, click "Keys and Endpoint"
   - You'll see:
     - **Endpoint**: `https://your-resource-name.cognitiveservices.azure.com/`
     - **Key 1**: A 32-character alphanumeric string
     - **Key 2**: Another key (either Key 1 or Key 2 works)

### Step 3: Configure in Plugin

You have two options to configure Azure credentials:

#### Option A: Using Settings Panel (Recommended)

1. **Open QGIS** and load the GeoAI Assistant Pro plugin
2. **Open the plugin** (from Plugins menu or toolbar)
3. **Go to Settings tab** (⚙️ Settings)
4. **Enter your credentials**:
   - **Endpoint URL**: Paste your endpoint (e.g., `https://your-resource-name.cognitiveservices.azure.com/`)
   - **Subscription Key**: Paste your Key 1 or Key 2
5. **Click "💾 Save Azure Credentials"**
6. **Restart QGIS** for changes to take effect

#### Option B: Manual .env File Setup

1. **Locate the plugin directory**:
   ```
   /Users/me/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/GeoAI_Assistant_Pro/
   ```

2. **Create or edit `.env` file**:
   - Copy `ENV_TEMPLATE.txt` to `.env` (if it exists)
   - Or create a new `.env` file

3. **Add your credentials**:
   ```env
   AZURE_VISION_ENDPOINT=https://your-resource-name.cognitiveservices.azure.com/
   AZURE_VISION_SUBSCRIPTION_KEY=your-actual-key-here
   ```

4. **Save the file** and restart QGIS

## ✅ Verify Setup

1. **Open QGIS** and load the plugin
2. **Go to Model Converter tab** (🖼️ Model Converter)
3. **Select an image** and try to convert it
4. **Check QGIS Log Messages**:
   - View → Panels → Log Messages
   - Look for "Azure Computer Vision client initialized successfully"

## 🔍 Troubleshooting

### Error: "Azure Computer Vision client not initialized"

**Possible causes:**
- `.env` file not found or in wrong location
- Credentials not saved correctly
- Missing environment variables

**Solutions:**
1. Check `.env` file exists in plugin directory
2. Verify variable names are correct:
   - `AZURE_VISION_ENDPOINT`
   - `AZURE_VISION_SUBSCRIPTION_KEY`
3. Use Settings panel to save credentials (Option A above)
4. Restart QGIS after saving

### Error: "Azure SDK not installed"

**Solution:**
Install Azure Computer Vision SDK:

1. **Open QGIS Python Console**:
   - Plugins → Python Console

2. **Find Python executable**:
   ```python
   import sys
   print(sys.executable)
   ```

3. **Install packages** (in terminal):
   ```bash
   /path/to/qgis/python3 -m pip install azure-cognitiveservices-vision-computervision msrest
   ```

4. **Restart QGIS**

### Error: "Invalid subscription key" or "401 Unauthorized"

**Possible causes:**
- Wrong subscription key
- Key expired or regenerated
- Wrong endpoint URL

**Solutions:**
1. Go back to Azure Portal → Keys and Endpoint
2. Copy the key again (make sure no extra spaces)
3. Verify endpoint URL is correct
4. Update credentials in Settings panel
5. Restart QGIS

### Error: "Endpoint not found" or "404 Not Found"

**Possible causes:**
- Wrong endpoint URL
- Resource deleted or moved
- Typo in endpoint

**Solutions:**
1. Verify endpoint in Azure Portal
2. Make sure endpoint ends with `/` (trailing slash)
3. Check resource still exists in Azure Portal
4. Update endpoint in Settings panel

## 📚 Additional Resources

- [Azure Computer Vision Documentation](https://docs.microsoft.com/azure/cognitive-services/computer-vision/)
- [Azure Portal](https://portal.azure.com/)
- [Azure Free Tier Limits](https://azure.microsoft.com/pricing/details/cognitive-services/computer-vision/)

## 💡 Tips

- **Free Tier**: Good for testing (20 calls/min, 5,000/month)
- **Keep Keys Secure**: Never commit `.env` file to version control
- **Use Key 1 or Key 2**: Both work, but Key 1 is recommended
- **Region Selection**: Choose closest region for better performance
- **Monitor Usage**: Check Azure Portal for API usage and costs

## 🔐 Security Best Practices

1. **Never share your keys** publicly
2. **Add `.env` to `.gitignore`** if using version control
3. **Regenerate keys** if accidentally exposed
4. **Use separate keys** for development and production
5. **Monitor usage** in Azure Portal regularly

