"""
Serviço de integração com OpenAI API
"""
import json
from typing import List, Dict
from openai import OpenAI
from config.settings import settings
from app.core.prompts import get_system_prompt


class AIService:
    """Serviço para interagir com OpenAI API"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
    
    def get_response(
        self,
        user_message: str,
        conversation_history: List[Dict],
        customer_type: str = "novo"
    ) -> str:
        """
        Obtém resposta da OpenAI para uma mensagem do usuário
        
        Args:
            user_message: Mensagem do usuário
            conversation_history: Histórico de conversas anteriores
            customer_type: "novo" ou "existente"
        
        Returns:
            Resposta da IA
        """
        try:
            # Formata o histórico para OpenAI
            messages = [
                {"role": "system", "content": get_system_prompt(customer_type)}
            ]
            
            for msg in conversation_history[-10:]:  # Últimas 10 mensagens
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
            
            # Adiciona a mensagem atual
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # Chama OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=500,
                temperature=0.7,
                messages=messages
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"Erro ao chamar OpenAI API: {str(e)}")
            return "Desculpe, houve um erro ao processar sua mensagem. Por favor, tente novamente."
    
    def extract_qualification_data(
        self,
        conversation_history: List[Dict]
    ) -> Dict:
        """
        Extrai dados de qualificação da conversa
        
        Args:
            conversation_history: Histórico de conversas
        
        Returns:
            Dicionário com dados extraídos (name, interest, necessity)
        """
        try:
            # Formata histórico
            messages = [
                {
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                }
                for msg in conversation_history[-15:]  # Últimas 15 mensagens
            ]
            
            # Prompt para extração
            extraction_prompt = """Analise esta conversa e extraia os seguintes dados em JSON:
            {
                "name": "nome da pessoa ou null",
                "interest": "interesse/produto mencionado ou null",
                "necessity": "necessidade específica ou null"
            }
            
            Retorne APENAS JSON válido, sem explicação."""
            
            messages.append({
                "role": "user",
                "content": extraction_prompt
            })
            
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=300,
                temperature=0.3,
                response_format={"type": "json_object"},
                messages=messages
            )
            
            # Tenta fazer parse do JSON
            response_text = response.choices[0].message.content
            
            # Remove markdown code blocks se existirem
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            data = json.loads(response_text.strip())
            return data
        
        except Exception as e:
            print(f"Erro ao extrair dados de qualificação: {str(e)}")
            return {"name": None, "interest": None, "necessity": None}
