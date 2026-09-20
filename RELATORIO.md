# Relatório — Observatório Pix Brasil

**Disciplina:** Matemática e Estatística para Computação. **Atividade:** Sistematização — Laboratório Estatístico Interativo.

**Autor:** Miguel Fernando Flores Barreto. **RA:** 72650465.

## 1. Objetivo e desenho do estudo

O projeto transforma medidas estatísticas em uma aplicação interativa. Seu núcleo não utiliza funções prontas de NumPy, SciPy, Pandas ou statistics; implementa as fórmulas com operações elementares. Bibliotecas consolidadas são usadas como referências independentes nos testes.

A camada pública facilita consultar os dados, enquanto o laboratório expõe convenções e limitações. A interface utiliza Next.js, com backend FastAPI e biblioteca Python separados.

O recorte acadêmico proposto é **2025**, com observações **município-mês**. Uma linha não é uma pessoa, uma empresa ou uma transação individual. Para análises entre municípios, pode-se fixar uma única competência, evitando misturar variação geográfica e temporal. Ao usar um ano, resultados são descritivos do painel; não se presume independência entre meses de um mesmo município.

## 2. Dataset e justificativa — M0

Fonte: [BCB, Estatísticas do Pix](https://dadosabertos.bcb.gov.br/dataset/pix). Recurso: [Transações Pix por Município](https://dadosabertos.bcb.gov.br/dataset/pix/resource/268e3bf6-b096-4006-83cd-813697012ece). A API disponibiliza perspectivas de pagador e recebedor, separadas em PF/PJ, e categorias municipais/regionais. O catálogo informa periodicidade mensal e ODbL.

A escolha permite trabalhar com valores monetários, contagens, heterogeneidade geográfica e associações de interesse público. O uso de uma única fonte reduz o risco de juntar indicadores de anos e definições incompatíveis.

| Campos originais | Natureza | Uso |
|---|---|---|
| `VL_PagadorPF`, `VL_PagadorPJ` | Numérica contínua | Valores pagos |
| `VL_RecebedorPF`, `VL_RecebedorPJ` | Numérica contínua | Valores recebidos |
| `QT_PagadorPF`, `QT_PagadorPJ` | Numérica discreta | Quantidades de transações pagas |
| `QT_RecebedorPF`, `QT_RecebedorPJ` | Numérica discreta | Quantidades de transações recebidas |
| `QT_PES_PagadorPF`, `QT_PES_PagadorPJ` | Numérica discreta | Contagens mensais de pessoas pagadoras |
| `QT_PES_RecebedorPF`, `QT_PES_RecebedorPJ` | Numérica discreta | Contagens mensais de pessoas recebedoras |
| `Municipio`, `Estado`, `Regiao` | Categórica nominal | Filtros e frequências |
| `AnoMes` | Temporal | Competência |
| `Municipio_Ibge`, `Estado_Ibge` | Identificadores | Chaves, agrupamentos, UF; nunca medidas |

O recorte de 01/2025 a 12/2025 foi auditado por `scripts/auditar_dataset.py` e atende ao mínimo de **1.000 registros reais**, quatro numéricas e duas categóricas. A evidência está em `documentacao/evidencias/auditoria_dataset_2025.json`.

| Métrica | Resultado |
|---|---:|
| Registros município-mês | 66.837 |
| Códigos municipais distintos | 5.571 |
| Estados/UFs | 27 |
| Regiões | 5 |
| Competências | 12 (202501–202512) |
| Variáveis numéricas | 12 |
| Variáveis categóricas | 4 |
| Ausências numéricas | 0 |
| Duplicidades município-mês | 0 |
| Tipos incorretos | 0 |
| Valores/quantidades negativos | 0 |
| Linhas “N/D” excluídas | 12 (uma por competência) |

### Tratamento dos dados

O provedor usa URL oficial fixa, competência validada, `$filter=AnoMes eq AAAAMM` e ordenação por código. Na consulta de 20/09/2026, o Swagger não anunciava `$skip`, esse parâmetro produzia HTTP 500 e a resposta integral não continha `@odata.nextLink`. O cliente rejeita um `nextLink` futuro para nunca apresentar resultado parcial sem implementar antes o novo contrato. Chaves duplicadas, competências inesperadas e campos ausentes causam erro explícito.

Códigos sem sete dígitos municipais são excluídos e contabilizados. Ausência numérica é preservada como `None`. Contagens devem ser inteiras, finitas e não negativas. Valores monetários não recebem multiplicadores implícitos ou correção inflacionária; a unidade deve ser confrontada com o contrato oficial antes da publicação. O agregado nacional do recorte não substitui totais oficiais com cobertura diferente.

A descritiva exclui ausentes somente da variável selecionada. A regressão exclui **pares** com ausência em X ou Y, mantendo o alinhamento. Atípicos permanecem nos cálculos. Não se soma pagador + recebedor e não se interpretam somas de pessoas mensais como indivíduos únicos anuais.

## 3. Núcleo matemático próprio — M1

Todos os identificadores autorais do backend e as docstrings são em português. APIs de bibliotecas (`FastAPI`, `get`, `model_config`), palavras reservadas e campos externos mantêm os nomes exigidos pelo protocolo. O núcleo é independente de FastAPI/Next. Recebe sequências, valida o domínio e retorna valores não arredondados; arredondamento é apenas visual.

Considere $n$ observações reais finitas $x_1,\ldots,x_n$.

### 3.1 Média, mediana, moda e amplitude

$$\bar{x}=\frac{1}{n}\sum_{i=1}^{n}x_i.$$

A soma utiliza `math.fsum`, operação aritmética elementar com melhor acumulação numérica. Não se usa `numpy.mean` ou equivalente na aplicação.

A mediana é o centro da sequência ordenada; para $n$ par, a média dos dois valores centrais. A moda preserva todos os empates na maior frequência. **Convenção:** todos os valores distintos resultam em lista vazia (amodal); a convenção difere de retornar todos os valores como modas e é explicitamente acomodada no teste contra `statistics.multimode`.

$$A=\max(x)-\min(x).$$

### 3.2 Variância e desvio padrão

$$\sigma^2=\frac{\sum_{i=1}^{n}(x_i-\bar{x})^2}{n},\qquad s^2=\frac{\sum_{i=1}^{n}(x_i-\bar{x})^2}{n-1}.$$

$$\sigma=\sqrt{\sigma^2},\qquad s=\sqrt{s^2}.$$

Implementação em duas passagens: centro e soma dos desvios quadráticos. Evita a forma $E[X^2]-E[X]^2$, sujeita a cancelamento quando valores são grandes e a dispersão pequena. A correção amostral exige $n\ge2$. A interface explicita `n` versus `n-1`. Descrever os registros filtrados como universo de referência não significa conhecer uma população de todas as pessoas.

### 3.3 Quartis e percentis

Adota-se o método linear tipo 7, correspondente a `numpy.percentile(..., method="linear")`. Na sequência ordenada com índices iniciados em zero:

$$h=(n-1)\frac{p}{100},\quad j=\lfloor h\rfloor,\quad g=h-j,$$
$$P_p=x_{(j)}+g\bigl(x_{(j+1)}-x_{(j)}\bigr).$$

Os extremos $p=0,100$ são tratados diretamente. $Q_1=P_{25}$, $Q_2=P_{50}$, $Q_3=P_{75}$, $IQR=Q_3-Q_1$. A ordenação não modifica a lista original.

### 3.4 Coeficiente de variação e assimetria

$$CV=100\frac{d}{|\bar{x}|},$$

em que $d$ é o desvio escolhido (amostral ou populacional). A convenção do denominador absoluto é documentada; com média zero o CV fica indefinido, não zero. Tem interpretação mais adequada em escalas de razão, como contagens positivas.

$$g_1=\frac{\frac1n\sum_i(x_i-\bar{x})^3}{\left(\frac1n\sum_i(x_i-\bar{x})^2\right)^{3/2}}.$$

A interpretação automática utiliza o terceiro momento padronizado populacional, comparado com `scipy.stats.skew(bias=True)`, em vez de deduzir assimetria somente por média versus mediana. Dispersão nula torna a assimetria indefinida.

### 3.5 Covariância e Pearson

$$s_{xy}=\frac{\sum_i(x_i-\bar{x})(y_i-\bar{y})}{n-1},\qquad \sigma_{xy}=\frac{\sum_i(x_i-\bar{x})(y_i-\bar{y})}{n}.$$

$$r=\frac{S_{xy}}{\sqrt{S_{xx}}\sqrt{S_{yy}}},\quad S_{xx}=\sum_i(x_i-\bar{x})^2,\quad S_{yy}=\sum_i(y_i-\bar{y})^2.$$

Os comprimentos devem coincidir. Pearson fica indefinido quando uma variável é constante; pequenos desvios numéricos fora de $[-1,1]$ são limitados ao intervalo matemático. Não se reporta significância ou causalidade.

## 4. Estatística descritiva interativa — M2

A tela `/descritiva` oferece seletor numérico/categórico, convenção amostral/populacional, número de classes e percentil adicional. A resposta identifica n válido e ausentes excluídos.

Para classes contínuas, calcula-se $f_j$, $f_j/n$, acumuladas absolutas e relativas. Classes são fechadas à esquerda e abertas à direita, exceto a última, que inclui o máximo. A densidade do histograma é

$$d_j=\frac{f_j}{n\Delta_j},$$

portanto a soma das áreas é 1. Para valores constantes, uma faixa artificial apenas de exibição evita largura nula. Frequências categóricas não recebem acumuladas com interpretação ordinal indevida. A tela permite barras/pizza e tabela completa; o gráfico categórico limita a 20 categorias sem alterar os cálculos.

Outliers são observações menores que $Q_1-1{,}5IQR$ ou maiores que $Q_3+1{,}5IQR$. Bigodes correspondem aos menores/maiores valores observados dentro dos limites, não aos limites teóricos. A contagem é completa; apenas a renderização pode limitar pontos. Atípicos não são automaticamente erros de dados.

## 5. Probabilidade e Monte Carlo — M3

### Lei dos Grandes Números

Experimentos de moeda justa ou dado justo. Para um evento escolhido:

$$\widehat{p}_N=\frac1N\sum_{i=1}^{N}I_i.$$

A interface controla experimento, resultado, repetições e semente; desenha a frequência acumulada e uma referência horizontal $p=1/2$ ou $p=1/6$. O erro não precisa diminuir a cada passo. Todos os lançamentos entram no resultado; a série desenhada é reduzida quando necessário.

### Teorema Central do Limite

A distribuição empírica filtrada é o universo do experimento. Sorteiam-se amostras independentes **com reposição**, calculando a média de cada amostra com a função própria. Sob esse mecanismo:

$$E(\bar{X})=\mu,\qquad \mathrm{DP}(\bar{X})=\frac{\sigma}{\sqrt{n}}.$$

O usuário varia $n$ e o número de amostras, comparando histograma original e histograma das médias. A curva Normal utiliza $(\mu,\sigma/\sqrt{n})$ do universo, não uma curva escolhida para parecer adequada. A semente permite reprodução; n=30 não é apresentado como garantia universal de aproximação. Com variável constante, a curva Normal não é traçada. Limite de dois milhões de sorteios por chamada para proteger a aplicação.

## 6. Distribuições candidatas — M4

A aplicação implementa **Normal e mais três famílias**, superando o mínimo de duas.

$$f_N(x)=\frac{1}{\sigma\sqrt{2\pi}}\exp\left[-\frac12\left(\frac{x-\mu}{\sigma}\right)^2\right].$$

Estimativas Normal: $\widehat\mu=\bar{x}$ e $\widehat\sigma=\sqrt{\sum_i(x_i-\bar{x})^2/n}$ (máxima verossimilhança).

$$f_E(x)=\lambda e^{-\lambda x},\quad x\ge0,\quad \widehat\lambda=1/\bar{x}.$$

Exponencial exige dados não negativos e média positiva, com origem fixada em zero.

$$f_U(x)=\frac1{b-a},\quad a\le x\le b.$$

Uniforme utiliza $\widehat a=\min(x)$ e $\widehat b=\max(x)$ e exige $a<b$.

$$P(X=k)=e^{-\lambda}\frac{\lambda^k}{k!},\quad k=0,1,\ldots,\quad \widehat\lambda=\bar{x}.$$

Poisson aceita somente inteiros não negativos; a massa é calculada em escala logarítmica com `math.lgamma` para evitar fatoriais gigantes. A comparação mostra massa em inteiros e frequências relativas, **não mistura probabilidade discreta com densidade contínua**. O histograma de classes continua disponível em tabela. A razão variância/média ajuda a discutir heterogeneidade, sem funcionar como teste formal de aderência.

PDFs contínuas são sobrepostas a histogramas de densidade. Nenhum p-valor ou selo de ajuste é inventado. Municípios heterogêneos podem gerar caudas e dispersão incompatíveis com todos esses modelos simples; reconhecer isso é parte do resultado.

## 7. Regressão linear e predição — M5

$$\widehat\beta_1=\frac{S_{xy}}{S_{xx}},\qquad \widehat\beta_0=\bar{y}-\widehat\beta_1\bar{x},\qquad\widehat y=\widehat\beta_0+\widehat\beta_1x.$$

$$R^2=1-\frac{\sum_i(y_i-\widehat y_i)^2}{\sum_i(y_i-\bar y)^2}.$$

Os coeficientes são calculados diretamente, sem `polyfit`, `linregress` ou sklearn na produção. As referências aparecem somente nos testes. $R^2$ é calculado pelos resíduos, e a identidade com $r^2$ é uma verificação, não a implementação principal.

X constante impede estimar a reta. Com Y constante, a reta horizontal permanece válida, mas Pearson e $R^2$ ficam indefinidos. Uma função genérica de $R^2$ não é truncada em zero para predições arbitrárias ruins.

A interface mostra equação, coeficientes, correlação, dispersão, resíduos, n válido e um campo de predição. A predição ocorre no servidor. X fora do intervalo observado recebe aviso de extrapolação. Y negativo, quando matematicamente produzido pela reta, é sinalizado como incompatível com o domínio, não truncado silenciosamente.

O scatter usa no máximo 2.000 pontos para renderização, preservando extremos; **todas as observações válidas** participam do ajuste. Cada ponto identifica município, UF e competência.

**Correlação não implica causalidade.** Quantidade e valor podem estar associados ao porte municipal. Nenhum controle de porte, inferência ecológica, teste causal, p-valor ou intervalo de confiança é indevidamente apresentado.

## 8. Validação e reprodutibilidade

Testes parametrizados comparam medidas com NumPy/SciPy/statistics, incluindo valores negativos, repetições, tamanhos pares/ímpares, constantes, sequências aleatórias reproduzíveis, pares alinhados, limites de percentis e dados não finitos. Casos indefinidos verificam exceções ou `None` explícito, não falsa equivalência.

Critério numérico declarado:

$$|a-b|\le\mathrm{atol}+\mathrm{rtol}|b|,\qquad\mathrm{atol}=\mathrm{rtol}=10^{-9}.$$

A suíte documenta suas asserções no código. Diferentes critérios estatísticos, como proximidade estocástica de uma frequência em Monte Carlo, **não** são confundidos com a tolerância de igualdade numérica.

`scripts/validar_nucleo.py` registra **26 comparações realmente executadas**, versões das bibliotecas, data e SHA-256 do código. [Consulte a evidência](documentacao/evidencias/validacao.json). A suíte completa inclui paginação, limites, filtros, CSV completo, falhas externas, API e prevenção de dupla contagem.

A suíte final registrou 219 testes aprovados, 95% de cobertura geral e no mínimo 90% em cada módulo do núcleo. Lint, TypeScript, build e 13 jornadas Playwright também foram executados; os testes de navegador usaram o BCB real por padrão.

## 9. Três descobertas — M6

O código implementa três análises reproduzíveis:

1. **Concentração municipal:** participação dos 50 maiores municípios (ou todos, se houver menos) no total pago PF+PJ do recorte, usando apenas o lado pagador.
2. **Centro da distribuição:** média, mediana e sua razão para quantidade de transações pagas por PF, acompanhadas do histograma e da ressalva sobre inferir forma apenas desses dois números.
3. **Associação quantidade/valor:** Pearson, $R^2$, coeficientes e n válido para quantidades versus valores pagos por PF, acompanhados da dispersão e das limitações de porte municipal.

Resultados calculados antes da interpretação, exclusivamente sobre as 66.837 observações válidas de 2025:

1. **Concentração municipal do valor pago.** Pergunta: qual parcela do valor pago PF+PJ está nos 50 maiores municípios? Resultado: **54,16%**. A visualização é o ranking da Visão Geral. Limitação: trata apenas o lado pagador e não mede renda, riqueza ou valores per capita.
2. **Centro da quantidade paga por PF.** Pergunta: quão distante está a média da mediana entre observações município-mês? Média **927.128,34**, mediana **202.135**, razão **4,5867**, com 66.837 observações e zero ausências. A visualização é o histograma/boxplot da Descritiva. Limitação: a distância entre média e mediana, isoladamente, não prova uma distribuição; o terceiro momento padronizado observado foi 32,1296.
3. **Quantidade versus valor pago por PF.** Pergunta: qual a associação linear no recorte? Pearson **r = 0,975617**, **R² = 0,951829**, inclinação **216,609975** e n=66.837. A visualização é a dispersão com reta de mínimos quadrados. Limitação: porte municipal afeta as duas variáveis; **correlação não implica causalidade** e o ajuste não garante predição fora do domínio.

Para reproduzir:

```bash
python scripts/verificar_fonte.py --competencia 202512
python scripts/gerar_evidencias.py --inicio 202501 --fim 202512
```

O [suplemento empírico](documentacao/resultados_bcb/DESCOBERTAS.md) e sua proveniência SHA-256 foram gerados pelos mesmos serviços analíticos da aplicação. O backend fornece cálculos e séries estruturadas; os gráficos são renderizados pelo front-end. Atípicos não foram removidos e nenhum dado ausente foi convertido em zero.

## 10. Interface e autoria

A tabela de rotas no README relaciona os módulos da aplicação. A pasta `documentacao/capturas/` contém imagens da interface conectada ao BCB.

O projeto foi desenvolvido individualmente por Miguel Fernando Flores Barreto, RA 72650465. O código, os testes e os resultados apresentados correspondem ao estado final analisado neste relatório.

## 11. Referências técnicas e de dados

- Banco Central do Brasil. [Estatísticas do Pix e metadados](https://dadosabertos.bcb.gov.br/dataset/pix).
- Banco Central do Brasil. [Recurso municipal](https://dadosabertos.bcb.gov.br/dataset/pix/resource/268e3bf6-b096-4006-83cd-813697012ece).
- Banco Central do Brasil. [Navegador da API](https://olinda.bcb.gov.br/olinda/servico/Pix_DadosAbertos/versao/v1/aplicacao).
- NumPy. [Percentile: convenção linear](https://numpy.org/doc/stable/reference/generated/numpy.percentile.html).
- SciPy. [Referência de estatística](https://docs.scipy.org/doc/scipy/reference/stats.html).
- Python. [statistics](https://docs.python.org/3/library/statistics.html) e [math](https://docs.python.org/3/library/math.html).
- Next.js. [Instalação e ambiente](https://nextjs.org/docs/app/getting-started/installation).
- FastAPI. [Concorrência e assincronicidade](https://fastapi.tiangolo.com/async/).
- shadcn/ui. [Gráficos baseados em Recharts](https://ui.shadcn.com/docs/components/radix/chart).

A consulta documental não substitui a verificação operacional da fonte e das dependências no ambiente de deploy.

**Escala financeira:** os quatro campos `VL_*` são “Volume financeiro em R$” no Swagger oficial consultado em 20/09/2026. A aplicação formata em reais e não aplica multiplicadores.
