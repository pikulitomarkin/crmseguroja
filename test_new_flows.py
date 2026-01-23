"""
Script de teste para os novos fluxos de atendimento
"""
from app.core.flow_manager import FlowManager
from app.core.prompts import get_system_prompt

def test_menu_detection():
    """Testa detecção de opções do menu"""
    print("\n🧪 Testando detecção de menu...")
    fm = FlowManager()
    
    tests = [
        ("1", "seguro"),
        ("2", "consorcio"),
        ("seguro", "seguro"),
        ("consórcio", "consorcio"),
        ("sinistro", "sinistro"),
        ("quero falar com um humano", "falar_humano"),
    ]
    
    for input_msg, expected in tests:
        result = fm.detect_menu_choice(input_msg)
        status = "✅" if result == expected else "❌"
        print(f"  {status} '{input_msg}' → {result} (esperado: {expected})")

def test_insurance_detection():
    """Testa detecção de tipo de seguro"""
    print("\n🧪 Testando detecção de tipo de seguro...")
    fm = FlowManager()
    
    tests = [
        ("auto", "seguro_auto"),
        ("seguro de carro", "seguro_auto"),
        ("residencial", "seguro_residencial"),
        ("casa", "seguro_residencial"),
        ("vida", "seguro_vida"),
    ]
    
    for input_msg, expected in tests:
        result = fm.detect_insurance_type(input_msg)
        status = "✅" if result == expected else "❌"
        print(f"  {status} '{input_msg}' → {result} (esperado: {expected})")

def test_field_extraction():
    """Testa extração de campos"""
    print("\n🧪 Testando extração de campos...")
    fm = FlowManager()
    
    tests = [
        ("123.456.789-00", "cpf", "12345678900"),
        ("12.345.678/0001-90", "cnpj", "12345678000190"),
        ("ABC1234", "placa", "ABC1234"),
        ("01234-567", "cep", "01234567"),
        ("11999998888", "phone", "11999998888"),
        ("sim", "yes_no", "sim"),
        ("não", "yes_no", "não"),
    ]
    
    for input_msg, field_type, expected in tests:
        result = fm.extract_field_from_message(input_msg, field_type)
        status = "✅" if result == expected else "❌"
        print(f"  {status} '{input_msg}' ({field_type}) → {result} (esperado: {expected})")

def test_required_fields():
    """Testa campos obrigatórios por fluxo"""
    print("\n🧪 Testando campos obrigatórios...")
    fm = FlowManager()
    
    flows = [
        ("seguro_auto", 8),  # has_young_driver e second_email são opcionais
        ("seguro_residencial", 6),
        ("consorcio", 7),
        ("segunda_via", 1),
        ("sinistro", 2),
    ]
    
    for flow_type, expected_count in flows:
        fields = fm.REQUIRED_FIELDS.get(flow_type, [])
        status = "✅" if len(fields) == expected_count else "❌"
        print(f"  {status} {flow_type}: {len(fields)} campos (esperado: {expected_count})")
        if len(fields) != expected_count:
            print(f"     Campos: {fields}")

def test_flow_completion():
    """Testa verificação de conclusão de fluxo"""
    print("\n🧪 Testando verificação de conclusão...")
    fm = FlowManager()
    
    # Fluxo incompleto
    lead_data_incomplete = {
        "cpf_cnpj": "12345678900",
        "vehicle_plate": "ABC1234"
    }
    result = fm.is_flow_complete("seguro_auto", lead_data_incomplete)
    status = "✅" if not result else "❌"
    print(f"  {status} Seguro Auto incompleto: {result} (esperado: False)")
    
    # Fluxo completo
    lead_data_complete = {
        "cpf_cnpj": "12345678900",
        "vehicle_plate": "ABC1234",
        "phone": "11999999999",
        "whatsapp_contact": "11999999999",
        "cep_pernoite": "01234567",
        "profession": "Engenheiro",
        "marital_status": "Casado",
        "vehicle_usage": "particular",
        "has_young_driver": False
    }
    result = fm.is_flow_complete("seguro_auto", lead_data_complete)
    status = "✅" if result else "❌"
    print(f"  {status} Seguro Auto completo: {result} (esperado: True)")

def test_prompts():
    """Testa carregamento de prompts"""
    print("\n🧪 Testando prompts...")
    
    flows = [
        "menu_principal",
        "seguro_auto",
        "seguro_residencial",
        "consorcio",
        "segunda_via",
        "sinistro",
        "falar_humano",
        "outros_assuntos"
    ]
    
    for flow in flows:
        prompt = get_system_prompt(flow)
        status = "✅" if prompt and len(prompt) > 100 else "❌"
        length = len(prompt) if prompt else 0
        print(f"  {status} {flow}: {length} caracteres")

def test_next_field():
    """Testa determinação do próximo campo"""
    print("\n🧪 Testando próximo campo a coletar...")
    fm = FlowManager()
    
    lead_data = {
        "cpf_cnpj": "12345678900",
        "vehicle_plate": "ABC1234"
    }
    
    next_field = fm.get_next_field_to_collect("seguro_auto", lead_data)
    status = "✅" if next_field == "phone" else "❌"
    print(f"  {status} Próximo campo: {next_field} (esperado: phone)")
    
    label = fm.get_field_label(next_field) if next_field else ""
    print(f"     Label amigável: {label}")

def main():
    """Executa todos os testes"""
    print("=" * 60)
    print("🧪 TESTES DO NOVO SISTEMA DE FLUXOS")
    print("=" * 60)
    
    try:
        test_menu_detection()
        test_insurance_detection()
        test_field_extraction()
        test_required_fields()
        test_flow_completion()
        test_prompts()
        test_next_field()
        
        print("\n" + "=" * 60)
        print("✅ TODOS OS TESTES CONCLUÍDOS!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Erro nos testes: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
