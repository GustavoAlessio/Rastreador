import os
import requests
from datetime import datetime

# Mock de pedidos de teste
MOCK_ORDERS = {
    "123456": {"status": "em trânsito", "carrier": "Correios"},
    "789012": {"status": "saiu para entrega", "carrier": "Braspress"},
    "345678": {"status": "entregue", "carrier": "Rodonaves"},
}

DEFAULT_TIMEOUT = 5  # Timeout padrão para todas as requisições (segundos)

def fetch_braspress_tracking(order_number):
    """Consulta o status do pedido via API da Braspress."""
    try:
        cnpj = os.getenv("BRASPRESS_CNPJ")
        url = f"https://api.braspress.com/v3/tracking/byNumPedido/{cnpj}/{order_number}/json"

        response = requests.get(url, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()

        tracking_data = response.json()

        if tracking_data and isinstance(tracking_data, list):
            last_event = tracking_data[-1]
            return parse_tracking_response(order_number, last_event, "Braspress")
        else:
            raise ValueError("Resposta vazia ou inválida da API Braspress.")
    except Exception as e:
        print(f"[Braspress] Erro: {e}")
        return None

def fetch_correios_tracking(order_number):
    """Consulta o status do pedido via API dos Correios."""
    try:
        correios_user = os.getenv("CORREIOS_USER")
        correios_pass = os.getenv("CORREIOS_PASS")
        url = f"https://api.linkdoscorreios/sro?usuario={correios_user}&senha={correios_pass}&codigo={order_number}"

        response = requests.get(url, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()

        tracking_data = response.json()

        if tracking_data:
            last_event = tracking_data.get("eventos", [{}])[-1]
            return parse_tracking_response(order_number, last_event, "Correios")
        else:
            raise ValueError("Resposta vazia ou inválida da API dos Correios.")
    except Exception as e:
        print(f"[Correios] Erro: {e}")
        return None

def fetch_rodonaves_tracking(order_number):
    """Consulta o status do pedido via API da Rodonaves."""
    try:
        token = os.getenv("RODONAVES_TOKEN")
        url = "https://tracking-apigateway.rte.com.br/api/v1/tracking"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {"pedido": order_number}

        response = requests.post(url, json=payload, headers=headers, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()

        tracking_data = response.json()

        if tracking_data and tracking_data.get("tracking"):
            last_event = tracking_data["tracking"][-1]
            return parse_tracking_response(order_number, last_event, "Rodonaves")
        else:
            raise ValueError("Resposta vazia ou inválida da API Rodonaves.")
    except Exception as e:
        print(f"[Rodonaves] Erro: {e}")
        return None

def parse_tracking_response(order_number, event_data, carrier):
    """Formata a resposta de rastreamento em um dicionário padrão."""
    return {
        "order_number": order_number,
        "status": event_data.get("situacao") or event_data.get("descricao") or "em trânsito",
        "carrier": carrier,
        "estimated_delivery": event_data.get("previsaoEntrega", "N/A"),
        "last_update": event_data.get("data") or event_data.get("dataEvento") or datetime.now().strftime("%d/%m/%Y")
    }

def get_order_status(identifier):
    """
    Consulta o status de um pedido pelo identificador (CPF/CNPJ ou número de pedido).
    Usa Correios, Braspress, Rodonaves ou Mock como fallback.
    """
    identifier = ''.join(filter(str.isdigit, identifier))

    # Verifica se está nos pedidos mockados
    if identifier in MOCK_ORDERS:
        carrier = MOCK_ORDERS[identifier]["carrier"].lower()
        carrier_functions = {
            "braspress": fetch_braspress_tracking,
            "correios": fetch_correios_tracking,
            "rodonaves": fetch_rodonaves_tracking,
        }

        fetch_function = carrier_functions.get(carrier)
        if fetch_function:
            real_status = fetch_function(identifier)
            if real_status:
                return real_status
        
        # Se não conseguir buscar, retorna o mock
        order_data = MOCK_ORDERS[identifier]
        return {
            "order_number": identifier,
            "status": order_data["status"],
            "carrier": order_data["carrier"],
            "estimated_delivery": "N/A",
            "last_update": datetime.now().strftime("%d/%m/%Y")
        }

    # Se não estiver no MOCK, retorna padrão genérico
    return {
        "order_number": identifier,
        "status": "em trânsito",
        "carrier": "Desconhecida",
        "estimated_delivery": "N/A",
        "last_update": datetime.now().strftime("%d/%m/%Y")
    }