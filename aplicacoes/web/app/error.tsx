"use client";
import {Button} from "@/components/ui/button";
export default function ErrorPage({reset}:{error:Error;reset:()=>void}){return <div className="error-state" role="alert"><h1>Não foi possível exibir esta página</h1><p>Verifique sua conexão e tente novamente.</p><Button onClick={reset}>Tentar novamente</Button></div>;}
