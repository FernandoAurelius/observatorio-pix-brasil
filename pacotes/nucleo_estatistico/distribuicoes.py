"""Densidades contínuas e massa discreta: fórmulas elementares, sem SciPy."""

import math as matematica

from .descritiva import desvio_padrao, histograma, media, variancia
from .validacao import validar_numeros


def densidade_normal(valor: float, centro: float, desvio: float) -> float:
    """Calcula exp(-0,5*((x-μ)/σ)^2)/(σ*√(2π)).

    Parâmetros: valor=x, centro=μ, desvio=σ>0, todos finitos.
    Retorno: densidade (não probabilidade pontual). Erros: ValueError se σ<=0.
    """
    valor, centro, desvio = validar_numeros([valor, centro, desvio])
    if desvio <= 0:
        raise ValueError("A Normal exige desvio padrão positivo.")
    return matematica.exp(-0.5 * ((valor - centro) / desvio) ** 2) / (
        desvio * matematica.sqrt(2 * matematica.pi)
    )


def densidade_exponencial(valor: float, taxa: float) -> float:
    """Retorna λ*exp(-λ*x) para x>=0; zero para x<0.

    Parâmetros: valor finito e taxa=λ>0 finita. Retorno: densidade.
    Erros: ValueError para taxa não positiva. Localização fixada em zero.
    """
    valor, taxa = validar_numeros([valor, taxa])
    if taxa <= 0:
        raise ValueError("A Exponencial exige taxa positiva.")
    return 0.0 if valor < 0 else taxa * matematica.exp(-taxa * valor)


def densidade_uniforme(valor: float, inferior: float, superior: float) -> float:
    """Retorna 1/(b-a) no intervalo [a,b] e zero fora dele.

    Parâmetros: valor=x, inferior=a, superior=b, todos finitos e a<b.
    Retorno: densidade. Erros: ValueError quando os limites não crescem.
    """
    valor, inferior, superior = validar_numeros([valor, inferior, superior])
    if superior <= inferior:
        raise ValueError("A Uniforme exige limite superior maior que o inferior.")
    return 1 / (superior - inferior) if inferior <= valor <= superior else 0.0


def massa_poisson(valor: float, intensidade: float) -> float:
    """Calcula P(X=k)=exp(-λ)*λ^k/k! no domínio inteiro não negativo.

    Parâmetros: valor=k finito; intensidade=λ>=0 finita.
    Retorno: probabilidade pontual, zero para k negativo ou não inteiro.
    λ=0 é a distribuição degenerada em k=0. Usa log-gama para evitar
    estouro do fatorial. Erros: ValueError para λ negativo ou não finito.
    """
    valor, intensidade = validar_numeros([valor, intensidade])
    if intensidade < 0:
        raise ValueError("A intensidade de Poisson deve ser não negativa.")
    if valor < 0 or not valor.is_integer():
        return 0.0
    if intensidade == 0:
        return 1.0 if valor == 0 else 0.0
    return min(
        1.0,
        matematica.exp(
            -intensidade + valor * matematica.log(intensidade) - matematica.lgamma(valor + 1)
        ),
    )


def ajustar_distribuicao(valores, distribuicao: str, classes: int = 25) -> dict:
    """Estima parâmetros e prepara uma comparação visual honesta.

    Parâmetros: valores finitos; distribuicao em normal/exponencial/uniforme/poisson.
    Normal: μ=média, σ=desvio populacional (máxima verossimilhança).
    Exponencial: λ=1/média, suporte >=0. Uniforme: a=mínimo,b=máximo.
    Poisson: λ=média, somente inteiros não negativos.
    Retorno: histograma normalizado, pontos da curva, parâmetros e ressalvas.
    Contínuas usam densidade; Poisson usa frequências pontuais e massa,
    jamais sobrepõe uma massa pontual a um histograma de densidade.
    Erros: ValueError para distribuição desconhecida ou suporte incompatível.
    """
    numeros = validar_numeros(valores, 2)
    menor, maior, centro = min(numeros), max(numeros), media(numeros)
    avisos = [
        "Inspeção visual não comprova uma distribuição. Não foram calculados p-valores de aderência.",
        "Municípios têm portes diferentes. Uma mistura heterogênea pode ajustar mal qualquer modelo simples.",
    ]
    if distribuicao == "normal":
        desvio = desvio_padrao(numeros, False)
        densidade_normal(centro, centro, desvio)
        parametros = {"media": centro, "desvio_populacional": desvio}

        def funcao(numero):
            return densidade_normal(numero, centro, desvio)
    elif distribuicao == "exponencial":
        if menor < 0 or centro <= 0:
            raise ValueError("A Exponencial exige dados não negativos e média positiva.")
        parametros = {"taxa": 1 / centro}

        def funcao(numero):
            return densidade_exponencial(numero, 1 / centro)
    elif distribuicao == "uniforme":
        densidade_uniforme(menor, menor, maior)
        parametros = {"inferior": menor, "superior": maior}

        def funcao(numero):
            return densidade_uniforme(numero, menor, maior)
    elif distribuicao == "poisson":
        if any(numero < 0 or not numero.is_integer() for numero in numeros):
            raise ValueError("Poisson só é compatível com contagens inteiras não negativas.")
        contagens: dict[float, int] = {}
        for numero in numeros:
            contagens[numero] = contagens.get(numero, 0) + 1
        ordenados = sorted(contagens)
        passo = max(1, matematica.ceil(len(ordenados) / 400))
        observados = [
            {"valor": numero, "probabilidade": contagens[numero] / len(numeros)}
            for numero in ordenados[::passo]
        ]
        espalhamento = matematica.sqrt(centro)
        inicio = max(0, int(centro - 5 * espalhamento))
        fim = max(inicio + 1, int(centro + 5 * espalhamento))
        passo_curva = max(1, matematica.ceil((fim - inicio) / 400))
        curva = [
            {"valor": numero, "densidade": massa_poisson(numero, centro)}
            for numero in range(inicio, fim + 1, passo_curva)
        ]
        if passo > 1:
            avisos.append(
                f"Gráfico exibe 1 a cada {passo} valores distintos, sem renormalizar probabilidades; cálculos usam todos os dados."
            )
        avisos.append(
            "A curva exibe suporte próximo de λ. Zeros visuais em outras faixas podem decorrer de probabilidades extremamente pequenas."
        )
        return {
            "tipo": "discreta",
            "distribuicao": distribuicao,
            "parametros": {"intensidade": centro},
            "dispersao_media": variancia(numeros, False) / centro if centro else None,
            "histograma": histograma(numeros, classes),
            "observados": observados,
            "curva": curva,
            "avisos": avisos,
        }
    else:
        raise ValueError("Distribuição desconhecida.")
    amplitude_dados = maior - menor
    curva = [
        {
            "valor": menor + amplitude_dados * indice / 240,
            "densidade": funcao(menor + amplitude_dados * indice / 240),
        }
        for indice in range(241)
    ]
    return {
        "tipo": "continua",
        "distribuicao": distribuicao,
        "parametros": parametros,
        "histograma": histograma(numeros, classes),
        "curva": curva,
        "avisos": avisos,
    }
