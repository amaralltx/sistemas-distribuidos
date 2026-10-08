import React from 'react';
import './style.css';

export interface CartItem {
  id: string | number;
  name: string;
  price: number;
  imageUrl: string;
  quantity: number;
}

interface CartProps {
  isOpen: boolean;
  onClose: () => void;
  items: CartItem[];
  onUpdateQuantity: (id: string | number, delta: number) => void;
  onRemoveItem: (id: string | number) => void;
  onCheckout: () => void;
}

export const Cart: React.FC<CartProps> = ({
  isOpen,
  onClose,
  items,
  onUpdateQuantity,
  onRemoveItem,
  onCheckout,
}) => {
  //valor total do pedido
  const totalAmount = items.reduce(
    (acc, item) => acc + item.price * item.quantity,
    0
  );

  const formattedTotal = new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(totalAmount);

  return (
    <>
      <div
        className={`cart-overlay ${isOpen ? 'open' : ''}`}
        onClick={onClose}
      />

      <aside className={`cart-aside ${isOpen ? 'open' : ''}`}>
        <div className="cart-header">
          <h2>Seu Carrinho</h2>
          <button className="close-button" onClick={onClose} aria-label="Fechar">
            &times;
          </button>
        </div>

        <div className="cart-body">
          {items.length === 0 ? (
            <p className="empty-cart">Seu carrinho está vazio.</p>
          ) : (
            items.map((item) => (
              <div key={item.id} className="cart-item">
                <img
                  src={item.imageUrl}
                  alt={item.name}
                  className="cart-item-image"
                />

                <div className="cart-item-info">
                  <h4 className="cart-item-name">{item.name}</h4>
                  <p className="cart-item-price">
                    {new Intl.NumberFormat('pt-BR', {
                      style: 'currency',
                      currency: 'BRL',
                    }).format(item.price)}
                  </p>

                  <div className="quantity-controls">
                    <button
                      className="quantity-btn"
                      onClick={() => onUpdateQuantity(item.id, -1)}
                    >
                      -
                    </button>
                    <span className="quantity-value">{item.quantity}</span>
                    <button
                      className="quantity-btn"
                      onClick={() => onUpdateQuantity(item.id, 1)}
                    >
                      +
                    </button>

                    <button
                      className="remove-btn"
                      onClick={() => onRemoveItem(item.id)}
                    >
                      Remover
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        <div className="cart-footer">
          <div className="total-container">
            <span className="total-label">Total:</span>
            <span className="total-amount">{formattedTotal}</span>
          </div>

          <button
            className="checkout-button"
            disabled={items.length === 0}
            onClick={onCheckout}
          >
            Finalizar Compra
          </button>
        </div>
      </aside>
    </>
  );
};