"""
Serviço de banco de dados - CRUD operations
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from app.database.models import Lead, ChatMessage, QualificationField


class LeadService:
    """Serviço para operações com leads"""
    
    @staticmethod
    def create_or_get_lead(
        db: Session,
        whatsapp_number: str,
        customer_type: str = "novo"
    ) -> Lead:
        """
        Cria ou retorna lead existente
        
        Args:
            db: Sessão do banco de dados
            whatsapp_number: Número WhatsApp
            customer_type: "novo" ou "existente"
        
        Returns:
            Objeto Lead
        """
        lead = db.query(Lead).filter(
            Lead.whatsapp_number == whatsapp_number
        ).first()
        
        if not lead:
            lead = Lead(
                whatsapp_number=whatsapp_number,
                customer_type=customer_type,
                status="novo"
            )
            db.add(lead)
            db.commit()
            db.refresh(lead)
        
        return lead
    
    @staticmethod
    def get_lead_by_number(
        db: Session,
        whatsapp_number: str
    ) -> Optional[Lead]:
        """Busca lead por número WhatsApp"""
        return db.query(Lead).filter(
            Lead.whatsapp_number == whatsapp_number
        ).first()
    
    @staticmethod
    def update_lead(
        db: Session,
        lead: Lead,
        **kwargs
    ) -> Lead:
        """
        Atualiza dados do lead
        
        Args:
            db: Sessão do banco de dados
            lead: Objeto Lead
            **kwargs: Campos a atualizar (name, status, etc)
        
        Returns:
            Lead atualizado
        """
        for key, value in kwargs.items():
            if hasattr(lead, key):
                setattr(lead, key, value)
        
        lead.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(lead)
        return lead
    
    @staticmethod
    def mark_qualified(
        db: Session,
        lead: Lead,
        qualification_score: int = 100,
        attended_by: str = "IA"
    ) -> Lead:
        """
        Marca lead como qualificado e desativa IA
        
        Args:
            db: Sessão do banco de dados
            lead: Objeto Lead
            qualification_score: Pontuação de qualificação (padrão: 100)
            attended_by: Quem qualificou (padrão: "IA")
        
        Returns:
            Lead atualizado
        """
        return LeadService.update_lead(
            db,
            lead,
            status="qualificado",
            status_ia=0,  # Desativa IA
            qualification_score=qualification_score,
            qualified_at=datetime.utcnow(),
            attended_by=attended_by
        )
    
    @staticmethod
    def deactivate_ia(
        db: Session,
        whatsapp_number: str
    ) -> bool:
        """Desativa IA para um número"""
        lead = LeadService.get_lead_by_number(db, whatsapp_number)
        if lead:
            LeadService.update_lead(db, lead, status_ia=0)
            return True
        return False
    
    @staticmethod
    def is_ia_active(
        db: Session,
        whatsapp_number: str
    ) -> bool:
        """Verifica se IA está ativa para um número"""
        lead = LeadService.get_lead_by_number(db, whatsapp_number)
        if lead:
            return lead.status_ia == 1
        return True  # Por padrão, IA ativa para novos números


class MessageService:
    """Serviço para operações com mensagens"""
    
    @staticmethod
    def save_message(
        db: Session,
        whatsapp_number: str,
        sender: str,
        message: str,
        role: str = "user",
        lead_id: int = None
    ) -> ChatMessage:
        """
        Salva mensagem no histórico
        
        Args:
            db: Sessão do banco de dados
            whatsapp_number: Número WhatsApp
            sender: "user" ou "ai"
            message: Conteúdo da mensagem
            role: Role para Claude (user/assistant)
            lead_id: ID do lead (opcional, será buscado se não fornecido)
        
        Returns:
            Objeto ChatMessage criado
        """
        # Se não forneceu lead_id, busca o lead pelo número
        if lead_id is None:
            lead = db.query(Lead).filter(Lead.whatsapp_number == whatsapp_number).first()
            if lead:
                lead_id = lead.id
        
        chat = ChatMessage(
            lead_id=lead_id,
            whatsapp_number=whatsapp_number,
            sender=sender,
            message=message,
            role=role
        )
        db.add(chat)
        db.commit()
        db.refresh(chat)
        return chat
    
    @staticmethod
    def get_conversation_history(
        db: Session,
        whatsapp_number: str,
        limit: int = 50
    ) -> List[dict]:
        """
        Retorna histórico de conversas
        
        Args:
            db: Sessão do banco de dados
            whatsapp_number: Número WhatsApp
            limit: Número máximo de mensagens
        
        Returns:
            Lista de mensagens formatadas para Claude
        """
        messages = db.query(ChatMessage).filter(
            ChatMessage.whatsapp_number == whatsapp_number
        ).order_by(ChatMessage.created_at.desc()).limit(limit).all()
        
        # Inverte para ordem cronológica
        messages.reverse()
        
        return [
            {
                "role": msg.role,
                "content": msg.message
            }
            for msg in messages
        ]


class QualificationFieldService:
    """Serviço para rastrear campos de qualificação"""
    
    @staticmethod
    def create_or_get_fields(
        db: Session,
        whatsapp_number: str
    ):
        """Cria ou retorna registro de campos"""
        fields = db.query(QualificationField).filter(
            QualificationField.whatsapp_number == whatsapp_number
        ).first()
        
        if not fields:
            fields = QualificationField(
                whatsapp_number=whatsapp_number
            )
            db.add(fields)
            db.commit()
            db.refresh(fields)
        
        return fields
    
    @staticmethod
    def update_fields(
        db: Session,
        whatsapp_number: str,
        has_name: bool = None,
        has_interest: bool = None,
        has_necessity: bool = None
    ):
        """Atualiza status dos campos coletados"""
        fields = QualificationFieldService.create_or_get_fields(
            db, whatsapp_number
        )
        
        if has_name is not None:
            fields.has_name = has_name
        if has_interest is not None:
            fields.has_interest = has_interest
        if has_necessity is not None:
            fields.has_necessity = has_necessity
        
        fields.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(fields)
        
        return fields
