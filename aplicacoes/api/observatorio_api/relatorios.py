"""Relatórios reproduzíveis com evidências do mesmo serviço da aplicação."""

import json as serializacao
from datetime import UTC
from datetime import datetime as DataHora

from . import servicos
from .esquemas import Analise, ConsultaPanorama, ConsultaRegressao


def preparar_evidencias(conjunto: dict, registros: list[dict], filtros) -> dict:
    """Calcula o material do relatório sem copiar resultados de uma narrativa.

    Parâmetros: conjunto com proveniência, registros filtrados e Filtros.
    Retorno: contexto, três descobertas, painel, descritiva e regressão.
    Erros: ValueError quando o recorte não suporta as medidas exigidas.
    """
    parametros = filtros.model_dump(include={"inicio", "fim", "regiao", "uf", "municipio"})
    return {
        "gerado_em": DataHora.now(UTC).isoformat(),
        "contexto": servicos.contexto(conjunto, registros),
        "filtros": parametros,
        "descobertas": servicos.descobertas(registros, filtros),
        "panorama": servicos.panorama(registros, ConsultaPanorama(**parametros)),
        "descritiva": servicos.analisar_descritiva(registros, Analise(**parametros)),
        "regressao": servicos.analisar_regressao(registros, ConsultaRegressao(**parametros)),
    }


def escrever_resumo(evidencias: dict) -> str:
    """Renderiza Markdown com os resultados efetivos e seus limites.

    O relatório exportado é um suplemento analítico do RELATORIO.md.
    Não inclui identidades, matrículas ou links de vídeo inventados.
    """
    contexto = evidencias["contexto"]
    linhas = [
        "# Observatório Pix Brasil - resultados do recorte",
        "",
        "**Fonte: Banco Central do Brasil, API oficial.**",
        "",
        f"Gerado em: {evidencias['gerado_em']}",
        f"Competências: {contexto['inicio']} a {contexto['fim']}.",
        f"Unidade observacional: {contexto['unidade_observacional']}.",
        f"Observações: {contexto['registros']}; municípios distintos: {contexto['municipios']}.",
        "Campos quantitativos originais: 12; categorias utilizadas: município, estado, UF e região.",
        "Valores monetários em reais (R$), sem deflator ou multiplicador implícito.",
        "",
        "## Três descobertas calculadas",
        "",
    ]
    for indice, descoberta in enumerate(evidencias["descobertas"], 1):
        linhas += [
            f"### {indice}. {descoberta['titulo']}",
            "",
            descoberta["texto"],
            "",
            "**Limite de interpretação:** " + descoberta["ressalva"],
            "",
            "Visualização correspondente na aplicação: `" + descoberta["grafico"] + "`.",
            "",
        ]
    linhas += [
        "## Medidas e evidências",
        "",
        "Os resultados abaixo foram produzidos pelo mesmo núcleo usado nos gráficos.",
        "",
        "```json",
        serializacao.dumps(evidencias["descritiva"]["medidas"], ensure_ascii=False, indent=2),
        "```",
        "",
        "## Ressalvas metodológicas",
        "",
        "- Fluxo pagador e recebedor são perspectivas distintas, não parcelas a somar.",
        "- Pessoas contadas em diferentes meses não são usuários únicos anuais.",
        "- Porte municipal pode explicar associações; correlação não implica causalidade.",
        "- Unidade município-mês não representa indivíduos; repetição no tempo não é independência inferencial.",
        "- A documentação do recurso se refere à liquidação no SPI; cobertura não equivale a qualquer fluxo Pix.",
        "- Dados históricos podem ser revisados na fonte; SHA-256 identifica a versão normalizada consultada.",
        "",
        "## Proveniência",
        "",
        "```json",
        serializacao.dumps(contexto, ensure_ascii=False, indent=2),
        "```",
        "",
        "Fonte original: https://dadosabertos.bcb.gov.br/dataset/pix",
        "",
        "Consulte RELATORIO.md para fórmulas, validação, descrição dos módulos e limitações.",
    ]
    return "\n".join(linhas) + "\n"
