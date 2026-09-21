import {test,expect} from "@playwright/test";
import fs from "node:fs";
import path from "node:path";
const captures=path.resolve(__dirname,"../../../test-results/capturas");
const screens:[[string,string],...[string,string][]]=[["/","Visão Geral"],["/explorar","Explorar Dados"],["/descritiva","Estatística Descritiva"],["/distribuicoes","Distribuições Teóricas"],["/regressao","Correlação e Regressão Linear"],["/descobertas","Descobertas Estatísticas"],["/metodologia","Metodologia"],["/sobre","Sobre os Dados"]];
test.beforeAll(()=>fs.mkdirSync(captures,{recursive:true}));
test("Tipografia segue o design visual do projeto",async({page})=>{
 await page.goto("/");
 await expect(page.getByRole("heading",{name:"Visão Geral",exact:true})).toBeVisible();
 await expect(page.locator("body")).toHaveCSS("font-family",/Geist/);
 await expect(page.locator(".metric-value").first()).toHaveCSS("font-family",/JetBrains Mono/);
});
for(const [url,title] of screens){test(`Página ${title}`,async({page})=>{
 const failures:string[]=[];page.on("pageerror",error=>failures.push(error.message));
 await page.goto(url);await expect(page.getByRole("heading",{name:title,exact:true}).first()).toBeVisible();
 await expect(page.locator(".loading-state")).toHaveCount(0);
 await expect(page.locator(".error-state")).toHaveCount(0);
 const nome=url==="/"?"bcb_inicio.png":`bcb${url.replaceAll("/","_")}.png`;
 await page.screenshot({path:path.join(captures,nome),fullPage:true});
 expect(failures).toEqual([]);
 });}
test("TCL e Lei dos Grandes Números",async({page})=>{
 await page.goto("/simulacao");await page.getByRole("button",{name:"Executar simulação",exact:true}).click();
 await expect(page.getByRole("heading",{name:"Distribuição das médias amostrais",exact:true})).toBeVisible();
 await page.screenshot({path:path.join(captures,"bcb_tcl.png"),fullPage:true});
 await page.getByRole("tab",{name:"Lei dos Grandes Números"}).click();
 await page.getByRole("button",{name:"Executar simulação",exact:true}).click();
 await expect(page.getByRole("heading",{name:"Convergência da frequência relativa",exact:true})).toBeVisible();
 await page.screenshot({path:path.join(captures,"bcb_lgn.png"),fullPage:true});
});
test("Categorica, distribuicao alternativa e predicao",async({page})=>{
 await page.goto("/descritiva");await page.getByLabel("Variável",{exact:true}).selectOption("regiao");
 await expect(page.getByRole("heading",{name:"Frequência por categoria"})).toBeVisible();
 await page.goto("/distribuicoes");await page.getByLabel("Distribuição candidata").selectOption("exponencial");
 await expect(page.getByRole("heading",{name:"Dados observados × Exponencial"})).toBeVisible();
 await page.goto("/regressao");await page.getByLabel("Informe um valor para X").fill("999999999999");
 await page.getByRole("button",{name:"Calcular Ŷ"}).click();
 await expect(page.getByText("Extrapolação:",{exact:false})).toBeVisible();
});
test("Exportacao completa e menu mobile",async({page})=>{
 await page.goto("/explorar");const wait=page.waitForEvent("download");
 await page.getByRole("button",{name:"Exportar CSV",exact:true}).click();const file=await wait;
 expect(file.suggestedFilename()).toContain("pix_");
 await page.setViewportSize({width:390,height:844});
 await page.getByRole("button",{name:"Abrir navegação"}).click();
 await expect(page.getByRole("dialog")).toBeVisible();
 await page.getByRole("dialog").getByRole("link",{name:"Visão Geral",exact:true}).click();
 await expect(page.getByRole("heading",{name:"Visão Geral",exact:true})).toBeVisible();
 await expect(page.locator(".loading-state")).toHaveCount(0);
 await page.screenshot({path:path.join(captures,"bcb_mobile.png"),fullPage:true});
});
test("Responsividade sem overflow global",async({page})=>{
 for(const [largura,altura] of [[1280,720],[768,1024],[390,844]]){
  await page.setViewportSize({width:largura,height:altura});await page.goto("/");
  await expect(page.getByRole("heading",{name:"Visão Geral",exact:true})).toBeVisible();
  await expect(page.locator(".loading-state")).toHaveCount(0);
  const excede=await page.evaluate(()=>document.documentElement.scrollWidth>document.documentElement.clientWidth+1);
  expect(excede,`overflow global em ${largura}x${altura}`).toBeFalsy();
 }
});
test("Falha da API é visível e permite tentar novamente",async({page})=>{
 await page.route("**/api/panorama",route=>route.fulfill({status:503,contentType:"application/json",body:JSON.stringify({mensagem:"Fonte oficial temporariamente indisponível."})}));
 await page.goto("/");
 await expect(page.getByText("Fonte oficial temporariamente indisponível.")).toBeVisible();
 await expect(page.getByRole("button",{name:"Tentar novamente"})).toBeVisible();
});
