# Use lightweight Python
FROM python:3.11-slim

# Set working dir
WORKDIR /app

# Copy files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir flask

# Expose port
EXPOSE 5012

# Run app
CMD ["python", "app.py"]