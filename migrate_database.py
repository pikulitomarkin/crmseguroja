"""
Script para migrar o banco de dados para o novo esquema de fluxos
"""
import sys
from sqlalchemy import create_engine, text, inspect
from config.settings import settings

def migrate_database():
    """Adiciona novas colunas ao banco de dados existente"""
    
    print("🔄 Iniciando migração do banco de dados...")
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            inspector = inspect(engine)
            existing_columns = [col['name'] for col in inspector.get_columns('leads')]
            
            print(f"✅ Banco conectado. Colunas existentes: {len(existing_columns)}")
            
            # Lista de novas colunas a adicionar
            new_columns = [
                ("second_email", "VARCHAR(150)"),
                ("flow_type", "VARCHAR(50)"),
                ("flow_step", "VARCHAR(50) DEFAULT 'menu_principal'"),
                ("vehicle_plate", "VARCHAR(10)"),
                ("cep_pernoite", "VARCHAR(10)"),
                ("profession", "VARCHAR(150)"),
                ("marital_status", "VARCHAR(50)"),
                ("vehicle_usage", "VARCHAR(50)"),
                ("has_young_driver", "BOOLEAN"),
                ("property_cep", "VARCHAR(10)"),
                ("property_type", "VARCHAR(100)"),
                ("property_value", "VARCHAR(100)"),
                ("property_ownership", "VARCHAR(50)"),
                ("consortium_type", "VARCHAR(50)"),
                ("consortium_value", "VARCHAR(100)"),
                ("consortium_term", "VARCHAR(50)"),
                ("has_previous_consortium", "BOOLEAN"),
            ]
            
            columns_added = 0
            columns_skipped = 0
            
            for column_name, column_type in new_columns:
                if column_name in existing_columns:
                    print(f"⏭️  Coluna '{column_name}' já existe, pulando...")
                    columns_skipped += 1
                else:
                    try:
                        # SQLite usa sintaxe diferente para ADD COLUMN
                        sql = f"ALTER TABLE leads ADD COLUMN {column_name} {column_type}"
                        conn.execute(text(sql))
                        conn.commit()
                        print(f"✅ Coluna '{column_name}' adicionada com sucesso")
                        columns_added += 1
                    except Exception as e:
                        print(f"❌ Erro ao adicionar coluna '{column_name}': {str(e)}")
            
            print(f"\n📊 Resumo da migração:")
            print(f"   ✅ Colunas adicionadas: {columns_added}")
            print(f"   ⏭️  Colunas já existentes: {columns_skipped}")
            print(f"\n🎉 Migração concluída com sucesso!")
            
    except Exception as e:
        print(f"\n❌ Erro na migração: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    migrate_database()
