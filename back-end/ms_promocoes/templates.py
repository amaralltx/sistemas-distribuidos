# ms_promocoes/templates.py
from html import escape

from config import FRONTEND_URL


def _brl(valor):
    return "R$ " + f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _layout(titulo, corpo_html):
    return f"""<!DOCTYPE html>
<html lang="pt-BR"><body style="margin:0;padding:24px;background:#f4f4f5;font-family:Arial,Helvetica,sans-serif;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:520px;margin:0 auto;background:#ffffff;border-radius:8px;overflow:hidden;">
<tr><td style="background:#111827;color:#ffffff;padding:16px 24px;font-size:18px;font-weight:bold;">{escape(titulo)}</td></tr>
<tr><td style="padding:24px;color:#111827;font-size:15px;line-height:1.5;">{corpo_html}</td></tr>
<tr><td style="padding:16px 24px;background:#f9fafb;color:#6b7280;font-size:12px;">
Você recebe este e-mail porque se inscreveu nas promoções da nossa loja.
Para cancelar, acesse <a href="{escape(FRONTEND_URL)}" style="color:#6b7280;">a loja</a> e remova seu interesse.
</td></tr></table></body></html>"""


def email_promocao(promo):
    nome = escape(promo["produto"])
    imagem = (
        f'<img src="{escape(promo["imagem"])}" alt="{nome}" width="100%" style="border-radius:6px;margin-bottom:16px;">'
        if promo.get("imagem") else ""
    )
    corpo = f"""{imagem}
<p style="margin:0 0 4px;color:#6b7280;">Categoria {escape(promo['categoria'])}</p>
<h2 style="margin:0 0 12px;">{nome}</h2>
<p style="margin:0;"><span style="text-decoration:line-through;color:#6b7280;">{_brl(promo['preco_original'])}</span>
&nbsp;<strong style="font-size:22px;color:#059669;">{_brl(promo['preco_promocional'])}</strong>
&nbsp;<span style="background:#dc2626;color:#fff;padding:2px 8px;border-radius:4px;font-size:13px;">{promo['desconto_percentual']}% OFF</span></p>
<p style="margin:20px 0 0;"><a href="{escape(FRONTEND_URL)}" style="background:#111827;color:#fff;padding:10px 20px;border-radius:6px;text-decoration:none;">Ver na loja</a></p>"""
    assunto = f"{promo['desconto_percentual']}% OFF em {promo['produto']}"
    texto = (
        f"{assunto} (categoria {promo['categoria']})\n"
        f"De {_brl(promo['preco_original'])} por {_brl(promo['preco_promocional'])}.\n"
        f"Confira: {FRONTEND_URL}\n"
    )
    return assunto, _layout("Promoção para você", corpo), texto


def email_confirmacao(categorias_exibicao):
    lista = ", ".join(escape(c) for c in categorias_exibicao)
    corpo = f"<p>Inscrição confirmada! Você vai receber ofertas das categorias: <strong>{lista}</strong>.</p>"
    texto = f"Inscrição confirmada! Você vai receber ofertas das categorias: {', '.join(categorias_exibicao)}.\n"
    return "Inscrição em promoções confirmada", _layout("Inscrição confirmada", corpo), texto
