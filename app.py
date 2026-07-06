from flask import Flask, redirect, request

app = Flask(__name__)

@app.route('/stream')
def get_stream():
    token = request.args.get('token')
    server = request.args.get('server', '1')
    
    if not token:
        return "Token missing!", 400

    # সরাসরি রিডাইরেক্ট (কোনো হেডার ছাড়া, কারণ এটি ব্রাউজার হ্যান্ডেল করবে)
    # মিডিয়া সার্ভার যখন দেখবে রিকোয়েস্টটি ব্রাউজার থেকে আসছে, সে আর 403 দেবে না।
    target_url = f"https://lb8.strmd.st/secure/QAUWckhqUnlkNqygcdGCcGOPskuUcSju/rtmp/stream/{token}/{server}/playlist.m3u8"
    
    return redirect(target_url, code=302)
