"""
Script standalone para monitorar e-mails a cada 24 horas
Execute este script se não quiser usar o scheduler integrado ao FastAPI
"""
import asyncio
import logging
import sys
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.database.models import init_db, get_session
from app.services.email_reader_service import EmailReaderService
from config.settings import settings

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def check_emails_job():
    """Job que verifica e-mails"""
    logger.info("=" * 60)
    logger.info(f"🔍 VERIFICAÇÃO AUTOMÁTICA DE E-MAILS - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    logger.info("=" * 60)
    
    # Inicializa banco de dados
    engine = init_db(settings.DATABASE_URL)
    db = get_session(engine)
    
    try:
        # Cria serviço de leitura
        email_service = EmailReaderService(db)
        
        # Lê e processa e-mails
        processed = await email_service.read_and_process_emails(
            max_emails=settings.EMAIL_MAX_PROCESS
        )
        
        logger.info(f"✅ Verificação concluída: {processed} e-mails de seguros processados")
        
        return processed
    
    except Exception as e:
        logger.error(f"❌ Erro na verificação automática: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return 0
    
    finally:
        db.close()


async def run_scheduler():
    """Roda o scheduler"""
    logger.info("=" * 60)
    logger.info("🚀 MONITOR DE E-MAILS - MODO STANDALONE")
    logger.info("=" * 60)
    
    # Valida configurações
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.error("❌ Configurações de e-mail não encontradas!")
        logger.error("Configure SMTP_USER e SMTP_PASSWORD no arquivo .env")
        sys.exit(1)
    
    logger.info(f"📧 Conta de e-mail: {settings.SMTP_USER}")
    logger.info(f"📱 WhatsApp admin: {settings.ADMIN_WHATSAPP or 'Não configurado'}")
    logger.info(f"⏰ Intervalo: A cada 24 horas")
    logger.info("")
    
    # Cria scheduler
    scheduler = AsyncIOScheduler()
    
    # Adiciona job que roda a cada 24 horas
    scheduler.add_job(
        check_emails_job,
        trigger=IntervalTrigger(hours=24),
        id='email_check_job',
        name='Verificação de E-mails',
        replace_existing=True,
        next_run_time=datetime.now()  # Executa imediatamente na primeira vez
    )
    
    # Inicia o scheduler
    scheduler.start()
    logger.info("✅ Scheduler iniciado com sucesso")
    logger.info("📅 Primeira verificação executando agora...")
    logger.info("")
    logger.info("💡 Pressione Ctrl+C para parar")
    logger.info("=" * 60)
    
    try:
        # Mantém o script rodando
        while True:
            await asyncio.sleep(60)  # Acorda a cada minuto para verificar
    except KeyboardInterrupt:
        logger.info("\n👋 Encerrando monitor de e-mails...")
        scheduler.shutdown()
        logger.info("✅ Monitor encerrado")


def main():
    """Função principal"""
    try:
        asyncio.run(run_scheduler())
    except KeyboardInterrupt:
        logger.info("\n👋 Monitor interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Erro fatal: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
