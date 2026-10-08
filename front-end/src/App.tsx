import { useState, useEffect } from "react";
import { Header } from "./components/Header/Header";
import { ProductSlider } from "./components/ProductSlider/ProductSlider";
import { Cart, type CartItem } from "./components/Cart/Cart";
import { Newsletter } from "./components/Newsletter/Newsletter";
import { OrderTracking } from "./components/OrderStatusConsole/OrderStatusConsole";
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
      isMounted = false; // Previne vazamento de memória em desmontagem do componente
    };
  }, []);

  const totalCartCount = cartItems.reduce(
    (acc, item) => acc + item.quantity,
    0,
  );

  const handleAddToCart = (productId: string | number) => {
    // Busca na lista dinâmica carregada da API
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

      // chamada REST POST /pedidos
      const result = await createOrder(cartItems);

      // Define o ID do pedido retornado pelo MS_Principal para o componente de acompanhamento
      setLastOrderId(result.id_pedido);

      // Limpa o carrinho e fecha o modal
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
        {/* Tratamento visual de Estados (Loading, Erro, Sucesso) */}
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

        {lastOrderId && (
          <div>
            <h2 style={{ fontFamily: "sans-serif", color: "#1f2937" }}>
              Acompanhe seu pedido
            </h2>
            <OrderTracking orderId={lastOrderId} />
          </div>
        )}

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
