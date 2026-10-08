import { type CartItem } from "../components/Cart/Cart";

// Interface representando o contrato exato devolvido pela API Flask
export interface BackendProduct {
  codigo: string;
  nome: string;
  preco: number;
  quantidade: number;
  categoria: string;
  imagem: string;
}

// Interface utilizada no frontend
export interface Product {
  id: string;
  name: string;
  price: number;
  imageUrl: string;
  category?: string;
  stockQuantity?: number;
}

const API_BASE_URL = 'http://localhost:5000';


export async function getProducts(): Promise<Product[]> {
  const response = await fetch(`${API_BASE_URL}/produtos`);

  if (!response.ok) {
    throw new Error(`Erro ao carregar catálogo de produtos (${response.status})`);
  }

  const data: BackendProduct[] = await response.json();

  // Mapeamento (Adapter pattern) do DTO do Backend para o formato da UI
  return data.map((item) => ({
    id: item.codigo,
    name: item.nome,
    price: item.preco,
    imageUrl: item.imagem,
    category: item.categoria,
    stockQuantity: item.quantidade,
  }));
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