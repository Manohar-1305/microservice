from flask import Flask, request, send_file, render_template, jsonify
from playwright.sync_api import sync_playwright
import os
import uuid
import requests

app = Flask(__name__)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


@app.route('/')
@app.route('/youtube')
def youtube_home():
    return render_template('youtube.html')


@app.route('/fetch_playlist')
def fetch_playlist():

    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Missing URL parameter"}), 400

    try:
        playlist_url = f"https://www.youtube.com/oembed?url={url}&format=json"
        r = requests.get(playlist_url)
        data = r.json()

        videos = [{
            "title": data.get("title"),
            "url": url
        }]

        return jsonify({"videos": videos})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_stream_url(video_url):

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()

        page.goto(video_url)

        page.wait_for_timeout(5000)

        video_src = page.evaluate("""
        () => {
            const v = document.querySelector('video')
            if (v) {
                return v.src
            }
            return null
        }
        """)

        browser.close()

        return video_src


@app.route('/download_best')
def download_best():

    url = request.args.get('url')

    if not url:
        return "Missing URL parameter", 400

    try:
        import yt_dlp

        unique_id = str(uuid.uuid4())
        output_path = os.path.join(DOWNLOAD_DIR, f"{unique_id}.mp4")

        ydl_opts = {
            'outtmpl': output_path,
            'format': 'best',
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return send_file(
            output_path,
            as_attachment=True,
            download_name="video.mp4",
            mimetype="video/mp4"
        )

    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
