"""
Modelos de Banco de Dados para o Sistema CRM
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Lead(Base):
    """Modelo para armazenar dados de leads"""
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    whatsapp_number = Column(String(20), unique=True, index=True)
    name = Column(String(150), nullable=True)
    email = Column(String(150), nullable=True)
    interest = Column(Text, nullable=True)
    necessity = Column(Text, nullable=True)
    qualification_score = Column(Float, default=0)
    qualification_data = Column(Text, nullable=True)  # JSON string
    status = Column(String(50), default="novo")  # novo, qualificado, em_atendimento, finalizado
    status_ia = Column(Integer, default=1)  # 1 = IA ativa, 0 = IA inativa (humano assumiu)
    customer_type = Column(String(20), default="novo")  # novo, existente
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    qualified_at = Column(DateTime, nullable=True)
    attended_by = Column(String(150), nullable=True)  # Nome do atendente que assumiu


class ChatMessage(Base):
    """Modelo para armazenar histórico de mensagens"""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, index=True)
    whatsapp_number = Column(String(20), index=True)
    sender = Column(String(20))  # "user" ou "ai"
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    role = Column(String(20), default="assistant")  # Para integração com Claude


class QualificationField(Base):
    """Modelo para rastrear quais campos foram coletados"""
    __tablename__ = "qualification_fields"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, index=True)
    whatsapp_number = Column(String(20), index=True)
    has_name = Column(Boolean, default=False)
    has_interest = Column(Boolean, default=False)
    has_necessity = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class NotificationLog(Base):
    """Modelo para rastrear notificações enviadas"""
    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, index=True)
    whatsapp_number = Column(String(20), index=True)
    notification_type = Column(String(50))  # email, whatsapp
    recipient = Column(String(150))
    status = Column(String(20))  # enviado, falha, pendente
    created_at = Column(DateTime, default=datetime.utcnow)
    error_message = Column(Text, nullable=True)


def init_db(database_url: str = "sqlite:///./crm_system.db"):
    """Inicializa o banco de dados"""
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False} if "sqlite" in database_url else {}
    )
    Base.metadata.create_all(bind=engine)
    return engine


def get_session(engine):
    """Retorna uma sessão do banco de dados"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()
