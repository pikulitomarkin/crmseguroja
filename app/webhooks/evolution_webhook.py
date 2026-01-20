"""
FastAPI Webhook para integração com Evolution API
"""
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Optional
from datetime import datetime
import asyncio
import logging
from config.settings import settings
from app.database.models import init_db, get_session
from app.services.ai_service import AIService
from app.services.evolution_service import EvolutionService
from app.services.notification_service import NotificationService
from app.services.database_service import (
    LeadService, MessageService, QualificationFieldService
)
from app.core.qualification import QualificationEngine

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializa FastAPI
app = FastAPI(
    title="CRM WhatsApp Integration",
    description="Integração Evolution API + OpenAI + Dashboard CRM",
    version="1.0.0"
)

# Inicializa banco de dados
engine = init_db(settings.DATABASE_URL)

# Serviços serão inicializados quando necessário
def get_ai_service():
    """Lazy initialization do AI Service"""
    return AIService()

def get_evolution_service():
    """Lazy initialization do Evolution Service"""
    return EvolutionService()

def get_qualification_engine():
    """Lazy initialization do Qualification Engine"""
    return QualificationEngine()


@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "ok",
        "message": "CRM System is running",
        "webhook_path": settings.API_WEBHOOK_PATH
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "timestamp": asyncio.get_event_loop().time()
    }


@app.get(f"{settings.API_WEBHOOK_PATH}/{{event_type:path}}")
@app.get(settings.API_WEBHOOK_PATH)
async def webhook_get_handler(event_type: str = ""):
    """
    GET handler para validação do webhook pela Evolution API
    """
    return JSONResponse(
        {"status": "ok", "message": "Webhook is active", "event_type": event_type},
        status_code=200
    )


@app.post(f"{settings.API_WEBHOOK_PATH}/{{event_type:path}}")
@app.post(settings.API_WEBHOOK_PATH)
async def webhook_handler(request: Request, background_tasks: BackgroundTasks, event_type: str = ""):
    """
    Webhook handler para mensagens da Evolution API
    
    Recebe todos os eventos da Evolution API
    """
    try:
        payload = await request.json()
        event = payload.get('event', 'unknown')
        logger.info(f"Webhook recebido [{event_type}]: {event}")
        
        # Ignora eventos que não são mensagens
        if event not in ['messages.upsert', 'messages-upsert']:
            return JSONResponse(
                {"status": "ok", "message": f"Event {event} ignored"},
                status_code=200
            )
        
        # Extrai dados da mensagem
        data = payload.get("data", {})
        
        # Se data for lista, pega o primeiro item
        if isinstance(data, list):
            if not data:
                return JSONResponse(
                    {"status": "ok", "message": "Empty data list"},
                    status_code=200
                )
            data = data[0]
        
        instance = data.get("instanceId", "")
        
        # A Evolution API pode enviar em dois formatos:
        # Formato 1: data.message contém key e message
        # Formato 2: data contém key e message diretamente
        if "message" in data and isinstance(data["message"], dict) and "key" in data["message"]:
            # Formato 1: data.message.key e data.message.message
            message_obj = data.get("message", {})
            whatsapp_number = message_obj.get("key", {}).get("remoteJid", "").split("@")[0]
            message_text = (
                message_obj.get("message", {}).get("conversation", "") or
                message_obj.get("message", {}).get("extendedTextMessage", {}).get("text", "")
            )
        else:
            # Formato 2: data.key e data.message diretamente
            whatsapp_number = data.get("key", {}).get("remoteJid", "").split("@")[0]
            message_text = (
                data.get("message", {}).get("conversation", "") or
                data.get("message", {}).get("extendedTextMessage", {}).get("text", "")
            )
        
        if not whatsapp_number or not message_text:
            logger.info(f"Mensagem ignorada - whatsapp: {whatsapp_number}, texto: {message_text}")
            return JSONResponse(
                {"status": "ok", "message": "Invalid message format"},
                status_code=200
            )
        
        # Processa em background
        background_tasks.add_task(
            process_message,
            whatsapp_number=whatsapp_number,
            message_text=message_text
        )
        
        return JSONResponse(
            {"status": "ok", "message": "Message received"},
            status_code=200
        )
    
    except Exception as e:
        logger.error(f"Erro ao processar webhook: {str(e)}")
        return JSONResponse(
            {"status": "error", "message": str(e)},
            status_code=500
        )


async def process_message(whatsapp_number: str, message_text: str):
    """
    Processa uma mensagem recebida
    
    Args:
        whatsapp_number: Número WhatsApp do remetente
        message_text: Conteúdo da mensagem
    """
    db = get_session(engine)
    notification_service = NotificationService(db)
    
    try:
        # 1. Verifica se IA ainda deve responder
        if not LeadService.is_ia_active(db, whatsapp_number):
            logger.info(f"IA desativada para {whatsapp_number}")
            return
        
        # 2. Cria ou recupera lead
        qualification_engine = get_qualification_engine()
        customer_type = qualification_engine.classify_customer([
            {"content": message_text}
        ])
        lead = LeadService.create_or_get_lead(db, whatsapp_number, customer_type)
        
        # 3. Salva mensagem do usuário
        MessageService.save_message(
            db, whatsapp_number, "user", message_text, role="user"
        )
        
        # 4. Extrai dados de qualificação
        conversation = MessageService.get_conversation_history(db, whatsapp_number)
        ai_service = get_ai_service()
        extracted_data = ai_service.extract_qualification_data(conversation)
        
        # Atualiza lead com dados extraídos
        if extracted_data.get("name"):
            LeadService.update_lead(db, lead, name=extracted_data["name"])
            QualificationFieldService.update_fields(
                db, whatsapp_number, has_name=True
            )
        
        if extracted_data.get("interest"):
            LeadService.update_lead(db, lead, interest=extracted_data["interest"])
            QualificationFieldService.update_fields(
                db, whatsapp_number, has_interest=True
            )
        
        if extracted_data.get("necessity"):
            LeadService.update_lead(db, lead, necessity=extracted_data["necessity"])
            QualificationFieldService.update_fields(
                db, whatsapp_number, has_necessity=True
            )
        
        # 5. Verifica se deve transferir para humano
        should_transfer, reason = qualification_engine.should_transition_to_human(
            extracted_data,
            conversation
        )
        
        if should_transfer:
            logger.info(f"Transferindo lead {whatsapp_number}: {reason}")
            
            # Desativa IA
            LeadService.mark_qualified(db, lead)
            
            # Notifica admin
            await notification_service.notify_admin_lead_qualified(
                extracted_data,
                whatsapp_number
            )
            
            # Envia mensagem de finalização ao cliente
            final_message = (
                "Perfeito! 😊 Coletei todas as informações. "
                "Um consultor especializado entrará em contato em breve para discutir "
                "as melhores soluções para você. Muito obrigado!"
            )
            evolution_service = get_evolution_service()
            await evolution_service.send_message(whatsapp_number, final_message)
            
            return
        
        # 6. Gera resposta da IA
        ai_response = ai_service.get_response(
            user_message=message_text,
            conversation_history=conversation,
            customer_type=customer_type
        )
        
        # 7. Salva resposta da IA
        MessageService.save_message(
            db, whatsapp_number, "ai", ai_response, role="assistant"
        )
        
        # 8. Envia resposta via WhatsApp
        evolution_service = get_evolution_service()
        await evolution_service.send_message(whatsapp_number, ai_response)
        
        logger.info(f"Mensagem processada e enviada para {whatsapp_number}")
    
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {str(e)}")
        try:
            if not evolution_service:
                evolution_service = get_evolution_service()
            await evolution_service.send_message(
                whatsapp_number,
                "Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente."
            )
        except:
            pass
    
    finally:
        db.close()


# ==================== ROTAS DE API PARA DASHBOARD ====================

@app.get("/api/leads/stats")
async def get_leads_stats():
    """Retorna estatísticas de leads"""
    try:
        db = get_session(engine)
        
        leads = db.query(Lead).all()
        today = datetime.now().date()
        
        stats = {
            "total_leads": len(leads),
            "novos_hoje": len([l for l in leads if l.created_at.date() == today]),
            "qualificados": len([l for l in leads if l.status == "qualificado"]),
            "em_negociacao": len([l for l in leads if l.status == "em_negociacao"]),
            "convertidos": len([l for l in leads if l.status == "convertido"]),
            "perdidos": len([l for l in leads if l.status == "perdido"]),
            "taxa_qualificacao": (len([l for l in leads if l.status == "qualificado"]) / len(leads) * 100) if leads else 0,
            "taxa_conversao": (len([l for l in leads if l.status == "convertido"]) / len(leads) * 100) if leads else 0
        }
        
        db.close()
        return stats
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas: {str(e)}")
        return {"error": str(e)}


@app.get("/api/leads")
async def get_leads(status: Optional[str] = None, limit: int = 50):
    """Retorna lista de leads"""
    try:
        db = get_session(engine)
        
        query = db.query(Lead)
        
        if status:
            query = query.filter(Lead.status == status)
        
        leads = query.order_by(Lead.created_at.desc()).limit(limit).all()
        
        result = []
        for lead in leads:
            result.append({
                "id": lead.id,
                "name": lead.name,
                "whatsapp_number": lead.whatsapp_number,
                "email": lead.email,
                "status": lead.status,
                "qualification_score": lead.qualification_score,
                "qualification_data": lead.qualification_data,
                "created_at": lead.created_at.isoformat() if lead.created_at else None,
                "updated_at": lead.updated_at.isoformat() if lead.updated_at else None
            })
        
        db.close()
        return result
    except Exception as e:
        logger.error(f"Erro ao buscar leads: {str(e)}")
        return []


@app.get("/api/leads/{lead_id}/messages")
async def get_lead_messages(lead_id: int):
    """Retorna mensagens de um lead"""
    try:
        db = get_session(engine)
        
        messages = db.query(ChatMessage).filter(
            ChatMessage.lead_id == lead_id
        ).order_by(ChatMessage.created_at.asc()).all()
        
        result = []
        for msg in messages:
            result.append({
                "id": msg.id,
                "lead_id": msg.lead_id,
                "sender": msg.sender,
                "message": msg.message,
                "created_at": msg.created_at.isoformat() if msg.created_at else None
            })
        
        db.close()
        return result
    except Exception as e:
        logger.error(f"Erro ao buscar mensagens: {str(e)}")
        return []


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT
    )
