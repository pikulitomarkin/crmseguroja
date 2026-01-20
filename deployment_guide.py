"""
Guia de Deployment para Produção
"""

DEPLOYMENT_GUIDE = """
# 🚀 GUIA DE DEPLOYMENT - CRM WHATSAPP SYSTEM

## 1. OPÇÃO A: Deployment em Servidor Linux (Recomendado)

### 1.1 Preparar o Servidor

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python 3.10+
sudo apt install python3.10 python3.10-venv python3-pip -y

# Instalar dependências do sistema
sudo apt install postgresql postgresql-contrib nginx supervisor git -y
```

### 1.2 Configurar PostgreSQL

```bash
# Criar usuário e banco de dados
sudo sudo -u postgres psql
CREATE USER crm_user WITH PASSWORD 'sua_senha_forte';
CREATE DATABASE crm_db OWNER crm_user;
GRANT ALL PRIVILEGES ON DATABASE crm_db TO crm_user;
\\q
```

### 1.3 Clonar Projeto

```bash
cd /var/www
git clone https://seu-repo.git crm-whatsapp
cd crm-whatsapp

# Criar ambiente virtual
python3.10 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 1.4 Configurar Variáveis de Ambiente

```bash
# Criar arquivo .env
nano .env
```

Adicione:
```
ANTHROPIC_API_KEY=sk-ant-xxxxx
EVOLUTION_API_URL=https://api.evolution.br/api
EVOLUTION_API_KEY=sua_chave
EVOLUTION_INSTANCE_NAME=sua_instancia

ADMIN_WHATSAPP=5511999999999
ADMIN_EMAIL=admin@seudominio.com

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu_email@gmail.com
SMTP_PASSWORD=sua_senha_app

DATABASE_URL=postgresql://crm_user:sua_senha_forte@localhost/crm_db

API_HOST=0.0.0.0
API_PORT=8000
```

### 1.5 Configurar Supervisor (para gerenciar processos)

```bash
# Criar arquivo de configuração para webhook
sudo nano /etc/supervisor/conf.d/crm-webhook.conf
```

Conteúdo:
```ini
[program:crm-webhook]
directory=/var/www/crm-whatsapp
command=/var/www/crm-whatsapp/venv/bin/python -m uvicorn app.webhooks.evolution_webhook:app --host 0.0.0.0 --port 8000
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/crm-webhook.err.log
stdout_logfile=/var/log/crm-webhook.out.log
```

```bash
# Criar arquivo de configuração para dashboard
sudo nano /etc/supervisor/conf.d/crm-dashboard.conf
```

Conteúdo:
```ini
[program:crm-dashboard]
directory=/var/www/crm-whatsapp
command=/var/www/crm-whatsapp/venv/bin/streamlit run dashboard/app.py --server.port=8501
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/crm-dashboard.err.log
stdout_logfile=/var/log/crm-dashboard.out.log
```

```bash
# Iniciar supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start crm-webhook crm-dashboard
```

### 1.6 Configurar Nginx como Reverse Proxy

```bash
sudo nano /etc/nginx/sites-available/crm-whatsapp
```

Conteúdo:
```nginx
upstream webhook_backend {
    server 127.0.0.1:8000;
}

upstream dashboard_backend {
    server 127.0.0.1:8501;
}

server {
    listen 80;
    server_name seu-dominio.com;
    
    # Webhook (API)
    location /webhook/ {
        proxy_pass http://webhook_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Dashboard
    location / {
        proxy_pass http://dashboard_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Ativar site
sudo ln -s /etc/nginx/sites-available/crm-whatsapp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 1.7 Configurar SSL com Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d seu-dominio.com
```

### 1.8 Monitorar Logs

```bash
# Webhook
tail -f /var/log/crm-webhook.out.log

# Dashboard
tail -f /var/log/crm-dashboard.out.log

# Nginx
tail -f /var/log/nginx/error.log
```

---

## 2. OPÇÃO B: Deployment com Docker (Mais Fácil)

### 2.1 Criar Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \\
    postgresql-client \\
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Expor portas
EXPOSE 8000 8501

# Comando padrão
CMD ["python", "run.py"]
```

### 2.2 Criar docker-compose.yml

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: crm_user
      POSTGRES_PASSWORD: sua_senha
      POSTGRES_DB: crm_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  webhook:
    build: .
    command: python -m uvicorn app.webhooks.evolution_webhook:app --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://crm_user:sua_senha@db:5432/crm_db
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - EVOLUTION_API_KEY=${EVOLUTION_API_KEY}
      - EVOLUTION_INSTANCE_NAME=${EVOLUTION_INSTANCE_NAME}
    depends_on:
      - db
    restart: unless-stopped

  dashboard:
    build: .
    command: streamlit run dashboard/app.py --server.port=8501
    ports:
      - "8501:8501"
    environment:
      - DATABASE_URL=postgresql://crm_user:sua_senha@db:5432/crm_db
    depends_on:
      - db
    restart: unless-stopped

volumes:
  postgres_data:
```

### 2.3 Executar com Docker

```bash
# Build
docker-compose build

# Start
docker-compose up -d

# Logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## 3. CHECKLIST PRÉ-PRODUÇÃO

- [ ] Todas as variáveis de ambiente configuradas
- [ ] Database com backup automático ativo
- [ ] SSL/HTTPS funcionando
- [ ] Webhook acessível de fora
- [ ] Email testado e funcionando
- [ ] Evolution API validada
- [ ] Claude API testada
- [ ] Logs sendo salvos
- [ ] Monitoramento configurado
- [ ] Backup strategy definida

---

## 4. MONITORAMENTO E LOGS

### Logs Importantes

```bash
# Webhook
/var/log/crm-webhook.out.log
/var/log/crm-webhook.err.log

# Dashboard
/var/log/crm-dashboard.out.log
/var/log/crm-dashboard.err.log

# Nginx
/var/log/nginx/error.log
/var/log/nginx/access.log
```

### Alertas Recomendados

- Erros de conexão com Claude API
- Falhas ao enviar emails
- Database connection errors
- Webhook timeouts

---

## 5. BACKUPS

```bash
# Backup PostgreSQL diário
0 2 * * * /usr/bin/pg_dump -U crm_user -h localhost crm_db > /backups/crm_$(date +\\%Y-\\%m-\\%d).sql

# Upload para S3
0 3 * * * aws s3 cp /backups/ s3://seu-bucket-backup/ --recursive
```

---

## 6. PERFORMANCE

- Cache database queries: TTL 30 segundos
- Limite de mensagens por conversa: 50
- Timeout de requisição HTTP: 30s
- Rate limiting: 100 req/min por IP (adicionar em produção)

---

## 7. TROUBLESHOOTING

### Webhook recusando conexões
```bash
# Verificar se porta 8000 está aberta
sudo ufw allow 8000
```

### Database lento
```bash
# Criar índices
CREATE INDEX idx_lead_whatsapp ON leads(whatsapp_number);
CREATE INDEX idx_chat_number ON chat_messages(whatsapp_number);
```

### Streamlit não acessível
```bash
# Reiniciar
sudo supervisorctl restart crm-dashboard
```

---

Qualquer dúvida, verifique os logs!
"""

if __name__ == "__main__":
    print(DEPLOYMENT_GUIDE)
    
    # Opcionalmente salvar em arquivo
    with open("DEPLOYMENT.md", "w", encoding="utf-8") as f:
        f.write(DEPLOYMENT_GUIDE)
    
    print("\n✅ Guia salvo em DEPLOYMENT.md")
