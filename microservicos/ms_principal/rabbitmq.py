import os
import pika
from assinatura import AssinaturaDigital

RABBITMQ_HOST = 'localhost'

class Publicador:
    def __init__(self, exchange, exchange_type, nome_remetente):
        self.exchange = exchange
        self.exchange_type = exchange_type
        self.nome_remetente = nome_remetente
        self.assinador = AssinaturaDigital()
        
        parametros = pika.ConnectionParameters(host=RABBITMQ_HOST, heartbeat=0)
        self.connection = pika.BlockingConnection(parametros)
        self.channel = self.connection.channel()
        
        self.channel.exchange_declare(exchange=self.exchange, exchange_type=self.exchange_type)

    def publicar(self, routing_key, mensagem):
        body_bytes = mensagem.encode('utf-8') if isinstance(mensagem, str) else mensagem
        
        # gera a assinatura digital e adiciona no cabeçalho da mensagem
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

def iniciar_consumidor(exchange, exchange_type, nome_fila, routing_keys, callback_negocio, nome_consumidor):
    """Intercepta a mensagem, valida a assinatura e passa para o callback_negocio."""
    assinador = AssinaturaDigital()
    
    # carrega as chaves públicas dos outros MS
    pasta_public = "public"
    if os.path.exists(pasta_public):
        for arquivo in os.listdir(pasta_public):
            if arquivo.endswith(".pem"):
                remetente = arquivo.replace("chave_publica_", "").replace(".pem", "")
                caminho_chave = os.path.join(pasta_public, arquivo)
                assinador.carregar_chave_publica(remetente, caminho_chave)
    else:
        print(f"[{nome_consumidor}] Aviso: Pasta '{pasta_public}' não encontrada. Nenhuma chave pública carregada.")

    parametros = pika.ConnectionParameters(host=RABBITMQ_HOST)
    connection = pika.BlockingConnection(parametros)
    channel = connection.channel()

    channel.exchange_declare(exchange=exchange, exchange_type=exchange_type)
    result = channel.queue_declare(queue=nome_fila, durable=True)
    fila_real = result.method.queue

    for rk in routing_keys:
        channel.queue_bind(exchange=exchange, queue=fila_real, routing_key=rk)

    def callback_interno(ch, method, properties, body):
        headers = properties.headers or {}
        assinatura = headers.get('Signature')
        remetente = headers.get('remetente')

        if not assinatura or not remetente:
            print(f"[{nome_consumidor}] Sem assinatura digital ou remetente.")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        if not assinador.validar_assinatura(body, assinatura, remetente):
            print(f"[{nome_consumidor}] Assinatura inválida do '{remetente}'.")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        # se passou na assinatura, chama o callback
        callback_negocio(method.routing_key, body)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=fila_real, on_message_callback=callback_interno, auto_ack=False)
    
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print(f"\n[{nome_consumidor}] Encerrando consumo...")
        channel.stop_consuming()
        connection.close()