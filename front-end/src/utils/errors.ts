export function mensagemDeErro(
  err: unknown,
  fallback = "Erro inesperado.",
): string {
  return err instanceof Error ? err.message : fallback;
}
