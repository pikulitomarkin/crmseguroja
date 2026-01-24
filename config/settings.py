"""
Configurações do Sistema CRM
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Detecta se está no Railway
is_railway = os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("PORT")

if is_railway:
    # No Railway, sempre usa o volume
    data_dir = Path("/app/data")
    data_dir.mkdir(parents=True, exist_ok=True)
    DB_PATH_DEFAULT = str(data_dir / "crm_system.db")
else:
    # Localmente, usa o diretório atual
    DB_PATH_DEFAULT = "./crm_system.db"


class Settings:
    """Configurações centralizadas"""
    
    # Banco de Dados
    db_path = os.getenv("DB_PATH", DB_PATH_DEFAULT)
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{db_path}")
    
    # Evolution API
    EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL", "https://api.evolution.br/api")
    EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "")
    EVOLUTION_INSTANCE_NAME = os.getenv("EVOLUTION_INSTANCE_NAME", "")
    
    # OpenAI API
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")  # ou gpt-4o-mini, gpt-4-turbo, etc.
    
    # Email Configuration (Agora usado para LEITURA de e-mails)
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")  # E-mail que será monitorado
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")  # Senha de app (Gmail) ou senha normal
    EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@crmsystem.com")
    
    # Email Reader Configuration
    EMAIL_CHECK_INTERVAL = int(os.getenv("EMAIL_CHECK_INTERVAL", "5"))  # minutos
    EMAIL_MAX_PROCESS = int(os.getenv("EMAIL_MAX_PROCESS", "10"))  # máx e-mails por vez
    
    # Notificações
    ADMIN_WHATSAPP = os.getenv("ADMIN_WHATSAPP", "")  # Número do admin para receber notificações
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "")  # Email do admin
    
    # FastAPI
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("PORT", os.getenv("API_PORT", "8000")))  # Railway usa PORT
    API_WEBHOOK_PATH = os.getenv("API_WEBHOOK_PATH", "/webhook/evolution")
    
    # Streamlit
    STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", "8501"))
    
    # Sistema
    MAX_RETRIES = 3
    TYPING_DELAY = 0.5  # segundos para mostrar "digitando..." (reduzido para respostas mais rápidas)
    QUALIFICATION_COMPLETE_THRESHOLD = 0.8  # 80% dos campos preenchidos


settings = Settings()
