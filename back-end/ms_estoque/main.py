import json
import threading
from rabbitmq import Publicador, iniciar_consumidor

TAG = "\033[92m[MS Estoque]\033[0m"

publicador = Publicador(exchange='eCommerce', exchange_type='direct', nome_remetente='estoque')

# Catálogo fixo sincronizado com o MS Principal
CATALOGO_INICIAL = [
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

# dictde estoque indexado pelo código do produto
ESTOQUE = {
    item[0]: {
        "nome": item[1],
        "preco": item[2],
        "quantidade": item[3],
        "categoria": item[4],
        "imagem": item[5]
    }
    for item in CATALOGO_INICIAL
}

# dict para guardar as reservas ativas por id_pedido
RESERVAS = {}
lock_estoque = threading.Lock()

def processar_evento_estoque(routing_key, body_mensagem):
    """Callback de processamento dos eventos 'pedido.criado' e 'pedido.excluido'."""
    try:
        dados = json.loads(body_mensagem.decode('utf-8'))
        id_pedido = dados.get("id_pedido")
        
        print(f"{TAG} Evento recebido: '{routing_key}' | Pedido #{id_pedido}")

        if routing_key == 'pedido.criado':
            produtos_pedido = dados.get("produtos", [])
            
            with lock_estoque:
                estoque_disponivel = True

                # valida se há quantidade suficiente para todos os itens
                for item in produtos_pedido:
                    codigo = str(item["codigo"])
                    qtd_solicitada = int(item["quantidade"])

                    if codigo not in ESTOQUE or ESTOQUE[codigo]["quantidade"] < qtd_solicitada:
                        estoque_disponivel = False
                        break

                # se tudo estiver disponível, realiza a baixa e salva a reserva
                if estoque_disponivel:
                    for item in produtos_pedido:
                        codigo = str(item["codigo"])
                        ESTOQUE[codigo]["quantidade"] -= int(item["quantidade"])

                    # salva cópia dos itens reservados para estorno futuro caso o pedido seja cancelado
                    RESERVAS[id_pedido] = produtos_pedido

                    print(f"{TAG} Estoque reservado com sucesso para o Pedido #{id_pedido}.")
                    publicador.publicar('pedido.estoque_ok', body_mensagem)
                else:
                    print(f"{TAG} Estoque insuficiente para o Pedido #{id_pedido}.")
                    publicador.publicar('estoque.indisponivel', body_mensagem)

        elif routing_key == 'pedido.excluido':
            with lock_estoque:
                # recupera os produtos a estornar (payload direto ou busca nas reservas salvas)
                produtos_estornar = dados.get("produtos") or RESERVAS.pop(id_pedido, [])

                if produtos_estornar:
                    for item in produtos_estornar:
                        codigo = str(item["codigo"])
                        if codigo in ESTOQUE:
                            ESTOQUE[codigo]["quantidade"] += int(item["quantidade"])
                    
                    print(f"{TAG} Itens do Pedido #{id_pedido} estornados ao estoque.")
                else:
                    print(f"{TAG} Nenhuma reserva encontrada para estornar o Pedido #{id_pedido}.")

    except Exception as e:
        print(f"{TAG} Erro ao processar mensagem do evento '{routing_key}': {e}")

if __name__ == '__main__':
    print(f"Iniciando {TAG}...")
    iniciar_consumidor(
        exchange='eCommerce',
        exchange_type='direct',
        nome_fila='fila_estoque',
        routing_keys=['pedido.criado', 'pedido.excluido'],
        callback_negocio=processar_evento_estoque,
        nome_consumidor='MS Estoque'
    )