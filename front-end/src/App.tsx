import { useState, useEffect } from "react";
import { Header } from "./components/Header/Header";
import { ProductSlider } from "./components/ProductSlider/ProductSlider";
import { Cart, type CartItem } from "./components/Cart/Cart";
import { Newsletter } from "./components/Newsletter/Newsletter";
import {
  getProducts,
  createOrder,
  type Product,
} from "./services/productService";
import "./App.css";

export default function App() {
  // Estados para dados e controle de requisição
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Estados do carrinho e pedido
  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  const [isCartOpen, setIsCartOpen] = useState<boolean>(false);
  const [lastOrderId, setLastOrderId] = useState<string | number | null>(null);
  const [isSubmittingOrder, setIsSubmittingOrder] = useState<boolean>(false);

  // Busca os produtos ao montar o componente
  useEffect(() => {
    let isMounted = true;

    async function loadCatalog() {
      try {
        setIsLoading(true);
        setError(null);
        const fetchedProducts = await getProducts();

        if (isMounted) {
          setProducts(fetchedProducts);
        }
      } catch (err) {
        if (isMounted) {
          setError(
            err instanceof Error
              ? err.message
              : "Erro desconhecido ao carregar o catálogo.",
          );
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    loadCatalog();

    return () => {
      isMounted = false;
    };
  }, []);

  // Escuta os eventos SSE via console
  useEffect(() => {
    if (!lastOrderId) return;

    const sseUrl = `http://localhost:5000/pedidos/${lastOrderId}/sse`;
    console.log(`%c[SSE] Conectando ao canal do Pedido #${lastOrderId}...`, "color: #3b82f6; font-weight: bold;");

    const eventSource = new EventSource(sseUrl);

    eventSource.onopen = () => {
      console.log(`%c[SSE] Conexão aberta com sucesso para o Pedido #${lastOrderId}`, "color: #10b981; font-weight: bold;");
    };

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log(
          `%c[SSE STATUS - Pedido #${lastOrderId}]%c ${data.status || JSON.stringify(data)}`,
          "background: #1e293b; color: #38bdf8; padding: 2px 6px; border-radius: 4px; font-weight: bold;",
          "color: #f8fafc; font-weight: bold;"
        );
      } catch (e) {
        console.log(`[SSE Raw Data - Pedido #${lastOrderId}]:`, event.data);
      }
    };

    eventSource.onerror = (err) => {
      console.warn(`[SSE] Erro de conexão ou reconectando ao canal do Pedido #${lastOrderId}...`, err);
    };

    // Função de limpeza ao desmontar ou trocar de pedido
    return () => {
      console.log(`%c[SSE] Encerrando conexão do Pedido #${lastOrderId}`, "color: #ef4444;");
      eventSource.close();
    };
  }, [lastOrderId]);

  const totalCartCount = cartItems.reduce(
    (acc, item) => acc + item.quantity,
    0,
  );

  const handleAddToCart = (productId: string | number) => {
    const productToAdd = products.find(
      (p) => String(p.id) === String(productId),
    );
    if (!productToAdd) return;

    setCartItems((prevItems) => {
      const existingItem = prevItems.find(
        (item) => String(item.id) === String(productId),
      );

      if (existingItem) {
        return prevItems.map((item) =>
          String(item.id) === String(productId)
            ? { ...item, quantity: item.quantity + 1 }
            : item,
        );
      }

      return [...prevItems, { ...productToAdd, quantity: 1 }];
    });

    setIsCartOpen(true);
  };

  const handleUpdateQuantity = (id: string | number, delta: number) => {
    setCartItems((prevItems) =>
      prevItems
        .map((item) => {
          if (String(item.id) === String(id)) {
            const newQuantity = item.quantity + delta;
            return newQuantity > 0 ? { ...item, quantity: newQuantity } : null;
          }
          return item;
        })
        .filter((item): item is CartItem => item !== null),
    );
  };

  const handleRemoveItem = (id: string | number) => {
    setCartItems((prevItems) =>
      prevItems.filter((item) => String(item.id) !== String(id)),
    );
  };

  const handleCheckout = async () => {
    if (cartItems.length === 0) return;

    try {
      setIsSubmittingOrder(true);

      const result = await createOrder(cartItems);

      // Define o ID do pedido para disparar o useEffect com o SSE
      setLastOrderId(result.id_pedido);

      setCartItems([]);
      setIsCartOpen(false);
    } catch (err) {
      alert(
        err instanceof Error
          ? err.message
          : "Ocorreu um erro ao finalizar a compra.",
      );
    } finally {
      setIsSubmittingOrder(false);
    }
  };

  return (
    <div style={{ minWidth: "1200px" }}>
      <Header
        storeName="Loja"
        cartCount={totalCartCount}
        onOpenCart={() => setIsCartOpen(true)}
      />

      <main>
        {isLoading && (
          <div
            style={{ textAlign: "center", padding: "40px", fontSize: "1.2rem" }}
          >
            Carregando produtos do catálogo...
          </div>
        )}

        {error && (
          <div style={{ textAlign: "center", padding: "40px", color: "red" }}>
            <p>{error}</p>
            <button
              onClick={() => window.location.reload()}
              style={{ padding: "8px 16px", marginTop: "10px" }}
            >
              Tentar Novamente
            </button>
          </div>
        )}

        {!isLoading && !error && (
          <ProductSlider
            title="Produtos"
            products={products}
            onBuyProduct={handleAddToCart}
          />
        )}
        <Newsletter />

        <div
          style={{ height: "100px", marginTop: "40px", textAlign: "center" }}
        >
          Footer Bonito
        </div>
      </main>

      <Cart
        isOpen={isCartOpen}
        onClose={() => setIsCartOpen(false)}
        items={cartItems}
        onUpdateQuantity={handleUpdateQuantity}
        onRemoveItem={handleRemoveItem}
        onCheckout={handleCheckout}
      />
    </div>
  );
}