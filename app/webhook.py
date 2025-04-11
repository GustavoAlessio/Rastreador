from flask import Blueprint, request
from twilio.twiml.messaging_response import MessagingResponse
from app.order_tracking import get_order_status
from app.openai_integration import generate_humanized_response
import re

webhook_bp = Blueprint('webhook', __name__)

# Sessões dos usuários
user_sessions = {}

# Mensagens genéricas de saudação
GENERIC_MESSAGES = {"oi", "olá", "hello", "hi", "bom dia", "boa tarde", "boa noite"}

@webhook_bp.route('/webhook', methods=['POST'])
def webhook():
    resp = MessagingResponse()
    incoming_msg = request.values.get('Body', '').strip().lower()
    user_number = request.values.get('From', '').replace('whatsapp:', '')

    if not incoming_msg:
        return _send_message(resp, "Por favor, envie uma mensagem para que possamos te ajudar. 📦")

    # Iniciar sessão se não existir
    session = user_sessions.setdefault(user_number, {"step": "awaiting_start"})

    # Se for uma saudação, reinicia o fluxo
    if incoming_msg in GENERIC_MESSAGES:
        session.clear()
        session["step"] = "awaiting_name"
        return _send_message(resp,
            "Olá! 👋 Seja bem-vindo ao *Grupo Aqueceletric*.\n"
            "Eu sou seu assistente virtual. 🤖\n\n"
            "Qual é o seu nome? 😊"
        )

    step = session.get("step")

    match step:
        case "awaiting_name":
            return _handle_name_step(resp, incoming_msg, session, user_number)
        case "awaiting_cpf":
            return _handle_cpf_step(resp, incoming_msg, session, user_number)
        case "awaiting_department":
            return _handle_department_step(resp, incoming_msg, session, user_number)
        case _:
            return _send_message(resp, "Não entendi sua mensagem. Por favor, envie *Oi* para começarmos! 👋")

def _handle_name_step(resp, incoming_msg, session, user_number):
    session["name"] = incoming_msg.title()
    session["step"] = "awaiting_cpf"
    return _send_message(resp,
        f"Prazer em te conhecer, *{session['name']}*! 🤝\n\n"
        "Agora, por favor, envie seu *CPF* ou *CNPJ* (somente números). 📄"
    )

def _handle_cpf_step(resp, incoming_msg, session, user_number):
    cpf_cnpj = re.sub(r'\D', '', incoming_msg)

    if len(cpf_cnpj) in {11, 14}:
        session["cpf_cnpj"] = cpf_cnpj
        session["step"] = "awaiting_department"
        return _send_message(resp,
            "✅ Documento recebido!\n\n"
            "Escolha o departamento desejado:\n"
            "1️⃣ *Envios e Rastreamentos*\n"
            "2️⃣ *Compras e Orçamentos*\n"
            "3️⃣ *Atendimento Humano*\n\n"
            "*Responda apenas com o número.* 🔢"
        )
    else:
        return _send_message(resp,
            "❌ CPF ou CNPJ inválido!\n\n"
            "Por favor, envie apenas números:\n"
            "- *CPF* (11 dígitos)\n"
            "- *CNPJ* (14 dígitos)\n\n"
            "Tente novamente. 📄"
        )

def _handle_department_step(resp, incoming_msg, session, user_number):
    option = incoming_msg

    if option == "1":
        return _handle_tracking(resp, session, user_number)
    elif option == "2":
        user_sessions.pop(user_number, None)
        return _send_message(resp,
            "🎯 Encaminhando para o *Departamento de Compras e Orçamentos*.\n"
            "👉 https://wa.me/5515996730603"
        )
    elif option == "3":
        user_sessions.pop(user_number, None)
        return _send_message(resp,
            "🛠️ Encaminhando para o *Atendimento Humano*.\n"
            "👉 https://wa.me/5515996730603"
        )
    else:
        return _send_message(resp,
            "Opção inválida! ❌ Por favor, responda apenas com:\n"
            "1️⃣ *Envios e Rastreamentos*\n"
            "2️⃣ *Compras e Orçamentos*\n"
            "3️⃣ *Atendimento Humano*\n\n"
            "Digite apenas o número da opção. 🔢"
        )

def _handle_tracking(resp, session, user_number):
    try:
        resp.message("🔍 Localizando seu pedido. Um momento...")
        order_status = get_order_status(session["cpf_cnpj"])
        humanized_response = generate_humanized_response(order_status)
        resp.message(humanized_response)
        resp.message("Agradecemos seu contato com o *Grupo Aqueceletric*! ✨👋")
    except Exception as e:
        print(f"Erro ao rastrear pedido: {e}")
        resp.message("Ocorreu um erro ao localizar seu pedido. 😔 Tente novamente mais tarde.")
    finally:
        user_sessions.pop(user_number, None)
    return str(resp)

def _send_message(resp, message):
    resp.message(message)
    return str(resp)