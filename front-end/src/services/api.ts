import { API_URL } from "../config/env";
import type { CartItem, OrderCreated, Product } from "../types";

export class ErroApi extends Error {
  readonly status: number;

  constructor(mensagem: string, status: number) {
    super(mensagem);
    this.name = "ErroApi";
    this.status = status;
  }
}

async function requisicao<T>(
  caminho: string,
  init: RequestInit = {},
): Promise<T> {
  let resposta: Response;
  try {
    resposta = await fetch(`${API_URL}${caminho}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...init.headers },
    });
  } catch (err) {
    if (init.signal?.aborted) throw err;
    throw new ErroApi("Não foi possível conectar ao servidor.", 0);
  }

  const corpo = await resposta.json().catch(() => ({}));

  if (!resposta.ok) {
    throw new ErroApi(
      corpo.erro ?? `Erro ao processar a requisição (${resposta.status}).`,
      resposta.status,
    );
  }
  return corpo as T;
}

export interface MensagemResposta {
  mensagem: string;
}

export function listarProdutos(signal?: AbortSignal): Promise<Product[]> {
  return requisicao<Product[]>("/produtos", { signal });
}

export function criarPedido(itens: CartItem[]): Promise<OrderCreated> {
  return requisicao<OrderCreated>("/pedidos", {
    method: "POST",
    body: JSON.stringify({
      itens: itens.map((item) => ({ id: item.id, quantidade: item.quantity })),
    }),
  });
}

export function registrarInteresse(
  email: string,
  categorias: string[],
): Promise<MensagemResposta> {
  return requisicao<MensagemResposta>("/promocoes/interesse", {
    method: "POST",
    body: JSON.stringify({ email, categorias }),
  });
}

export function cancelarInteresse(
  email: string,
  categorias: string[],
): Promise<MensagemResposta> {
  return requisicao<MensagemResposta>("/promocoes/interesse", {
    method: "DELETE",
    body: JSON.stringify({ email, categorias }),
  });
}
