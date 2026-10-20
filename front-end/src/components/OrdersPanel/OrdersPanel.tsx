import type { PedidoAcompanhado } from "../../hooks/useOrderTracking";

interface OrdersPanelProps {
  pedidos: PedidoAcompanhado[];
}

export function OrdersPanel({ pedidos }: OrdersPanelProps) {
  if (pedidos.length === 0) return null;

  return (
    <section className="orders-panel">
      <h2>Meus pedidos</h2>
      {pedidos.map((pedido) => (
        <article key={pedido.id} className="order-card">
          <header>
            <strong>Pedido #{pedido.id}</strong>
            {pedido.finalizado && <span className="order-badge">Concluído</span>}
          </header>

          {pedido.erro && <p className="order-error">{pedido.erro}</p>}

          <ol className="order-timeline">
            {pedido.eventos.map((evento) => (
              <li key={evento.seq} className={evento.final ? "final" : undefined}>
                {evento.status}
              </li>
            ))}
            {!pedido.finalizado && !pedido.erro && (
              <li className="pending">Aguardando atualizações...</li>
            )}
          </ol>
        </article>
      ))}
    </section>
  );
}
