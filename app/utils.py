import requests
import os

def send_whatsapp_buttons(to):
    """
    Envia um menu de opções simulado para o WhatsApp via API Twilio.
    """
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_whatsapp_number = os.getenv("TWILIO_PHONE_NUMBER")

    if not account_sid or not auth_token or not from_whatsapp_number:
        print("[Twilio] Variáveis de ambiente não configuradas corretamente.")
        return

    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"

    payload = {
        "To": f"whatsapp:{to}",
        "From": f"whatsapp:{from_whatsapp_number}",
        "Body": (
            "Ótimo! ✅ Escolha o departamento desejado:\n\n"
            "🛒 1 - Envios e Rastreamentos\n"
            "🎯 2 - Atendimento Comercial\n"
            "🛠️ 3 - Suporte Técnico\n\n"
            "Digite o número da opção. 🔢"
        ),
    }

    try:
        response = requests.post(url, data=payload, auth=(account_sid, auth_token))
        
        if response.status_code == 201:
            print("[Twilio] Botões enviados com sucesso!")
        else:
            print(f"[Twilio] Falha ao enviar botões. Código: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"[Twilio] Erro de comunicação: {e}")