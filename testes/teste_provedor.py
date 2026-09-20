"""Contrato OData testado com transporte controlado, sem rede."""

import httpx as cliente_http
import pytest as testes
from observatorio_api.catalogo import NUMERICAS
from observatorio_api.provedor_bcb import (
    FalhaFonte,
    ProvedorBCB,
    listar_competencias,
    normalizar_linhas,
)


def linha_oficial(codigo="5300108"):
    """Cria uma linha sintética no esquema externo, não dado real."""
    return {
        "AnoMes": "202512",
        "Municipio_Ibge": codigo,
        "Municipio": "Teste",
        "Estado_Ibge": 53,
        "Estado": "Distrito Federal",
        "Regiao": "Centro-Oeste",
        **{definicao["original"]: 10 for definicao in NUMERICAS.values()},
    }


def teste_normalizacao():
    linha = linha_oficial()
    linha["VL_PagadorPF"] = 12345.67
    linha["QT_PagadorPJ"] = None
    registros, qualidade = normalizar_linhas([linha], "202512")
    assert registros[0]["valor_pagador_pf"] == 12345.67
    assert registros[0]["quantidade_pagador_pj"] is None
    assert registros[0]["uf"] == "DF"
    assert qualidade["ausentes"]["quantidade_pagador_pj"] == 1
    assert len(NUMERICAS) == 12


def teste_qualidade():
    with testes.raises(FalhaFonte):
        normalizar_linhas([{}], "202512")
    with testes.raises(FalhaFonte):
        normalizar_linhas([linha_oficial(), linha_oficial()], "202512")
    with testes.raises(FalhaFonte):
        normalizar_linhas([linha_oficial()], "202501")
    linha = linha_oficial()
    linha["VL_PagadorPF"] = -1
    with testes.raises(FalhaFonte):
        normalizar_linhas([linha], "202512")
    registros, qualidade = normalizar_linhas([linha_oficial("0")], "202512")
    assert not registros and qualidade["identificadores_excluidos"] == 1


def teste_consulta_filtrada_e_cache():
    chamadas = []

    def responder(requisicao):
        """Simula a resposta integral prevista pelo contrato vigente."""
        chamadas.append(dict(requisicao.url.params))
        dados = [linha_oficial("5300108"), linha_oficial("3550308")]
        return cliente_http.Response(200, json={"value": dados})

    provedor = ProvedorBCB(cliente_http.MockTransport(responder))
    primeiro = provedor.obter_mes("202512")
    segundo = provedor.obter_mes("202512")
    assert primeiro is segundo
    assert len(chamadas) == 1
    assert chamadas[0]["$filter"] == "AnoMes eq 202512"
    assert "$skip" not in chamadas[0]
    assert len(primeiro["registros"]) == 2
    assert len(primeiro["proveniencia"]["sha256_normalizado"]) == 64


def teste_paginacao_inesperada():
    resposta = {"value": [linha_oficial()], "@odata.nextLink": "https://exemplo.invalid/proxima"}
    provedor = ProvedorBCB(
        cliente_http.MockTransport(lambda requisicao: cliente_http.Response(200, json=resposta))
    )
    with testes.raises(FalhaFonte, match="paginar"):
        provedor.obter_mes("202512")


def teste_falha_da_fonte_e_explicita():
    provedor = ProvedorBCB(
        cliente_http.MockTransport(lambda requisicao: cliente_http.Response(403))
    )
    with testes.raises(FalhaFonte):
        provedor.obter_mes("202512")
    assert not provedor.cache


def teste_janela():
    assert listar_competencias("202501", "202512") == [f"2025{mes:02d}" for mes in range(1, 13)]
    assert listar_competencias("202412", "202501") == ["202412", "202501"]
    for inicio, fim in [
        ("202500", "202501"),
        ("202502", "202501"),
        ("202401", "202512"),
        ("200001", "200012"),
    ]:
        with testes.raises(ValueError):
            listar_competencias(inicio, fim)
