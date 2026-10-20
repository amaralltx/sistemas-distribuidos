import { useCallback, useEffect, useRef, useState } from "react";
import { abrirAcompanhamento } from "../services/orderStream";
import type { OrderEvent } from "../types";

export interface PedidoAcompanhado {
  id: string;
  eventos: OrderEvent[];
  finalizado: boolean;
  erro: string | null;
}

export function useOrderTracking() {
  const [pedidos, setPedidos] = useState<Record<string, PedidoAcompanhado>>({});
  const fechamentos = useRef(new Map<string, () => void>());

  const track = useCallback((id: string) => {
    if (fechamentos.current.has(id)) return;

    setPedidos((prev) => ({
      ...prev,
      [id]: { id, eventos: [], finalizado: false, erro: null },
    }));

    const fechar = abrirAcompanhamento(id, {
      onEvent: (evento) => {
        setPedidos((prev) => {
          const atual = prev[id];
          if (!atual || atual.eventos.some((item) => item.seq === evento.seq)) {
            return prev;
          }
          return {
            ...prev,
            [id]: {
              ...atual,
              eventos: [...atual.eventos, evento],
              finalizado: evento.final,
            },
          };
        });
        if (evento.final) fechamentos.current.delete(id);
      },
      onError: (mensagem) => {
        fechamentos.current.delete(id);
        setPedidos((prev) =>
          prev[id] ? { ...prev, [id]: { ...prev[id], erro: mensagem } } : prev,
        );
      },
    });

    fechamentos.current.set(id, fechar);
  }, []);

  useEffect(() => {
    const mapa = fechamentos.current;
    return () => {
      mapa.forEach((fechar) => fechar());
      mapa.clear();
    };
  }, []);

  return { pedidos: Object.values(pedidos), track };
}
