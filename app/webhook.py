from flask import Blueprint, request, Response
from twilio.twiml.messaging_response import MessagingResponse
from app.order_tracking import get_order_status
from app.openai_integration import generate_humanized_response
import re

webhook_bp = Blueprint('webhook', __name__)

# Controle de sessão em memória
user_sessions = {}

@webhook_bp.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From', '')
    incoming_msg_lower = incoming_msg.lower()

    resp = MessagingResponse()
    msg = resp.message()

    session = user_sessions.get(from_number, {"step": "main_menu"})

    def reset_session():
        user_sessions[from_number] = {"step": "main_menu"}

    # Fluxo principal
    if any(word in incoming_msg_lower for word in ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite"]):
        reset_session()
        msg.body(
            "\U0001F44B Olá! Seja bem-vindo(a) ao Grupo Aqueceletric, especialistas em peças e equipamentos para gastronomia industrial!\n\n"
            "Escolha uma opção:\n"
            "1️⃣ Buscar peça/equipamento 🔎\n"
            "2️⃣ Acompanhar pedido 📦\n"
            "3️⃣ Solicitar orçamento 📄\n"
            "4️⃣ Exportação / Comércio Exterior 🌎\n"
            "5️⃣ Outros assuntos ✉️"
        )

    elif incoming_msg.startswith("1"):
        session["step"] = "search_parts"
        msg.body(
            "🔎 Catálogo de Peças e Equipamentos\n\n"
            "📄 Acesse nosso catálogo completo aqui:\n"
            "👉 https://grupoaqueceletric.com.br/cartalogo/catalogo_aqueceletric.pdf\n\n"
            "💬 Ou fale diretamente com um vendedor:\n"
            "👉 https://wa.me/5515996730603\n\n"
            "Estamos prontos para te ajudar! 🚀"
        )

    elif incoming_msg.startswith("2"):
        session["step"] = "tracking"
        msg.body(
            "📦 Vamos acompanhar seu pedido!\n\n"
            "Por favor, envie:\n- Número do pedido\nOU\n- CPF/CNPJ utilizado na compra."
        )

    elif incoming_msg.startswith("3"):
        session["step"] = "quotation"
        msg.body(
            "📄 Solicitar Orçamento\n\n"
            "💬 Fale diretamente com nosso time de vendas:\n"
            "👉 https://wa.me/5515996730603\n\n"
            "Ou, se preferir, envie aqui:\n- Produto(s) desejado(s)\n- Quantidade\n- Cidade/Estado\n- E-mail e WhatsApp para contato."
        )

    elif incoming_msg.startswith("4"):
        session["step"] = "export"
        msg.body(
            "🌎 Exportação / Comércio Exterior\n\n"
            "💬 Nosso time de exportação está à disposição:\n"
            "👉 https://wa.me/5515996730603\n\n"
            "Informe:\n- Produto(s) desejado(s)\n- Quantidade\n- País de destino\n- E-mail/WhatsApp para contato."
        )

    elif incoming_msg.startswith("5"):
        session["step"] = "other"
        msg.body(
            "✉️ Outros assuntos\n\n"
            "💬 Fale diretamente conosco:\n"
            "👉 https://wa.me/5515996730603\n\n"
            "Ou descreva sua dúvida ou necessidade aqui mesmo."
        )

    # Se o usuário estiver na etapa de rastreamento e mandar um número
    elif session.get("step") == "tracking":
        numbers_only = re.sub(r'\D', '', incoming_msg)
        if len(numbers_only) >= 6:
            order_status = get_order_status(numbers_only)
            humanized_response = generate_humanized_response(order_status)
            msg.body(humanized_response)
            reset_session()
        else:
            msg.body(
                "❗ Por favor, envie um número de pedido válido ou CPF/CNPJ correto."
            )

    # Se mandou número diretamente fora de contexto
    elif incoming_msg.isdigit() and len(incoming_msg) >= 6:
        order_status = get_order_status(incoming_msg)
        humanized_response = generate_humanized_response(order_status)
        msg.body(humanized_response)
        reset_session()

    else:
        msg.body(
            "⚠️ Desculpe, não entendi sua mensagem.\n\n"
            "Digite \"Olá\" para começar ou escolha uma das opções do menu principal."
        )
        reset_session()

    # Atualiza a sessão
    user_sessions[from_number] = session

    return Response(str(resp), mimetype="application/xml")