# domain/catalog.py

CATALOGO_INICIAL = [
    # (codigo, nome, preco, quantidade, categoria, imagem)
    ("1", "Vestido Floral", 120.00, 10, "Feminino", "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?auto=format&fit=crop&w=600&q=80"),
    ("2", "Blusa de Seda", 89.90, 10, "Feminino", "https://images.unsplash.com/photo-1584030373081-f37b7bb4fa8e?auto=format&fit=crop&w=600&q=80"),
    ("3", "Calça Jeans Skinny", 150.00, 10, "Feminino", "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?auto=format&fit=crop&w=600&q=80"),
    ("4", "Saia Midi", 95.00, 10, "Feminino", "https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa?auto=format&fit=crop&w=600&q=80"),
    ("5", "Casaco de Lã", 250.00, 10, "Feminino", "https://images.unsplash.com/photo-1539533018447-63fcce2678e3?auto=format&fit=crop&w=600&q=80"),
    ("6", "T-shirt Básica Feminina", 45.00, 10, "Feminino", "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=600&q=80"),
    ("7", "Macacão Pantalona", 180.00, 10, "Feminino", "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=600&q=80"),
    ("8", "Camiseta de Algodão", 50.00, 10, "Masculino", "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=600&q=80"),
    ("9", "Calça Sarja", 130.00, 10, "Masculino", "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?auto=format&fit=crop&w=600&q=80"),
    ("10", "Camisa Social Branca", 110.00, 10, "Masculino", "https://images.unsplash.com/photo-1620012253295-c15cc3e65df4?auto=format&fit=crop&w=600&q=80"),
    ("11", "Jaqueta de Couro", 300.00, 10, "Masculino", "https://images.unsplash.com/photo-1551028719-00167b16eac5?auto=format&fit=crop&w=600&q=80"),
    ("12", "Bermuda Moletom", 70.00, 10, "Masculino", "https://images.unsplash.com/photo-1591195853828-11db59a44f6b?auto=format&fit=crop&w=600&q=80"),
    ("13", "Suéter de Tricô", 140.00, 10, "Masculino", "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?auto=format&fit=crop&w=600&q=80"),
    ("14", "Terno Slim Fit", 450.00, 10, "Masculino", "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?auto=format&fit=crop&w=600&q=80"),
    ("15", "Conjunto Moletom Infantil", 85.00, 10, "Infantil", "https://images.unsplash.com/photo-1519238263530-99bdd11df2ea?auto=format&fit=crop&w=600&q=80"),
    ("16", "Vestido de Festa Infantil", 110.00, 10, "Infantil", "https://images.unsplash.com/photo-1622290291468-a28f7a7dc6a8?auto=format&fit=crop&w=600&q=80"),
    ("17", "Camiseta Estampa Dinossauro", 40.00, 10, "Infantil", "https://images.unsplash.com/photo-1503944583220-79d8926ad5e2?auto=format&fit=crop&w=600&q=80"),
    ("18", "Calça Jeans Kids", 90.00, 10, "Infantil", "https://images.unsplash.com/photo-1519457431-44ccd64a579b?auto=format&fit=crop&w=600&q=80"),
    ("19", "Pijama Brilha no Escuro", 65.00, 10, "Infantil", "https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?auto=format&fit=crop&w=600&q=80"),
    ("20", "Jaqueta Corta-Vento Infantil", 100.00, 10, "Infantil", "https://images.unsplash.com/photo-1543852786-1cf6624b9987?auto=format&fit=crop&w=600&q=80"),
]

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