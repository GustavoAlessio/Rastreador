from flask import Blueprint, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from app.order_tracking import get_order_status
from app.openai_integration import generate_humanized_response
import os
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

    # Inicia sessão se necessário
    if user_number not in user_sessions:
        user_sessions[user_number] = {
            "step": "awaiting_name",
            "attempts": 0  # contador de erros
        }

    session = user_sessions[user_number]

    # Se o usuário mandar uma saudação
    if incoming_msg.lower() in GENERIC_MESSAGES and session["step"] == "awaiting_name":
        resp.message(
            "Olá! 👋 Seja bem-vindo ao *Grupo Aqueceletric*.\n"
            "Eu sou seu assistente virtual e estou aqui para te ajudar. 🤖\n\n"
            "Qual é o seu nome? 😊"
        )
        return str(resp)

    # Se estamos esperando o nome
    if session["step"] == "awaiting_name":
        session["name"] = incoming_msg.strip().title()
        session["step"] = "awaiting_cpf"
        resp.message(
            f"Prazer em te conhecer, *{session['name']}*! 🤝\n\n"
            "Agora, por gentileza, me informe seu *CPF* (11 dígitos) ou *CNPJ* (14 dígitos), apenas números. 📄"
        )
        return str(resp)

    # Se estamos esperando CPF ou CNPJ
    if session["step"] == "awaiting_cpf":
        cpf_cnpj = ''.join(filter(str.isdigit, incoming_msg))

        if len(cpf_cnpj) == 11:
            session["cpf_cnpj"] = cpf_cnpj
            session["document_type"] = "CPF"
        elif len(cpf_cnpj) == 14:
            session["cpf_cnpj"] = cpf_cnpj
            session["document_type"] = "CNPJ"
        else:
            resp.message(
                "O número enviado não parece ser um CPF (11 dígitos) ou CNPJ (14 dígitos) válido. ❌\n\n"
                "Por favor, envie novamente apenas números. 📄"
            )
            return str(resp)

        session["step"] = "awaiting_department"

        # Envia o menu numerado
        resp.message(
            "✅ *CPF/CNPJ recebido com sucesso!*\n\n"
            "Agora, escolha o departamento que deseja falar:\n\n"
            "1️⃣ *Envios e Rastreamentos* (acompanhar seu pedido)\n"
            "2️⃣ *Atendimento Comercial* (dúvidas sobre produtos e vendas)\n"
            "3️⃣ *Suporte Técnico* (ajuda com instalação ou problemas)\n\n"
            "*Por favor, responda apenas com o número da opção.* 🔢"
        )
        return str(resp)

    # Se estamos esperando a escolha do departamento
    if session["step"] == "awaiting_department":
        option = incoming_msg.strip()

        if option == "1":
            session["step"] = "tracking"
            resp.message("🔍 Localizando o status do seu pedido. Um momento, por favor...")

            try:
                order_status = get_order_status(session["cpf_cnpj"])
                humanized_response = generate_humanized_response(order_status)
                resp.message(humanized_response)

                # Finaliza atendimento após rastrear
                resp.message("Agradecemos pelo contato com o *Grupo Aqueceletric*! ✨\nEstamos sempre à disposição. 👋")
                del user_sessions[user_number]
            except Exception as e:
                resp.message("Desculpe, tivemos um problema ao rastrear seu pedido. 🙏")
                print(f"Erro ao rastrear pedido: {str(e)}")
            return str(resp)

        elif option == "2":
            resp.message(
                "🎯 Encaminhando você para o nosso *Atendimento Comercial*.\n\n"
                "Clique no link abaixo para continuar:\n"
                "👉 https://wa.me/5515996730603\n\n"
                "Nosso time vai te atender em instantes! 🧑‍💼✨"
            )
            del user_sessions[user_number]
            return str(resp)

        elif option == "3":
            resp.message(
                "🛠️ Encaminhando você para o nosso *Suporte Técnico*.\n\n"
                "Clique no link abaixo para continuar:\n"
                "👉 https://wa.me/5515996730603\n\n"
                "Um especialista irá te atender! 🔧💬"
            )
            del user_sessions[user_number]
            return str(resp)

        else:
            # Se digitou errado
            session["attempts"] += 1
            if session["attempts"] >= 3:
                resp.message(
                    "Parece que tivemos algumas dificuldades para entender sua escolha. 😕\n"
                    "Vamos reiniciar o atendimento. Por favor, envie *Oi* para começarmos novamente. 👋"
                )
                del user_sessions[user_number]
                return str(resp)
            else:
                resp.message(
                    "Desculpe, não entendi sua escolha. 😕\n\n"
                    "Por favor, responda apenas com o número:\n"
                    "1️⃣ *Envios e Rastreamentos*\n"
                    "2️⃣ *Atendimento Comercial*\n"
                    "3️⃣ *Suporte Técnico*\n\n"
                    "*Digite apenas 1, 2 ou 3.* 🔢"
                )
                return str(resp)

    # Se cair fora do fluxo