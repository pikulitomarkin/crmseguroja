#!/usr/bin/env python3
"""
Script de inicialização do banco de dados
Garante que o diretório do volume existe e cria o banco
"""
import os
import sys
from pathlib import Path
from config.settings import settings
from app.database.models import init_db

def main():
    """Inicializa o banco de dados no Railway"""
    print("=" * 60)
    print("Inicializando banco de dados...")
    print("=" * 60)
    
    # Detecta ambiente
    is_railway = os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("PORT")
    
    if is_railway:
        print("✓ Ambiente: Railway (produção)")
        data_dir = Path("/app/data")
        
        # Cria diretório se não existir
        if not data_dir.exists():
            print(f"✓ Criando diretório: {data_dir}")
            data_dir.mkdir(parents=True, exist_ok=True)
        else:
            print(f"✓ Diretório existe: {data_dir}")
        
        # Verifica permissões
        if os.access(data_dir, os.W_OK):
            print(f"✓ Permissão de escrita: OK")
        else:
            print(f"✗ ERRO: Sem permissão de escrita em {data_dir}")
            sys.exit(1)
        
        # Lista conteúdo do diretório
        contents = list(data_dir.iterdir())
        if contents:
            print(f"✓ Arquivos em {data_dir}:")
            for item in contents:
                size = item.stat().st_size if item.is_file() else 0
                print(f"  - {item.name} ({size:,} bytes)")
        else:
            print(f"✓ Diretório vazio (primeira inicialização)")
    else:
        print("✓ Ambiente: Local (desenvolvimento)")
    
    # Mostra configuração do banco
    print(f"\n✓ Database URL: {settings.DATABASE_URL}")
    print(f"✓ Database Path: {settings.db_path}")
    
    # Inicializa banco de dados
    try:
        # Verifica se o banco já existe
        db_file = Path(settings.db_path)
        db_exists = db_file.exists()
        
        if db_exists:
            db_size = db_file.stat().st_size
            print(f"✓ Banco de dados EXISTENTE encontrado: {db_file}")
            print(f"✓ Tamanho do arquivo: {db_size:,} bytes")
        else:
            print(f"✓ Criando NOVO banco de dados: {db_file}")
        
        engine = init_db(settings.DATABASE_URL)
        
        if db_exists:
            print("✓ Banco de dados conectado (dados preservados)")
        else:
            print("✓ Banco de dados criado com sucesso!")
        
        # Testa conexão e conta registros
        from sqlalchemy import text
        from app.database.models import get_session, Lead
        db = get_session(engine)
        
        # Conta leads existentes
        lead_count = db.query(Lead).count()
        print(f"✓ Leads no banco: {lead_count}")
        
        db.execute(text("SELECT 1"))
        db.close()
        print("✓ Teste de conexão: OK")
        
    except Exception as e:
        print(f"✗ ERRO ao inicializar banco: {str(e)}")
        sys.exit(1)
    
    print("=" * 60)
    print("✓ Inicialização concluída com sucesso!")
    print("=" * 60)

if __name__ == "__main__":
    main()
