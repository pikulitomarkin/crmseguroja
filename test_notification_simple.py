"""
Script simplificado para testar notificação admin
"""
import asyncio
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(__file__))

async def test_simple():
    """Teste simples de notificação"""
    
    print("\n" + "="*80)
    print("🧪 TESTE SIMPLIFICADO DE NOTIFICAÇÃO")
    print("="*80 + "\n")
    
    # Importa settings
    from config.settings import settings
    
    print("📋 Configurações:")
    print(f"   ADMIN_WHATSAPP: {settings.ADMIN_WHATSAPP}")
    print(f"   EVOLUTION_API_URL: {settings.EVOLUTION_API_URL}")
    print(f"   EVOLUTION_INSTANCE: {settings.EVOLUTION_INSTANCE_NAME}")
    print()
    
    if not settings.ADMIN_WHATSAPP:
        print("❌ ADMIN_WHATSAPP não configurado!")
        return
    
    if not settings.EVOLUTION_API_KEY:
        print("❌ EVOLUTION_API_KEY não configurado!")
        return
    
    # Testa Evolution Service
    from app.services.evolution_service import EvolutionService
    
    evolution = EvolutionService()
    
    print("📨 Enviando mensagem de teste...")
    print()
    
    test_message = """🧪 TESTE DE NOTIFICAÇÃO

Este é um teste do sistema de notificação de emails.

Se você recebeu esta mensagem, a integração está funcionando!"""
    
    try:
        success = await evolution.send_notification(
            settings.ADMIN_WHATSAPP,
            test_message
        )
        
        print()
        if success:
            print("✅ SUCESSO! Mensagem enviada")
            print(f"📱 Verifique o WhatsApp: {settings.ADMIN_WHATSAPP}")
        else:
            print("❌ FALHA ao enviar mensagem")
            print()
            print("🔍 Possíveis problemas:")
            print("   1. Evolution API não está online")
            print("   2. Instância não está conectada")
            print("   3. Número incorreto")
            
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("="*80)


if __name__ == "__main__":
    asyncio.run(test_simple())
