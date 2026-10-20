import React, { useState } from 'react';
import { registrarInteresse, cancelarInteresse } from '../../services/productService';
import './style.css';

export const Newsletter: React.FC = () => {
  const [email, setEmail] = useState('');
  const [category, setCategory] = useState('todas');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'ok' | 'error'; text: string } | null>(null);

  const send = async (action: 'register' | 'cancel') => {
    setLoading(true);
    setMessage(null);
    try {
      if (action === 'register') {
        await registrarInteresse(email, [category]);
        setMessage({ type: 'ok', text: 'Inscrição solicitada! Você receberá um e-mail de confirmação em instantes.' });
      } else {
        await cancelarInteresse(email, [category]);
        setMessage({ type: 'ok', text: 'Cancelamento solicitado. Você não receberá mais essas promoções.' });
      }
      setEmail('');
    } catch (err) {
      setMessage({ type: 'error', text: err instanceof Error ? err.message : 'Erro inesperado.' });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    send('register');
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
            <option value="Feminino">Moda Feminina</option>
            <option value="Masculino">Moda Masculina</option>
            <option value="Infantil">Moda Infantil</option>
          </select>

          <button type="submit" className="newsletter-button" disabled={loading}>
            {loading ? 'Enviando...' : 'Inscrever-se'}
          </button>
          <button
            type="button"
            className="newsletter-button"
            disabled={loading || !email}
            onClick={() => send('cancel')}
          >
            Cancelar inscrição
          </button>
        </form>

        {message && (
          <p style={{ marginTop: '12px', color: message.type === 'ok' ? '#059669' : '#dc2626' }}>
            {message.text}
          </p>
        )}
      </div>
    </section>
  );
};