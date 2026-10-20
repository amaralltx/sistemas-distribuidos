import { type CartItem } from "../components/Cart/Cart";
export interface Product {
  id: string;
  nome: string;
  preco: number;
  quantidade: number;
  categoria: string;
  imagem: string;
}

const MS_PRINCIPAL_URL = 'http://localhost:5000';

export async function getProducts(): Promise<Product[]> {
  const response = await fetch(`${MS_PRINCIPAL_URL}/produtos`);

  if (!response.ok) {
    throw new Error(`Erro ao carregar catálogo (${response.status})`);
  }

  return await response.json();
}

export async function createOrder(cartItems: CartItem[]): Promise<{ id_pedido: string; status: string; valor_total: number }> {
  const response = await fetch(`${MS_PRINCIPAL_URL}/pedidos`, {
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

async function enviarInteresse(method: "POST" | "DELETE", email: string, categorias: string[]): Promise<void> {
  const response = await fetch(`${MS_PRINCIPAL_URL}/promocoes/interesse`, {
    method,
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, categorias }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.erro || `Erro ao atualizar inscrição (${response.status})`);
  }
}

export function registrarInteresse(email: string, categorias: string[]): Promise<void> {
  return enviarInteresse("POST", email, categorias);
}

export function cancelarInteresse(email: string, categorias: string[]): Promise<void> {
  return enviarInteresse("DELETE", email, categorias);
}