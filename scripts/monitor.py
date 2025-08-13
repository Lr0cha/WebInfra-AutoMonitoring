import os
import requests
import datetime
import pytz
from dotenv import load_dotenv
import subprocess
import time

# Carregar variáveis do arquivo .env
load_dotenv(dotenv_path="/usr/local/bin/monitor-site/.env")

URL = os.getenv("SITE_URL")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
LOG_PATH = "/var/log/nginx-general.log"
        
def send_discord_alert(message):
    """Envia uma mensagem para o Discord usando o webhook."""
    payload = {"content": f"🚨 **[Alerta de Monitoramento]** 🚨\n{message}"}
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        response.raise_for_status()  # Verifica se a requisição foi bem-sucedida
    except requests.exceptions.RequestException as e:
        log(f"Erro ao enviar alerta para o Discord: {e}")
        
def restart_service():
     try:
        time.sleep(15)
        subprocess.run(["systemctl", "restart", "nginx"], check=True)
        send_discord_alert(f"✅ Serviço nginx do {URL} reiniciado automaticamente com sucesso no servidor!")
     except subprocess.CalledProcessError:
        send_discord_alert(f"⚠️ Falha ao reiniciar o serviço nginx no servidor {URL}.")

def log(message):
    """Registra mensagens no log com a hora de Brasília."""
    timezone = pytz.timezone('America/Sao_Paulo')
    now = datetime.datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a") as f:
        f.write(f"[{now}] {message}\n")

def check_site():
    """Verifica se o site está acessível e envia um alerta se não estiver."""
    if not URL or not WEBHOOK_URL:
        log("Erro: Variáveis de ambiente não definidas (check .env).")
        return

    try:
        response = requests.get(URL, timeout=10)
        if response.status_code == 200:
            log(f"Site {URL} está OK.")
        else:
            log(f"Site {URL} retornou o status code: {response.status_code}")
    except requests.exceptions.RequestException as e: # exception, caso fora de ar ...
        log(f"Erro ao acessar o site {URL}: {e}")
        send_discord_alert(f"❌ Não foi possível acessar o site {URL} (fora do ar). Tentando reiniciar automaticamente...")
        restart_service()
        
if __name__ == "__main__":
    check_site()

