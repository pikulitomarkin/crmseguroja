#!/usr/bin/env python
"""
Script para executar o sistema completo
Inicia tanto o webhook FastAPI quanto o dashboard Streamlit
"""
import subprocess
import sys
import os
from pathlib import Path

# Adiciona o diretório raiz ao path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

def main():
    print("=" * 60)
    print("🚀 CRM WhatsApp System - Iniciando...")
    print("=" * 60)
    
    # Verifica se .env existe
    env_file = root_dir / ".env"
    if not env_file.exists():
        print("\n⚠️  ATENÇÃO: Arquivo .env não encontrado!")
        print("   Copie .env.example para .env e configure suas chaves")
        print("   Comando: cp .env.example .env")
        sys.exit(1)
    
    print("\n✅ Arquivo .env encontrado")
    
    # Inicializa banco de dados
    print("\n📊 Inicializando banco de dados...")
    try:
        from config.settings import settings
        from app.database.models import init_db
        
        init_db(settings.DATABASE_URL)
        print("   ✅ Banco de dados pronto!")
    except Exception as e:
        print(f"   ❌ Erro ao inicializar banco: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎯 INICIALIZAR COMPONENTES")
    print("=" * 60)
    
    print("\nOpções:")
    print("1. Iniciar Webhook FastAPI (porta 8000)")
    print("2. Iniciar Dashboard Streamlit (porta 8501)")
    print("3. Iniciar ambos (recomendado - usa 2 terminais)")
    print("0. Sair")
    
    choice = input("\nEscolha uma opção (0-3): ").strip()
    
    if choice == "1":
        start_webhook()
    elif choice == "2":
        start_dashboard()
    elif choice == "3":
        print("\n⚠️  Abra dois terminais (PowerShell) e execute:")
        print("\nTerminal 1 - Webhook:")
        print("  python -m uvicorn app.webhooks.evolution_webhook:app --reload")
        print("\nTerminal 2 - Dashboard:")
        print("  streamlit run dashboard/app.py")
    else:
        print("Saindo...")
        sys.exit(0)


def start_webhook():
    """Inicia o servidor FastAPI"""
    print("\n🚀 Iniciando Webhook FastAPI...")
    print("   Acessível em: http://localhost:8000")
    print("   Docs em: http://localhost:8000/docs")
    print("   Webhook: POST http://localhost:8000/webhook/evolution")
    print("\n   Pressione CTRL+C para parar\n")
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "app.webhooks.evolution_webhook:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\n\n⛔ Webhook parado")


def start_dashboard():
    """Inicia o dashboard Streamlit"""
    print("\n🎨 Iniciando Dashboard Streamlit...")
    print("   Acessível em: http://localhost:8501")
    print("   Pressione CTRL+C para parar\n")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            "dashboard/app.py",
            "--logger.level=info"
        ])
    except KeyboardInterrupt:
        print("\n\n⛔ Dashboard parado")


if __name__ == "__main__":
    main()
