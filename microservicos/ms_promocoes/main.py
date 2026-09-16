import json
import random
import time
import uuid

from publicador import Publicador

# identificador do MS
TAG = "\033[95m[MS Promoções]\033[0m"

# cria um publicador para enviar mensagens para o exchange 'Promoções' do tipo topic
publicador = Publicador(exchange='Promoções', exchange_type='topic', nome_remetente='ms_promocoes')

# categorias de produtos e alguns itens de exemplo para variar as promoções geradas
CATEGORIAS = {
    "A": {
        "nome": "Feminino",
        "produtos": ["Vestido Floral", "Blusa de Seda", "Calça Jeans Skinny", "Casaco de Lã"],
    },
    "B": {
        "nome": "Masculino",
        "produtos": ["Camiseta de Algodão", "Camisa Social Branca", "Jaqueta de Couro", "Terno Slim Fit"],
    },
    "C": {
        "nome": "Infantil",
        "produtos": ["Conjunto Moletom Infantil", "Vestido de Festa Infantil", "Pijama Brilha no Escuro"],
    },
}

DESCONTOS_POSSIVEIS = [10, 15, 20, 25, 30, 40, 50]


def gerar_promocao():
    categoria = random.choice(list(CATEGORIAS.keys()))
    info_categoria = CATEGORIAS[categoria]
    produto = random.choice(info_categoria["produtos"])
    desconto = random.choice(DESCONTOS_POSSIVEIS)

    payload = {
        "id_promocao": str(uuid.uuid4())[:8],
        "categoria": categoria,
        "categoria_nome": info_categoria["nome"],
        "produto": produto,
        "desconto_percentual": desconto,
        "descricao": f"{desconto}% OFF em {produto} (Categoria {categoria} - {info_categoria['nome']})",
    }

    routing_key = f"promocao.categoria.{categoria}"
    return routing_key, payload


def iniciar_geracao_promocoes(intervalo_min=5, intervalo_max=10):
    print(f"{TAG} Gerando promoções aleatórias. Pressione Ctrl+C para encerrar.")
    while True:
        routing_key, payload = gerar_promocao()
        publicador.publicar(routing_key, json.dumps(payload))
        print(f"{TAG} {payload['descricao']}")
        time.sleep(random.uniform(intervalo_min, intervalo_max))


if __name__ == '__main__':
    print(f"Iniciando {TAG}...")
    try:
        iniciar_geracao_promocoes()
    except KeyboardInterrupt:
        print(f"\n{TAG} Encerrando MS Promoções...")