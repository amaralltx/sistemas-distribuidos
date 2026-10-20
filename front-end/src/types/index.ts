export interface Product {
  id: string;
  nome: string;
  preco: number;
  quantidade: number;
  categoria: string;
  imagem: string;
}

export interface CartItem {
  id: string;
  nome: string;
  preco: number;
  imagem: string;
  quantity: number;
}

export interface OrderCreated {
  id_pedido: string;
  status: string;
  valor_total: number;
  mensagem: string;
}

export interface OrderEvent {
  seq: number;
  id_pedido: string;
  status: string;
  routing_key: string;
  final: boolean;
}
