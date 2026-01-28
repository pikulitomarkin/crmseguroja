# 🔍 DIAGNÓSTICO: Email recebido mas lead não enviado ao admin

## ❌ PROBLEMA IDENTIFICADO

**Status:** A Evolution API retorna erro 400 com mensagem "Connection Closed"

**Causa Raiz:** A instância do WhatsApp (`seguroja`) está **desconectada** da Evolution API

## 📊 Resultados dos Testes

```
[EVOLUTION] Response Status: 400
[EVOLUTION] Response Body: {"status":400,"error":"Bad Request","response":{"message":["Error: Connection Closed"]}}
```

### O que isso significa:

1. ✅ O código de leitura de email está funcionando corretamente
2. ✅ O lead está sendo criado no banco de dados
3. ✅ A configuração do ADMIN_WHATSAPP está correta: `5511983217785`
4. ✅ A URL da Evolution API está correta
5. ❌ **A instância do WhatsApp não está conectada**

## 🔧 CORREÇÕES IMPLEMENTADAS NO CÓDIGO

### 1. Melhor tratamento de erros em `email_reader_service.py`

**Antes:**
```python
await self.evolution.send_message(settings.ADMIN_WHATSAPP, message)
```

**Depois:**
```python
success = await self.evolution.send_notification(settings.ADMIN_WHATSAPP, message)
if success:
    logger.info(f"✅ Admin notificado com SUCESSO")
else:
    logger.error(f"❌ FALHA ao notificar admin")
```

### 2. Logs detalhados adicionados

- ✅ Log quando inicia a notificação
- ✅ Log do número do admin
- ✅ Log do tamanho da mensagem
- ✅ Log de sucesso/falha
- ✅ Traceback completo em caso de exceção

### 3. Validações adicionadas

- ✅ Verifica se ADMIN_WHATSAPP está configurado
- ✅ Retorna status de sucesso/falha
- ✅ Logs mais informativos

## ✅ SOLUÇÃO IMEDIATA

Para resolver o problema de notificação do admin, você precisa **reconectar a instância do WhatsApp**:

### Passo 1: Acessar a Evolution API

1. Acesse o painel da Evolution API
2. URL: `https://evolution-api-production-df00.up.railway.app`
3. Use suas credenciais de admin

### Passo 2: Verificar status da instância `seguroja`

1. Vá em "Instâncias"
2. Procure por "seguroja"
3. Verifique o status:
   - 🟢 **Conectado** = OK
   - 🔴 **Desconectado** = PROBLEMA

### Passo 3: Reconectar a instância

Se estiver desconectado:

1. Clique na instância `seguroja`
2. Clique em "Conectar" ou "Gerar QR Code"
3. Escaneie o QR Code com o WhatsApp
4. Aguarde a conexão

### Passo 4: Testar novamente

Execute o teste após reconectar:

```powershell
& "C:\crm whats\.venv\Scripts\python.exe" test_notification_simple.py
```

## 🎯 VERIFICAÇÃO ADICIONAL

### Testar manualmente a Evolution API

Use este comando para testar diretamente:

```powershell
curl -X POST "https://evolution-api-production-df00.up.railway.app/message/sendText/seguroja" `
  -H "Content-Type: application/json" `
  -H "apikey: SUA_API_KEY" `
  -d '{"number":"5511983217785","text":"Teste manual"}'
```

### Verificar logs da Evolution API

Se você tem acesso aos logs da Evolution API no Railway:

1. Acesse o painel do Railway
2. Vá para o serviço da Evolution API
3. Verifique os logs para mensagens de desconexão

## 📝 FLUXO CORRIGIDO

Agora o fluxo está assim:

```
1. Email recebido
   ↓
2. Email classificado pela IA (relevante?)
   ↓ SIM
3. Lead criado no banco de dados ✅
   ↓
4. Dados extraídos pela IA ✅
   ↓
5. Lead atualizado com dados ✅
   ↓
6. Histórico salvo ✅
   ↓
7. NOTIFICAÇÃO PARA ADMIN
   ├─ Verifica se ADMIN_WHATSAPP está configurado ✅
   ├─ Monta mensagem com dados do lead ✅
   ├─ Tenta enviar via Evolution API
   │  ├─ ❌ Connection Closed (WhatsApp desconectado)
   │  ├─ Log detalhado do erro ✅
   │  └─ Retorna falha ✅
   └─ Admin não recebe notificação
```

## 🚀 PRÓXIMOS PASSOS

1. **URGENTE:** Reconecte a instância do WhatsApp na Evolution API
2. **TESTE:** Execute `test_notification_simple.py` novamente
3. **MONITORE:** Verifique se novos emails estão gerando notificações
4. **CONSIDERE:** Implementar um webhook de status da Evolution para alertar quando desconectar

## 🛡️ PREVENÇÃO

Para evitar este problema no futuro:

1. **Monitor de Conexão:** Criar script que verifica status da instância periodicamente
2. **Alertas:** Configurar alerta quando a instância desconectar
3. **Auto-Reconexão:** Implementar tentativas automáticas de reconexão
4. **Log Centralizado:** Enviar logs de falha para um sistema de monitoramento

## 📞 CONTATO

Se o problema persistir após reconectar:

1. Verifique se o número `5511983217785` está correto e no formato internacional
2. Confirme que a API Key está válida
3. Verifique se há limites de taxa na Evolution API
4. Teste com outro número para verificar se é específico do número do admin

---

**Data do diagnóstico:** 2026-01-28  
**Arquivos modificados:** `app/services/email_reader_service.py`  
**Scripts de teste criados:** `test_notification_simple.py`, `test_email_notification.py`
