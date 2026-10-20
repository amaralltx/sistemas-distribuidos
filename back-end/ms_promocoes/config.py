# ms_promocoes/config.py
import os
from dotenv import load_dotenv

load_dotenv()

TAG = "\033[95m[MS Promoções]\033[0m"

# RabbitMQ
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
EXCHANGE_NAME = "eCommerce"
EXCHANGE_TYPE = "direct"
QUEUE_NAME = "fila_promocoes"
ROUTING_KEYS = ["interesse.promocao"]

# API externa de e-mail (Resend)
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "").strip()
EMAIL_FROM = os.getenv("EMAIL_FROM", "Loja <onboarding@resend.dev>")
# sem chave configurada, os e-mails apenas são impressos no console
EMAIL_DRY_RUN = os.getenv("EMAIL_DRY_RUN", "").strip() == "1" or not RESEND_API_KEY
EMAIL_INTERVALO_SEG = float(os.getenv("EMAIL_INTERVALO_SEG", "0.6"))  # respeita o rate limit da Resend
EMAIL_CONFIRMACAO = os.getenv("EMAIL_CONFIRMACAO", "1") == "1"

# Geração de promoções
PROMO_INTERVALO_SEG = float(os.getenv("PROMO_INTERVALO_SEG", "30"))
ESTOQUE_URL = os.getenv("ESTOQUE_URL", "http://localhost:5001")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
ARQUIVO_INSCRICOES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inscricoes.json")
