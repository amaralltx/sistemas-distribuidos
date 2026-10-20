# api/routes.py
import json
import uuid
import time
import requests
from flask import Blueprint, jsonify, request, Response
from config import TAG
from domain.repository import pedidos_db
from messaging.publisher import publicador

api_bp = Blueprint('api', __name__)

URL_MS_ESTOQUE = "http://localhost:5001"

@api_bp.route('/produtos', methods=['GET'])
def listar_produtos():
    """Endpoint REST que atua como API Gateway, buscando o catálogo do MS Estoque."""
    try:
        # Faz a requisição HTTP GET para a API do Estoque
        resposta = requests.get(f"{URL_MS_ESTOQUE}/produtos", timeout=5)
        resposta.raise_for_status() # Lança erro se o status não for 200 OK
        
        produtos = resposta.json()
        return jsonify(produtos), 200
        
    except requests.exceptions.RequestException as e:
        print(f"{TAG} Erro ao buscar produtos no MS Estoque: {e}")
        return jsonify({"erro": "Não foi possível carregar o catálogo de produtos no momento."}), 503

@api_bp.route('/pedidos', methods=['POST'])
def criar_pedido():
    """Endpoint REST para receber os itens do carrinho e registrar o pedido."""
    dados = request.get_json()

    if not dados or 'itens' not in dados or not dados['itens']:
        return jsonify({"erro": "O pedido deve conter uma lista de itens."}), 400

    itens_req = dados['itens']
    
    # 1. Consulta o MS_Estoque para validar os preços e nomes reais dos produtos
    try:
        resposta = requests.get(f"{URL_MS_ESTOQUE}/produtos", timeout=5)
        resposta.raise_for_status()
        # Cria um dicionário de acesso rápido indexado pelo código do produto
        catalogo_atual = {str(p["id"]): p for p in resposta.json()}
    except requests.exceptions.RequestException as e:
        print(f"{TAG} Erro ao validar produtos no MS Estoque: {e}")
        return jsonify({"erro": "Serviço de estoque indisponível para validação do pedido."}), 503

    produtos_payload = []
    valor_total = 0.0

    # 2. Monta o payload garantindo a integridade dos dados (preço real vs preço enviado)
    for item in itens_req:
        id = str(item.get('id') or item.get('id'))
        quantidade = int(item.get('quantidade') or item.get('quantity', 1))
        
        info_prod = catalogo_atual.get(id)
        
        # Se o produto existe no banco do estoque, usa os dados oficiais
        nome = info_prod['nome'] if info_prod else item.get('nome', 'Produto Desconhecido')
        preco = float(info_prod['preco']) if info_prod else float(item.get('preco') or 0.0)
        categoria = info_prod['categoria'] if info_prod else item.get('categoria', 'Geral')

        valor_total += preco * quantidade

        produtos_payload.append({
            "id": id,
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

@api_bp.route('/promocoes/interesse', methods=['POST', 'DELETE'])
def interesse_promocao():
    """POST registra e DELETE cancela o interesse em receber promoções por e-mail."""
    dados = request.get_json(silent=True) or {}
    email = (dados.get('email') or '').strip()

    if '@' not in email:
        return jsonify({"erro": "Informe um e-mail válido."}), 400

    categorias = dados.get('categorias') or ([dados['categoria']] if dados.get('categoria') else [])
    acao = 'registrar' if request.method == 'POST' else 'cancelar'

    try:
        publicador.publicar('interesse.promocao', json.dumps({
            "acao": acao,
            "email": email,
            "categorias": categorias
        }))
        print(f"{TAG} Evento interesse.promocao ({acao}) publicado para {email}.")
    except Exception as e:
        print(f"{TAG} Falha ao publicar interesse.promocao: {e}")
        return jsonify({"erro": "Não foi possível processar a solicitação agora."}), 503

    return jsonify({"mensagem": f"Interesse ({acao}) enviado com sucesso."}), 202