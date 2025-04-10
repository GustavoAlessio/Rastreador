from flask import Blueprint, request, Response
from twilio.twiml.messaging_response import MessagingResponse

webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get('Body', '').strip().lower()
    resp = MessagingResponse()
    msg = resp.message()

    if any(word in incoming_msg for word in ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite"]):
        msg.body(
            "\U0001F44B Olá! Seja bem-vindo(a) ao Grupo Aqueceletric, especialistas em peças e equipamentos para gastronomia industrial!\n\n"
            "Escolha uma opção:\n"
            "1\u20e3 Buscar peça/equipamento \U0001F50D\n"
            "2\u20e3 Acompanhar pedido \U0001F4E6\n"
            "3\u20e3 Solicitar orçamento \U0001F4D1\n"
            "4\u20e3 Suporte técnico \U0001F468‍\U0001F527\n"
            "5\u20e3 Exportação / Comércio Exterior \U0001F30E\n"
            "6\u20e3 Outros assuntos \U0001F4E8"
        )

    elif incoming_msg.startswith("1"):
        msg.body(
            "\U0001F50D Vamos encontrar sua peça!\nSelecione a linha de produtos:\n"
            "1\u20e3 Termostatos\n"
            "2\u20e3 Resistências Elétricas\n"
            "3\u20e3 Panificação\n"
            "4\u20e3 Cozinha Industrial\n"
            "5\u20e3 Chopp\n"
            "6\u20e3 Cafeteiras Industriais\n"
            "7\u20e3 Automação Industrial\n"
            "8\u20e3 Outros"
        )

    elif incoming_msg.startswith("2"):
        msg.body(
            "\U0001F4E6 Vamos acompanhar seu pedido!\n\n"
            "Por favor, envie:\n- Número do pedido\nOU\n- CPF/CNPJ utilizado na compra."
        )

    elif incoming_msg.startswith("3"):
        msg.body(
            "\U0001F4D1 Vamos gerar seu orçamento!\n\nInforme:\n- Produto(s) desejado(s)\n- Quantidade\n- Cidade/Estado\n- E-mail e WhatsApp para contato."
        )

    elif incoming_msg.startswith("4"):
        msg.body(
            "\U0001F468‍\U0001F527 Suporte Técnico\n\nInforme:\n- Nome e modelo do equipamento\n- Tipo de problema (ex.: não aquece, não liga)\n- Cidade/Estado."
        )

    elif incoming_msg.startswith("5"):
        msg.body(
            "\U0001F30E Exportação / Comércio Exterior\n\nInforme:\n- Produto(s) desejado(s)\n- Quantidade\n- País de destino\n- E-mail/WhatsApp para contato."
        )

    elif incoming_msg.startswith("6"):
        msg.body(
            "\U0001F4E8 Outros assuntos\n\nPor favor, me conte qual é sua dúvida ou necessidade."
        )

    else:
        msg.body(
            "\u26a0\ufe0f Desculpe, não entendi sua mensagem.\n\nDigite \"Olá\" para começar ou escolha uma das opções do menu."
        )

    return Response(str(resp), mimetype="application/xml")
