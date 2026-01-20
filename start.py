#!/usr/bin/env python3
"""
Script para iniciar webhook e dashboard simultaneamente
"""
import os
import sys
import subprocess
import signal
from multiprocessing import Process

def start_webhook():
    """Inicia o servidor webhook FastAPI"""
    port = os.getenv("PORT", "8000")
    print(f"🚀 Iniciando webhook na porta {port}...")
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "app.webhooks.evolution_webhook:app",
        "--host", "0.0.0.0",
        "--port", port
    ])

def start_dashboard():
    """Inicia o dashboard Streamlit"""
    dashboard_port = os.getenv("DASHBOARD_PORT", "8501")
    print(f"📊 Iniciando dashboard na porta {dashboard_port}...")
    subprocess.run([
        sys.executable, "-m", "streamlit",
        "run", "dashboard/app.py",
        "--server.port", dashboard_port,
        "--server.address", "0.0.0.0",
        "--server.headless", "true"
    ])

if __name__ == "__main__":
    print("=" * 60)
    print("🎯 CRM WhatsApp - Iniciando sistema completo")
    print("=" * 60)
    
    # Inicia webhook em processo principal
    webhook_process = Process(target=start_webhook)
    
    # Inicia dashboard em processo separado
    dashboard_process = Process(target=start_dashboard)
    
    try:
        webhook_process.start()
        dashboard_process.start()
        
        # Aguarda os processos
        webhook_process.join()
        dashboard_process.join()
        
    except KeyboardInterrupt:
        print("\n🛑 Encerrando sistema...")
        webhook_process.terminate()
        dashboard_process.terminate()
        webhook_process.join()
        dashboard_process.join()
        sys.exit(0)
