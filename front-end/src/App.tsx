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

    const terminalStatuses = new Set([
      "Pedido Enviado.",
      "Estoque Indisponível. Pedido Cancelado.",
      "Pagamento Recusado. Pedido Cancelado.",
    ]);
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

        // O backend encerra o stream após um status final. Fechar aqui
        // evita que o EventSource interprete o encerramento como erro e
        // tente reconectar automaticamente.
        if (terminalStatuses.has(data.status)) {
          eventSource.close();
        }
      } catch (e) {
        console.log(`[SSE Raw Data - Pedido #${lastOrderId}]:`, event.data);
      }
    };

    eventSource.onerror = (err) => {
      if (eventSource.readyState !== EventSource.CLOSED) {
        console.warn(`[SSE] Erro de conexão ou reconectando ao canal do Pedido #${lastOrderId}...`, err);
      }
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

  const handleAddToCart = (idDoProduto: string | number) => {
    // Busca o produto no catálogo carregado da API
    const produto = products.find(p => String(p.id) === String(idDoProduto));
    
    if (!produto) return;

    // Verifica quantos itens desse produto o usuário já tem no carrinho
    const itemJaNoCarrinho = cartItems.find(item => String(item.id) === String(idDoProduto));
    const quantidadeAtualNoCarrinho = itemJaNoCarrinho ? itemJaNoCarrinho.quantity : 0; 

    // Valida se a adição de +1 vai ultrapassar o limite do estoque
    if (quantidadeAtualNoCarrinho + 1 > produto.quantidade) {
      alert(`Estoque insuficiente! O produto "${produto.nome}" possui apenas ${produto.quantidade} unidade(s) disponível(is).`);
      return; 
    }

    // Adiciona o item ao estado do carrinho
    setCartItems((prevItems) => {
      if (itemJaNoCarrinho) {
        // Se já existe, apenas incrementa a quantidade (quantity)
        return prevItems.map(item => 
          String(item.id) === String(idDoProduto)
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      } else {
        // Se não existe, adiciona como um novo item no carrinho
        return [
          ...prevItems, 
          { 
            id: produto.id, 
            nome: produto.nome, 
            preco: produto.preco, 
            imagem: produto.imagem,
            quantity: 1 
          }
        ];
      }
    });
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
          <div style={{ display: "flex", flexDirection: "column" }}>
            <ProductSlider
              title="Todos os Produtos"
              products={products}
              onBuyProduct={handleAddToCart}
            />
            
            {/* Slider Categoria: Feminino */}
            <ProductSlider
              title="Moda Feminina"
              products={products.filter((p) => p.categoria === "Feminino")}
              onBuyProduct={handleAddToCart}
            />

            {/* Slider Categoria: Masculino */}
            <ProductSlider
              title="Moda Masculina"
              products={products.filter((p) => p.categoria === "Masculino")}
              onBuyProduct={handleAddToCart}
            />

            {/* Slider Categoria: Infantil */}
            <ProductSlider
              title="Moda Infantil"
              products={products.filter((p) => p.categoria === "Infantil")}
              onBuyProduct={handleAddToCart}
            />
          </div>
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
        isSubmittingOrder={isSubmittingOrder}
      />
    </div>
  );
}