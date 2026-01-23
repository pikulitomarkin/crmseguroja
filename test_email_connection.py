"""
Script de teste para verificar conexão IMAP e leitura de e-mails
"""
import imaplib
import email
from email.header import decode_header
from config.settings import settings


def test_imap_connection():
    """Testa conexão IMAP"""
    print("=" * 60)
    print("🧪 TESTE DE CONEXÃO IMAP")
    print("=" * 60)
    
    # Valida configurações
    if not settings.SMTP_USER:
        print("❌ SMTP_USER não configurado")
        return False
    
    if not settings.SMTP_PASSWORD:
        print("❌ SMTP_PASSWORD não configurado")
        return False
    
    print(f"📧 Conta: {settings.SMTP_USER}")
    print(f"🖥️  Servidor SMTP: {settings.SMTP_SERVER}")
    
    # Determina servidor IMAP
    if "gmail" in settings.SMTP_SERVER.lower():
        imap_server = "imap.gmail.com"
        print("📮 Detectado: Gmail")
        print("⚠️  Lembre-se: Use uma senha de app, não sua senha normal!")
        print("   Gere em: https://myaccount.google.com/apppasswords")
    elif "outlook" in settings.SMTP_SERVER.lower() or "hotmail" in settings.SMTP_SERVER.lower():
        imap_server = "outlook.office365.com"
        print("📮 Detectado: Outlook/Hotmail")
    elif "yahoo" in settings.SMTP_SERVER.lower():
        imap_server = "imap.mail.yahoo.com"
        print("📮 Detectado: Yahoo")
    else:
        imap_server = settings.SMTP_SERVER.replace("smtp", "imap")
        print(f"📮 Servidor IMAP: {imap_server}")
    
    print("\n🔌 Conectando ao servidor IMAP...")
    
    try:
        # Conecta
        mail = imaplib.IMAP4_SSL(imap_server)
        print("✅ Conexão SSL estabelecida")
        
        # Login
        mail.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        print("✅ Login realizado com sucesso")
        
        # Lista pastas
        print("\n📁 Pastas disponíveis:")
        status, folders = mail.list()
        if status == "OK":
            for folder in folders[:5]:  # Mostra primeiras 5
                print(f"   - {folder.decode()}")
        
        # Seleciona INBOX
        status, messages = mail.select("INBOX")
        if status == "OK":
            num_messages = int(messages[0])
            print(f"\n📬 Caixa de entrada: {num_messages} mensagens totais")
        
        # Busca não lidos
        status, unread = mail.search(None, "UNSEEN")
        if status == "OK":
            unread_ids = unread[0].split()
            print(f"📩 E-mails não lidos: {len(unread_ids)}")
            
            if unread_ids:
                print("\n📧 Últimos 3 e-mails não lidos:")
                for email_id in unread_ids[-3:]:
                    try:
                        status, msg_data = mail.fetch(email_id, "(RFC822)")
                        raw_email = msg_data[0][1]
                        msg = email.message_from_bytes(raw_email)
                        
                        subject = msg.get("Subject", "")
                        from_header = msg.get("From", "")
                        
                        # Decodifica subject
                        decoded_parts = decode_header(subject)
                        decoded_subject = ""
                        for part, encoding in decoded_parts:
                            if isinstance(part, bytes):
                                decoded_subject += part.decode(encoding or "utf-8", errors="ignore")
                            else:
                                decoded_subject += part
                        
                        print(f"\n   📨 De: {from_header}")
                        print(f"   📋 Assunto: {decoded_subject[:60]}...")
                    except Exception as e:
                        print(f"   ❌ Erro ao ler e-mail: {str(e)}")
        
        # Fecha conexão
        mail.close()
        mail.logout()
        
        print("\n" + "=" * 60)
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("=" * 60)
        print("\n💡 Dica: Execute 'python email_monitor.py --once' para processar e-mails")
        
        return True
    
    except imaplib.IMAP4.error as e:
        print(f"\n❌ Erro de autenticação IMAP: {str(e)}")
        print("\n💡 Dicas:")
        print("   1. Verifique se SMTP_USER e SMTP_PASSWORD estão corretos")
        print("   2. Para Gmail, use uma senha de app (não a senha normal)")
        print("   3. Para Gmail, ative IMAP nas configurações")
        print("   4. Alguns provedores exigem configurações especiais")
        return False
    
    except Exception as e:
        print(f"\n❌ Erro ao conectar: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False


if __name__ == "__main__":
    test_imap_connection()
