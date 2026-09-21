"""Entradas HTTP em português; execute uvicorn observatorio_api.principal:aplicacao."""

import csv as arquivo_csv
import io as fluxos
import os as sistema
import time as relogio
from collections import defaultdict as DicionarioPadrao
from collections import deque as Fila
from threading import Lock as Trava

from fastapi import FastAPI as AplicacaoHTTP
from fastapi import Request as Requisicao
from fastapi.exceptions import RequestValidationError as ErroValidacaoRequisicao
from fastapi.middleware.cors import CORSMiddleware as IntermediarioCORS
from fastapi.responses import JSONResponse as RespostaJSON
from fastapi.responses import Response as Resposta
from nucleo_estatistico import ajustar_distribuicao, simular_grandes_numeros, simular_limite_central

from . import servicos
from .catalogo import CATEGORICAS, FONTE, NUMERICAS
from .esquemas import (
    Analise,
    ConsultaDistribuicao,
    ConsultaLGN,
    ConsultaPanorama,
    ConsultaRegressao,
    ConsultaTabela,
    ConsultaTCL,
    Filtros,
)
from .provedor_bcb import FalhaFonte, ProvedorBCB

aplicacao = AplicacaoHTTP(
    docs_url="/api/documentacao",
    openapi_url="/api/openapi.json",
    redoc_url=None,
    title="Observatório Pix Brasil",
    version="1.0.0",
    description="API educacional: dados BCB + núcleo matemático próprio. Não afiliado ao BCB.",
)
origens_cors = [
    origem.strip()
    for origem in sistema.getenv(
        "ORIGENS_CORS", "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")
    if origem.strip()
]
aplicacao.add_middleware(
    IntermediarioCORS,
    allow_origins=origens_cors,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
provedor = ProvedorBCB()
acessos = DicionarioPadrao(Fila)
trava_acessos = Trava()


@aplicacao.middleware("http")
async def limitar_requisicoes(requisicao: Requisicao, proxima):
    """Limita chamadas por conexão/IP; proxy público deve aplicar limite próprio."""
    if requisicao.url.path.startswith("/api/") and requisicao.url.path != "/api/saude":
        endereco = requisicao.client.host if requisicao.client else "local"
        instante = relogio.monotonic()
        with trava_acessos:
            fila = acessos[endereco]
            while fila and instante - fila[0] > 60:
                fila.popleft()
            if len(fila) >= 120:
                return RespostaJSON(
                    status_code=429,
                    content={"mensagem": "Muitas consultas. Aguarde um minuto."},
                    headers={"Retry-After": "60"},
                )
            fila.append(instante)
            if len(acessos) > 10000:
                for chave in list(acessos):
                    if acessos[chave] and instante - acessos[chave][-1] > 60:
                        del acessos[chave]
    resposta = await proxima(requisicao)
    resposta.headers["X-Content-Type-Options"] = "nosniff"
    return resposta


@aplicacao.exception_handler(FalhaFonte)
async def tratar_fonte(requisicao: Requisicao, erro: FalhaFonte):
    """Não apresenta falhas da fonte como resultado vazio."""
    return RespostaJSON(
        status_code=503, content={"mensagem": str(erro), "tipo": "fonte_indisponivel"}
    )


@aplicacao.exception_handler(ValueError)
async def tratar_matematica(requisicao: Requisicao, erro: ValueError):
    """Comunica domínios matemáticos inválidos em português."""
    return RespostaJSON(
        status_code=422, content={"mensagem": str(erro), "tipo": "dominio_invalido"}
    )


@aplicacao.exception_handler(ErroValidacaoRequisicao)
async def tratar_validacao(requisicao: Requisicao, erro: ErroValidacaoRequisicao):
    """Evita depender de mensagens padrão em inglês de bibliotecas."""
    campos = [".".join(str(parte) for parte in item["loc"][1:]) for item in erro.errors()]
    return RespostaJSON(
        status_code=422,
        content={
            "mensagem": "Revise os parâmetros, seus tipos e limites: " + ", ".join(campos),
            "tipo": "parametros_invalidos",
        },
    )


def carregar(filtros: Filtros) -> tuple[dict, list[dict]]:
    """Obtém o período completo e aplica os filtros sem alterar a fonte."""
    conjunto = provedor.obter_periodo(filtros.inicio, filtros.fim)
    return conjunto, servicos.filtrar(conjunto, filtros)


def empacotar(conjunto, registros, resultado):
    """Acrescenta proveniência a toda resposta analítica."""
    return {"contexto": servicos.contexto(conjunto, registros), "resultado": resultado}


@aplicacao.get("/api/saude")
def consultar_saude():
    """Verifica o processo local; não afirma conectividade com a fonte."""
    return {"estado": "operacional", "modo": provedor.modo, "fonte_verificada": False}


@aplicacao.get("/api/catalogo")
def consultar_catalogo():
    """Retorna nomes internos, campos originais, unidades e limitações."""
    return {
        "numericas": NUMERICAS,
        "categoricas": CATEGORICAS,
        "fonte": FONTE,
        "modo": provedor.modo,
        "periodicidade": "mensal",
        "unidade_observacional": "município-mês",
        "aviso": "Dados agregados. Não somar os lados pagador e recebedor nem pessoas ao longo de meses.",
    }


@aplicacao.post("/api/filtros")
def consultar_filtros(consulta: Filtros):
    """Lista categorias realmente presentes no período, sem cobertura fixa."""
    conjunto, registros = carregar(consulta)
    todos = conjunto["registros"]
    municipios = {}
    for linha in todos:
        if (not consulta.regiao or linha["regiao"] == consulta.regiao) and (
            not consulta.uf or linha["uf"] == consulta.uf
        ):
            municipios[linha["codigo_municipio"]] = {
                "codigo": linha["codigo_municipio"],
                "nome": linha["municipio"],
                "uf": linha["uf"],
            }
    return empacotar(
        conjunto,
        registros,
        {
            "regioes": sorted({linha["regiao"] for linha in todos}),
            "estados": sorted(
                {
                    linha["uf"]
                    for linha in todos
                    if not consulta.regiao or linha["regiao"] == consulta.regiao
                }
            ),
            "municipios": sorted(municipios.values(), key=lambda linha: linha["nome"]),
        },
    )


@aplicacao.post("/api/panorama")
def consultar_panorama(consulta: ConsultaPanorama):
    """Totais, evolução e comparações calculados na perspectiva escolhida."""
    conjunto, registros = carregar(consulta)
    return empacotar(conjunto, registros, servicos.panorama(registros, consulta))


@aplicacao.post("/api/dados")
def consultar_dados(consulta: ConsultaTabela):
    """Pagina e ordena dados no servidor, sem exportar apenas a página atual."""
    conjunto, registros = carregar(consulta)
    if consulta.busca:
        registros = [
            linha
            for linha in registros
            if consulta.busca.casefold() in (linha["municipio"] + " " + linha["uf"]).casefold()
        ]
    permitidos = set(NUMERICAS) | set(CATEGORICAS) | {"competencia", "codigo_municipio"}
    if consulta.ordenar not in permitidos:
        raise ValueError("Coluna de ordenação inválida.")
    preenchidos = [linha for linha in registros if linha[consulta.ordenar] is not None]
    nulos = [linha for linha in registros if linha[consulta.ordenar] is None]
    ordenados = (
        sorted(preenchidos, key=lambda linha: linha[consulta.ordenar], reverse=consulta.decrescente)
        + nulos
    )
    inicio = (consulta.pagina - 1) * consulta.tamanho
    return empacotar(
        conjunto,
        registros,
        {
            "linhas": ordenados[inicio : inicio + consulta.tamanho],
            "total": len(ordenados),
            "pagina": consulta.pagina,
            "paginas": max(1, (len(ordenados) + consulta.tamanho - 1) // consulta.tamanho),
        },
    )


@aplicacao.post("/api/exportar")
def exportar_dados(consulta: Filtros):
    """Exporta todas as linhas do recorte em CSV UTF-8 BOM, protegido para planilhas."""
    conjunto, registros = carregar(consulta)
    colunas = ["competencia", "codigo_municipio", "municipio", "uf", "estado", "regiao"] + list(
        NUMERICAS
    )
    saida = fluxos.StringIO()
    escritor = arquivo_csv.DictWriter(saida, fieldnames=colunas, delimiter=";", lineterminator="\n")
    escritor.writeheader()
    for linha in registros:
        segura = {
            campo: (
                "'" + str(valor)
                if isinstance(valor, str) and valor.startswith(("=", "+", "-", "@", "\t", "\r"))
                else valor
            )
            for campo, valor in linha.items()
        }
        escritor.writerow(segura)
    return Resposta(
        content=("﻿" + saida.getvalue()).encode("utf-8"),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="pix_{consulta.inicio}_{consulta.fim}.csv"'
        },
    )


@aplicacao.post("/api/descritiva")
def consultar_descritiva(consulta: Analise):
    """Descritiva completa, frequências e boxplot do núcleo próprio."""
    conjunto, registros = carregar(consulta)
    return empacotar(conjunto, registros, servicos.analisar_descritiva(registros, consulta))


@aplicacao.post("/api/regressao")
def consultar_regressao(consulta: ConsultaRegressao):
    """Mínimos quadrados e predição calculados no backend."""
    conjunto, registros = carregar(consulta)
    return empacotar(conjunto, registros, servicos.analisar_regressao(registros, consulta))


@aplicacao.post("/api/distribuicoes")
def consultar_distribuicoes(consulta: ConsultaDistribuicao):
    """Estima parâmetros e compara densidades/massas na escala adequada."""
    conjunto, registros = carregar(consulta)
    valores, ausentes = servicos.extrair_numeros(registros, consulta.variavel)
    resultado = ajustar_distribuicao(valores, consulta.distribuicao, consulta.classes)
    resultado["ausentes_excluidos"] = ausentes
    return empacotar(conjunto, registros, resultado)


@aplicacao.post("/api/simulacoes/lgn")
def consultar_lgn(consulta: ConsultaLGN):
    """Executa Monte Carlo de moeda/dado; não exige dados do BCB."""
    return simular_grandes_numeros(
        consulta.repeticoes, consulta.experimento, consulta.resultado, consulta.semente
    )


@aplicacao.post("/api/simulacoes/tcl")
def consultar_tcl(consulta: ConsultaTCL):
    """Amostragem independente com reposição do universo filtrado."""
    conjunto, registros = carregar(consulta)
    valores, ausentes = servicos.extrair_numeros(registros, consulta.variavel)
    resultado = simular_limite_central(
        valores, consulta.tamanho_amostra, consulta.repeticoes, consulta.semente
    )
    resultado.pop("medias")
    resultado["ausentes_excluidos"] = ausentes
    return empacotar(conjunto, registros, resultado)


@aplicacao.post("/api/descobertas")
def consultar_descobertas(consulta: Filtros):
    """Gera três descobertas a partir dos números do recorte atual."""
    conjunto, registros = carregar(consulta)
    return empacotar(conjunto, registros, servicos.descobertas(registros, consulta))


@aplicacao.get("/api/validacao")
def consultar_validacao():
    """Descreve o critério de validação coberto pela suíte automatizada."""
    return {
        "metodo": "comparação com bibliotecas estatísticas de referência",
        "tolerancia_absoluta": 1e-9,
        "tolerancia_relativa": 1e-9,
    }


@aplicacao.post("/api/relatorio")
def exportar_relatorio(consulta: Filtros):
    """Exporta descobertas calculadas e proveniência em Markdown."""
    from .relatorios import escrever_resumo, preparar_evidencias

    conjunto, registros = carregar(consulta)
    evidencias = preparar_evidencias(conjunto, registros, consulta)
    return Resposta(
        content=escrever_resumo(evidencias).encode("utf-8"),
        media_type="text/markdown; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="descobertas_{consulta.inicio}_{consulta.fim}.md"'
        },
    )
