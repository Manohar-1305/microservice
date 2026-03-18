Gateway
=======
docker stop gateway-service && docker rm gateway-service && docker build --no-cache -t gateway-service ~/gateway && docker run -d --name gateway-service --network micro-net -p 5000:5000 gateway-service

Audio Service
==============
docker stop audio-service && docker rm audio-service && docker build --no-cache -t audio-service ~/audioconverter && docker run -d --name audio-service --network micro-net -p 5003:5003 audio-service

Music service
==============
docker rm -f music-service 2>/dev/null; docker build --no-cache -t music-service ~/music_service && docker run -d --name music-service --network micro-net -p 5004:5004 music-service

YOUTUBE Service
=================
docker rm -f youtube-service 2>/dev/null; docker build --no-cache -t youtube-service ~/youtube_downloader && docker run -d --name youtube-service --network micro-net -p 5002:5002 youtube-service

PDF converter
==============
docker rm -f pdf-service 2>/dev/null; docker build --no-cache -t pdf-service ~/pdf_service && docker run -d --name pdf-service --network micro-net -p 5001:5001 pdf-service

word converter
==============
docker rm -f word2pdf-service 2>/dev/null; docker build --no-cache -t word2pdf-service . && docker run -d --name word2pdf-service --network micro-net -p 5005:5005 word2pdf-service

User Service
=============
docker stop user-service && docker rm user-service && docker build --no-cache -t user-service ~/user_service && docker run -d --name user-service --network micro-net -p 5006:5006 user-service



upload the image locally
==========================
kind load docker-image gateway-service:latest --name multi-node-cluster

kind load docker-image audio-service:latest --name multi-node-cluster

kind load docker-image music-service:latest --name multi-node-cluster

kind load docker-image pdf-service:latest --name multi-node-cluster

kind load docker-image user-service:latest --name multi-node-cluster

kind load docker-image word2pdf-service:latest --name multi-node-cluster

kind load docker-image youtube-service:latest --name multi-node-cluster
