from flask import Flask, Response, request
import requests

app = Flask(__name__)

@app.route('/stream')
def stream():
    # সরাসরি আপনার লিংকটি এখানে দিয়ে দিন
    url = "https://lb8.strmd.st/secure/QAUWckhqUnIkNqygcdGCcGOPskuUcSju/rtmp/stream/Kdmp7byfeEwY4hCRPQUJzS779TXojAc1upP_kMojK31W6fh4M05LUfVQJr8jvUU_RsAAzMbq4Q/1/playlist.m3u8"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Referer": "https://footstreams.me/"
    }
    
    try:
        # পাইথন দিয়ে ডাটা রিড করা
        response = requests.get(url, headers=headers, timeout=10)
        
        # ডাটা প্লেয়ারে পাঠানো
        return Response(response.text, mimetype='application/x-mpegURL')
    except Exception as e:
        return f"Error: {str(e)}", 500
