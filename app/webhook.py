from flask import Blueprint, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from app.order_tracking import get_order_status
from app.openai_integration import generate_humanized_response
from app.utils import send_whatsapp_buttons
import os
import re

webhook_bp = Blueprint('webhook', __name__)

# Armazena sessões de usuários
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

    # Inicializa a sessão do usuário se não existir
    if user_number not in user_sessions:
        user_sessions[user_number] = {"step": "awaiting_name"}

    session = user_sessions[user_number]

    # Se o usuário mandou uma saudação
    if incoming_msg.lower() in GENERIC_MESSAGES and session["step"] == "awaiting_name":
        resp.message(
            "Olá! 👋 Eu sou o Assistente Virtual do Grupo Aqueceletric.\n"
            "Qual é o seu nome? 😊"
        )
        return str(resp)

    # Se estamos esperando o nome
    if session["step"] == "awaiting_name":
        session["name"] = incoming_msg.strip().title()
        session["step"] = "awaiting_cpf"
        resp.message(
            f"Prazer em te conhecer, {session['name']}! 🤝\n\n"
            "Agora, poderia me informar seu CPF ou CNPJ para localizarmos seu pedido? 📄"
        )
        return str(resp)

    # Se estamos esperando o CPF ou CNPJ
    if session["step"] == "awaiting_cpf":
        cpf_cnpj = ''.join(filter(str.isdigit, incoming_msg))

        if len(cpf_cnpj) < 6:
            resp.message("O CPF ou CNPJ parece inválido. Por favor, envie apenas números. 📄")
            return str(resp)

        session["cpf_cnpj"] = cpf_cnpj
        session["step"] = "awaiting_department"

        # Aqui envia os botões para o cliente
        send_whatsapp_buttons(user_number)

        return ('', 204)  # Responde vazio para encerrar o webhook depois de enviar os botões

    # Se estamos esperando a escolha do departamento
    if session["step"] == "awaiting_department":
        department = incoming_msg.lower()

        if "envios" in department or "rastreamento" in department:
            session["step"] = "tracking"
            resp.message("Perfeito! 📦 Vou localizar o status do seu pedido. Um momento...")

            try:
                order_status = get_order_status(session["cpf_cnpj"])
                humanized_response = generate_humanized_response(order_status)
                resp.message(humanized_response)

                # Após rastrear, limpa a sessão
                del user_sessions[user_number]
            except Exception as e:
                resp.message("Desculpe, tivemos um problema ao processar seu rastreamento. 🙏")
                print(f"Erro ao rastrear pedido: {str(e)}")

            return str(resp)

        elif "atendimento" in department:
            resp.message(
                "Ótimo! 🎯 Você está sendo direcionado para o *Atendimento Comercial*.\n\n"
                "Nosso time está disponível para tirar dúvidas sobre:\n"
                "- Produtos\n"
                "- Orçamentos\n"
                "- Prazo de entrega\n"
                "- Pagamentos\n\n"
                "Por favor, aguarde alguns instantes que um atendente irá te chamar. 🧑‍💼✨"
            )
            del user_sessions[user_number]
            return str(resp)

        elif "suporte" in department:
            resp.message(
                "Tudo certo! 🛠️ Você está sendo direcionado para o *Suporte Técnico*.\n\n"
                "Nosso time pode te ajudar com:\n"
                "- Dúvidas técnicas\n"
                "- Instalação de produtos\n"
                "- Garantia e manutenção\n\n"
                "Aguarde um momento enquanto um especialista entra em contato. 🔧💬"
            )
            del user_sessions[user_number]
            return str(resp)

        else:
            resp.message(
                "Desculpe, não entendi sua escolha. 😕\n"
                "Por favor, clique em uma das opções enviadas anteriormente. 🛒🎯🛠️"
            )
            return str(resp)

    # Se cair fora do fluxo
    resp.message("Desculpe, não entendi. Vamos começar novamente. 👋")
    del user_sessions[user_number]
    return str(resp)

@webhook_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"})