# services/sse_manager.py
# Gerencia as conexões SSE: quem está ouvindo cada pedido e o histórico de eventos.
import queue
import threading

# id_pedido -> lista de filas (uma por conexão SSE aberta)
_subscritores = {}
# id_pedido -> lista de eventos já ocorridos (para reenviar a quem conectar tarde)
_historico = {}
_lock = threading.Lock()


def registrar_evento(id_pedido, evento):
    """Guarda o evento no histórico e o envia a todos os clientes conectados."""
    with _lock:
        _historico.setdefault(id_pedido, []).append(evento)
        filas = list(_subscritores.get(id_pedido, []))
    for fila in filas:
        fila.put(evento)


def assinar(id_pedido):
    """Cria uma fila para uma nova conexão e devolve (fila, eventos já ocorridos).
    A fila é criada e o histórico é copiado no mesmo bloqueio, então nenhum
    evento se perde entre as duas operações."""
    fila = queue.Queue()
    with _lock:
        _subscritores.setdefault(id_pedido, []).append(fila)
        historico = list(_historico.get(id_pedido, []))
    return fila, historico


def cancelar_assinatura(id_pedido, fila):
    """Remove a fila quando o cliente desconecta."""
    with _lock:
        filas = _subscritores.get(id_pedido, [])
        if fila in filas:
            filas.remove(fila)
        if not filas:
            _subscritores.pop(id_pedido, None)


def existe_historico(id_pedido):
    with _lock:
        return id_pedido in _historico


def apagar_historico(id_pedido):
    """Libera a memória de um pedido que terminou."""
    with _lock:
        _historico.pop(id_pedido, None)