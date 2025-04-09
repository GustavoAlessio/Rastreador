import random
from datetime import datetime, timedelta

# Simulação de banco de dados de pedidos
MOCK_ORDERS = {
    # Pedidos por número
    "123456": {"status": "em trânsito", "carrier": "Correios"},
    "789012": {"status": "saiu para entrega", "carrier": "Braspress"},
    "345678": {"status": "entregue", "carrier": "Rodonaves"},
    "901234": {"status": "parado", "carrier": "Correios"},
    "567890": {"status": "atraso", "carrier": "Braspress"},
    "234567": {"status": "devolvido", "carrier": "Rodonaves"},
    
    # Pedidos por CPF (simplificado)
    "12345678900": {"status": "em trânsito", "carrier": "Correios", "order_number": "111222"},
    "98765432100": {"status": "entregue", "carrier": "Braspress", "order_number": "333444"},
    "45678912300": {"status": "saiu para entrega", "carrier": "Rodonaves", "order_number": "555666"}
}

def get_order_status(identifier):
    """
    Simula a consulta de status de um pedido com base no número do pedido ou CPF.
    
    No futuro, esta função pode ser adaptada para integrar com APIs reais de 
    transportadoras como Correios, Braspress e Rodonaves.
    
    Args:
        identifier (str): Número do pedido ou CPF do cliente
    
    Returns:
        dict: Dicionário contendo informações do status do pedido
    """
    # Remove caracteres não numéricos (para lidar com CPFs formatados)
    identifier = ''.join(filter(str.isdigit, identifier))
    
    # Verifica se o identificador existe na base simulada
    if identifier in MOCK_ORDERS:
        order_data = MOCK_ORDERS[identifier].copy()
        
        # Se o identificador for um CPF, usa o número do pedido associado
        order_number = order_data.pop("order_number", identifier)
        
        # Gera datas simuladas
        today = datetime.now()
        
        # Define a previsão de entrega com base no status
        if order_data["status"] == "em trânsito":
            estimated_delivery = (today + timedelta(days=random.randint(2, 5))).strftime("%d/%m/%Y")
        elif order_data["status"] == "saiu para entrega":
            estimated_delivery = today.strftime("%d/%m/%Y")
        elif order_data["status"] == "parado" or order_data["status"] == "atraso":
            estimated_delivery = (today + timedelta(days=random.randint(5, 10))).strftime("%d/%m/%Y")
        else:
            estimated_delivery = "N/A"
        
        # Define a data da última atualização
        if order_data["status"] == "entregue" or order_data["status"] == "devolvido":
            last_update = (today - timedelta(days=random.randint(1, 3))).strftime("%d/%m/%Y")
        else:
            last_update = today.strftime("%d/%m/%Y")
        
        # Monta o objeto de resposta
        return {
            "order_number": order_number,
            "status": order_data["status"],
            "carrier": order_data["carrier"],
            "estimated_delivery": estimated_delivery,
            "last_update": last_update
        }
    else:
        # Se o pedido não for encontrado, gera um pedido aleatório
        # Isso é apenas para fins de demonstração
        statuses = ["em trânsito", "saiu para entrega", "entregue", "parado", "atraso"]
        carriers = ["Correios", "Braspress", "Rodonaves"]
        
        status = random.choice(statuses)
        today = datetime.now()
        
        if status == "em trânsito":
            estimated_delivery = (today + timedelta(days=random.randint(2, 5))).strftime("%d/%m/%Y")
        elif status == "saiu para entrega":
            estimated_delivery = today.strftime("%d/%m/%Y")
        elif status == "parado" or status == "atraso":
            estimated_delivery = (today + timedelta(days=random.randint(5, 10))).strftime("%d/%m/%Y")
        else:
            estimated_delivery = "N/A"
            
        return {
            "order_number": identifier,
            "status": status,
            "carrier": random.choice(carriers),
            "estimated_delivery": estimated_delivery,
            "last_update": today.strftime("%d/%m/%Y")
        }
