# 🚀 INÍCIO RÁPIDO - CRM WhatsApp System

## ⚡ Comando Único (Recomendado)

```bash
# Abre wizard de configuração automático
python setup.py
```

---

## 📋 Passo a Passo Manual

### 1️⃣ Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2️⃣ Configurar Variáveis
```bash
# Copiar template
cp .env.example .env

# Editar com suas chaves
# Abra .env e preencha:
# - ANTHROPIC_API_KEY
# - EVOLUTION_API_KEY  
# - EVOLUTION_INSTANCE_NAME
# - ADMIN_EMAIL e ADMIN_WHATSAPP
# - SMTP_USER e SMTP_PASSWORD
```

### 3️⃣ Inicializar Banco
```bash
python app/__init__.py
```

### 4️⃣ Iniciar Sistema

**Terminal 1 - Webhook (FastAPI)**
```bash
python -m uvicorn app.webhooks.evolution_webhook:app --reload
```
✅ Acesso: http://localhost:8000
✅ Docs: http://localhost:8000/docs
✅ Webhook: POST http://localhost:8000/webhook/evolution

**Terminal 2 - Dashboard (Streamlit)**
```bash
streamlit run dashboard/app.py
```
✅ Acesso: http://localhost:8501

### 5️⃣ Configurar Webhook Evolution API

```
URL: http://seu-dominio.com/webhook/evolution
Método: POST
Evento: MESSAGES_UPSERT
```

**Para desenvolvimento local (sem domínio):**
```bash
# Terminal 3 - Instalar ngrok (https://ngrok.com)
ngrok http 8000

# Copie a URL gerada e use como webhook:
# https://seu-ngrok-url.ngrok.io/webhook/evolution
```

### 6️⃣ Testar Sistema

```bash
# Ver todas as integrações
python test_system.py

# Gerar comandos curl para teste
python webhook_tests.py
```

---

## 📊 O Que Cada Arquivo Faz

| Arquivo | Função | Porta |
|---------|--------|-------|
| `evolution_webhook.py` | Recebe mensagens WhatsApp | 8000 |
| `app.py` (dashboard) | Interface CRM | 8501 |
| `claude_service.py` | Integração com IA | - |
| `evolution_service.py` | Integração WhatsApp | - |
| `notification_service.py` | Email e notificações | - |
| `models.py` | Banco de dados | - |

---

## 🎯 Fluxo Rápido

```
1. Cliente envia mensagem no WhatsApp
   ↓
2. Webhook recebe e processa
   ↓
3. Sistema extrai dados (nome, interesse, necessidade)
   ↓
4. Se incompleto → Claude responde
5. Se completo → Notifica admin + Move para dashboard
   ↓
6. Atendente assume no dashboard
   ↓
7. Conversa continua com humano
```

---

## ⚙️ Variáveis de Ambiente Essenciais

```bash
# Mínimo necessário para funcionar:

ANTHROPIC_API_KEY=sk-ant-xxxxx
EVOLUTION_API_KEY=sk_xxxxx
EVOLUTION_INSTANCE_NAME=sua_instancia
ADMIN_EMAIL=admin@email.com
ADMIN_WHATSAPP=5511999999999
SMTP_USER=seu_email@gmail.com
SMTP_PASSWORD=sua_senha_app
```

---

## 🧪 Testar Webhook com CURL

```bash
curl -X POST http://localhost:8000/webhook/evolution \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "instanceId": "test",
      "message": {
        "key": {"remoteJid": "5511999999999@s.whatsapp.net"},
        "message": {"conversation": "Oi! Preciso de um software"}
      }
    }
  }'
```

---

## 📚 Documentação Completa

- **Técnica**: `README.md`
- **Rápida**: `GETTING_STARTED.md`  
- **Deploy**: `DEPLOYMENT.md`
- **Sumário**: `PROJECT_SUMMARY.py` (execute para ver)

---

## 🐛 Problemas Comuns

### ❌ "ModuleNotFoundError: No module named 'anthropic'"
**Solução**: `pip install -r requirements.txt`

### ❌ "ANTHROPIC_API_KEY not found"
**Solução**: Edite `.env` com sua chave

### ❌ "Webhook não recebe mensagens"
**Solução**: 
1. Verifique Evolution API configurada corretamente
2. Teste com curl (comando acima)
3. Use ngrok para desenvolvimento local

### ❌ Dashboard vazio
**Solução**: 
1. Webhook está recebendo? (verifique logs)
2. Banco de dados foi inicializado? (`python app/__init__.py`)
3. Envie uma mensagem de teste

---

## 🎉 Sucesso?

Se ver no dashboard um lead qualificado = **Sistema funcionando!**

Agora configure na Evolution API e comece!

---

## 📞 Próximas Dúvidas?

1. Veja `README.md` para detalhes técnicos
2. Veja `DEPLOYMENT.md` para produção
3. Execute `python PROJECT_SUMMARY.py` para visão geral
4. Verifique logs no terminal do webhook

---

**Desenvolvido com ❤️ | Python + FastAPI + Claude + Evolution API**

Última atualização: Janeiro 2026
