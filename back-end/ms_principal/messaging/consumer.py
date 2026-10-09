# messaging/consumer.py
import json
from rabbitmq import iniciar_consumidor
from config import TAG, EXCHANGE_NAME, EXCHANGE_TYPE, QUEUE_NAME
from domain.repository import pedidos_db
from services.sse_manager import notificar_sse
from messaging.publisher import publicador

def processar_atualizacao_status(routing_key, body_mensagem):
    """Consome os eventos do RabbitMQ, atualiza o pedido e notifica a fila SSE."""
    try:
        dados = json.loads(body_mensagem.decode('utf-8'))
        id_pedido = dados.get("id_pedido")

        if not pedidos_db.obter(id_pedido):
            return

        print(f"{TAG} Evento recebido do RabbitMQ: '{routing_key}' para Pedido #{id_pedido}")

        status_map = {
            'pedido.estoque_ok': "Estoque Reservado. Aguardando Pagamento.",
            'estoque.indisponivel': "Estoque Indisponível. Pedido Cancelado.",
            'pagamento.aprovado': "Pagamento Aprovado. Aguardando Envio.",
            'pagamento.recusado': "Pagamento Recusado. Pedido Cancelado.",
            'pedido.enviado': "Pedido Enviado.",
        }
        novo_status = status_map.get(routing_key)
        
        if novo_status:
            pedidos_db.atualizar_status(id_pedido, novo_status)
            pedido = pedidos_db.obter(id_pedido)
            print(f"{TAG} Status do Pedido #{id_pedido} atualizado para: '{pedido['status']}'")

            # Emite atualização SSE em tempo real
            notificar_sse(id_pedido, {
                "id_pedido": id_pedido,
                "status": pedido["status"],
                "routing_key": routing_key
            })

        if routing_key in ['estoque.indisponivel', 'pagamento.recusado']:
            print(f"{TAG} Emitindo 'pedido.excluido' para o Pedido #{id_pedido}...")
            pedidos_db.remover(id_pedido)
            publicador.publicar('pedido.excluido', body_mensagem)

    except Exception as e:
        print(f"{TAG} Erro ao processar evento '{routing_key}': {e}")

def iniciar_escuta():
    """Inscrição do consumidor do MS Principal no RabbitMQ."""
    iniciar_consumidor(
        exchange=EXCHANGE_NAME,
        exchange_type=EXCHANGE_TYPE,
        nome_fila=QUEUE_NAME,
        routing_keys=[
            'pagamento.aprovado',
            'pagamento.recusado',
            'pedido.enviado',
            'pedido.estoque_ok',
            'estoque.indisponivel',
        ],
        callback_negocio=processar_atualizacao_status,
        nome_consumidor='MS Principal'
    )