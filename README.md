<<<<<<< HEAD
(seu conteúdo local)
# Rastreador de Pedidos WhatsApp
Projeto para rastrear status de pedidos via WhatsApp.


# Rastreador de Pedidos WhatsApp
Projeto para rastrear status de pedidos via WhatsApp.
# Webhook para Rastreamento de Pedidos via WhatsApp

Este projeto implementa um webhook para rastreamento inteligente de pedidos via WhatsApp, integrando as APIs do Twilio e OpenAI para fornecer respostas personalizadas e humanizadas sobre o status de pedidos.

## Funcionalidades

- Recebimento de mensagens do WhatsApp via Twilio
- Simulação de consulta de status de pedidos (preparado para futura integração com APIs reais)
- Geração de respostas humanizadas utilizando a OpenAI API (GPT-4)
- Envio de respostas personalizadas de volta ao cliente via WhatsApp

## Requisitos

- Python 3.10 ou superior
- Flask
- Twilio
- OpenAI
- python-dotenv

## Configuração do Ambiente

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/webhook-rastreamento.git
cd webhook-rastreamento
```

### 2. Crie e ative um ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install flask twilio openai python-dotenv
```

### 4. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```
# Configurações da API OpenAI
OPENAI_API_KEY=sua_chave_api_openai_aqui

# Configurações da API Twilio
TWILIO_ACCOUNT_SID=seu_account_sid_twilio_aqui
TWILIO_AUTH_TOKEN=seu_auth_token_twilio_aqui
TWILIO_PHONE_NUMBER=seu_numero_whatsapp_twilio_aqui

# Configurações do servidor
PORT=5000
DEBUG=True
```

## Estrutura do Projeto

```
webhook_rastreamento/
├── app/
│   ├── __init__.py          # Inicialização da aplicação Flask
│   ├── webhook.py           # Endpoints para receber mensagens do Twilio
│   ├── openai_integration.py # Integração com a API da OpenAI
│   └── order_tracking.py    # Simulação de consulta de status de pedidos
├── .env                     # Variáveis de ambiente (não versionado)
└── run.py                   # Script para iniciar a aplicação
```

## Executando o Projeto

Para iniciar o servidor localmente:

```bash
python run.py
```

O servidor estará disponível em `http://localhost:5000`.

## Configuração do Twilio

Para configurar o Twilio para enviar mensagens do WhatsApp para o seu webhook:

1. Crie uma conta no [Twilio](https://www.twilio.com/)
2. Ative o sandbox do WhatsApp no console do Twilio
3. Configure a URL do webhook para apontar para o seu endpoint:
   - Se estiver testando localmente, use uma ferramenta como ngrok para expor seu servidor local
   - URL do webhook: `https://seu-dominio.com/webhook` ou `https://seu-tunnel-ngrok.io/webhook`

## Implantação

### Implantação em VPS

1. Conecte-se ao seu servidor via SSH
2. Clone o repositório e configure o ambiente conforme as instruções acima
3. Instale e configure o Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "run:app"
```

4. Configure o Nginx como proxy reverso (opcional, mas recomendado)
5. Configure o serviço systemd para manter a aplicação em execução

### Implantação no Render

1. Crie uma conta no [Render](https://render.com/)
2. Crie um novo Web Service e conecte ao seu repositório Git
3. Configure o serviço:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn run:app`
4. Adicione as variáveis de ambiente necessárias nas configurações do serviço

### Implantação no Heroku

1. Crie uma conta no [Heroku](https://www.heroku.com/)
2. Instale o Heroku CLI e faça login
3. Crie um arquivo `Procfile` na raiz do projeto com o conteúdo:

```
web: gunicorn run:app
```

4. Crie um arquivo `requirements.txt`:

```bash
pip freeze > requirements.txt
```

5. Implante a aplicação:

```bash
heroku create webhook-rastreamento
git push heroku main
```

6. Configure as variáveis de ambiente no dashboard do Heroku

## Testando o Webhook

Para testar o webhook:

1. Certifique-se de que o servidor está em execução e acessível publicamente
2. Configure o Twilio para apontar para o seu webhook
3. Envie uma mensagem para o número do WhatsApp do Twilio com um número de pedido ou CPF
4. Você deverá receber uma resposta humanizada sobre o status do pedido

## Futuras Melhorias

- Integração com APIs reais de transportadoras (Correios, Braspress, Rodonaves)
- Implementação de autenticação para maior segurança
- Adição de funcionalidades de logging e monitoramento
- Suporte a múltiplos idiomas

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para mais detalhes.
(conteúdo do GitHub)
>>>>>>> main
=======
# Rastreador
>>>>>>> fb334a630cf44d53709be5701d238e18a4fcd4f2
=======
# Rastreador
>>>>>>> fb334a630cf44d53709be5701d238e18a4fcd4f2

