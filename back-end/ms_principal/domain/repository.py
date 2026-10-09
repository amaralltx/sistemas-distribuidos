# domain/repository.py
import threading

class RepositorioPedidos:
    def __init__(self):
        self._pedidos = {}
        self._lock = threading.Lock()

    def salvar(self, id_pedido, dados_pedido):
        with self._lock:
            self._pedidos[id_pedido] = dados_pedido

    def atualizar_status(self, id_pedido, novo_status):
        with self._lock:
            if id_pedido in self._pedidos:
                self._pedidos[id_pedido]["status"] = novo_status
                return True
            return False

    def obter(self, id_pedido):
        with self._lock:
            return self._pedidos.get(id_pedido)

    def listar_todos(self):
        with self._lock:
            return dict(self._pedidos)

    def remover(self, id_pedido):
        with self._lock:
            if id_pedido in self._pedidos:
                del self._pedidos[id_pedido]
                return True
            return False

pedidos_db = RepositorioPedidos()