"""
FastAPI Webhook para integração com Evolution API
"""
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse
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


@app.post(f"{settings.API_WEBHOOK_PATH}/{{event_type:path}}")
@app.post(settings.API_WEBHOOK_PATH)
async def webhook_handler(request: Request, background_tasks: BackgroundTasks, event_type: str = ""):
    """
    Webhook handler para mensagens da Evolution API
    
    Recebe todos os eventos da Evolution API
    """
    try:
        payload = await request.json()
        logger.info(f"Webhook recebido [{event_type}]: {payload.get('event', 'unknown')}")
        
        # Processa apenas eventos de mensagens recebidas
        if event_type and "messages-upsert" not in event_type:
            return JSONResponse(
                {"status": "ok", "message": f"Event {event_type} ignored"},
                status_code=200
            )
        
        # Extrai dados da mensagem
        data = payload.get("data", {})
        instance = data.get("instanceId", "")
        message = data.get("message", {})
        
        if not message:
            return JSONResponse(
                {"status": "ok", "message": "No message data"},
                status_code=200
            )
        
        # Extrai número e conteúdo
        whatsapp_number = message.get("key", {}).get("remoteJid", "").split("@")[0]
        message_text = (
            message.get("message", {}).get("conversation", "") or
            message.get("message", {}).get("extendedTextMessage", {}).get("text", "")
        )
        
        if not whatsapp_number or not message_text:
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
        if not evolution_service:
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT
    )
