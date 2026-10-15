# ms_estoque/api.py
# API REST do MS Estoque. Quem consome é o MS Principal (API Gateway).
from flask import Flask, jsonify

import db

app = Flask(__name__)


@app.get("/produtos")
def listar_produtos():
    return jsonify(db.listar_disponiveis())


def iniciar_api(porta=5001):
    # use_reloader=False: o reloader do Flask não funciona fora da thread principal
    app.run(host="0.0.0.0", port=porta, debug=False, use_reloader=False)