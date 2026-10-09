# main.py
import threading
from flask import Flask
from flask_cors import CORS
from config import TAG
from api.routes import api_bp
from messaging.consumer import iniciar_escuta

def main():
    # inicia o consumidor do RabbitMQ em segundo plano
    thread_consumidor = threading.Thread(target=iniciar_escuta, daemon=True)
    thread_consumidor.start()
    print(f"{TAG} Thread de escuta do RabbitMQ iniciada em segundo plano.")

    # inicializa o servidor Flask com CORS e Blueprints
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(api_bp)

    # executa a API REST
    print(f"{TAG} Rodando API Gateway HTTP na porta 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    main()