FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN apt-get update && apt-get install -y \
    libnss3 libatk-bridge2.0-0 libgtk-3-0 libgtk-4-1 \
    libgstreamer1.0-0 libgstreamer-plugins-base1.0-0 \
    libglib2.0-0 libnspr4 libx11-xcb1 libxcomposite1 \
    libxdamage1 libxrandr2 libgbm1 libasound2 \
    libpangocairo-1.0-0 libpango-1.0-0 libcups2 \
    libatk1.0-0 libdrm2 libxkbcommon0 libxfixes3 \
    libxext6 libx11-6 libxcb1 libxshmfence1 \
    libglu1-mesa libegl1 libopengl0 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install playwright && playwright install
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p downloads

EXPOSE 5002

CMD ["python","app.py"]
