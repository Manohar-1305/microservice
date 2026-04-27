# Dockerfile (inside micro-bot/)
FROM golang:1.22-alpine

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .

RUN go build -o app .

EXPOSE 5013

CMD ["./app"]