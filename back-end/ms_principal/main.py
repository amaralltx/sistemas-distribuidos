# microservicos/ms_principal/main.py
import json, sys, threading, uuid, time
from flask import Flask, jsonify, request
from flask_cors import CORS
from rabbitmq import Publicador, iniciar_consumidor

# Identificador do MS para logs
TAG = "\033[94m[MS Principal]\033[0m" 

# Publicador RabbitMQ
publicador = Publicador(exchange='eCommerce', exchange_type='direct', nome_remetente='principal')

# Catálogo fixo em memória conforme solicitado para a primeira etapa
CATALOGO_INICIAL = [
    # (codigo, nome, preco, quantidade, categoria, imagem)
    ("1", "Vestido Floral", 120.00, 10, "Feminino", "https://exemplo.com/imagens/vestido-floral.jpg"),
    ("2", "Blusa de Seda", 89.90, 10, "Feminino", "https://exemplo.com/imagens/blusa-seda.jpg"),
    ("3", "Calça Jeans Skinny", 150.00, 10, "Feminino", "https://exemplo.com/imagens/calca-jeans-skinny.jpg"),
    ("4", "Saia Midi", 95.00, 10, "Feminino", "https://exemplo.com/imagens/saia-midi.jpg"),
    ("5", "Casaco de Lã", 250.00, 10, "Feminino", "https://exemplo.com/imagens/casaco-la.jpg"),
    ("6", "T-shirt Básica Feminina", 45.00, 10, "Feminino", "https://exemplo.com/imagens/t-shirt-basica.jpg"),
    ("7", "Macacão Pantalona", 180.00, 10, "Feminino", "https://exemplo.com/imagens/macacao-pantalona.jpg"),
    ("8", "Camiseta de Algodão", 50.00, 10, "Masculino", "https://exemplo.com/imagens/camiseta-algodao.jpg"),
    ("9", "Calça Sarja", 130.00, 10, "Masculino", "https://exemplo.com/imagens/calca-sarja.jpg"),
    ("10", "Camisa Social Branca", 110.00, 10, "Masculino", "https://exemplo.com/imagens/camisa-social.jpg"),
    ("11", "Jaqueta de Couro", 300.00, 10, "Masculino", "https://exemplo.com/imagens/jaqueta-couro.jpg"),
    ("12", "Bermuda Moletom", 70.00, 10, "Masculino", "https://exemplo.com/imagens/bermuda-moletom.jpg"),
    ("13", "Suéter de Tricô", 140.00, 10, "Masculino", "https://exemplo.com/imagens/sueter-trico.jpg"),
    ("14", "Terno Slim Fit", 450.00, 10, "Masculino", "https://exemplo.com/imagens/terno-slim.jpg"),
    ("15", "Conjunto Moletom Infantil", 85.00, 10, "Infantil", "https://exemplo.com/imagens/conjunto-moletom.jpg"),
    ("16", "Vestido de Festa Infantil", 110.00, 10, "Infantil", "https://exemplo.com/imagens/vestido-festa.jpg"),
    ("17", "Camiseta Estampa Dinossauro", 40.00, 10, "Infantil", "https://exemplo.com/imagens/camiseta-dinossauro.jpg"),
    ("18", "Calça Jeans Kids", 90.00, 10, "Infantil", "https://exemplo.com/imagens/calca-jeans-kids.jpg"),
    ("19", "Pijama Brilha no Escuro", 65.00, 10, "Infantil", "https://exemplo.com/imagens/pijama-brilha.jpg"),
    ("20", "Jaqueta Corta-Vento Infantil", 100.00, 10, "Infantil", "https://exemplo.com/imagens/jaqueta-corta-vento.jpg"),
]

# Dicionário auxiliar derivado para busca rápida de produtos por código
PRODUTOS = {
    item[0]: {
        "nome": item[1],
        "preco": item[2],
        "quantidade": item[3],
        "categoria": item[4],
        "imagem": item[5]
    }
    for item in CATALOGO_INICIAL
}

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

def processar_atualizacao_status(routing_key, body_mensagem):
    """Consome os eventos de atualização dos outros microsserviços e altera o status do pedido em memória."""
    try:
        dados = json.loads(body_mensagem.decode('utf-8'))
        id_pedido = dados.get("id_pedido")

        if not pedidos_db.obter(id_pedido):
            return

        print(f"{TAG} Evento recebido do RabbitMQ: '{routing_key}' para Pedido #{id_pedido}")

        # Mapeamento das routing keys para mensagens amigáveis
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

        # Emite pedido.excluido para o RabbitMQ quando há falha no fluxo
        if routing_key in ['estoque.indisponivel', 'pagamento.recusado']:
            print(f"{TAG} Emitindo 'pedido.excluido' para o Pedido #{id_pedido}...")
            pedidos_db.remover(id_pedido)
            publicador.publicar('pedido.excluido', body_mensagem)

    except Exception as e:
        print(f"{TAG} Erro ao processar evento '{routing_key}': {e}")

def iniciar_escuta():
    """Inscricão do MS Principal nas routing keys dos demais microsserviços."""
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
        nome_consumidor='MS Principal'
    )

# Configuração do Flask
app = Flask(__name__)
CORS(app)  # Permite que o frontend web faça requisições AJAX/Fetch para esta API

@app.route('/produtos', methods=['GET'])
def listar_produtos():
    """Endpoint REST que disponibiliza a lista de produtos formatada em JSON para o frontend."""
    lista_formatada = [
        {
            "codigo": item[0],
            "nome": item[1],
            "preco": item[2],
            "quantidade": item[3],
            "categoria": item[4],
            "imagem": item[5]
        }
        for item in CATALOGO_INICIAL
    ]
    return jsonify(lista_formatada), 200

@app.route('/pedidos', methods=['POST'])
def criar_pedido():
    """Endpoint REST para receber os itens do carrinho e iniciar o processamento do pedido."""
    dados = request.get_json()

    if not dados or 'itens' not in dados or not dados['itens']:
        return jsonify({"erro": "O pedido deve conter uma lista de itens."}), 400

    itens_req = dados['itens']
    produtos_payload = []
    valor_total = 0.0

    # estruturação e validação dos itens do carrinho
    for item in itens_req:
        codigo = str(item.get('id') or item.get('codigo'))
        quantidade = int(item.get('quantity') or item.get('quantidade', 1))
        info_prod = PRODUTOS.get(codigo)
        nome = item.get('name') or item.get('nome') or (info_prod['nome'] if info_prod else 'Produto')
        preco = float(item.get('price') or item.get('preco') or (info_prod['preco'] if info_prod else 0.0))
        categoria = item.get('category') or item.get('categoria') or (info_prod['categoria'] if info_prod else 'Geral')

        valor_total += preco * quantidade

        produtos_payload.append({
            "codigo": codigo,
            "nome": nome,
            "quantidade": quantidade,
            "preco_unitario": preco,
            "categoria": categoria
        })

    # gera um id pro pedido
    id_pedido = str(uuid.uuid4())[:8]

    # salva o pedido localmente no MS_Principal
    pedidos_db.salvar(
        id_pedido,
        {
            "itens": produtos_payload,
            "valor_total": valor_total,
            "status": "Criado",
        }
    )

    # monta o payload para o RabbitMQ
    payload_evento = {
        "id_pedido": id_pedido,
        "produtos": produtos_payload,
        "valor_total": valor_total
    }

    # publica o evento 'pedido.criado' no RabbitMQ para o MS_Estoque
    try:
        publicador.publicar('pedido.criado', json.dumps(payload_evento))
        print(f"{TAG} Pedido #{id_pedido} criado e publicado no RabbitMQ com sucesso!")
    except Exception as e:
        print(f"{TAG} Pedido #{id_pedido} salvo localmente, mas falhou ao publicar no RabbitMQ: {e}")

    # retorna o ID do pedido gerado para o front-end acompanhar via SSE
    return jsonify({
        "id_pedido": id_pedido,
        "status": "Criado",
        "valor_total": valor_total,
        "mensagem": "Pedido recebido com sucesso!"
    }), 201

def main():
    #inicia o consumidor do RabbitMQ em uma thread em segundo plano
    thread_consumidor = threading.Thread(target=iniciar_escuta, daemon=True)
    thread_consumidor.start()
    print(f"{TAG} Thread de escuta do RabbitMQ iniciada em segundo plano.")

    # inicia o servidor da API REST com Flask na thread principal
    print(f"{TAG} Rodando API Gateway HTTP na porta 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    main()