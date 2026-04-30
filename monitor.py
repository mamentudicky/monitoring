from google import genai
import datetime
import requests
import subprocess

# 1. Konfigurasi Client Baru (Library: google-genai)
# Segera ganti API Key ini jika sudah Anda revoke/hapus
client = genai.Client(api_key="AIzaSyBrrzrf0937zB8Hy4MgAhm58PjOxTJsElQ")

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
    try:
        # 2. Syntax baru untuk memanggil Gemini 1.5 Flash
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=f"Analisa log SSH brute force ini secara singkat: {log_text}. Berikan saran keamanan dalam Bahasa Indonesia."
        )
        return response.text
    except Exception as e:
        return f"⚠️ Error Analisis: {str(e)}"

def send_whatsapp(message):
    token = "xAn512gx3d76L21YJwVp"
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