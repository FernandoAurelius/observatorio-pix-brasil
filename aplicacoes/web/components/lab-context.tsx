"use client";
import {createContext,useContext,useState,useEffect,useCallback,type ReactNode} from "react";
import {useResource} from "@/lib/api";
import type {Catalog,Filters,Context,Envelope} from "@/lib/types";
const initialFilters:Filters={inicio:"202512",fim:"202512",regiao:"",uf:"",municipio:""};
type LabState={filters:Filters;setFilters:(value:Filters)=>void;catalog?:Catalog;context?:Context;setContext:(value:Context)=>void;notice:string;notify:(value:string)=>void};
const LabContext=createContext<LabState|null>(null);
/** Filtros compartilhados são parte da URL, para reproduzir o recorte. */
export function LabProvider({children}:{children:ReactNode}){
 const [filters,changeFilters]=useState(initialFilters);const [context,setContext]=useState<Context>();const [notice,notify]=useState("");
 const catalog=useResource<Catalog>("catalogo");
 useEffect(()=>{const params=new URLSearchParams(window.location.search);const restored={...initialFilters};
   for(const key of Object.keys(restored) as (keyof Filters)[]) {const value=params.get(key);if(value!==null)restored[key]=value;}
   changeFilters(restored);
 },[]);
 const setFilters=useCallback((value:Filters)=>{changeFilters(value);setContext(undefined);},[]);
 useEffect(()=>{if(!notice)return;const timeout=setTimeout(()=>notify(""),5000);return()=>clearTimeout(timeout);},[notice]);
 return <LabContext.Provider value={{filters,setFilters,catalog:catalog.data,context,setContext,notice,notify}}>{children}</LabContext.Provider>;
}
export function useLab(){const context=useContext(LabContext);if(!context)throw new Error("Contexto da aplicação indisponível.");return context;}
export function useAnalysis<T>(path:string,body?:unknown,enabled=true){
 const {setContext}=useLab();const resource=useResource<Envelope<T>>(path,body,enabled);
 useEffect(()=>{if(resource.data)setContext(resource.data.contexto);},[resource.data,setContext]);
 return resource;
}
