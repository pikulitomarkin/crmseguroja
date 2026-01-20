#!/usr/bin/env python3
"""
Script para iniciar webhook e dashboard simultaneamente
"""
import os
import sys
import subprocess
import threading
import time

def start_dashboard():
    """Inicia o dashboard Streamlit em background"""
    dashboard_port = os.getenv("DASHBOARD_PORT", "8501")
    print(f"📊 Iniciando dashboard na porta {dashboard_port}...")
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit",
            "run", "dashboard/app.py",
            "--server.port", dashboard_port,
            "--server.address", "0.0.0.0",
            "--server.headless", "true",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false"
        ])
    except Exception as e:
        print(f"❌ Erro ao iniciar dashboard: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("🎯 CRM WhatsApp - Iniciando sistema completo")
    print("=" * 60)
    
    # Verifica volume persistente
    try:
        from check_volume import check_and_setup_volume
        print("\n🔍 Verificando volume persistente...")
        check_and_setup_volume()
    except Exception as e:
        print(f"⚠️  Aviso: Erro ao verificar volume: {e}")
    
    print()
    
    # Inicia dashboard em thread separada
    dashboard_thread = threading.Thread(target=start_dashboard, daemon=True)
    dashboard_thread.start()
    
    # Aguarda 3 segundos para dashboard iniciar
    time.sleep(3)
    
    # Inicia webhook no processo principal (Railway precisa disso)
    port = os.getenv("PORT", "8000")
    print(f"🚀 Iniciando webhook na porta {port}...")
    
    os.execvp(sys.executable, [
        sys.executable, "-m", "uvicorn",
        "app.webhooks.evolution_webhook:app",
        "--host", "0.0.0.0",
        "--port", port
    ])
