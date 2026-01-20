# 🤖 Configuração OpenAI

O projeto foi atualizado para usar **OpenAI** (GPT-4o) ao invés do Claude.

## 📋 Pré-requisitos

1. **Conta OpenAI**: Crie em [platform.openai.com/signup](https://platform.openai.com/signup)
2. **Créditos**: Adicione créditos à sua conta OpenAI

## 🔑 Obtendo sua API Key

1. Acesse: https://platform.openai.com/api-keys
2. Clique em **"Create new secret key"**
3. Dê um nome (ex: "CRM WhatsApp")
4. Copie a chave (começa com `sk-proj-...`)
5. ⚠️ **IMPORTANTE**: Guarde a chave em local seguro, ela só aparece uma vez!

## ⚙️ Configuração do Projeto

### 1. Configure o arquivo .env

Crie um arquivo `.env` na raiz do projeto (se não existir):

```bash
# Copie o .env.example
Copy-Item .env.example .env
```

### 2. Edite o arquivo .env

Abra o arquivo `.env` e configure:

```env
# OpenAI API
OPENAI_API_KEY=sk-proj-sua_chave_aqui
OPENAI_MODEL=gpt-4o

# Outras configurações...
EVOLUTION_API_KEY=sua_chave_evolution
EVOLUTION_API_URL=https://api.evolution.br/api
EVOLUTION_INSTANCE_NAME=sua_instancia
```

### 3. Modelos Disponíveis

Você pode escolher entre os modelos:

- **`gpt-4o`** (recomendado) - Mais inteligente e rápido
- **`gpt-4o-mini`** - Mais econômico
- **`gpt-4-turbo`** - Versão turbo do GPT-4
- **`gpt-3.5-turbo`** - Mais barato, mas menos capaz

## 📦 Instalação das Dependências

Instale o pacote OpenAI:

```powershell
pip install -r requirements.txt
```

## ✅ Teste a Configuração

Execute o script de teste:

```powershell
python test_system.py
```

Você deve ver:

```
🤖 TESTANDO OPENAI API...
--------------------------------------------------
✅ OpenAI respondeu:
   Olá! Sou um assistente...
```

## 💰 Custos Estimados

### GPT-4o (Recomendado)
- Input: $5.00 / 1M tokens
- Output: $15.00 / 1M tokens
- Estimativa: ~$0.01 por conversa de 10 mensagens

### GPT-4o-mini (Econômico)
- Input: $0.15 / 1M tokens
- Output: $0.60 / 1M tokens
- Estimativa: ~$0.0003 por conversa de 10 mensagens

### GPT-3.5-turbo
- Input: $0.50 / 1M tokens
- Output: $1.50 / 1M tokens
- Estimativa: ~$0.002 por conversa de 10 mensagens

## 🔧 Arquivos Atualizados

Os seguintes arquivos foram modificados para usar OpenAI:

- ✅ `config/settings.py` - Configurações da API
- ✅ `app/services/ai_service.py` - Serviço OpenAI (antes claude_service.py)
- ✅ `app/webhooks/evolution_webhook.py` - Integração webhook
- ✅ `app/core/qualification.py` - Motor de qualificação
- ✅ `requirements.txt` - Dependências atualizadas

## 🚀 Execução

Após configurar, execute o projeto:

```powershell
python run.py
```

## ❓ Troubleshooting

### Erro: "Invalid API Key"
- Verifique se copiou a chave corretamente
- Certifique-se de que a chave está ativa em: https://platform.openai.com/api-keys

### Erro: "Insufficient credits"
- Adicione créditos em: https://platform.openai.com/account/billing

### Erro: "Rate limit exceeded"
- Você atingiu o limite de requisições
- Aguarde alguns minutos ou aumente o limite na sua conta

## 📚 Documentação Oficial

- OpenAI Platform: https://platform.openai.com
- API Reference: https://platform.openai.com/docs/api-reference
- Pricing: https://openai.com/pricing

## 🆘 Suporte

Se precisar de ajuda:
1. Verifique os logs em tempo real
2. Teste a API Key com o `test_system.py`
3. Consulte a documentação oficial da OpenAI
