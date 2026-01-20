#!/usr/bin/env python
"""
Script para testar a integração com Evolution API e Claude
"""
import asyncio
import sys
from pathlib import Path

# Setup
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from config.settings import settings
from app.database.models import init_db, get_session
from app.services.ai_service import AIService
from app.services.evolution_service import EvolutionService
from app.services.notification_service import NotificationService
from app.services.database_service import LeadService, MessageService


async def test_openai():
    """Testa integração com OpenAI"""
    print("\n🤖 TESTANDO OPENAI API...")
    print("-" * 50)
    
    try:
        ai = AIService()
        
        # Teste 1: Mensagem simples
        response = ai.get_response(
            user_message="Olá! Qual é o seu nome?",
            conversation_history=[],
            customer_type="novo"
        )
        
        print("✅ OpenAI respondeu:")
        print(f"   {response[:100]}...")
        
        # Teste 2: Extração de dados
        conversation = [
            {"role": "user", "content": "Meu nome é João Silva"},
            {"role": "assistant", "content": "Prazer, João!"},
            {"role": "user", "content": "Preciso de um software de automação"},
        ]
        
        extracted = ai.extract_qualification_data(conversation)
        print(f"\n✅ Dados extraídos:")
        print(f"   Nome: {extracted.get('name')}")
        print(f"   Interesse: {extracted.get('interest')}")
        print(f"   Necessidade: {extracted.get('necessity')}")
        
        return True
    
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        print("   Verifique OPENAI_API_KEY em .env")
        return False


async def test_evolution():
    """Testa integração com Evolution API"""
    print("\n📱 TESTANDO EVOLUTION API...")
    print("-" * 50)
    
    try:
        evolution = EvolutionService()
        
        # Valida configuração
        if not settings.EVOLUTION_API_KEY:
            raise Exception("EVOLUTION_API_KEY não configurada")
        
        if not settings.EVOLUTION_INSTANCE_NAME:
            raise Exception("EVOLUTION_INSTANCE_NAME não configurada")
        
        print("✅ Configuração de Evolution API validada")
        print(f"   Instance: {settings.EVOLUTION_INSTANCE_NAME}")
        print(f"   API URL: {settings.EVOLUTION_API_URL}")
        
        # Nota: Não testamos send_message aqui pois precisaria de um número válido
        print("\n⚠️  Para testar envio de mensagens, use o webhook com um número real")
        
        return True
    
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False


def test_database():
    """Testa integração com banco de dados"""
    print("\n💾 TESTANDO BANCO DE DADOS...")
    print("-" * 50)
    
    try:
        # Inicializa BD
        engine = init_db(settings.DATABASE_URL)
        db = get_session(engine)
        
        # Testa criar lead
        test_number = "5511999999999"
        lead = LeadService.create_or_get_lead(db, test_number)
        
        print(f"✅ Lead criado/recuperado:")
        print(f"   ID: {lead.id}")
        print(f"   Número: {lead.whatsapp_number}")
        print(f"   Status: {lead.status}")
        
        # Testa salvar mensagem
        msg = MessageService.save_message(
            db, test_number, "user", "Mensagem de teste"
        )
        
        print(f"\n✅ Mensagem salva:")
        print(f"   ID: {msg.id}")
        print(f"   Conteúdo: {msg.message}")
        
        # Testa recuperar histórico
        history = MessageService.get_conversation_history(db, test_number)
        print(f"\n✅ Histórico recuperado: {len(history)} mensagens")
        
        db.close()
        return True
    
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False


def test_email():
    """Testa integração de Email"""
    print("\n📧 TESTANDO EMAIL...")
    print("-" * 50)
    
    try:
        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            raise Exception("SMTP_USER ou SMTP_PASSWORD não configurados")
        
        engine = init_db(settings.DATABASE_URL)
        db = get_session(engine)
        
        notif = NotificationService(db)
        
        print("✅ Configuração de email validada")
        print(f"   SMTP: {settings.SMTP_SERVER}:{settings.SMTP_PORT}")
        print(f"   Usuário: {settings.SMTP_USER}")
        
        # Nota: Não enviamos email de teste para não spamear
        print("\n⚠️  Email de teste não enviado para evitar spam")
        
        db.close()
        return True
    
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False


async def run_all_tests():
    """Executa todos os testes"""
    print("\n" + "=" * 50)
    print("🧪 TESTES DO SISTEMA CRM")
    print("=" * 50)
    
    results = {}
    
    # Testes
    results["OpenAI"] = await test_openai()
    results["Evolution"] = await test_evolution()
    results["Database"] = test_database()
    results["Email"] = test_email()
    
    # Resumo
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)
    
    for service, passed in results.items():
        status = "✅ OK" if passed else "❌ ERRO"
        print(f"{service:15} {status}")
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"\n{passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 Sistema pronto para uso!")
        print("\nPróximos passos:")
        print("1. Configure o webhook na Evolution API")
        print("2. Execute: python run.py")
        print("3. Acesse o dashboard em http://localhost:8501")
    else:
        print("\n⚠️  Corrija os erros antes de usar o sistema")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
