# ms_promocoes/gerador.py
# Gera promoções a partir do catálogo real do MS Estoque (GET /produtos).
import random
import uuid

import requests

from config import ESTOQUE_URL, TAG
from inscricoes import normalizar

DESCONTOS_POSSIVEIS = [10, 15, 20, 25, 30, 40, 50]

# usado só se o MS Estoque estiver fora do ar
CATALOGO_FALLBACK = [
    {"id": "f1", "nome": "Vestido Floral", "preco": 120.0, "categoria": "Feminino", "imagem": ""},
    {"id": "f2", "nome": "Blusa de Seda", "preco": 89.9, "categoria": "Feminino", "imagem": ""},
    {"id": "f3", "nome": "Camisa Social Branca", "preco": 139.9, "categoria": "Masculino", "imagem": ""},
    {"id": "f4", "nome": "Jaqueta de Couro", "preco": 299.9, "categoria": "Masculino", "imagem": ""},
    {"id": "f5", "nome": "Pijama Brilha no Escuro", "preco": 59.9, "categoria": "Infantil", "imagem": ""},
]


def obter_catalogo():
    try:
        r = requests.get(f"{ESTOQUE_URL}/produtos", timeout=3)
        r.raise_for_status()
        produtos = r.json()
        if produtos:
            return produtos
    except requests.exceptions.RequestException as e:
        print(f"{TAG} MS Estoque indisponível ({e}); usando catálogo reserva.")
    return CATALOGO_FALLBACK


def categorias_do_catalogo(catalogo):
    """{'feminino': 'Feminino', ...} (chave normalizada -> nome de exibição)."""
    return {normalizar(p["categoria"]): p["categoria"] for p in catalogo}


def gerar_promocao(categoria_norm, catalogo):
    candidatos = [p for p in catalogo if normalizar(p["categoria"]) == categoria_norm]
    if not candidatos:
        return None
    produto = random.choice(candidatos)
    desconto = random.choice(DESCONTOS_POSSIVEIS)
    preco = float(produto["preco"])
    return {
        "id_promocao": str(uuid.uuid4())[:8],
        "categoria": produto["categoria"],
        "produto": produto["nome"],
        "imagem": produto.get("imagem", ""),
        "preco_original": preco,
        "desconto_percentual": desconto,
        "preco_promocional": round(preco * (1 - desconto / 100), 2),
    }
