import {Lineicons,type LineiconsProps} from "@lineiconshq/react-lineicons";
import {
 ArrowAngularTopRightStroke,ArrowBothDirectionHorizontal1Stroke,ArrowBothDirectionVertical1Stroke,
 BarChart4Stroke,Book1Stroke,Bulb2Stroke,Calculator1Stroke,CheckStroke,ChevronLeftStroke,
 ChevronRightStroke,Code1Stroke,DashboardSquare1Stroke,Database2Stroke,Download1Stroke,
 ExitUpStroke,FileMultipleStroke,MapPin5Stroke,MenuHamburger1Stroke,MoonHalfRight5Stroke,
 PieChart2Stroke,PlayStroke,QuestionMarkCircleStroke,RefreshCircle1ClockwiseStroke,
 Search1Stroke,Share1Stroke,Sun1Stroke,Ticket1Stroke,TrendUp1Stroke,VectorNodes6Stroke,
 Wallet1Stroke,XmarkStroke,
} from "@lineiconshq/free-icons";

type IconProps=Omit<LineiconsProps,"icon">;
function criarIcone(icon:LineiconsProps["icon"]){return function Icone(props:IconProps){return <Lineicons icon={icon} {...props}/>;};}

export const ArrowUpRight=criarIcone(ArrowAngularTopRightStroke);
export const ArrowLeftRight=criarIcone(ArrowBothDirectionHorizontal1Stroke);
export const ArrowDownUp=criarIcone(ArrowBothDirectionVertical1Stroke);
export const ChartNoAxesCombined=criarIcone(BarChart4Stroke);
export const BookOpen=criarIcone(Book1Stroke);
export const Lightbulb=criarIcone(Bulb2Stroke);
export const Calculator=criarIcone(Calculator1Stroke);
export const Check=criarIcone(CheckStroke);
export const ChevronLeft=criarIcone(ChevronLeftStroke);
export const ChevronRight=criarIcone(ChevronRightStroke);
export const Code2=criarIcone(Code1Stroke);
export const LayoutDashboard=criarIcone(DashboardSquare1Stroke);
export const Database=criarIcone(Database2Stroke);
export const Download=criarIcone(Download1Stroke);
export const ExternalLink=criarIcone(ExitUpStroke);
export const Table2=criarIcone(FileMultipleStroke);
export const MapPin=criarIcone(MapPin5Stroke);
export const Menu=criarIcone(MenuHamburger1Stroke);
export const Moon=criarIcone(MoonHalfRight5Stroke);
export const Dices=criarIcone(PieChart2Stroke);
export const Play=criarIcone(PlayStroke);
export const AlertTriangle=criarIcone(QuestionMarkCircleStroke);
export const RefreshCw=criarIcone(RefreshCircle1ClockwiseStroke);
export const Search=criarIcone(Search1Stroke);
export const Share2=criarIcone(Share1Stroke);
export const Sun=criarIcone(Sun1Stroke);
export const Receipt=criarIcone(Ticket1Stroke);
export const ChartSpline=criarIcone(TrendUp1Stroke);
export const ScatterChart=criarIcone(VectorNodes6Stroke);
export const Wallet=criarIcone(Wallet1Stroke);
export const X=criarIcone(XmarkStroke);
export const Info=criarIcone(QuestionMarkCircleStroke);

/** Símbolo Pix em versão monocromática para ambientes digitais. */
export function PixIcon({size=24,className}:{size?:number;className?:string}){
 return <svg aria-hidden="true" className={className} width={size} height={size} viewBox="0 0 24 24" fill="currentColor"><path d="M5.283 18.36a3.505 3.505 0 0 0 2.493-1.032l3.6-3.6a.684.684 0 0 1 .946 0l3.613 3.613a3.504 3.504 0 0 0 2.493 1.032h.71l-4.56 4.56a3.647 3.647 0 0 1-5.156 0L4.85 18.36Zm13.145-12.733a3.505 3.505 0 0 0-2.493 1.032l-3.613 3.614a.67.67 0 0 1-.946 0l-3.6-3.6A3.505 3.505 0 0 0 5.283 5.64h-.434l4.573-4.572a3.646 3.646 0 0 1 5.156 0l4.559 4.559ZM1.068 9.422 3.79 6.699h1.492a2.483 2.483 0 0 1 1.744.722l3.6 3.6a1.73 1.73 0 0 0 2.443 0l3.614-3.613a2.482 2.482 0 0 1 1.744-.723h1.767l2.737 2.737a3.646 3.646 0 0 1 0 5.156l-2.736 2.736h-1.768a2.482 2.482 0 0 1-1.744-.722l-3.613-3.613a1.77 1.77 0 0 0-2.444 0l-3.6 3.6a2.483 2.483 0 0 1-1.744.722H3.791l-2.723-2.723a3.646 3.646 0 0 1 0-5.156Z"/></svg>;
}
