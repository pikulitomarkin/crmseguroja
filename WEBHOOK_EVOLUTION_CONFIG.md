# Configuração do Webhook Evolution API

## ⚠️ PROBLEMA IDENTIFICADO

Baseado nos logs do Evolution API, o webhook **NÃO está recebendo os eventos** porque:

1. As mensagens estão chegando na Evolution API (logs confirmam)
2. Mas os eventos **NÃO estão sendo enviados para o webhook** (falta requisição HTTP nos logs)
3. O Evolution API está processando mensagens internamente mas não disparando o webhook

## 📋 CORREÇÕES APLICADAS NO CÓDIGO

✅ Webhook agora aceita tanto `messages.upsert` quanto `messages.update`  
✅ Filtro adicionado para ignorar atualizações de status (apenas leitura/entrega)  
✅ Logs detalhados para identificar tipo de evento recebido

## 🔧 VERIFICAR CONFIGURAÇÃO NA EVOLUTION API

### 1. Verificar se o Webhook está Configurado

Acesse a Evolution API e verifique:

**URL do webhook deve ser:**
```
https://seu-dominio-railway.up.railway.app/webhook/evolution
```

### 2. Eventos que DEVEM estar habilitados

No Evolution API, certifique-se de que estes eventos estão marcados:

- ✅ `MESSAGES_UPSERT` (novo mensagem)
- ✅ `MESSAGES_UPDATE` (atualização de mensagem)
- ❌ `MESSAGES_DELETE` (opcional)

### 3. Comandos cURL para Configurar o Webhook

Use estes comandos para configurar via API:

#### A. Listar instâncias
```bash
curl -X GET "https://api.evolution.com.br/instance/fetchInstances" \
  -H "apikey: SUA_API_KEY_EVOLUTION"
```

#### B. Verificar webhook da instância
```bash
curl -X GET "https://api.evolution.com.br/webhook/find/NOME_DA_INSTANCIA" \
  -H "apikey: SUA_API_KEY_EVOLUTION"
```

#### C. Configurar/Atualizar webhook
```bash
curl -X POST "https://api.evolution.com.br/webhook/set/seguroja" \
  -H "Content-Type: application/json" \
  -H "apikey: SUA_API_KEY_EVOLUTION" \
  -d '{
    "url": "https://crmseguroja-production.up.railway.app/webhook/evolution",
    "webhook_by_events": false,
    "webhook_base64": false,
    "events": [
      "MESSAGES_UPSERT",
      "MESSAGES_UPDATE"
    ]
  }'
```

**IMPORTANTE:**
- Substitua `SUA_API_KEY_EVOLUTION` pela API key real
- Substitua `seguroja` pelo nome da sua instância
- Substitua a URL pelo seu domínio Railway

### 4. Teste com Webhook de Debug

Para capturar TODOS os eventos (debug), você pode temporariamente usar:

```bash
curl -X POST "https://api.evolution.com.br/webhook/set/seguroja" \
  -H "Content-Type: application/json" \
  -H "apikey: SUA_API_KEY_EVOLUTION" \
  -d '{
    "url": "https://crmseguroja-production.up.railway.app/webhook/evolution/debug",
    "webhook_by_events": false,
    "webhook_base64": false,
    "events": [
      "MESSAGES_UPSERT",
      "MESSAGES_UPDATE",
      "CONNECTION_UPDATE",
      "QRCODE_UPDATED"
    ]
  }'
```

Depois acesse:
```
https://crmseguroja-production.up.railway.app/webhook/evolution/debug/events
```

Para ver os últimos 20 eventos recebidos.

## 🧪 TESTAR O WEBHOOK

### 1. Enviar mensagem de teste

Envie uma mensagem para o número da Evolution API pelo WhatsApp:

```
Olá
```

### 2. Verificar logs no Railway

Nos logs do Railway você deve ver:

```
[WEBHOOK] Evento completo: messages.update
[WEBHOOK] ✅ Evento de mensagem recebido: messages.update
[NOTIFICATION] Enviando notificação WhatsApp para admin
```

### 3. Se NÃO aparecer nada nos logs

Significa que o webhook NÃO está configurado ou a URL está incorreta.

## 🔍 DIAGNÓSTICO PASSO A PASSO

1. ✅ **Código corrigido** (aceita messages.update)
2. ⏳ **Verificar configuração Evolution** (você precisa fazer)
3. ⏳ **Testar webhook** (enviar mensagem teste)
4. ⏳ **Ver logs Railway** (confirmar recebimento)

## 📞 PRÓXIMOS PASSOS

1. Execute o comando cURL da seção 3.C para configurar o webhook
2. Envie uma mensagem de teste para o WhatsApp
3. Verifique os logs do Railway
4. Se ainda não funcionar, use o endpoint de debug (seção 4) para capturar eventos

## 🆘 TROUBLESHOOTING

### Erro: "Cannot reach webhook URL"
- Verifique se a URL do Railway está correta
- Teste manualmente: `curl https://seu-app.up.railway.app/health`

### Erro: "Instance not found"
- Verifique o nome da instância com o comando da seção 3.A

### Nenhum evento chegando
- Use o webhook de debug (seção 4)
- Verifique se a instância está conectada no Evolution API
- Verifique os logs da Evolution API

## ⚡ INFORMAÇÕES ADICIONAIS

**Endpoint do webhook:** `/webhook/evolution`  
**Endpoint de debug:** `/webhook/evolution/debug`  
**Ver eventos capturados:** `/webhook/evolution/debug/events`  
**Health check:** `/health`

---

**Status atual:** Código corrigido ✅ | Aguardando configuração do webhook na Evolution API ⏳
