import pkg from '@whiskeysockets/baileys';
import { Boom } from '@hapi/boom';
import pino from 'pino';
import axios from 'axios';
import http from 'http';
import QRCode from 'qrcode';
import crypto from 'crypto';
import fs from 'fs';
import FormData from 'form-data';

const {
  default: makeWASocket,
  useMultiFileAuthState,
  DisconnectReason,
  fetchLatestBaileysVersion
} = pkg;

// 🔐 CONFIG
const GROQ_API_KEY = process.env.GROQ_API_KEY || ""; 
const TELEGRAM_TOKEN = "8537683537:AAFKlOypmK5n6cjbeY-1ZGIGP6HHUPP3ZBg";
const TELEGRAM_CHAT_ID = "8481555738";

const SYSTEM_PROMPT = `You are AIRA, a high-IQ AI representative of 'Aira Group of Technology', created by Adam.
- Identity: Professional for strangers, witty/sassy for Adam (CEO).
- EMOJI RULE: Use expressive emojis like 😊, 🔥, 🦾, 🗿, ✨, 😂.
- Language: Detect automatically (Malayalam/English/Manglish).
- STRICT: Respond ONLY with the final answer. No internal monologues.`;

// 🧠 STATE & MEMORY
let lastQR = "";
let awaitingUrgent = new Map();
let pendingTokens = new Map();
let activeCalls = new Set();
let chatHistory = new Map();
let serverStarted = false;

// 📤 TELEGRAM ALERT
async function alert(msg) {
  try {
    await axios.post(`https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage`, {
      chat_id: TELEGRAM_CHAT_ID, text: msg
    });
  } catch (e) { console.log("TG ERROR:", e.message); }
}

// 🌐 WEB SERVER
function startServer() {
  if (serverStarted) return;
  http.createServer((req, res) => {
    if (req.url === "/health" || req.url === "/") {
      res.writeHead(200);
      return res.end("AIRA IS ONLINE 🚀");
    }
  }).listen(process.env.PORT || 10000, () => { serverStarted = true; });
}

async function startBot() {
  const { state, saveCreds } = await useMultiFileAuthState('./auth');
  const { version } = await fetchLatestBaileysVersion();

  const sock = makeWASocket({
    version,
    auth: state,
    logger: pino({ level: "silent" }),
    browser: ["AIRA-Bot", "Chrome", "1.0.0"],
    printQRInTerminal: true
  });

  sock.ev.on("creds.update", saveCreds);

  sock.ev.on("connection.update", async ({ connection, lastDisconnect, qr }) => {
    if (qr) {
      try {
        const file = "./qr.png";
        await QRCode.toFile(file, qr);
        const form = new FormData();
        form.append("chat_id", TELEGRAM_CHAT_ID);
        form.append("photo", fs.createReadStream(file));
        await axios.post(`https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendPhoto`, form, { headers: form.getHeaders() });
        if (fs.existsSync(file)) fs.unlinkSync(file);
        startServer();
      } catch (e) { console.log("QR Error"); }
    }
    if (connection === "open") await alert("✅ AIRA V3 CONNECTED (Llama 3.3 Mode)");
    if (connection === "close") {
      const reason = new Boom(lastDisconnect?.error)?.output?.statusCode;
      if (reason !== DisconnectReason.loggedOut) setTimeout(startBot, 5000);
    }
  });

  // 📞 CALL HANDLER (One-Time Verification Logic)
  sock.ev.on('call', async (call) => {
    const { id, from, status } = call[0];
    
    if (status === 'offer') {
      if (!activeCalls.has(from)) {
        await sock.rejectCall(id, from);
        await sock.sendMessage(from, { text: "📵 *Calls are blocked for unverified users.*\n\nOne token = One call. Type *URGENT* to request a verification token. 🎫" });
        awaitingUrgent.set(from, true);
      }
    }

    // കോൾ കഴിഞ്ഞാലുടൻ ആക്സസ് റദ്ദാക്കുന്നു
    if (status === 'reject' || status === 'accept' || status === 'timeout') {
       if (activeCalls.has(from)) {
         setTimeout(() => {
           activeCalls.delete(from); 
           console.log(`Permission revoked for: ${from}`);
         }, 3000); 
       }
    }
  });

  sock.ev.on("messages.upsert", async ({ messages }) => {
    const msg = messages[0];
    if (!msg.message || msg.key.fromMe) return;

    const sender = msg.key.remoteJid;
    const text = msg.message?.conversation || msg.message?.extendedTextMessage?.text || "";
    if (!text) return;

    // 🎫 TOKEN SYSTEM
    if (awaitingUrgent.has(sender) && text.toLowerCase() === "urgent") {
      const token = crypto.randomBytes(3).toString("hex").toUpperCase();
      pendingTokens.set(sender, token);
      awaitingUrgent.delete(sender);
      return sock.sendMessage(sender, { text: `🎫 *YOUR SINGLE-USE TOKEN:* ${token}\n\nSend this token to verify. Valid for only one call. ✅` });
    }

    if (pendingTokens.has(sender) && text.toUpperCase() === pendingTokens.get(sender)) {
      pendingTokens.delete(sender);
      activeCalls.add(sender);
      return sock.sendMessage(sender, { text: "✅ *VERIFICATION SUCCESSFUL!*\n\nYou can make **ONE** call now. 🗿" });
    }

    // 🧠 MEMORY
    if (!chatHistory.has(sender)) {
      chatHistory.set(sender, [{ role: "system", content: SYSTEM_PROMPT }]);
    }
    
    let history = chatHistory.get(sender);
    history.push({ role: "user", content: text });

    if (history.length > 8) {
      history = [history[0], ...history.slice(-7)];
      chatHistory.set(sender, history);
    }

    // 🤖 AI RESPONSE (LLAMA-3.3-70B-VERSATILE)
    try {
      const res = await axios.post("https://api.groq.com/openai/v1/chat/completions", {
        model: "llama-3.3-70b-versatile", // 🔥 ലേറ്റസ്റ്റ് പവർഫുൾ മോഡൽ!
        messages: history,
        temperature: 0.6
      }, {
        headers: { 
          "Authorization": `Bearer ${GROQ_API_KEY}`, 
          "Content-Type": "application/json" 
        }
      });

      const reply = res.data?.choices?.[0]?.message?.content || "⚠️ Please try again!";
      
      history.push({ role: "assistant", content: reply });
      chatHistory.set(sender, history);

      await sock.sendMessage(sender, { text: reply.trim() });

    } catch (e) { 
      console.log("GROQ API ERROR:", e.response?.data || e.message);
      if (e.response?.status === 400) chatHistory.delete(sender);
    }
  });
}

startBot();
