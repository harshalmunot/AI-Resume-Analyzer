# Quick Setup Guide

## Prerequisites
- Python 3.10 or higher
- pip

## Steps

### 1. Extract the zip
Extract this folder somewhere on your PC.

### 2. Open PowerShell / Terminal in the folder
```powershell
cd path\to\ai-resume-analyzer-humanized
```

### 3. Create a virtual environment
```powershell
python -m venv venv
```

### 4. Activate the venv
```powershell
# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 5. Upgrade pip (Windows quirk)
```powershell
python -m pip install --upgrade pip
```

### 6. Install dependencies
```powershell
pip install --only-binary=:all: -r requirements.txt
```

### 7. Download NLTK data (first time only)
```powershell
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords')"
```

### 8. Run the app
```powershell
python run.py
```

### 9. Open in browser
http://localhost:5000

## Features

- **Full Analyzer** mode: Upload resume + JD → ATS score, breakdown, keywords, suggestions, job matches
- **Job Match Only** mode: Just upload resume → top 10 matching jobs with % scores
- **Theme toggle** (dark / light)
- **Drag & drop** file upload
- **12 job roles** in the recommendation database

## Testing
```powershell
pytest tests/ -v
```

## Deploy
See README.md for Render / Railway deployment instructions.
Both `Procfile` and `runtime.txt` are already included.
