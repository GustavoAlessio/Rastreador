from flask import Blueprint, request
from twilio.twiml.messaging_response import MessagingResponse
from app.order_tracking import get_order_status
from app.openai_integration import generate_humanized_response
import re

webhook_bp = Blueprint('webhook', __name__)

# Sessões dos usuários
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

    session = user_sessions.get(user_number, {"step": "awaiting_start"})

    # Fluxo de saudação inicial
    if incoming_msg.lower() in GENERIC_MESSAGES:
        user_sessions[user_number] = {"step": "awaiting_name"}
        resp.message(
            "Olá! 👋 Seja bem-vindo ao *Grupo Aqueceletric*.\n"
            "Eu sou seu assistente virtual. 🤖\n\n"
            "Qual é o seu nome? 😊"
        )
        return str(resp)

    # Identifica em qual etapa o usuário está
    step = session.get("step", "awaiting_start")

    if step == "awaiting_name":
        session["name"] = incoming_msg.title()
        session["step"] = "awaiting_cpf"
        user_sessions[user_number] = session
        resp.message(
            f"Prazer em te conhecer, *{session['name']}*! 🤝\n\n"
            "Agora, por favor, envie seu *CPF* (11 dígitos) ou *CNPJ* (14 dígitos), apenas números. 📄"
        )
        return str(resp)

    if step == "awaiting_cpf":
        cpf_cnpj = re.sub(r'\D', '', incoming_msg)

        if len(cpf_cnpj) not in [11, 14]:
            resp.message("Número inválido! ❌ Envie apenas o CPF (11 dígitos) ou CNPJ (14 dígitos). 📄")
            return str(resp)

        session["cpf_cnpj"] = cpf_cnpj
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
                # Consulta o status do pedido
                order_status = get_order_status(session["cpf_cnpj"])
                
                # Gera a resposta humanizada via OpenAI
                humanized_response = generate_humanized_response(order_status)

                resp.message(humanized_response)
                resp.message("Agradecemos seu contato com o *Grupo Aqueceletric*! ✨👋")
                user_sessions.pop(user_number, None)  # Finaliza sessão
            except Exception as e:
                print(f"Erro ao rastrear pedido: {e}")
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