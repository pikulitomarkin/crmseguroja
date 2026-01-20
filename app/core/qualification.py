"""
Lógica de qualificação de leads
"""
from typing import Tuple, Dict
from app.services.ai_service import AIService


class QualificationEngine:
    """Motor de qualificação de leads"""
    
    def __init__(self):
        self.ai = AIService()
        self.required_fields = ["name", "interest", "necessity"]
    
    def is_lead_qualified(self, qualification_data: Dict) -> bool:
        """
        Verifica se um lead está qualificado (todos os campos preenchidos)
        
        Args:
            qualification_data: Dicionário com name, interest, necessity
        
        Returns:
            True se lead está qualificado
        """
        fields_filled = sum([
            bool(qualification_data.get("name")),
            bool(qualification_data.get("interest")),
            bool(qualification_data.get("necessity"))
        ])
        
        # Lead qualificado quando tem todos os 3 campos
        return fields_filled >= 3
    
    def get_qualification_progress(self, qualification_data: Dict) -> Tuple[float, list]:
        """
        Calcula o progresso de qualificação
        
        Args:
            qualification_data: Dicionário com dados coletados
        
        Returns:
            Tupla (percentage: float, missing_fields: list)
        """
        fields_filled = sum([
            bool(qualification_data.get("name")),
            bool(qualification_data.get("interest")),
            bool(qualification_data.get("necessity"))
        ])
        
        percentage = (fields_filled / len(self.required_fields)) * 100
        
        missing_fields = [
            field for field in self.required_fields
            if not qualification_data.get(field)
        ]
        
        return percentage, missing_fields
    
    def classify_customer(self, chat_history: list) -> str:
        """
        Classifica se o cliente é novo ou existente
        
        Args:
            chat_history: Histórico de conversas
        
        Returns:
            "novo" ou "existente"
        """
        # Se há muitas mensagens e já tem nome, provavelmente é um cliente existente
        # ou é uma conversa longa que devemos tratar como cliente
        
        # Análise simples: se houver menção a "cliente anterior", "já uso", "já comprei", etc
        keywords_existente = [
            "já uso", "já comprei", "cliente anterior", "volta", "retorno",
            "renovar", "upgrade", "continuação", "já sou cliente"
        ]
        
        full_text = " ".join([msg.get("content", "").lower() for msg in chat_history])
        
        if any(keyword in full_text for keyword in keywords_existente):
            return "existente"
        
        # Padrão: considera novo por default
        return "novo"
    
    def should_transition_to_human(
        self,
        qualification_data: Dict,
        chat_history: list
    ) -> Tuple[bool, str]:
        """
        Determina se o lead deve ser transferido para atendente humano
        
        Args:
            qualification_data: Dados coletados
            chat_history: Histórico de conversas
        
        Returns:
            Tupla (should_transfer: bool, reason: str)
        """
        # Qualificação completa
        if self.is_lead_qualified(qualification_data):
            return True, "lead_qualificado"
        
        # Se chat ficou muito longo sem qualificar completamente, transfer
        if len(chat_history) > 20:
            return True, "tempo_limite_excedido"
        
        # Se cliente mencionou orçamento/preço, deve ser transferido
        last_messages = " ".join([
            msg.get("content", "").lower()
            for msg in chat_history[-5:]
        ])
        
        if any(word in last_messages for word in ["preço", "valor", "cotação", "orçamento", "custa"]):
            return True, "cliente_pediu_preco"
        
        return False, None
