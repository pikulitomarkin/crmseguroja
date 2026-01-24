"""
Gerenciador de Fluxos de Atendimento
"""
from typing import Dict, Tuple, Optional
import re


class FlowManager:
    """Gerencia a navegação entre diferentes fluxos de atendimento"""
    
    # Mapeamento de opções do menu principal
    MENU_OPTIONS = {
        "1": "seguro",
        "2": "consorcio", 
        "3": "segunda_via",
        "4": "sinistro",
        "5": "falar_humano",
        "6": "outros_assuntos"
    }
    
    # Campos obrigatórios por fluxo (second_email é sempre opcional)
    REQUIRED_FIELDS = {
        "seguro_auto": [
            "cpf_cnpj", "vehicle_plate", "whatsapp_contact",
            "cep_pernoite", "profession", "marital_status", 
            "vehicle_usage", "has_young_driver"
        ],
        "seguro_residencial": [
            "name", "cpf_cnpj", "whatsapp_contact", "property_cep", "property_type",
            "property_value", "property_ownership"
        ],
        "seguro_vida": [
            "name", "whatsapp_contact", "cpf_cnpj", "email"
        ],
        "seguro_empresarial": [
            "name", "whatsapp_contact", "cpf_cnpj", "email"
        ],
        "consorcio": [
            "cpf_cnpj", "whatsapp_contact", "email",
            "consortium_type", "consortium_value", "consortium_term"
        ],
        "segunda_via": ["name", "cpf_cnpj", "whatsapp_contact"],
        "sinistro": ["name", "cpf_cnpj", "whatsapp_contact"],
        "outros_assuntos": ["cpf_cnpj", "name", "whatsapp_contact", "interest"]
    }
    
    def detect_menu_choice(self, message: str) -> Optional[str]:
        """
        Detecta qual opção do menu o usuário escolheu
        
        Args:
            message: Mensagem do usuário
            
        Returns:
            flow_type identificado ou None
        """
        message_lower = message.lower().strip()
        
        # DETECÇÃO AUTOMÁTICA DE SINISTRO (prioridade máxima)
        sinistro_keywords = [
            "batida", "bati", "bateu", "bateram", "colisão", "colisao", "colidi", 
            "choque", "pancada", "acidente", "trombei", "trombada", "abalroamento",
            "encostou", "fechada", "engavetamento", "perda total", "pt",
            "roubo", "roubado", "roubaram", "assalto", "furto", "furtaram",
            "levaram o carro", "levaram a moto", "sumiu", "desapareceu",
            "capotou", "capotamento", "virou", "tombou",
            "pegou fogo", "incêndio", "incendio", "queimou", "fogo", "curto circuito",
            "alagou", "alagamento", "enchente", "água no carro", "carro molhou",
            "vidro quebrado", "parabrisa", "para-brisa", "farol quebrado",
            "atropelamento", "atropelei", "atropelou", "pedestre",
            "sinistro", "ocorrência", "ocorrencia", "acionei o seguro", "acionar seguro"
        ]
        if any(keyword in message_lower for keyword in sinistro_keywords):
            return "sinistro"
        
        # Detecta número
        if message_lower in self.MENU_OPTIONS:
            return self.MENU_OPTIONS[message_lower]
        
        # Volta ao menu
        if message_lower in ["0", "menu", "voltar", "inicio"]:
            return "menu_principal"
        
        # Detecta por palavra-chave
        if "seguro" in message_lower and "segunda" not in message_lower:
            return "seguro"
        if "consórcio" in message_lower or "consorcio" in message_lower:
            return "consorcio"
        if "segunda via" in message_lower or "boleto" in message_lower:
            return "segunda_via"
        if "humano" in message_lower or "atendente" in message_lower or "pessoa" in message_lower:
            return "falar_humano"
        if "outro" in message_lower:
            return "outros_assuntos"
            
        return None
    
    def detect_insurance_type(self, message: str) -> Optional[str]:
        """
        Detecta o tipo de seguro escolhido
        
        Args:
            message: Mensagem do usuário
            
        Returns:
            Tipo de seguro ou None
        """
        message = message.lower().strip()
        
        # Detecta por número
        if message == "1":
            return "seguro_auto"
        if message == "2":
            return "seguro_residencial"
        if message == "3":
            return "seguro_vida"
        if message == "4":
            return "seguro_empresarial"
        
        # Detecta por palavra-chave
        if "auto" in message or "carro" in message or "veículo" in message or "veiculo" in message:
            return "seguro_auto"
        if "residencial" in message or "casa" in message or "imóvel" in message or "imovel" in message or "apartamento" in message:
            return "seguro_residencial"
        if "vida" in message:
            return "seguro_vida"
        if "empresa" in message:
            return "seguro_empresarial"
            
        return None
    
    def detect_consortium_type(self, message: str) -> Optional[str]:
        """
        Detecta o tipo de consórcio escolhido
        
        Args:
            message: Mensagem do usuário
            
        Returns:
            Tipo de consórcio ou None
        """
        message = message.lower().strip()
        
        # Detecta por número
        if message == "1":
            return "auto"
        if message == "2":
            return "imovel"
        if message == "3":
            return "servico"
        
        # Detecta por palavra-chave
        if "auto" in message or "carro" in message or "veículo" in message or "veiculo" in message:
            return "auto"
        if "imóvel" in message or "imovel" in message or "casa" in message or "apartamento" in message:
            return "imovel"
        if "serviço" in message or "servico" in message:
            return "servico"
            
        return None
    
    def extract_field_from_message(self, message: str, field_type: str) -> Optional[str]:
        """
        Extrai campos específicos da mensagem
        
        Args:
            message: Mensagem do usuário
            field_type: Tipo de campo (cpf, cnpj, placa, etc)
            
        Returns:
            Valor extraído ou None
        """
        message = message.strip()
        
        if field_type == "cpf":
            # Remove formatação e valida tamanho
            cpf = re.sub(r'[^\d]', '', message)
            if len(cpf) == 11:
                return cpf
                
        elif field_type == "cnpj":
            cnpj = re.sub(r'[^\d]', '', message)
            if len(cnpj) == 14:
                return cnpj
                
        elif field_type == "cpf_cnpj":
            doc = re.sub(r'[^\d]', '', message)
            if len(doc) == 11 or len(doc) == 14:
                return doc
                
        elif field_type == "placa":
            # Formato brasileiro: ABC1234 ou ABC1D23
            placa = re.sub(r'[^\w]', '', message).upper()
            if len(placa) == 7:
                return placa
                
        elif field_type == "phone":
            phone = re.sub(r'[^\d]', '', message)
            if len(phone) >= 10:
                return phone
                
        elif field_type == "cep":
            cep = re.sub(r'[^\d]', '', message)
            if len(cep) == 8:
                return cep
        
        # Campos de texto simples
        elif field_type in ["name", "email", "profession", "property_type"]:
            if len(message) > 2:
                return message
        
        # Campos de sim/não
        elif field_type == "yes_no":
            message_lower = message.lower()
            if any(word in message_lower for word in ["sim", "yes", "s"]):
                return "sim"
            if any(word in message_lower for word in ["não", "nao", "no", "n"]):
                return "não"
        
        return None
    
    def get_next_field_to_collect(self, flow_type: str, lead_data: Dict) -> Optional[str]:
        """
        Determina qual é o próximo campo a ser coletado
        
        Args:
            flow_type: Tipo de fluxo (seguro_auto, consorcio, etc)
            lead_data: Dados já coletados do lead
            
        Returns:
            Nome do próximo campo ou None se completo
        """
        if flow_type not in self.REQUIRED_FIELDS:
            return None
        
        required = self.REQUIRED_FIELDS[flow_type]
        
        for field in required:
            if not lead_data.get(field):
                return field
        
        # Todos os campos foram coletados
        return None
    
    def is_flow_complete(self, flow_type: str, lead_data: Dict) -> bool:
        """
        Verifica se o fluxo está completo
        
        Args:
            flow_type: Tipo de fluxo
            lead_data: Dados coletados
            
        Returns:
            True se todos os campos obrigatórios foram coletados
        """
        return self.get_next_field_to_collect(flow_type, lead_data) is None
    
    def should_transfer_to_human(self, flow_step: str, flow_type: str, lead_data: Dict) -> bool:
        """
        Determina se deve transferir para atendimento humano
        
        Args:
            flow_step: Etapa atual do fluxo
            flow_type: Tipo de fluxo
            lead_data: Dados coletados
            
        Returns:
            True se deve transferir
        """
        # Fluxos que sempre transferem imediatamente
        immediate_transfer = ["falar_humano", "sinistro", "outros_assuntos"]
        if flow_step in immediate_transfer:
            return True
        
        # Verifica se fluxo está completo
        if flow_type and self.is_flow_complete(flow_type, lead_data):
            return True
        
        return False
    
    def get_field_label(self, field_name: str) -> str:
        """
        Retorna o rótulo amigável do campo
        
        Args:
            field_name: Nome técnico do campo
            
        Returns:
            Rótulo amigável
        """
        labels = {
            "name": "Nome",
            "cpf_cnpj": "CPF ou CNPJ",
            "vehicle_plate": "Placa do veículo",
            "phone": "Telefone",
            "whatsapp_contact": "WhatsApp",
            "email": "E-mail",
            "second_email": "Segundo e-mail",
            "cep_pernoite": "CEP de pernoite do veículo",
            "profession": "Profissão",
            "marital_status": "Estado civil",
            "vehicle_usage": "Uso do veículo",
            "has_young_driver": "Condutor menor de 26 anos",
            "property_cep": "CEP do imóvel",
            "property_type": "Tipo de imóvel",
            "property_value": "Valor aproximado",
            "property_ownership": "Próprio ou alugado",
            "consortium_type": "Tipo de consórcio",
            "consortium_value": "Valor da carta de crédito",
            "consortium_term": "Prazo",
            "has_previous_consortium": "Já participou de consórcio antes"
        }
        return labels.get(field_name, field_name)
