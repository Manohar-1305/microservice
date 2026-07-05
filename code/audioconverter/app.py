import pika
import uuid
import json
import base64
import os
import time

app = Flask(__name__)

RABBITMQ_URL = os.getenv(
    "RABBITMQ_URL",
    "amqp://admin:changeme@rabbitmq:5672/"
)
REQUEST_QUEUE = "audio_convert_requests"


def get_connection():
    params = pika.URLParameters(RABBITMQ_URL)
    return pika.BlockingConnection(params)


@app.route('/convert', methods=['GET'])
def convert_page():
    return render_template('text_to_audio.html')


@app.route('/convert', methods=['POST'])
def convert():
    data = request.get_json()
    text = data.get('text')
    if not text:
        return jsonify({'error': 'Please enter some text'}), 400

    connection = get_connection()
    channel = connection.channel()
    channel.queue_declare(queue=REQUEST_QUEUE, durable=True)

    result = channel.queue_declare(queue='', exclusive=True)
    callback_queue = result.method.queue

    correlation_id = str(uuid.uuid4())
    response_holder = {}

    def on_response(ch, method, props, body):
        if props.correlation_id == correlation_id:
            response_holder['body'] = body
            ch.stop_consuming()

    channel.basic_consume(
        queue=callback_queue,
        on_message_callback=on_response,
        auto_ack=True
    )

    channel.basic_publish(
        exchange='',
        routing_key=REQUEST_QUEUE,
        properties=pika.BasicProperties(
            reply_to=callback_queue,
            correlation_id=correlation_id,
            delivery_mode=2,
        ),
        body=json.dumps({'text': text, 'lang': 'en', 'tld': 'co.in'})
    )

    timeout = 30
    start = time.time()
    while 'body' not in response_holder:
        connection.process_data_events(time_limit=1)
        if time.time() - start > timeout:
            connection.close()
            return jsonify({'error': 'conversion timed out'}), 504

    connection.close()

    payload = json.loads(response_holder['body'])
    if 'error' in payload:
        return jsonify({'error': payload['error']}), 500

    audio_bytes = base64.b64decode(payload['audio'])
    return Response(audio_bytes, mimetype='audio/mpeg')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5003)
