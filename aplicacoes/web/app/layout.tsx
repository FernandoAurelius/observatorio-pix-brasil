import type {Metadata} from "next";
import type {ReactNode} from "react";
import {Geist,JetBrains_Mono} from "next/font/google";
import {AppShell} from "@/components/app-shell";
import "./globals.css";

const geist=Geist({
 subsets:["latin"],
 weight:["300","400","500","600","700"],
 variable:"--font-geist",
 display:"swap",
});

const jetBrainsMono=JetBrains_Mono({
 subsets:["latin"],
 weight:["400","500","600"],
 variable:"--font-jetbrains-mono",
 display:"swap",
});

export const metadata:Metadata={title:"Observatório Pix Brasil",description:"Dados abertos do Banco Central e um laboratório estatístico com cálculos transparentes. Projeto independente e educacional."};
export default function RootLayout({children}:{children:ReactNode}){return <html lang="pt-BR" suppressHydrationWarning><body className={`${geist.variable} ${jetBrainsMono.variable}`}><AppShell>{children}</AppShell></body></html>;}
