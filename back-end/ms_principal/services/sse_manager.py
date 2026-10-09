# services/sse_manager.py
import queue
import threading

sse_subscribers = {}
sse_lock = threading.Lock()

def registrar_subscritor(id_pedido):
    """Cria e registra uma fila de eventos para a conexão SSE de um pedido."""
    q = queue.Queue()
    with sse_lock:
        if id_pedido not in sse_subscribers:
            sse_subscribers[id_pedido] = []
        sse_subscribers[id_pedido].append(q)
    return q

def desregistrar_subscritor(id_pedido, q):
    """Remove a fila de eventos quando a conexão do cliente é encerrada."""
    with sse_lock:
        if id_pedido in sse_subscribers:
            if q in sse_subscribers[id_pedido]:
                sse_subscribers[id_pedido].remove(q)
            if not sse_subscribers[id_pedido]:
                del sse_subscribers[id_pedido]

def notificar_sse(id_pedido, dados_evento):
    """Encaminha o novo status do pedido para todas as conexões SSE ativas do pedido."""
    with sse_lock:
        if id_pedido in sse_subscribers:
            for q in sse_subscribers[id_pedido]:
                q.put(dados_evento)