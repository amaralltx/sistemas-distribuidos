import json
import pika
from assinatura import AssinaturaDigital

TAG = "\033[96m[Consumidor C1 - Categorias A e B]\033[0m"
RABBITMQ_HOST = 'localhost'
EXCHANGE = 'Promoções'
EXCHANGE_TYPE = 'topic'
NOME_FILA = 'fila_c1'
ROUTING_KEYS = ['promocao.categoria.A', 'promocao.categoria.B']

assinador = AssinaturaDigital()
assinador.carregar_chave_publica('ms_promocoes', 'public/chave_publica_ms_promocoes.pem')

def processar_promocao(routing_key, body):
    dados = json.loads(body.decode('utf-8'))
    print(f"{TAG} [{routing_key}] {dados['descricao']}")

def main():
    parametros = pika.ConnectionParameters(host=RABBITMQ_HOST)
    connection = pika.BlockingConnection(parametros)
    channel = connection.channel()

    channel.exchange_declare(exchange=EXCHANGE, exchange_type=EXCHANGE_TYPE)

    result = channel.queue_declare(queue=NOME_FILA, durable=True)
    fila_real = result.method.queue

    for rk in ROUTING_KEYS:
        channel.queue_bind(exchange=EXCHANGE, queue=fila_real, routing_key=rk)
        print(f"{TAG} Fila '{fila_real}' associada à routing key '{rk}'")

    def callback(ch, method, properties, body):
        headers = properties.headers or {}
        assinatura = headers.get('Signature')
        remetente = headers.get('remetente')

        if not assinatura or not remetente:
            print(f"{TAG} Ausencia de assinatura ou remetente.")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        if not assinador.validar_assinatura(body, assinatura, remetente):
            print(f"{TAG} Assinatura inválida por '{remetente}'.")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        processar_promocao(method.routing_key, body)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=fila_real, on_message_callback=callback, auto_ack=False)

    print(f"{TAG} Aguardando promoções das categorias A e B. Pressione Ctrl+C para encerrar.")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print(f"\n{TAG} Encerrando consumidor C1...")
        channel.stop_consuming()
        connection.close()

if __name__ == '__main__':
    main()