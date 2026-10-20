# ms_promocoes/inscricoes.py
# Repositório thread-safe de interesses (e-mail -> categorias), persistido em JSON.
import json
import os
import re
import threading
import unicodedata

from config import ARQUIVO_INSCRICOES

TODAS = "todas"
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalizar(texto):
    """'Vestuário ' -> 'vestuario' (minúsculo, sem acento, sem espaços nas pontas)."""
    texto = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    return texto.strip().lower()


def email_valido(email):
    return bool(email) and bool(_EMAIL_RE.match(email))


class RepositorioInscricoes:
    def __init__(self, caminho=ARQUIVO_INSCRICOES):
        self._caminho = caminho
        self._lock = threading.Lock()
        self._dados = {}  # email -> set(categorias normalizadas)
        self._carregar()

    def _carregar(self):
        if os.path.exists(self._caminho):
            try:
                with open(self._caminho, encoding="utf-8") as f:
                    self._dados = {e: set(c) for e, c in json.load(f).items()}
            except (ValueError, OSError):
                self._dados = {}

    def _salvar(self):
        tmp = self._caminho + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({e: sorted(c) for e, c in self._dados.items()}, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self._caminho)

    def registrar(self, email, categorias):
        email = email.strip().lower()
        cats = {normalizar(c) for c in categorias if str(c).strip()} or {TODAS}
        with self._lock:
            self._dados.setdefault(email, set()).update(cats)
            self._salvar()
            return set(self._dados[email])

    def cancelar(self, email, categorias):
        """Sem categorias (ou com 'todas') remove o e-mail por completo."""
        email = email.strip().lower()
        cats = {normalizar(c) for c in categorias if str(c).strip()}
        with self._lock:
            if email not in self._dados:
                return False
            if not cats or TODAS in cats:
                del self._dados[email]
            else:
                self._dados[email] -= cats
                if not self._dados[email]:
                    del self._dados[email]
            self._salvar()
            return True

    def destinatarios(self, categoria):
        """E-mails interessados na categoria (ou em 'todas')."""
        cat = normalizar(categoria)
        with self._lock:
            return sorted(e for e, c in self._dados.items() if cat in c or TODAS in c)

    def categorias_com_interessados(self, categorias_candidatas):
        """Subconjunto das categorias candidatas que têm pelo menos um interessado."""
        return [c for c in categorias_candidatas if self.destinatarios(c)]

    def total(self):
        with self._lock:
            return len(self._dados)


inscricoes_db = RepositorioInscricoes()
