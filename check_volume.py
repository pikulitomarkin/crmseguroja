#!/usr/bin/env python3
"""
Script para verificar e configurar o volume persistente
"""
import os
import sys
from pathlib import Path

def check_and_setup_volume():
    """Verifica e configura o volume persistente"""
    
    # Verifica se estamos no Railway
    is_railway = os.getenv("RAILWAY_ENVIRONMENT") is not None
    
    # Define o caminho do volume
    volume_path = Path("/app/data")
    db_file = volume_path / "crm_system.db"
    
    print("=" * 60)
    print("🔍 VERIFICAÇÃO DE VOLUME PERSISTENTE")
    print("=" * 60)
    
    print(f"\n📍 Ambiente: {'Railway' if is_railway else 'Local'}")
    print(f"📁 Caminho do volume: {volume_path}")
    print(f"💾 Arquivo do banco: {db_file}")
    
    # Verifica se o diretório existe
    if volume_path.exists():
        print(f"\n✅ Volume encontrado: {volume_path}")
        print(f"   Permissões: {oct(volume_path.stat().st_mode)[-3:]}")
        print(f"   Espaço livre: {get_free_space(volume_path)}")
        
        # Lista conteúdo
        contents = list(volume_path.iterdir())
        if contents:
            print(f"\n📂 Conteúdo do volume ({len(contents)} itens):")
            for item in contents[:10]:  # Mostra até 10 itens
                size = item.stat().st_size if item.is_file() else 0
                print(f"   - {item.name} ({format_size(size)})")
        else:
            print("\n📂 Volume vazio (primeira execução)")
            
        # Verifica banco de dados
        if db_file.exists():
            size = db_file.stat().st_size
            print(f"\n✅ Banco de dados encontrado: {format_size(size)}")
        else:
            print("\n⚠️  Banco de dados não encontrado (será criado)")
            
    else:
        print(f"\n❌ Volume não encontrado: {volume_path}")
        print("   Usando banco local: ./crm_system.db")
        
        if is_railway:
            print("\n⚠️  ATENÇÃO: No Railway mas sem volume configurado!")
            print("   Configure o volume seguindo as instruções em VOLUME_SETUP.md")
    
    print("\n" + "=" * 60)
    
    return volume_path.exists()


def get_free_space(path):
    """Retorna espaço livre no volume"""
    try:
        stat = os.statvfs(path)
        free = stat.f_bavail * stat.f_frsize
        total = stat.f_blocks * stat.f_frsize
        used = total - free
        percent = (used / total) * 100 if total > 0 else 0
        return f"{format_size(free)} livre de {format_size(total)} ({percent:.1f}% usado)"
    except:
        return "N/A"


def format_size(bytes):
    """Formata tamanho em bytes para formato legível"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} TB"


if __name__ == "__main__":
    has_volume = check_and_setup_volume()
    sys.exit(0 if has_volume or not os.getenv("RAILWAY_ENVIRONMENT") else 1)
