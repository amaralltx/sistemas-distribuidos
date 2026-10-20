# ms_estoque/db.py
import json
import os
import threading

ARQUIVO_DB = "estoque.json"

# Flask e RabbitMQ rodam em threads diferentes e mexem no msm arquivo
# Lock garante que só uma thread por vez leia/altere/grave.
_lock = threading.Lock()

CATALOGO_INICIAL = [
    # (id, nome, preco, quantidade, categoria, imagem)
    ("1", "Vestido Floral", 120.00, 10, "Feminino", "https://plus.unsplash.com/premium_photo-1723535671118-ae4028123e40?q=80&w=387&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"),
    ("2", "Blusa de Seda", 89.90, 10, "Feminino", "https://plus.unsplash.com/premium_photo-1673384389447-5a4364e7c93b?q=80&w=388&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"),
    ("3", "Calça Jeans Skinny", 150.00, 10, "Feminino", "https://images.unsplash.com/photo-1714143136372-ddaf8b606da7?q=80&w=580&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"),
    ("4", "Saia Midi", 95.00, 10, "Feminino", "https://plus.unsplash.com/premium_photo-1674129670339-554be9059cf4?q=80&w=674&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"),
    ("5", "Casaco de Lã", 250.00, 10, "Feminino", "https://plus.unsplash.com/premium_photo-1671460923085-f7ec58f56b28?q=80&w=387&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"),
    ("6", "T-shirt Básica Feminina", 45.00, 10, "Feminino", "https://plus.unsplash.com/premium_photo-1755034663782-3902ccfae2d4?q=80&w=387&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"),
    ("7", "Macacão Pantalona", 180.00, 10, "Feminino", "https://images.unsplash.com/photo-1591954289868-8f356bf1d102?q=80&w=465&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"),
    ("8", "Camiseta de Algodão", 50.00, 10, "Masculino", "https://plus.unsplash.com/premium_photo-1718913936342-eaafff98834b?q=80&w=872&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"),
    ("9", "Calça Sarja", 130.00, 10, "Masculino", "https://plus.unsplash.com/premium_photo-1690366911138-bd50985e0379?q=80&w=870&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"),
    ("10", "Camisa Social Branca", 110.00, 10, "Masculino", "https://images.unsplash.com/photo-1611619668823-13e82692eddc?q=80&w=387&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"),
    ("11", "Jaqueta de Couro", 300.00, 10, "Masculino", "https://plus.unsplash.com/premium_photo-1661313817350-1fa759c43a3b?q=80&w=917&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"),
    ("12", "Bermuda Moletom", 70.00, 10, "Masculino", "https://plus.unsplash.com/premium_photo-1715724793563-ba82fad6cf5d?q=80&w=387&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"),
    ("13", "Suéter de Tricô", 140.00, 10, "Masculino", "https://plus.unsplash.com/premium_photo-1695339146296-ab03c0e6ae50?q=80&w=387&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"),
    ("14", "Terno Slim Fit", 450.00, 10, "Masculino", "https://images.unsplash.com/photo-1507679799987-c73779587ccf?q=80&w=871&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"),
    ("15", "Conjunto Moletom Infantil", 85.00, 10, "Infantil", "https://images.unsplash.com/photo-1749560515162-977fe54dbf92?q=80&w=387&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"),
    ("16", "Vestido de Festa Infantil", 110.00, 10, "Infantil", "https://images.unsplash.com/photo-1620774760711-caa4c94d683a?q=80&w=870&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"),
    ("17", "Camiseta Estampa Dinossauro", 40.00, 10, "Infantil", "https://images.unsplash.com/photo-1633051246794-95b672a76da4?q=80&w=415&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"),
    ("18", "Calça Jeans Kids", 90.00, 10, "Infantil", "https://images.unsplash.com/photo-1789110854969-94d36ba7636e?q=80&w=387&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"),
    ("19", "Pijama Brilha no Escuro", 65.00, 10, "Infantil", "https://plus.unsplash.com/premium_photo-1682001267817-8a8adc7b1d21?q=80&w=847&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"),
    ("20", "Jaqueta Corta-Vento Infantil", 100.00, 10, "Infantil", "https://plus.unsplash.com/premium_photo-1697612943446-ef0d34fd8a3a?q=80&w=387&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"),
]


def _carregar():
    with open(ARQUIVO_DB, encoding="utf-8") as f:
        return json.load(f)


def _salvar(dados):
    # grava num arquivo temporário e depois troca pelo definitivo
    # se o processo cair no meio da gravação, o estoque.json não fica corrompido.
    tmp = ARQUIVO_DB + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    os.replace(tmp, ARQUIVO_DB)


def inicializar():
    """Cria o estoque.json com o catálogo inicial, se ele ainda não existir."""
    with _lock:
        if os.path.exists(ARQUIVO_DB):
            return
        _salvar({
            "produtos": {
                c: {"id": c, "nome": n, "preco": p, "quantidade": qtd, "categoria": cat, "imagem": img}
                for c, n, p, qtd, cat, img in CATALOGO_INICIAL
            },
            # o que foi reservado por pedido: {id_pedido: {id: quantidade}}
            "reservas": {},
        })


def listar_disponiveis():
    """Produtos com quantidade > 0, como lista de dicts (pronto para virar JSON)."""
    with _lock:
        produtos = _carregar()["produtos"].values()
    return [p for p in sorted(produtos, key=lambda p: int(p["id"])) if p["quantidade"] > 0]


def reservar(id_pedido, itens):
    """Tenta reservar todos os itens do pedido, de forma atômica.
    itens: lista de {"id": ..., "quantidade": ...}.
    Retorna True se reservou tudo; False (sem alterar nada) se algum item não tem estoque."""
    with _lock:
        dados = _carregar()
        produtos = dados["produtos"]

        # primeiro confere, só depois baixa
        for item in itens:
            produto = produtos.get(item["id"])
            if produto is None or produto["quantidade"] < item["quantidade"]:
                return False  # nada foi alterado nem gravado

        reserva = dados["reservas"].setdefault(id_pedido, {})
        for item in itens:
            produtos[item["id"]]["quantidade"] -= item["quantidade"]
            reserva[item["id"]] = reserva.get(item["id"], 0) + item["quantidade"]

        _salvar(dados)  # uma única gravação para a reserva inteira
        return True


def devolver(id_pedido):
    """Devolve ao estoque o que foi reservado para o pedido (se houver reserva).
    Retorna a lista de itens devolvidos (vazia se o pedido nunca reservou nada)."""
    with _lock:
        dados = _carregar()
        reserva = dados["reservas"].pop(id_pedido, None)
        if not reserva:
            return []
        for id, qtd in reserva.items():
            dados["produtos"][id]["quantidade"] += qtd
        _salvar(dados)
        return [{"id": c, "quantidade": q} for c, q in reserva.items()]