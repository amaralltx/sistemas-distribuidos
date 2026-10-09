# messaging/publisher.py
from rabbitmq import Publicador
from config import EXCHANGE_NAME, EXCHANGE_TYPE, SENDER_NAME

publicador = Publicador(
    exchange=EXCHANGE_NAME,
    exchange_type=EXCHANGE_TYPE,
    nome_remetente=SENDER_NAME
)