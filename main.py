import os
import time
import requests
import urllib.parse
from instagrapi import Client

# Render Env Variables
USERNAME = os.getenv('x_hunder_y')
PASSWORD = os.getenv('Adamee@123')

cl = Client()
SESSION_FILE = "session.json"

def get_pollination_ai_response(user_message):
    """Pollinations.ai വഴി ഫ്രീയായി മറുപടി ഉണ്ടാക്കുന്നു"""
    try:
        system_prompt = "You are a witty, Thug-style AI from Kerala. Reply in a mix of Malayalam and English with massive attitude. Be short and savage."
        # മുകളിൽ പറഞ്ഞ പ്രോംപ്റ്റും യൂസർ മെസ്സേജും ചേർത്ത് URL ഉണ്ടാക്കുന്നു
        prompt = f"{system_prompt}\nUser: {user_message}"
        encoded_prompt = urllib.parse.quote(prompt)
        
        # Pollinations AI API (No Key Needed)
        url = f"https://text.pollinations.ai/{encoded_prompt}?model=openai&cache=false"
        
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            return response.text.strip()
        else:
            return "Server thട്ടിപ്പോയി മോനേ, കുറച്ച് കഴിഞ്ഞ് വാ! 😎"
    except Exception as e:
        print(f"AI Error: {e}")
        return "Ente buddhi ippo block aayi ഇരിക്കുവാ! 🦾"

def login_and_save():
    if os.path.exists(SESSION_FILE):
        try:
            cl.load_settings(SESSION_FILE)
            cl.login(USERNAME, PASSWORD)
            print("✅ Session Loaded from File!")
        except:
            print("⚠️ Session expired, logging in again...")
            cl.login(USERNAME, PASSWORD)
            cl.dump_settings(SESSION_FILE)
    else:
        cl.login(USERNAME, PASSWORD)
        cl.dump_settings(SESSION_FILE)
        print("✅ New Session Created and Saved!")

# Initial Login
login_and_save()

print("🚀 X_hunder_y AI is Online & Listening...")

while True:
    try:
        # പുതിയ മെസ്സേജുകൾക്കായി ചെക്ക് ചെയ്യുന്നു
        threads = cl.direct_threads()
        for thread in threads:
            # അവസാനത്തെ മെസ്സേജ് എടുക്കുന്നു
            last_msg = thread.messages[0]
            
            # മെസ്സേജ് വന്നിട്ട് 1 മിനിറ്റിൽ കൂടുതൽ ആയിട്ടില്ലെന്ന് ഉറപ്പാക്കാൻ (Optional)
            # കൂടാതെ മറുപടി അയച്ചത് നമ്മളല്ലെന്ന് ഉറപ്പാക്കുന്നു
            if last_msg.user_id != cl.user_id and not last_msg.is_sent_by_viewer:
                print(f"📩 New Message: {last_msg.text}")
                
                # AI Response എടുക്കുന്നു
                ai_reply = get_pollination_ai_response(last_msg.text)
                
                # മറുപടി അയക്കുന്നു
                cl.direct_answer(thread.id, ai_reply)
                print(f"📤 AI Response Sent: {ai_reply}")
                
        # ഇൻസ്റ്റാഗ്രാം ബ്ലോക്ക് ചെയ്യാതിരിക്കാൻ ചെറിയ ഇടവേള
        time.sleep(40) 
        
    except Exception as e:
        print(f"⚠️ Loop Error: {e}")
        time.sleep(60)
