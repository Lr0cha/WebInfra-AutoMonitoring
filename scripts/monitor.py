import os
import requests
import datetime
from dotenv import load_dotenv

load_dotenv(dotenv_path="/opt/monitor-site/.env")

URL = os.getenv("SITE_URL")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
LOG_PATH = "/var/log/nginx-general.log"

def send_discord_alert(message):
    payload = {"content": f"🚨 **[Alerta de Monitoramento]** 🚨\n{message}"}
    try:
        requests.post(WEBHOOK_URL, json=payload)
    except Exception as e:
        log(f"Erro ao enviar alerta: {e}")

def log(message):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a") as f:
        f.write(f"[{now}] {message}\n")

def check_site():
    if not URL or not WEBHOOK_URL:
        log("Variáveis de ambiente não definidas (check .env).")
        return
    try:
        response = requests.get(URL, timeout=10)
        if response.status_code == 200:
            log("✅ Site OK.")
    except Exception as e:
        log(f"❌ Site inacessível: {str(e)}")
        send_discord_alert(f"❌ Não foi possível acessar o site `{URL}`.

if __name__ == "__main__":
    check_site()

