import os
import requests
from datetime import datetime

# --- Mock de pedidos associados a CPF/CNPJ ---
MOCK_CPF_TO_ORDER = {
    "12345678900": "123456",
    "00123456000100": "789012",
    "98765432100": "345678",
    "11122233344": "999999",
}

# --- Mock de status dos pedidos ---
MOCK_ORDERS = {
    "123456": {"status": "em trânsito", "carrier": "Correios"},
    "789012": {"status": "saiu para entrega", "carrier": "Braspress"},
    "345678": {"status": "entregue", "carrier": "Rodonaves"},
    "999999": {"status": "em trânsito", "carrier": "Correios"},
}

# --- Configuração ---
DEFAULT_TIMEOUT = 5  # Segundos para timeout padrão

# --- Funções de Rastreamento das Transportadoras ---

def fetch_braspress_tracking(order_number):
    """Busca o rastreamento na Braspress."""
    cnpj = os.getenv("BRASPRESS_CNPJ")
    if not cnpj:
        print("[Braspress] CNPJ não configurado.")
        return None

    try:
        url = f"https://api.braspress.com/v3/tracking/byNumPedido/{cnpj}/{order_number}/json"
        response = requests.get(url, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()

        try:
            tracking_data = response.json()
        except Exception as e:
            print(f"[Braspress] Erro ao ler JSON: {e}")
            return None

        if tracking_data and isinstance(tracking_data, list):
            return parse_tracking_response(order_number, tracking_data[-1], "Braspress")

    except Exception as e:
        print(f"[Braspress] Erro na API: {e}")
    return None

def fetch_correios_tracking(order_number):
    """Busca o rastreamento nos Correios."""
    correios_user = os.getenv("CORREIOS_USER")
    correios_pass = os.getenv("CORREIOS_PASS")
    if not correios_user or not correios_pass:
        print("[Correios] Usuário ou senha não configurados.")
        return None

    try:
        url = f"https://api.linkdoscorreios/sro?usuario={correios_user}&senha={correios_pass}&codigo={order_number}"
        response = requests.get(url, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()

        try:
            tracking_data = response.json()
        except Exception as e:
            print(f"[Correios] Erro ao ler JSON: {e}")
            return None

        if tracking_data:
            return parse_tracking_response(order_number, tracking_data.get("eventos", [{}])[-1], "Correios")

    except Exception as e:
        print(f"[Correios] Erro na API: {e}")
    return None

def fetch_rodonaves_tracking(order_number):
    """Busca o rastreamento na Rodonaves."""
    token = os.getenv("RODONAVES_TOKEN")
    if not token:
        print("[Rodonaves] Token não configurado.")
        return None

    try:
        url = "https://tracking-apigateway.rte.com.br/api/v1/tracking"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {"pedido": order_number}

        response = requests.post(url, json=payload, headers=headers, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()

        try:
            tracking_data = response.json()
        except Exception as e:
            print(f"[Rodonaves] Erro ao ler JSON: {e}")
            return None

        if tracking_data and tracking_data.get("tracking"):
            return parse_tracking_response(order_number, tracking_data["tracking"][-1], "Rodonaves")

    except Exception as e:
        print(f"[Rodonaves] Erro na API: {e}")
    return None

# --- Funções Auxiliares ---

def parse_tracking_response(order_number, event_data, carrier):
    """Formata o evento de rastreamento em um dicionário padrão."""
    return {
        "order_number": order_number,
        "status": event_data.get("situacao") or event_data.get("descricao") or "em trânsito",
        "carrier": carrier,
        "estimated_delivery": event_data.get("previsaoEntrega", "N/A"),
        "last_update": event_data.get("data") or event_data.get("dataEvento") or today(),
    }

def today():
    """Retorna a data de hoje formatada."""
    return datetime.now().strftime("%d/%m/%Y")

def generate_unknown_order(identifier):
    """Cria um rastreamento padrão para pedidos desconhecidos."""
    return {
        "order_number": identifier,
        "status": "em trânsito",
        "carrier": "Desconhecida",
        "estimated_delivery": "N/A",
        "last_update": today()
    }

# --- Função Principal ---

def get_order_status(identifier):
    """
    Obtém o status do pedido a partir do CPF/CNPJ informado.
    Garante que sempre haverá uma resposta, mesmo que as APIs reais falhem.
    """
    identifier = ''.join(filter(str.isdigit, identifier))
    order_number = MOCK_CPF_TO_ORDER.get(identifier)

    if not order_number:
        print(f"CPF/CNPJ {identifier} não encontrado no mock.")
        return generate_unknown_order(identifier)

    return fetch_order(order_number)

def fetch_order(order_number):
    """
    Busca o status do pedido pelo número, tentando APIs reais e caindo para Mock se necessário.
    """
    order_info = MOCK_ORDERS.get(order_number)

    if not order_info:
        print(f"Pedido {order_number} não encontrado no mock.")
        return generate_unknown_order(order_number)

    carrier = order_info["carrier"].lower()
    carrier_fetcher = {
        "braspress": fetch_braspress_tracking,
        "correios": fetch_correios_tracking,
        "rodonaves": fetch_rodonaves_tracking,
    }.get(carrier)

    if carrier_fetcher:
        real_tracking = carrier_fetcher(order_number)
        if real_tracking:
            return real_tracking

    print(f"Pedido {order_number} retornando fallback mock.")
    return {
        "order_number": order_number,
        "status": order_info["status"],
        "carrier": order_info["carrier"],
        "estimated_delivery": "N/A",
        "last_update": today()
    }