import requests
from flask import Flask, request, Response, render_template, redirect, session
import config

app = Flask(__name__)
app.secret_key = "supersecret"

AUDIO_SERVICE = config.AUDIO_SERVICE
MUSIC_SERVICE = config.MUSIC_SERVICE
PDF_SERVICE = config.PDF_SERVICE
WORD2PDF_SERVICE = config.WORD2PDF_SERVICE
YTDL_SERVICE = config.YTDL_SERVICE
USER_SERVICE = config.USER_SERVICE


# -------- ROOT --------
@app.route('/')
def root():
    return redirect('/login')


# -------- LOGIN --------
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        error = request.args.get('error')

        r = requests.get(f"{USER_SERVICE}/login")

        html = r.text

        # inject error message into HTML
        if error:
            html = html.replace(
                "</form>",
                f"""
                <div style='color:red;text-align:center;margin-top:10px;'>
                    {error}
                </div>
                </form>
                """
            )

        return html

    r = requests.post(f"{USER_SERVICE}/login", data=request.form, allow_redirects=False)

    if r.status_code == 302:
        session['user'] = request.form['username']
        return redirect('/home')

    return redirect('/login?error=Incorrect+credentials')
# -------- REGISTER --------
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        r = requests.get(f"{USER_SERVICE}/register")
        return Response(r.content, r.status_code)

    r = requests.post(f"{USER_SERVICE}/register", data=request.form, allow_redirects=False)

    # success → redirect to login
    if r.status_code == 302:
        return redirect('/login')

    return "User already exists"


# -------- HOME --------
@app.route('/home')
def home():
    if 'user' not in session:
        return redirect('/login')
    return render_template("home.html")


# -------- AUTH CHECK --------
def check_auth():
    if 'user' not in session:
        return redirect('/login')
    return None


# -------- SERVICES --------
@app.route('/audio')
def audio_page():
    auth = check_auth()
    if auth: return auth
    r = requests.get(f"{AUDIO_SERVICE}/convert")
    return Response(r.content, r.status_code)


@app.route('/music')
def music_page():
    auth = check_auth()
    if auth: return auth
    return requests.get(f"{MUSIC_SERVICE}/").text


@app.route('/api/audio/convert', methods=['POST'])
def convert_text_to_audio():
    auth = check_auth()
    if auth: return auth
    r = requests.post(f"{AUDIO_SERVICE}/convert", json={"text": request.form.get('text')})
    return Response(r.content, r.status_code)


@app.route('/upload', methods=['POST'])
def music_upload():
    auth = check_auth()
    if auth: return auth
    file = request.files['music']
    r = requests.post(f"{MUSIC_SERVICE}/upload",
                      files={'music': (file.filename, file.stream, file.mimetype)})
    return Response(r.content, r.status_code)


@app.route('/list')
def music_list():
    auth = check_auth()
    if auth: return auth
    r = requests.get(f"{MUSIC_SERVICE}/list")
    return Response(r.content, r.status_code)


@app.route('/music_files/<filename>')
def music_files(filename):
    auth = check_auth()
    if auth: return auth
    r = requests.get(f"{MUSIC_SERVICE}/music_files/{filename}")
    return Response(r.content, r.status_code)


@app.route('/pdf')
def pdf_page():
    auth = check_auth()
    if auth: return auth
    r = requests.get(f"{PDF_SERVICE}/pdf_converter")
    return Response(r.content, r.status_code)


@app.route('/api/pdf', methods=['POST'])
def convert_pdf():
    auth = check_auth()
    if auth: return auth
    file = request.files['file']
    r = requests.post(f"{PDF_SERVICE}/convert",
                      files={'file': (file.filename, file.stream, file.mimetype)})
    return Response(r.content, r.status_code)

# -------- WORD → PDF UI --------
@app.route('/word_to_pdf')
def word_to_pdf():
    auth = check_auth()
    if auth: return auth

    r = requests.get(f"{WORD2PDF_SERVICE}/")
    return Response(r.content, r.status_code)

# -------- WORD → PDF API --------
@app.route('/word-to-pdf/convert', methods=['POST'])
def word_to_pdf_api():
    auth = check_auth()
    if auth: return auth

    if 'word_file' not in request.files:
        return {"success": False, "error": "No file received"}, 400

    file = request.files['word_file']

    try:
        r = requests.post(
            f"{WORD2PDF_SERVICE}/pdf_converter",
            files={'word_file': (file.filename, file.stream, file.content_type)}
        )

        return Response(
            r.content,
            status=r.status_code,
            content_type=r.headers.get('Content-Type')
        )

    except Exception as e:
        return {"success": False, "error": str(e)}, 500

# -------- DOWNLOAD (FIXED STREAMING) --------
@app.route('/download/<filename>')
def download_pdf(filename):
    auth = check_auth()
    if auth: return auth

    r = requests.get(f"{WORD2PDF_SERVICE}/download/{filename}", stream=True)

    return Response(
        r.iter_content(chunk_size=8192),
        status=r.status_code,
        headers=dict(r.headers)
    )

@app.route('/youtube')
def youtube_ui():
    auth = check_auth()
    if auth: return auth
    r = requests.get(f"{YTDL_SERVICE}")   # <-- FIX HERE
    return Response(r.content, r.status_code)

@app.route('/api/youtube/download')
def youtube_download():
    auth = check_auth()
    if auth: return auth

    url = request.args.get('url')

    r = requests.get(
        f"{YTDL_SERVICE}/download_best",
        params={"url": url},
        stream=True
    )

    return Response(r.content, status=r.status_code, headers=dict(r.headers))

@app.route('/logout')
def logout():
    session.clear()   # destroy session
    return redirect('/login')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
