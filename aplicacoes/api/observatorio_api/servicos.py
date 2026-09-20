"""Orquestra os dados; toda medida exibida vem do núcleo próprio."""

import math as matematica
import random as aleatoriedade

from nucleo_estatistico import (
    detectar_atipicos,
    frequencias_categoricas,
    histograma,
    media,
    mediana,
    percentil,
    predizer,
    regressao_linear,
    resumo,
    soma,
)

from .catalogo import CATEGORICAS, NUMERICAS


def filtrar(conjunto: dict, filtros) -> list[dict]:
    """Filtra sem modificar o cache; categorias são comparadas exatamente."""
    return [
        linha
        for linha in conjunto["registros"]
        if (not filtros.regiao or linha["regiao"] == filtros.regiao)
        and (not filtros.uf or linha["uf"] == filtros.uf)
        and (not filtros.municipio or linha["codigo_municipio"] == filtros.municipio)
    ]


def contexto(conjunto: dict, registros: list[dict]) -> dict:
    """Expõe modo, n, granularidade, cobertura observada e proveniência."""
    return {
        "modo": conjunto["modo"],
        "fonte": conjunto["fonte"],
        "inicio": conjunto["inicio"],
        "fim": conjunto["fim"],
        "registros": len(registros),
        "municipios": len({linha["codigo_municipio"] for linha in registros}),
        "unidade_observacional": "município-mês",
        "proveniencia": conjunto["proveniencia"],
        "atende_volume_minimo": len(registros) >= 1000,
        "aviso": "Cobertura municipal observada no recurso do BCB, não cobertura garantida de todas as transações Pix.",
    }


def extrair_numeros(registros: list[dict], variavel: str) -> tuple[list[float], int]:
    """Extrai uma variável permitida, contando explicitamente ausentes."""
    if variavel not in NUMERICAS:
        raise ValueError("Selecione uma variável numérica do dicionário.")
    valores = [linha[variavel] for linha in registros if linha[variavel] is not None]
    if not valores:
        raise ValueError("Nenhuma observação numérica válida para os filtros selecionados.")
    return valores, len(registros) - len(valores)


def analisar_descritiva(registros: list[dict], consulta) -> dict:
    """Calcula numéricas e categóricas sem atribuir média a categorias."""
    if consulta.variavel in CATEGORICAS:
        if not registros:
            raise ValueError("Nenhum registro para os filtros selecionados.")
        frequencias = frequencias_categoricas(linha[consulta.variavel] for linha in registros)
        return {
            "tipo": "categorica",
            "frequencias": frequencias,
            "quantidade": len(registros),
            "interpretacao": "Barras representam número de observações município-mês, não valor ou volume de Pix.",
        }
    valores, ausentes = extrair_numeros(registros, consulta.variavel)
    caixa = detectar_atipicos(valores)
    # A amostra visual inclui extremos; as medidas continuam usando todas as observações.
    ordenados_atipicos = sorted(caixa["valores"])
    passo = max(1, matematica.ceil(len(ordenados_atipicos) / 200))
    caixa["valores"] = ordenados_atipicos[::passo]
    caixa.pop("indices")
    return {
        "tipo": "numerica",
        "medidas": resumo(valores, consulta.amostral),
        "frequencias": histograma(valores, consulta.classes),
        "caixa": caixa,
        "percentil": {
            "percentual": consulta.percentual,
            "valor": percentil(valores, consulta.percentual),
        },
        "ausentes_excluidos": ausentes,
        "variavel": NUMERICAS[consulta.variavel],
    }


def dividir_seguro(numerador: float, denominador: float) -> float | None:
    """Retorna a razão, ou None quando o denominador é zero."""
    return numerador / denominador if denominador else None


def agregar_fluxo(registros: list[dict], papel: str, pessoa: str) -> dict:
    """Soma apenas lados selecionados do fluxo; pessoas não são somadas."""
    pessoas = ("pf", "pj") if pessoa == "todos" else (pessoa,)
    campos_valor = [f"valor_{papel}_{tipo}" for tipo in pessoas]
    campos_quantidade = [f"quantidade_{papel}_{tipo}" for tipo in pessoas]
    completos = [
        linha
        for linha in registros
        if all(linha[campo] is not None for campo in campos_valor + campos_quantidade)
    ]
    valor = soma(linha[campo] for linha in completos for campo in campos_valor)
    quantidade = soma(linha[campo] for linha in completos for campo in campos_quantidade)
    return {
        "valor": valor,
        "quantidade": quantidade,
        "ticket_medio": dividir_seguro(valor, quantidade),
        "excluidos": len(registros) - len(completos),
    }


def panorama(registros: list[dict], consulta) -> dict:
    """Agrega fluxos por mês, região e município na perspectiva escolhida."""

    def agrupar(campo):
        """Agrupa linhas por uma categoria sem calcular estatísticas prontas."""
        grupos = {}
        for linha in registros:
            grupos.setdefault(linha[campo], []).append(linha)
        return grupos

    meses = [
        {"competencia": chave, **agregar_fluxo(linhas, consulta.papel, consulta.pessoa)}
        for chave, linhas in sorted(agrupar("competencia").items())
    ]
    regioes = [
        {"regiao": chave, **agregar_fluxo(linhas, consulta.papel, consulta.pessoa)}
        for chave, linhas in agrupar("regiao").items()
    ]
    municipios = [
        {
            "codigo_municipio": chave,
            "municipio": linhas[0]["municipio"],
            "uf": linhas[0]["uf"],
            **agregar_fluxo(linhas, consulta.papel, consulta.pessoa),
        }
        for chave, linhas in agrupar("codigo_municipio").items()
    ]
    municipios.sort(key=lambda linha: linha["valor"], reverse=True)
    total = agregar_fluxo(registros, consulta.papel, consulta.pessoa)
    maiores = min(50, len(municipios))
    concentracao = dividir_seguro(
        soma(linha["valor"] for linha in municipios[:maiores]), total["valor"]
    )
    return {
        "totais": total,
        "meses": meses,
        "regioes": sorted(regioes, key=lambda linha: linha["valor"], reverse=True),
        "municipios": municipios,
        "pessoas": [
            {"pessoa": tipo.upper(), **agregar_fluxo(registros, consulta.papel, tipo)}
            for tipo in ("pf", "pj")
        ],
        "concentracao": {"quantidade": maiores, "participacao": concentracao},
        "papel": consulta.papel,
        "pessoa": consulta.pessoa,
        "aviso": "Ticket médio = soma de valores / soma de transações, não média simples dos tickets municipais. Valores nominais; sem correção monetária.",
    }


def analisar_regressao(registros: list[dict], consulta) -> dict:
    """Mantém pares alinhados; amostragem limita somente a renderização."""
    if consulta.variavel_x not in NUMERICAS or consulta.variavel_y not in NUMERICAS:
        raise ValueError("Escolha duas variáveis numéricas do dicionário.")
    completos = [
        linha
        for linha in registros
        if linha[consulta.variavel_x] is not None and linha[consulta.variavel_y] is not None
    ]
    valores_x = [linha[consulta.variavel_x] for linha in completos]
    valores_y = [linha[consulta.variavel_y] for linha in completos]
    modelo = regressao_linear(valores_x, valores_y)
    indices = list(range(len(completos)))
    if len(indices) > 2000:
        extremos = {
            min(indices, key=lambda indice: valores_x[indice]),
            max(indices, key=lambda indice: valores_x[indice]),
            min(indices, key=lambda indice: valores_y[indice]),
            max(indices, key=lambda indice: valores_y[indice]),
        }
        indices = sorted(
            extremos
            | set(
                aleatoriedade.Random(42).sample(
                    [indice for indice in indices if indice not in extremos], 2000 - len(extremos)
                )
            )
        )
    pontos = [
        {
            "valor_x": valores_x[indice],
            "valor_y": valores_y[indice],
            "residuo": modelo["residuos"][indice],
            "previsto": modelo["previstos"][indice],
            "municipio": completos[indice]["municipio"],
            "uf": completos[indice]["uf"],
            "competencia": completos[indice]["competencia"],
        }
        for indice in indices
    ]
    modelo.pop("residuos")
    modelo.pop("previstos")
    predicao = None
    if consulta.valor_predicao is not None:
        predicao = {
            "valor_x": consulta.valor_predicao,
            "valor_y": predizer(
                consulta.valor_predicao, modelo["intercepto"], modelo["inclinacao"]
            ),
            "extrapolacao": not modelo["minimo_x"] <= consulta.valor_predicao <= modelo["maximo_x"],
        }
    return {
        "modelo": modelo,
        "pontos": pontos,
        "ausentes_excluidos": len(registros) - len(completos),
        "reta": [
            {
                "valor_x": valor,
                "valor_y": predizer(valor, modelo["intercepto"], modelo["inclinacao"]),
            }
            for valor in (modelo["minimo_x"], modelo["maximo_x"])
        ],
        "predicao": predicao,
        "amostragem_visual": len(indices) < len(completos),
        "interpretacao": f"Uma unidade adicional de X está associada a {modelo['inclinacao']:.6g} unidades de Y na reta ajustada. "
        "O intercepto representa Y estimado em X=0; pode não ter interpretação substantiva fora do domínio observado. "
        "Municípios maiores podem apresentar X e Y maiores. Observações do mesmo município em meses diferentes não são tratadas como independentes para inferência.",
    }


def descobertas(registros: list[dict], filtros) -> list[dict]:
    """Produz três descobertas computadas no recorte, sem números fixos."""
    from .esquemas import ConsultaPanorama, ConsultaRegressao

    base = filtros.model_dump(include={"inicio", "fim", "regiao", "uf", "municipio"})
    painel = panorama(registros, ConsultaPanorama(**base))
    concentracao = painel["concentracao"]
    valores, ausentes = extrair_numeros(registros, "quantidade_pagador_pf")
    centro, mediano = media(valores), mediana(valores)
    try:
        ajuste = analisar_regressao(registros, ConsultaRegressao(**base))["modelo"]
        texto_ajuste = (
            f"r={ajuste['pearson']:.6f}; R²={ajuste['r_quadrado']:.6f}; n={ajuste['quantidade']}."
            if ajuste["pearson"] is not None
            else "Resposta constante: r e R² indefinidos."
        )
    except ValueError as erro:
        texto_ajuste = str(erro)
        ajuste = None
    participacao = concentracao["participacao"]
    return [
        {
            "titulo": "Concentração municipal do valor pago",
            "texto": f"Os {concentracao['quantidade']} municípios com maior valor pago concentram {100 * participacao:.2f}% do valor do recorte."
            if participacao is not None
            else "Sem valor positivo no recorte.",
            "evidencia": concentracao,
            "grafico": "/",
            "ressalva": "Soma PF+PJ somente no lado pagador. Não mede riqueza nem renda por habitante.",
        },
        {
            "titulo": "Média e mediana das transações pagas por PF",
            "texto": f"Média={centro:.6g}; mediana={mediano:.6g}; n={len(valores)} município-mês; {ausentes} ausentes excluídos.",
            "evidencia": {
                "media": centro,
                "mediana": mediano,
                "razao": dividir_seguro(centro, mediano),
                "n": len(valores),
            },
            "grafico": "/descritiva",
            "ressalva": "Comparar com o histograma e com a assimetria; diferença entre média e mediana isoladamente não comprova um formato.",
        },
        {
            "titulo": "Associação entre quantidade e valor pago por PF",
            "texto": texto_ajuste,
            "evidencia": ajuste,
            "grafico": "/regressao",
            "ressalva": "Valor e quantidade compartilham efeito do porte municipal. Ajuste descritivo, não efeito causal ou garantia de previsão.",
        },
    ]
