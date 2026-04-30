from google import genai
import os
import datetime
import requests
import subprocess

# 1. Konfigurasi Client (Mengambil API Key dari Environment Variable)
# Pastikan GEMINI_API_KEY sudah diset di Jenkins Environment
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyD309N4StITb57jJAwpLdxG_qRll2ziqVU")
FONNTE_TOKEN = os.environ.get("FONNTE_TOKEN", "xAn512gx3d76L21YJwVp")

client = genai.Client(api_key=GEMINI_KEY)

def get_ssh_attempts():
    try:
        # Mengambil 10 baris terakhir percobaan gagal
        result = subprocess.check_output(
            "grep 'Failed password' /var/log/auth.log | tail -n 10",
            shell=True
        )
        return result.decode()
    except Exception:
        return "Tidak ada percobaan login gagal terbaru."

def get_gemini_analysis(log_text):
    if not GEMINI_KEY:
        return "⚠️ Analisis dilewati: GEMINI_API_KEY tidak diatur di Environment Jenkins."

    try:
        # Menggunakan model flash standar
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=f"Ada percobaan login brute force pada server saya:\n{log_text}\n\nApa yang sebaiknya saya lakukan? Berikan analisa singkat dan saran keamanan dalam Bahasa Indonesia."
        )
        return response.text
    except Exception as e:
        err_msg = str(e)
        if "429" in err_msg:
            return "⚠️ Quota Terlampaui: Terlalu banyak permintaan ke Gemini. Silakan tunggu 1 menit."
        if "403" in err_msg:
            return "⚠️ Izin Ditolak: API Key tidak valid atau telah diblokir karena bocor."
        return f"⚠️ Gagal Analisis: {err_msg}"

def send_whatsapp(message):
    payload = {
        "target": "6281543330656",
        "message": message,
    }
    headers = {"Authorization": FONNTE_TOKEN}
    try:
        r = requests.post("https://api.fonnte.com/send", data=payload, headers=headers)
        return r.status_code
    except Exception:
        return "Gagal kirim WA"

# --- Eksekusi Utama ---
log_data = get_ssh_attempts()
ai_result = get_gemini_analysis(log_data)

timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
full_message = (
    f"📅 {timestamp}\n"
    f"⚠️ *PERCOBAAN LOGIN DETECTED!*\n\n"
    f"```{log_data}```\n\n"
    f"🤖 *Gemini Analysis:*\n{ai_result}\n\n"
    f"> _Sent via Jenkins Monitor_"
)

# Tampilkan di Console Jenkins
print(full_message)

# Kirim ke WhatsApp
send_whatsapp(full_message)