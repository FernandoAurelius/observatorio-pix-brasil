"""Testes locais da API com uma amostra controlada."""

import pytest as testes
from observatorio_api import servicos
from observatorio_api.esquemas import ConsultaPanorama, ConsultaRegressao


@testes.mark.parametrize(
    "rota,corpo",
    [
        ("panorama", {}),
        ("dados", {}),
        ("descritiva", {}),
        ("descritiva", {"variavel": "regiao"}),
        ("regressao", {"valor_predicao": 100}),
        ("distribuicoes", {"distribuicao": "normal"}),
        ("distribuicoes", {"distribuicao": "exponencial"}),
        ("distribuicoes", {"distribuicao": "uniforme"}),
        ("distribuicoes", {"distribuicao": "poisson"}),
        ("simulacoes/tcl", {"repeticoes": 50}),
        ("descobertas", {}),
        ("filtros", {}),
    ],
)
def teste_rotas(cliente, rota, corpo):
    resposta = cliente.post("/api/" + rota, json=corpo)
    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["contexto"]["modo"] == "bcb"
    assert resposta.json()["contexto"]["registros"] == 1200
    assert resposta.json()["contexto"]["atende_volume_minimo"] is True
    assert "NaN" not in resposta.text and "Infinity" not in resposta.text


def teste_rotas_sem_dados(cliente):
    assert cliente.get("/api/saude").json()["modo"] == "bcb"
    assert len(cliente.get("/api/catalogo").json()["numericas"]) == 12
    assert cliente.post("/api/simulacoes/lgn", json={}).status_code == 200
    assert cliente.get("/api/validacao").status_code == 200


def teste_cors_local_restrito(cliente):
    resposta = cliente.options(
        "/api/catalogo",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert resposta.status_code == 200
    assert resposta.headers["access-control-allow-origin"] == "http://localhost:3000"
    resposta_bloqueada = cliente.options(
        "/api/catalogo",
        headers={
            "Origin": "https://origem.invalid",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert "access-control-allow-origin" not in resposta_bloqueada.headers


def teste_validacao_entradas(cliente):
    for corpo in [
        {"classes": 101},
        {"inicio": "abc"},
        {"variavel": "SELECT *"},
        {"percentual": -2},
    ]:
        resposta = cliente.post("/api/descritiva", json=corpo)
        assert resposta.status_code == 422
        assert "mensagem" in resposta.json()
    assert cliente.post("/api/simulacoes/lgn", json={"resultado": 6}).status_code == 422
    assert (
        cliente.post(
            "/api/simulacoes/tcl", json={"tamanho_amostra": 1000, "repeticoes": 10000}
        ).status_code
        == 422
    )


def teste_vazio_e_paginacao(cliente):
    resposta = cliente.post("/api/dados", json={"municipio": "0000000"})
    assert resposta.json()["resultado"]["total"] == 0
    resposta = cliente.post("/api/descritiva", json={"municipio": "0000000"})
    assert resposta.status_code == 422
    resposta = cliente.post("/api/dados", json={"pagina": 2, "tamanho": 10})
    assert len(resposta.json()["resultado"]["linhas"]) == 10
    assert resposta.json()["resultado"]["paginas"] == 120


def teste_exportacao_completa(cliente):
    resposta = cliente.post("/api/exportar", json={"uf": "GO"})
    assert resposta.status_code == 200
    assert "pix_202512_202512.csv" in resposta.headers["content-disposition"]
    assert len(resposta.text.splitlines()) == 241


def teste_totais_sem_dupla_contagem(registros_teste):
    dados = registros_teste
    painel = servicos.panorama(dados, ConsultaPanorama())
    esperado = sum(linha["valor_pagador_pf"] + linha["valor_pagador_pj"] for linha in dados)
    assert painel["totais"]["valor"] == testes.approx(esperado)
    assert "pessoas_unicas" not in painel["totais"]


def teste_exclusao_pareada_e_extrapolacao(registros_teste):
    dados = registros_teste[:5]
    dados[0]["valor_pagador_pf"] = None
    dados[1]["quantidade_pagador_pf"] = None
    resultado = servicos.analisar_regressao(dados, ConsultaRegressao(valor_predicao=-1))
    assert resultado["modelo"]["quantidade"] == 3
    assert resultado["ausentes_excluidos"] == 2
    assert resultado["predicao"]["extrapolacao"] is True
