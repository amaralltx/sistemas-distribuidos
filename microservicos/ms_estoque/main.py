import json
from rabbitmq import Publicador, iniciar_consumidor

TAG = "\033[92m[MS Estoque]\033[0m"

publicador = Publicador(exchange='eCommerce', exchange_type='direct', nome_remetente='estoque')

# dict dos produtos e suas quantidades em estoque
ESTOQUE = {
    # Feminino
    "1": {"nome": "Vestido Floral", "quantidade": 10},
    "2": {"nome": "Blusa de Seda", "quantidade": 10},
    "3": {"nome": "Calça Jeans Skinny", "quantidade": 10},
    "4": {"nome": "Saia Midi", "quantidade": 10},
    "5": {"nome": "Casaco de Lã", "quantidade": 10},
    "6": {"nome": "T-shirt Básica Feminina", "quantidade": 10},
    "7": {"nome": "Macacão Pantalona", "quantidade": 10},
    # Masculino
    "8": {"nome": "Camiseta de Algodão", "quantidade": 10},
    "9": {"nome": "Calça Sarja", "quantidade": 10},
    "10": {"nome": "Camisa Social Branca", "quantidade": 10},
    "11": {"nome": "Jaqueta de Couro", "quantidade": 10},
    "12": {"nome": "Bermuda Moletom", "quantidade": 10},
    "13": {"nome": "Suéter de Tricô", "quantidade": 10},
    "14": {"nome": "Terno Slim Fit", "quantidade": 10},
    # Infantil
    "15": {"nome": "Conjunto Moletom Infantil", "quantidade": 10},
    "16": {"nome": "Vestido de Festa Infantil", "quantidade": 10},
    "17": {"nome": "Camiseta Estampa Dinossauro", "quantidade": 10},
    "18": {"nome": "Calça Jeans Kids", "quantidade": 10},
    "19": {"nome": "Pijama Brilha no Escuro", "quantidade": 10},
    "20": {"nome": "Jaqueta Corta-Vento Infantil", "quantidade": 10}
}

def processar_evento_estoque(routing_key, body_mensagem):
    print(f"{TAG} Evento recebido: {routing_key}")
    
    # decodifica a mensagem que veio do RabbitMQ
    dados = json.loads(body_mensagem.decode('utf-8'))
    id_pedido = dados.get("id_pedido")
    if routing_key == 'pedido.criado':
        produtos_pedido = dados.get("produtos", [])
        
        estoque_disponivel = True

        # verifica se todos os produtos possuem estoque
        for item in produtos_pedido:
            codigo = item["codigo"]
            qtd_solicitada = item["quantidade"]
            
            # se não existe ou não tem quantidade
            if codigo not in ESTOQUE or ESTOQUE[codigo]["quantidade"] < qtd_solicitada:
                estoque_disponivel = False
                break

        # publica o evento com base na disponibilidade
        if estoque_disponivel:
            # Dá baixa no estoque
            for item in produtos_pedido:
                codigo = item["codigo"]
                ESTOQUE[codigo]["quantidade"] -= item["quantidade"]
                
            print(f"{TAG} Estoque reservado para o Pedido #{id_pedido}.")
            publicador.publicar('pedido.estoque_ok', body_mensagem)
        else:
            print(f"{TAG} Item esgotado ou insuficiente para o Pedido #{id_pedido}.")
            publicador.publicar('estoque.indisponivel', body_mensagem)

    elif routing_key == 'pedido.excluido':
        print(f"{TAG} Recebendo evento 'pedido.excluido' para o Pedido #{id_pedido}.")
        # devolve os itens do pedido ao estoque
        produtos_pedido = dados.get("produtos", [])
        if produtos_pedido:
            for item in produtos_pedido:
                codigo = item["codigo"]
                if codigo in ESTOQUE:
                    ESTOQUE[codigo]["quantidade"] += item["quantidade"]
            print(f"{TAG} Itens do Pedido #{id_pedido} devolvidos ao estoque.")

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