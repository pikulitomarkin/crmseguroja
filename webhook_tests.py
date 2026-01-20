"""
Exemplo de teste de webhook com curl
Execute este arquivo para gerar comandos curl de teste
"""

def generate_curl_commands():
    """Gera comandos curl para testar o webhook"""
    
    commands = {
        "Test 1: Mensagem Simples": """curl -X POST http://localhost:8000/webhook/evolution ^
  -H "Content-Type: application/json" ^
  -d ^{
  "data": {
    "instanceId": "test-instance",
    "message": {
      "key": {
        "remoteJid": "5511999999999@s.whatsapp.net"
      },
      "message": {
        "conversation": "Olá! Como posso ajudar?"
      }
    }
  }
}^""",
        
        "Test 2: Usuário Perguntando Nome": """curl -X POST http://localhost:8000/webhook/evolution ^
  -H "Content-Type: application/json" ^
  -d ^{
  "data": {
    "instanceId": "test-instance",
    "message": {
      "key": {
        "remoteJid": "5511999999999@s.whatsapp.net"
      },
      "message": {
        "conversation": "Meu nome é João Silva"
      }
    }
  }
}^""",
        
        "Test 3: Usuário Informando Interesse": """curl -X POST http://localhost:8000/webhook/evolution ^
  -H "Content-Type: application/json" ^
  -d ^{
  "data": {
    "instanceId": "test-instance",
    "message": {
      "key": {
        "remoteJid": "5511999999999@s.whatsapp.net"
      },
      "message": {
        "conversation": "Procuro um software de automação de marketing"
      }
    }
  }
}^""",
        
        "Test 4: Qualificação Completa": """curl -X POST http://localhost:8000/webhook/evolution ^
  -H "Content-Type: application/json" ^
  -d ^{
  "data": {
    "instanceId": "test-instance",
    "message": {
      "key": {
        "remoteJid": "5511999999999@s.whatsapp.net"
      },
      "message": {
        "conversation": "Preciso integrar com meu CRM atual para automatizar contatos"
      }
    }
  }
}^""",
    }
    
    print("=" * 70)
    print("🧪 COMANDOS PARA TESTAR WEBHOOK")
    print("=" * 70)
    print("\nCertifique-se de que o servidor FastAPI está rodando:")
    print("  python -m uvicorn app.webhooks.evolution_webhook:app --reload\n")
    
    for name, command in commands.items():
        print(f"\n{name}")
        print("-" * 70)
        print(command)
        print()
    
    print("\n" + "=" * 70)
    print("NOTAS IMPORTANTES:")
    print("=" * 70)
    print("""
1. Substitua "5511999999999" pelo número que deseja testar
2. Aguarde alguns segundos entre requisições
3. Verifique o banco de dados e dashboard para ver o progresso
4. Todos os testes usam o mesmo número (para simular conversa contínua)

Para testar com um número diferente:
  - Altere "5511999999999" nos comandos acima
  
DICAS:
- Use ngrok para testar com a Evolution API real:
  ngrok http 8000
  
- Configure o webhook na Evolution API com a URL do ngrok:
  https://seu-ngrok-url.ngrok.io/webhook/evolution
""")


if __name__ == "__main__":
    generate_curl_commands()
