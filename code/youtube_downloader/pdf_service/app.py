from flask import Flask, request, send_file, render_template
from pdf2docx import Converter
import io
import os

app = Flask(__name__)

@app.route('/pdf_converter')
def pdf_ui():
    return render_template('pdf_converter.html')

@app.route('/convert', methods=['POST'])
def convert_pdf_to_word():
    file = request.files.get('file')

    if not file or file.filename == '':
        return {"error": "No file provided"}, 400

    pdf_path = "temp_upload.pdf"
    output_path = "temp_output.docx"

    file.save(pdf_path)

    cv = Converter(pdf_path)
    cv.convert(output_path, start=0, end=None)
    cv.close()

    output_stream = io.BytesIO()

    with open(output_path, "rb") as f:
        output_stream.write(f.read())

    os.remove(pdf_path)
    os.remove(output_path)

    output_stream.seek(0)

    return send_file(
        output_stream,
        as_attachment=True,
        download_name=f"{os.path.splitext(file.filename)[0]}.docx",
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
