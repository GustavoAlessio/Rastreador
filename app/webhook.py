from flask import Blueprint, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from app.order_tracking import get_order_status
from app.openai_integration import generate_humanized_response
import os

webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route('/webhook', methods=['POST'])
def webhook():
    """
    Endpoint para receber mensagens do Twilio WhatsApp.
    
    Fluxo:
    1. Recebe a mensagem do cliente via Twilio
    2. Extrai o número do pedido ou CPF da mensagem
    3. Consulta o status do pedido (simulado ou API real)
    4. Envia o status para a OpenAI para humanizar a resposta
    5. Retorna a resposta humanizada para o cliente via Twilio
    """
    # Inicializa a resposta do Twilio
    resp = MessagingResponse()
    
    # Obtém a mensagem do usuário
    incoming_msg = request.values.get('Body', '').strip()
    
    if not incoming_msg:
        resp.message("Por favor, envie o número do seu pedido ou CPF para que possamos verificar o status.")
        return str(resp)
    
    try:
        # Consulta o status do pedido (simulado ou API real)
        order_status = get_order_status(incoming_msg)
        
        # Gera uma resposta humanizada usando a OpenAI
        humanized_response = generate_humanized_response(order_status)
        
        # Envia a resposta humanizada de volta para o cliente
        resp.message(humanized_response)
        
    except Exception as e:
        # Em caso de erro, envia uma mensagem amigável
        resp.message("Desculpe, tivemos um problema ao processar sua solicitação. "
                    "Por favor, tente novamente em alguns instantes ou entre em contato com nosso suporte.")
        print(f"Erro ao processar mensagem: {str(e)}")
    
    return str(resp)

@webhook_bp.route('/health', methods=['GET'])
def health_check():
    """Endpoint simples para verificar se o serviço está funcionando"""
    return jsonify({"status": "ok"})
