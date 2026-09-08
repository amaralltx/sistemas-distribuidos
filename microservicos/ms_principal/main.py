# microservicos/ms_principal/main.py
import json, sys, threading, uuid

from rabbitmq import Publicador, iniciar_consumidor

# indentificador do MS
TAG = "\033[94m[MS Principal]\033[0m" 

publicador = Publicador(exchange='eCommerce', exchange_type='direct')

# dict dos produtos
PRODUTOS = {
    # Categoria: Feminino
    "1": {"nome": "Vestido Floral", "preco": 120.00, "categoria": "Feminino"},
    "2": {"nome": "Blusa de Seda", "preco": 89.90, "categoria": "Feminino"},
    "3": {"nome": "Calça Jeans Skinny", "preco": 150.00, "categoria": "Feminino"},
    "4": {"nome": "Saia Midi", "preco": 95.00, "categoria": "Feminino"},
    "5": {"nome": "Casaco de Lã", "preco": 250.00, "categoria": "Feminino"},
    "6": {"nome": "T-shirt Básica Feminina", "preco": 45.00, "categoria": "Feminino"},
    "7": {"nome": "Macacão Pantalona", "preco": 180.00, "categoria": "Feminino"},

    # Categoria: Masculino
    "8": {"nome": "Camiseta de Algodão", "preco": 50.00, "categoria": "Masculino"},
    "9": {"nome": "Calça Sarja", "preco": 130.00, "categoria": "Masculino"},
    "10": {"nome": "Camisa Social Branca", "preco": 110.00, "categoria": "Masculino"},
    "11": {"nome": "Jaqueta de Couro", "preco": 300.00, "categoria": "Masculino"},
    "12": {"nome": "Bermuda Moletom", "preco": 70.00, "categoria": "Masculino"},
    "13": {"nome": "Suéter de Tricô", "preco": 140.00, "categoria": "Masculino"},
    "14": {"nome": "Terno Slim Fit", "preco": 450.00, "categoria": "Masculino"},

    # Categoria: Infantil
    "15": {"nome": "Conjunto Moletom Infantil", "preco": 85.00, "categoria": "Infantil"},
    "16": {"nome": "Vestido de Festa Infantil", "preco": 110.00, "categoria": "Infantil"},
    "17": {"nome": "Camiseta Estampa Dinossauro", "preco": 40.00, "categoria": "Infantil"},
    "18": {"nome": "Calça Jeans Kids", "preco": 90.00, "categoria": "Infantil"},
    "19": {"nome": "Pijama Brilha no Escuro", "preco": 65.00, "categoria": "Infantil"},
    "20": {"nome": "Jaqueta Corta-Vento Infantil", "preco": 100.00, "categoria": "Infantil"}
}

class RepositorioPedidos:
    def __init__(self):
        self._pedidos = {}
        self._lock = threading.Lock()

    def salvar(self, id_pedido, dados_pedido):
        with self._lock:
            self._pedidos[id_pedido] = dados_pedido

    def atualizar_status(self, id_pedido, novo_status):
        # trava para evitar race condition 
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

pedidos_db = RepositorioPedidos()

# consome os eventos de atualização e altera o status do pedido
def processar_atualizacao_status(routing_key, body_mensagem):
    try:
        dados = json.loads(body_mensagem.decode('utf-8'))
        id_pedido = dados.get("id_pedido")

        if not pedidos_db.obter(id_pedido):
            return

        print(
            f"\n{TAG} Evento recebido: '{routing_key}' para Pedido #{id_pedido}"
        )

        # mapeamento das routing keys e suas mensagens
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
            print(f"{TAG} Status atual: \033[1m{pedido['status']}\033[0m")

        # emite pedido.excluido quando há falha no fluxo
        if routing_key in ['estoque.indisponivel', 'pagamento.recusado']:
            print(
                f"{TAG} Emitindo 'pedido.excluido' para o Pedido #{id_pedido}..."
            )
            publicador.publicar('pedido.excluido', body_mensagem)

    except Exception as e:
        print(f"{TAG} Erro ao processar evento '{routing_key}': {e}")


def iniciar_escuta():

    # inscreve o MS Principal nas routing keys
    iniciar_consumidor(
        exchange='eCommerce',
        exchange_type='direct',
        nome_fila='fila_principal',
        routing_keys=[
            'pagamento.aprovado',
            'pagamento.recusado',
            'pedido.enviado',
            'pedido.estoque_ok',
            'estoque.indisponivel',
        ],
        callback_negocio=processar_atualizacao_status,
    )


def realizar_pedido():
    print("\nCATÁLOGO\n")
    for codigo, info in PRODUTOS.items():
        print(f"[{codigo}] {info['nome']} - R$ {info['preco']:.2f} (Categoria: {info['categoria']})")
    
    codigo = input("\nDigite o código do produto para comprar: ").strip()
    if codigo not in PRODUTOS:
        print(f"{TAG} Código de produto inválido.")
        return

    try:
        quantidade = int(input("Digite a quantidade: "))
        if quantidade <= 0:
            print(f"{TAG} A quantidade deve ser maior que zero.")
            return
    except ValueError:
        print(f"{TAG} Entrada de quantidade inválida.")
        return

    id_pedido = str(uuid.uuid4())[:8] # gera um ID curto para o pedido
    item = PRODUTOS[codigo]

    # prepara o payload para o pedido
    payload = {
        "id_pedido": id_pedido,
        "produtos": [{
            "codigo": codigo,
            "nome": item["nome"],
            "quantidade": quantidade,
            "preco_unitario": item["preco"],
            "categoria": item["categoria"],
        }],
        "valor_total": item["preco"] * quantidade,
    }

    pedidos_db.salvar(
        id_pedido,
        {
            "itens": payload["produtos"],
            "valor_total": payload["valor_total"],
            "status": "Criado",
        },
    )

    # publica o evento de criação do pedido
    publicador.publicar('pedido.criado', json.dumps(payload))
    print(f"{TAG} Pedido #{id_pedido} criado com sucesso e publicado!")

def consultar_pedidos():
    pedidos = pedidos_db.listar_todos()
    if not pedidos:
        print(f"\n{TAG} Nenhum pedido registrado.")
        return

    print("\nPEDIDOS\n")
    for id_p, info in pedidos.items():
        print(f"ID: #{id_p} | Status: {info['status']} | Total: R$ {info['valor_total']:.2f}")
        for item in info["itens"]:
            print(f"   - {item['quantidade']}x {item['nome']}")

def excluir_pedido():
    id_pedido = input("\nDigite o ID do pedido que deseja excluir: ").strip()
    pedido = pedidos_db.obter(id_pedido)
    
    if not pedido:
        print(f"{TAG} Pedido não encontrado.")
        return

    if "Cancelado" in pedido["status"]:
        print(f"{TAG} Este pedido já está cancelado.")
        return

    pedidos_db.atualizar_status(id_pedido, "Cancelado pelo Usuário")
    payload = json.dumps({"id_pedido": id_pedido})
    publicador.publicar('pedido.excluido', payload)
    print(f"{TAG} Pedido #{id_pedido} cancelado.")

def executar_menu():
    while True:
        print("\nMENU\n")
        print("1. Realizar pedido")
        print("2. Excluir pedido")
        print("3. Consultar pedidos e status")
        print("0. Sair")
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == "1":
            realizar_pedido()
        elif opcao == "2":
            excluir_pedido()
        elif opcao == "3":
            consultar_pedidos()
        elif opcao == "0":
            print(f"{TAG} Encerrando MS Principal...")
            sys.exit(0)
        else:
            print("\nOpção inválida. Tente novamente.")


def main():
    # inicia a escuta de eventos em outra thread
    thread_consumidor = threading.Thread(target=iniciar_escuta, daemon=True)
    thread_consumidor.start()

    # recebe o input do usuário na thread principal
    executar_menu()

if __name__ == '__main__':
    main()