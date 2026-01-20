# CRM WhatsApp + Claude + Evolution API

## 📊 Dashboard

![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

Sistema completo de qualificação automática de leads via WhatsApp, integrado com IA Claude e Dashboard CRM.

---

## ✨ Recursos Principais

✅ **Atendimento Automatizado com IA**
- Claude Haiku para respostas naturais
- System prompts customizados
- Histórico contextualizado

✅ **Qualificação de Leads**
- Coleta automática de: Nome, Interesse, Necessidade
- Extração inteligente de dados
- Transferência automática para humano

✅ **Notificações**
- Email com resumo do lead
- WhatsApp para admin
- Dashboard em tempo real

✅ **Dashboard CRM**
- Visualização de leads qualificados
- Histórico de conversas
- Controle de status da IA
- Assumir atendimento com um clique

✅ **Segurança**
- Bloqueio de discussão de preços
- Status de IA ativo/inativo por lead
- Logs de todas as operações
- Notificações de transferência

---

## 🏗️ Arquitetura

```
Evolution API (WhatsApp)
        ↓
  FastAPI Webhook
        ↓
  Claude AI (Resposta)
        ↓
  Database (Histórico)
        ↓
  Notifications (Email/WhatsApp)
        ↓
  Streamlit Dashboard
```

---

## 📁 Estrutura do Projeto

```
c:\crm whats\
├── app/
│   ├── database/           # Modelos SQLAlchemy
│   ├── services/           # Lógica de negócio
│   ├── webhooks/           # FastAPI endpoints
│   └── core/               # Qualificação e prompts
├── dashboard/              # Streamlit UI
├── config/                 # Configurações
├── requirements.txt        # Dependências
├── .env.example           # Template de variáveis
├── run.py                 # Script de execução
├── test_system.py         # Testes unitários
└── README.md
```

---

## 🚀 Início Rápido

### 1. Instalação

```bash
# Clonar/preparar projeto
cd c:\crm whats

# Criar ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente

```bash
# Copiar template
cp .env.example .env

# Editar .env com suas chaves:
# - ANTHROPIC_API_KEY
# - EVOLUTION_API_KEY
# - EVOLUTION_INSTANCE_NAME
# - ADMIN_WHATSAPP e ADMIN_EMAIL
# - Credenciais SMTP
```

### 3. Inicializar Banco de Dados

```bash
python app/__init__.py
```

### 4. Executar Sistema

```bash
# Terminal 1 - Webhook
python -m uvicorn app.webhooks.evolution_webhook:app --reload

# Terminal 2 - Dashboard
streamlit run dashboard/app.py
```

Webhook: http://localhost:8000/webhook/evolution
Dashboard: http://localhost:8501

---

## 📊 Fluxo de Funcionamento

### 1. Cliente Inicia Conversa
```
WhatsApp → Evolution API Webhook → Sistema
```

### 2. Sistema Processa
```
✓ Verifica se IA está ativa
✓ Classifica cliente (novo/existente)
✓ Salva mensagem no histórico
✓ Extrai dados de qualificação
```

### 3. Decisão Automática
```
Se qualificado completo:
  → Desativa IA para o número
  → Notifica admin (Email + WhatsApp)
  → Move para dashboard "Pronto para Atendimento"

Se não qualificado:
  → Gera resposta com Claude
  → Envia via Evolution API
  → Continua coleta de dados
```

### 4. Dashboard
```
Atendente visualiza leads qualificados
Clica "Assumir" para começar atendimento
IA é desativada automaticamente
```

---

## 🤖 System Prompts

### Novos Clientes
```
Objetivo: Coletar nome, interesse e necessidade
Restrição: JAMAIS informar preços
Tom: Profissional e amigável
```

### Clientes Existentes
```
Objetivo: Responder apenas dúvidas comuns
Restrição: Não discutir preços ou planos complexos
Tom: Assistente de suporte
```

---

## 📧 Notificações

### Quando Lead é Qualificado

**Email:**
```html
Nome: João Silva
WhatsApp: 5511999999999
Interesse: Software de automação
Necessidade: Integração com CRM
```

**WhatsApp:**
```
🎯 NOVO LEAD QUALIFICADO
Nome: João Silva
WhatsApp: 5511999999999
...
```

**Dashboard:**
- Aparece em "Leads Qualificados"
- Botão "Assumir" disponível
- Histórico completo visível

---

## 🛠️ Serviços Disponíveis

### ClaudeService
```python
# Resposta contextualizada
response = claude.get_response(
    user_message="Olá",
    conversation_history=[...],
    customer_type="novo"
)

# Extração de dados
data = claude.extract_qualification_data(conversation)
```

### EvolutionService
```python
# Enviar mensagem com typing
await evolution.send_message(
    whatsapp_number="551199999999",
    message="Olá!",
    show_typing=True
)
```

### NotificationService
```python
# Email
notif.send_email(
    recipient_email="admin@email.com",
    subject="Novo Lead",
    body="Texto"
)

# WhatsApp
await notif.send_whatsapp_notification(
    whatsapp_number="551199999999",
    message="Notificação"
)
```

---

## 📊 Banco de Dados

### Tabelas

**leads** - Dados do cliente
- id, whatsapp_number, name, interest, necessity
- status (novo/qualificado/em_atendimento/finalizado)
- status_ia (1=ativo, 0=inativo)
- customer_type (novo/existente)

**chat_messages** - Histórico
- id, whatsapp_number, sender (user/ai), message
- role (user/assistant para Claude)

**qualification_fields** - Rastreamento
- whatsapp_number, has_name, has_interest, has_necessity

**notification_logs** - Auditoria
- lead_id, notification_type, recipient, status

---

## 🔧 Configuração

### Variáveis de Ambiente

```bash
# Claude
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Evolution API
EVOLUTION_API_URL=https://api.evolution.br/api
EVOLUTION_API_KEY=sk_xxxxx
EVOLUTION_INSTANCE_NAME=sua_instancia

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=email@gmail.com
SMTP_PASSWORD=senha_app

# Admin
ADMIN_WHATSAPP=5511999999999
ADMIN_EMAIL=admin@domain.com

# Database
DATABASE_URL=sqlite:///./crm_system.db
# Ou: postgresql://user:pass@localhost/crm_db

# API
API_PORT=8000
STREAMLIT_PORT=8501
```

---

## 🧪 Testes

```bash
# Testar todas as integrações
python test_system.py

# Gerar comandos curl para webhook
python webhook_tests.py
```

---

## 📈 Recursos Avançados

### Extração de Dados
Usa Claude para extrair informações do chat automaticamente

### Typing Indicator
Mostra "digitando..." para conversas mais naturais

### Context Window
Mantém últimas 10 mensagens para economia de tokens

### Rate Limiting
Pronto para adicionar em produção

---

## 🚀 Deploy

### Docker
```bash
docker-compose up -d
```

### Linux + Nginx
Ver `DEPLOYMENT.md` para instruções completas

### Cloudflare Workers
Possível usar como edge proxy

---

## 🔐 Segurança

✅ Variáveis de ambiente protegidas
✅ Sem discussão de preços (bloqueado)
✅ IA ativa/inativa por lead
✅ Logs de todas as operações
✅ HTTPS em produção

---

## 📝 Exemplos de Uso

### Criar um Lead Manualmente

```python
from app.services.database_service import LeadService
from app.database.models import init_db, get_session
from config.settings import settings

engine = init_db(settings.DATABASE_URL)
db = get_session(engine)

lead = LeadService.create_or_get_lead(
    db, 
    "5511999999999",
    customer_type="novo"
)
```

### Enviar Notificação

```python
from app.services.notification_service import NotificationService

notif = NotificationService(db)
await notif.notify_admin_lead_qualified(
    lead_data={
        "name": "João Silva",
        "interest": "Software",
        "necessity": "Automação"
    },
    whatsapp_number="5511999999999"
)
```

---

## 🐛 Troubleshooting

### Mensagens não chegam?
- Verifique `EVOLUTION_API_KEY`
- Teste o webhook com `curl`
- Verifique logs da API

### Dashboard vazio?
- Confirme que webhook está recebendo mensagens
- Verifique banco de dados: `sqlite3 crm_system.db`
- Limpe cache Streamlit

### Claude não responde?
- Valide `ANTHROPIC_API_KEY`
- Execute `python test_system.py`
- Verifique quota da API

---

## 📞 Suporte

Documentação completa em `README.md`
Deployment: `DEPLOYMENT.md`
Testes: `test_system.py`

---

## 📄 Licença

MIT - Use livremente

---

## 🎯 Roadmap

- [ ] Multi-instance WhatsApp
- [ ] Integração Pipedrive/Hubspot
- [ ] Analytics avançado
- [ ] Agendamento automático
- [ ] Custom workflows
- [ ] Webhooks customizáveis

---

**Desenvolvido com ❤️ | Python + FastAPI + Claude + Evolution API**

Última atualização: Janeiro 2026
