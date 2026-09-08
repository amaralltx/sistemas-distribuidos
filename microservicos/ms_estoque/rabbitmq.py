# microservicos/ms_estoque/rabbitmq.py

import pika

# indentificador do MS
TAG = "\033[92m[MS Estoque]\033[0m" 
RABBITMQ_HOST = 'localhost'

class Publicador:
    def __init__(self, exchange, exchange_type):
        self.exchange = exchange
        self.exchange_type = exchange_type
        
        parametros = pika.ConnectionParameters(host=RABBITMQ_HOST)
        self.connection = pika.BlockingConnection(parametros)
        self.channel = self.connection.channel()
        
        self.channel.exchange_declare(exchange=self.exchange, exchange_type=self.exchange_type)
        print(f"{TAG} Conexão persistente estabelecida. Exchange '{self.exchange}' pronta.")

    def publicar(self, routing_key, mensagem):
        self.channel.basic_publish(
            exchange=self.exchange,
            routing_key=routing_key,
            body=mensagem
        )
        print(f"{TAG} Mensagem enviada com routing_key '{routing_key}'")


def iniciar_consumidor(exchange, exchange_type, nome_fila, routing_keys, callback_negocio):

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
        
        # TODO: validar a assinatura digital contida em 'properties.headers'[cite: 1]
        
        callback_negocio(method.routing_key, body)
        
        # Confirmação manual de processamento
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=fila_real, on_message_callback=callback_interno, auto_ack=False)
    channel.start_consuming()