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
        try:
            self.client = OpenAI(
                api_key=settings.OPENAI_API_KEY,
                timeout=15.0,  # Reduzido de 30s para 15s
                max_retries=1  # Reduzido de 2 para 1
            )
            self.model = settings.OPENAI_MODEL
        except Exception as e:
            raise Exception(f"Erro ao inicializar OpenAI: {str(e)}")
    
    def get_response(
        self,
        user_message: str,
        conversation_history: List[Dict],
        flow_step: str = "menu_principal",
        missing_fields: list = None
    ) -> str:
        """
        Obtém resposta da OpenAI para uma mensagem do usuário
        
        Args:
            user_message: Mensagem do usuário
            conversation_history: Histórico de conversas anteriores
            flow_step: Etapa atual do fluxo (menu_principal, seguro_auto, etc)
            missing_fields: Lista de campos obrigatórios faltantes
        
        Returns:
            Resposta da IA
        """
        try:
            # Formata o histórico para OpenAI
            messages = [
                {"role": "system", "content": get_system_prompt(flow_step, missing_fields)}
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
    
    def extract_lead_data_from_conversation(
        self,
        conversation_history: List[Dict],
        flow_type: str
    ) -> Dict:
        """
        Extrai dados específicos do lead baseado no tipo de fluxo
        
        Args:
            conversation_history: Histórico de conversas
            flow_type: Tipo de fluxo (seguro_auto, consorcio, etc)
        
        Returns:
            Dicionário com dados extraídos
        """
        try:
            # Formata histórico
            messages = [
                {
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                }
                for msg in conversation_history[-20:]  # Últimas 20 mensagens
            ]
            
            # Define os campos a extrair baseado no fluxo
            fields_map = {
                "seguro_auto": {
                    "name": "nome completo ou null",
                    "cpf_cnpj": "CPF ou CNPJ (apenas números) ou null",
                    "vehicle_plate": "placa do veículo ou null",
                    "phone": "telefone (apenas números) ou null",
                    "whatsapp_contact": "WhatsApp (apenas números) ou null",
                    "email": "e-mail ou null",
                    "second_email": "segundo e-mail ou null",
                    "cep_pernoite": "CEP de pernoite (apenas números) ou null",
                    "profession": "profissão ou null",
                    "marital_status": "estado civil ou null",
                    "vehicle_usage": "uso do veículo (particular/trabalho) ou null",
                    "has_young_driver": "condutor menor de 26 anos (true/false) ou null",
                    "interest": "observações ou informações extras mencionadas (modelo do carro, ano, cor, etc) ou null",
                    "necessity": "necessidades ou preferências mencionadas ou null"
                },
                "seguro_residencial": {
                    "name": "nome completo ou null",
                    "cpf_cnpj": "CPF ou CNPJ (apenas números) ou null",
                    "phone": "telefone (apenas números) ou null",
                    "whatsapp_contact": "WhatsApp (apenas números) ou null",
                    "email": "e-mail ou null",
                    "property_cep": "CEP do imóvel (apenas números) ou null",
                    "property_type": "tipo de imóvel ou null",
                    "property_value": "valor aproximado ou null",
                    "property_ownership": "próprio ou alugado ou null",
                    "interest": "observações ou informações extras mencionadas ou null"
                },
                "seguro_vida": {
                    "name": "nome completo ou null",
                    "cpf_cnpj": "CPF ou CNPJ (apenas números) ou null",
                    "phone": "telefone (apenas números) ou null",
                    "whatsapp_contact": "WhatsApp (apenas números) ou null",
                    "email": "e-mail ou null",
                    "interest": "observações, tipo de cobertura desejada ou informações extras ou null",
                    "necessity": "necessidades ou situação familiar mencionada ou null"
                },
                "seguro_empresarial": {
                    "name": "nome completo ou null",
                    "cpf_cnpj": "CPF ou CNPJ (apenas números) ou null",
                    "phone": "telefone (apenas números) ou null",
                    "whatsapp_contact": "WhatsApp (apenas números) ou null",
                    "email": "e-mail ou null",
                    "interest": "tipo de empresa, ramo de atividade ou informações extras ou null",
                    "necessity": "necessidades específicas da empresa ou null"
                },
                "consorcio": {
                    "name": "nome completo ou null",
                    "cpf_cnpj": "CPF ou CNPJ (apenas números) ou null",
                    "phone": "telefone (apenas números) ou null",
                    "whatsapp_contact": "WhatsApp (apenas números) ou null",
                    "email": "e-mail principal ou null",
                    "second_email": "segundo e-mail ou null",
                    "consortium_type": "tipo de consórcio (auto/imovel/servico) ou null",
                    "consortium_value": "valor da carta de crédito ou null",
                    "consortium_term": "prazo em meses ou null",
                    "has_previous_consortium": "já participou de consórcio (true/false) ou null",
                    "interest": "preferências ou observações mencionadas ou null"
                },
                "segunda_via": {
                    "cpf_cnpj": "CPF ou CNPJ (apenas números) ou null",
                    "interest": "produto (seguro/consorcio) ou null"
                },
                "sinistro": {
                    "name": "nome completo ou null",
                    "cpf_cnpj": "CPF ou CNPJ (apenas números) ou null",
                    "phone": "telefone (apenas números) ou null",
                    "whatsapp_contact": "WhatsApp (apenas números) ou null",
                    "vehicle_plate": "placa do veículo ou null",
                    "email": "e-mail ou null",
                    "interest": "tipo de sinistro e detalhes do que aconteceu ou null",
                    "necessity": "situação atual e urgência ou null"
                },
                "falar_humano": {
                    "name": "nome completo ou null",
                    "cpf_cnpj": "CPF ou CNPJ (apenas números) ou null",
                    "whatsapp_contact": "WhatsApp (apenas números) ou null",
                    "email": "e-mail ou null",
                    "interest": "motivo do contato ou null",
                    "necessity": "observações ou preferências ou null"
                }
            }
            
            fields = fields_map.get(flow_type, {})
            if not fields:
                return {}
            
            # Cria prompt de extração
            fields_json = json.dumps(fields, ensure_ascii=False, indent=2)
            extraction_prompt = f"""Analise TODA a conversa abaixo e extraia TODOS os dados mencionados pelo usuário.

IMPORTANTE:
- Extraia TODOS os dados que o usuário forneceu nas mensagens
- Se o usuário mencionou um valor mas depois corrigiu, use o valor MAIS RECENTE
- Para CPF/CNPJ, telefone, CEP: retorne APENAS números (sem pontos, traços ou espaços)
- Para campos booleanos (true/false): retorne true ou false baseado na resposta do usuário
- Se um dado NÃO foi mencionado, retorne null
- Se o usuário disse "não tenho", "não quero", "nenhum": retorne null para aquele campo

Campos a extrair:
{fields_json}

Retorne APENAS JSON válido no formato acima, sem explicação adicional."""
            
            messages.append({
                "role": "user",
                "content": extraction_prompt
            })
            
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=400,
                temperature=0.3,
                response_format={"type": "json_object"},
                messages=messages
            )
            
            # Parse JSON
            response_text = response.choices[0].message.content
            
            # Remove markdown se existir
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            data = json.loads(response_text.strip())
            return data
        
        except Exception as e:
            print(f"Erro ao extrair dados do lead: {str(e)}")
            return {}
