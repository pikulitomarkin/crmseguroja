"""
Serviço de Notificações (Email e WhatsApp)
"""
import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict
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
            with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT, timeout=5) as server:
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
        
        except (OSError, ConnectionError) as e:
            # Erro de rede (esperado no Railway - SMTP bloqueado)
            # Não loga como erro, apenas aviso silencioso
            if self.db:
                self._log_notification(
                    recipient=recipient_email,
                    notification_type="email",
                    status="bloqueado",
                    error_message="SMTP bloqueado pela plataforma"
                )
            return False
        
        except Exception as e:
            # Outros erros (credenciais, etc)
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
            print(f"[NOTIFICATION] Tentando enviar WhatsApp para: {whatsapp_number}")
            print(f"[NOTIFICATION] Tamanho da mensagem: {len(message)} caracteres")
            
            success = await self.evolution.send_notification(whatsapp_number, message)
            
            if success:
                print(f"[NOTIFICATION] ✅ WhatsApp enviado com sucesso para {whatsapp_number}")
            else:
                print(f"[NOTIFICATION] ❌ Falha ao enviar WhatsApp para {whatsapp_number}")
            
            if self.db:
                self._log_notification(
                    recipient=whatsapp_number,
                    notification_type="whatsapp",
                    status="enviado" if success else "falha"
                )
            
            return success
        
        except Exception as e:
            print(f"[NOTIFICATION] ❌ ERRO ao enviar notificação WhatsApp para {whatsapp_number}: {str(e)}")
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
            lead_data: Dados do lead completos
            whatsapp_number: Número WhatsApp do lead
        
        Returns:
            True se notificações foram enviadas com sucesso
        """
        try:
            flow_type = lead_data.get('flow_type', 'desconhecido')
            
            # Monta mensagem baseada no tipo de fluxo
            if flow_type == 'seguro_auto':
                # Coleta TODOS os dados disponíveis
                dados_principais = []
                if lead_data.get('name'):
                    dados_principais.append(f"👤 Nome: {lead_data.get('name')}")
                dados_principais.append(f"📱 WhatsApp: {whatsapp_number}")
                if lead_data.get('cpf_cnpj'):
                    dados_principais.append(f"🔢 CPF/CNPJ: {lead_data.get('cpf_cnpj')}")
                if lead_data.get('vehicle_plate'):
                    dados_principais.append(f"🚙 Placa: {lead_data.get('vehicle_plate')}")
                
                contato = []
                if lead_data.get('phone'):
                    contato.append(f"📞 Telefone: {lead_data.get('phone')}")
                if lead_data.get('email'):
                    contato.append(f"📧 Email: {lead_data.get('email')}")
                if lead_data.get('second_email'):
                    contato.append(f"📧 Email 2: {lead_data.get('second_email')}")
                
                dados_complementares = []
                if lead_data.get('cep_pernoite'):
                    dados_complementares.append(f"📍 CEP Pernoite: {lead_data.get('cep_pernoite')}")
                if lead_data.get('profession'):
                    dados_complementares.append(f"🏢 Profissão: {lead_data.get('profession')}")
                if lead_data.get('marital_status'):
                    dados_complementares.append(f"💍 Estado Civil: {lead_data.get('marital_status')}")
                if lead_data.get('vehicle_usage'):
                    dados_complementares.append(f"🎯 Uso: {lead_data.get('vehicle_usage')}")
                if lead_data.get('has_young_driver') is not None:
                    dados_complementares.append(f"👨‍👦 Condutor < 26 anos: {lead_data.get('has_young_driver')}")
                
                extras = []
                if lead_data.get('interest'):
                    extras.append(f"📝 Observações: {lead_data.get('interest')}")
                if lead_data.get('necessity'):
                    extras.append(f"📝 Necessidade: {lead_data.get('necessity')}")
                
                # Monta mensagem apenas com dados disponíveis
                msg_parts = [f"🔔 *NOVO LEAD - SEGURO AUTO*\n"]
                
                if dados_principais:
                    msg_parts.append("📋 *DADOS PRINCIPAIS:*")
                    msg_parts.extend(dados_principais)
                    msg_parts.append("")
                
                if contato:
                    msg_parts.append("📧 *CONTATO:*")
                    msg_parts.extend(contato)
                    msg_parts.append("")
                
                if dados_complementares:
                    msg_parts.append("🚗 *DADOS COMPLEMENTARES:*")
                    msg_parts.extend(dados_complementares)
                    msg_parts.append("")
                
                if extras:
                    msg_parts.append("💬 *INFORMAÇÕES EXTRAS:*")
                    msg_parts.extend(extras)
                    msg_parts.append("")
                
                msg_parts.append("---")
                msg_parts.append("💡 *Entre em contato imediatamente!*")
                
                whatsapp_msg = "\n".join(msg_parts)

            elif flow_type == 'seguro_residencial':
                dados_cliente = []
                if lead_data.get('name'):
                    dados_cliente.append(f"👤 Nome: {lead_data.get('name')}")
                dados_cliente.append(f"📱 WhatsApp: {whatsapp_number}")
                if lead_data.get('cpf_cnpj'):
                    dados_cliente.append(f"🔢 CPF/CNPJ: {lead_data.get('cpf_cnpj')}")
                if lead_data.get('email'):
                    dados_cliente.append(f"📧 Email: {lead_data.get('email')}")
                if lead_data.get('phone'):
                    dados_cliente.append(f"📞 Telefone: {lead_data.get('phone')}")
                
                dados_imovel = []
                if lead_data.get('property_cep'):
                    dados_imovel.append(f"📍 CEP: {lead_data.get('property_cep')}")
                if lead_data.get('property_type'):
                    dados_imovel.append(f"🏢 Tipo: {lead_data.get('property_type')}")
                if lead_data.get('property_value'):
                    dados_imovel.append(f"💰 Valor: {lead_data.get('property_value')}")
                if lead_data.get('property_ownership'):
                    dados_imovel.append(f"🔑 Situação: {lead_data.get('property_ownership')}")
                
                extras = []
                if lead_data.get('interest'):
                    extras.append(f"📝 Observações: {lead_data.get('interest')}")
                
                msg_parts = [f"🔔 *NOVO LEAD - SEGURO RESIDENCIAL*\n"]
                if dados_cliente:
                    msg_parts.append("📋 *DADOS DO CLIENTE:*")
                    msg_parts.extend(dados_cliente)
                    msg_parts.append("")
                if dados_imovel:
                    msg_parts.append("🏠 *DADOS DO IMÓVEL:*")
                    msg_parts.extend(dados_imovel)
                    msg_parts.append("")
                if extras:
                    msg_parts.append("💬 *INFORMAÇÕES EXTRAS:*")
                    msg_parts.extend(extras)
                    msg_parts.append("")
                msg_parts.append("---")
                msg_parts.append("💡 *Entre em contato imediatamente!*")
                whatsapp_msg = "\n".join(msg_parts)

            elif flow_type == 'consorcio':
                dados_cliente = []
                if lead_data.get('name'):
                    dados_cliente.append(f"👤 Nome: {lead_data.get('name')}")
                if lead_data.get('cpf_cnpj'):
                    dados_cliente.append(f"🔢 CPF/CNPJ: {lead_data.get('cpf_cnpj')}")
                dados_cliente.append(f"📱 WhatsApp: {whatsapp_number}")
                if lead_data.get('email'):
                    dados_cliente.append(f"📧 Email: {lead_data.get('email')}")
                if lead_data.get('second_email'):
                    dados_cliente.append(f"📧 Email 2: {lead_data.get('second_email')}")
                if lead_data.get('phone'):
                    dados_cliente.append(f"📞 Telefone: {lead_data.get('phone')}")
                
                dados_consorcio = []
                if lead_data.get('consortium_type'):
                    dados_consorcio.append(f"📝 Tipo: {lead_data.get('consortium_type')}")
                if lead_data.get('consortium_value'):
                    dados_consorcio.append(f"💰 Valor da Carta: {lead_data.get('consortium_value')}")
                if lead_data.get('consortium_term'):
                    dados_consorcio.append(f"📅 Prazo: {lead_data.get('consortium_term')} meses")
                if lead_data.get('has_previous_consortium') is not None:
                    dados_consorcio.append(f"🔄 Já participou antes: {lead_data.get('has_previous_consortium')}")
                
                extras = []
                if lead_data.get('interest'):
                    extras.append(f"📝 Observações: {lead_data.get('interest')}")
                
                msg_parts = [f"🔔 *NOVO LEAD - CONSÓRCIO*\n"]
                if dados_cliente:
                    msg_parts.append("📋 *DADOS DO CLIENTE:*")
                    msg_parts.extend(dados_cliente)
                    msg_parts.append("")
                if dados_consorcio:
                    msg_parts.append("💼 *DADOS DO CONSÓRCIO:*")
                    msg_parts.extend(dados_consorcio)
                    msg_parts.append("")
                if extras:
                    msg_parts.append("💬 *INFORMAÇÕES EXTRAS:*")
                    msg_parts.extend(extras)
                    msg_parts.append("")
                msg_parts.append("---")
                msg_parts.append("💡 *Entre em contato imediatamente!*")
                whatsapp_msg = "\n".join(msg_parts)

            elif flow_type == 'seguro_vida':
                # Informações extras
                extras = []
                if lead_data.get('interest'):
                    extras.append(f"📝 Observações: {lead_data.get('interest')}")
                if lead_data.get('necessity'):
                    extras.append(f"📝 Necessidade: {lead_data.get('necessity')}")
                if lead_data.get('phone'):
                    extras.append(f"📞 Telefone: {lead_data.get('phone')}")
                
                extras_text = "\n".join(extras) if extras else ""
                
                whatsapp_msg = f"""🔔 *NOVO LEAD QUALIFICADO - SEGURO DE VIDA*

📋 *DADOS DO CLIENTE:*
👤 Nome: {lead_data.get('name', 'N/A')}
🔢 CPF/CNPJ: {lead_data.get('cpf_cnpj', 'N/A')}
📱 WhatsApp: {whatsapp_number}
📧 Email: {lead_data.get('email', 'N/A')}
{f"\n💬 *INFORMAÇÕES EXTRAS:*\n{extras_text}" if extras_text else ""}

---
💡 *Entre em contato imediatamente!*"""

            elif flow_type == 'seguro_empresarial':
                # Informações extras
                extras = []
                if lead_data.get('interest'):
                    extras.append(f"📝 Observações: {lead_data.get('interest')}")
                if lead_data.get('necessity'):
                    extras.append(f"📝 Necessidade: {lead_data.get('necessity')}")
                if lead_data.get('phone'):
                    extras.append(f"📞 Telefone: {lead_data.get('phone')}")
                
                extras_text = "\n".join(extras) if extras else ""
                
                whatsapp_msg = f"""🔔 *NOVO LEAD QUALIFICADO - SEGURO EMPRESARIAL*

📋 *DADOS DO CLIENTE:*
👤 Nome: {lead_data.get('name', 'N/A')}
🔢 CPF/CNPJ: {lead_data.get('cpf_cnpj', 'N/A')}
📱 WhatsApp: {whatsapp_number}
📧 Email: {lead_data.get('email', 'N/A')}
{f"\n💬 *INFORMAÇÕES EXTRAS:*\n{extras_text}" if extras_text else ""}

---
💡 *Entre em contato imediatamente!*"""

            elif flow_type == 'segunda_via':
                # Inclui o produto desejado (interest)
                whatsapp_msg = f"""🔔 *SOLICITAÇÃO - SEGUNDA VIA*

📋 *DADOS:*
👤 Nome: {lead_data.get('name', 'N/A')}
🔢 CPF/CNPJ: {lead_data.get('cpf_cnpj', 'N/A')}
📱 WhatsApp: {whatsapp_number}
📄 Produto: {lead_data.get('interest', 'N/A')}

---
💡 *Enviar segunda via do boleto*"""

            elif flow_type == 'sinistro':
                # Informações extras sobre o sinistro
                extras = []
                if lead_data.get('interest'):
                    extras.append(f"📝 Detalhes: {lead_data.get('interest')}")
                if lead_data.get('necessity'):
                    extras.append(f"📝 Situação: {lead_data.get('necessity')}")
                if lead_data.get('email'):
                    extras.append(f"📧 Email: {lead_data.get('email')}")
                
                extras_text = "\n".join(extras) if extras else ""
                
                whatsapp_msg = f"""🔔 *URGENTE - SINISTRO*

📋 *DADOS DO CLIENTE:*
👤 Nome: {lead_data.get('name', 'N/A')}
🔢 CPF/CNPJ: {lead_data.get('cpf_cnpj', 'N/A')}
📱 WhatsApp: {whatsapp_number}
🚙 Placa do Veículo: {lead_data.get('vehicle_plate', 'N/A')}
{f"\n💬 *INFORMAÇÕES DO SINISTRO:*\n{extras_text}" if extras_text else ""}

---
⚠️ *PRIORIDADE: Entrar em contato IMEDIATAMENTE!*"""

            elif flow_type == 'falar_humano':
                # Informações extras sobre o motivo do contato
                extras = []
                if lead_data.get('email'):
                    extras.append(f"📧 Email: {lead_data.get('email')}")
                if lead_data.get('interest'):
                    extras.append(f"📝 Motivo: {lead_data.get('interest')}")
                if lead_data.get('necessity'):
                    extras.append(f"📝 Observações: {lead_data.get('necessity')}")
                
                extras_text = "\n".join(extras) if extras else ""
                
                whatsapp_msg = f"""🔔 *CLIENTE SOLICITOU ATENDIMENTO HUMANO*

📋 *DADOS DO CLIENTE:*
👤 Nome: {lead_data.get('name', 'N/A')}
🔢 CPF/CNPJ: {lead_data.get('cpf_cnpj', 'N/A')}
📱 WhatsApp: {whatsapp_number}
{f"\n💬 *INFORMAÇÕES EXTRAS:*\n{extras_text}" if extras_text else ""}

---
💡 *Cliente pediu para falar com atendente - Entre em contato!*"""

            else:
                # Fluxo genérico
                whatsapp_msg = f"""🔔 *NOVO LEAD QUALIFICADO*

👤 Nome: {lead_data.get('name', 'N/A')}
📱 WhatsApp: {whatsapp_number}
📧 Email: {lead_data.get('email', 'N/A')}
📋 Tipo: {flow_type}

---
💡 *Entre em contato!*"""
            
            # Envia WhatsApp - valida número do admin
            whatsapp_sent = False
            if settings.ADMIN_WHATSAPP:
                admin_number = settings.ADMIN_WHATSAPP.strip()
                print(f"[NOTIFICATION] ADMIN_WHATSAPP configurado: {admin_number}")
                # Valida que o número tem pelo menos 10 dígitos (código país + DDD + número)
                if len(admin_number) >= 10:
                    print(f"[NOTIFICATION] Enviando notificação de lead ({flow_type}) para admin...")
                    whatsapp_sent = await self.send_whatsapp_notification(
                        admin_number,
                        whatsapp_msg
                    )
                    print(f"[NOTIFICATION] Resultado do envio ao admin: {'✅ Sucesso' if whatsapp_sent else '❌ Falha'}")
                else:
                    print(f"[NOTIFICATION] ❌ ADMIN_WHATSAPP inválido: '{admin_number}' (deve ter pelo menos 10 dígitos)")
            else:
                print(f"[NOTIFICATION] ⚠️ ADMIN_WHATSAPP não configurado nas variáveis de ambiente")
            
            # Email simplificado (opcional)
            email_sent = False
            if settings.ADMIN_EMAIL:
                email_body = whatsapp_msg.replace('*', '').replace('_', '')
                email_sent = self.send_email(
                    recipient_email=settings.ADMIN_EMAIL,
                    subject=f"🎯 Novo Lead - {flow_type.replace('_', ' ').title()}",
                    body=email_body
                )
            
            return email_sent or whatsapp_sent
        except Exception as e:
            print(f"Erro ao notificar admin: {str(e)}")
            return False

    async def notify_admin_outros_assuntos(self, lead_data: Dict, whatsapp_number: str) -> bool:
        """
        Notifica admin sobre outros assuntos (não é lead qualificado)
        Envia apenas notificação com dados básicos
        
        Args:
            lead_data: Dicionário com dados coletados
            whatsapp_number: Número do WhatsApp
        
        Returns:
            True se notificação foi enviada com sucesso
        """
        try:
            # Mensagem específica para outros assuntos
            whatsapp_msg = f"""📋 *NOTIFICAÇÃO - OUTROS ASSUNTOS*

👤 Nome: {lead_data.get('name', 'N/A')}
📱 Telefone: {whatsapp_number}
💬 Assunto: {lead_data.get('interest', 'Não especificado')}

---
💡 *Contato solicitou informações sobre outro assunto*"""
            
            # Envia WhatsApp - valida número do admin
            whatsapp_sent = False
            if settings.ADMIN_WHATSAPP:
                admin_number = settings.ADMIN_WHATSAPP.strip()
                print(f"[NOTIFICATION] ADMIN_WHATSAPP configurado: {admin_number}")
                # Valida que o número tem pelo menos 10 dígitos (código país + DDD + número)
                if len(admin_number) >= 10:
                    print(f"[NOTIFICATION] Enviando notificação de outros assuntos para admin...")
                    whatsapp_sent = await self.send_whatsapp_notification(
                        admin_number,
                        whatsapp_msg
                    )
                    print(f"[NOTIFICATION] Resultado do envio ao admin: {'✅ Sucesso' if whatsapp_sent else '❌ Falha'}")
                else:
                    print(f"[NOTIFICATION] ❌ ADMIN_WHATSAPP inválido: '{admin_number}' (deve ter pelo menos 10 dígitos)")
            else:
                print(f"[NOTIFICATION] ⚠️ ADMIN_WHATSAPP não configurado nas variáveis de ambiente")
                # Valida que o número tem pelo menos 10 dígitos (código país + DDD + número)
                if len(admin_number) >= 10:
                    whatsapp_sent = await self.send_whatsapp_notification(
                        admin_number,
                        whatsapp_msg
                    )
                else:
                    print(f"ADMIN_WHATSAPP inválido: '{admin_number}' (deve ter pelo menos 10 dígitos)")
            
            # Email simplificado (opcional)
            email_sent = False
            if settings.ADMIN_EMAIL:
                email_body = whatsapp_msg.replace('*', '').replace('_', '')
                email_sent = self.send_email(
                    recipient_email=settings.ADMIN_EMAIL,
                    subject="📋 Notificação - Outros Assuntos",
                    body=email_body
                )
            
            return email_sent or whatsapp_sent
        
        except Exception as e:
            print(f"Erro ao notificar admin sobre outros assuntos: {str(e)}")
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
