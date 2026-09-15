import type {InputHTMLAttributes,SelectHTMLAttributes,LabelHTMLAttributes} from "react";
import {cn} from "@/lib/utils";
/** Controles nativos preservam teclado, validação e leitores de tela. */
export function Input({className,...props}:InputHTMLAttributes<HTMLInputElement>){return <input className={cn("input",className)} {...props}/>;}
export function Select({className,...props}:SelectHTMLAttributes<HTMLSelectElement>){return <select className={cn("input select",className)} {...props}/>;}
export function Label({className,...props}:LabelHTMLAttributes<HTMLLabelElement>){return <label className={cn("field-label",className)} {...props}/>;}
