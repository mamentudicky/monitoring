from google import genai
import datetime
import requests
import subprocess
import os
import sys

# ================= CONFIG =================
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
FONNTE_TOKEN = os.environ.get("FONNTE_TOKEN")
TARGET_PHONE = os.environ.get("TARGET_PHONE", "6281543330656")

client = genai.Client(api_key=GEMINI_KEY)

# ================= FUNCTION =================

def get_ssh_attempts():
    try:
        result = subprocess.check_output(
            "grep 'Failed password' /var/log/auth.log | tail -n 10",
            shell=True,
            stderr=subprocess.DEVNULL
        )
        return result.decode().strip() or "Tidak ada percobaan login."
    except Exception as e:
        return f"Error baca log: {e}"


def get_gemini_analysis(log_text):
    if not GEMINI_KEY:
        return "⚠️ GEMINI_API_KEY tidak diatur."

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"""
            Kamu adalah security analyst.

            Analisa log brute force SSH berikut secara singkat.
            Berikan maksimal 3 tindakan yang harus dilakukan.

            {log_text}
            """
        )

        return response.text.strip()

    except Exception as e:
        return f"⚠️ Error Gemini: {e}"


def send_whatsapp(message):
    if not FONNTE_TOKEN:
        return "⚠️ Token Fonnte tidak diatur."

    payload = {
        "target": TARGET_PHONE,
        "message": message,
    }

    headers = {"Authorization": FONNTE_TOKEN}

    try:
        r = requests.post(
            "https://api.fonnte.com/send",
            data=payload,
            headers=headers,
            timeout=10
        )
        return r.status_code
    except Exception as e:
        return f"Gagal kirim WA: {e}"


# ================= MAIN =================

def main():
    log = get_ssh_attempts()
    ai_response = get_gemini_analysis(log)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    message = (
        f"📅 {timestamp}\n"
        f"⚠️ *PERCOBAAN LOGIN DETECTED!*\n\n"
        f"```{log}```\n\n"
        f"🤖 *Gemini Analysis:*\n{ai_response}"
    )

    print(message)

    status = send_whatsapp(message)
    print(f"[WA STATUS] {status}")

    # ❗ Biar Jenkins fail kalau AI error
    if "⚠️" in ai_response:
        sys.exit(1)


if __name__ == "__main__":
    main()