# Observatório Pix Brasil

Aplicação acadêmica para exploração estatística dos dados públicos do Pix por município. O projeto reúne uma interface web, uma API de consulta e um núcleo matemático próprio para apresentar conceitos de estatística descritiva, probabilidade, distribuições e regressão sobre um conjunto real de abrangência nacional.

**Aplicação:** [observatorio-pix.floresdev.com.br](https://observatorio-pix.floresdev.com.br)

**Apresentação:** [youtu.be/VeD9sZRknd8](https://youtu.be/VeD9sZRknd8)

## Autoria

Trabalho individual desenvolvido por **Miguel Fernando Flores Barreto**, RA **72650465**.

GitHub: [@FernandoAurelius](https://github.com/FernandoAurelius)

## Fonte e recorte

Os dados pertencem ao conjunto [Estatísticas do Pix](https://dadosabertos.bcb.gov.br/dataset/pix), publicado pelo Banco Central do Brasil. O recurso analisado é [Transações Pix por Município](https://dadosabertos.bcb.gov.br/dataset/pix/resource/268e3bf6-b096-4006-83cd-813697012ece).

O estudo considera o período de janeiro a dezembro de 2025. Cada observação representa uma combinação entre município e competência mensal.

| Característica | Resultado |
|---|---:|
| Observações município-mês | 66.837 |
| Códigos municipais | 5.571 |
| Unidades federativas | 27 |
| Regiões | 5 |
| Competências mensais | 12 |
| Variáveis numéricas | 12 |
| Variáveis categóricas | 4 |

Os campos monetários representam volume financeiro em reais. Pagadores e recebedores são perspectivas distintas do fluxo e não são somados. As contagens mensais de pessoas não representam usuários únicos no ano. Registros sem identificação municipal válida foram desconsiderados, enquanto valores atípicos permaneceram nas análises.

## Funcionalidades

| Rota | Conteúdo |
|---|---|
| `/` | Panorama geral, evolução mensal, regiões e destaques municipais |
| `/explorar` | Consulta, ordenação, paginação e exportação dos registros |
| `/descritiva` | Medidas de centro, dispersão, quartis, frequências, histograma e boxplot |
| `/simulacao` | Lei dos Grandes Números e Teorema Central do Limite |
| `/distribuicoes` | Distribuições Normal, Exponencial, Uniforme e Poisson |
| `/regressao` | Correlação de Pearson, regressão linear, R² e predição |
| `/descobertas` | Interpretações calculadas para o recorte selecionado |
| `/metodologia` | Fórmulas, convenções e limites das análises |
| `/sobre` | Origem, abrangência e interpretação dos dados |

## Arquitetura

O frontend em Next.js apresenta tabelas e gráficos a partir de resultados estruturados fornecidos pela API FastAPI. A API consulta a fonte oficial, normaliza os registros, aplica os filtros e encaminha os dados ao núcleo estatístico em Python. Não há banco de dados local nem uma segunda implementação dos cálculos no navegador.

```text
Navegador
   │
   ▼
Next.js ──► FastAPI ──► Banco Central do Brasil
                  │
                  └──► Núcleo estatístico em Python
```

O núcleo implementa diretamente média, mediana, moda, amplitude, variâncias, desvios padrão, percentis, quartis, coeficiente de variação, frequências, assimetria, covariância, correlação, regressão e distribuições de probabilidade. NumPy, SciPy e `statistics` são utilizados apenas como referências independentes na suíte de testes.

## Resultados principais

No recorte completo de 2025:

1. Os 50 municípios com maior movimentação concentraram **54,16%** do valor pago por pessoas físicas e jurídicas.
2. A quantidade paga por pessoa física apresentou média de **927.128,34** transações e mediana de **202.135**, razão de **4,5867** entre as duas medidas.
3. Quantidade e valor pagos por pessoa física apresentaram correlação de Pearson de **0,975617** e R² de **0,951829**, com inclinação estimada de **216,609975**.

Esses resultados descrevem observações município-mês. Eles não demonstram causalidade, não representam indivíduos e não garantem predições fora do domínio observado.

## Qualidade

A validação compara as implementações matemáticas com NumPy, SciPy e `statistics` sob tolerância absoluta e relativa de `1e-9`. A suíte final registrou **219 testes Python aprovados**, **95% de cobertura total** e **14 jornadas de interface**. O projeto também passa por análise estática, verificação TypeScript e compilação de produção.

## Estrutura

| Caminho | Responsabilidade |
|---|---|
| `aplicacoes/api/` | API FastAPI e integração com o Banco Central |
| `aplicacoes/web/` | Interface Next.js e testes de navegador |
| `pacotes/nucleo_estatistico/` | Implementações matemáticas |
| `scripts/` | Auditorias e verificações auxiliares |
| `testes/` | Testes unitários e de integração |
| `RELATORIO.md` | Fundamentação metodológica e análise dos resultados |

## Licenças e referências

O código é distribuído sob a licença MIT. Os dados pertencem ao Banco Central do Brasil e seguem a licença indicada no catálogo oficial.

As principais referências técnicas são Python, FastAPI, Next.js, React, Recharts, NumPy e SciPy. As dependências completas e suas versões estão registradas nos arquivos de configuração do projeto.
