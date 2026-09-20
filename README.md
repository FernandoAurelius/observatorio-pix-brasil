# Observatório Pix Brasil

Laboratório estatístico interativo desenvolvido para a disciplina de **Matemática e Estatística para Computação**. O projeto reúne dados públicos do Pix por município, cálculos estatísticos implementados em Python e uma interface web para exploração dos resultados.

## Autoria

**Miguel Fernando Flores Barreto**

**RA:** 72650465

**GitHub:** [@FernandoAurelius](https://github.com/FernandoAurelius)

## Fonte e recorte

Os dados são publicados pelo **Banco Central do Brasil** no conjunto [Estatísticas do Pix](https://dadosabertos.bcb.gov.br/dataset/pix), recurso [Transações Pix por Município](https://dadosabertos.bcb.gov.br/dataset/pix/resource/268e3bf6-b096-4006-83cd-813697012ece).

O estudo utiliza o período de janeiro a dezembro de 2025 e considera cada combinação de município e mês como uma observação. O conjunto analisado contém:

| Característica | Resultado |
|---|---:|
| Observações município-mês | 66.837 |
| Códigos municipais | 5.571 |
| Unidades federativas | 27 |
| Regiões | 5 |
| Competências | 12 |
| Variáveis numéricas | 12 |
| Variáveis categóricas | 4 |

Os campos monetários representam volume financeiro em reais (R$), conforme a documentação oficial. Pagadores e recebedores são perspectivas diferentes do fluxo e não devem ser somados. As contagens mensais de pessoas também não representam usuários únicos no ano.

Mais detalhes estão no [contrato dos dados](documentacao/CONTRATO_DADOS.md) e no [relatório metodológico](RELATORIO.md).

## Funcionalidades

| Rota | Conteúdo |
|---|---|
| `/` | Panorama, evolução, regiões, PF/PJ e destaques municipais |
| `/explorar` | Tabela pesquisável, ordenação, paginação e exportação CSV |
| `/descritiva` | Média, mediana, moda, dispersão, quartis, frequências, histograma e boxplot |
| `/simulacao` | Lei dos Grandes Números e Teorema Central do Limite |
| `/distribuicoes` | Normal, Exponencial, Uniforme e Poisson |
| `/regressao` | Correlação de Pearson, regressão linear, R² e predição |
| `/descobertas` | Três leituras estatísticas do recorte selecionado |
| `/metodologia` | Fórmulas, convenções e limites das análises |
| `/sobre` | Origem, abrangência e interpretação dos dados |

![Visão geral do observatório](documentacao/capturas/bcb_inicio.png)

![Interface em dispositivo móvel](documentacao/capturas/bcb_mobile.png)

## Arquitetura

```text
Navegador
   │
   ▼
Next.js ──► FastAPI ──► Banco Central do Brasil
                  │
                  └──► Núcleo estatístico em Python
```

- **Frontend:** Next.js, React, TypeScript, Tailwind CSS, componentes baseados em shadcn/ui, Lineicons e Recharts.
- **Backend:** FastAPI com aquisição, normalização, filtros e exportações.
- **Núcleo estatístico:** implementação própria das medidas, simulações, distribuições e regressão.
- **Dados:** fonte pública oficial do Banco Central do Brasil, sem banco de dados local.

## Execução local

Pré-requisitos: Python 3.13, Node.js 22 e npm.

```bash
python -m venv .venv
python -m pip install -r requirements.txt
python -m pip install -e . --no-deps
npm ci
```

No Windows PowerShell, ative o ambiente com:

```powershell
.venv\Scripts\Activate.ps1
```

Inicie a API:

```bash
uvicorn observatorio_api.principal:aplicacao --reload --host 127.0.0.1 --port 8000
```

Em outro terminal, inicie a interface:

```bash
npm run dev
```

A aplicação estará em `http://localhost:3000` e a documentação da API em `http://localhost:8000/api/documentacao`.

### Docker

```bash
cp .env.example .env
docker compose up --build
```

No PowerShell, use `Copy-Item .env.example .env` no lugar de `cp`. O Compose publica a interface em `http://127.0.0.1:3000` e a API em `http://127.0.0.1:8000`.

## Testes e qualidade

```bash
python -m pytest --cov --cov-report=term-missing
python scripts/validar_nucleo.py
npm run lint
npm run typecheck
npm run build
npm run test:e2e
```

Os testes numéricos comparam a implementação própria com NumPy, SciPy e `statistics`, usando tolerâncias explícitas de `1e-9`. Essas bibliotecas são referências de teste e não participam dos cálculos exibidos pela aplicação.

## Reprodução da análise de 2025

```bash
python scripts/verificar_fonte.py --competencia 202512
python scripts/auditar_dataset.py --inicio 202501 --fim 202512
python scripts/gerar_relatorio.py --inicio 202501 --fim 202512
```

Os resultados consolidados ficam em [documentacao/resultados_bcb](documentacao/resultados_bcb), acompanhados das evidências da auditoria em [documentacao/evidencias](documentacao/evidencias).

## Estrutura do repositório

```text
aplicacoes/api/                 FastAPI e integração com o BCB
aplicacoes/web/                 Next.js e testes de navegador
pacotes/nucleo_estatistico/     Implementações matemáticas
testes/                         Testes unitários e de integração
scripts/                        Reprodução e validação das análises
documentacao/                   Contrato, evidências, capturas e resultados
RELATORIO.md                    Discussão metodológica e conclusões
compose.yaml                    Execução em contêineres
```

## Licenças

O código é distribuído sob a licença MIT. Os dados pertencem ao Banco Central do Brasil e seguem a licença indicada no catálogo oficial. Dependências e atribuições adicionais estão registradas em [documentacao/TERCEIROS.md](documentacao/TERCEIROS.md).
