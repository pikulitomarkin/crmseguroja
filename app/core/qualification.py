"""
Lógica de qualificação de leads
"""
from typing import Tuple, Dict
from app.services.ai_service import AIService
from app.core.flow_manager import FlowManager


class QualificationEngine:
    """Motor de qualificação de leads"""
    
    def __init__(self):
        self.ai = AIService()
        self.flow_manager = FlowManager()
        # Manter campos legados por compatibilidade
        self.required_fields = ["name", "interest", "necessity"]
    
    def is_lead_qualified(self, qualification_data: Dict) -> bool:
        """
        Verifica se um lead está qualificado (usando novo sistema de fluxos)
        
        Args:
            qualification_data: Dicionário com flow_type e dados coletados
        
        Returns:
            True se lead está qualificado
        """
        flow_type = qualification_data.get("flow_type")
        
        if not flow_type:
            # Sistema legado - manter compatibilidade
            fields_filled = sum([
                bool(qualification_data.get("name")),
                bool(qualification_data.get("interest")),
                bool(qualification_data.get("necessity"))
            ])
            return fields_filled >= 3
        
        # Novo sistema - verifica se fluxo está completo
        return self.flow_manager.is_flow_complete(flow_type, qualification_data)
    
    def get_qualification_progress(self, qualification_data: Dict) -> Tuple[float, list]:
        """
        Calcula o progresso de qualificação
        
        Args:
            qualification_data: Dicionário com dados coletados
        
        Returns:
            Tupla (percentage: float, missing_fields: list)
        """
        flow_type = qualification_data.get("flow_type")
        
        if not flow_type:
            # Sistema legado
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
        
        # Novo sistema
        required = self.flow_manager.REQUIRED_FIELDS.get(flow_type, [])
        if not required:
            return 0, []
        
        fields_filled = sum([
            1 for field in required
            if qualification_data.get(field)
        ])
        
        percentage = (fields_filled / len(required)) * 100
        missing_fields = [
            field for field in required
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
        chat_history: list,
        flow_step: str = None
    ) -> Tuple[bool, str]:
        """
        Determina se o lead deve ser transferido para atendente humano
        
        Args:
            qualification_data: Dados coletados
            chat_history: Histórico de conversas
            flow_step: Etapa atual do fluxo
        
        Returns:
            Tupla (should_transfer: bool, reason: str)
        """
        flow_type = qualification_data.get("flow_type")
        
        # Fluxos que transferem imediatamente
        if self.flow_manager.should_transfer_to_human(flow_step or "menu_principal", flow_type, qualification_data):
            return True, "fluxo_completo_ou_direto"
        
        # Se chat ficou muito longo sem qualificar, transferir
        if len(chat_history) > 25:
            return True, "tempo_limite_excedido"
        
        # Se cliente mencionou orçamento/preço (não aplicável a novos fluxos)
        last_messages = " ".join([
            msg.get("content", "").lower()
            for msg in chat_history[-5:]
        ])
        
        if any(word in last_messages for word in ["preço", "valor", "cotação", "orçamento", "quanto custa"]):
            # No novo fluxo, IA deve lidar com isso
            pass
        
        return False, None
