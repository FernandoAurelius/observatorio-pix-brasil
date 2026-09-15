import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
/** Combina classes seguindo o padrão shadcn/ui. */
export function cn(...inputs: ClassValue[]) { return twMerge(clsx(inputs)); }
/** Formata apenas a apresentação; não calcula medidas estatísticas. */
export function number(value: number | null | undefined, digits = 2) {
  return value == null || !Number.isFinite(value) ? "Indefinido" : new Intl.NumberFormat("pt-BR", {maximumFractionDigits: digits}).format(value);
}
export function compact(value: number | null | undefined) {
  return value == null || !Number.isFinite(value) ? "—" : new Intl.NumberFormat("pt-BR", {notation: "compact", maximumFractionDigits: 2}).format(value);
}
export function money(value: number | null | undefined, abbreviated = false) {
  if (value == null || !Number.isFinite(value)) return "Indefinido";
  return new Intl.NumberFormat("pt-BR", abbreviated
    ? {style:"currency",currency:"BRL",notation:"compact",maximumFractionDigits:2}
    : {style:"currency",currency:"BRL",maximumFractionDigits:2}).format(value);
}
export function period(value: string) { return `${value.slice(4,6)}/${value.slice(0,4)}`; }
export function precise(value: number | null | undefined) {
  if (value == null || !Number.isFinite(value)) return "Indefinido";
  if (value !== 0 && (Math.abs(value) < 0.001 || Math.abs(value) > 1e10)) return value.toExponential(4).replace(".",",");
  return number(value,6);
}
/** Salva um resultado efetivamente recebido, sem gerar números no cliente. */
export function download(name: string, content: Blob | string, type="application/json") {
  const blob = content instanceof Blob ? content : new Blob([content], {type});
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a"); anchor.href=url; anchor.download=name; anchor.click();
  setTimeout(() => URL.revokeObjectURL(url),1000);
}
