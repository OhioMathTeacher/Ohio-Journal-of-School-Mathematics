# Deployment Guide — Hosted Citation Validator

This tool can be deployed as a free hosted web app so anyone can use it
from a browser with no install.

---

## Option 1: Hugging Face Spaces (Recommended)

**URL format:** `https://huggingface.co/spaces/YourName/citation-validator`
**Cost:** Free
**Cold start:** ~30 seconds after idle (sleeps after ~48 hours of no visitors)

### Steps

1. Create a Hugging Face account at https://huggingface.co/join

2. Create a new Space:
   - Go to https://huggingface.co/new-space
   - Name: `citation-validator`
   - SDK: **Docker**
   - Visibility: **Public**

3. Clone the Space repo and copy our files in:
   ```bash
   git clone https://huggingface.co/spaces/YourName/citation-validator hf-space
   cd hf-space

   # Copy the app files from this repo
   cp -r /path/to/Ohio-Journal-of-School-Mathematics/* .

   # The Dockerfile is already included in this repo.
   # Hugging Face will build and deploy it automatically.

   git add .
   git commit -m "Deploy citation validator"
   git push
   ```

4. Wait 2–3 minutes for the build. Visit your Space URL.

### What the user sees

- A web page with a text area for pasting BibTeX
- Drag-and-drop support for .bib files
- Per-citation results: valid, warning, suspicious, invalid
- Optional AI analysis (user provides their own API key)

---

## Option 2: PythonAnywhere

**URL format:** `https://YourName.pythonanywhere.com`
**Cost:** Free
**Always awake:** Yes (free tier requires manual renewal every 3 months)

### Steps

1. Create account at https://www.pythonanywhere.com

2. Upload the repo (or clone from GitHub):
   ```bash
   git clone https://github.com/OhioMathTeacher/Ohio-Journal-of-School-Mathematics.git
   ```

3. Create a new Web App:
   - Framework: **Flask**
   - Python version: **3.11**
   - Source code: `/home/YourName/Ohio-Journal-of-School-Mathematics/scripts`
   - WSGI file: set `application` to import from `webapp`

4. Edit the WSGI config file:
   ```python
   import sys
   sys.path.insert(0, '/home/YourName/Ohio-Journal-of-School-Mathematics/scripts')
   from webapp import app as application
   ```

5. Install dependencies in a Bash console:
   ```bash
   pip install -r /home/YourName/Ohio-Journal-of-School-Mathematics/scripts/requirements.txt
   ```

6. Reload the web app.

---

## Option 3: Render

**URL format:** `https://your-app.onrender.com`
**Cost:** Free
**Cold start:** ~60 seconds after 15 min idle

### Steps

1. Create account at https://render.com

2. New Web Service → connect your GitHub repo

3. Settings:
   - Build command: `pip install -r scripts/requirements.txt gunicorn`
   - Start command: `cd scripts && gunicorn --bind 0.0.0.0:$PORT --timeout 120 webapp:app`

4. Deploy.

---

## Testing the deployment

After deploying, test with a known citation:

```bibtex
@article{test2024,
  author = {Einstein, Albert},
  title = {On the Electrodynamics of Moving Bodies},
  journal = {Annalen der Physik},
  year = {1905},
  doi = {10.1002/andp.19053221004}
}
```

This should return `valid` — the DOI resolves correctly in CrossRef.

Then test with a known fake:

```bibtex
@article{fake2024,
  author = {Smith, John and Doe, Jane},
  title = {A Comprehensive Framework for Quantum Neural Networks},
  journal = {Nature Machine Intelligence},
  year = {2024},
  doi = {10.1038/s42256-024-99999-z}
}
```

This should return `suspicious` or `invalid` — the DOI doesn't exist.
