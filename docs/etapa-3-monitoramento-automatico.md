# 🚨 Etapa 3: Monitoramento automático do site com Python e alertas via Discord

Nesta etapa, será criado um script em **Python** que monitorará a disponibilidade do site (HTTP). Se o site estiver fora do ar, um alerta será enviado para um canal do **Discord** via *webhook* e as ocorrências serão registradas em `/var/log/nginx-general.log`. Em seguida vamos agendar a execução com `cron` para rodar **a cada minuto**.

---

## ✅ 1 — Criar um Webhook no Discord

1. Acesse seu servidor no Discord.  
   <details>
   <summary><b>Servidor do Discord</b></summary>
   <img src="../assets/disc-server.png" width="900px" alt="Servidor do discord">
   <p><i>Figura — Servidor do Discord</i></p>
   </details>

2. Vá em **Configurações do servidor > Integrações > Webhooks**.  
3. Clique em **"Novo Webhook"**, escolha o canal e **Copiar URL do Webhook**.  
   <details>
   <summary><b>Novo Webhook no Discord</b></summary>
   <img src="../assets/disc-web-hook.png" width="900px" alt="WebHook no discord">
   <p><i>Figura — Criando o webhook</i></p>
   </details>
   
> [!NOTE]\
>Guarde a URL do webhook — você usará essa URL no `.env`.

---

## ✅ 2 — Preparar o ambiente e o script

### 2.1 Pré-requisitos (instalar pacotes do sistema)

No terminal da sua VM (Ubuntu):

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
```
> [!IMPORTANT]\
> `python3-venv` é necessário para criar ambientes virtuais.

---

### 2.2 Criar a pasta do projeto e ajustar permissões (recomendo usar o root)

```bash
mkdir -p /opt/monitor-site
cd /opt/monitor-site
```

> [!IMPORTANT]\
> Se a pasta for criada com um user do grupo `sudo`, o `owner` e `group` será o `root`, use `chown` para ficar com seu usuário antes de criar o `venv`, evitando `Permission denied`.
> ```bash
> sudo chown -R $USER:$USER /opt/monitor-site``

---

### 2.3 Criar e ativar o ambiente virtual (venv)

```bash
python3 -m venv venv
source venv/bin/activate   # você verá o prompt com (venv), que significa que você está no ambiente virtual python desta pasta
```

Instalar dependências dentro do `venv`:

```bash
pip install --upgrade pip
pip install python-dotenv requests # para usar .env
```

> [!NOTE]\
> Sempre use o `venv/bin/python` e o `venv/bin/pip` quando referenciar o interpretador do projeto (importante para o `cron`).

<details>
  <summary><b>Terminal do venv</b></summary>
  <img src="../assets/venv.png" width="900px" alt="Terminal do venv">
  <p><i>Figura — Ambiente virtual </i></p>
</details>

---

### 2.4 Criar o arquivo `.env`

Crie `/opt/monitor-site/.env`:

```bash
nano /opt/monitor-site/.env
```

Exemplo de conteúdo (substitua pelos seus valores):

```
SITE_URL=http://192.168.15.16
WEBHOOK_URL=https://discord.com/api/webhooks/SEU_WEBHOOK_AQUI
```

Interessante retirar algumas permissões do `.env`:

```bash
chmod 600 /opt/monitor-site/.env
```

---

### 2.5 Copiar / colar o `monitor_site.py` para a VM

Se você editou o script localmente na máquina ou pegou o script que deixei na pasta `\scripts`, copie para a VM:

```bash
scp \pasta usuario@IP_DA_VM:/tmp
```

<details>
  <summary><b>Exemplo SCP no terminal</b></summary>
  <img src="../assets/scp-script.png" width="700px" alt="Terminal scp script">
  <p><i>Figura — Copiando arquivo para a VM</i></p>
</details>

Mover o script para o diretório do projeto na VM:

```bash
mv /tmp/monitor_site.py /opt/monitor-site/monitor_site.pyy
```

<details>
  <summary><b>Movendo o script</b></summary>
  <img src="../assets/mv-script.png" width="900px" alt="Terminal mv do script">
  <p><i>Figura — Movendo script para /opt/monitor-site</i></p>
</details>

Edite o script com `nano` se precisar:

```bash
nano /opt/monitor-site/monitor_site.py
```

<details>
  <summary><b>Script em edição (exemplo)</b></summary>
  <img src="../assets/monitor-nano" width="900px" alt="Script em python para monitoramento">
  <p><i>Figura — Edição do script</i></p>
</details>

Torne executável:

```bash
chmod +x /opt/monitor-site/monitor.py
```

---

### 2.7 Criar o arquivo de log e ajustar permissões

```bash
cd /var/log
touch nginx-general.log
chmod 664 /var/log/nginx-general.log
```

---

### 2.8 Teste manual (dentro do venv)

Ative o venv e execute o script manualmente:

```bash
cd /opt/monitor-site
source venv/bin/activate
python monitor_site.py
# ou: /opt/monitor-site/venv/bin/python /opt/monitor-site/monitor_site.py
```

> [!IMPORTANT]\
> Para desativar o ambiente virtual use `deactivate`

Verifique o log:

```bash
cat /var/log/nginx-general.log
```

<details>
  <summary><b>Teste manual da venv</b></summary>
  <img src="../assets/test-log.png" width="700px" alt="Teste manual da venv">
  <p><i>Figura — Exemplo de teste manual com venv</i></p>
</details>

Se o site estiver caído, você verá entradas no log e receberá a notificação no Discord.

<details>
  <summary><b>Notificação de erro no Discord</b></summary>
  <img src="../assets/disc-error-msg.png" width="700px" alt="Notificação do discord">
  <p><i>Figura — Exemplo de mensagem de alerta no Discord</i></p>
</details>

---

## ✅ 3 — Agendar execução automática com `cron`

1. Abra o crontab:

```bash
crontab -e
```

2. Adicione a linha abaixo para executar **a cada minuto** usando o Python do `venv`:

```bash
* * * * * /opt/monitor-site/venv/bin/python /opt/monitor-site/monitor_site.py >> /var/log/nginx-general.log 2>&1
```

**Explicação rápida:**
- `* * * * *` → executa a cada 1 minuto.  
- Usa `/opt/monitor-site/venv/bin/python` para garantir as bibliotecas instaladas no `venv`.  
- Redireciona saída padrão e erros para o mesmo arquivo de log.

<details>
  <summary><b>Configuração do cron</b></summary>
  <img src="../assets/cron-job.png" width="700px" alt="Configuração do cron">
  <p><i>Figura — Cron configurado para rodar o script a cada minuto</i></p>
</details>

3. Salve e saia do editor (`Ctrl+O`, `Enter`, `Ctrl+X` no nano; `:wq` no vim).

---

## ✅ 4 — Verificações e troubleshooting rápido

- **`Invalid URL 'None'`** → veja se o `.env` está no caminho correto (`/opt/monitor-site/.env`) e contém `SITE_URL` com `http://` ou `https://`.
- **Erro de permissão ao gravar log** → verifique o owner/permissions de `/var/log/nginx-general.log`.
- **Cron não encontra requests/dotenv** → verifique se está usando o `venv` no `crontab` (veja linha acima).
- **Testar webhook manualmente**:
  ```bash
  curl -H "Content-Type: application/json" -X POST -d '{"content":"teste"}' https://discord.com/api/webhooks/SEU_WEBHOOK
  ```
- **Ver fuso horário (timestamp está adiantado)**: ajuste o timezone do servidor (afeta o `datetime.now().astimezone()`):
  ```bash
  sudo timedatectl set-timezone America/Sao_Paulo
  date
  ```
