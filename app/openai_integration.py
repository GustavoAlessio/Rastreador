import os
from openai import OpenAI

def generate_humanized_response(order_status):
    """
    Envia o status do pedido para a OpenAI API para gerar uma resposta humanizada.
    
    Args:
        order_status (dict): Dicionário contendo informações do status do pedido
            Exemplo: {
                'order_number': '123456',
                'status': 'em trânsito',
                'carrier': 'Correios',
                'estimated_delivery': '2025-04-15',
                'last_update': '2025-04-08'
            }
    
    Returns:
        str: Resposta humanizada gerada pela OpenAI
    """
    try:
        # Inicializa o cliente da OpenAI com a chave da API
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Prepara o prompt com as informações do pedido
        order_info = (
            f"Número do pedido: {order_status.get('order_number', 'N/A')}\n"
            f"Status: {order_status.get('status', 'N/A')}\n"
            f"Transportadora: {order_status.get('carrier', 'N/A')}\n"
            f"Previsão de entrega: {order_status.get('estimated_delivery', 'N/A')}\n"
            f"Última atualização: {order_status.get('last_update', 'N/A')}"
        )
        
        # Define o prompt do sistema conforme especificado nos requisitos
        system_prompt = """
        Você é um assistente virtual especializado em rastreamento de pedidos para uma empresa que vende em marketplaces como Mercado Livre, Amazon, Shopee e Magazine Luiza. Seu objetivo é interpretar o status logístico dos pedidos enviados pelas transportadoras Correios, Braspress e Rodonaves, e transformar essas informações em mensagens claras, amigáveis e acolhedoras para o cliente final, utilizando uma linguagem natural e personalizada.

        Sempre reescreva o status recebido da transportadora com um tom humano e positivo. Não copie o texto técnico ou bruto. Seja breve, educado e objetivo. Escreva como se estivesse em uma conversa de WhatsApp, com simpatia e cordialidade.

        Se o pedido estiver "em trânsito", diga que "o pedido está a caminho e logo chegará". Se o pedido "saiu para entrega", informe que "o pedido saiu para entrega e deve chegar hoje". Se o pedido foi "entregue", parabenize e agradeça pela compra. Se o pedido estiver "parado" ou "sem movimentação", explique que "o pedido está em trânsito e que estamos acompanhando tudo de perto". Se houver um "atraso" ou "problema na entrega", peça desculpas de forma empática e garanta que a equipe está trabalhando para resolver. Se o pedido foi "devolvido", informe de maneira cuidadosa e oriente que o suporte entrará em contato para resolver.

        Nunca culpe diretamente a transportadora. Use linguagem neutra e mostre comprometimento em ajudar. Caso a informação seja insuficiente, diga que "estamos monitorando seu pedido e qualquer novidade será informada em breve". Sempre que possível, mencione o nome da transportadora e a previsão de entrega, se estiver disponível. Use ícones simples e amigáveis como 🚚, 📦 ou ✨ para tornar a mensagem mais leve.

        A resposta deve ser estruturada com uma saudação inicial, o resumo amigável da situação atual do pedido, uma orientação (se necessário) e uma despedida cordial. Sempre priorize a clareza, o acolhimento e o tom positivo em todas as respostas.
        """
        
        # Faz a chamada para a API da OpenAI
        response = client.chat.completions.create(
            model="gpt-4",  # Conforme solicitado nos requisitos
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": order_info}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        # Retorna a resposta gerada
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"Erro ao gerar resposta humanizada: {str(e)}")
        # Em caso de erro, retorna uma mensagem padrão
        return (
            "Olá! Estamos acompanhando seu pedido e trabalhando para garantir que "
            "ele chegue até você o mais rápido possível. Qualquer novidade, "
            "entraremos em contato. Obrigado pela compreensão! 📦"
        )
