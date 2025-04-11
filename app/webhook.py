from flask import Blueprint, request
from twilio.twiml.messaging_response import MessagingResponse
from app.order_tracking import get_order_status
import re

webhook_bp = Blueprint('webhook', __name__)

# Sessões de usuários
user_sessions = {}

# Palavras que são apenas saudações
GENERIC_MESSAGES = ["oi", "olá", "hello", "hi", "bom dia", "boa tarde", "boa noite"]

@webhook_bp.route('/webhook', methods=['POST'])
def webhook():
    resp = MessagingResponse()
    incoming_msg = request.values.get('Body', '').strip()
    user_number = request.values.get('From', '').replace('whatsapp:', '')

    if not incoming_msg:
        resp.message("Por favor, envie uma mensagem para que possamos te ajudar. 📦")
        return str(resp)

    # Resetar sessão se saudação recebida
    if incoming_msg.lower() in GENERIC_MESSAGES:
        user_sessions[user_number] = {"step": "awaiting_name"}
        resp.message(
            "Olá! 👋 Seja bem-vindo ao *Grupo Aqueceletric*.\n"
            "Eu sou seu assistente virtual. 🤖\n\n"
            "Qual é o seu nome? 😊"
        )
        return str(resp)

    session = user_sessions.get(user_number, {"step": "awaiting_name"})

    # Fluxo baseado na etapa
    step = session.get("step")

    if step == "awaiting_name":
        session["name"] = incoming_msg.strip().title()
        session["step"] = "awaiting_cpf"
        user_sessions[user_number] = session
        resp.message(
            f"Prazer em te conhecer, *{session['name']}*! 🤝\n\n"
            "Agora, por favor, envie seu *CPF* (11 dígitos) ou *CNPJ* (14 dígitos), apenas números. 📄"
        )
        return str(resp)

    if step == "awaiting_cpf":
        cpf_cnpj = re.sub(r'\D', '', incoming_msg)

        if len(cpf_cnpj) == 11:
            session["cpf_cnpj"] = cpf_cnpj
            session["document_type"] = "CPF"
        elif len(cpf_cnpj) == 14:
            session["cpf_cnpj"] = cpf_cnpj
            session["document_type"] = "CNPJ"
        else:
            resp.message("Número inválido! ❌ Envie apenas o CPF (11 dígitos) ou CNPJ (14 dígitos). 📄")
            return str(resp)

        session["step"] = "awaiting_department"
        user_sessions[user_number] = session
        resp.message(
            "✅ Documento recebido!\n\n"
            "Escolha o departamento:\n"
            "1️⃣ *Envios e Rastreamentos*\n"
            "2️⃣ *Atendimento Comercial*\n"
            "3️⃣ *Suporte Técnico*\n\n"
            "*Responda apenas com o número.* 🔢"
        )
        return str(resp)

    if step == "awaiting_department":
        option = incoming_msg.strip()

        if option == "1":
            session["step"] = "tracking"
            user_sessions[user_number] = session
            resp.message("🔍 Localizando seu pedido. Um momento...")

            try:
                order_status = get_order_status(session["cpf_cnpj"])
                simple_response = generate_simple_response(order_status)
                resp.message(simple_response)
                resp.message("Agradecemos seu contato com o *Grupo Aqueceletric*! ✨👋")
                user_sessions.pop(user_number, None)
            except Exception as e:
                print(f"Erro: {e}")
                resp.message("Ocorreu um erro ao localizar seu pedido. 😔 Tente novamente mais tarde.")
                user_sessions.pop(user_number, None)
            return str(resp)

        elif option == "2":
            resp.message(
                "🎯 Encaminhando para o *Atendimento Comercial*.\n"
                "👉 https://wa.me/5515996730603"
            )
            user_sessions.pop(user_number, None)
            return str(resp)

        elif option == "3":
            resp.message(
                "🛠️ Encaminhando para o *Suporte Técnico*.\n"
                "👉 https://wa.me/5515996730603"
            )
            user_sessions.pop(user_number, None)
            return str(resp)

        else:
            resp.message("Opção inválida! ❌ Responda apenas com 1, 2 ou 3. 🔢")
            return str(resp)

    # Se cair fora do fluxo
    resp.message("Não entendi sua mensagem. Por favor, envie *Oi* para começarmos! 👋")
    return str(resp)

def generate_simple_response(order_status):
    status = order_status.get('status', '').lower()
    carrier = order_status.get('carrier', 'Transportadora')
    estimated_delivery = order_status.get('estimated_delivery', 'em breve')

    if "em trânsito" in status:
        return f"🚚 Seu pedido está a caminho com a {carrier}! Previsão de entrega: {estimated_delivery}."
    elif "saiu para entrega" in status:
        return f"📦 Seu pedido saiu para entrega e deve chegar hoje! Fique atento. ✨"
    elif "entregue" in status:
        return f"🎉 Pedido entregue com sucesso! Agradecemos por comprar conosco. ✨"
    else:
        return f"Estamos monitorando seu pedido. 🚚 Qualquer novidade, avisaremos!"