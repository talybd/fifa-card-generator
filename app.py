import re
import requests
from flask import Flask, request, Response

app = Flask(__name__)

@app.route('/')
def home():
    return "BDIX IPTV Automated Server is Running!"

@app.route('/stream')
def get_stream():
    match_id = request.args.get('match', 'portugal-vs-spain-2511721')
    server = request.args.get('server', '1')

    # ১. সাইটের আসল ইউআরএল স্ট্রাকচার
    target_url = f"https://footstreams.me/watch/{match_id}-admin-{server}"

    # ক্লাউডফ্লেয়ার এবং বোট ডিটেকশন এড়ানোর জন্য শক্তিশালী ব্রাউজার হেডার্স
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Referer": "https://footstreams.me/",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive"
    }

    try:
        session = requests.Session()
        # পেজের সোর্স কোড রিকোয়েস্ট করা
        html_content = session.get(target_url, headers=headers, timeout=10).text

        # ২. ডাইনামিক রেগুলার এক্সপ্রেশন: এটি ডোমেইন (lb8 বা অন্য কিছু) এবং যেকোনো লাইভ টোকেন অটোমেটিক খুঁজে নেবে
        # সাইট টোকেন পরিবর্তন করলেও এই কোড তা লাইভ ধরে ফেলবে
        match = re.search(r'https://[a-zA-Z0-9\.]+\.strmd\.st/secure/[^\s"\']+playlist\.m3u8', html_content)
        
        # ব্যাকআপ ম্যাচ লজিক (যদি সোর্সের ভেতর আংশিক পাথ থাকে)
        if not match:
            path_match = re.search(r'/rtmp/stream/[^\s"\']+/playlist\.m3u8', html_content)
            dom_match = re.search(r'https://[a-zA-Z0-9\.]+\.strmd\.st', html_content)
            
            if path_match:
                base_domain = dom_match.group(0) if dom_match else "https://lb8.strmd.st"
                # এখানে 'QAUWckhqUnlkNqygcdGCcGOPskuUcSju' হচ্ছে মূল প্লেয়ার আইডি যা সাধারণত ফিক্সড থাকে
                match_url = f"{base_domain}/secure/QAUWckhqUnlkNqygcdGCcGOPskuUcSju{path_match.group(0)}"
            else:
                return "Cloudflare Blocked Python Request. Please refresh or try again.", 403
        else:
            match_url = match.group(0)

        # ৩. প্রক্সি হিসেবে ৪MD Forbidden বাইপাস করে ভিডিও ডাটা প্লেয়ারে পাঠানো
        stream_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://footstreams.me/",
            "Origin": "https://footstreams.me"
        }

        stream_response = session.get(match_url, headers=stream_headers, timeout=10)
        
        if stream_response.status_code == 200:
            return Response(stream_response.text, mimetype='application/x-mpegURL')
        else:
            return f"Media Server Error: {stream_response.status_code}. Token expired or IP blocked.", stream_response.status_code

    except Exception as e:
        return f"Server Error: {str(e)}", 500
