"""
Script de configuração rápida
Guia passo a passo para configurar o sistema
"""

import os
import sys
from pathlib import Path

def clear_screen():
    """Limpa a tela"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(text):
    """Imprime um cabeçalho"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def print_step(number, text):
    """Imprime um passo"""
    print(f"📍 PASSO {number}: {text}")
    print("-" * 70)


def setup_wizard():
    """Wizard interativo de configuração"""
    
    clear_screen()
    print_header("🚀 SETUP WIZARD - CRM WHATSAPP SYSTEM")
    
    # Verificar .env
    print_step(1, "Verificar arquivo .env")
    
    env_file = Path(".env")
    if env_file.exists():
        print("✅ Arquivo .env já existe")
        modify = input("Deseja reconfigurar? (s/n): ").lower()
        if modify != "s":
            proceed_to_install()
            return
    else:
        print("❌ Arquivo .env não encontrado")
        print("Criando a partir de .env.example...")
        
        if Path(".env.example").exists():
            with open(".env.example", "r") as f:
                template = f.read()
            with open(".env", "w") as f:
                f.write(template)
            print("✅ Arquivo .env criado com sucesso")
        else:
            print("❌ .env.example não encontrado!")
            sys.exit(1)
    
    # Configurar variáveis
    print_step(2, "Configurar Variáveis de Ambiente")
    
    config = {}
    
    print("\n🤖 ANTHROPIC (Claude)")
    config["ANTHROPIC_API_KEY"] = input("Cole sua ANTHROPIC_API_KEY: ").strip()
    
    print("\n📱 EVOLUTION API (WhatsApp)")
    config["EVOLUTION_API_URL"] = input("Evolution API URL [https://api.evolution.br/api]: ").strip()
    config["EVOLUTION_API_URL"] = config["EVOLUTION_API_URL"] or "https://api.evolution.br/api"
    config["EVOLUTION_API_KEY"] = input("Evolution API Key: ").strip()
    config["EVOLUTION_INSTANCE_NAME"] = input("Evolution Instance Name: ").strip()
    
    print("\n📧 EMAIL (SMTP)")
    print("Exemplo: Gmail")
    print("  SMTP Server: smtp.gmail.com")
    print("  Port: 587")
    print("  Para Gmail, gerar 'Senha de App' em: https://myaccount.google.com/apppasswords")
    
    config["SMTP_USER"] = input("Email (SMTP_USER): ").strip()
    config["SMTP_PASSWORD"] = input("Senha do app (SMTP_PASSWORD): ").strip()
    config["EMAIL_FROM"] = input("Email de origem [mesmo email]: ").strip() or config["SMTP_USER"]
    
    print("\n👨‍💼 ADMIN")
    config["ADMIN_EMAIL"] = input("Email do admin: ").strip()
    config["ADMIN_WHATSAPP"] = input("WhatsApp do admin (formato: 5511999999999): ").strip()
    
    print("\n💾 DATABASE")
    db_choice = input("SQLite (padrão) ou PostgreSQL? (sqlite/postgres): ").lower().strip()
    
    if db_choice == "postgres":
        db_host = input("Host [localhost]: ").strip() or "localhost"
        db_user = input("Usuário [crm_user]: ").strip() or "crm_user"
        db_pass = input("Senha: ").strip()
        db_name = input("Nome do banco [crm_db]: ").strip() or "crm_db"
        config["DATABASE_URL"] = f"postgresql://{db_user}:{db_pass}@{db_host}/{db_name}"
    else:
        config["DATABASE_URL"] = "sqlite:///./crm_system.db"
    
    # Salvar configuração
    print_step(3, "Salvar Configuração")
    
    with open(".env", "r") as f:
        content = f.read()
    
    for key, value in config.items():
        if value:
            # Substituir variável existente
            lines = content.split("\n")
            new_lines = []
            found = False
            
            for line in lines:
                if line.startswith(f"{key}="):
                    new_lines.append(f"{key}={value}")
                    found = True
                else:
                    new_lines.append(line)
            
            if not found:
                new_lines.append(f"{key}={value}")
            
            content = "\n".join(new_lines)
    
    with open(".env", "w") as f:
        f.write(content)
    
    print("✅ Configuração salva em .env")
    
    # Testar conexões
    print_step(4, "Testar Conexões")
    
    test = input("Deseja testar as conexões agora? (s/n): ").lower()
    if test == "s":
        os.system(f"{sys.executable} test_system.py")
    
    proceed_to_install()


def proceed_to_install():
    """Próximos passos"""
    
    print_header("✅ CONFIGURAÇÃO CONCLUÍDA")
    
    print("""
📍 PRÓXIMOS PASSOS:

1. INSTALAR DEPENDÊNCIAS (se não fez)
   pip install -r requirements.txt

2. INICIALIZAR BANCO DE DADOS
   python app/__init__.py

3. INICIAR O SISTEMA

   Terminal 1 - Webhook FastAPI:
   python -m uvicorn app.webhooks.evolution_webhook:app --reload

   Terminal 2 - Dashboard Streamlit:
   streamlit run dashboard/app.py

4. ACESSAR

   Dashboard: http://localhost:8501
   API Docs: http://localhost:8000/docs
   Webhook: http://localhost:8000/webhook/evolution

5. CONFIGURAR WEBHOOK NA EVOLUTION API
   
   URL: http://seu-dominio.com/webhook/evolution
   Método: POST
   Evento: MESSAGES_UPSERT

   (Para dev local, use ngrok)

6. TESTAR
   python webhook_tests.py

---

DÚVIDAS?
- Veja README.md para documentação completa
- Veja DEPLOYMENT.md para deploy em produção
- Execute test_system.py para validar integrações

Boa sorte! 🚀
    """)


if __name__ == "__main__":
    try:
        setup_wizard()
    except KeyboardInterrupt:
        print("\n\n⛔ Setup cancelado pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Erro: {e}")
        sys.exit(1)
