import os, base64
from dotenv import load_dotenv
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

load_dotenv() 

class AssinaturaDigital:
    def __init__(self, caminho_chave_privada=None):

        chave_privada_str = os.getenv("CHAVE_PRIVADA")

        if chave_privada_str:
                self.chave_privada = RSA.import_key(chave_privada_str)
        else:
            print("Aviso: Chave privada não encontrada no ambiente!")

        # dict com as chaves públicas dos remetentes esperados
        self.chaves_publicas = {}

    def carregar_chave_publica(self, nome_ms, caminho_chave):
        # carrega a chave pública do dir e armazena no dict de chaves públicas
        with open(caminho_chave, 'rb') as f:
            self.chaves_publicas[nome_ms] = RSA.import_key(f.read())

    def assinar_mensagem(self, payload_bytes):
        # cria o hash SHA256 e assina com a chave privada
        hash_obj = SHA256.new(payload_bytes)
        assinatura = pkcs1_15.new(self.chave_privada).sign(hash_obj)
        # base64 para trafegar como texto no header do RabbitMQ
        return base64.b64encode(assinatura).decode('utf-8')


    def validar_assinatura(self, payload_bytes, assinatura_b64, nome_remetente):
        # valida se a assinatura confere com a chave pública do remetente
        if nome_remetente not in self.chaves_publicas:
            print(f"Chave pública do remetente '{nome_remetente}' não encontrada!")
            return False

        try:
            chave_publica = self.chaves_publicas[nome_remetente]
            hash_obj = SHA256.new(payload_bytes)
            assinatura_bytes = base64.b64decode(assinatura_b64)
            
            # verify levanta erro se a assinatura for inválida
            pkcs1_15.new(chave_publica).verify(hash_obj, assinatura_bytes)
            return True
            
        except (ValueError, TypeError):
            return False