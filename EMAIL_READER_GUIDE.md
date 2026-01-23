# 📧 Sistema de Leitura de E-mails para Captura de Leads

## 📋 Visão Geral

O sistema agora **LÊ e-mails recebidos** automaticamente e captura leads relacionados a seguros/consórcios, notificando o admin via WhatsApp.

## 🔧 Como Funciona

### 1. **Monitoramento Contínuo**
- O sistema verifica periodicamente a caixa de entrada configurada
- Intervalo padrão: **5 minutos** (configurável)
- Processa apenas e-mails **não lidos**

### 2. **Detecção Inteligente**
- Identifica e-mails relacionados a seguros usando palavras-chave:
  - seguro, cotação, apólice, sinistro, consórcio
  - auto, veículo, residencial, imóvel, vida
  - etc.

### 3. **Processamento Automático**
- Extrai informações do remetente (nome e e-mail)
- Usa IA para extrair dados relevantes do conteúdo
- Cria lead automaticamente no banco de dados
- Salva o e-mail no histórico de conversas

### 4. **Notificação ao Admin**
- Envia mensagem via WhatsApp para o admin
- Inclui: nome, e-mail, assunto e preview do conteúdo
- Link para acessar o lead no dashboard

## ⚙️ Configuração

### 1. **Variáveis de Ambiente (.env)**

```env
# E-mail que será monitorado
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-de-app

# Servidor (detectado automaticamente)
SMTP_SERVER=smtp.gmail.com

# WhatsApp do admin (para notificações)
ADMIN_WHATSAPP=5511999999999

# Opcional: Configurações avançadas
EMAIL_CHECK_INTERVAL=5  # minutos entre verificações
EMAIL_MAX_PROCESS=10    # máximo de e-mails por verificação
```

### 2. **Gmail - Configuração Especial**

⚠️ **IMPORTANTE**: Gmail exige "senha de app" (não a senha normal)

**Passos:**
1. Acesse: https://myaccount.google.com/apppasswords
2. Crie uma nova senha de app
3. Use essa senha no `SMTP_PASSWORD`
4. Ative IMAP no Gmail:
   - Gmail → Configurações → Encaminhamento e POP/IMAP
   - Marque "Ativar IMAP"

### 3. **Outlook/Hotmail**
- Use sua senha normal
- Servidor detectado automaticamente

### 4. **Yahoo**
- Pode exigir senha de app
- Servidor detectado automaticamente

## 🚀 Execução

### **Opção 1: Integrado ao Sistema (Recomendado)**

O scheduler de e-mails é iniciado **automaticamente** quando você roda o sistema principal:

```bash
python run.py
```

O sistema irá:
- ✅ Iniciar o servidor FastAPI (webhooks)
- ✅ Iniciar o scheduler de e-mails (verificação a cada 24h)
- ✅ Executar a primeira verificação imediatamente
- ✅ Continuar verificando a cada 24 horas automaticamente

**Verificar Status:**
```bash
# Acesse no navegador ou via curl:
http://localhost:8000/api/email/status
```

**Forçar Verificação Imediata:**
```bash
# Via API:
curl -X POST http://localhost:8000/api/email/check-now
```

### **Opção 2: Modo Standalone (24h automático)**

Se preferir rodar apenas o monitor de e-mails (sem webhooks):

```bash
python email_monitor_24h.py
```

Isso vai:
- ✅ Verificar e-mails imediatamente
- ✅ Verificar novamente a cada 24 horas
- ✅ Rodar continuamente em loop
- ✅ Notificar admin via WhatsApp quando encontrar leads

**Para rodar em background:**

Linux/Mac:
```bash
nohup python email_monitor_24h.py > email_monitor.log 2>&1 &
```

Windows PowerShell:
```powershell
Start-Process python -ArgumentList "email_monitor_24h.py" -WindowStyle Hidden
```

### **Opção 3: Verificação Manual (Testes)**

Para testar ou fazer verificações pontuais:

```bash
# Teste de conexão
python test_email_connection.py

# Processar e-mails uma vez
python email_monitor.py --once

# Processar com intervalo customizado (minutos)
python email_monitor.py --interval 30
```

## 📊 Fluxo Completo

```
1. E-mail chega na caixa de entrada
         ⬇️
2. Sistema verifica a cada 5 minutos
         ⬇️
3. Detecta se é sobre seguro/consórcio
         ⬇️
4. Extrai: nome, e-mail, assunto, conteúdo
         ⬇️
5. Usa IA para extrair dados estruturados
         ⬇️
6. Cria lead no banco de dados
         ⬇️
7. Notifica admin via WhatsApp
         ⬇️
8. Admin pode responder diretamente ao cliente
```

## 🔍 Logs e Monitoramento

O sistema gera logs detalhados:

```bash
# Ver logs em tempo real
python email_monitor.py

# Logs mostram:
# - E-mails verificados
# - E-mails processados
# - Leads criados
# - Notificações enviadas
# - Erros (se houver)
```

## 🐛 Solução de Problemas

### ❌ "Erro de autenticação"
- **Gmail**: Use senha de app, não senha normal
- Verifique se SMTP_USER e SMTP_PASSWORD estão corretos
- Verifique se IMAP está ativado

### ❌ "Não foi possível conectar"
- Verifique sua conexão com internet
- Alguns firewalls bloqueiam IMAP
- Tente mudar servidor IMAP manualmente

### ❌ "Nenhum e-mail processado"
- Verifique se há e-mails NÃO LIDOS
- Verifique se contêm palavras-chave relacionadas a seguros
- Use `--once` para testar

### ❌ "Admin não recebe notificação"
- Verifique se ADMIN_WHATSAPP está configurado corretamente
- Formato: 5511999999999 (com DDI + DDD + número)
- Verifique se Evolution API está funcionando

## 📝 Palavras-Chave Detectadas

O sistema busca estas palavras no assunto e corpo:

```
seguro, cotação, cotacao, orçamento, orcamento
apólice, apolice, sinistro, indenização
cobertura, prêmio, premio, franquia
consórcio, consorcio, carta de crédito
auto, veículo, veiculo, carro, moto
residencial, imóvel, imovel, casa, apartamento
vida, acidentes pessoais
proposta, renovação, renovacao
seguro já, seguro ja
```

## 🎯 Exemplo de Notificação ao Admin

Quando um e-mail é processado, o admin recebe:

```
🔔 NOVO LEAD VIA E-MAIL

📧 E-mail: cliente@example.com
👤 Nome: João Silva
📋 Assunto: Cotação de Seguro Auto

Preview:
Olá, gostaria de uma cotação para 
seguro do meu veículo Fiat Uno 2020...

---
💡 Lead capturado automaticamente do e-mail
🆔 ID do Lead: 42
```

## 🔒 Segurança

- ✅ Senhas armazenadas em `.env` (nunca no código)
- ✅ Conexão IMAP usa SSL/TLS
- ✅ E-mails não são deletados, apenas marcados como lidos
- ✅ Dados sensíveis não são logados

## 📈 Próximos Passos

Após configurar:

1. **Teste a conexão**: `python test_email_connection.py`
2. **Teste processamento**: `python email_monitor.py --once`
3. **Inicie monitoramento**: `python email_monitor.py`
4. **Configure em produção**: Adicione ao Procfile/systemd

## 💡 Dicas

- Configure um e-mail específico para receber leads
- Use filtros no Gmail para organizar e-mails
- Monitore os logs regularmente
- Ajuste intervalo de verificação conforme necessidade
- Teste com e-mails reais antes de colocar em produção

## 🆘 Suporte

Se tiver problemas:
1. Execute `python test_email_connection.py`
2. Verifique os logs
3. Confirme configurações no `.env`
4. Teste com `--once` antes de rodar continuamente
