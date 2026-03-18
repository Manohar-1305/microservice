from flask import Flask, request, render_template, jsonify, send_file
from gtts import gTTS
import io

app = Flask(__name__)


@app.route('/convert', methods=['GET'])
def convert_page():
    return render_template('text_to_audio.html')


@app.route('/convert', methods=['POST'])
def convert():
    data = request.get_json()

    text = data.get('text')

    if not text:
        return jsonify({'error': 'Please enter some text'}), 400

    tts = gTTS(text, lang='en', tld='co.in')

    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)

    return send_file(
        mp3_fp,
        mimetype='audio/mpeg',
        as_attachment=False,
        download_name='output.mp3'
    )


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5003)
