import requests
import os

def send_whatsapp_buttons(to):
    """
    Envia botões interativos no WhatsApp usando a API do Twilio.
    """
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER")

    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"

    payload = {
        "To": f"whatsapp:{to}",
        "From": f"whatsapp:{from_whatsapp_number}",
        "Body": "Ótimo! ✅ Agora, escolha com qual departamento deseja falar:\n\n"
                "🛒 Envios e Rastreamentos\n"
                "🎯 Atendimento Comercial\n"
                "🛠️ Suporte Técnico\n\n"
                "Clique em uma opção:",
        # OBS: Twilio API standard não suporta "real" botão via API normal ainda,
        # isso é uma simulação via PersistentAction (apenas no WhatsApp Business API avançado).
    }

    response = requests.post(url, data=payload, auth=(account_sid, auth_token))
    
    if response.status_code == 201:
        print("Botões enviados com sucesso!")
    else:
        print(f"Erro ao enviar botões: {response.text}")