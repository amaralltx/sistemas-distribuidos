from rabbitmq import Publicador, iniciar_consumidor

# identificador do MS
TAG = f"\033[90m[MS Entrega]\033[0m"

# cria um publicador para enviar mensagens para o exchange 'eCommerce' do tipo direct
publicador = Publicador(exchange='eCommerce', exchange_type='direct', nome_remetente='entrega')

def processar_entrega(routing_key, body_mensagem):
    print(f"{TAG} Processando entrega e preparando pacote para: {routing_key}")    
    publicador.publicar('pedido.enviado', body_mensagem)

if __name__ == '__main__':
    print(f"Iniciando {TAG}...")

    iniciar_consumidor(
        exchange='eCommerce',
        exchange_type='direct',
        nome_fila='fila_entrega',
        routing_keys=['pagamento.aprovado'],
        callback_negocio=processar_entrega,
        nome_consumidor='MS Entrega'
    )