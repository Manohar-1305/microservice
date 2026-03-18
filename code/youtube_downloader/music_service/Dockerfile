FROM python:3.11-slim

ENV SDL_AUDIODRIVER=dummy
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libsdl2-mixer-2.0-0 \
    libsdl2-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p music_files

EXPOSE 5004

CMD ["python","app.py"]
