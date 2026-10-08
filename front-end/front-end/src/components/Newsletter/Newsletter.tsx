import React, { useState } from 'react';
import './style.css';

interface NewsletterProps {
  onSubscribe?: (data: { email: string; category: string }) => void;
}

export const Newsletter: React.FC<NewsletterProps> = ({ onSubscribe }) => {
  const [email, setEmail] = useState('');
  const [category, setCategory] = useState('todas');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (onSubscribe) {
      onSubscribe({ email, category });
    } else {
      console.log('Inscrição efetuada:', { email, category });
      alert(`Obrigado por se inscrever! Categoria escolhida: ${category}`);
    }

    setEmail('');
  };

  return (
    <section className="newsletter-container">
      <div className="newsletter-content">
        <h2 className="newsletter-title">Newsletter</h2>
        <p className="newsletter-description">
          Receba ofertas exclusivas e lançamentos diretamente no seu e-mail!
        </p>

        <form onSubmit={handleSubmit} className="newsletter-form">
          <input
            type="email"
            placeholder="Digite seu melhor e-mail"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="newsletter-input"
            required
          />

          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="newsletter-select"
          >
            <option value="todas">Todas as categorias</option>
            <option value="eletronicos">Eletrônicos</option>
            <option value="vestuario">Vestuário e Acessórios</option>
            <option value="esportes">Esportes e Lazer</option>
          </select>

          <button type="submit" className="newsletter-button">
            Inscrever-se
          </button>
        </form>
      </div>
    </section>
  );
};