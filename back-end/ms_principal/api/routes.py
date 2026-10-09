# api/routes.py
import json
import uuid
import time
from flask import Blueprint, jsonify, request, Response
from config import TAG
from domain.catalog import CATALOGO_INICIAL, PRODUTOS
from domain.repository import pedidos_db
from messaging.publisher import publicador

api_bp = Blueprint('api', __name__)

@api_bp.route('/produtos', methods=['GET'])
def listar_produtos():
    """Endpoint REST que disponibiliza a lista de produtos do catálogo."""
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

@api_bp.route('/pedidos', methods=['POST'])
def criar_pedido():
    """Endpoint REST para receber os itens do carrinho e registrar o pedido."""
    dados = request.get_json()

    if not dados or 'itens' not in dados or not dados['itens']:
        return jsonify({"erro": "O pedido deve conter uma lista de itens."}), 400

    itens_req = dados['itens']
    produtos_payload = []
    valor_total = 0.0

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

    # Gera identificador único para o pedido
    id_pedido = str(uuid.uuid4())[:8]

    # Salva no repositório thread-safe em memória
    pedidos_db.salvar(
        id_pedido,
        {
            "itens": produtos_payload,
            "valor_total": valor_total,
            "status": "Criado",
        }
    )

    # Monta payload para o evento 'pedido.criado'
    payload_evento = {
        "id_pedido": id_pedido,
        "produtos": produtos_payload,
        "valor_total": valor_total
    }

    try:
        publicador.publicar('pedido.criado', json.dumps(payload_evento))
        print(f"{TAG} Pedido #{id_pedido} criado e publicado no RabbitMQ com sucesso!")
    except Exception as e:
        print(f"{TAG} Pedido #{id_pedido} salvo localmente, mas falhou ao publicar no RabbitMQ: {e}")

    return jsonify({
        "id_pedido": id_pedido,
        "status": "Criado",
        "valor_total": valor_total,
        "mensagem": "Pedido recebido com sucesso!"
    }), 201

@api_bp.route('/pedidos/<id_pedido>/sse', methods=['GET'])
def sse_pedido(id_pedido):
    """Stream SSE que monitora alterações de status do pedido através de polling em memória."""
    def stream():
        status_anterior = None
        
        while True:
            pedido = pedidos_db.obter(id_pedido)
            
            if pedido:
                status_atual = pedido.get("status")
                
                # Transmite os dados ao cliente apenas se houver mudança de status
                if status_atual != status_anterior:
                    status_anterior = status_atual
                    payload = json.dumps({
                        "id_pedido": id_pedido,
                        "status": status_atual
                    })
                    yield f"data: {payload}\n\n"
                    
                    # Interrompe o loop do gerador ao atingir um estado conclusivo
                    if status_atual in [
                        "Pedido Enviado.",
                        "Estoque Indisponível. Pedido Cancelado.",
                        "Pagamento Recusado. Pedido Cancelado."
                    ]:
                        break

            # Intervalo de verificação de 1 segundo
            time.sleep(1)

    return Response(
        stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Access-Control-Allow-Origin': '*'
        }
    )