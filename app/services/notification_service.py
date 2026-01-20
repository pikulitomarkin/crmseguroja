"""
Serviço de Notificações (Email e WhatsApp)
"""
import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from sqlalchemy.orm import Session
from config.settings import settings
from app.database.models import NotificationLog
from app.services.evolution_service import EvolutionService


class NotificationService:
    """Serviço centralizado de notificações"""
    
    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self.evolution = EvolutionService()
    
    def send_email(
        self,
        recipient_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """
        Envia email via SMTP
        
        Args:
            recipient_email: Email do destinatário
            subject: Assunto do email
            body: Corpo do email em texto
            html_body: Corpo do email em HTML (opcional)
        
        Returns:
            True se enviado com sucesso
        """
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = settings.EMAIL_FROM
            msg["To"] = recipient_email
            
            # Adiciona versão em texto
            msg.attach(MIMEText(body, "plain"))
            
            # Adiciona versão em HTML se fornecida
            if html_body:
                msg.attach(MIMEText(html_body, "html"))
            
            # Conecta ao servidor SMTP
            with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
            
            # Log no banco de dados
            if self.db:
                self._log_notification(
                    recipient=recipient_email,
                    notification_type="email",
                    status="enviado"
                )
            
            return True
        
        except Exception as e:
            print(f"Erro ao enviar email: {str(e)}")
            if self.db:
                self._log_notification(
                    recipient=recipient_email,
                    notification_type="email",
                    status="falha",
                    error_message=str(e)
                )
            return False
    
    async def send_whatsapp_notification(
        self,
        whatsapp_number: str,
        message: str
    ) -> bool:
        """
        Envia notificação via WhatsApp
        
        Args:
            whatsapp_number: Número do WhatsApp
            message: Conteúdo da mensagem
        
        Returns:
            True se enviado com sucesso
        """
        try:
            success = await self.evolution.send_notification(whatsapp_number, message)
            
            if self.db:
                self._log_notification(
                    recipient=whatsapp_number,
                    notification_type="whatsapp",
                    status="enviado" if success else "falha"
                )
            
            return success
        
        except Exception as e:
            print(f"Erro ao enviar notificação WhatsApp: {str(e)}")
            if self.db:
                self._log_notification(
                    recipient=whatsapp_number,
                    notification_type="whatsapp",
                    status="falha",
                    error_message=str(e)
                )
            return False
    
    async def notify_admin_lead_qualified(
        self,
        lead_data: dict,
        whatsapp_number: str
    ) -> bool:
        """
        Notifica admin quando um lead é qualificado
        
        Args:
            lead_data: Dados do lead (name, interest, necessity, email)
            whatsapp_number: Número WhatsApp do lead
        
        Returns:
            True se notificações foram enviadas com sucesso
        """
        try:
            # Formata mensagem de notificação (sem formatação especial)
            whatsapp_msg = f"""NOVO LEAD QUALIFICADO

Nome: {lead_data.get('name', 'N/A')}
Email: {lead_data.get('email', 'N/A')}
WhatsApp: {whatsapp_number}
Interesse: {lead_data.get('interest', 'N/A')}
Necessidade: {lead_data.get('necessity', 'N/A')}

Entre em contato via WhatsApp ou email."""
            
            # Formata corpo do email
            email_body = f"""Novo Lead Qualificado

Nome: {lead_data.get('name', 'N/A')}
Email: {lead_data.get('email', 'N/A')}
WhatsApp: {whatsapp_number}
Interesse: {lead_data.get('interest', 'N/A')}
Necessidade: {lead_data.get('necessity', 'N/A')}

Acesse o dashboard para assumir o atendimento."""
            
            email_html = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2 style="color: #25D366;">🎯 Novo Lead Qualificado</h2>
                    <p><strong>Nome:</strong> {lead_data.get('name', 'N/A')}</p>
                    <p><strong>WhatsApp:</strong> {whatsapp_number}</p>
                    <p><strong>Interesse:</strong> {lead_data.get('interest', 'N/A')}</p>
                    <p><strong>Necessidade:</strong> {lead_data.get('necessity', 'N/A')}</p>
                    <p><a href="http://localhost:8501" style="background-color: #25D366; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                        Acessar Dashboard
                    </a></p>
                </body>
            </html>
            """
            
            # Envia email
            email_sent = self.send_email(
                recipient_email=settings.ADMIN_EMAIL,
                subject=f"🎯 Novo Lead Qualificado - {lead_data.get('name', 'Sem nome')}",
                body=email_body,
                html_body=email_html
            )
            
            # Envia WhatsApp
            whatsapp_sent = False
            if settings.ADMIN_WHATSAPP:
                whatsapp_sent = await self.send_whatsapp_notification(
                    settings.ADMIN_WHATSAPP,
                    whatsapp_msg
                )
            
            return email_sent or whatsapp_sent
        
        except Exception as e:
            print(f"Erro ao notificar admin: {str(e)}")
            return False
    
    def _log_notification(
        self,
        recipient: str,
        notification_type: str,
        status: str,
        error_message: Optional[str] = None,
        lead_id: Optional[int] = None
    ):
        """Log de notificação no banco de dados"""
        try:
            if not self.db:
                return
            
            log = NotificationLog(
                lead_id=lead_id,
                whatsapp_number=recipient if notification_type == "whatsapp" else None,
                notification_type=notification_type,
                recipient=recipient,
                status=status,
                error_message=error_message
            )
            self.db.add(log)
            self.db.commit()
        except Exception as e:
            print(f"Erro ao logar notificação: {str(e)}")
