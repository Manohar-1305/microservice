from flask import Flask, render_template, request
import qrcode
import base64
from io import BytesIO

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")


@app.route('/process', methods=['POST'])
def process_payment():

    name = request.form.get("name")
    amount = request.form.get("amount")
    method = request.form.get("method")

    print(f"Payment Received -> Name: {name}, Amount: {amount}, Method: {method}")

    qr_data = f"{method} PAYMENT | AMOUNT: {amount}"

    qr = qrcode.make(qr_data)

    buffer = BytesIO()

    qr.save(buffer, format="PNG")

    qr_base64 = base64.b64encode(
        buffer.getvalue()
    ).decode()

    return render_template(
        "successful.html",
        qr_code=qr_base64,
        amount=amount,
        method=method
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5014)
