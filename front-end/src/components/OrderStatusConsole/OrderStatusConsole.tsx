import React, { useEffect, useState, useRef } from 'react';
import './style.css';

interface TrackingEvent {
  id: string;
  timestamp: string;
  message: string;
  type: 'info' | 'system' | 'success';
}

interface OrderTrackingProps {
  orderId: string | number;
}

export const OrderTracking: React.FC<OrderTrackingProps> = ({ orderId }) => {
  const [events, setEvents] = useState<TrackingEvent[]>([]);
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // mantem o scroll no final do componente para ver as msgs mais atuais
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight;
    }
  }, [events]);

  useEffect(() => {

    const eventSource = new EventSource(`http://localhost:8080/api/orders/${orderId}/stream`);

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      setEvents((prev) => [
        ...prev,
        {
          id: data.id || crypto.randomUUID(),
          timestamp: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }),
          message: data.message,
          type: data.type || 'info', // O backend pode informar se é 'info' ou 'success'
        }
      ]);
    };

    eventSource.onerror = () => {
      setEvents((prev) => [...prev, { id: 'err', timestamp: 'Agora', message: 'Conexão de atualização perdida. Reconectando...', type: 'system' }]);
    };

    return () => eventSource.close();
    setEvents([
      { 
        id: '1', 
        timestamp: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }), 
        message: `Iniciando rastreamento do pedido.`, 
        type: 'system' 
      }
    ]);

    const fakeEvents = [
      { message: "Aguardando confirmação de pagamento da operadora de cartão.", type: "info" },
      { message: "Pagamento aprovado. O pedido foi encaminhado para separação no estoque.", type: "info" },
      { message: "Nota fiscal emitida com sucesso (NF-e 192837).", type: "info" },
      { message: "O pedido foi coletado pela transportadora.", type: "info" },
      { message: "Pedido entregue ao destinatário.", type: "success" },
    ] as const;

    let currentIndex = 0;
    const interval = setInterval(() => {
      if (currentIndex < fakeEvents.length) {
        setEvents((prev) => [
          ...prev,
          {
            id: crypto.randomUUID(),
            timestamp: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }),
            message: fakeEvents[currentIndex].message,
            type: fakeEvents[currentIndex].type,
          },
        ]);
        currentIndex++;
      } else {
        clearInterval(interval);
      }
    }, 4000); // 1 mensagem nova a cada 4 segundos

    return () => clearInterval(interval);
  }, [orderId]);

  return (
    <div className="order-tracking-container">
      <div className="order-tracking-header">
        <h2 className="order-tracking-title">Acompanhar Pedido</h2>
        <span className="order-tracking-id">Pedido #{orderId}</span>
      </div>

      <div className="order-tracking-list" ref={listRef}>
        {events.map((event) => (
          <div key={event.id} className={`tracking-item type-${event.type}`}>
            <div className="tracking-time">{event.timestamp}</div>
            <p className="tracking-message">{event.message}</p>
          </div>
        ))}
        {events.length === 0 && (
          <p style={{ textAlign: 'center', color: '#9ca3af' }}>Nenhuma atualização ainda...</p>
        )}
      </div>
    </div>
  );
};