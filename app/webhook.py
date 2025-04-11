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

    # Obter sessão atual do usuário
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

    # Perguntar o nome
    if step == "awaiting_name":
        session["name"] = incoming_msg.title()
        session["step"] = "awaiting_cpf"
        user_sessions[user_number] = session
        resp.message(
            f"Prazer em te conhecer, *{session['name']}*! 🤝\n\n"
            "Agora, por favor, envie seu *CPF* ou *CNPJ* (somente números). 📄"
        )
        return str(resp)

    # Perguntar CPF ou CNPJ
    if step == "awaiting_cpf":
        cpf_cnpj = re.sub(r'\D', '', incoming_msg)  # Remove tudo que não é número

        if len(cpf_cnpj) == 11 or len(cpf_cnpj) == 14:
            # CPF ou CNPJ válido
            session["cpf_cnpj"] = cpf_cnpj
            session["step"] = "awaiting_department"
            user_sessions[user_number] = session

            resp.message(
                "✅ Documento recebido!\n\n"
                "Escolha o departamento desejado:\n"
                "1️⃣ *Envios e Rastreamentos*\n"
                "2️⃣ *Compras e Orçamentos*\n"
                "3️⃣ *Atendimento Humano*\n\n"
                "*Responda apenas com o número.* 🔢"
            )
            return str(resp)

        else:
            # CPF ou CNPJ inválido
            resp.message(
                "❌ CPF ou CNPJ inválido!\n\n"
                "Por favor, envie apenas números:\n"
                "- *CPF* (11 dígitos)\n"
                "- *CNPJ* (14 dígitos)\n\n"
                "Tente novamente. 📄"
            )
            return str(resp)

    # Escolher departamento
    if step == "awaiting_department":
        option = incoming_msg.strip()

        if option == "1":
            session["step"] = "tracking"
            user_sessions[user_number] = session
            resp.message("🔍 Localizando seu pedido. Um momento...")

            try:
                order_status = get_order_status(session["cpf_cnpj"])
                humanized_response = generate_humanized_response(order_status)
                resp.message(humanized_response)
                resp.message("Agradecemos seu contato com o *Grupo Aqueceletric*! ✨👋")
            except Exception as e:
                print(f"Erro ao rastrear pedido: {e}")
                resp.message("Ocorreu um erro ao localizar seu pedido. 😔 Tente novamente mais tarde.")

            user_sessions.pop(user_number, None)
            return str(resp)

        elif option == "2":
            resp.message(
                "🎯 Encaminhando para o *Departamento de Compras e Orçamentos*.\n"
                "👉 https://wa.me/5515996730603"
            )
            user_sessions.pop(user_number, None)
            return str(resp)

        elif option == "3":
            resp.message(
                "🛠️ Encaminhando para o *Atendimento Humano*.\n"
                "👉 https://wa.me/5515996730603"
            )
            user_sessions.pop(user_number, None)
            return str(resp)

        else:
            resp.message(
                "Opção inválida! ❌ Por favor, responda apenas com:\n"
                "1️⃣ *Envios e Rastreamentos*\n"
                "2️⃣ *Compras e Orçamentos*\n"
                "3️⃣ *Atendimento Humano*\n\n"
                "Digite apenas o número da opção. 🔢"
            )
            return str(resp)

    # Se o usuário enviar qualquer outra coisa inesperada
    resp.message("Não entendi sua mensagem. Por favor, envie *Oi* para começarmos! 👋")
    return str(resp)