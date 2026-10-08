from Crypto.PublicKey import RSA
import os

print("Gerando chaves RSA (2048 bits) para o MS Promoções...")

# 1. Gera o par de chaves
chave = RSA.generate(2048)
chave_privada = chave.export_key().decode('utf-8')
chave_publica = chave.publickey().export_key().decode('utf-8')

# 2. Cria o arquivo da chave pública (.pem)
nome_publica = "chave_publica_ms_promocoes.pem"
with open(nome_publica, "w") as f:
    f.write(chave_publica)
print(f"✅ Chave pública salva em: {nome_publica}")

# 3. Cria o arquivo .env com a chave privada
with open(".env", "w") as f:
    # Escreve a variável de ambiente exata que o assinatura.py procura
    f.write(f'CHAVE_PRIVADA="{chave_privada}"\n')
print("✅ Arquivo '.env' criado com a Chave Privada oculta.")

print("\nTudo pronto! Agora o MS Promoções e os Consumidores já podem rodar.")