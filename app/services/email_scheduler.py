"""
Scheduler para verificação automática de e-mails a cada 24 horas
"""
import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.database.models import init_db, get_session
from app.services.email_reader_service import EmailReaderService
from config.settings import settings

logger = logging.getLogger(__name__)


class EmailScheduler:
    """Scheduler para verificação periódica de e-mails"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
    
    async def check_emails_job(self):
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
    
    def start(self, interval_hours: int = 24):
        """
        Inicia o scheduler
        
        Args:
            interval_hours: Intervalo em horas entre verificações (padrão: 24h)
        """
        if self.is_running:
            logger.warning("⚠️  Scheduler já está rodando")
            return
        
        logger.info(f"🚀 Iniciando scheduler de e-mails (intervalo: {interval_hours}h)")
        
        # Verifica se as credenciais de e-mail estão configuradas
        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            logger.warning("⚠️  Credenciais de e-mail não configuradas - scheduler não iniciado")
            logger.warning("Configure SMTP_USER e SMTP_PASSWORD no .env para ativar verificação automática")
            return
        
        # Adiciona job que roda a cada X horas
        self.scheduler.add_job(
            self.check_emails_job,
            trigger=IntervalTrigger(hours=interval_hours),
            id='email_check_job',
            name='Verificação de E-mails',
            replace_existing=True,
            next_run_time=datetime.now()  # Executa imediatamente na primeira vez
        )
        
        # Inicia o scheduler
        self.scheduler.start()
        self.is_running = True
        
        logger.info(f"✅ Scheduler iniciado - próxima verificação em {interval_hours}h")
        logger.info(f"📧 Monitorando: {settings.SMTP_USER}")
        logger.info(f"📱 Notificações para: {settings.ADMIN_WHATSAPP or 'Não configurado'}")
    
    def stop(self):
        """Para o scheduler"""
        if not self.is_running:
            return
        
        logger.info("🛑 Parando scheduler de e-mails...")
        self.scheduler.shutdown()
        self.is_running = False
        logger.info("✅ Scheduler parado")
    
    def get_next_run_time(self):
        """Retorna o horário da próxima execução"""
        if not self.is_running:
            return None
        
        job = self.scheduler.get_job('email_check_job')
        if job:
            return job.next_run_time
        return None
    
    def trigger_now(self):
        """Dispara verificação imediata"""
        if not self.is_running:
            logger.warning("⚠️  Scheduler não está rodando")
            return
        
        logger.info("⚡ Disparando verificação imediata de e-mails...")
        job = self.scheduler.get_job('email_check_job')
        if job:
            job.modify(next_run_time=datetime.now())
            logger.info("✅ Verificação agendada para execução imediata")


# Instância global do scheduler
email_scheduler = EmailScheduler()
