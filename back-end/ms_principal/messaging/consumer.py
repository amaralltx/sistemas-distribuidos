# messaging/consumer.py
import json
import itertools
import threading
from rabbitmq import iniciar_consumidor
from config import TAG, EXCHANGE_NAME, EXCHANGE_TYPE, QUEUE_NAME
from domain.repository import pedidos_db
from services import sse_manager
from messaging.publisher import publicador

# mapeamento da routing key ao texto exibido e estado
ESTADOS = {
    'pedido.estoque_ok':    ("Estoque Reservado. Aguardando Pagamento.", False),
    'estoque.indisponivel': ("Estoque Indisponível. Pedido Cancelado.", True),
    'pagamento.aprovado':   ("Pagamento Aprovado. Aguardando Envio.", False),
    'pagamento.recusado':   ("Pagamento Recusado. Pedido Cancelado.", True),
    'pedido.enviado':       ("Pedido Enviado.", True),
}

_seq = itertools.count(1) # contador por pedido para o frontend ordenar e detectar duplicatas
_seq_lock = threading.Lock() # lock para proteger o contador


def processar_atualizacao_status(routing_key, body_mensagem):
    """Consome os eventos do RabbitMQ, atualiza o pedido e notifica os clientes SSE."""
    try:
        dados = json.loads(body_mensagem.decode('utf-8'))
        id_pedido = dados.get("id_pedido")

        if not pedidos_db.obter(id_pedido) or routing_key not in ESTADOS:
            return

        texto, final = ESTADOS[routing_key]
        pedidos_db.atualizar_status(id_pedido, texto)

        with _seq_lock:
            seq = next(_seq)

        evento = {
            "seq": seq,
            "id_pedido": id_pedido,
            "status": texto,
            "routing_key": routing_key,
            "final": final,
        }
        print(f"{TAG} Pedido #{id_pedido}: '{texto}'")
        sse_manager.registrar_evento(id_pedido, evento)

        if routing_key in ('estoque.indisponivel', 'pagamento.recusado'):
            print(f"{TAG} Emitindo 'pedido.excluido' para o Pedido #{id_pedido}...")
            publicador.publicar('pedido.excluido', body_mensagem)

    except Exception as e:
        print(f"{TAG} Erro ao processar evento '{routing_key}': {e}")


def iniciar_escuta():
    """Inscrição do consumidor do MS Principal no RabbitMQ."""
    iniciar_consumidor(
        exchange=EXCHANGE_NAME,
        exchange_type=EXCHANGE_TYPE,
        nome_fila=QUEUE_NAME,
        routing_keys=list(ESTADOS.keys()),
        callback_negocio=processar_atualizacao_status,
        nome_consumidor='MS Principal',
    )