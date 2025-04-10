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
            "👋 Olá! Seja bem-vindo(a) ao Grupo Aqueceletric, especialistas em peças e equipamentos para gastronomia industrial!\n\n"
            "Escolha uma opção:\n\n"
            "1⃣ Buscar peça/equipamento 🔎\n"
            "2⃣ Acompanhar pedido 📦\n"
            "3⃣ Solicitar orçamento 📄\n"
            "4⃣ Exportação / Comércio Exterior 🌎\n"
            "5⃣ Falar com atendimento humano 👤\n"
            "6⃣ Perguntas Frequentes ❓"
        )

    elif incoming_msg.startswith("1"):
        reset_session()
        msg.body(
            "🔎 Catálogo de Peças e Equipamentos\n\n"
            "📄 Acesse nosso catálogo completo aqui:\n"
            "👉 https://grupoaqueceletric.com.br/cartalogo/catalogo_aqueceletric.pdf\n\n"
            "💬 Fale diretamente com um especialista:\n"
            "👉 https://wa.me/5515996730603\n\n"
            "Estamos prontos para te ajudar! 🚀"
        )

    elif incoming_msg.startswith("2"):
        session["step"] = "tracking"
        msg.body(
            "📦 Vamos acompanhar seu pedido!\n\n"
            "Por favor, envie:\n"
            "- Número do pedido\nOU\n- CPF/CNPJ utilizado na compra."
        )

    elif incoming_msg.startswith("3"):
        reset_session()
        msg.body(
            "📄 Solicitar Orçamento\n\n"
            "💬 Fale diretamente com nosso time de vendas pelo WhatsApp:\n"
            "👉 https://wa.me/5515996730603\n\n"
            "Estamos prontos para te atender! 🚀"
        )

    elif incoming_msg.startswith("4"):
        reset_session()
        msg.body(
            "🌎 Exportação / Comércio Exterior\n\n"
            "💬 Fale diretamente com nosso time de exportação pelo WhatsApp:\n"
            "👉 https://wa.me/5515996730603\n\n"
            "Estamos à disposição para atender sua necessidade internacional! 🚀"
        )

    elif incoming_msg.startswith("5"):
        reset_session()
        msg.body(
            "👤 Falar com Atendimento Humano\n\n"
            "💬 Clique no link abaixo para conversar com um de nossos atendentes:\n"
            "👉 https://wa.me/5515996730603\n\n"
            "Estamos prontos para te ajudar! 🚀"
        )

    elif incoming_msg.startswith("6"):
        session["step"] = "faq"
        msg.body(
            "❓ Perguntas Frequentes\n\n"
            "Digite uma das opções para saber mais:\n\n"
            "- Entrega\n"
            "- Marcas\n"
            "- Garantia\n"
            "- Prazo\n"
            "- Assistência\n\n"
            "Ou digite \"menu\" para voltar."
        )

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

    elif session.get("step") == "faq":
        faq_question = incoming_msg_lower

        if "entrega" in faq_question:
            msg.body("🚚 Sim! Entregamos para todo o Brasil 🌟 com transportadoras parceiras confiáveis.")
        elif "marcas" in faq_question:
            msg.body("🏷️ Trabalhamos com marcas como Venâncio, Progás, Gpaniz, Marchesoni e outras líderes do mercado. 🔥")
        elif "garantia" in faq_question:
            msg.body("✅ Todos os nossos produtos possuem garantia conforme o fabricante. Pode comprar tranquilo(a)!")
        elif "prazo" in faq_question:
            msg.body("⏳ O prazo de entrega varia conforme sua cidade e transportadora. Mas enviamos rapidinho! 🚚")
        elif "assistencia" in faq_question:
            msg.body(
                "🛠️ Para assistência, entre em contato com nosso time de vendas:\n"
                "👉 https://wa.me/5515996730603"
            )
        elif "menu" in faq_question:
            reset_session()
            msg.body(
                "👋 Voltando ao menu principal...\n\n"
                "Escolha uma opção:\n\n"
                "1⃣ Buscar peça/equipamento 🔎\n"
                "2⃣ Acompanhar pedido 📦\n"
                "3⃣ Solicitar orçamento 📄\n"
                "4⃣ Exportação / Comércio Exterior 🌎\n"
                "5⃣ Falar com atendimento humano 👤\n"
                "6⃣ Perguntas Frequentes ❓"
            )
        else:
            msg.body(
                "❗ Não entendi sua pergunta.\n\n"
                "Digite uma das opções:\n"
                "- Entrega\n- Marcas\n- Garantia\n- Prazo\n- Assistência\n\n"
                "Ou digite \"menu\" para voltar."
            )

    else:
        reset_session()
        msg.body(
            "⚠️ Desculpe, não entendi sua mensagem.\n\n"
            "Digite \"Olá\" para ver o menu principal."
        )

    user_sessions[from_number] = session

    return Response(str(resp), mimetype="application/xml")