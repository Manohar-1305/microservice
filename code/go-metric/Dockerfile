FROM golang:1.22-alpine

WORKDIR /app

COPY . .

RUN go build -o metrics-app

EXPOSE 5012

CMD ["./metrics-app"]
