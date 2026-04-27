import os
import time
import requests
import urllib.parse
from threading import Thread
from flask import Flask
from instagrapi import Client

# 1. Flask App (Keep-Alive)
app = Flask('')

@app.route('/')
def home():
    return "Aira AI (Aira Group Technology) is Online! Developed by Adam 🦾"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 2. Login Details (നേരിട്ട് Gmail കൊടുക്കാം)
USERNAME = 'adameehan34gmail.com' # ഇവിടെ നിന്റെ ജിമെയിൽ ഇടുക
PASSWORD = 'Adamee@12345'

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
        return "Adam-ine vilikko, system error aayi! 🦾"

def bot_logic():
    try:
        print(f"📡 Aira AI logging in as {USERNAME}...")
        
        # ⚠️ Verification വന്നാൽ അത് ഹാൻഡിൽ ചെയ്യാനുള്ള സെറ്റപ്പ്
        cl.login(USERNAME, PASSWORD)
        print("✅ Login Success! Aira AI is Live.")
        
    except Exception as e:
        # ഇവിടെയാണ് കളി! വെരിഫിക്കേഷൻ ചോദിച്ചാൽ ലോഗ്സിൽ അത് കാണിക്കും.
        print(f"❌ Login Error: {e}")
        if "Challenge" in str(e):
            print("⚠️ ഇൻസ്റ്റാഗ്രാം വെരിഫിക്കേഷൻ ചോദിക്കുന്നുണ്ട്! നിന്റെ മെയിൽ നോക്ക്.")
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
            time.sleep(45) # അല്പം ഗ്യാപ്പ് ഇടുന്നത് നല്ലതാ, അല്ലെങ്കിൽ ബ്ലോക്ക് കിട്ടും.
        except Exception as e:
            print(f"⚠️ Loop Warning: {e}")
            time.sleep(60)

if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.start()
    bot_logic()
