from flask import Flask, jsonify, request

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

app = Flask(__name__)

@app.route('/produtos', methods=['GET'])
def get_items():
    return jsonify(PRODUTOS), 200

if __name__ == '__main__':
    app.run(debug=True)


