# Quick Start Guide

Get up and running with GeoAI Assistant Pro in 5 minutes!

## 🚀 Installation

### 1. Install Plugin

**Option A: Git Clone**
```bash
cd ~/Library/Application\ Support/QGIS/QGIS3/profiles/default/python/plugins/
git clone <repository-url> GeoAI_Assistant
```

**Option B: Manual Download**
- Download and extract to QGIS plugins directory

### 2. Enable in QGIS

1. Open QGIS
2. `Plugins → Manage and Install Plugins`
3. Search "GeoAI Assistant Pro"
4. Enable the plugin

### 3. Configure Environment

Create `.env` file from `.env.example`:
```bash
cp .env.example .env
```

Edit `.env` with your API keys (or use Ollama for local, free usage).

### 4. Restart QGIS

Close and reopen QGIS.

## 🎯 First Steps

### 1. Open Plugin

Click the **GeoAI Assistant Pro** icon in toolbar.

### 2. Select Model

Choose from:
- **Ollama** (Local, Free) - Recommended
- **OpenAI** (Cloud, Paid)
- **Anthropic** (Cloud, Paid)
- **Google** (Cloud, Paid)

### 3. Generate SQL

1. Go to **SQL Generator** tab
2. Type: `"Find all buildings larger than 1000 square meters"`
3. Click **🚀 Generate SQL**
4. Review and execute

## 📚 Next Steps

- Read [USER_GUIDE.md](USER_GUIDE.md) for detailed usage
- Check [DOCUMENTATION.md](DOCUMENTATION.md) for complete docs
- See [AZURE_SETUP.md](AZURE_SETUP.md) for Model Converter setup

## 🆘 Need Help?

- Check [USER_GUIDE.md](USER_GUIDE.md)
- Review [DOCUMENTATION.md](DOCUMENTATION.md)
- Open an issue on GitHub

---

**Happy Geospatial AI! 🎉**

