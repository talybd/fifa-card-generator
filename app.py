import re
import requests
from flask import Flask, request, Response

app = Flask(__name__)

@app.route('/')
def home():
    return "BDIX IPTV Permanent Proxy Server is Running!"

@app.route('/stream')
def get_stream():
    match_id = request.args.get('match', 'portugal-vs-spain-2511721')
    server = request.args.get('server', '1')

    # ১. সঠিক ম্যাচ এবং সার্ভার অনুযায়ী সাইটের ইউআরএল তৈরি
    target_url = f"https://footstreams.me/watch/{match_id}-admin-{server}"

    # ক্লাউডফ্লেয়ার ও বোট প্রোটেকশন বাইপাস করার জন্য স্ট্যান্ডার্ড ব্রাউজার হেডার
    site_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Referer": "https://footstreams.me/",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
    }

    try:
        session = requests.Session()
        html_content = session.get(target_url, headers=site_headers, timeout=10).text

        # ২. ডাইনামিকালি একদম তাজা .m3u8 এবং সিকিউর টোকেন খুঁজে বের করা (যা কখনো ম্যানুয়ালি বদলাতে হবে না)
        match = re.search(r'https://[a-zA-Z0-9\.]+\.strmd\.st/secure/[^\s"\']+playlist\.m3u8', html_content)
        
        if not match:
            # যদি সরাসরি না পায়, তবে ভেতরের আংশিক পাথ খোঁজার চেষ্টা করবে
            path_match = re.search(r'/rtmp/stream/[^\s"\']+/playlist\.m3u8', html_content)
            if path_match:
                match_url = f"https://lb8.strmd.st/secure/QAUWckhqUnlkNqygcdGCcGOPskuUcSju{path_match.group(0)}"
            else:
                return "Stream Not Found on Source Page. Match might be over.", 404
        else:
            match_url = match.group(0)

        # ৩. গুরুত্বপূর্ণ অংশ: 403 Forbidden বাইপাস করার জন্য সঠিক হেডার দিয়ে m3u8 রিকোয়েস্ট করা
        stream_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": f"https://footstreams.me/",
            "Origin": "https://footstreams.me"
        }

        stream_response = session.get(match_url, headers=stream_headers, timeout=10)
        
        if stream_response.status_code == 200:
            # সরাসরি রিডাইরেক্ট না করে ডাটাটি প্লেয়ারে পাস করা, যাতে প্লেয়ার ৪MD বা 403 না পায়
            return Response(stream_response.text, mimetype='application/x-mpegURL')
        else:
            return f"Media Server responded with status: {stream_response.status_code}", stream_response.status_code

    except Exception as e:
        return f"Server Error: {str(e)}", 500
