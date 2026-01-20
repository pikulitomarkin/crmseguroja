"""
📊 SUMÁRIO DO PROJETO - CRM WhatsApp + Claude + Evolution API

Gerado em: Janeiro 19, 2026
Versão: 1.0.0
Status: Em Desenvolvimento
"""

PROJECT_STRUCTURE = """
📁 c:\\crm whats\\
│
├── 📄 ARQUIVOS RAIZ
│   ├── run.py                    → Script para iniciar o sistema
│   ├── setup.py                  → Wizard de configuração
│   ├── test_system.py            → Testes das integrações
│   ├── webhook_tests.py          → Testes de webhook
│   ├── deployment_guide.py       → Guia de deployment
│   ├── requirements.txt          → Dependências Python
│   ├── .env.example              → Template de variáveis
│   ├── .gitignore                → Arquivos ignorados
│   ├── README.md                 → Documentação técnica
│   ├── GETTING_STARTED.md        → Guia rápido
│   └── DEPLOYMENT.md             → Deployment em produção
│
├── 📁 app/
│   ├── 📁 database/              → Camada de dados
│   │   ├── models.py             → SQLAlchemy models (Lead, ChatMessage, etc)
│   │   └── __init__.py
│   │
│   ├── 📁 services/              → Lógica de negócio
│   │   ├── claude_service.py     → Integração Claude API
│   │   ├── evolution_service.py  → Integração WhatsApp
│   │   ├── notification_service.py → Email + WhatsApp
│   │   ├── database_service.py   → CRUD operations
│   │   └── __init__.py
│   │
│   ├── 📁 webhooks/              → API endpoints
│   │   ├── evolution_webhook.py  → Webhook FastAPI main
│   │   └── __init__.py
│   │
│   ├── 📁 core/                  → Lógica central
│   │   ├── prompts.py            → System prompts para Claude
│   │   ├── qualification.py      → Engine de qualificação
│   │   ├── utils.py              → Utilitários
│   │   └── __init__.py
│   │
│   └── __init__.py
│
├── 📁 dashboard/                 → Interface do usuário
│   ├── app.py                    → Dashboard Streamlit (main)
│   └── __init__.py
│
└── 📁 config/                    → Configurações
    ├── settings.py               → Variáveis e settings
    └── __init__.py


🔧 ARQUITETURA DO SISTEMA
═══════════════════════════════════════════════════════════════

┌─────────────────┐
│  USUÁRIO/ADMIN  │
└────────┬────────┘
         │
         ├────────────────────────────────────────┐
         │                                        │
    (WhatsApp)                            (Browser)
         │                                        │
         ▼                                        ▼
┌─────────────────────┐              ┌──────────────────┐
│  EVOLUTION API      │              │  STREAMLIT DASH  │
│  (Webhook)          │              │  (Port 8501)     │
└────────┬────────────┘              └──────────┬───────┘
         │                                      │
         │ POST /webhook/evolution              │
         ▼                                      ▼
┌──────────────────────────────────────────────────────────┐
│              FASTAPI WEBHOOK SERVER (Port 8000)         │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ 1. Receber mensagem WhatsApp                       │ │
│  │ 2. Verificar status_ia (IA ativa?)                │ │
│  │ 3. Salvar mensagem no banco                       │ │
│  │ 4. Extrair dados (nome, interesse, necessidade) │ │
│  │ 5. Decidir: Responder ou Transferir              │ │
│  └─────────────────────────────────────────────────────┘ │
└────┬────────────────────────────────────────────────┬────┘
     │                                                │
     ├────────────────────┬──────────────────────────┤
     │                    │                          │
     ▼                    ▼                          ▼
┌──────────────┐  ┌──────────────┐          ┌──────────────┐
│  CLAUDE API  │  │  DATABASE    │          │NOTIFICATION │
│  (Responder) │  │  (SQLite or  │          │ Service      │
│              │  │  PostgreSQL) │          │              │
└──────────────┘  └──────────────┘          └────┬─────────┘
                        │                        │
                        │              ┌─────────┴─────────┐
                        │              │                   │
                        │              ▼                   ▼
                        │          ┌────────┐         ┌─────────┐
                        │          │ EMAIL  │         │WHATSAPP │
                        │          │ SMTP   │         │ NOTIF   │
                        │          └────────┘         └─────────┘
                        │
                        └── SALVA EM:
                            ├── leads
                            ├── chat_messages
                            ├── qualification_fields
                            └── notification_logs


🎯 FLUXO DE UM NOVO LEAD
═══════════════════════════════════════════════════════════════

1️⃣  CLIENTE INICIA CONVERSA NO WHATSAPP
    "Olá! Preciso de um software"
         │
         └→ Webhook recebe evento MESSAGES_UPSERT

2️⃣  SISTEMA PROCESSA
    - ✅ Cria lead automaticamente
    - ✅ Verifica se IA está ativa
    - ✅ Salva mensagem no histórico
    - ✅ Extrai dados iniciais com Claude

3️⃣  PRIMEIRO CICLO (INCOMPLETO)
    ❌ Não tem todos os dados (nome, interesse, necessidade)
    ✅ Gera resposta com Claude
    ✅ Mostra "digitando..."
    ✅ Envia resposta via Evolution API
    ✅ Aguarda próxima mensagem

4️⃣  CLIENTE RESPONDE
    "Meu nome é João Silva, preciso integrar com meu CRM"
         │
         └→ Loop volta ao passo 2

5️⃣  QUALIFICAÇÃO COMPLETA
    ✅ Sistema detecta que tem:
       - Nome: João Silva
       - Interesse: Software
       - Necessidade: Integração com CRM
    
    TRANSIÇÃO AUTOMÁTICA:
    ├─ Desativa IA para este número (status_ia = 0)
    ├─ Atualiza lead: status = "qualificado"
    ├─ Envia EMAIL ao admin com resumo
    ├─ Envia WHATSAPP ao admin com notificação
    ├─ Dashboard mostra lead em "Pronto para Atendimento"
    └─ Envia mensagem ao cliente informando que será contatado

6️⃣  ATENDENTE HUMANO ASSUME
    - Acessa dashboard
    - Vê lead qualificado
    - Clica "Assumir"
    - Dashboard marca como "em_atendimento"
    - Atendente pode reiniciar IA se precisar


📦 DEPENDÊNCIAS PRINCIPAIS
═══════════════════════════════════════════════════════════════

FastAPI              → API Web framework
Uvicorn              → ASGI server
SQLAlchemy           → ORM para banco de dados
Anthropic            → Claude API client
Aiohttp              → HTTP assíncrono
Streamlit            → Dashboard web
Pandas               → Data analysis
Python-dotenv        → Variáveis de ambiente
Psycopg2             → PostgreSQL driver (opcional)


🔐 SEGURANÇA IMPLEMENTADA
═══════════════════════════════════════════════════════════════

✅ PROTEÇÃO DE PREÇOS
   - System prompt explicitamente bloqueia discussão de preços
   - Se cliente perguntar sobre preço, resposta padrão: 
     "Consultor humano cuidará dessa parte"

✅ STATUS DA IA
   - Coluna status_ia no banco: 1 (ativo) ou 0 (inativo)
   - Webhook verifica antes de responder
   - Atendente humano controla status

✅ LOGS DETALHADOS
   - Todas as mensagens salvas
   - Notificações rastreadas
   - Histórico completo no dashboard

✅ VARIÁVEIS PROTEGIDAS
   - Nenhuma chave em código
   - Tudo em .env (não commitado)
   - .gitignore configurado


📱 INTEGRAÇÕES EXTERNAS
═══════════════════════════════════════════════════════════════

CLAUDE API (Anthropic)
├─ Endpoint: https://api.anthropic.com/v1/messages
├─ Model: claude-3-5-haiku-20241022
├─ Max tokens: 500
└─ Context: Últimas 10 mensagens

EVOLUTION API (WhatsApp)
├─ Endpoint: {EVOLUTION_API_URL}/message/sendText/{instance}
├─ Método: POST
├─ Features: Mensagens + Typing indicator
└─ Auth: API key

EMAIL (SMTP)
├─ Provider: Gmail, Outlook, etc
├─ Port: 587 (TLS)
└─ Auth: Email + Senha de app

DATABASE
├─ SQLite (default): ./crm_system.db
└─ PostgreSQL: postgresql://user:pass@host/db


📊 TABELAS DO BANCO DE DADOS
═══════════════════════════════════════════════════════════════

LEADS
├─ id (INT, PK)
├─ whatsapp_number (STR, UNIQUE)
├─ name (STR)
├─ interest (TEXT)
├─ necessity (TEXT)
├─ status (STR: novo/qualificado/em_atendimento/finalizado)
├─ status_ia (INT: 1=ativo, 0=inativo)
├─ customer_type (STR: novo/existente)
├─ created_at (DATETIME)
├─ updated_at (DATETIME)
├─ qualified_at (DATETIME)
└─ attended_by (STR)

CHAT_MESSAGES
├─ id (INT, PK)
├─ lead_id (INT, FK)
├─ whatsapp_number (STR, INDEX)
├─ sender (STR: user/ai)
├─ message (TEXT)
├─ role (STR: user/assistant para Claude)
└─ created_at (DATETIME, INDEX)

QUALIFICATION_FIELDS
├─ id (INT, PK)
├─ lead_id (INT, FK)
├─ whatsapp_number (STR, INDEX)
├─ has_name (BOOL)
├─ has_interest (BOOL)
├─ has_necessity (BOOL)
├─ created_at (DATETIME)
└─ updated_at (DATETIME)

NOTIFICATION_LOGS
├─ id (INT, PK)
├─ lead_id (INT, FK)
├─ whatsapp_number (STR, INDEX)
├─ notification_type (STR: email/whatsapp)
├─ recipient (STR)
├─ status (STR: enviado/falha/pendente)
├─ created_at (DATETIME)
└─ error_message (TEXT)


🚀 COMO COMEÇAR
═══════════════════════════════════════════════════════════════

1. INSTALAR DEPENDÊNCIAS
   pip install -r requirements.txt

2. CONFIGURAR VARIÁVEIS
   python setup.py
   (Wizard interativo)

3. INICIALIZAR BANCO
   python app/__init__.py

4. TESTAR CONEXÕES
   python test_system.py

5. INICIAR SISTEMA
   Terminal 1: python -m uvicorn app.webhooks.evolution_webhook:app --reload
   Terminal 2: streamlit run dashboard/app.py

6. CONFIGURAR WEBHOOK NA EVOLUTION API
   URL: https://seu-dominio.com/webhook/evolution
   (Para dev local, use ngrok)

7. TESTAR WEBHOOK
   python webhook_tests.py


📋 CHECKLIST DE CONFIGURAÇÃO
═══════════════════════════════════════════════════════════════

Arquivo .env:
  □ ANTHROPIC_API_KEY configurada
  □ EVOLUTION_API_KEY configurada
  □ EVOLUTION_INSTANCE_NAME configurada
  □ ADMIN_WHATSAPP configurado
  □ ADMIN_EMAIL configurado
  □ SMTP_USER e SMTP_PASSWORD configurados
  □ DATABASE_URL configurada

Testes:
  □ Banco de dados criado
  □ Claude API respondendo
  □ Evolution API validada
  □ Email testado

Sistema:
  □ Webhook rodando (porta 8000)
  □ Dashboard rodando (porta 8501)
  □ Webhook configurado na Evolution API
  □ Primeira mensagem sendo processada


🎯 PRÓXIMOS PASSOS
═══════════════════════════════════════════════════════════════

MVP (Atual):
  ✅ Qualificação automática de leads
  ✅ Notificações ao admin
  ✅ Dashboard CRM básico
  ✅ IA com bloqueio de preços

Fase 2:
  □ Autenticação no dashboard
  □ Múltiplas instâncias WhatsApp
  □ Agendamento de follow-up
  □ Integração com Pipedrive/Hubspot
  □ Analytics e relatórios

Fase 3:
  □ Custom workflows
  □ Bot training com histórico
  □ Integração SMS
  □ Chatbot multilíngue


📞 DOCUMENTAÇÃO
═══════════════════════════════════════════════════════════════

README.md              → Documentação técnica completa
GETTING_STARTED.md    → Guia rápido
DEPLOYMENT.md         → Deploy em produção
webhook_tests.py      → Exemplos de teste
setup.py              → Assistente de configuração


✨ RECURSOS ÚNICOS DO SISTEMA
═══════════════════════════════════════════════════════════════

✅ Qualificação automática com extração de dados
✅ Sistema de status_ia (IA ativa/inativa por lead)
✅ Transição automática para humano quando qualificado
✅ Notificações por email e WhatsApp integradas
✅ Dashboard em tempo real com Streamlit
✅ Typing indicator para conversas naturais
✅ Context window otimizado para economia de tokens
✅ Logs completos de todas as operações
✅ Suporte a múltiplos tipos de cliente (novo/existente)
✅ Fácil deploy em Docker ou servidor tradicional


🎉 PRONTO PARA USAR!

Execute: python run.py

Dúvidas? Consulte README.md ou GETTING_STARTED.md

Desenvolvido com ❤️ | Python + FastAPI + Claude + Evolution API
═══════════════════════════════════════════════════════════════
"""

if __name__ == "__main__":
    print(PROJECT_STRUCTURE)
    
    # Salvar em arquivo
    with open("PROJECT_SUMMARY.txt", "w", encoding="utf-8") as f:
        f.write(PROJECT_STRUCTURE)
    
    print("\n✅ Sumário salvo em PROJECT_SUMMARY.txt")
