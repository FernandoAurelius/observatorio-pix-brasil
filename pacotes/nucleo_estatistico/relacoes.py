"""Covariância, Pearson e mínimos quadrados sem funções estatísticas prontas."""

import math as matematica

from .descritiva import media
from .validacao import validar_numeros, validar_pares


def covariancia(valores_x, valores_y, amostral: bool = True) -> float:
    """Calcula Σ(x_i-x̄)(y_i-ȳ)/(n-ddof) sobre pares válidos.

    Parâmetros: vetores reais finitos, de igual comprimento; amostral=True
    define ddof=1; False define ddof=0.
    Retorno: float (unidade de X multiplicada pela unidade de Y).
    Erros: ValueError para comprimentos diferentes ou n insuficiente.
    Complexidade: O(n); exclusão de ausentes é sempre pareada no serviço.
    """
    numeros_x, numeros_y = validar_pares(valores_x, valores_y, 2 if amostral else 1)
    centro_x, centro_y = media(numeros_x), media(numeros_y)
    return matematica.fsum(
        (valor_x - centro_x) * (valor_y - centro_y)
        for valor_x, valor_y in zip(numeros_x, numeros_y, strict=False)
    ) / (len(numeros_x) - int(amostral))


def correlacao_pearson(valores_x, valores_y) -> float:
    """Calcula r=Sxy/√(Sxx*Syy), a associação linear descritiva.

    Parâmetros: pares finitos, mesmo tamanho n>=2, ambas variáveis não constantes.
    Retorno: float em [-1,1]; pequenas ultrapassagens por arredondamento
    são limitadas ao intervalo matemático.
    Erros: ValueError para variável constante ou entrada incompatível.
    Complexidade: O(n). Não fornece teste, causalidade nem independência.
    """
    numeros_x, numeros_y = validar_pares(valores_x, valores_y)
    centro_x, centro_y = media(numeros_x), media(numeros_y)
    soma_xx = matematica.fsum((valor - centro_x) ** 2 for valor in numeros_x)
    soma_yy = matematica.fsum((valor - centro_y) ** 2 for valor in numeros_y)
    if soma_xx == 0 or soma_yy == 0:
        raise ValueError("Pearson indefinido quando uma das variáveis é constante.")
    soma_xy = matematica.fsum(
        (valor_x - centro_x) * (valor_y - centro_y)
        for valor_x, valor_y in zip(numeros_x, numeros_y, strict=False)
    )
    return max(-1.0, min(1.0, soma_xy / matematica.sqrt(soma_xx) / matematica.sqrt(soma_yy)))


def coeficiente_determinacao(observados, previstos) -> float:
    """Calcula R²=1-SQres/SQtot, sem forçar o resultado para [0,1].

    Parâmetros: duas sequências finitas pareadas, n>=2.
    Retorno: float; pode ser negativo para previsões arbitrárias.
    Erros: ValueError para resposta constante (SQtot=0), pois R² é indefinido.
    Complexidade: O(n). Na regressão com intercepto ajustada à mesma amostra,
    R² coincide com r² quando ambos estão definidos.
    """
    reais, estimados = validar_pares(observados, previstos)
    centro = media(reais)
    total = matematica.fsum((valor - centro) ** 2 for valor in reais)
    if total == 0:
        raise ValueError("R² indefinido para uma resposta constante.")
    residuos = matematica.fsum(
        (real - estimado) ** 2 for real, estimado in zip(reais, estimados, strict=False)
    )
    return 1 - residuos / total


def predizer(valor_x: float, intercepto: float, inclinacao: float) -> float:
    """Retorna ŷ=β0+β1*x para três parâmetros reais finitos.

    Retorno: float. Erros: ValueError/TypeError para entradas inválidas.
    Não arredonda, não impede extrapolação e não impõe positividade;
    cabe à interface explicitar essas limitações.
    """
    valor_x, intercepto, inclinacao = validar_numeros([valor_x, intercepto, inclinacao])
    return intercepto + inclinacao * valor_x


def regressao_linear(valores_x, valores_y) -> dict:
    """Ajusta regressão linear simples com intercepto por mínimos quadrados.

    Parâmetros: vetores pareados, n>=2; X não pode ser constante.
    Fórmulas: β1=Sxy/Sxx; β0=ȳ-β1*x̄; ŷ=β0+β1*x.
    Retorno: coeficientes, r, R², resíduos, valores ajustados e domínio de X.
    Para Y constante, coeficientes são válidos, r/R² são None.
    Erros: ValueError se X for constante ou os pares forem inválidos.
    Complexidade: O(n). Sem inferência causal ou intervalos não justificados.
    """
    numeros_x, numeros_y = validar_pares(valores_x, valores_y)
    centro_x, centro_y = media(numeros_x), media(numeros_y)
    soma_xx = matematica.fsum((numero - centro_x) ** 2 for numero in numeros_x)
    if soma_xx == 0:
        raise ValueError("Não é possível ajustar uma reta quando X é constante.")
    soma_xy = matematica.fsum(
        (numero_x - centro_x) * (numero_y - centro_y)
        for numero_x, numero_y in zip(numeros_x, numeros_y, strict=False)
    )
    inclinacao = soma_xy / soma_xx
    intercepto = centro_y - inclinacao * centro_x
    previstos = [predizer(numero, intercepto, inclinacao) for numero in numeros_x]
    constante_y = all(numero == numeros_y[0] for numero in numeros_y)
    return {
        "inclinacao": inclinacao,
        "intercepto": intercepto,
        "pearson": None if constante_y else correlacao_pearson(numeros_x, numeros_y),
        "r_quadrado": None if constante_y else coeficiente_determinacao(numeros_y, previstos),
        "covariancia": covariancia(numeros_x, numeros_y),
        "previstos": previstos,
        "residuos": [real - previsto for real, previsto in zip(numeros_y, previstos, strict=False)],
        "minimo_x": min(numeros_x),
        "maximo_x": max(numeros_x),
        "quantidade": len(numeros_x),
        "aviso": "Correlação não implica causalidade. R² descreve o ajuste nestes dados, não a precisão fora deles.",
    }


def calcular_covariancia(valores_x, valores_y, amostral: bool = True) -> float:
    """Calcula a covariância ``Σ(xᵢ−x̄)(yᵢ−ȳ)/(n−ddof)``.

    Args: valores_x e valores_y, sequências pareadas de reais finitos;
    amostral usa ddof=1 quando verdadeiro e zero caso contrário.
    Returns: covariância na unidade composta X×Y.
    Raises: ValueError para tamanhos diferentes ou amostra insuficiente e
    TypeError para item não numérico. Ausentes devem ser removidos em pares.
    """
    return covariancia(valores_x, valores_y, amostral)


def calcular_correlacao_pearson(valores_x, valores_y) -> float:
    """Calcula ``r = Sxy/√(SxxSyy)`` para associação linear descritiva.

    Args: valores_x e valores_y, sequências pareadas com ao menos dois reais.
    Returns: coeficiente limitado numericamente ao intervalo [-1, 1].
    Raises: ValueError para tamanhos incompatíveis ou variável constante e
    TypeError para item não numérico. Correlação não implica causalidade.
    """
    return correlacao_pearson(valores_x, valores_y)
