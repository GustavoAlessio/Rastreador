from flask import Blueprint, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from app.order_tracking import get_order_status
from app.openai_integration import generate_humanized_response
import os
import re

webhook_bp = Blueprint('webhook', __name__)

GENERIC_MESSAGES = ["oi", "olá", "hello", "hi", "bom dia", "boa tarde", "boa noite"]

@webhook_bp.route('/webhook', methods=['POST'])
def webhook():
    resp = MessagingResponse()
    incoming_msg = request.values.get('Body', '').strip().lower()

    if not incoming_msg:
        resp.message("Por favor, envie o número do seu pedido ou CPF para que possamos verificar o status. 📦")
        return str(resp)

    # Se a mensagem for algo genérico tipo "Oi", "Olá", etc
    if incoming_msg in GENERIC_MESSAGES:
        resp.message("Olá! 👋 Por favor, envie seu número de pedido ou CPF (somente números) para rastrearmos seu pedido. 📦")
        return str(resp)

    # Limpa a mensagem para deixar só números
    cleaned_msg = ''.join(filter(str.isdigit, incoming_msg))

    if not cleaned_msg or len(cleaned_msg) < 6:
        resp.message("Por favor, envie um número de pedido ou CPF válido. 📦")
        return str(resp)

    try:
        # Busca o status real ou simulado
        order_status = get_order_status(cleaned_msg)
        # Gera uma resposta humanizada via OpenAI
        humanized_response = generate_humanized_response(order_status)
        resp.message(humanized_response)
        
    except Exception as e:
        resp.message("Desculpe, tivemos um problema ao processar sua solicitação. "
                     "Por favor, tente novamente ou entre em contato com nosso suporte. 🙏")
        print(f"Erro ao processar mensagem: {str(e)}")
    
    return str(resp)

@webhook_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"})