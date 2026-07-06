from flask import Flask, redirect, request

app = Flask(__name__)

@app.route('/')
def home():
    return "BDIX IPTV Permanent Server is Running!"

@app.route('/stream')
def get_stream():
    # প্লেলিস্ট থেকে আসা সার্ভার নম্বর (যেমন: 1, 2, 3)
    server = request.args.get('server', '1')
    
    # প্রথম স্ক্রিনশট থেকে নেওয়া আজকের ম্যাচের আসল ডিরেক্ট সিকিউর টোকেন পাথ
    # ক্লাউডফ্লেয়ার বাইপাস করার জন্য আমরা সরাসরি এই ডাইনামিক লিংকে রিডাইরেক্ট করে দেব
    secure_token_path = "QAUWckhqUnlkNqygcdGCcGOPskuUcSju/rtmp/stream/Kdmp7byfeWY4hCRPQUJzS779TXojAc1upP_kMojK31W6fH4M05LUfVQJr8jvUU_RsAAzMbq4Q"
    
    # ডাইনামিক m3u8 লিংক তৈরি (এখানে সার্ভার নম্বরটি অটো বসে যাবে)
    direct_m3u8_url = f"https://lb8.strmd.st/secure/{secure_token_path}/{server}/playlist.m3u8"
    
    # সরাসরি প্লেয়ারকে m3u8 লিংকটি ফরওয়ার্ড করে দেওয়া
    return redirect(direct_m3u8_url, code=302)
