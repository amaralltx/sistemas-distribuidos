# ms_promocoes/main.py
# Consome 'interesse.promocao', gera promoções e as envia por e-mail (API Resend).
import json
import queue
import random
import threading
import time

import config
from config import TAG
from email_resend import enviar_email
from gerador import categorias_do_catalogo, gerar_promocao, obter_catalogo
from inscricoes import email_valido, inscricoes_db, normalizar, TODAS
from rabbitmq import iniciar_consumidor
from templates import email_confirmacao, email_promocao

# fila interna de envio: um único worker serializa os envios (respeita o rate limit da Resend)
fila_envio = queue.Queue()


def worker_envio():
    while True:
        para, (assunto, html, texto) = fila_envio.get()
        ok, info = enviar_email(para, assunto, html, texto)
        print(f"{TAG} E-mail para {para}: {'enviado (' + str(info) + ')' if ok else 'FALHOU - ' + info}")
        time.sleep(0 if config.EMAIL_DRY_RUN else config.EMAIL_INTERVALO_SEG)


def processar_interesse(routing_key, body):
    """Evento 'interesse.promocao': {"acao": "registrar"|"cancelar", "email": "...", "categorias": [...]}"""
    try:
        dados = json.loads(body.decode("utf-8"))
    except ValueError:
        print(f"{TAG} Evento com JSON inválido; ignorado.")
        return

    acao = str(dados.get("acao", "registrar")).lower()
    email = str(dados.get("email", "")).strip()
    categorias = dados.get("categorias") or ([dados["categoria"]] if dados.get("categoria") else [])

    if not email_valido(email):
        print(f"{TAG} E-mail inválido '{email}'; evento ignorado.")
        return

    if acao == "cancelar":
        removido = inscricoes_db.cancelar(email, categorias)
        print(f"{TAG} Interesse de {email} cancelado ({'ok' if removido else 'não havia inscrição'}).")
        return

    if acao != "registrar":
        print(f"{TAG} Ação desconhecida '{acao}'; evento ignorado.")
        return

    conhecidas = categorias_do_catalogo(obter_catalogo())
    for c in categorias:
        if normalizar(c) not in conhecidas and normalizar(c) != TODAS:
            print(f"{TAG} Aviso: categoria '{c}' não existe no catálogo ({', '.join(conhecidas.values())}).")

    cats = inscricoes_db.registrar(email, categorias)
    print(f"{TAG} Interesse registrado: {email} -> {sorted(cats)}")

    if config.EMAIL_CONFIRMACAO:
        exibicao = ["Todas"] if TODAS in cats else [conhecidas.get(c, c) for c in sorted(cats)]
        fila_envio.put((email, email_confirmacao(exibicao)))


def disparar_promocao():
    catalogo = obter_catalogo()
    categorias = categorias_do_catalogo(catalogo)
    ativas = inscricoes_db.categorias_com_interessados(categorias.keys())
    if not ativas:
        print(f"{TAG} Nenhum interessado no momento; promoção não gerada.")
        return

    categoria = random.choice(ativas)
    promo = gerar_promocao(categoria, catalogo)
    destinatarios = inscricoes_db.destinatarios(categoria)
    print(f"{TAG} Promoção {promo['id_promocao']}: {promo['desconto_percentual']}% OFF em "
          f"{promo['produto']} ({promo['categoria']}) -> {len(destinatarios)} destinatário(s)")

    mensagem = email_promocao(promo)
    for email in destinatarios:
        fila_envio.put((email, mensagem))


def loop_promocoes():
    while True:
        time.sleep(config.PROMO_INTERVALO_SEG)
        try:
            disparar_promocao()
        except Exception as e:  # o loop nunca deve morrer por causa de uma falha pontual
            print(f"{TAG} Erro ao gerar promoção: {e}")


if __name__ == "__main__":
    print(f"Iniciando {TAG}...")
    modo = "DRY-RUN (e-mails só impressos no console)" if config.EMAIL_DRY_RUN else f"Resend, remetente {config.EMAIL_FROM}"
    print(f"{TAG} Envio de e-mail: {modo}. Promoção a cada {config.PROMO_INTERVALO_SEG:g}s. "
          f"{inscricoes_db.total()} inscrito(s) carregado(s).")

    threading.Thread(target=worker_envio, daemon=True).start()
    threading.Thread(target=loop_promocoes, daemon=True).start()

    iniciar_consumidor(
        exchange=config.EXCHANGE_NAME,
        exchange_type=config.EXCHANGE_TYPE,
        nome_fila=config.QUEUE_NAME,
        routing_keys=config.ROUTING_KEYS,
        callback_negocio=processar_interesse,
    )
