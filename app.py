import re
import requests
from flask import Flask, redirect

app = Flask(__name__)

@app.route('/')
def home():
    return "BDIX IPTV Server is Running!"

@app.route('/stream')
def get_stream():
    source_url = "https://footstreams.me/watch/star-sports-1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://footstreams.me/"
    }
    try:
        html_content = requests.get(source_url, headers=headers, timeout=10).text
        match = re.search(r'https://[a-zA-Z0-9\.]+\.strmd\.st/secure/[^\s"\']+playlist\.m3u8', html_content)
        if match:
            return redirect(match.group(0), code=302)
        return "Stream not found", 404
    except Exception as e:
        return f"Error: {str(e)}", 500
