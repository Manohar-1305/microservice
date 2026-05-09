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
URL_SHORTENER_SERVICE = config.URL_SHORTENER_SERVICE
TODO_SERVICE = config.TODO_SERVICE
AUDIO_COMBINER_SERVICE = config.AUDIO_COMBINER_SERVICE
AUDIO_CUTTER_SERVICE = config.AUDIO_CUTTER_SERVICE
CIDR_SERVICE = config.CIDR_SERVICE
METRICS_SERVICE = config.METRICS_SERVICE
PAYMENT_SERVICE = config.PAYMENT_SERVICE

@app.before_request
def track_all_requests():
    path = request.path

    # skip static + metrics UI + stats API
    if path.startswith("/static") or path.startswith("/metrics") or path == "/api/stats":
        return

    try:
        requests.get(
            f"{METRICS_SERVICE}/api/hit",
            params={"service": path},
            timeout=0.2
        )
    except:
        pass

@app.route('/api/stats')
def metrics_stats():
    r = requests.get(f"{METRICS_SERVICE}/api/stats")
    return Response(r.content, r.status_code, content_type="application/json")
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

@app.route('/bot')
def bot():
    return render_template("bot.html")


@app.route('/bot/ws')
def bot_ws_proxy():
    def proxy():
        with requests.get(f"{BOT_SERVICE}/ws", stream=True) as r:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    yield chunk
    return Response(proxy(), content_type="application/octet-stream")

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/metrics')
def metrics_ui():
    r = requests.get(f"{METRICS_SERVICE}/")
    return Response(r.content, r.status_code)

# -------- CIDR TOOL --------
@app.route('/cidr')
def cidr_page():
    auth = check_auth()
    if auth:
        return auth

    r = requests.get(f"{CIDR_SERVICE}/")
    return Response(r.content, r.status_code)


@app.route('/cidr/calculate', methods=['POST'])
def cidr_calculate():
    auth = check_auth()
    if auth:
        return auth

    r = requests.post(
        f"{CIDR_SERVICE}/",
        data=request.form
    )

    return Response(r.content, r.status_code)

# -------- PAYMENT SERVICE --------

@app.route('/payment')
def payment_page():
    auth = check_auth()
    if auth:
        return auth

    r = requests.get(f"{PAYMENT_SERVICE}/")
    return Response(r.content, r.status_code)


@app.route('/payment/process', methods=['POST'])
def payment_process():
    auth = check_auth()
    if auth:
        return auth

    r = requests.post(
        f"{PAYMENT_SERVICE}/process",
        data=request.form
    )

    return Response(
        r.content,
        r.status_code,
        content_type=r.headers.get('Content-Type')
    )
#----------Audio Cutter------------
@app.route('/audio-cutter')
def audio_cutter_page():
    auth = check_auth()
    if auth: return auth

    r = requests.get(f"{AUDIO_CUTTER_SERVICE}/audio-cutter")
    return Response(r.content, r.status_code)


@app.route('/audio-cutter/cut', methods=['POST'])
def audio_cutter_cut():
    auth = check_auth()
    if auth: return auth

    file = request.files['audio']

    r = requests.post(
        f"{AUDIO_CUTTER_SERVICE}/audio-cutter/cut",
        files={'audio': (file.filename, file.stream, file.mimetype)},
        data={
            'start': request.form['start'],
            'end': request.form['end']
        }
    )

    return Response(
        r.content,
        r.status_code,
        content_type=r.headers.get('Content-Type'),
        headers={
            "Content-Disposition": r.headers.get("Content-Disposition", "")
        }
    )


# -------- AUDIO COMBINER --------
@app.route('/audio-combiner')
def audio_combiner_page():
    auth = check_auth()
    if auth:
        return auth

    r = requests.get(f"{AUDIO_COMBINER_SERVICE}/audio-combiner")
    return Response(r.content, r.status_code)


@app.route('/audio-combiner/combine', methods=['POST'])
def audio_combiner_combine():
    auth = check_auth()
    if auth:
        return auth

    files = request.files.getlist('audio')

    multiple_files = [
        ('audio', (file.filename, file.stream, file.mimetype))
        for file in files
    ]

    r = requests.post(
        f"{AUDIO_COMBINER_SERVICE}/audio-combiner/combine",
        files=multiple_files
    )

    return Response(
        r.content,
        r.status_code,
        content_type=r.headers.get('Content-Type'),
        headers={
            "Content-Disposition": r.headers.get("Content-Disposition", "")
        }
    )

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

# -------------Shortner-----------

@app.route('/shortener')
def shortener_page():
    auth = check_auth()
    if auth: return auth

    r = requests.get(f"{URL_SHORTENER_SERVICE}/")
    return Response(r.content, r.status_code)

@app.route('/api/shorten', methods=['POST'])
def shorten_url():
    auth = check_auth()
    if auth: return auth

    r = requests.post(
        f"{URL_SHORTENER_SERVICE}/api/shorten",
        json=request.get_json()
    )

    return Response(
        r.content,
        r.status_code,
        content_type=r.headers.get('Content-Type')
    )

@app.route('/s/<code>')
def redirect_short_url(code):
    r = requests.get(
        f"{URL_SHORTENER_SERVICE}/{code}",
        allow_redirects=False
    )

    return Response(
        r.content,
        r.status_code,
        headers=dict(r.headers)
    )


@app.route('/todo')
def todo_page():
    auth = check_auth()
    if auth: return auth

    r = requests.get(f"{TODO_SERVICE}/")
    return Response(r.content, r.status_code)

@app.route('/add', methods=['POST'])
def todo_add():
    auth = check_auth()
    if auth: return auth

    r = requests.post(
        f"{TODO_SERVICE}/add",
        data=request.form
    )

    return redirect('/todo')

@app.route('/toggle/<int:task_id>', methods=['POST'])
def todo_toggle(task_id):
    auth = check_auth()
    if auth: return auth

    requests.post(f"{TODO_SERVICE}/toggle/{task_id}")
    return redirect('/todo')

@app.route('/delete/<int:task_id>', methods=['POST'])
def todo_delete(task_id):
    auth = check_auth()
    if auth: return auth

    requests.post(f"{TODO_SERVICE}/delete/{task_id}")
    return redirect('/todo')

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def todo_edit(task_id):
    auth = check_auth()
    if auth: return auth

    if request.method == 'GET':
        r = requests.get(f"{TODO_SERVICE}/edit/{task_id}")
        return Response(r.content, r.status_code)

    requests.post(
        f"{TODO_SERVICE}/edit/{task_id}",
        data=request.form
    )
    return redirect('/todo')

@app.route('/static/<path:filename>')
def todo_static(filename):
    r = requests.get(f"{TODO_SERVICE}/static/{filename}")
    return Response(r.content, r.status_code, content_type=r.headers.get('Content-Type'))

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
