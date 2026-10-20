# ms_promocoes/email_resend.py
# Cliente da API externa de e-mail (Resend) — POST https://api.resend.com/emails
import time

import requests

from config import EMAIL_DRY_RUN, EMAIL_FROM, RESEND_API_KEY, TAG

URL_RESEND = "https://api.resend.com/emails"
MAX_TENTATIVAS = 3


def enviar_email(para, assunto, html, texto):
    """Envia um e-mail. Retorna (ok, id_ou_erro). Nunca levanta exceção."""
    if EMAIL_DRY_RUN:
        print(f"{TAG} [DRY-RUN] Para: {para} | Assunto: {assunto}\n{texto}")
        return True, "dry-run"

    payload = {"from": EMAIL_FROM, "to": [para], "subject": assunto, "html": html, "text": texto}
    headers = {"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"}

    erro = ""
    for tentativa in range(1, MAX_TENTATIVAS + 1):
        try:
            r = requests.post(URL_RESEND, json=payload, headers=headers, timeout=10)
        except requests.exceptions.RequestException as e:
            erro = f"falha de rede: {e}"
        else:
            if r.status_code in (200, 201):
                return True, r.json().get("id", "")
            erro = f"HTTP {r.status_code}: {r.text[:200]}"
            # só vale repetir em rate limit (429) e erro do servidor (5xx)
            if r.status_code != 429 and r.status_code < 500:
                break
            if r.status_code == 429:
                time.sleep(float(r.headers.get("retry-after", 2 ** tentativa)))
                continue
        time.sleep(2 ** tentativa)

    return False, erro
