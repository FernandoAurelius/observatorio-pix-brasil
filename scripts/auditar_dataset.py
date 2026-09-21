"""Audita o recorte real do BCB e grava um resumo reproduzível, sem cache bruto."""

import sys as sistema
from pathlib import Path as Caminho

RAIZ = Caminho(__file__).resolve().parents[1]
sistema.path[:0] = [str(RAIZ / "pacotes"), str(RAIZ / "aplicacoes/api")]

import argparse as argumentos
from datetime import UTC
from datetime import datetime as DataHora

from observatorio_api.catalogo import CATEGORICAS, NUMERICAS
from observatorio_api.provedor_bcb import ProvedorBCB


def auditar(inicio: str, fim: str) -> dict:
    """Coleta e verifica volume, cobertura, ausências, chaves, tipos e sinais.

    Args:
        inicio: Primeira competência no formato AAAAMM.
        fim: Última competência inclusiva no formato AAAAMM.
    Returns:
        Dicionário JSON-compatível com contagens e aprovação do recorte.
    Raises:
        FalhaFonte: Se o BCB estiver indisponível ou quebrar o contrato.
        ValueError: Se o período for inválido ou o recorte não tiver linhas.
    """
    conjunto = ProvedorBCB().obter_periodo(inicio, fim)
    registros = conjunto["registros"]
    if not registros:
        raise ValueError("O recorte não contém observações válidas.")
    chaves = [(linha["competencia"], linha["codigo_municipio"]) for linha in registros]
    ausentes = {campo: sum(linha[campo] is None for linha in registros) for campo in NUMERICAS}
    negativos = {
        campo: sum(linha[campo] is not None and linha[campo] < 0 for linha in registros)
        for campo in NUMERICAS
    }
    discretas = [campo for campo, definicao in NUMERICAS.items() if definicao["tipo"] == "discreta"]
    tipos_incorretos = {
        campo: sum(
            linha[campo] is not None
            and (
                isinstance(linha[campo], bool)
                or (campo in discretas and not isinstance(linha[campo], int))
                or (campo not in discretas and not isinstance(linha[campo], float))
            )
            for linha in registros
        )
        for campo in NUMERICAS
    }
    resumo = {
        "consultado_em": DataHora.now(UTC).isoformat(),
        "fonte": conjunto["fonte"],
        "inicio": inicio,
        "fim": fim,
        "registros": len(registros),
        "municipios": len({linha["codigo_municipio"] for linha in registros}),
        "estados": len({linha["uf"] for linha in registros}),
        "regioes": len({linha["regiao"] for linha in registros}),
        "competencias": sorted({linha["competencia"] for linha in registros}),
        "variaveis_numericas": len(NUMERICAS),
        "variaveis_categoricas": len(CATEGORICAS),
        "ausentes_por_variavel": ausentes,
        "ausentes_total": sum(ausentes.values()),
        "duplicidades_municipio_mes": len(chaves) - len(set(chaves)),
        "tipos_incorretos_por_variavel": tipos_incorretos,
        "tipos_incorretos_total": sum(tipos_incorretos.values()),
        "municipios_sem_identificacao_aceitos": sum(
            not linha["codigo_municipio"] or not linha["municipio"].strip() for linha in registros
        ),
        "identificadores_nao_municipais_excluidos": sum(
            item["qualidade"]["identificadores_excluidos"] for item in conjunto["proveniencia"]
        ),
        "negativos_por_variavel": negativos,
        "negativos_total": sum(negativos.values()),
        "competencias_duplicadas": len(conjunto["proveniencia"])
        - len({item["competencia"] for item in conjunto["proveniencia"]}),
        "regra_limpeza": (
            "Excluem-se somente linhas sem código IBGE municipal válido de sete dígitos; "
            "ausências numéricas seriam preservadas e contabilizadas; nenhuma observação "
            "válida ou valor atípico é removido."
        ),
    }
    resumo["atende_requisitos"] = (
        resumo["registros"] >= 1000
        and resumo["variaveis_numericas"] >= 4
        and resumo["variaveis_categoricas"] >= 2
        and resumo["duplicidades_municipio_mes"] == 0
        and resumo["tipos_incorretos_total"] == 0
        and resumo["negativos_total"] == 0
        and resumo["competencias"] == [f"2025{mes:02d}" for mes in range(1, 13)]
    )
    return resumo


def imprimir_tabela(resumo: dict) -> None:
    """Imprime a tabela pedida para conferência no terminal."""
    linhas = [
        ("Registros", resumo["registros"]),
        ("Municípios", resumo["municipios"]),
        ("Estados/UFs", resumo["estados"]),
        ("Regiões", resumo["regioes"]),
        ("Competências", ", ".join(resumo["competencias"])),
        ("Variáveis numéricas", resumo["variaveis_numericas"]),
        ("Variáveis categóricas", resumo["variaveis_categoricas"]),
        ("Valores ausentes", resumo["ausentes_total"]),
        ("Duplicidades município-mês", resumo["duplicidades_municipio_mes"]),
        ("Tipos incorretos", resumo["tipos_incorretos_total"]),
        ("Valores negativos", resumo["negativos_total"]),
        ("Linhas N/D excluídas", resumo["identificadores_nao_municipais_excluidos"]),
        ("Requisitos atendidos", "sim" if resumo["atende_requisitos"] else "não"),
    ]
    print("| Métrica | Resultado |")
    print("|---|---:|")
    for nome, valor in linhas:
        print(f"| {nome} | {valor} |")


if __name__ == "__main__":
    analisador = argumentos.ArgumentParser(description=__doc__)
    analisador.add_argument("--inicio", default="202501")
    analisador.add_argument("--fim", default="202512")
    opcoes = analisador.parse_args()
    resultado = auditar(opcoes.inicio, opcoes.fim)
    imprimir_tabela(resultado)
    sistema.exit(0 if resultado["atende_requisitos"] else 1)
