# 🚀 Deploy no Railway

## 📋 Pré-requisitos

1. Conta no Railway: https://railway.app
2. GitHub para conectar o repositório (ou fazer deploy direto)

## 🔧 Passo a Passo

### 1. Criar Projeto no Railway

1. Acesse https://railway.app
2. Clique em **"New Project"**
3. Escolha **"Deploy from GitHub repo"** ou **"Empty Project"**

### 2. Configurar Variáveis de Ambiente

No Railway, vá em **Variables** e adicione:

```env
# OpenAI
OPENAI_API_KEY=sk-proj-sua_chave_aqui
OPENAI_MODEL=gpt-4o

# Evolution API
EVOLUTION_API_URL=evolution-api-production-df00.up.railway.app
EVOLUTION_API_KEY=seguroja2026
EVOLUTION_INSTANCE_NAME=seguroja

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=mpadilha932@gmail.com
SMTP_PASSWORD=hapfdjeczjhvnmna
EMAIL_FROM=mpadilha932@gmail.com

# Notificações
ADMIN_WHATSAPP=5511983217785
ADMIN_EMAIL=contato@seguroja.com.br

# Banco (Railway fornece automaticamente se adicionar PostgreSQL)
DATABASE_URL=sqlite:///./crm_system.db

# API
API_HOST=0.0.0.0
API_PORT=8000
```

### 3. Deploy

#### Opção A: Via GitHub
1. Faça push do código para GitHub
2. No Railway, conecte o repositório
3. Railway fará deploy automaticamente

#### Opção B: Railway CLI
```bash
# Instalar CLI
npm i -g @railway/cli

# Login
railway login

# Iniciar projeto
railway init

# Deploy
railway up
```

### 4. Configurar Webhook na Evolution API

Após o deploy, o Railway vai gerar uma URL (ex: `https://seu-projeto.up.railway.app`)

Configure no Evolution API:
- **URL**: `https://seu-projeto.up.railway.app/webhook/evolution`
- **Eventos**: MESSAGES_UPSERT

## ✅ Verificar Deploy

Acesse: `https://seu-projeto.up.railway.app/health`

Deve retornar:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

## 🗄️ Banco de Dados (Opcional)

Para usar PostgreSQL no Railway:
1. Clique em **"New"** → **"Database"** → **"Add PostgreSQL"**
2. Railway vai criar `DATABASE_URL` automaticamente
3. O sistema vai usar PostgreSQL ao invés de SQLite

## 📊 Monitoramento

- **Logs**: Aba "Deployments" → Clique no deploy → "View Logs"
- **Métricas**: Aba "Metrics"
- **URL**: Aba "Settings" → "Domains"

## 🔄 Atualizar Deploy

Basta fazer push para o repositório GitHub e o Railway atualiza automaticamente!

## ⚠️ Importante

- O plano gratuito do Railway tem limite de horas/mês
- SQLite funciona mas é melhor usar PostgreSQL em produção
- Guarde as credenciais em segurança
