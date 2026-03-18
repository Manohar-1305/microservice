import os

AUDIO_SERVICE = os.getenv("AUDIO_SERVICE_URL", "http://audio-service:5003")
MUSIC_SERVICE = os.getenv("MUSIC_SERVICE_URL", "http://music-service:5004")
PDF_SERVICE = os.getenv("PDF_SERVICE_URL", "http://pdf-service:5001")
WORD2PDF_SERVICE = os.getenv("WORD2PDF_SERVICE_URL", "http://word2pdf-service:5005")
YTDL_SERVICE = os.getenv("YTDL_SERVICE_URL", "http://youtube-service:5002")
USER_SERVICE = os.getenv("USER_SERVICE_URL", "http://user-service:5006")
