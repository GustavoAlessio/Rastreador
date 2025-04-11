import os
from openai import OpenAI

def generate_humanized_response(order_status):
    """
    Gera uma resposta humanizada para o status do pedido usando OpenAI.
    """
    try:
        # Inicializa cliente OpenAI
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        # Prepara o conteúdo do pedido
        order_info = (
            f"Número do pedido: {order_status.get('order_number', 'N/A')}\n"
            f"Status: {order_status.get('status', 'N/A')}\n"
            f"Transportadora: {order_status.get('carrier', 'N/A')}\n"
            f"Previsão de entrega: {order_status.get('estimated_delivery', 'N/A')}\n"
            f"Última atualização: {order_status.get('last_update', 'N/A')}"
        )

        # Prompt de sistema (instruções para o GPT)
        system_prompt = """
        Você é um assistente virtual, do Grupo Aqueceletric, especializado em rastreamento de pedidos para marketplaces. 
        Sempre reescreva o status do pedido de forma simpática, clara e otimista.
        """
        
        # Chamada à API OpenAI
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": order_info}
            ],
            max_tokens=300,
            temperature=0.7,
            timeout=10  # Tempo máximo de espera
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"[OpenAI] Erro ao gerar resposta: {e}")
        # Retorno padrão se falhar
        return (
            "Olá! Estamos acompanhando seu pedido e trabalhando para que "
            "ele chegue até você o mais breve possível. ✨🚚 Agradecemos sua paciência!"
        )