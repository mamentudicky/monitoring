from google import genai
import os
import datetime
import requests
import subprocess

# 1. Konfigurasi Client (Mengambil API Key dari Environment Variable)
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyD309N4StITb57jJAwpLdxG_qRll2ziqVU")

def get_ssh_attempts():
    try:
        # Mengambil 5 baris terakhir percobaan gagal
        result = subprocess.check_output(
            "grep 'Failed password' /var/log/auth.log | tail -n 5",
            shell=True
        )
        return result.decode()
    except Exception:
        return "Tidak ada percobaan login gagal terbaru."

def get_gemini_analysis(log_text):
    if not GEMINI_KEY:
        return "⚠️ Analisis dilewati: GEMINI_API_KEY tidak diatur."

    # Menggunakan v1beta untuk kompatibilitas model flash yang lebih luas
    client = genai.Client(
        api_key=GEMINI_KEY,
        http_options={'api_version': 'v1beta'}
    )
    
    # Mencoba model flash standar
    models_to_try = ["gemini-1.5-flash", "gemini-1.5-flash-latest"]
    
    last_error = ""
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=f"Analisa log SSH brute force ini secara singkat: {log_text}. Berikan saran keamanan dalam Bahasa Indonesia."
            )
            return response.text
        except Exception as e:
            last_error = str(e)
            if "404" in last_error:
                continue # Coba model lain
            if "429" in last_error:
                return "⚠️ Quota Terlampaui: Terlalu banyak permintaan ke Gemini. Silakan tunggu beberapa saat."
            return f"⚠️ Error ({model_name}): {last_error}"
            
    return f"⚠️ Analisis Gagal: {last_error}"

def send_whatsapp(message):
    # Mengambil token Fonnte dari environment variable
    token = os.environ.get("FONNTE_TOKEN", "xAn512gx3d76L21YJwVp") # Fallback ke token lama jika belum diatur
    payload = {
        "target": "081543330656",
        "message": message,
    }
    headers = {"Authorization": token}
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

print(full_message)
send_whatsapp(full_message)