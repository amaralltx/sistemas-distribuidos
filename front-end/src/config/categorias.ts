export const ROTULOS_CATEGORIA: Record<string, string> = {
  Feminino: "Moda Feminina",
  Masculino: "Moda Masculina",
  Infantil: "Moda Infantil",
};

export function rotuloCategoria(categoria: string): string {
  return ROTULOS_CATEGORIA[categoria] ?? categoria;
}
