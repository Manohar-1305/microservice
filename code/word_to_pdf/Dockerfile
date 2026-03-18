FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install required system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice \
    python3 \
    python3-venv \
    python3-pip \
    fonts-dejavu-core \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create virtual environment
RUN python3 -m venv /app/venv

# Activate venv and install requirements
COPY requirements.txt .
# RUN . /app/venv/bin/activate && pip install --no-cache-dir -r requirements.txt
RUN . /app/venv/bin/activate && pip install --no-cache-dir -r requirements.txt
# Copy application code
COPY . .

# Expose the Flask port
EXPOSE 5005

# Set environment path to use venv
ENV PATH="/app/venv/bin:$PATH"

# Run app
CMD ["python", "app.py"]

