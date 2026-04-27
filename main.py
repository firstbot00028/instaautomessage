import os
import time
import requests
import urllib.parse
from threading import Thread
from flask import Flask
from instagrapi import Client

# 1. Flask App for UptimeRobot (Keep-Alive System)
app = Flask('')

@app.route('/')
def home():
    return "Aira AI is Online! Developed by Adam (Aira Group Technology) 🦾"

def run_flask():
    # Render-ൽ പോർട്ട് ഓട്ടോമാറ്റിക് ആയി എടുക്കും
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 2. Instagram Credentials (Direct Input as requested)
USERNAME = 'x_hunder_y'
PASSWORD = 'Adamee@123'

cl = Client()

def get_aira_response(user_message):
    """Pollinations.ai വഴി Aira AI മറുപടി നൽകുന്നു"""
    try:
        # 🤖 നിന്റെ കമ്പനിയുടെയും നിന്റെയും പേര് ഉൾപ്പെടുത്തിയ പ്രോംപ്റ്റ്
        system_prompt = (
            "Your name is Aira AI. You are a highly intelligent and witty AI assistant. "
            "You were developed by Adam, the CEO of Aira Group Technology. "
            "Reply in a mix of Malayalam and English with a 'Thug' attitude and savage humor. "
            "Keep your identity consistent: Developer is Adam, Company is Aira Group Technology."
        )
        
        full_prompt = f"{system_prompt}\nUser: {user_message}"
        encoded_prompt = urllib.parse.quote(full_prompt)
        
        # Pollinations AI API (Free)
        url = f"https://text.pollinations.ai/{encoded_prompt}?model=openai&cache=false"
        
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            return response.text.strip()
        else:
            return "Aira AI is taking a nap. Catch me later! 😎"
    except Exception as e:
        print(f"AI Error: {e}")
        return "Ente memory-il entho error vannu, Adam-ine vilിക്കൂ! 🦾"

def bot_logic():
    """Instagram Automation Loop"""
    try:
        print(f"📡 Aira AI is connecting to Instagram for {USERNAME}...")
        cl.login(USERNAME, PASSWORD)
        print("✅ Aira AI is now Live and Active!")
    except Exception as e:
        print(f"❌ Login Failed: {e}")
        return

    while True:
        try:
            # പുതിയ മെസ്സേജുകൾ റീഡ് ചെയ്യുന്നു
            threads = cl.direct_threads()
            for thread in threads:
                last_msg = thread.messages[0]
                
                # മറുപടി അയച്ചത് നമ്മളല്ലെങ്കിൽ മാത്രം പ്രതികരിക്കുക
                if last_msg.user_id != cl.user_id and not last_msg.is_sent_by_viewer:
                    print(f"📩 New Message from {last_msg.user_id}: {last_msg.text}")
                    
                    # Aira AI Response
                    reply = get_aira_response(last_msg.text)
                    
                    # Direct Message Reply
                    cl.direct_answer(thread.id, reply)
                    print(f"📤 Aira AI Replied: {reply}")
                    
            # ഇൻസ്റ്റാഗ്രാം ബ്ലോക്ക് ഒഴിവാക്കാൻ 30-40 സെക്കന്റ് ഗ്യാപ്പ്
            time.sleep(30)
            
        except Exception as e:
            print(f"⚠️ Loop Warning: {e}")
            time.sleep(60)

# 3. Execution Start
if __name__ == "__main__":
    # വെബ് സെർവർ സ്റ്റാർട്ട് ചെയ്യുന്നു (UptimeRobot-ന് വേണ്ടി)
    t = Thread(target=run_flask)
    t.start()
    
    # ഇൻസ്റ്റാഗ്രാം ബോട്ട് ലോജിക് സ്റ്റാർട്ട് ചെയ്യുന്നു
    bot_logic()
