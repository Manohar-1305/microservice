FROM python:3.12-slim

# Prevent python from writing pyc files and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Flask app will listen on 50009
EXPOSE 50009

# Run Flask
CMD ["python", "app.py"]
