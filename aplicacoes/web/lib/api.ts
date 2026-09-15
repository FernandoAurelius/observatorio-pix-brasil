"use client";
import {useEffect,useState,useCallback} from "react";
import type {Envelope} from "./types";
/** Transporte abortável, sem substituir erro por dados ilustrativos. */
export async function request<T>(path:string, body?:unknown, signal?:AbortSignal):Promise<T> {
  const response = await fetch(`/api/${path}`, {method:body===undefined?"GET":"POST", headers:body===undefined?{}:{"Content-Type":"application/json"}, body:body===undefined?undefined:JSON.stringify(body), signal, cache:"no-store"});
  if (!response.ok) {
    const error = await response.json().catch(() => ({mensagem:"A API não respondeu no formato esperado."}));
    throw new Error(error.mensagem ?? `Falha na consulta (${response.status}).`);
  }
  return response.json() as Promise<T>;
}
export function useResource<T>(path:string, body?:unknown, enabled=true) {
  const key = body===undefined ? "" : JSON.stringify(body);
  const [data,setData]=useState<T>(); const [error,setError]=useState("");
  const [loading,setLoading]=useState(enabled); const [revision,setRevision]=useState(0);
  const retry=useCallback(() => setRevision(value=>value+1),[]);
  useEffect(() => {
    if (!enabled) {setLoading(false);return;}
    const controller=new AbortController(); let current=true;
    setLoading(true);setError("");setData(undefined);
    request<T>(path,key===""?undefined:JSON.parse(key),controller.signal)
      .then(value=>{if(current)setData(value);})
      .catch((failure:Error)=>{if(current && failure.name!=="AbortError")setError(failure.message);})
      .finally(()=>{if(current)setLoading(false);});
    return ()=>{current=false;controller.abort();};
  },[path,key,enabled,revision]);
  return {data,error,loading,retry};
}
export type AnalysisResponse<T> = ReturnType<typeof useResource<Envelope<T>>>;
