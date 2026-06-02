# 💾 SSD Lifespan Analyzer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Windows](https://img.shields.io/badge/Windows-0078D4?logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![Python](https://img.shields.io/badge/Python-3.7+-3776AB?logo=python&logoColor=white)](https://python.org)

**Detect your actual SSD model, read SMART data, and calculate remaining lifespan in years.**

## ✨ Features

- 🔍 **Auto-detects** your SSD model (Samsung, WD, Crucial, Kingston, etc.)
- 📊 **Reads SMART data** for total host writes
- ⏱️ **Calculates remaining lifespan** based on your usage
- 💾 **Saves detailed reports** as text files
- 🚀 **No internet required** after download
- 🔒 **Open source** - inspect the code yourself

## 📋 Quick Start

### Windows (Recommended)
1. Download the ZIP from [Releases](../../releases) or clone this repo
2. Extract to a folder (e.g., `C:\SSD_Analyzer`)
3. **Right-click** `install_and_run.bat` → **Run as Administrator**
4. Follow the prompts

### Linux / macOS
```bash
git clone https://github.com/braysonimbambi455/ssd_lifespan_analyzer
cd ssd-lifespan-analyzer
sudo python3 ssd_analyzer.py