# Novo Sistema de Fluxos de Atendimento - Seguro Já

## 📋 Resumo das Mudanças

O sistema foi completamente reestruturado para implementar fluxos de atendimento específicos por tipo de produto e serviço.

## 🔄 Principais Alterações

### 1. **Modelo de Dados (models.py)**
Novos campos adicionados à tabela `leads`:
- `flow_type`: Tipo de fluxo atual (seguro_auto, consorcio, etc)
- `flow_step`: Etapa atual do fluxo (menu_principal, escolher_seguro, etc)
- `second_email`: Segundo e-mail opcional
- Campos específicos para **Seguro Auto**: cpf_cnpj, vehicle_plate, phone, whatsapp_contact, cep_pernoite, profession, marital_status, vehicle_usage, has_young_driver
- Campos específicos para **Seguro Residencial**: property_cep, property_type, property_value, property_ownership
- Campos específicos para **Consórcio**: consortium_type, consortium_value, consortium_term, has_previous_consortium

### 2. **Sistema de Prompts (prompts.py)**
Criados prompts específicos para cada etapa:
- `PROMPT_MENU_PRINCIPAL`: Menu inicial com 6 opções
- `PROMPT_SEGURO_AUTO`: Coleta dados para seguro auto
- `PROMPT_SEGURO_RESIDENCIAL`: Coleta dados para seguro residencial
- `PROMPT_CONSORCIO`: Coleta dados para consórcio
- `PROMPT_SEGUNDA_VIA`: Atendimento rápido para boletos
- `PROMPT_SINISTRO`: Atendimento prioritário para sinistros
- `PROMPT_FALAR_HUMANO`: Transferência direta
- `PROMPT_OUTROS_ASSUNTOS`: Atendimento genérico

### 3. **Gerenciador de Fluxos (flow_manager.py)** - NOVO
Arquivo criado para gerenciar navegação entre fluxos:
- Detecta escolhas do menu (números ou palavras-chave)
- Detecta tipo de seguro escolhido
- Detecta tipo de consórcio escolhido
- Extrai campos específicos (CPF, placa, CEP, etc)
- Determina próximo campo a coletar
- Verifica se fluxo está completo

### 4. **Engine de Qualificação (qualification.py)**
Atualizado para trabalhar com novo sistema:
- Compatibilidade mantida com sistema antigo
- Suporte aos novos fluxos
- Verificação de conclusão por tipo de fluxo

### 5. **Serviço de IA (ai_service.py)**
Novos métodos:
- `get_response()`: Agora recebe `flow_step` em vez de `customer_type`
- `extract_lead_data_from_conversation()`: Novo método para extrair dados específicos por tipo de fluxo

### 6. **Webhook Principal (evolution_webhook.py)**
Lógica de processamento completamente reescrita:
- Gerenciamento de navegação entre etapas
- Detecção automática de escolhas do usuário
- Extração contextual de dados
- Transferência inteligente para humanos

## 📱 Fluxos Implementados

### **Menu Principal**
```
1️⃣ Seguro
2️⃣ Consórcio
3️⃣ Segunda via de boleto
4️⃣ Sinistro
5️⃣ Falar com um humano
6️⃣ Outros assuntos
```

### **Fluxo: Seguro Auto**
1. Nome
2. CPF/CNPJ
3. Placa do veículo
4. Telefone
5. WhatsApp
6. Segundo e-mail (opcional)
7. CEP de pernoite
8. Profissão
9. Estado civil
10. Uso do veículo (particular/trabalho)
11. Condutor menor de 26 anos (sim/não)

### **Fluxo: Seguro Residencial**
1. Nome
2. Telefone/WhatsApp
3. CEP do imóvel
4. Tipo de imóvel
5. Valor aproximado
6. Próprio ou alugado

### **Fluxo: Consórcio**
1. Tipo (Auto/Imóvel/Serviço)
2. CPF/CNPJ
3. Telefone
4. WhatsApp
5. E-mail principal
6. Segundo e-mail (opcional)
7. Valor da carta de crédito
8. Prazo (meses)
9. Já participou antes? (opcional)

### **Fluxos Rápidos**
- **Segunda Via**: CPF/CNPJ → Transfere para humano
- **Sinistro**: Nome + Telefone + Tipo → Transfere IMEDIATAMENTE
- **Falar com Humano**: Transfere direto
- **Outros Assuntos**: Deixa falar → Transfere

## 🚀 Como Usar

### 1. **Migrar o Banco de Dados**
```bash
python migrate_database.py
```

### 2. **Reiniciar o Sistema**
```bash
python run.py
```

### 3. **Testar os Fluxos**
Envie mensagens via WhatsApp:
- "1" ou "seguro" → Acessa menu de seguros
- "2" ou "consórcio" → Inicia fluxo de consórcio
- "4" ou "sinistro" → Atendimento prioritário
- etc.

## ⚙️ Configurações Importantes

### Regras de Negócio
- ✅ Perguntas feitas UMA por vez
- ✅ Não avança sem resposta
- ✅ Não discute preços
- ✅ Emojis moderados
- ✅ Respostas curtas (máx 2 linhas)
- ✅ Transferência automática ao completar dados

### Transferência para Humano
Ocorre quando:
1. Todos os dados do fluxo foram coletados
2. Cliente escolheu "Falar com humano"
3. Fluxo de sinistro foi iniciado
4. Mais de 25 mensagens sem completar qualificação

## 📊 Estrutura de Dados

### Lead com Novo Schema
```python
{
    "id": 1,
    "whatsapp_number": "5511999999999",
    "flow_type": "seguro_auto",
    "flow_step": "seguro_auto",
    "name": "João Silva",
    "cpf_cnpj": "12345678900",
    "vehicle_plate": "ABC1234",
    "phone": "11999999999",
    "whatsapp_contact": "11999999999",
    "email": "joao@email.com",
    "cep_pernoite": "01234567",
    "profession": "Engenheiro",
    "marital_status": "Casado",
    "vehicle_usage": "particular",
    "has_young_driver": False,
    "status": "qualificado",
    "status_ia": 0  # IA desativada após transferir
}
```

## 🔧 Manutenção

### Adicionar Novo Fluxo
1. Adicionar prompt em `prompts.py`
2. Adicionar campos necessários em `models.py`
3. Atualizar `REQUIRED_FIELDS` em `flow_manager.py`
4. Adicionar lógica de detecção em `flow_manager.py`
5. Criar prompt de extração em `ai_service.py`

### Modificar Perguntas
Edite os prompts em `app/core/prompts.py`

### Alterar Campos Obrigatórios
Edite `REQUIRED_FIELDS` em `app/core/flow_manager.py`

## 📝 Arquivos Modificados

1. ✅ `app/database/models.py` - Novos campos
2. ✅ `app/core/prompts.py` - Sistema de prompts por fluxo
3. ✅ `app/core/flow_manager.py` - **NOVO** Gerenciador de fluxos
4. ✅ `app/core/qualification.py` - Compatibilidade com novos fluxos
5. ✅ `app/services/ai_service.py` - Novo método de extração
6. ✅ `app/webhooks/evolution_webhook.py` - Lógica de processamento reescrita
7. ✅ `migrate_database.py` - **NOVO** Script de migração

## ⚠️ Observações

- Sistema mantém compatibilidade com dados legados
- Mensagens antigas continuam funcionando
- Leads em andamento não são afetados
- Novos leads usam automaticamente o novo sistema

## 🎯 Próximos Passos

1. Testar todos os fluxos em produção
2. Coletar feedback dos atendentes
3. Ajustar prompts conforme necessário
4. Implementar mais tipos de seguro (vida, empresarial)
5. Adicionar validações adicionais (CPF, placa, etc)
