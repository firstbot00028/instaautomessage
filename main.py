import os
import time
import requests
import urllib.parse
from threading import Thread
from flask import Flask
from instagrapi import Client

# 1. Flask App for UptimeRobot
app = Flask('')

@app.route('/')
def home():
    return "Aira AI is Online! Developed by Adam (Aira Group Technology) 🦾"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 2. Instagram Credentials (Direct Strings)
# ഇവിടെ os.getenv ഉപയോഗിക്കുന്നില്ല, അതുകൊണ്ട് എറർ വരില്ല!
USERNAME = 'x_hunder_y'
PASSWORD = 'Adamee@1234'

cl = Client()

def get_aira_response(user_message):
    try:
        system_prompt = (
            "Your name is Aira AI. You are a witty AI assistant developed by Adam, "
            "CEO of Aira Group Technology. Reply in Malayalam and English mix with savage attitude."
        )
        prompt = f"{system_prompt}\nUser: {user_message}"
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://text.pollinations.ai/{encoded_prompt}?model=openai"
        
        response = requests.get(url, timeout=15)
        return response.text.strip() if response.status_code == 200 else "Aira is busy! 😎"
    except:
        return "Adam-ine vilikko, ente system error aayi! 🦾"

def bot_logic():
    # 📡 നേരിട്ടുള്ള ലോഗിൻ
    try:
        print(f"📡 Aira AI logging in as {USERNAME}...")
        cl.login(USERNAME, PASSWORD)
        print("✅ Login Success! Aira AI is Live.")
    except Exception as e:
        print(f"❌ Login Failed: {e}")
        return

    while True:
        try:
            threads = cl.direct_threads()
            for thread in threads:
                last_msg = thread.messages[0]
                if last_msg.user_id != cl.user_id and not last_msg.is_sent_by_viewer:
                    reply = get_aira_response(last_msg.text)
                    cl.direct_answer(thread.id, reply)
                    print(f"📩 Msg: {last_msg.text} | 📤 Aira: {reply}")
            time.sleep(40)
        except Exception as e:
            print(f"⚠️ Warning: {e}")
            time.sleep(60)

if __name__ == "__main__":
    # Flask for UptimeRobot
    t = Thread(target=run_flask)
    t.start()
    
    # Start Bot
    bot_logic()
