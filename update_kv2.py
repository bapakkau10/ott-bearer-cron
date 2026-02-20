import os
import subprocess
import requests
import time
from datetime import datetime

# ================= CONFIG =================

CHANNELS = {
    "makkah_live": "https://www.youtube.com/watch?v=VIg8bJxRyNw",
    "madinah_live": "https://www.youtube.com/watch?v=XerknsSudwk",
    "uai_live": "https://www.youtube.com/watch?v=cqi_8ERTqh4",
    "poker_live": "https://www.youtube.com/watch?v=yJ98FfwdEPA",
    "warner_live": "https://www.youtube.com/watch?v=G43NInZfoPE",
    "hp_live": "https://www.youtube.com/watch?v=bZwI3A3gUgk",
    "nat_live": "https://www.youtube.com/watch?v=FqQJmDiW0xs",
    "laugh_live": "https://www.youtube.com/watch?v=4ebPiyrtmJo",
    "mc_live": "https://www.youtube.com/watch?v=rdhvZYmVVGs",
}

CF_ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID")
CF_NAMESPACE_ID = os.getenv("CF_NAMESPACE_ID")
CF_API_TOKEN = os.getenv("CF_API_TOKEN")

LOG_FILE = "update_log.txt"

# ===========================================


def log(message):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    line = f"[{timestamp}] {message}"
    print(line)

    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass


def validate_env():
    if not CF_ACCOUNT_ID or not CF_NAMESPACE_ID or not CF_API_TOKEN:
        log("❌ Missing Cloudflare environment variables.")
        exit(1)


def get_manifest(url, retries=3):
    for attempt in range(retries):
        try:
            result = subprocess.check_output(
                ["python", "-m", "yt_dlp", "--print", "manifest_url", url],
                text=True,
                stderr=subprocess.DEVNULL
            ).strip()

            if result:
                return result

        except Exception as e:
            log(f"Extraction attempt {attempt+1} failed: {e}")
            time.sleep(3)

    return None


def get_current_value(key):
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/storage/kv/namespaces/{CF_NAMESPACE_ID}/values/{key}"

    headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)

        if response.status_code == 200:
            return response.text
        elif response.status_code == 404:
            return None
        else:
            log(f"{key} GET failed: {response.text}")
            return None

    except Exception as e:
        log(f"{key} GET exception: {e}")
        return None


def update_kv(key, manifest_url):
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/storage/kv/namespaces/{CF_NAMESPACE_ID}/values/{key}"

    headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}",
        "Content-Type": "text/plain"
    }

    try:
        response = requests.put(url, headers=headers, data=manifest_url, timeout=15)

        if response.status_code == 200:
            log(f"✅ {key} updated successfully.")
        else:
            log(f"❌ {key} update failed: {response.text}")

    except Exception as e:
        log(f"❌ {key} PUT exception: {e}")


# ================= MAIN ====================

if __name__ == "__main__":

    log("===== START UPDATE CYCLE =====")

    validate_env()

    for key, youtube_url in CHANNELS.items():
        log(f"Checking {key}...")

        manifest = get_manifest(youtube_url)

        if not manifest:
            log(f"❌ {key} FAILED extraction.")
            continue

        current_value = get_current_value(key)

        if current_value == manifest:
            log(f"{key} unchanged. Skipping write.")
        else:
            update_kv(key, manifest)

    log("===== END UPDATE CYCLE =====\n")