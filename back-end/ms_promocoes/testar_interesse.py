# ms_promocoes/testar_interesse.py
#   python testar_interesse.py registrar aluno@email.com Feminino Infantil
#   python testar_interesse.py cancelar  aluno@email.com            (cancela tudo)
import json
import sys

import pika
from dotenv import dotenv_values

from rabbitmq import RABBITMQ_HOST  # noqa: F401 (reaproveita o host configurado)
from assinatura import AssinaturaDigital

if len(sys.argv) < 3:
    sys.exit(__doc__)

acao, email, categorias = sys.argv[1], sys.argv[2], sys.argv[3:]

assinador = AssinaturaDigital.__new__(AssinaturaDigital)
from Crypto.PublicKey import RSA
assinador.chave_privada = RSA.import_key(dotenv_values("../ms_principal/.env")["CHAVE_PRIVADA"])
assinador.chaves_publicas = {}

corpo = json.dumps({"acao": acao, "email": email, "categorias": categorias}).encode()
conexao = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
canal = conexao.channel()
canal.exchange_declare(exchange="eCommerce", exchange_type="direct")
canal.basic_publish(
    exchange="eCommerce", routing_key="interesse.promocao", body=corpo,
    properties=pika.BasicProperties(headers={"Signature": assinador.assinar_mensagem(corpo), "remetente": "principal"}),
)
print("Evento publicado:", corpo.decode())
conexao.close()
