# microservicos/ms_entrega/rabbitmq.py

import os
import pika
from assinatura import AssinaturaDigital

# indentificador do MS
TAG = "\033[90m[MS Entrega]\033[0m" 
RABBITMQ_HOST = 'localhost'

class Publicador:
    def __init__(self, exchange, exchange_type, nome_remetente):
        self.exchange = exchange
        self.exchange_type = exchange_type
        self.nome_remetente = nome_remetente
        self.assinador = AssinaturaDigital()
        
        parametros = pika.ConnectionParameters(host=RABBITMQ_HOST)
        self.connection = pika.BlockingConnection(parametros)
        self.channel = self.connection.channel()
        
        self.channel.exchange_declare(exchange=self.exchange, exchange_type=self.exchange_type)
        print(f"{TAG} Conexão persistente estabelecida. Exchange '{self.exchange}' pronta.")

    def publicar(self, routing_key, mensagem):
        body_bytes = mensagem.encode('utf-8') if isinstance(mensagem, str) else mensagem
        assinatura_b64 = self.assinador.assinar_mensagem(body_bytes)
        
        propriedades = pika.BasicProperties(
            headers={
                'Signature': assinatura_b64,
                'remetente': self.nome_remetente
            }
        )

        self.channel.basic_publish(
            exchange=self.exchange,
            routing_key=routing_key,
            body=body_bytes,
            properties=propriedades
        )
        print(f"{TAG} Mensagem enviada com routing_key '{routing_key}'")


def iniciar_consumidor(exchange, exchange_type, nome_fila, routing_keys, callback_negocio, nome_consumidor):
    assinador = AssinaturaDigital()
    pasta_public = "public"
    
    if os.path.exists(pasta_public):
        for arquivo in os.listdir(pasta_public):
            if arquivo.endswith(".pem"):
                remetente = arquivo.replace("chave_publica_", "").replace(".pem", "")
                caminho_chave = os.path.join(pasta_public, arquivo)
                assinador.carregar_chave_publica(remetente, caminho_chave)

    parametros = pika.ConnectionParameters(host=RABBITMQ_HOST)
    connection = pika.BlockingConnection(parametros)
    channel = connection.channel()
    
    channel.exchange_declare(exchange=exchange, exchange_type=exchange_type)
    
    result = channel.queue_declare(queue=nome_fila, durable=True, exclusive=(nome_fila == ''))
    fila_real = result.method.queue

    if isinstance(routing_keys, str):
        routing_keys = [routing_keys]
        
    for rk in routing_keys:
        channel.queue_bind(exchange=exchange, queue=fila_real, routing_key=rk)

    def callback_interno(ch, method, properties, body):
        print(f"{TAG} Mensagem recebida na fila '{fila_real}' (Routing Key: '{method.routing_key}')")
        
        headers = properties.headers or {}
        assinatura = headers.get('Signature')
        remetente = headers.get('remetente')

        if not assinatura or not remetente or not assinador.validar_assinatura(body, assinatura, remetente):
            print(f"{TAG} Falha na validação da assinatura digital de '{remetente}'.")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        
        callback_negocio(method.routing_key, body)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=fila_real, on_message_callback=callback_interno, auto_ack=False)
    channel.start_consuming()