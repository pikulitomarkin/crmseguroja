"""
Script para testar a notificação do admin quando um email é recebido
"""
import asyncio
import logging
from datetime import datetime
from app.database.models import init_db, get_session, Lead
from app.services.email_reader_service import EmailReaderService
from config.settings import settings

# Configuração de logging detalhado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_email_notification():
    """Testa a notificação do admin sobre um email"""
    
    print("=" * 80)
    print("🧪 TESTE DE NOTIFICAÇÃO DE EMAIL PARA ADMIN")
    print("=" * 80)
    print()
    
    # Verifica configurações
    print("📋 VERIFICANDO CONFIGURAÇÕES:")
    print(f"   ADMIN_WHATSAPP: {settings.ADMIN_WHATSAPP}")
    print(f"   EVOLUTION_API_URL: {settings.EVOLUTION_API_URL}")
    print(f"   EVOLUTION_INSTANCE_NAME: {settings.EVOLUTION_INSTANCE_NAME}")
    print(f"   EVOLUTION_API_KEY: {'***' + settings.EVOLUTION_API_KEY[-4:] if settings.EVOLUTION_API_KEY else 'NÃO CONFIGURADO'}")
    print()
    
    if not settings.ADMIN_WHATSAPP:
        print("❌ ERRO: ADMIN_WHATSAPP não está configurado!")
        return False
    
    if not settings.EVOLUTION_API_KEY:
        print("❌ ERRO: EVOLUTION_API_KEY não está configurado!")
        return False
    
    # Inicializa banco de dados
    print("🗄️  Conectando ao banco de dados...")
    engine = init_db(settings.DATABASE_URL)
    db = get_session(engine)
    
    try:
        # Cria serviço de leitura
        email_service = EmailReaderService(db)
        
        # Cria um lead de teste
        print("📝 Criando lead de teste...")
        test_lead = Lead(
            whatsapp_number="email_test_123",
            name="Lead de Teste - Email",
            email="teste@example.com",
            status="novo",
            flow_type="email_inbound",
            flow_step="email_recebido",
            created_at=datetime.now()
        )
        db.add(test_lead)
        db.commit()
        db.refresh(test_lead)
        
        print(f"✅ Lead criado com ID: {test_lead.id}")
        print()
        
        # Testa notificação
        print("📨 TESTANDO NOTIFICAÇÃO PARA ADMIN...")
        print("-" * 80)
        
        subject = "Teste de Cotação de Seguro Auto"
        body_preview = "Olá, gostaria de uma cotação para seguro do meu carro placa ABC1234. Aguardo retorno."
        
        success = await email_service.notify_admin_about_email(
            test_lead,
            subject,
            body_preview
        )
        
        print("-" * 80)
        print()
        
        if success:
            print("✅ SUCESSO! Notificação enviada para o admin")
            print(f"📱 Número: {settings.ADMIN_WHATSAPP}")
            print()
            print("🔍 Verifique o WhatsApp do admin para confirmar o recebimento")
            return True
        else:
            print("❌ FALHA! Notificação NÃO foi enviada")
            print()
            print("🔍 Possíveis causas:")
            print("   1. Evolution API não está respondendo")
            print("   2. Instância do WhatsApp não está conectada")
            print("   3. Número do admin está incorreto")
            print("   4. Credenciais da Evolution API estão incorretas")
            return False
    
    except Exception as e:
        print(f"❌ ERRO durante o teste: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False
    
    finally:
        # Limpa lead de teste (opcional)
        try:
            if 'test_lead' in locals():
                print("🧹 Limpando lead de teste...")
                db.delete(test_lead)
                db.commit()
                print("✅ Lead de teste removido")
        except:
            pass
        
        db.close()


async def test_evolution_connection():
    """Testa conexão com Evolution API"""
    
    print()
    print("=" * 80)
    print("🔌 TESTANDO CONEXÃO COM EVOLUTION API")
    print("=" * 80)
    print()
    
    from app.services.evolution_service import EvolutionService
    
    evolution = EvolutionService()
    
    print(f"📡 URL: {evolution.base_url}")
    print(f"🔑 Instance: {evolution.instance_name}")
    print()
    
    # Tenta enviar mensagem de teste simples
    print("📨 Enviando mensagem de teste...")
    
    test_message = "🧪 Teste de conexão - CRM Sistema"
    
    try:
        success = await evolution.send_notification(
            settings.ADMIN_WHATSAPP,
            test_message
        )
        
        if success:
            print("✅ Mensagem de teste enviada com SUCESSO!")
            return True
        else:
            print("❌ FALHA ao enviar mensagem de teste")
            return False
    
    except Exception as e:
        print(f"❌ EXCEÇÃO ao testar conexão: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False


async def main():
    """Função principal"""
    
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "DIAGNÓSTICO COMPLETO DE EMAIL" + " " * 29 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    # Teste 1: Conexão com Evolution
    connection_ok = await test_evolution_connection()
    
    if not connection_ok:
        print()
        print("⚠️  A conexão com Evolution API falhou. Verifique as configurações.")
        print()
        return
    
    # Teste 2: Notificação de email
    await test_email_notification()
    
    print()
    print("=" * 80)
    print("🏁 TESTES CONCLUÍDOS")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
