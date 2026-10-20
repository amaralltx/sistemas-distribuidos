# ms_promocoes/rabbitmq.py
# Consumidor do MS Promoções: valida a assinatura digital antes de repassar o evento.
import os

import pika

from assinatura import AssinaturaDigital
from config import RABBITMQ_HOST, TAG


def iniciar_consumidor(exchange, exchange_type, nome_fila, routing_keys, callback_negocio):
    assinador = AssinaturaDigital()

    # carrega as chaves públicas dos remetentes (public/principal.pem -> 'principal')
    pasta_public = "public"
    if os.path.exists(pasta_public):
        for arquivo in os.listdir(pasta_public):
            if arquivo.endswith(".pem"):
                remetente = arquivo.replace("chave_publica_", "").replace(".pem", "")
                assinador.carregar_chave_publica(remetente, os.path.join(pasta_public, arquivo))
    else:
        print(f"{TAG} Aviso: pasta '{pasta_public}' não encontrada. Nenhuma chave pública carregada.")

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange, exchange_type=exchange_type)
    fila_real = channel.queue_declare(queue=nome_fila, durable=True).method.queue
    for rk in routing_keys:
        channel.queue_bind(exchange=exchange, queue=fila_real, routing_key=rk)

    def callback_interno(ch, method, properties, body):
        headers = properties.headers or {}
        assinatura = headers.get("Signature")
        remetente = headers.get("remetente")

        if not assinatura or not remetente or not assinador.validar_assinatura(body, assinatura, remetente):
            print(f"{TAG} Assinatura ausente/inválida de '{remetente}'. Evento descartado.")
        else:
            callback_negocio(method.routing_key, body)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=fila_real, on_message_callback=callback_interno, auto_ack=False)
    print(f"{TAG} Aguardando eventos {routing_keys} na fila '{fila_real}'. Ctrl+C para encerrar.")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print(f"\n{TAG} Encerrando consumo...")
        channel.stop_consuming()
        connection.close()
