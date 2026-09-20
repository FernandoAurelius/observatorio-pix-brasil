"""Experimentos Monte Carlo reprodutíveis usando gerador local independente."""

import math as matematica
import random as aleatoriedade

from .descritiva import desvio_padrao, histograma, media
from .distribuicoes import densidade_normal
from .validacao import validar_numeros


def simular_grandes_numeros(
    repeticoes: int = 2000, experimento: str = "moeda", resultado: int = 1, semente: int = 42
) -> dict:
    """Simula indicadores Bernoulli de moeda justa ou de uma face de dado justo.

    Parâmetros: repeticoes inteiro 10..100000; experimento moeda/dado;
    resultado=1/2 para moeda (cara/coroa), 1..6 para dado; semente inteira.
    Retorno: frequência final, p teórica e série de convergência (até 1001 pontos).
    Fórmula: f_n=(Σ I_i)/n. A convergência não precisa ser monótona.
    Erros: ValueError para parâmetros fora do domínio. Complexidade: O(repeticoes).
    """
    if experimento not in ("moeda", "dado"):
        raise ValueError("Escolha moeda ou dado.")
    if (
        isinstance(repeticoes, bool)
        or not isinstance(repeticoes, int)
        or not 10 <= repeticoes <= 100000
    ):
        raise ValueError("Use de 10 a 100000 repetições inteiras.")
    faces = 2 if experimento == "moeda" else 6
    if (
        isinstance(resultado, bool)
        or not isinstance(resultado, int)
        or resultado not in range(1, faces + 1)
    ):
        raise ValueError("Resultado incompatível com o experimento.")
    if isinstance(semente, bool) or not isinstance(semente, int):
        raise ValueError("A semente deve ser um inteiro.")
    gerador = aleatoriedade.Random(semente)
    acertos, pontos = 0, []
    passo = max(1, matematica.ceil(repeticoes / 1000))
    for repeticao in range(1, repeticoes + 1):
        acertos += int(gerador.randint(1, faces) == resultado)
        if repeticao == 1 or repeticao % passo == 0 or repeticao == repeticoes:
            pontos.append({"repeticao": repeticao, "frequencia": acertos / repeticao})
    return {
        "pontos": pontos,
        "probabilidade": 1 / faces,
        "frequencia_final": acertos / repeticoes,
        "acertos": acertos,
        "repeticoes": repeticoes,
        "semente": semente,
        "aviso": "A frequência tende à probabilidade em muitas repetições; o erro pode aumentar temporariamente.",
    }


def simular_limite_central(
    valores, tamanho_amostra: int = 30, repeticoes: int = 1000, semente: int = 42
) -> dict:
    """Sorteia amostras independentes COM reposição do universo empírico.

    Parâmetros: dados finitos, n>=2; tamanho_amostra 2..1000;
    repeticoes 50..10000; produto limitado a 2000000; semente inteira.
    Retorno: médias, histogramas, média das médias, desvio observado,
    erro padrão teórico σ/√n e curva Normal N(μ,σ²/n).
    O universo empírico é tratado como população finita de referência.
    Isso não afirma que município-mês seja independente na realidade.
    Erros: ValueError para domínio inválido. Complexidade: O(n*repeticoes).
    """
    numeros = validar_numeros(valores, 2)
    if (
        isinstance(tamanho_amostra, bool)
        or not isinstance(tamanho_amostra, int)
        or not 2 <= tamanho_amostra <= 1000
    ):
        raise ValueError("O tamanho da amostra deve estar entre 2 e 1000.")
    if (
        isinstance(repeticoes, bool)
        or not isinstance(repeticoes, int)
        or not 50 <= repeticoes <= 10000
    ):
        raise ValueError("Use de 50 a 10000 simulações.")
    if tamanho_amostra * repeticoes > 2000000:
        raise ValueError("Reduza os parâmetros: limite de 2 milhões de sorteios por requisição.")
    if isinstance(semente, bool) or not isinstance(semente, int):
        raise ValueError("A semente deve ser um inteiro.")
    gerador = aleatoriedade.Random(semente)
    medias = [media(gerador.choices(numeros, k=tamanho_amostra)) for _indice in range(repeticoes)]
    centro = media(numeros)
    desvio = desvio_padrao(numeros, False)
    erro_padrao = desvio / matematica.sqrt(tamanho_amostra)
    menor, maior = min(medias), max(medias)
    curva = (
        []
        if erro_padrao == 0
        else [
            {
                "valor": menor + (maior - menor) * indice / 200,
                "densidade": densidade_normal(
                    menor + (maior - menor) * indice / 200, centro, erro_padrao
                ),
            }
            for indice in range(201)
        ]
    )
    return {
        "media_populacao": centro,
        "desvio_populacao": desvio,
        "media_das_medias": media(medias),
        "desvio_das_medias": desvio_padrao(medias, True),
        "erro_padrao": erro_padrao,
        "histograma_original": histograma(numeros, 30),
        "histograma_medias": histograma(medias, 30),
        "curva": curva,
        "medias": medias,
        "tamanho_amostra": tamanho_amostra,
        "repeticoes": repeticoes,
        "semente": semente,
        "com_reposicao": True,
        "aviso": "Compare n=5, n=30 e n=100. Caudas intensas podem exigir amostras grandes; n=30 não garante Normalidade.",
    }
