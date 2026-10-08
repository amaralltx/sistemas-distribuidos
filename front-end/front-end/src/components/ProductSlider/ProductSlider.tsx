import React from 'react';
import { Swiper, SwiperSlide } from 'swiper/react';
import { Navigation, Pagination } from 'swiper/modules';
import { ProductCard } from '../ProductCard/ProductCard';

import 'swiper/css';
import 'swiper/css/navigation';
import 'swiper/css/pagination';
import './style.css';

export interface Product {
  id: string | number;
  name: string;
  price: number;
  imageUrl: string;
}

interface ProductSliderProps {
  title?: string;
  products: Product[];
  onBuyProduct?: (id: string | number) => void;
}

export const ProductSlider: React.FC<ProductSliderProps> = ({
  title,
  products,
  onBuyProduct,
}) => {
  return (
    <section className="product-slider-container">
      {title && <h2 className="product-slider-title">{title}</h2>}

      <Swiper
        modules={[Navigation, Pagination]}
        spaceBetween={24}
        slidesPerView={4}
        navigation
        pagination={{ clickable: true }}
        className="product-swiper"
      >
        {products.map((product) => (
          <SwiperSlide key={product.id}>
            <ProductCard
              id={product.id}
              name={product.name}
              price={product.price}
              imageUrl={product.imageUrl}
              onBuy={onBuyProduct}
            />
          </SwiperSlide>
        ))}
      </Swiper>
    </section>
  );
};