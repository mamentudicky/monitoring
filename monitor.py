from google import genai # Menggunakan library baru
import datetime
import requests
import subprocess
import os

# 1. Konfigurasi Client Gemini Baru
# Sebaiknya simpan di environment variable, tapi jika ingin hardcode:
client = genai.Client(api_key="AIzaSyBrrzrf0937zB8Hy4MgAhm58PjOxTJsElQ")

def get_ssh_attempts():
    try:
        # Menambahkan pengecekan jika file log ada
        result = subprocess.check_output(
            "grep 'Failed password' /var/log/auth.log | tail -n 5",
            shell=True
        )
        return result.decode()
    except subprocess.CalledProcessError:
        return "Tidak ada percobaan login gagal yang ditemukan."

def get_gemini_analysis(log_text):
    try:
        # 2. Cara panggil model yang benar pada library baru
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=f"Ada percobaan login brute force:\n{log_text}\nApa yang sebaiknya saya lakukan? Respon dalam Bahasa Indonesia, singkat dan padat."
        )
        return response.text
    except Exception as e:
        # Ini akan membantu Anda melihat detail error jika terjadi lagi
        return f"⚠️ Gagal mendapatkan analisis dari Gemini: {str(e)}"

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
    except Exception as e:
        print(f"Error sending WhatsApp: {e}")
        return None

# Eksekusi
log_content = get_ssh_attempts()
ai_analysis = get_gemini_analysis(log_content)

full_message = (
    f"📅 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    f"⚠️ *PERCOBAAN LOGIN DETECTED!*\n\n"
    f"```{log_content}```\n\n"
    f"🤖 *Gemini Analysis:*\n{ai_analysis}\n\n"
    f"> _Sent via Automonitoring Jenkins_"
)

status = send_whatsapp(full_message)
print(f"Status kirim WA: {status}")