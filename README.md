# AI Resume Analyzer

A Flask web app that scores your resume against any job description using NLP,
and recommends the top job roles that suit your skills.
Built as part of my portfolio to learn Flask + scikit-learn + basic NLP techniques.

## What it does

Upload a resume (PDF or DOCX), and choose one of two modes:

### 1. Full Analyzer Mode
Paste a job description → get:
- An ATS compatibility score out of 100
- Breakdown across 4 dimensions (keywords, sections, formatting, semantic match)
- List of matched vs missing keywords
- Personalized improvement suggestions
- Top 5 job roles that fit your resume

### 2. Job Match Only Mode
Just upload the resume → get:
- Top 10 matching job roles with % match
- Skills you already have for each role
- Must-learn (required) and nice-to-have (preferred) skills you're missing

Runs in under 3 seconds on my machine.

## Tech Stack

- **Backend**: Python 3.11, Flask, Flask-CORS
- **NLP**: scikit-learn (TF-IDF + cosine similarity), NLTK
- **Parsing**: pdfplumber (PDF), python-docx (DOCX)
- **Frontend**: HTML, CSS, vanilla JS, Chart.js
- **Testing**: pytest
- **Deploy**: Gunicorn + Procfile (Render / Railway ready)

## Setup

See `SETUP.md` for detailed steps. Quick version:

```bash
python -m venv venv
venv\Scripts\activate      # Windows
pip install --only-binary=:all: -r requirements.txt
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords')"
python run.py
```

Then open http://localhost:5000

## Project Structure

```
ai-resume-analyzer/
├── app/
│   ├── __init__.py            # flask app factory
│   ├── config.py              # config
│   ├── routes.py              # HTTP routes + REST API
│   ├── services/
│   │   ├── parser.py          # PDF/DOCX text extraction
│   │   ├── nlp_extractor.py   # TF-IDF keyword extraction
│   │   ├── scorer.py          # ATS scoring engine
│   │   ├── suggester.py       # suggestion generator
│   │   └── job_matcher.py     # job recommendation engine
│   ├── static/
│   │   ├── style.css          # glassmorphism UI
│   │   └── main.js            # frontend logic
│   └── templates/
│       └── index.html         # main page
├── data/
│   ├── skills_taxonomy.txt    # curated skills list (80+ tech skills)
│   └── job_roles.py           # 12 job role definitions
├── tests/                     # pytest suite
├── requirements.txt
├── run.py                     # entry point
├── Procfile                   # for deploy
├── runtime.txt                # Python version pin
├── SETUP.md                   # setup guide
└── README.md
```

## How the ATS scoring works

Split the ATS score into 4 weighted components:

| Component | Weight | What it measures |
|-----------|--------|------------------|
| Keyword coverage | 50 | % of JD keywords found in the resume |
| Section completeness | 20 | Whether standard sections are present |
| Formatting | 15 | Length, bullet density, contact info |
| Semantic similarity | 15 | Cosine similarity of resume vs JD (TF-IDF vectors) |

The keyword extraction combines two approaches:
1. Match against a curated skills taxonomy (80+ tech skills)
2. TF-IDF top terms for anything not in the taxonomy

## How Job Matching works

Each job role in the database has:
- **Required skills** (must-have) — worth 2 points each
- **Preferred skills** (nice-to-have) — worth 1 point each

Score for a role = (matched required × 2 + matched preferred × 1) / total possible × 100

Plus a +5 bonus if all required skills are matched.

Top 5-10 roles by score are returned, ranked with medals.

### 12 job roles in the DB

- Backend Developer (Java/Spring Boot)
- Backend Developer (Python/Flask)
- Full Stack Developer
- Frontend Developer
- Data Analyst
- Data Scientist / ML Engineer
- NLP / AI Engineer
- DevOps / SRE Intern
- Cloud Engineer (AWS)
- Software Engineer Intern (Generalist)
- Database Administrator / SQL Developer
- QA / Test Automation Engineer

## API Endpoints

### `GET /`
Main web page

### `GET /api/health`
Health check → `{"status": "ok"}`

### `POST /api/analyze` (multipart/form-data)
Full analysis — needs both resume + JD
- `resume` — PDF or DOCX file
- `job_description` — JD as text

Returns JSON with score, breakdown, matched/missing keywords, suggestions, and job matches.

### `POST /api/job-match` (multipart/form-data)
Just find matching jobs — no JD needed
- `resume` — PDF or DOCX file

Returns JSON with top 10 job matches + detected skills.

## Testing

```bash
pytest tests/ -v
```

## Deployment

The project is ready to deploy on Render or Railway (Procfile + runtime.txt included).

### Render (Free tier)
1. Push to GitHub
2. render.com → New Web Service → Connect repo
3. Build: `pip install -r requirements.txt`
4. Start: `gunicorn run:app --bind 0.0.0.0:$PORT --timeout 120`

### Railway
1. Push to GitHub
2. railway.app → New Project → Deploy from GitHub
3. Auto-detects Flask, done

## What I learned

- Flask app factory pattern
- TF-IDF vectorization with scikit-learn
- Cosine similarity for text comparison
- Weighted scoring algorithms
- File uploads and multipart form handling
- Building a REST API with proper error handling
- Responsive frontend without any framework
- Deploying Python apps with Gunicorn

## Author

Harshal Munot — B.Tech CSE (AI & DS), Parul University

---

## v2.0 — New Features

### 🌐 Multi-Language Support
- English, हिन्दी (Hindi), Español (Spanish)
- Language dropdown in the navbar, choice saved in localStorage
- Add a language = add a dict in `app/services/translations.py`

### 👤 LinkedIn Import
- Paste your public LinkedIn profile URL → auto-fill name/skills/education
- Also accepts pasted profile text (LinkedIn blocks bots, so it's best-effort)
- `POST /api/linkedin/import` endpoint

### ✉️ Cover Letter Generator
- Generates a tailored 4-paragraph cover letter from your resume + JD
- Smart section: intro, JD-skill alignment, top project highlight, closing
- Preview in the app + download as .docx
- `POST /api/cover-letter` and `POST /api/cover-letter/export`

### 📚 Resume Templates Library
- 3 built-in styles: **Modern**, **Classic**, **Creative**
- Live preview in a new tab + export your actual resume as .docx in that style
- Template engine in `app/services/resume_templates.py` (easy to add more)
- `GET /api/templates`, `GET /api/templates/<id>/preview`, `POST /api/templates/<id>/export`

### 🤖 Career Coach AI (chat)
- Floating chat widget (bottom-right corner)
- Rule-based answers using your last analysis (score, missing keywords, job matches)
- Optional: set `OPENAI_API_KEY` env var to get free-form LLM answers (gpt-4o-mini)
- `POST /api/coach`

### Deploy note
- `requirements.txt` now includes `requests` (LinkedIn import) and python-docx (already there).
- `OPENAI_API_KEY` is optional - the app works fully without it.
