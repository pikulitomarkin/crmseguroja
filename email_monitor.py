"""
Script para monitorar e processar e-mails recebidos
Executa periodicamente para verificar novos e-mails sobre seguros
"""
import asyncio
import logging
import sys
from datetime import datetime
from app.database.models import init_db, get_session
from app.services.email_reader_service import EmailReaderService
from config.settings import settings

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def check_emails_once():
    """Verifica e-mails uma única vez"""
    logger.info("=" * 60)
    logger.info("🔍 INICIANDO VERIFICAÇÃO DE E-MAILS")
    logger.info("=" * 60)
    
    # Inicializa banco de dados
    engine = init_db(settings.DATABASE_URL)
    db = get_session(engine)
    
    try:
        # Cria serviço de leitura
        email_service = EmailReaderService(db)
        
        # Lê e processa e-mails
        processed = await email_service.read_and_process_emails(max_emails=10)
        
        logger.info(f"✅ Verificação concluída: {processed} e-mails processados")
        
        return processed
    
    except Exception as e:
        logger.error(f"❌ Erro na verificação: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return 0
    
    finally:
        db.close()


async def monitor_emails_loop(interval_minutes: int = 5):
    """
    Monitora e-mails continuamente
    
    Args:
        interval_minutes: Intervalo entre verificações em minutos
    """
    logger.info(f"🔄 Monitoramento de e-mails iniciado (intervalo: {interval_minutes} min)")
    
    while True:
        try:
            await check_emails_once()
        except Exception as e:
            logger.error(f"Erro no loop de monitoramento: {str(e)}")
        
        # Aguarda intervalo
        logger.info(f"⏰ Próxima verificação em {interval_minutes} minutos...")
        await asyncio.sleep(interval_minutes * 60)


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor de E-mails para Leads")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Verifica e-mails uma única vez e sai"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Intervalo entre verificações em minutos (padrão: 5)"
    )
    
    args = parser.parse_args()
    
    # Valida configurações
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.error("❌ Configurações de e-mail não encontradas!")
        logger.error("Configure SMTP_USER e SMTP_PASSWORD no arquivo .env")
        sys.exit(1)
    
    if not settings.ADMIN_WHATSAPP:
        logger.warning("⚠️  ADMIN_WHATSAPP não configurado - notificações desabilitadas")
    
    logger.info(f"📧 Conta de e-mail: {settings.SMTP_USER}")
    logger.info(f"📱 WhatsApp admin: {settings.ADMIN_WHATSAPP or 'Não configurado'}")
    
    if args.once:
        # Executa uma única vez
        asyncio.run(check_emails_once())
    else:
        # Loop contínuo
        try:
            asyncio.run(monitor_emails_loop(args.interval))
        except KeyboardInterrupt:
            logger.info("\n👋 Monitoramento interrompido pelo usuário")
            sys.exit(0)


if __name__ == "__main__":
    main()
