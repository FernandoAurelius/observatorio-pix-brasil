"""Aquisição OData paginada, normalização estrita e cache volátil limitado."""

import hashlib as resumos_digitais
import json as serializacao
import math as matematica
import os as sistema
import time as relogio
from collections import OrderedDict as DicionarioOrdenado
from concurrent.futures import ThreadPoolExecutor as ExecutorParalelo
from datetime import UTC
from datetime import datetime as DataHora
from threading import RLock as TravaReentrante

import httpx as cliente_http

from .catalogo import ENDERECO_BCB, FONTE, NUMERICAS, UNIDADES_FEDERATIVAS


class FalhaFonte(Exception):
    """Indisponibilidade ou quebra de contrato da fonte externa."""


def listar_competencias(inicio: str, fim: str) -> list[str]:
    """Valida AAAAMM, proíbe períodos futuros e limita a janela a 12 meses."""
    try:
        primeira, ultima = DataHora.strptime(inicio, "%Y%m"), DataHora.strptime(fim, "%Y%m")
    except ValueError as erro:
        raise ValueError("Informe competências válidas no formato AAAAMM.") from erro
    atual = DataHora.now(UTC).strftime("%Y%m")
    if len(inicio) != 6 or len(fim) != 6 or inicio < "202011" or inicio > fim or fim > atual:
        raise ValueError("Use de novembro/2020 até o mês atual, com início anterior ao fim.")
    quantidade = (ultima.year - primeira.year) * 12 + ultima.month - primeira.month + 1
    if quantidade > 12:
        raise ValueError("Cada consulta pode abranger no máximo 12 meses.")
    resultado = []
    for deslocamento in range(quantidade):
        ordinal = primeira.year * 12 + primeira.month - 1 + deslocamento
        resultado.append(f"{ordinal // 12:04d}{ordinal % 12 + 1:02d}")
    return resultado


def normalizar_linhas(linhas: list[dict], competencia: str) -> tuple[list[dict], dict]:
    """Mapeia o esquema externo para pt-BR, sem transformar ausentes em zero.

    Chave única: (competência,código IBGE). Duplicatas geram erro.
    Identificadores sem sete dígitos municipais são excluídos e contabilizados.
    Códigos são categorias, nunca medidas. Valores monetários são preservados
    numericamente (nenhum fator 1000/1000000 é aplicado implicitamente).
    """
    resultado, vistos, excluidos = [], set(), 0
    ausentes = {campo: 0 for campo in NUMERICAS}
    obrigatorios = {"AnoMes", "Municipio_Ibge", "Municipio", "Estado_Ibge", "Estado", "Regiao"} | {
        dados["original"] for dados in NUMERICAS.values()
    }
    for linha in linhas:
        faltantes = obrigatorios - set(linha)
        if faltantes:
            raise FalhaFonte(
                "Esquema da fonte mudou. Campos ausentes: " + ", ".join(sorted(faltantes))
            )
        codigo = str(linha["Municipio_Ibge"]).removesuffix(".0")
        if not codigo.isdigit() or len(codigo) != 7 or codigo.startswith("0"):
            excluidos += 1
            continue
        periodo = str(linha["AnoMes"]).removesuffix(".0")
        if periodo != competencia:
            raise FalhaFonte("A fonte devolveu registros de outra competência.")
        chave = (periodo, codigo)
        if chave in vistos:
            raise FalhaFonte(
                "A fonte devolveu chave município-mês duplicada. Nenhuma soma automática foi realizada."
            )
        vistos.add(chave)
        estado_codigo = str(linha["Estado_Ibge"]).removesuffix(".0")
        registro = {
            "competencia": periodo,
            "codigo_municipio": codigo,
            "municipio": str(linha["Municipio"]).strip(),
            "estado": str(linha["Estado"]).strip(),
            "uf": UNIDADES_FEDERATIVAS.get(estado_codigo, estado_codigo),
            "regiao": str(linha["Regiao"]).strip().title(),
        }
        for campo, definicao in NUMERICAS.items():
            valor = linha[definicao["original"]]
            if valor is None or valor == "":
                registro[campo] = None
                ausentes[campo] += 1
                continue
            try:
                numero = float(valor)
            except (TypeError, ValueError) as erro:
                raise FalhaFonte(f"Valor não numérico em {definicao['original']}.") from erro
            if isinstance(valor, bool) or not matematica.isfinite(numero) or numero < 0:
                raise FalhaFonte(f"Valor negativo, booleano ou não finito em {campo}.")
            if definicao["tipo"] == "discreta":
                if not numero.is_integer():
                    raise FalhaFonte(f"Contagem não inteira em {campo}.")
                registro[campo] = int(numero)
            else:
                registro[campo] = numero
        resultado.append(registro)
    return resultado, {
        "recebidos": len(linhas),
        "aceitos": len(resultado),
        "identificadores_excluidos": excluidos,
        "ausentes": ausentes,
    }


class ProvedorBCB:
    """Cliente da fonte oficial com retentativas e cache em memória.

    Configurações: CACHE_SEGUNDOS=86400; MAXIMO_MESES_CACHE=36.
    Nenhum banco ou armazenamento em disco é exigido.
    O histórico pode ser revisado pelo BCB; resumos SHA-256 identificam cada leitura.
    """

    def __init__(proprio, transporte=None):
        """Configura o cliente; permite transporte HTTP controlado nos testes."""
        proprio.modo = "bcb"
        proprio.transporte = transporte
        proprio.cache = DicionarioOrdenado()
        proprio.trava = TravaReentrante()
        proprio.travas_mes = {}
        proprio.validade = max(60, int(sistema.getenv("CACHE_SEGUNDOS", "86400")))
        proprio.maximo_cache = max(12, int(sistema.getenv("MAXIMO_MESES_CACHE", "36")))

    def obter_mes(proprio, competencia: str) -> dict:
        """Retorna um mês completo; consultas simultâneas compartilham a coleta."""
        listar_competencias(competencia, competencia)
        with proprio.trava:
            trava_mes = proprio.travas_mes.setdefault(competencia, TravaReentrante())
        with trava_mes:
            with proprio.trava:
                existente = proprio.cache.get(competencia)
                if existente and existente[0] > relogio.monotonic():
                    proprio.cache.move_to_end(competencia)
                    return existente[1]
            brutos = proprio.baixar_mes(competencia)
            registros, qualidade = normalizar_linhas(brutos, competencia)
            endereco = (
                f"{ENDERECO_BCB}?@DataBase='{competencia}'&$format=json"
                f"&$filter=AnoMes%20eq%20{competencia}&$orderby=Municipio_Ibge"
            )
            if not registros:
                raise FalhaFonte(
                    f"Não há registros municipais válidos para {competencia}; o mês pode não estar publicado."
                )
            resumo_digital = resumos_digitais.sha256(
                serializacao.dumps(registros, sort_keys=True, ensure_ascii=False).encode()
            ).hexdigest()
            conjunto = {
                "registros": registros,
                "proveniencia": {
                    "competencia": competencia,
                    "modo": proprio.modo,
                    "url": endereco,
                    "consultado_em": DataHora.now(UTC).isoformat(),
                    "sha256_normalizado": resumo_digital,
                    "qualidade": qualidade,
                },
            }
            with proprio.trava:
                proprio.cache[competencia] = (relogio.monotonic() + proprio.validade, conjunto)
                proprio.cache.move_to_end(competencia)
                while len(proprio.cache) > proprio.maximo_cache:
                    proprio.cache.popitem(last=False)
            return conjunto

    def baixar_mes(proprio, competencia: str) -> list[dict]:
        """Lê uma competência completa com o contrato OData vigente.

        A especificação oficial aceita ``$filter``, ``$orderby`` e ``$top``, mas
        não anuncia ``$skip``. Em 20/09/2026, ``$skip`` devolvia HTTP 500 e o
        recurso não emitia ``@odata.nextLink``. Por isso a coleta filtra a
        competência no servidor e recebe a resposta integral, cuja completude é
        auditada por chaves únicas na normalização. Três tentativas são feitas
        apenas para erros transitórios.
        """
        with cliente_http.Client(
            timeout=45, transport=proprio.transporte, follow_redirects=False
        ) as cliente:
            # O Olinda rejeita espaços codificados como ``+`` no $filter.
            # A competência já foi validada como seis algarismos, portanto a
            # montagem explícita mantém a URL fixa e não abre vetor de injeção.
            endereco_consulta = (
                f"{ENDERECO_BCB}?@DataBase='{competencia}'&$format=json"
                f"&$filter=AnoMes%20eq%20{competencia}&$orderby=Municipio_Ibge"
            )
            resposta = None
            for tentativa in range(3):
                try:
                    resposta = cliente.get(endereco_consulta)
                    if resposta.status_code in (429, 500, 502, 503, 504) and tentativa < 2:
                        relogio.sleep(0.5 * (2**tentativa))
                        continue
                    resposta.raise_for_status()
                    break
                except (cliente_http.TransportError, cliente_http.HTTPStatusError) as erro:
                    if tentativa == 2 or (
                        resposta is not None
                        and resposta.status_code not in (429, 500, 502, 503, 504)
                    ):
                        raise FalhaFonte(
                            "Não foi possível consultar o Banco Central. Verifique acesso à internet e disponibilidade da API."
                        ) from erro
                    relogio.sleep(0.5 * (2**tentativa))
            try:
                dados = resposta.json()
                linhas = dados["value"]
                if not isinstance(linhas, list):
                    raise TypeError("value não é lista")
            except (ValueError, KeyError, TypeError) as erro:
                raise FalhaFonte("A fonte não devolveu JSON OData no formato esperado.") from erro
            if dados.get("@odata.nextLink"):
                raise FalhaFonte(
                    "A fonte passou a paginar a resposta. Atualize o cliente antes de usar dados parciais."
                )
            return linhas

    def obter_periodo(proprio, inicio: str, fim: str) -> dict:
        """Reúne até 12 meses com três coletas simultâneas, sem persistência."""
        competencias = listar_competencias(inicio, fim)
        with ExecutorParalelo(max_workers=3) as executor:
            conjuntos = list(executor.map(proprio.obter_mes, competencias))
        return {
            "registros": [linha for conjunto in conjuntos for linha in conjunto["registros"]],
            "proveniencia": [conjunto["proveniencia"] for conjunto in conjuntos],
            "modo": proprio.modo,
            "fonte": FONTE,
            "inicio": inicio,
            "fim": fim,
        }
