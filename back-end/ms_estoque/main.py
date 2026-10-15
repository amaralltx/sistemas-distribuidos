# ms_estoque/main.py
import json
import threading

import db
from api import iniciar_api
from rabbitmq import Publicador, iniciar_consumidor

TAG = "\033[92m[MS Estoque]\033[0m"

publicador = Publicador(exchange='eCommerce', exchange_type='direct', nome_remetente='estoque')


def processar_evento_estoque(routing_key, body_mensagem):
    print(f"{TAG} Evento recebido: {routing_key}")
    dados = json.loads(body_mensagem.decode('utf-8'))
    id_pedido = dados.get("id_pedido")

    if routing_key == 'pedido.criado':
        if db.reservar(id_pedido, dados.get("produtos", [])):
            print(f"{TAG} Estoque reservado para o Pedido #{id_pedido}.")
            publicador.publicar('pedido.estoque_ok', body_mensagem)
        else:
            print(f"{TAG} Item esgotado ou insuficiente para o Pedido #{id_pedido}.")
            publicador.publicar('estoque.indisponivel', body_mensagem)

    elif routing_key == 'pedido.excluido':
        devolvidos = db.devolver(id_pedido)
        if devolvidos:
            print(f"{TAG} Itens do Pedido #{id_pedido} devolvidos ao estoque.")
        else:
            print(f"{TAG} Pedido #{id_pedido} não tinha reserva; nada a devolver.")


if __name__ == '__main__':
    print(f"Iniciando {TAG}...")
    db.inicializar()

    # a API roda em outra thread, porque start_consuming() bloqueia a thread principal
    threading.Thread(target=iniciar_api, daemon=True).start()

    iniciar_consumidor(
        exchange='eCommerce',
        exchange_type='direct',
        nome_fila='fila_estoque',
        routing_keys=['pedido.criado', 'pedido.excluido'],
        callback_negocio=processar_evento_estoque,
        nome_consumidor='MS Estoque'
    )