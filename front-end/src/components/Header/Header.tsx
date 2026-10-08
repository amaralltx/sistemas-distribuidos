 import React from 'react';
import './style.css';

interface HeaderProps {
  storeName?: string;
  cartCount?: number;
  onOpenCart?: () => void;
  onNavigateCategories?: () => void;
  onNavigateOrders?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  storeName = 'Minha Loja',
  cartCount = 0,
  onOpenCart,
  onNavigateCategories,
  onNavigateOrders,
}) => {
  const handleCartClick = () => {
    if (onOpenCart) {
      onOpenCart();
    } else {
      console.log('Abrir carrinho (implementar futuramente)');
    }
  };

  return (
    <header className="header-container">
      <div className="header-wrapper">
              <div className="header-left">
        <a href="#" className="brand-name">
          {storeName}
        </a>

        <nav className="header-nav">
          <a
            href="#categorias"
            className="nav-link"
            onClick={(e) => {
              if (onNavigateCategories) {
                e.preventDefault();
                onNavigateCategories();
              }
            }}
          >
            Categorias
          </a>

          <a
            href="#pedidos"
            className="nav-link"
            onClick={(e) => {
              if (onNavigateOrders) {
                e.preventDefault();
                onNavigateOrders();
              }
            }}
          >
            Pedidos
          </a>
        </nav>
      </div>

      <div className="header-actions">
        <button
          onClick={handleCartClick}
          className="header-cart-button"
          aria-label="Abrir carrinho de compras"
        >
          {/* Ícone de Carrinho (SVG inline) */}
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="header-cart-icon"
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

          {/* Badge de quantidade de itens (exibe apenas se houver itens no carrinho) */}
          {cartCount > 0 && <span className="cart-badge">{cartCount}</span>}
        </button>
      </div>
      </div>  
    </header>
  );
};