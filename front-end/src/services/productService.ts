import { type CartItem } from "../components/Cart/Cart";
export interface Product {
  id: string;
  nome: string;
  preco: number;
  quantidade: number;
  categoria: string;
  imagem: string;
}

const API_BASE_URL = 'http://localhost:5000';

export async function getProducts(): Promise<Product[]> {
  const response = await fetch(`${API_BASE_URL}/produtos`);

  if (!response.ok) {
    throw new Error(`Erro ao carregar catálogo (${response.status})`);
  }

  return await response.json();
}

export async function createOrder(cartItems: CartItem[]): Promise<{ id_pedido: string; status: string; valor_total: number }> {
  const response = await fetch(`${API_BASE_URL}/pedidos`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ itens: cartItems }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.erro || `Erro ao processar o pedido (${response.status})`);
  }

  return await response.json();
}