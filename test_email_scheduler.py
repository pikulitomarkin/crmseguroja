"""
Teste rápido do scheduler de e-mails
"""
import asyncio
import logging
from app.services.email_scheduler import EmailScheduler

logging.basicConfig(level=logging.INFO)

async def test_scheduler():
    print("=" * 60)
    print("🧪 TESTE DO SCHEDULER DE E-MAILS")
    print("=" * 60)
    
    scheduler = EmailScheduler()
    
    print("\n1️⃣ Testando inicialização...")
    scheduler.start(interval_hours=24)
    
    await asyncio.sleep(2)
    
    print("\n2️⃣ Verificando status...")
    if scheduler.is_running:
        print("   ✅ Scheduler está rodando")
        next_run = scheduler.get_next_run_time()
        if next_run:
            print(f"   📅 Próxima execução: {next_run}")
    else:
        print("   ❌ Scheduler NÃO está rodando")
    
    print("\n3️⃣ Parando scheduler...")
    scheduler.stop()
    
    await asyncio.sleep(1)
    
    if not scheduler.is_running:
        print("   ✅ Scheduler parado com sucesso")
    
    print("\n" + "=" * 60)
    print("✅ TESTE CONCLUÍDO")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_scheduler())
