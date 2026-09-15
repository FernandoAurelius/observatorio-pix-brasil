"use client";
import Link from "next/link";
import {usePathname} from "next/navigation";
import {useEffect,useState,type ReactNode} from "react";
import * as Dialog from "@radix-ui/react-dialog";
import {LayoutDashboard,Table2,ChartNoAxesCombined,Dices,ChartSpline,ScatterChart,BookOpen,Database,Lightbulb,Menu,Sun,Moon,X,Check,PixIcon} from "./ui/icons";
import {LabProvider,useLab} from "./lab-context";
import {Button} from "./ui/button";
import {ExportButton,ProvenanceFooter} from "./shared";
import {period} from "@/lib/utils";
const items=[{href:"/",label:"Visão Geral",icon:LayoutDashboard},{href:"/explorar",label:"Explorar Dados",icon:Table2},{href:"/descritiva",label:"Estatística Descritiva",icon:ChartNoAxesCombined},{href:"/simulacao",label:"Probabilidade e Simulação",icon:Dices},{href:"/distribuicoes",label:"Distribuições Teóricas",icon:ChartSpline},{href:"/regressao",label:"Correlação e Regressão",icon:ScatterChart},{href:"/descobertas",label:"Descobertas",icon:Lightbulb},{href:"/metodologia",label:"Metodologia",icon:BookOpen},{href:"/sobre",label:"Sobre os Dados",icon:Database}];
function Brand(){return <Link href="/" className="brand" aria-label="Observatório Pix Brasil, início"><span className="brand-mark"><PixIcon size={25}/></span><span><strong>Observatório Pix</strong><small>BRASIL · DADOS ABERTOS</small></span></Link>;}
function Navigation({onNavigate}:{onNavigate?:()=>void}){const pathname=usePathname();return <nav aria-label="Navegação principal">{items.map((item,index)=><div key={item.href}>{index===0&&<div className="nav-section">Observatório público</div>}{index===2&&<div className="nav-section">Laboratório estatístico</div>}{index===7&&<div className="nav-section">Transparência</div>}<Link href={item.href} onClick={onNavigate} aria-current={pathname===item.href?"page":undefined} className={`nav-item ${pathname===item.href?"active":""}`}><item.icon size={16}/><span>{item.label}</span></Link></div>)}</nav>;}
function Shell({children}:{children:ReactNode}){
 const {filters,notice}=useLab();const pathname=usePathname();const [dark,setDark]=useState(false);const [open,setOpen]=useState(false);
 useEffect(()=>{setDark(localStorage.getItem("tema")==="escuro");},[]);
 useEffect(()=>{document.documentElement.classList.toggle("dark",dark);localStorage.setItem("tema",dark?"escuro":"claro");},[dark]);
 return <div className="application"><a className="skip-link" href="#conteudo">Ir para o conteúdo</a><aside className="sidebar"><Brand/><span className="panel-label"><span className="status-dot"/>Painel estatístico</span><Navigation/><div className="sidebar-bottom"><div className="source-label"><Database size={14}/><div>Fonte dos dados<strong>Banco Central do Brasil</strong></div></div><div className="sidebar-tools"><span>Atualização mensal</span><Button variant="ghost" size="icon" aria-label={dark?"Ativar tema claro":"Ativar tema escuro"} onClick={()=>setDark(!dark)}>{dark?<Sun size={17}/>:<Moon size={17}/>}</Button></div></div></aside>
 <div className="workspace"><header className="topbar"><Dialog.Root open={open} onOpenChange={setOpen}><Dialog.Trigger asChild><Button className="mobile-menu" size="icon" variant="ghost" aria-label="Abrir navegação"><Menu/></Button></Dialog.Trigger><Dialog.Portal><Dialog.Overlay className="drawer-overlay"/><Dialog.Content className="drawer"><Dialog.Title className="sr-only">Navegação</Dialog.Title><Dialog.Description className="sr-only">Páginas do observatório e do laboratório estatístico.</Dialog.Description><div className="drawer-header"><Brand/><Dialog.Close asChild><Button size="icon" variant="ghost" aria-label="Fechar navegação"><X/></Button></Dialog.Close></div><Navigation onNavigate={()=>setOpen(false)}/></Dialog.Content></Dialog.Portal></Dialog.Root>
 <div className="breadcrumb"><span className="topmark"><PixIcon size={21}/></span><span>OBSERVATÓRIO<br/><b>PIX BRASIL</b></span><span className="breadcrumb-divider">/</span><strong>{items.find(item=>item.href===pathname)?.label??"Laboratório"}</strong></div>
 <div className="topbar-right"><div className="period-tag"><small>COMPETÊNCIA</small><span>{period(filters.inicio)}{filters.fim!==filters.inicio?` — ${period(filters.fim)}`:""}</span></div><ExportButton report/></div></header>
 <main id="conteudo" className="content">{children}<ProvenanceFooter/></main>
 </div>{notice&&<div className="toast" role="status"><Check size={17}/>{notice}</div>}</div>;
}
export function AppShell({children}:{children:ReactNode}){return <LabProvider><Shell>{children}</Shell></LabProvider>;}
