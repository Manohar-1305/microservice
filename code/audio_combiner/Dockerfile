FROM python:3.11-slim

WORKDIR /app

# install ffmpeg (required for pydub)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# copy files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5011

CMD ["python", "app.py"]