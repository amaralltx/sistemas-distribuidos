import { useMemo, useState } from "react";
import { Header } from "./components/Header/Header";
import { ProductSlider } from "./components/ProductSlider/ProductSlider";
import { Cart } from "./components/Cart/Cart";
import { Newsletter } from "./components/Newsletter/Newsletter";
import { OrdersPanel } from "./components/OrdersPanel/OrdersPanel";
import { useCatalog } from "./hooks/useCatalog";
import { useCart } from "./hooks/useCart";
import { useOrderTracking } from "./hooks/useOrderTracking";
import { criarPedido } from "./services/api";
import { rotuloCategoria } from "./config/categorias";
import { mensagemDeErro } from "./utils/errors";
import "./App.css";

export default function App() {
  const catalogo = useCatalog();
  const carrinho = useCart(catalogo.products);
  const pedidos = useOrderTracking();

  const [carrinhoAberto, setCarrinhoAberto] = useState(false);
  const [enviandoPedido, setEnviandoPedido] = useState(false);
  const [aviso, setAviso] = useState<string | null>(null);

  const categorias = useMemo(
    () => [...new Set(catalogo.products.map((produto) => produto.categoria))],
    [catalogo.products],
  );

  function adicionarAoCarrinho(id: string | number) {
    const produto = catalogo.products.find(
      (item) => item.id === String(id),
    );
    if (!produto) return;
    const erro = carrinho.add(produto);
    if (erro) setAviso(erro);
  }

  function alterarQuantidade(id: string, delta: number) {
    const erro = carrinho.changeQuantity(id, delta);
    if (erro) setAviso(erro);
  }

  async function finalizarCompra() {
    if (carrinho.items.length === 0) return;

    setEnviandoPedido(true);
    setAviso(null);
    try {
      const pedido = await criarPedido(carrinho.items);
      pedidos.track(pedido.id_pedido);
      carrinho.clear();
      setCarrinhoAberto(false);
      catalogo.reload();
    } catch (err) {
      setAviso(mensagemDeErro(err, "Erro ao finalizar a compra."));
    } finally {
      setEnviandoPedido(false);
    }
  }

  return (
    <div className="app">
      <Header
        storeName="Loja"
        cartCount={carrinho.count}
        onOpenCart={() => setCarrinhoAberto(true)}
      />

      <main>
        {aviso && (
          <div role="alert" className="aviso" onClick={() => setAviso(null)}>
            {aviso}
          </div>
        )}

        {catalogo.isLoading && (
          <p className="status">Carregando produtos do catálogo...</p>
        )}

        {catalogo.error && (
          <div className="status erro">
            <p>{catalogo.error}</p>
            <button onClick={catalogo.reload}>Tentar novamente</button>
          </div>
        )}

        {!catalogo.isLoading && !catalogo.error && (
          <div className="catalogo">
            <ProductSlider
              title="Todos os Produtos"
              products={catalogo.products}
              onBuyProduct={adicionarAoCarrinho}
            />
            {categorias.map((categoria) => (
              <ProductSlider
                key={categoria}
                title={rotuloCategoria(categoria)}
                products={catalogo.products.filter(
                  (produto) => produto.categoria === categoria,
                )}
                onBuyProduct={adicionarAoCarrinho}
              />
            ))}
          </div>
        )}

        <OrdersPanel pedidos={pedidos.pedidos} />
        <Newsletter />
      </main>

      <Cart
        isOpen={carrinhoAberto}
        onClose={() => setCarrinhoAberto(false)}
        items={carrinho.items}
        onUpdateQuantity={alterarQuantidade}
        onRemoveItem={carrinho.remove}
        onCheckout={finalizarCompra}
        isSubmittingOrder={enviandoPedido}
      />
    </div>
  );
}
