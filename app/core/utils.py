"""
Utilitários do Sistema
"""
import re
from typing import Optional


def sanitize_whatsapp_number(number: str) -> str:
    """
    Sanitiza número de WhatsApp
    
    Args:
        number: Número bruto
    
    Returns:
        Número sanitizado (apenas dígitos)
    """
    return re.sub(r"\D", "", number)


def format_whatsapp_number(number: str, country_code: str = "55") -> str:
    """
    Formata número para padrão WhatsApp
    
    Args:
        number: Número (com ou sem país)
        country_code: Código do país (padrão: 55 para Brasil)
    
    Returns:
        Número formatado
    """
    clean = sanitize_whatsapp_number(number)
    
    # Remove código de país se existir
    if clean.startswith(country_code):
        clean = clean[len(country_code):]
    
    # Remove primeiro 0 (DDI)
    if clean.startswith("0"):
        clean = clean[1:]
    
    return country_code + clean


def is_valid_email(email: str) -> bool:
    """Valida formato de email"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def extract_first_name(full_name: str) -> str:
    """
    Extrai primeiro nome
    
    Args:
        full_name: Nome completo
    
    Returns:
        Primeiro nome
    """
    if not full_name:
        return ""
    return full_name.split()[0].capitalize()


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Trunca texto
    
    Args:
        text: Texto original
        max_length: Comprimento máximo
    
    Returns:
        Texto truncado com "..."
    """
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text
