# 🛠️ Baldor Product Scraper

This project is a web scraping tool built with Python and Selenium to extract structured data from the [Baldor](https://www.baldor.com/catalog) product catalog. It automatically navigates to a specific product category, collects details such as product descriptions, specifications, manuals, and images, and saves them locally in organized JSON format.

## 📦 Features

- Simulates human-like browsing  
- Handles cookie consent popup automatically  
- Extracts product metadata, nameplate specs, BOM (bill of materials), images, and manual PDFs  
- Saves all product data in a structured directory (`output/assets`)  

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12
- Google Chrome browser
- [ChromeDriver](https://sites.google.com/chromium.org/driver/) (ensure it's compatible with your Chrome version)

---

### 🔧 Installation

#### Using `uv` (recommended for reproducible and isolated environments)

```bash
# Install uv if you haven't already

# Create and enter a new virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate

# Install dependencies from pyproject.toml
uv pip install -r requirements.txt
```

### 🧪 Running the Scraper

After setting up the environment and dependencies:
```bash
python src/main.py
```
or
```bash
uv run src/main.py
```

### 🗂 Output Structure
```
output/
├── 34-6610-3704.json
├── assets/
│   └── 34-6610-3704/
│       ├── manual.pdf
│       └── img.jpg
```
