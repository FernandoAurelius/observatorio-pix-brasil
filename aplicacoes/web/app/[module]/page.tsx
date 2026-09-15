import {notFound} from "next/navigation";
import {ExplorerPage} from "@/components/pages/explorer";
import {DescriptivePage} from "@/components/pages/descriptive";
import {SimulationPage} from "@/components/pages/simulation";
import {DistributionPage} from "@/components/pages/distribution";
import {RegressionPage} from "@/components/pages/regression";
import {MethodologyPage,SourcesPage,FindingsPage} from "@/components/pages/documentation";
const pages={explorar:ExplorerPage,descritiva:DescriptivePage,simulacao:SimulationPage,distribuicoes:DistributionPage,regressao:RegressionPage,metodologia:MethodologyPage,sobre:SourcesPage,descobertas:FindingsPage};
export function generateStaticParams(){return Object.keys(pages).map(module=>({module}));}
export default async function Page({params}:{params:Promise<{module:string}>}){const {module}=await params;if(!(module in pages))notFound();const Component=pages[module as keyof typeof pages];return <Component/>;}
