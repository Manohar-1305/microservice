import pika
import json
import base64
import io
import os
from gtts import gTTS

RABBITMQ_URL = os.getenv(
    "RABBITMQ_URL",
    "amqp://admin:changeme@rabbitmq:5672/"
)
REQUEST_QUEUE = "audio_convert_requests"


def process_request(text, lang, tld):
    tts = gTTS(text, lang=lang, tld=tld)
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    return mp3_fp.read()


def on_request(ch, method, props, body):
    data = json.loads(body)
    text = data.get('text')
    lang = data.get('lang', 'en')
    tld = data.get('tld', 'co.in')

    try:
        audio_bytes = process_request(text, lang, tld)
        response = {'audio': base64.b64encode(audio_bytes).decode('utf-8')}
    except Exception as e:
        response = {'error': str(e)}

    ch.basic_publish(
        exchange='',
        routing_key=props.reply_to,
        properties=pika.BasicProperties(correlation_id=props.correlation_id),
        body=json.dumps(response)
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue=REQUEST_QUEUE, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=REQUEST_QUEUE, on_message_callback=on_request)
    print("audio-worker waiting for jobs...")
    channel.start_consuming()


if __name__ == '__main__':
    main()
