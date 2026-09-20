"""Contratos explícitos de entrada para os cálculos estatísticos."""

import math as matematica
from collections.abc import Iterable as Iteravel
from numbers import Real as NumeroReal


def validar_numeros(valores: Iteravel[float], minimo: int = 1) -> list[float]:
    """Materializa uma sequência de números reais finitos.

    Parâmetros
    ----------
    valores : iterável de reais
        Observações sem ausentes. O serviço faz exclusão explícita
        antes de chamar o núcleo; aqui não existe exclusão silenciosa.
    minimo : int
        Quantidade mínima de observações.

    Retorno
    -------
    list[float]
        Cópia numérica dos dados, sem alterar a entrada.

    Erros
    -----
    ValueError
        Sequência insuficiente, NaN ou infinito.
    TypeError
        Booleano, texto ou objeto que não representa um real.
    """
    resultado = []
    for valor in valores:
        if isinstance(valor, bool) or not isinstance(valor, NumeroReal):
            raise TypeError("Cada observação deve ser um número real, não booleano.")
        numero = float(valor)
        if not matematica.isfinite(numero):
            raise ValueError("NaN e infinito não são observações válidas.")
        resultado.append(numero)
    if len(resultado) < minimo:
        raise ValueError(f"São necessárias pelo menos {minimo} observações válidas.")
    return resultado


def validar_pares(
    valores_x: Iteravel[float], valores_y: Iteravel[float], minimo: int = 2
) -> tuple[list[float], list[float]]:
    """Valida dois vetores finitos de mesmo comprimento; preserva os pares.

    Retorna duas listas e lança ValueError se os tamanhos diferirem.
    Os contratos individuais são os de ``validar_numeros``.
    """
    numeros_x = validar_numeros(valores_x, minimo)
    numeros_y = validar_numeros(valores_y, minimo)
    if len(numeros_x) != len(numeros_y):
        raise ValueError("Os vetores devem ter o mesmo número de observações pareadas.")
    return numeros_x, numeros_y
