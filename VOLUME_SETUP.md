# Configuração de Volume Persistente no Railway

## 📦 Volume para Banco de Dados SQLite

O projeto está configurado para usar um volume persistente no Railway, garantindo que os dados do banco SQLite não sejam perdidos entre deploys.

## 🚀 Como Configurar no Railway

### Opção 1: Via railway.toml (Automático)
O arquivo `railway.toml` já está configurado com o volume:
```toml
[[deploy.volumes]]
mountPath = "/app/data"
name = "crm_data_volume"
```

O Railway irá criar automaticamente o volume no próximo deploy.

### Opção 2: Via Dashboard do Railway (Manual)

1. **Acesse o projeto no Railway Dashboard**
   - Vá para: https://railway.app
   - Selecione o projeto `crmseguroja-production`

2. **Configure o Volume**
   - Clique na aba **"Variables"**
   - Role até a seção **"Volumes"**
   - Clique em **"+ New Volume"**
   - Configure:
     - **Mount Path**: `/app/data`
     - **Size**: 1 GB (ou mais se necessário)

3. **Redeploy**
   - Após criar o volume, faça um redeploy do serviço
   - Os dados agora serão persistidos mesmo após novos deploys

## 📁 Estrutura de Dados

```
/app/data/
└── crm_system.db    # Banco SQLite persistente
```

## 🔍 Verificação

Para verificar se o volume está funcionando:

1. Acesse os logs do Railway
2. Procure por: `DATABASE_URL` 
3. Deve mostrar: `sqlite:////app/data/crm_system.db`

## 🔄 Backup

Para fazer backup do banco de dados:

1. Use o Railway CLI:
```bash
railway run cat /app/data/crm_system.db > backup.db
```

2. Ou baixe via SFTP se configurado

## ⚠️ Importante

- O volume é específico do serviço no Railway
- Dados persistem entre deploys, mas não entre serviços diferentes
- Considere fazer backups regulares
- O volume tem limite de tamanho (padrão: 1GB)

## 🔧 Troubleshooting

Se os dados não estiverem persistindo:

1. Verifique se o volume foi criado: Railway Dashboard > Service > Volumes
2. Verifique o mount path: `/app/data`
3. Verifique os logs: `railway logs`
4. Force um redeploy: `git commit --allow-empty -m "Force redeploy" && git push`

## 📊 Alternativas ao SQLite

Para produção com alto volume, considere:
- **PostgreSQL** (recomendado para Railway)
- **MySQL**
- **MongoDB**

O Railway oferece PostgreSQL como plugin com backup automático.
