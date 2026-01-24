"""
FastAPI Webhook para integração com Evolution API
"""
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Optional
from datetime import datetime
import asyncio
import logging
from sqlalchemy import text
from config.settings import settings
from app.database.models import init_db, get_session, Lead, ChatMessage
from app.services.ai_service import AIService
from app.services.evolution_service import EvolutionService
from app.services.notification_service import NotificationService
from app.services.email_scheduler import email_scheduler
from app.services.database_service import (
    LeadService, MessageService, QualificationFieldService
)
from app.core.qualification import QualificationEngine
from app.core.flow_manager import FlowManager

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializa FastAPI
app = FastAPI(
    title="CRM WhatsApp Integration",
    description="Integração Evolution API + OpenAI + Dashboard CRM + Email Monitor",
    version="1.0.0"
)

# Inicializa banco de dados
engine = init_db(settings.DATABASE_URL)


@app.on_event("startup")
async def startup_event():
    """Evento executado ao iniciar a aplicação"""
    logger.info("🚀 Iniciando sistema CRM...")
    
    # Inicia scheduler de e-mails (verifica a cada 24 horas)
    email_scheduler.start(interval_hours=24)
    
    logger.info("✅ Sistema CRM iniciado com sucesso")


@app.on_event("shutdown")
async def shutdown_event():
    """Evento executado ao encerrar a aplicação"""
    logger.info("🛑 Encerrando sistema CRM...")
    
    # Para scheduler de e-mails
    email_scheduler.stop()
    
    logger.info("✅ Sistema CRM encerrado")

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
    try:
        # Testa conexão com o banco
        db = get_session(engine)
        db.execute(text("SELECT 1"))
        db.close()
        db_status = "connected"
    except Exception as e:
        logger.error(f"Health check DB error: {str(e)}")
        db_status = "error"
    
    # Verifica status do scheduler de e-mails
    email_scheduler_status = {
        "running": email_scheduler.is_running,
        "next_run": email_scheduler.get_next_run_time().isoformat() if email_scheduler.get_next_run_time() else None
    }
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "email_scheduler": email_scheduler_status,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/email/check-now")
async def trigger_email_check():
    """Dispara verificação imediata de e-mails"""
    try:
        if not email_scheduler.is_running:
            return JSONResponse(
                {"status": "error", "message": "Email scheduler não está rodando"},
                status_code=400
            )
        
        email_scheduler.trigger_now()
        
        return {
            "status": "ok",
            "message": "Verificação de e-mails agendada para execução imediata"
        }
    except Exception as e:
        logger.error(f"Erro ao disparar verificação de e-mails: {str(e)}")
        return JSONResponse(
            {"status": "error", "message": str(e)},
            status_code=500
        )


@app.get("/api/email/status")
async def email_scheduler_status():
    """Retorna status do scheduler de e-mails"""
    next_run = email_scheduler.get_next_run_time()
    
    return {
        "status": "running" if email_scheduler.is_running else "stopped",
        "is_running": email_scheduler.is_running,
        "next_check": next_run.isoformat() if next_run else None,
        "email_account": settings.SMTP_USER or "Não configurado",
        "admin_whatsapp": settings.ADMIN_WHATSAPP or "Não configurado"
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
            key = message_obj.get("key", {})
            whatsapp_number = key.get("remoteJid", "").split("@")[0]
            from_me = key.get("fromMe", False)  # Verifica se é mensagem enviada pelo bot
            message_text = (
                message_obj.get("message", {}).get("conversation", "") or
                message_obj.get("message", {}).get("extendedTextMessage", {}).get("text", "")
            )
        else:
            # Formato 2: data.key e data.message diretamente
            key = data.get("key", {})
            whatsapp_number = key.get("remoteJid", "").split("@")[0]
            from_me = key.get("fromMe", False)  # Verifica se é mensagem enviada pelo bot
            message_text = (
                data.get("message", {}).get("conversation", "") or
                data.get("message", {}).get("extendedTextMessage", {}).get("text", "")
            )
        
        # Ignora mensagens enviadas pelo próprio bot
        # MAS: registra no log para debug
        if from_me:
            logger.warning(f"[{whatsapp_number}] Mensagem com fromMe=true ignorada: '{message_text[:50]}'")
            logger.warning(f"[{whatsapp_number}] Key completo: {key}")
            return JSONResponse(
                {"status": "ok", "message": "Bot message ignored (fromMe=true)"},
                status_code=200
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
    Processa uma mensagem recebida usando o novo sistema de fluxos
    
    Args:
        whatsapp_number: Número WhatsApp do remetente
        message_text: Conteúdo da mensagem
    """
    import time
    start_time = time.time()
    db = get_session(engine)
    notification_service = NotificationService(db)
    
    try:
        logger.info(f"[{whatsapp_number}] Iniciando processamento: '{message_text[:50]}'")
        
        # 1. Cria ou recupera lead
        lead = LeadService.create_or_get_lead(db, whatsapp_number, "novo")
        logger.info(f"[{whatsapp_number}] Lead ID: {lead.id}, IA Ativa: {lead.status_ia}, Etapa: {lead.flow_step}")
        
        # 2. SEMPRE salva mensagem do usuário
        MessageService.save_message(
            db, whatsapp_number, "user", message_text, role="user", lead_id=lead.id
        )
        db.commit()
        logger.info(f"[{whatsapp_number}] Mensagem do usuário salva")
        
        # 3. Inicializa serviços (IA sempre responde)
        ai_service = get_ai_service()
        flow_manager = FlowManager()
        qualification_engine = get_qualification_engine()
        conversation = MessageService.get_conversation_history(db, whatsapp_number)
        
        # 5. Gerencia navegação do fluxo
        current_step = lead.flow_step or "menu_principal"
        flow_type = lead.flow_type
        
        # Se está no menu principal, detecta escolha
        if current_step == "menu_principal":
            choice = flow_manager.detect_menu_choice(message_text)
            if choice:
                if choice == "seguro":
                    # Perguntar tipo de seguro
                    current_step = "escolher_seguro"
                elif choice == "consorcio":
                    current_step = "consorcio"
                    flow_type = "consorcio"
                elif choice in ["segunda_via", "sinistro", "falar_humano", "outros_assuntos"]:
                    current_step = choice
                    flow_type = choice
                
                # Atualiza lead
                LeadService.update_lead(db, lead, flow_step=current_step, flow_type=flow_type)
                db.commit()
        
        # Se está escolhendo tipo de seguro
        elif current_step == "escolher_seguro":
            insurance_type = flow_manager.detect_insurance_type(message_text)
            if insurance_type:
                current_step = insurance_type
                flow_type = insurance_type
                LeadService.update_lead(db, lead, flow_step=current_step, flow_type=flow_type)
                db.commit()
        
        # Se está em consórcio mas ainda não escolheu tipo
        elif current_step == "consorcio" and not lead.consortium_type:
            consortium_type = flow_manager.detect_consortium_type(message_text)
            if consortium_type:
                LeadService.update_lead(db, lead, consortium_type=consortium_type)
                db.commit()
        
        # 6. Extrai dados da mensagem atual
        lead_dict = {
            "name": lead.name,
            "email": lead.email,
            "second_email": lead.second_email,
            "cpf_cnpj": lead.cpf_cnpj,
            "phone": lead.phone,
            "whatsapp_contact": lead.whatsapp_contact,
            "vehicle_plate": lead.vehicle_plate,
            "cep_pernoite": lead.cep_pernoite,
            "profession": lead.profession,
            "marital_status": lead.marital_status,
            "vehicle_usage": lead.vehicle_usage,
            "has_young_driver": lead.has_young_driver,
            "property_cep": lead.property_cep,
            "property_type": lead.property_type,
            "property_value": lead.property_value,
            "property_ownership": lead.property_ownership,
            "consortium_type": lead.consortium_type,
            "consortium_value": lead.consortium_value,
            "consortium_term": lead.consortium_term,
            "has_previous_consortium": lead.has_previous_consortium,
            "flow_type": flow_type,
            "flow_step": current_step
        }
        
        # Extrai dados específicos do fluxo atual
        if flow_type:
            extracted = ai_service.extract_lead_data_from_conversation(conversation, flow_type)
            # Atualiza lead com dados extraídos
            for key, value in extracted.items():
                if value and value != "null" and not lead_dict.get(key):
                    lead_dict[key] = value
                    setattr(lead, key, value)
            
            db.commit()
        
        # 7. Verifica se deve transferir para humano
        should_transfer = flow_manager.should_transfer_to_human(current_step, flow_type, lead_dict)
        
        if should_transfer:
            logger.info(f"Transferindo lead {whatsapp_number}: {current_step}")
            
            # Marca como qualificado
            LeadService.mark_qualified(db, lead)
            db.commit()
            
            # Mensagem de finalização já será enviada pela IA com o prompt correto
            # Notifica admin em background
            async def notify_admin_background(service, data, number):
                try:
                    await service.notify_admin_lead_qualified(data, number)
                    logger.info(f"Admin notificado sobre lead {number}")
                except Exception as e:
                    logger.error(f"Erro ao notificar admin: {str(e)}")
            
            try:
                asyncio.create_task(
                    notify_admin_background(notification_service, lead_dict, whatsapp_number)
                )
            except Exception as e:
                logger.error(f"Erro ao criar task de notificação: {str(e)}")
        
        # 8. Gera resposta da IA com o prompt correto
        try:
            ai_response = ai_service.get_response(
                user_message=message_text,
                conversation_history=conversation,
                flow_step=current_step
            )
        except Exception as e:
            logger.error(f"Erro ao gerar resposta IA: {str(e)}")
            ai_response = "Desculpe, tive um problema técnico. Pode repetir sua mensagem?"
        
        # 9. Salva resposta da IA
        try:
            MessageService.save_message(
                db, whatsapp_number, "ai", ai_response, role="assistant", lead_id=lead.id
            )
            db.commit()
        except Exception as e:
            logger.error(f"Erro ao salvar mensagem IA: {str(e)}")
        
        # 10. Envia resposta via WhatsApp
        try:
            evolution_service = get_evolution_service()
            await evolution_service.send_message(whatsapp_number, ai_response)
            elapsed = time.time() - start_time
            logger.info(f"[{whatsapp_number}] ✅ Processado em {elapsed:.2f}s")
        except Exception as e:
            logger.error(f"[{whatsapp_number}] Erro ao enviar resposta: {str(e)}")
    
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"[{whatsapp_number}] ❌ Erro após {elapsed:.2f}s: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        try:
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
    db = None
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
        
        return stats
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas: {str(e)}")
        return {"error": str(e)}
    finally:
        if db:
            db.close()


@app.get("/api/leads")
async def get_leads(status: Optional[str] = None, limit: int = 50):
    """Retorna lista de leads"""
    db = None
    try:
        db = get_session(engine)
        
        query = db.query(Lead)
        
        if status:
            query = query.filter(Lead.status == status)
        
        leads = query.order_by(Lead.created_at.desc()).limit(limit).all()
        logger.info(f"Encontrados {len(leads)} leads no banco de dados")
        
        result = []
        for lead in leads:
            try:
                lead_dict = {
                    "id": lead.id,
                    "name": lead.name or "Aguardando qualificação",
                    "whatsapp_number": lead.whatsapp_number,
                    "email": lead.email,
                    "status": lead.status,
                    "qualification_score": int(lead.qualification_score) if lead.qualification_score else 0,
                    "qualification_data": lead.qualification_data if lead.qualification_data else {},
                    "created_at": lead.created_at.isoformat() if lead.created_at else None,
                    "updated_at": lead.updated_at.isoformat() if lead.updated_at else None
                }
                result.append(lead_dict)
            except Exception as e:
                logger.error(f"Erro ao serializar lead {lead.id}: {str(e)}")
                continue
        
        logger.info(f"Retornando {len(result)} leads serializados")
        return result
    except Exception as e:
        logger.error(f"Erro ao buscar leads: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return []
    finally:
        if db:
            db.close()


@app.get("/api/leads/{lead_id}/messages")
async def get_lead_messages(lead_id: int):
    """Retorna mensagens de um lead"""
    db = None
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
        
        return result
    except Exception as e:
        logger.error(f"Erro ao buscar mensagens: {str(e)}")
        return []
    finally:
        if db:
            db.close()


@app.post("/api/leads/{lead_id}/send-message")
async def send_message_to_lead(lead_id: int, request: Request):
    """Envia mensagem do humano para o lead via WhatsApp"""
    db = None
    try:
        db = get_session(engine)
        data = await request.json()
        message_text = data.get("message", "").strip()
        
        if not message_text:
            raise HTTPException(status_code=400, detail="Mensagem vazia")
        
        # Busca o lead
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead não encontrado")
        
        # Desativa IA e atualiza status para em_negociacao
        lead.status_ia = 0
        if lead.status == "qualificado":
            lead.status = "em_negociacao"
            logger.info(f"[{lead.whatsapp_number}] Status alterado: qualificado → em_negociacao")
        db.commit()
        
        logger.info(f"[{lead.whatsapp_number}] Humano enviando mensagem: {message_text[:50]}...")
        
        # Envia mensagem via Evolution API
        evolution = EvolutionService()
        success = await evolution.send_message(lead.whatsapp_number, message_text)
        
        if not success:
            raise HTTPException(status_code=500, detail="Falha ao enviar mensagem")
        
        # Salva mensagem no histórico
        chat_message = ChatMessage(
            lead_id=lead.id,
            whatsapp_number=lead.whatsapp_number,
            sender="human",
            message=message_text,
            role="assistant"
        )
        db.add(chat_message)
        db.commit()
        
        logger.info(f"[{lead.whatsapp_number}] Mensagem enviada pelo humano com sucesso")
        
        return {"success": True, "message": "Mensagem enviada com sucesso"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if db:
            db.close()


@app.post("/api/leads/{lead_id}/close")
async def close_conversation(lead_id: int, request: Request):
    """Encerra conversa com o lead"""
    db = None
    try:
        db = get_session(engine)
        data = await request.json()
        success = data.get("success", False)  # True = convertido, False = perdido
        
        # Busca o lead
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead não encontrado")
        
        # Atualiza status baseado no resultado
        old_status = lead.status
        if success:
            lead.status = "convertido"
            logger.info(f"[{lead.whatsapp_number}] Status: {old_status} → convertido ✅")
        else:
            lead.status = "perdido"
            logger.info(f"[{lead.whatsapp_number}] Status: {old_status} → perdido ❌")
        
        # Mantém IA desativada
        lead.status_ia = 0
        db.commit()
        
        return {
            "success": True, 
            "message": f"Conversa encerrada - Status: {lead.status}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao encerrar conversa: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if db:
            db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT
    )
