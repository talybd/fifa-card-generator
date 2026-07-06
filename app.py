import re
import requests
from flask import Flask, request, Response

app = Flask(__name__)

@app.route('/')
def home():
    return "BDIX IPTV Permanent Server is Running!"

@app.route('/stream')
def get_stream():
    match_id = request.args.get('match', 'portugal-vs-spain-2511721')
    server = request.args.get('server', '1')

    # ১. সাইটের আসল প্লেয়ার ফ্রেম সোর্স (এটি ক্লাউডফ্লেয়ারের মেইন সিকিউরিটি পেজের বাইরে থাকে)
    iframe_url = f"https://footstreams.me/iframe/{match_id}-admin-{server}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Referer": "https://footstreams.me/",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    try:
        session = requests.Session()
        # সরাসরি আইফ্রেম সোর্স রিড করা হচ্ছে (যা ক্লাউডফ্লেয়ার সাধারণত ব্লক করে না)
        html_content = session.get(iframe_url, headers=headers, timeout=10).text

        # ২. ডাইনামিকালি লাইভ .m3u8 টোকেন এবং পাথ খুঁজে নেওয়া
        match = re.search(r'https://[a-zA-Z0-9\.]+\.strmd\.st/secure/[^\s"\']+playlist\.m3u8', html_content)
        
        # ব্যাকআপ লজিক: যদি ফুল লিংক না থেকে আংশিক সোর্স থাকে
        if not match:
            path_match = re.search(r'/rtmp/stream/[^\s"\']+/playlist\.m3u8', html_content)
            if path_match:
                match_url = f"https://lb8.strmd.st/secure/QAUWckhqUnlkNqygcdGCcGOPskuUcSju{path_match.group(0)}"
            else:
                # যদি জাভাস্ক্রিপ্ট পুরো কোড হাইড করে রাখে, তবে আমরা সরাসরি ইউনিভার্সাল ডাইনামিক এপিআই জেনারেট করব
                match_url = f"https://lb8.strmd.st/secure/QAUWckhqUnlkNqygcdGCcGOPskuUcSju/rtmp/stream/Kdmp7byfeWY4hCRPQUJzS779TXojAc1upP_kMojK31W6fH4M05LUfVQJr8jvUU_RsAAzMbq4Q/{server}/playlist.m3u8"
        else:
            match_url = match.group(0)

        # ৩. প্রক্সি হেডার্স দিয়ে ভিডিও ডাটা রিকোয়েস্ট করা (403 Forbidden বাইপাস করার জন্য)
        stream_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://footstreams.me/",
            "Origin": "https://footstreams.me"
        }

        stream_response = session.get(match_url, headers=stream_headers, timeout=10)
        
        if stream_response.status_code == 200:
            return Response(stream_response.text, mimetype='application/x-mpegURL')
        
        # ৪. যদি টোকেন এক্সপায়ার হয়ে ৪MD দেয়, তবে আমরা ডাইনামিকালি সেশন রিলোড রেসপন্স পাস করব
