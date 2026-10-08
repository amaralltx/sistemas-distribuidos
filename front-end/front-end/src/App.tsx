import { useState } from "react";
import { Header } from "./components/Header/Header";
import { ProductSlider, type Product } from "./components/ProductSlider/ProductSlider";
import { Cart, type CartItem } from "./components/Cart/Cart";
import { Newsletter } from "./components/Newsletter/Newsletter";
import "./App.css";

const productsList: Product[] = [
  {
    id: "1",
    name: "Fone de Ouvido Bluetooth",
    price: 299.9,
    imageUrl: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&q=80",
  },
  {
    id: "2",
    name: "Smartwatch Esportivo",
    price: 899.5,
    imageUrl: "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&q=80",
  },
  {
    id: "3",
    name: "Câmera DSLR",
    price: 3499.0,
    imageUrl: "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=500&q=80",
  },
  {
    id: "4",
    name: "Óculos de Sol Vintage",
    price: 150.0,
    imageUrl: "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=500&q=80",
  },
  {
    id: "5",
    name: "Tênis de Corrida",
    price: 499.99,
    imageUrl: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500&q=80",
  },
];

export default function App() {
  // Lista dos itens no carrinho
  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  // Estado para controlar a abertura do carrinho (aside)
  const [isCartOpen, setIsCartOpen] = useState(false);

  // Quantidade total de itens calculada para o badge do Header
  const totalCartCount = cartItems.reduce((acc, item) => acc + item.quantity, 0);

  // Adiciona produto ou incrementa a quantidade se já existir
  const handleAddToCart = (productId: string | number) => {
    const productToAdd = productsList.find((p) => p.id === productId);
    if (!productToAdd) return;

    setCartItems((prevItems) => {
      const existingItem = prevItems.find((item) => item.id === productId);

      if (existingItem) {
        return prevItems.map((item) =>
          item.id === productId
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      }

      return [...prevItems, { ...productToAdd, quantity: 1 }];
    });

    // Abre o carrinho automaticamente ao clicar em comprar
    setIsCartOpen(true);
  };

  // Atualiza quantidade (+1 ou -1) e remove se for <= 0
  const handleUpdateQuantity = (id: string | number, delta: number) => {
    setCartItems((prevItems) =>
      prevItems
        .map((item) => {
          if (item.id === id) {
            const newQuantity = item.quantity + delta;
            return newQuantity > 0 ? { ...item, quantity: newQuantity } : null;
          }
          return item;
        })
        .filter((item): item is CartItem => item !== null)
    );
  };

  // Remove item diretamente
  const handleRemoveItem = (id: string | number) => {
    setCartItems((prevItems) => prevItems.filter((item) => item.id !== id));
  };

  // Finalizar Compra e gerar o objeto final do pedido
  const handleCheckout = () => {
    const totalValue = cartItems.reduce(
      (acc, item) => acc + item.price * item.quantity,
      0
    );

    // Estrutura de dados do pedido completo
    const orderData = {
      orderId: Date.now(),
      items: cartItems,
      totalValue: totalValue,
      createdAt: new Date().toISOString(),
    };

    console.log("Pedido Finalizado:", orderData);
    alert(`Compra realizada com sucesso!\nTotal: R$ ${totalValue.toFixed(2)}`);

    // Limpa o carrinho e fecha a gaveta
    setCartItems([]);
    setIsCartOpen(false);
  };

return (
    <div style={{ minWidth: "1200px" }}>
      <Header
        storeName="Loja"
        cartCount={totalCartCount}
        onOpenCart={() => setIsCartOpen(true)}
      />

      <main>
        <ProductSlider
          title="Produtos"
          products={productsList}
          onBuyProduct={handleAddToCart}
        />

        {/* Componente Newsletter adicionado aqui */}
        <Newsletter/>
        <div style={{ height: "100px" }}>Footer Bonito</div>
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