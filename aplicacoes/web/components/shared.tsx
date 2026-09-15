"use client";
import {AlertTriangle,RefreshCw,Download,Share2,Database,Info} from "./ui/icons";
import type {ReactNode} from "react";
import {Button} from "./ui/button";
import {Card,CardContent,CardHeader,CardTitle} from "./ui/card";
import {Select,Input,Label} from "./ui/input";
import {useLab,useAnalysis} from "./lab-context";
import {download,number,period} from "@/lib/utils";
import type {Geography,Filters} from "@/lib/types";

export function PageHeading({eyebrow,title,description,actions}:{eyebrow?:string;title:string;description:string;actions?:ReactNode}){
 return <div className="page-heading"><div><div className="eyebrow"><span className="badge">{eyebrow??"LABORATÓRIO ESTATÍSTICO"}</span><span className="mini-label">Matemática transparente</span></div><h1>{title}</h1><p>{description}</p></div>{actions&&<div className="heading-actions">{actions}</div>}</div>;
}
export function Metric({label,value,hint,icon,accent=false}:{label:string;value:ReactNode;hint?:string;icon?:ReactNode;accent?:boolean}){
 return <Card className={accent?"metric accent":"metric"}><div className="metric-label">{label}{icon}</div><div className="metric-value">{value}</div>{hint&&<p className="metric-hint">{hint}</p>}</Card>;
}
export function InfoBox({children,tone="info",title}:{children:ReactNode;tone?:"info"|"warning"|"success";title?:string}){
 return <div className={`info-box ${tone}`}><span aria-hidden="true">{tone==="warning"?<AlertTriangle size={17}/>:<Info size={17}/>}</span><div>{title&&<strong>{title}</strong>}<div>{children}</div></div></div>;
}
export function Status({loading,error,onRetry}:{loading:boolean;error:string;onRetry:()=>void}){
 if(error)return <div role="alert" className="error-state"><AlertTriangle/><h2>Não foi possível carregar os dados</h2><p>{error}</p><p className="small muted">Verifique sua conexão e tente novamente em alguns instantes.</p><Button onClick={onRetry}><RefreshCw size={16}/>Tentar novamente</Button></div>;
 if(loading)return <div aria-busy="true" role="status" className="loading-state"><div className="loading-label"><RefreshCw size={16} className="spin"/>Preparando os resultados…</div><div className="metrics-grid">{[1,2,3,4].map(key=><div key={key} className="skeleton metric"/>)}</div><div className="skeleton skeleton-chart"/></div>;
 return null;
}
export function FilterBar(){
 const {filters,setFilters,context}=useLab();const geography=useAnalysis<Geography>("filtros",filters);
 const update=(key:keyof Filters,value:string)=>setFilters({...filters,[key]:value,...(key==="regiao"?{uf:"",municipio:""}:key==="uf"?{municipio:""}:{})});
 return <Card className="filter-card"><div className="filters-row">
  <div className="filter-item"><Label htmlFor="inicio">De</Label><Input id="inicio" type="month" value={`${filters.inicio.slice(0,4)}-${filters.inicio.slice(4)}`} min="2020-11" onChange={event=>update("inicio",event.target.value.replace("-",""))}/></div>
  <div className="filter-item"><Label htmlFor="fim">Até</Label><Input id="fim" type="month" value={`${filters.fim.slice(0,4)}-${filters.fim.slice(4)}`} min="2020-11" onChange={event=>update("fim",event.target.value.replace("-",""))}/></div>
  <div className="filter-item"><Label htmlFor="regiao">Região</Label><Select id="regiao" value={filters.regiao} onChange={event=>update("regiao",event.target.value)}><option value="">Todas as regiões</option>{geography.data?.resultado.regioes.map(value=><option key={value}>{value}</option>)}</Select></div>
  <div className="filter-item narrow"><Label htmlFor="uf">UF</Label><Select id="uf" value={filters.uf} onChange={event=>update("uf",event.target.value)}><option value="">Todas</option>{geography.data?.resultado.estados.map(value=><option key={value}>{value}</option>)}</Select></div>
  <div className="filter-item grow"><Label htmlFor="municipio">Município</Label><Select id="municipio" value={filters.municipio} onChange={event=>update("municipio",event.target.value)}><option value="">Todos os municípios</option>{geography.data?.resultado.municipios.map(value=><option key={value.codigo} value={value.codigo}>{value.nome} / {value.uf}</option>)}</Select></div>
  <Button variant="ghost" size="sm" onClick={()=>setFilters({inicio:"202512",fim:"202512",regiao:"",uf:"",municipio:""})}>Limpar</Button>
  <Button variant="secondary" size="sm" onClick={()=>setFilters({...filters,inicio:"202501",fim:"202512"})}>2025 completo</Button>
 </div><div className="filter-context"><span className="scope"><Database size={13}/>{context?`${number(context.municipios,0)} municípios · ${number(context.registros,0)} observações`:(geography.loading?"Carregando abrangência…":"Abrangência indisponível")}</span><span>Unidade: município-mês · atualização mensal</span></div>{geography.error&&<p className="small warning-text">Categorias indisponíveis: {geography.error}</p>}</Card>;
}
export function VariableSelect({value,onChange,label="Variável",id="variavel",categories=false}:{value:string;onChange:(value:string)=>void;label?:string;id?:string;categories?:boolean}){
 const {catalog}=useLab();return <div className="filter-item grow"><Label htmlFor={id}>{label}</Label><Select id={id} value={value} onChange={event=>onChange(event.target.value)}>{!catalog&&<option value={value}>{value}</option>}{catalog&&<optgroup label="Variáveis numéricas">{Object.entries(catalog.numericas).map(([key,definition])=><option key={key} value={key}>{definition.rotulo}</option>)}</optgroup>}{categories&&catalog&&<optgroup label="Variáveis categóricas">{Object.entries(catalog.categoricas).map(([key,definition])=><option key={key} value={key}>{definition}</option>)}</optgroup>}</Select></div>;
}
export function ExportButton({report=false}:{report?:boolean}){
 const {filters,notify}=useLab();
 async function exportData(){try{const response=await fetch(`/api/${report?"relatorio":"exportar"}`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(filters)});if(!response.ok){const error=await response.json();throw new Error(error.mensagem??"Falha ao exportar.");}const disposition=response.headers.get("content-disposition");const name=disposition?.match(/filename="([^"]+)"/)?.[1]??`pix_${filters.inicio}_${filters.fim}.${report?"md":"csv"}`;download(name,await response.blob());notify("Arquivo exportado com os filtros atuais.");}catch(error){notify(error instanceof Error?error.message:"Falha na exportação.");}}
 return <Button onClick={exportData}><Download size={15}/>{report?"Exportar relatório":"Exportar CSV"}</Button>;
}
export function ShareButton(){const {filters,notify}=useLab();return <Button variant="outline" onClick={async()=>{try{const url=new URL(window.location.href);url.search=new URLSearchParams(filters).toString();await navigator.clipboard.writeText(url.toString());notify("Link do recorte copiado. Seletores específicos de cada análise não estão incluídos.");}catch{notify("Não foi possível acessar a área de transferência.");}}}><Share2 size={15}/>Compartilhar recorte</Button>;}
export function ProvenanceFooter(){const {context}=useLab();if(!context)return null;const year=new Date().getFullYear();return <footer className="provenance"><span><span className="status-dot"/> Dados do Banco Central do Brasil</span><span>Período analisado: {period(context.inicio)} — {period(context.fim)}</span><span>© {year} · Criado por <a href="https://github.com/FernandoAurelius" target="_blank" rel="noreferrer">@FernandoAurelius</a></span></footer>;}
export function ChartCard({title,subtitle,children,action,className=""}:{title:string;subtitle?:string;children:ReactNode;action?:ReactNode;className?:string}){return <Card className={className}><CardHeader><div><CardTitle>{title}</CardTitle>{subtitle&&<p className="muted small">{subtitle}</p>}</div>{action}</CardHeader><CardContent>{children}</CardContent></Card>;}
export function Empty(){return <div className="empty-state"><Database/><h3>Nenhum dado encontrado</h3><p>Amplie o período ou limpe os filtros selecionados.</p></div>;}
