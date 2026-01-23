"""
Serviço de Leitura e Processamento de E-mails
"""
import imaplib
import email
from email.header import decode_header
from typing import List, Dict, Optional
import re
from datetime import datetime
import logging
from sqlalchemy.orm import Session
from app.database.models import Lead
from app.services.database_service import LeadService, MessageService
from app.services.evolution_service import EvolutionService
from app.services.ai_service import AIService
from config.settings import settings

logger = logging.getLogger(__name__)


class EmailReaderService:
    """Serviço para ler e processar e-mails recebidos"""
    
    def __init__(self, db: Session):
        self.db = db
        self.evolution = EvolutionService()
        self.ai_service = AIService()
    
    def connect_to_mailbox(self) -> Optional[imaplib.IMAP4_SSL]:
        """
        Conecta à caixa de entrada via IMAP
        
        Returns:
            Conexão IMAP ou None em caso de erro
        """
        try:
            # Determina servidor IMAP baseado no SMTP
            if "gmail" in settings.SMTP_SERVER.lower():
                imap_server = "imap.gmail.com"
            elif "outlook" in settings.SMTP_SERVER.lower() or "hotmail" in settings.SMTP_SERVER.lower():
                imap_server = "outlook.office365.com"
            elif "yahoo" in settings.SMTP_SERVER.lower():
                imap_server = "imap.mail.yahoo.com"
            else:
                # Tenta substituir smtp por imap
                imap_server = settings.SMTP_SERVER.replace("smtp", "imap")
            
            logger.info(f"Conectando ao servidor IMAP: {imap_server}")
            
            mail = imaplib.IMAP4_SSL(imap_server)
            mail.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            
            logger.info("✅ Conectado ao servidor IMAP com sucesso")
            return mail
        
        except Exception as e:
            logger.error(f"❌ Erro ao conectar ao IMAP: {str(e)}")
            return None
    
    def decode_email_subject(self, subject: str) -> str:
        """
        Decodifica assunto do e-mail
        
        Args:
            subject: Assunto codificado
        
        Returns:
            Assunto decodificado
        """
        try:
            decoded_parts = decode_header(subject)
            decoded_subject = ""
            
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    decoded_subject += part.decode(encoding or "utf-8", errors="ignore")
                else:
                    decoded_subject += part
            
            return decoded_subject
        except:
            return subject
    
    def extract_email_body(self, msg: email.message.Message) -> str:
        """
        Extrai o corpo do e-mail
        
        Args:
            msg: Mensagem de e-mail
        
        Returns:
            Corpo do e-mail em texto
        """
        body = ""
        
        try:
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    
                    # Ignora anexos
                    if "attachment" in content_disposition:
                        continue
                    
                    # Pega texto
                    if content_type == "text/plain":
                        charset = part.get_content_charset() or "utf-8"
                        body = part.get_payload(decode=True).decode(charset, errors="ignore")
                        break
                    elif content_type == "text/html" and not body:
                        # Se não tem texto simples, usa HTML
                        charset = part.get_content_charset() or "utf-8"
                        html_body = part.get_payload(decode=True).decode(charset, errors="ignore")
                        # Remove tags HTML básicas
                        body = re.sub(r'<[^>]+>', '', html_body)
            else:
                charset = msg.get_content_charset() or "utf-8"
                body = msg.get_payload(decode=True).decode(charset, errors="ignore")
        
        except Exception as e:
            logger.error(f"Erro ao extrair corpo do e-mail: {str(e)}")
            body = ""
        
        return body.strip()
    
    def extract_sender_info(self, from_header: str) -> Dict[str, str]:
        """
        Extrai informações do remetente
        
        Args:
            from_header: Header "From" do e-mail
        
        Returns:
            Dict com name e email
        """
        try:
            # Formato: "Nome <email@example.com>" ou "email@example.com"
            match = re.match(r'(.+?)\s*<(.+?)>', from_header)
            if match:
                name = match.group(1).strip().strip('"')
                email_addr = match.group(2).strip()
            else:
                name = ""
                email_addr = from_header.strip()
            
            # Decodifica nome se necessário
            if name:
                name = self.decode_email_subject(name)
            
            return {"name": name, "email": email_addr}
        
        except Exception as e:
            logger.error(f"Erro ao extrair remetente: {str(e)}")
            return {"name": "", "email": from_header}
    
    def is_insurance_related(self, subject: str, body: str) -> bool:
        """
        Verifica se o e-mail é relacionado a seguros ou consórcios
        
        Args:
            subject: Assunto do e-mail
            body: Corpo do e-mail
        
        Returns:
            True se for relacionado a seguros
        """
        keywords = [
            "seguro", "cotação", "cotacao", "orçamento", "orcamento",
            "apólice", "apolice", "sinistro", "indenização", "indenizacao",
            "cobertura", "prêmio", "premio", "franquia",
            "consórcio", "consorcio", "carta de crédito", "carta de credito",
            "auto", "veículo", "veiculo", "carro", "moto",
            "residencial", "imóvel", "imovel", "casa", "apartamento",
            "vida", "acidentes pessoais",
            "proposta", "renovação", "renovacao",
            "seguro já", "seguro ja"
        ]
        
        text = (subject + " " + body).lower()
        
        return any(keyword in text for keyword in keywords)
    
    async def process_insurance_email(
        self,
        sender_name: str,
        sender_email: str,
        subject: str,
        body: str
    ) -> bool:
        """
        Processa e-mail relacionado a seguros e cria lead
        
        Args:
            sender_name: Nome do remetente
            sender_email: E-mail do remetente
            subject: Assunto
            body: Corpo do e-mail
        
        Returns:
            True se processado com sucesso
        """
        try:
            logger.info(f"📧 Processando e-mail de {sender_email}: {subject[:50]}...")
            
            # Usa e-mail como identificador único (ao invés de WhatsApp)
            # Gera um "phone number" fictício baseado no hash do e-mail
            phone_hash = str(abs(hash(sender_email)) % 10000000000).zfill(10)
            whatsapp_number = f"email_{phone_hash}"
            
            # Verifica se já existe lead com este e-mail
            existing_lead = self.db.query(Lead).filter(Lead.email == sender_email).first()
            
            if existing_lead:
                logger.info(f"Lead já existe para {sender_email}")
                lead = existing_lead
            else:
                # Cria novo lead
                lead = LeadService.create_or_get_lead(self.db, whatsapp_number, "novo")
                lead.name = sender_name if sender_name else "Lead via E-mail"
                lead.email = sender_email
                lead.flow_type = "email_inbound"
                lead.flow_step = "email_recebido"
                self.db.commit()
                logger.info(f"✅ Novo lead criado via e-mail: {sender_email}")
            
            # Usa IA para extrair informações do e-mail
            conversation = [
                {"role": "user", "content": f"Assunto: {subject}\n\n{body}"}
            ]
            
            extracted_data = self.ai_service.extract_lead_data_from_conversation(
                conversation,
                "seguro_auto"  # Tenta extrair campos de seguro auto por padrão
            )
            
            # Atualiza lead com dados extraídos
            for key, value in extracted_data.items():
                if value and value != "null" and hasattr(lead, key):
                    setattr(lead, key, value)
            
            # Força alguns campos
            if not lead.name and sender_name:
                lead.name = sender_name
            if not lead.email:
                lead.email = sender_email
            
            self.db.commit()
            
            # Salva o e-mail como mensagem no histórico
            MessageService.save_message(
                self.db,
                whatsapp_number,
                "user",
                f"📧 E-mail recebido\nAssunto: {subject}\n\n{body[:500]}...",
                role="user",
                lead_id=lead.id
            )
            self.db.commit()
            
            # Notifica admin via WhatsApp
            if settings.ADMIN_WHATSAPP:
                await self.notify_admin_about_email(lead, subject, body[:300])
            
            logger.info(f"✅ E-mail processado com sucesso: {sender_email}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Erro ao processar e-mail: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    async def notify_admin_about_email(
        self,
        lead: Lead,
        subject: str,
        body_preview: str
    ):
        """
        Notifica admin via WhatsApp sobre novo lead de e-mail
        
        Args:
            lead: Lead criado
            subject: Assunto do e-mail
            body_preview: Preview do corpo
        """
        try:
            message = f"""🔔 *NOVO LEAD VIA E-MAIL*

📧 *E-mail:* {lead.email}
👤 *Nome:* {lead.name or "Não informado"}
📋 *Assunto:* {subject}

*Preview:*
{body_preview}

---
💡 Lead capturado automaticamente do e-mail
🆔 ID do Lead: {lead.id}"""
            
            await self.evolution.send_message(settings.ADMIN_WHATSAPP, message)
            logger.info(f"✅ Admin notificado sobre lead de e-mail: {lead.email}")
        
        except Exception as e:
            logger.error(f"❌ Erro ao notificar admin: {str(e)}")
    
    async def read_and_process_emails(self, max_emails: int = 10) -> int:
        """
        Lê e processa e-mails não lidos relacionados a seguros
        
        Args:
            max_emails: Número máximo de e-mails a processar
        
        Returns:
            Número de e-mails processados
        """
        processed = 0
        
        try:
            mail = self.connect_to_mailbox()
            if not mail:
                logger.error("Não foi possível conectar à caixa de entrada")
                return 0
            
            # Seleciona caixa de entrada
            mail.select("INBOX")
            
            # Busca e-mails não lidos
            status, messages = mail.search(None, "UNSEEN")
            
            if status != "OK":
                logger.error("Erro ao buscar e-mails")
                mail.close()
                mail.logout()
                return 0
            
            email_ids = messages[0].split()
            
            if not email_ids:
                logger.info("Nenhum e-mail novo para processar")
                mail.close()
                mail.logout()
                return 0
            
            logger.info(f"📬 Encontrados {len(email_ids)} e-mails não lidos")
            
            # Processa os últimos emails (máximo definido)
            for email_id in email_ids[-max_emails:]:
                try:
                    # Busca o e-mail
                    status, msg_data = mail.fetch(email_id, "(RFC822)")
                    
                    if status != "OK":
                        continue
                    
                    # Parse do e-mail
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    
                    # Extrai informações
                    subject = self.decode_email_subject(msg.get("Subject", ""))
                    from_header = msg.get("From", "")
                    sender_info = self.extract_sender_info(from_header)
                    body = self.extract_email_body(msg)
                    
                    logger.info(f"📧 E-mail de {sender_info['email']}: {subject[:50]}")
                    
                    # Verifica se é relacionado a seguros
                    if self.is_insurance_related(subject, body):
                        logger.info(f"✅ E-mail relacionado a seguros detectado")
                        
                        # Processa o e-mail
                        success = await self.process_insurance_email(
                            sender_info["name"],
                            sender_info["email"],
                            subject,
                            body
                        )
                        
                        if success:
                            processed += 1
                    else:
                        logger.info(f"⏭️  E-mail não relacionado a seguros, ignorando")
                
                except Exception as e:
                    logger.error(f"Erro ao processar e-mail individual: {str(e)}")
                    continue
            
            mail.close()
            mail.logout()
            
            logger.info(f"✅ Processamento concluído: {processed} e-mails de seguros processados")
            return processed
        
        except Exception as e:
            logger.error(f"❌ Erro ao ler e-mails: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return 0
