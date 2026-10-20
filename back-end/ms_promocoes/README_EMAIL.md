# MS Promoções + API externa de e-mail (Resend)

## Fluxo
`Frontend` → `POST/DELETE /promocoes/interesse` (Gateway) → evento `interesse.promocao` (exchange `eCommerce`, assinado por `principal`)
→ **MS Promoções** guarda o interesse (`inscricoes.json`) → a cada `PROMO_INTERVALO_SEG` gera uma promoção com produto real do MS Estoque
→ envia 1 e-mail por inscrito via `POST https://api.resend.com/emails`.

## Contrato do evento `interesse.promocao`
```json
{"acao": "registrar", "email": "aluno@email.com", "categorias": ["Feminino", "Infantil"]}
{"acao": "cancelar",  "email": "aluno@email.com", "categorias": ["Infantil"]}   // sem categorias (ou "todas") cancela tudo
```
Categorias válidas: as do catálogo do Estoque (`Feminino`, `Masculino`, `Infantil`) ou `todas`. Acentos/maiúsculas são ignorados.

## Setup
1. `pip install -r requirements.txt`
2. Crie a chave em resend.com/api-keys e **acrescente** ao `.env` existente as linhas de `.env.example` (não apague `CHAVE_PRIVADA`; não rode `gerar.py` de novo, ele recria o `.env`).
3. `python main.py` (sem `RESEND_API_KEY` roda em DRY-RUN: imprime os e-mails no console).
4. Teste sem o Gateway: `python testar_interesse.py registrar aluno@email.com Feminino`

## Resend: limites para a demo
- `onboarding@resend.dev` é remetente de teste. Para enviar a destinatários arbitrários é preciso verificar um domínio (resend.com/domains); sem isso, use seu próprio e-mail ou `delivered@resend.dev`.
- Rate limit padrão baixo (2–5 req/s): o worker envia 1 e-mail por vez com pausa e repete em 429/5xx.

## Trecho para o Gateway (`ms_principal/api/routes.py`), se ainda não existir
```python
@api_bp.route('/promocoes/interesse', methods=['POST', 'DELETE'])
def interesse_promocao():
    dados = request.get_json(silent=True) or {}
    email = (dados.get('email') or '').strip()
    if not email:
        return jsonify({"erro": "Informe o e-mail."}), 400
    categorias = dados.get('categorias') or ([dados['categoria']] if dados.get('categoria') else [])
    acao = 'registrar' if request.method == 'POST' else 'cancelar'
    publicador.publicar('interesse.promocao', json.dumps({"acao": acao, "email": email, "categorias": categorias}))
    return jsonify({"mensagem": f"Interesse ({acao}) enviado."}), 202
```
