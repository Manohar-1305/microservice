from flask import Flask, render_template, request, send_file
from pydub import AudioSegment
from io import BytesIO

app = Flask(__name__)

# match gateway route
@app.route('/audio-combiner')
def index():
    return render_template('index.html')


# match gateway route
@app.route('/audio-combiner/combine', methods=['POST'])
def combine_audio():
    files = request.files.getlist('audio')

    if not files:
        return "No files uploaded", 400

    combined = None

    for file in files:
        audio = AudioSegment.from_file(file)

        if combined is None:
            combined = audio
        else:
            combined += audio

    buffer = BytesIO()
    combined.export(buffer, format="mp3")
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="combined_audio.mp3",
        mimetype="audio/mpeg"
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5011, debug=True)
