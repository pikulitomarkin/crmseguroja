# CRM WhatsApp System - Documentação Técnica

## 📋 Visão Geral

Sistema completo de qualificação automática de leads via WhatsApp, integrado com IA (Claude) e Dashboard CRM.

**Stack Tecnológico:**
- **Backend:** FastAPI + Python 3.10+
- **Database:** SQLite/PostgreSQL
- **Frontend:** Streamlit
- **IA:** Anthropic Claude (Haiku)
- **WhatsApp:** Evolution API

---

## 🚀 Instalação Rápida

### 1. Requisitos
- Python 3.10+
- pip

### 2. Clone e Configuração

```bash
cd c:\crm whats
pip install -r requirements.txt
```

### 3. Configure as Variáveis de Ambiente

Copie e edite o arquivo `.env`:

```bash
cp .env.example .env
```

Edite `.env` com suas chaves:

```
ANTHROPIC_API_KEY=sk-ant-xxxxx
EVOLUTION_API_KEY=sua_chave_evolution
EVOLUTION_API_URL=https://api.evolution.br/api
EVOLUTION_INSTANCE_NAME=sua_instancia
ADMIN_WHATSAPP=5511999999999
ADMIN_EMAIL=admin@email.com
SMTP_USER=seu_email@gmail.com
SMTP_PASSWORD=sua_senha_app
```

### 4. Inicialize o Banco de Dados

```bash
python app/__init__.py
```

---

## 🏗️ Estrutura do Projeto

```
c:\crm whats\
├── app/
│   ├── database/
│   │   ├── models.py           # Modelos SQLAlchemy (Lead, ChatMessage, etc)
│   │   └── __init__.py
│   ├── services/
│   │   ├── claude_service.py   # Integração com Claude API
│   │   ├── evolution_service.py # Integração com Evolution API
│   │   ├── notification_service.py # Email e notificações
│   │   ├── database_service.py # CRUD operations
│   │   └── __init__.py
│   ├── webhooks/
│   │   ├── evolution_webhook.py # Webhook endpoint FastAPI
│   │   └── __init__.py
│   ├── core/
│   │   ├── prompts.py          # System prompts para Claude
│   │   ├── qualification.py    # Lógica de qualificação
│   │   ├── utils.py            # Utilitários
│   │   └── __init__.py
│   └── __init__.py
├── dashboard/
│   ├── app.py                  # Dashboard Streamlit
│   └── __init__.py
├── config/
│   ├── settings.py             # Configurações centralizadas
│   └── __init__.py
├── requirements.txt            # Dependências
├── .env.example                # Exemplo de variáveis
├── .gitignore
└── README.md
```

---

## 🔄 Fluxo de Funcionamento

### 1️⃣ **Recebimento de Mensagem (Webhook)**

```
Evolution API → Webhook /webhook/evolution (FastAPI)
```

### 2️⃣ **Processamento**

```
Message recebida
    ↓
Verifica se IA está ativa para o número
    ↓
Classifica cliente (novo/existente)
    ↓
Salva mensagem no banco
    ↓
Extrai dados (nome, interesse, necessidade)
```

### 3️⃣ **Decisão: Responder ou Transferir**

```
Se qualificado completo:
    → Desativa IA
    → Notifica admin (Email + WhatsApp)
    → Coloca em coluna "Pronto para Atendimento"
    
Se não qualificado:
    → Gera resposta com Claude
    → Envia via Evolution API
```

### 4️⃣ **Dashboard**

O atendente acessa o dashboard para:
- Ver leads qualificados
- Visualizar histórico de conversas
- Assumir o atendimento
- Finalizar ou reativar IA

---

## 📡 Integrações

### Anthropic Claude API

**Endpoints usados:**
- `messages.create()` - Gerar respostas
- Context window: 5000 tokens (últimas 10 mensagens)

**Models disponíveis:**
- `claude-3-5-haiku-20241022` (rápido, barato)
- `claude-3-opus-20240229` (mais inteligente)

### Evolution API

**Endpoints:**
```
POST /message/sendText/{instance}
POST /chat/togglePresence/{instance}
```

**Headers:**
```
Content-Type: application/json
apikey: {EVOLUTION_API_KEY}
```

### Notificações

**Email:** SMTP (Gmail, Outlook, etc)
**WhatsApp:** Evolution API

---

## 🚀 Como Executar

### Terminal 1: FastAPI Webhook Server

```bash
cd c:\crm whats
python -m uvicorn app.webhooks.evolution_webhook:app --reload --host 0.0.0.0 --port 8000
```

Webhook estará disponível em: `http://localhost:8000/webhook/evolution`

### Terminal 2: Streamlit Dashboard

```bash
cd c:\crm whats
streamlit run dashboard/app.py
```

Dashboard estará em: `http://localhost:8501`

---

## 🛠️ Configurando o Webhook na Evolution API

Acesse seu painel Evolution API e configure:

```
URL: https://seu-dominio.com/webhook/evolution
Método: POST
Eventos: MESSAGES_UPSERT
```

Para desenvolvimento local, use ngrok:

```bash
ngrok http 8000
```

Então use: `https://seu-ngrok-url.ngrok.io/webhook/evolution`

---

## 📊 Banco de Dados

### Tabelas Principais

**leads**
- `id`: ID único
- `whatsapp_number`: Número WhatsApp (chave única)
- `name`: Nome do cliente
- `interest`: Interesse coletado
- `necessity`: Necessidade coletada
- `status`: novo/qualificado/em_atendimento/finalizado
- `status_ia`: 1 (ativo) ou 0 (inativo)
- `customer_type`: novo/existente
- `created_at`, `updated_at`: Timestamps
- `qualified_at`: Quando foi qualificado
- `attended_by`: Qual atendente assumiu

**chat_messages**
- `id`: ID único
- `whatsapp_number`: Referência ao lead
- `sender`: "user" ou "ai"
- `message`: Conteúdo
- `role`: "user" ou "assistant" (para Claude)
- `created_at`: Timestamp

**qualification_fields**
- `whatsapp_number`: Chave
- `has_name`, `has_interest`, `has_necessity`: Booleanos
- Rastreia quais campos foram coletados

**notification_logs**
- Registro de emails e mensagens enviadas
- Status: enviado/falha/pendente

---

## 🎯 System Prompt do Claude

O sistema usa dois prompts diferentes:

### Para Novos Clientes (Qualificação)
```
Você é atendente de vendas profissional...
Objetivo: Coletar nome, interesse e necessidade
JAMAIS fale sobre preços
```

### Para Clientes Existentes
```
Você é assistente para clientes existentes...
Responda apenas dúvidas comuns
Não discuta preços ou planos
```

Ver detalhes em `app/core/prompts.py`

---

## 🎪 Lógica de Qualificação

Um lead é considerado **qualificado** quando:
1. ✅ Nome coletado
2. ✅ Interesse coletado
3. ✅ Necessidade coletada

O sistema extrai esses dados automaticamente do histórico de chat usando Claude.

---

## 📧 Sistema de Notificações

### Quando um Lead é Qualificado:

1. **Email ao Admin**
```html
Novo Lead Qualificado
Nome: João Silva
WhatsApp: 5511999999999
Interesse: Software de automação
Necessidade: Integrar com meu sistema
```

2. **WhatsApp ao Admin**
```
🎯 NOVO LEAD QUALIFICADO
Nome: João Silva
WhatsApp: 5511999999999
Interesse: Software
Necessidade: Integração
```

3. **Dashboard**
- Lead aparece em "Leads Qualificados"
- Botão "Assumir" disponível

---

## 🔧 Variáveis de Ambiente (`.env`)

```bash
# Evolution API (WhatsApp)
EVOLUTION_API_URL=https://api.evolution.br/api
EVOLUTION_API_KEY=sk_xxxxx
EVOLUTION_INSTANCE_NAME=sua_instancia

# Claude (IA)
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Email (Notificações)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu_email@gmail.com
SMTP_PASSWORD=sua_senha_app  # Para Gmail: gerar senha de app

# Admin
ADMIN_WHATSAPP=5511999999999
ADMIN_EMAIL=admin@seudominio.com

# Banco de Dados
DATABASE_URL=sqlite:///./crm_system.db
# ou: postgresql://user:password@localhost/crm_db

# API
API_HOST=0.0.0.0
API_PORT=8000
```

---

## 💡 Recursos Avançados

### 1. Extração Automática de Dados

O sistema usa Claude para extrair informações do chat:

```python
extracted_data = claude_service.extract_qualification_data(conversation)
# Retorna: {"name": "João", "interest": "...", "necessity": "..."}
```

### 2. Typing Indicator

Mostra "digitando..." antes de enviar resposta:

```python
await evolution_service.send_message(
    number, 
    message, 
    show_typing=True  # Aguarda 2s antes de enviar
)
```

### 3. Histórico Contextualizado

Apenas últimas 10 mensagens são enviadas para Claude para economizar tokens:

```python
messages = db.query(ChatMessage).filter(...).limit(10)
```

---

## 📝 Exemplos de Uso

### Enviar Mensagem Manual

```python
from app.services.evolution_service import EvolutionService

service = EvolutionService()
await service.send_message("5511999999999", "Olá! Como posso ajudar?")
```

### Qualificar Lead Manualmente

```python
from app.services.database_service import LeadService
from app.database.models import get_session, init_db
from config.settings import settings

engine = init_db(settings.DATABASE_URL)
db = get_session(engine)
lead = LeadService.get_lead_by_number(db, "5511999999999")
LeadService.mark_qualified(db, lead, attended_by="Sistema")
```

### Enviar Email Customizado

```python
from app.services.notification_service import NotificationService

notif = NotificationService(db)
notif.send_email(
    recipient_email="admin@example.com",
    subject="Lead Qualificado",
    body="Texto simples",
    html_body="<h1>HTML opcional</h1>"
)
```

---

## ⚠️ Troubleshooting

### Error: "ANTHROPIC_API_KEY not found"
- Verifique `.env` com a chave correta
- Reinicie a aplicação

### Mensagens não chegam no WhatsApp
- Verifique `EVOLUTION_API_KEY` e `EVOLUTION_INSTANCE_NAME`
- Teste o webhook com curl:
```bash
curl -X POST http://localhost:8000/webhook/evolution \
  -H "Content-Type: application/json" \
  -d '{"data":{"message":{"key":{"remoteJid":"5511999999999"},"message":{"conversation":"teste"}}}}'
```

### Dashboard não atualiza
- Limpe o cache: Delete `/.streamlit/cache`
- Verifique DATABASE_URL

---

## 🔐 Segurança

1. **Nunca commit `.env`** - Use `.env.example`
2. **Validar todos inputs** do webhook
3. **Rate limiting** em produção (adicionar após MVP)
4. **HTTPS** sempre em produção
5. **Tokens:** Guardar em variáveis de ambiente, nunca em código

---

## 📈 Próximos Passos

- [ ] Autenticação no Dashboard
- [ ] Histórico de ações do atendente
- [ ] Agendamento automático de follow-up
- [ ] Integrações com CRM (Pipedrive, Hubspot)
- [ ] Analytics e relatórios
- [ ] Múltiplas instâncias WhatsApp
- [ ] Fila inteligente de atendimento

---

## 📞 Suporte

Para dúvidas técnicas:
1. Verifique os logs em `uvicorn` output
2. Inspeccione o banco de dados
3. Teste o webhook manualmente

---

**Desenvolvido com ❤️ | Python + FastAPI + Claude + Evolution API**
