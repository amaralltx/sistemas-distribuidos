import { API_URL } from "../config/env";
import type { OrderEvent } from "../types";

interface Handlers {
  onEvent: (evento: OrderEvent) => void;
  onError: (mensagem: string) => void;
}

export function abrirAcompanhamento(
  idPedido: string,
  handlers: Handlers,
): () => void {
  const origem = new EventSource(`${API_URL}/pedidos/${idPedido}/sse`);

  origem.onmessage = (mensagem) => {
    let evento: OrderEvent;
    try {
      evento = JSON.parse(mensagem.data) as OrderEvent;
    } catch {
      console.warn("[SSE] Evento com JSON inválido:", mensagem.data);
      return;
    }

    handlers.onEvent(evento);
    if (evento.final) origem.close();
  };

  origem.onerror = () => {
    if (origem.readyState === EventSource.CLOSED) {
      handlers.onError("Não foi possível acompanhar este pedido.");
    }
  };

  return () => origem.close();
}
