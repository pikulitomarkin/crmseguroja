"""
Inicializar serviços de banco de dados
"""
import sys
from config.settings import settings
from app.database.models import init_db

if __name__ == "__main__":
    print(f"Inicializando banco de dados em: {settings.DATABASE_URL}")
    engine = init_db(settings.DATABASE_URL)
    print("✅ Banco de dados inicializado com sucesso!")
