import { useMemo, useState } from "react";
import type { CartItem, Product } from "../types";

function erroDeEstoque(
  produto: Product,
  quantidadePretendida: number,
): string | null {
  if (quantidadePretendida <= produto.quantidade) return null;
  return `Estoque insuficiente! "${produto.nome}" possui apenas ${produto.quantidade} unidade(s).`;
}

export function useCart(products: Product[]) {
  const [items, setItems] = useState<CartItem[]>([]);

  const produtoPorId = useMemo(
    () => new Map(products.map((produto) => [produto.id, produto])),
    [products],
  );

  const quantidadeNoCarrinho = (id: string) =>
    items.find((item) => item.id === id)?.quantity ?? 0;

  function add(produto: Product): string | null {
    const erro = erroDeEstoque(produto, quantidadeNoCarrinho(produto.id) + 1);
    if (erro) return erro;

    setItems((prev) => {
      if (prev.some((item) => item.id === produto.id)) {
        return prev.map((item) =>
          item.id === produto.id
            ? { ...item, quantity: item.quantity + 1 }
            : item,
        );
      }
      return [
        ...prev,
        {
          id: produto.id,
          nome: produto.nome,
          preco: produto.preco,
          imagem: produto.imagem,
          quantity: 1,
        },
      ];
    });
    return null;
  }

  function changeQuantity(id: string, delta: number): string | null {
    const nova = quantidadeNoCarrinho(id) + delta;

    if (delta > 0) {
      const produto = produtoPorId.get(id);
      if (!produto) return "Produto indisponível no momento.";
      const erro = erroDeEstoque(produto, nova);
      if (erro) return erro;
    }

    setItems((prev) =>
      prev.flatMap((item) => {
        if (item.id !== id) return [item];
        return nova > 0 ? [{ ...item, quantity: nova }] : [];
      }),
    );
    return null;
  }

  function remove(id: string) {
    setItems((prev) => prev.filter((item) => item.id !== id));
  }

  function clear() {
    setItems([]);
  }

  const count = useMemo(
    () => items.reduce((total, item) => total + item.quantity, 0),
    [items],
  );

  return { items, count, add, changeQuantity, remove, clear };
}
