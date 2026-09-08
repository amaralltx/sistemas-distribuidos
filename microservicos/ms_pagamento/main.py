# microservicos/ms_pagamento/main.py

import random, json, time
from rabbitmq import Publicador, iniciar_consumidor

# identificador do MS
TAG = f"\033[91m[MS Pagamento]\033[0m"

# cria um publicador para enviar mensagens para o exchange 'eCommerce' do tipo direct
publicador = Publicador(exchange='eCommerce', exchange_type='direct')

def processar_pagamento(routing_key, body_mensagem):
    # Lendo o pacote para pegar o ID do pedido
    dados = json.loads(body_mensagem.decode('utf-8'))
    id_pedido = dados.get("id_pedido", "Desconhecido")
    
    print(f"\n{TAG} Processando cobrança para o Pedido #{id_pedido}...")
    
    time.sleep(2) # Apenas para dar um "charme" de processamento no terminal
    aprovado = random.choice([True, False])
    
    if aprovado:
        print(f"{TAG} Transação aprovada para o Pedido #{id_pedido}.")
        publicador.publicar('pagamento.aprovado', body_mensagem)
    else:
        print(f"{TAG} Transação recusada para o Pedido #{id_pedido}.")
        publicador.publicar('pagamento.recusado', body_mensagem)

if __name__ == '__main__':
    print(f"Iniciando {TAG}...")
    iniciar_consumidor(
        exchange='eCommerce',
        exchange_type='direct',
        nome_fila='fila_pagamento',
        routing_keys=['pedido.estoque_ok'],
        callback_negocio=processar_pagamento
    )