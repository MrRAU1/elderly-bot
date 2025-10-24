from flask import Flask, request, jsonify, send_file, render_template
from gtts import gTTS
import hashlib
import os

app = Flask(__name__)
AUDIO_CACHE_DIR = "audio_cache"

if not os.path.exists(AUDIO_CACHE_DIR):
    os.makedirs(AUDIO_CACHE_DIR)

responses = {
    "english": {
        "good morning": "Good morning! Did you sleep well? Let’s make today a great day!",
        "i need someone to talk to": "Tell me about anything. No matter how big or small, I’m all ears.",
        "i feel lonely": "I’m right here. How about a nice song, or maybe you want to vent out to me?",
        "i feel sad": "I am here. You can talk to me anytime.",
        "i'm bored": "It is a great time for your favourite hobby. Or, let us look at some old photos.",
        "music": "I can play your favourite song. Or would you like to sing along?",
        "sing": "Let us sing together. Music always makes us happy.",
        "time check": "It is 10:30 AM. We could have a tea break or go out for a walk.",
        "ouch": "Alert. Did you fall? I am calling an ambulance. Please stay still.",
        "what do i need to do at 2pm": "Reminder. It is pill time. Please confirm you have taken your medication.",
        "i feel dizzy": "Please sit down immediately. I am monitoring your status.",
        "unusual smell": "Emergency. High level fumes detected. Move to a window. Calling for help.",
        "i need help": "I am ready. Do you need help finding something?",
        "where is my": "Where did you last see it?",
        "cleaning time": "I will assist with floor tidiness. You can relax.",
        "goodnight": "Time for bed. I will patrol the house to ensure doors are locked. Sleep tight.",
        "pill time": "You need to take medication at 10am, 4pm and 8pm daily.",
        "morning medicines": "Good morning. Your morning tablets are on the counter.",
        "evening medicines": "It is late. Remember your evening dose.",
        "did i take it": "Yes. You took your medication at 10am today."
    },
    "mandarin": {
        "早上好": "早上好! 你睡得好吗? 让我们一起度过美好的一天吧!",
        "我需要有人说话": "告诉我任何事吧. 无论大小, 我都在听.",
        "我感到孤独": "我就在这儿. 你可以向我倾诉.",
        "我感到悲伤": "我在这里陪你. 一起听一首歌好吗?",
        "我无聊": "适合进行你的爱好. 或者我们看看旧照片吧.",
        "音乐": "我可以播放你喜欢的歌曲.",
        "唱歌": "想和我一起唱吗?",
        "哎哟": "警报: 你摔倒了吗? 我正在叫救护车.",
        "异常气味": "紧急! 高浓度气体! 靠近窗户. 我正在呼叫帮助.",
        "晚安": "睡觉时间到了. 晚安!"
    },
    "malay": {
        "selamat pagi": "Selamat pagi. Anda tidur lena? Mari jadikan hari ini hebat!",
        "saya rasa sunyi": "Saya ada di sini. Mahu saya mainkan lagu?",
        "saya rasa sedih": "Saya ada untuk anda. Cuba beritahu saya apa yang berlaku.",
        "saya bosan": "Masa yang bagus untuk hobi kegemaran anda.",
        "muzik": "Saya boleh memainkan lagu kegemaran anda.",
        "menyanyi": "Mahu menyanyi bersama saya?",
        "aduh": "Amaran. Anda jatuh? Saya hubungi ambulans.",
        "selamat malam": "Masa untuk tidur. Tidur nyenyak."
    },
    "hindi": {
        "शुभ प्रभात": "शुभ प्रभात. आइए आज का दिन शानदार बनाते हैं.",
        "मुझे किसी से बात करनी है": "मुझे कुछ भी बताएं. मैं सुन रहा हूँ.",
        "मैं दुखी महसूस कर रहा हूँ": "मैं यहीं हूँ. आप मुझसे बात कर सकते हैं.",
        "मैं ऊब गया हूँ": "यह आपके शौक का अच्छा समय है.",
        "संगीत": "मैं आपका पसंदीदा गाना बजा सकता हूँ.",
        "गाना": "क्या आप मेरे साथ गाना चाहेंगे?",
        "आउच": "अलर्ट. क्या आप गिर गए? मैं एंबुलेंस को कॉल कर रहा हूँ.",
        "शुभरात्रि": "सोने का समय. अच्छे से सोएं."
    }
}

# Pre-generate all audio files at startup
for lang, phrases in responses.items():
    for phrase_text, response_text in phrases.items():
        key = f"{lang}:{response_text}"
        filename = hashlib.md5(key.encode()).hexdigest() + ".mp3"
        filepath = os.path.join(AUDIO_CACHE_DIR, filename)
        if not os.path.exists(filepath):
            tts = gTTS(text=response_text, lang={"english":"en","mandarin":"zh-CN","malay":"ms","hindi":"hi"}[lang])
            tts.save(filepath)


def get_audio(text, lang):
    key = f"{lang}:{text}"
    filename = hashlib.md5(key.encode()).hexdigest() + ".mp3"
    filepath = os.path.join(AUDIO_CACHE_DIR, filename)

    if not os.path.exists(filepath):
        tts = gTTS(text=text, lang={"english":"en","mandarin":"zh-CN","malay":"ms","hindi":"hi"}[lang])
        tts.save(filepath)

    return filepath

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/process_text", methods=["POST"])
def process_text():
    data = request.json
    lang = data.get("language")
    user_text = data.get("text").lower()

    best_match = None
    for phrase in responses.get(lang, {}):
        if phrase in user_text:
            best_match = phrase
            break

    if best_match:
        final_text = responses[lang][best_match]
        audio_path = get_audio(final_text, lang)
        return jsonify({"response": final_text, "audio_url": f"/audio/{os.path.basename(audio_path)}"})
    return jsonify({"response": None, "audio_url": None})

@app.route("/audio/<filename>")
def get_audio_file(filename):
    return send_file(os.path.join(AUDIO_CACHE_DIR, filename))



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

