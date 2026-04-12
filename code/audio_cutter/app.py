from flask import Flask, render_template, request, send_file
from pydub import AudioSegment
from io import BytesIO

app = Flask(__name__)

def to_millis(time_str):
    h, m, s = map(int, time_str.split(':'))
    return (h * 3600 + m * 60 + s) * 1000


@app.route('/audio-cutter')
def index():
    return render_template('index.html')


@app.route('/audio-cutter/cut', methods=['POST'])
def cut_audio():
    file = request.files['audio']

    start = to_millis(request.form['start'])
    end = to_millis(request.form['end'])

    audio = AudioSegment.from_file(file)
    cut_audio = audio[start:end]

    buffer = BytesIO()
    cut_audio.export(buffer, format="mp3")
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="cut_audio.mp3",
        mimetype="audio/mpeg"
    )
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=50010)
