import React from 'react';
import './style.css';

interface ProductCardProps {
  id: string | number;
  name: string;
  price: number;
  imageUrl: string;
  onBuy?: (productId: string | number) => void;
}

export const ProductCard: React.FC<ProductCardProps> = ({
  id,
  name,
  price,
  imageUrl,
  onBuy,
}) => {
  const formattedPrice = new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(price);

  const handleBuyClick = () => {
    if (onBuy) {
      onBuy(id);
    } else {
      console.log(`Produto ${id} adicionado ao carrinho!`);
    }
  };

  return (
    <div className="product-card">
      <img
        src={imageUrl}
        alt={`Foto do produto ${name}`}
        className="product-image"
      />

      <div className="product-info">
        <h3 className="product-title" title={name}>
          {name}
        </h3>
        <p className="product-price">
          {formattedPrice}
        </p>

        <button onClick={handleBuyClick} className="buy-button">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="cart-icon"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <circle cx="9" cy="21" r="1" />
            <circle cx="20" cy="21" r="1" />
            <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6" />
          </svg>
          Comprar
        </button>
      </div>
    </div>
  );
};