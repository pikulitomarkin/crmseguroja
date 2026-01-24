"""
Serviço de integração com Evolution API (WhatsApp)
"""
import asyncio
import aiohttp
from typing import Optional
from config.settings import settings


class EvolutionService:
    """Serviço para interagir com Evolution API"""
    
    def __init__(self):
        base_url = settings.EVOLUTION_API_URL
        # Garante que a URL tenha o protocolo https://
        if not base_url.startswith('http://') and not base_url.startswith('https://'):
            base_url = f'https://{base_url}'
        # Remove barra final se existir para evitar barra dupla
        self.base_url = base_url.rstrip('/')
        self.api_key = settings.EVOLUTION_API_KEY
        self.instance_name = settings.EVOLUTION_INSTANCE_NAME
    
    def _get_headers(self) -> dict:
        """Retorna headers para requisições à API"""
        return {
            "Content-Type": "application/json",
            "apikey": self.api_key
        }
    
    async def send_message(
        self,
        whatsapp_number: str,
        message: str,
        show_typing: bool = True
    ) -> bool:
        """
        Envia uma mensagem via WhatsApp
        
        Args:
            whatsapp_number: Número do WhatsApp (ex: 5511999999999)
            message: Conteúdo da mensagem
            show_typing: Se deve mostrar "digitando..." antes de enviar
        
        Returns:
            True se enviado com sucesso
        """
        try:
            # Envia indicador de digitação e mensagem em paralelo para ser mais rápido
            if show_typing:
                asyncio.create_task(self._send_typing_indicator(whatsapp_number))
                await asyncio.sleep(settings.TYPING_DELAY)
            
            url = f"{self.base_url}/message/sendText/{self.instance_name}"
            
            payload = {
                "number": whatsapp_number,
                "text": message
            }
            
            print(f"[EVOLUTION] POST {url}")
            print(f"[EVOLUTION] Payload: number={whatsapp_number}, text_length={len(message)}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    headers=self._get_headers(),
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response_text = await response.text()
                    print(f"[EVOLUTION] Response Status: {response.status}")
                    print(f"[EVOLUTION] Response Body: {response_text[:200]}...")
                    
                    if response.status in [200, 201]:
                        print(f"[EVOLUTION] ✅ Mensagem enviada com sucesso")
                        return True
                    else:
                        print(f"[EVOLUTION] ❌ Erro ao enviar mensagem: {response.status} - {response_text}")
                        return False
        
        except Exception as e:
            print(f"Erro ao enviar mensagem via Evolution API: {str(e)}")
            return False
    
    async def _send_typing_indicator(self, whatsapp_number: str) -> bool:
        """
        Envia indicador de digitação
        
        Args:
            whatsapp_number: Número do WhatsApp
        
        Returns:
            True se enviado com sucesso
        """
        try:
            url = f"{self.base_url}/chat/togglePresence/{self.instance_name}"
            
            payload = {
                "number": whatsapp_number,
                "presence": "composing"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    headers=self._get_headers(),
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    return response.status in [200, 201]
        
        except Exception as e:
            print(f"Erro ao enviar typing indicator: {str(e)}")
            return False
    
    async def send_notification(
        self,
        whatsapp_number: str,
        message: str
    ) -> bool:
        """
        Envia notificação (sem typing indicator)
        
        Args:
            whatsapp_number: Número do WhatsApp
            message: Conteúdo da mensagem
        
        Returns:
            True se enviado com sucesso
        """
        print(f"[EVOLUTION] Enviando notificação para: {whatsapp_number}")
        print(f"[EVOLUTION] URL base: {self.base_url}")
        print(f"[EVOLUTION] Instance: {self.instance_name}")
        
        result = await self.send_message(whatsapp_number, message, show_typing=False)
        
        if result:
            print(f"[EVOLUTION] ✅ Notificação enviada com sucesso para {whatsapp_number}")
        else:
            print(f"[EVOLUTION] ❌ Falha ao enviar notificação para {whatsapp_number}")
        
        return result
