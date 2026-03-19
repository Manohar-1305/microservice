FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install flask
RUN pip install flask mysql-connector-python

EXPOSE 5006

CMD ["python", "app.py"]
