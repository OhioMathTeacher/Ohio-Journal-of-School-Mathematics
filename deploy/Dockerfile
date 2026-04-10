FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY scripts/requirements.txt scripts/requirements.txt
RUN pip install --no-cache-dir -r scripts/requirements.txt gunicorn

# Copy the full repository
COPY . .

# Hugging Face Spaces expects port 7860
EXPOSE 7860

# Run with gunicorn for production (Flask dev server is not suitable)
# Workers set to 2 — enough for a demo tool, low memory footprint
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--workers", "2", "--timeout", "120", "--chdir", "scripts", "webapp:app"]
