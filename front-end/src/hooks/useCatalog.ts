import { useCallback, useEffect, useState } from "react";
import { listarProdutos } from "../services/api";
import type { Product } from "../types";
import { mensagemDeErro } from "../utils/errors";

export function useCatalog() {
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const carregar = useCallback(async (signal?: AbortSignal) => {
    setIsLoading(true);
    setError(null);
    try {
      const dados = await listarProdutos(signal);
      setProducts(dados);
    } catch (err) {
      if (signal?.aborted) return;
      setError(mensagemDeErro(err, "Erro ao carregar o catálogo."));
    } finally {
      if (!signal?.aborted) setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    void Promise.resolve().then(() => carregar(controller.signal));
    return () => controller.abort();
  }, [carregar]);

  return { products, isLoading, error, reload: () => carregar() };
}
