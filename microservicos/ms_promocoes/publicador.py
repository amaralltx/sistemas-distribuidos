import pika
from assinatura import AssinaturaDigital

# identificador do MS
TAG = "\033[95m[MS Promoções]\033[0m"
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
        print(f"{TAG} Mensagem '{routing_key}' enviada com Assinatura Digital.")