import os

PDF_SERVICE = os.getenv("PDF_SERVICE_URL", "http://pdf-service:5001")
YTDL_SERVICE = os.getenv("YTDL_SERVICE_URL", "http://youtube-service:5002")
AUDIO_SERVICE = os.getenv("AUDIO_SERVICE_URL", "http://audio-converter-service:5003")
MUSIC_SERVICE = os.getenv("MUSIC_SERVICE_URL", "http://music-service:5004")
WORD2PDF_SERVICE = os.getenv("WORD2PDF_SERVICE_URL", "http://word2pdf-service:5005")
USER_SERVICE = os.getenv("USER_SERVICE_URL", "http://user-service:5006")
URL_SHORTENER_SERVICE = os.getenv("URL_SHORTENER_SERVICE_URL","http://url-shortner-service:50007")
CIDR_SERVICE = os.getenv("CIDR_SERVICE_URL", "http://cidr-service:5008")
TODO_SERVICE = os.getenv("TODO_SERVICE_URL","http://todo:50009")
AUDIO_CUTTER_SERVICE = os.getenv("AUDIO_CUTTER_SERVICE_URL","http://audio-cutter-service:50010")
AUDIO_COMBINER_SERVICE = os.getenv("AUDIO_COMBINER_SERVICE_URL","http://audio-combiner-service:5011")
METRICS_SERVICE = os.getenv("METRICS_SERVICE_URL", "http://metrics-service:5012")


