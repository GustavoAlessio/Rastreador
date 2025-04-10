import os
import requests
from datetime import datetime  # ✅ Corrige datetime

# ✅ MOCK_ORDERS precisa estar aqui
MOCK_ORDERS = {
    "123456": {"status": "em trânsito", "carrier": "Correios"},
    "789012": {"status": "saiu para entrega", "carrier": "Braspress"},
    "345678": {"status": "entregue", "carrier": "Rodonaves"},
}

def fetch_braspress_tracking(order_number):
    """Consulta status via API Braspress."""
    try:
        cnpj = os.getenv("BRASPRESS_CNPJ")
        return_type = "json"
        url = f"https://api.braspress.com/v3/tracking/byNumPedido/{cnpj}/{order_number}/{return_type}"

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        tracking_data = response.json()

        if tracking_data and isinstance(tracking_data, list):
            last_event = tracking_data[-1]
            return {
                "order_number": order_number,
                "status": last_event.get("situacao", "em trânsito").lower(),
                "carrier": "Braspress",
                "estimated_delivery": last_event.get("previsaoEntrega", "N/A"),
                "last_update": last_event.get("data", datetime.now().strftime("%d/%m/%Y"))
            }
        else:
            raise ValueError("Resposta da API da Braspress vazia ou inválida.")
    except Exception as e:
        print(f"Erro Braspress: {str(e)}")
        return None

def fetch_correios_tracking(order_number):
    """Consulta status via API Correios."""
    try:
        correios_user = os.getenv("CORREIOS_USER")
        correios_pass = os.getenv("CORREIOS_PASS")

        url = f"https://api.linkdoscorreios/sro?usuario={correios_user}&senha={correios_pass}&codigo={order_number}"

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        tracking_data = response.json()

        if tracking_data:
            last_event = tracking_data.get("eventos", [{}])[-1]
            return {
                "order_number": order_number,
                "status": last_event.get("descricao", "em trânsito").lower(),
                "carrier": "Correios",
                "estimated_delivery": last_event.get("previsaoEntrega", "N/A"),
                "last_update": last_event.get("data", datetime.now().strftime("%d/%m/%Y"))
            }
        else:
            raise ValueError("Resposta da API dos Correios vazia ou inválida.")
    except Exception as e:
        print(f"Erro Correios: {str(e)}")
        return None

def fetch_rodonaves_tracking(order_number):
    """Consulta status via API Rodonaves."""
    try:
        token = os.getenv("RODONAVES_TOKEN")
        url = "https://tracking-apigateway.rte.com.br/api/v1/tracking"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        payload = {
            "pedido": order_number
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        tracking_data = response.json()

        if tracking_data and tracking_data.get("tracking"):
            last_event = tracking_data["tracking"][-1]
            return {
                "order_number": order_number,
                "status": last_event.get("situacao", "em trânsito").lower(),
                "carrier": "Rodonaves",
                "estimated_delivery": last_event.get("previsaoEntrega", "N/A"),
                "last_update": last_event.get("dataEvento", datetime.now().strftime("%d/%m/%Y"))
            }
        else:
            raise ValueError("Resposta da API Rodonaves vazia ou inválida.")
    except Exception as e:
        print(f"Erro Rodonaves: {str(e)}")
        return None

def get_order_status(identifier):
    """
    Consulta Correios, Braspress ou Rodonaves, ou usa MOCK se não disponível.
    """
    identifier = ''.join(filter(str.isdigit, identifier))

    if identifier in MOCK_ORDERS:
        carrier = MOCK_ORDERS[identifier]["carrier"].lower()

        CARRIER_FETCH_FUNCTIONS = {
            "braspress": fetch_braspress_tracking,
            "correios": fetch_correios_tracking,
            "rodonaves": fetch_rodonaves_tracking,
        }

        fetch_function = CARRIER_FETCH_FUNCTIONS.get(carrier)

        if fetch_function:
            real_status = fetch_function(identifier)
            if real_status:
                return real_status
        
        # fallback se não conseguir
        order_data = MOCK_ORDERS[identifier]
        return {
            "order_number": identifier,
            "status": order_data["status"],
            "carrier": order_data["carrier"],
            "estimated_delivery": "N/A",
            "last_update": datetime.now().strftime("%d/%m/%Y")
        }

    # fallback total se o pedido não estiver nos mocks
    return {
        "order_number": identifier,
        "status": "em trânsito",
        "carrier": "Desconhecida",
        "estimated_delivery": "N/A",
        "last_update": datetime.now().strftime("%d/%m/%Y")
    }