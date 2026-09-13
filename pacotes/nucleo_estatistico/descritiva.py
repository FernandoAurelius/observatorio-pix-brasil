"""Tendência central, dispersão, frequências e quantis implementados na unha.

Somente operações elementares da biblioteca padrão são utilizadas.
``math.fsum`` realiza soma compensada, não uma medida estatística pronta.
"""
import math as matematica
from collections.abc import Iterable as Iteravel
from .validacao import validar_numeros

def soma(valores: Iteravel[float]) -> float:
    """Soma reais finitos com ``fsum``; a soma da sequência vazia é zero.

    Parâmetros: valores, iterável de números finitos.
    Retorno: total como float. Erros: TypeError/ValueError para dados inválidos.
    Fórmula: S = Σ x_i. Complexidade: O(n).
    """
    return matematica.fsum(validar_numeros(valores, 0))

def media(valores: Iteravel[float]) -> float:
    """Calcula a média aritmética de observações não vazias.

    Parâmetros: valores, reais finitos; nenhum ausente é ignorado.
    Retorno: float. Erros: ValueError para entrada vazia ou não finita.
    Fórmula: x̄ = (Σ x_i)/n. Complexidade: O(n).
    Exemplo: media([2, 4, 6]) == 4.0.
    """
    numeros = validar_numeros(valores)
    return matematica.fsum(numeros) / len(numeros)

def percentil(valores: Iteravel[float], percentual: float) -> float:
    """Calcula um percentil por interpolação linear, tipo 7 de Hyndman-Fan.

    Parâmetros: valores finitos; percentual real entre 0 e 100 (inclusivos).
    Retorno: float. Erros: ValueError para entrada vazia ou percentual inválido.
    Fórmula: h=(n-1)p/100; j=floor(h); Q=(1-g)x[j]+g*x[j+1], g=h-j.
    Convenção: idêntica a numpy.percentile(method="linear").
    Complexidade: O(n log n); a entrada não é modificada.
    """
    percentual = validar_numeros([percentual])[0]
    if not 0 <= percentual <= 100:
        raise ValueError('O percentil deve estar entre 0 e 100.')
    ordenados = sorted(validar_numeros(valores))
    posicao = (len(ordenados) - 1) * percentual / 100
    inferior = matematica.floor(posicao)
    superior = min(inferior + 1, len(ordenados) - 1)
    fracao = posicao - inferior
    return ordenados[inferior] + fracao * (ordenados[superior] - ordenados[inferior])

def mediana(valores: Iteravel[float]) -> float:
    """Retorna o percentil 50 (central ou média dos dois valores centrais).

    Parâmetros: valores finitos não vazios. Retorno: float.
    Erros e complexidade: iguais aos de ``percentil``.
    """
    return percentil(valores, 50)

def moda(valores: Iteravel[float]) -> list[float]:
    """Retorna todas as modas em ordem crescente, ou [] para dados amodais.

    Parâmetros: valores finitos não vazios.
    Retorno: lista dos valores com maior frequência absoluta.
    Convenção: quando todos aparecem uma única vez, a série é amodal.
    Empates repetidos são preservados (multimodalidade); não há arredondamento.
    Erros: os de validar_numeros. Complexidade: O(n + k log k).
    """
    contagens: dict[float, int] = {}
    for numero in validar_numeros(valores):
        contagens[numero] = contagens.get(numero, 0) + 1
    maior = max(contagens.values())
    return sorted(numero for numero, contagem in contagens.items() if contagem == maior) if maior > 1 else []

def amplitude(valores: Iteravel[float]) -> float:
    """Retorna max(x)-min(x) para reais finitos não vazios, em O(n).

    Retorno: float não negativo. Erros: contrato de validar_numeros.
    """
    numeros = validar_numeros(valores)
    return max(numeros) - min(numeros)

def variancia(valores: Iteravel[float], amostral: bool = True) -> float:
    """Calcula a variância em duas passagens com soma compensada.

    Parâmetros: valores finitos; amostral=True usa correção de Bessel.
    Retorno: float em unidades ao quadrado.
    Fórmula: Σ(x_i-x̄)^2 / (n-1), ou /n na modalidade populacional.
    Erros: ValueError se n<2 (amostral), n<1 (populacional), NaN ou infinito.
    Evita E[X^2]-E[X]^2, vulnerável a cancelamento catastrófico.
    Complexidade: O(n).
    """
    numeros = validar_numeros(valores, 2 if amostral else 1)
    centro = media(numeros)
    return matematica.fsum((numero - centro) ** 2 for numero in numeros) / (len(numeros) - int(amostral))

def desvio_padrao(valores: Iteravel[float], amostral: bool = True) -> float:
    """Retorna a raiz da variância, na unidade original dos dados.

    Parâmetros/erros: os de ``variancia``. Retorno: float não negativo.
    Fórmula: s=√(s²); σ=√(σ²). Complexidade: O(n).
    """
    return matematica.sqrt(variancia(valores, amostral))

def quartis(valores: Iteravel[float]) -> tuple[float, float, float]:
    """Retorna Q1, Q2 e Q3, percentis 25, 50 e 75 pelo método linear.

    Parâmetros: valores finitos não vazios. Retorno: tupla de três floats.
    Erros: contrato de percentil. Complexidade: O(n log n).
    """
    numeros = validar_numeros(valores)
    return tuple(percentil(numeros, percentual) for percentual in (25, 50, 75))

def coeficiente_variacao(valores: Iteravel[float], amostral: bool = True) -> float:
    """Retorna a dispersão relativa em porcentagem: 100*s/|x̄|.

    Parâmetros: valores em escala de razão; amostral escolhe s ou σ.
    Retorno: float não negativo. Erros: ValueError quando a média é zero,
    além dos contratos do desvio padrão. Média próxima de zero torna
    a interpretação instável; a aplicação não classifica CV por limiares universais.
    """
    numeros = validar_numeros(valores)
    centro = media(numeros)
    if centro == 0:
        raise ValueError('Coeficiente de variação indefinido para média zero.')
    return 100 * desvio_padrao(numeros, amostral) / abs(centro)

def assimetria(valores: Iteravel[float]) -> float:
    """Calcula o terceiro momento padronizado populacional g1=m3/m2^(3/2).

    Parâmetros: reais finitos não constantes. Retorno: float com sinal.
    Referência de validação: scipy.stats.skew(bias=True).
    Erros: ValueError para variância zero. Complexidade: O(n).
    Não é teste de simetria; é um descritor sensível a extremos.
    """
    numeros = validar_numeros(valores)
    centro = media(numeros)
    segundo = variancia(numeros, False)
    if segundo == 0:
        raise ValueError('Assimetria indefinida para uma variável constante.')
    terceiro = matematica.fsum((numero-centro)**3 for numero in numeros) / len(numeros)
    return terceiro / segundo ** 1.5

def frequencias_categoricas(valores: Iteravel[str]) -> list[dict]:
    """Conta categorias em O(n+k log k) sem usar value_counts ou Counter.

    Parâmetros: rótulos de categorias não nulos.
    Retorno: linhas ordenadas por frequência decrescente e depois rótulo.
    Frequência relativa é uma proporção [0,1], não porcentagem.
    Erros: ValueError para conjunto vazio ou ausentes (None).
    Acumuladas não são calculadas: categorias nominais não têm ordem natural.
    """
    contagens: dict[str, int] = {}
    for valor in valores:
        if valor is None:
            raise ValueError('A contagem categórica exige rótulos não nulos.')
        categoria = str(valor)
        contagens[categoria] = contagens.get(categoria, 0) + 1
    total = sum(contagens.values())
    if total == 0:
        raise ValueError('Não há categorias para contar.')
    return [{'categoria': categoria, 'frequencia': frequencia, 'relativa': frequencia/total}
            for categoria, frequencia in sorted(contagens.items(), key=lambda par: (-par[1], par[0]))]

def histograma(valores: Iteravel[float], classes: int = 20) -> list[dict]:
    """Constrói classes contíguas e frequências absolutas/relativas/acumuladas.

    Parâmetros: reais finitos não vazios; classes inteiro entre 1 e 100.
    Retorno: lista de limites, centro, frequência, relativa e densidade.
    Densidade = frequência/(n*largura): área total do histograma igual a 1.
    Convenção: [inferior,superior), exceto a última classe, fechada à direita.
    Constantes: intervalo de largura 1, ampliado quando a precisão de
    ponto flutuante exigir. Classes numericamente indistinguíveis são rejeitadas.
    Erros: ValueError para quantidade de classes inválida ou entrada vazia.
    Complexidade: O(n log(classes) + classes).
    """
    numeros = validar_numeros(valores)
    if isinstance(classes, bool) or not isinstance(classes, int) or not 1 <= classes <= 100:
        raise ValueError('O número de classes deve ser um inteiro entre 1 e 100.')
    menor, maior = min(numeros), max(numeros)
    if menor == maior:
        folga = max(0.5, matematica.ulp(menor)*classes)
        menor, maior = menor - folga, maior + folga
    largura = (maior-menor)/classes
    limites = [menor + indice*largura for indice in range(classes+1)]
    limites[-1] = maior
    if any(not matematica.isfinite(limite) for limite in limites) or any(
            limites[indice+1] <= limites[indice] for indice in range(classes)):
        raise ValueError('Reduza as classes: limites fora da precisão numérica representável.')
    contagens = [0]*classes
    # Busca binária manual: mesmas fronteiras retornadas e comparadas nos testes.
    for numero in numeros:
        esquerda, direita = 0, classes
        while esquerda < direita:
            meio = (esquerda+direita)//2
            if numero < limites[meio+1]:
                direita = meio
            else:
                esquerda = meio+1
        contagens[min(esquerda, classes-1)] += 1
    linhas, acumulada = [], 0
    for indice, frequencia in enumerate(contagens):
        acumulada += frequencia
        largura_real = limites[indice+1]-limites[indice]
        linhas.append({'inferior':limites[indice], 'superior':limites[indice+1],
            'centro':(limites[indice]+limites[indice+1])/2, 'frequencia':frequencia,
            'relativa':frequencia/len(numeros), 'acumulada':acumulada,
            'relativa_acumulada':acumulada/len(numeros),
            'densidade':frequencia/(len(numeros)*largura_real)})
    return linhas

def detectar_atipicos(valores: Iteravel[float]) -> dict:
    """Aplica a regra de Tukey: valores fora de [Q1-1,5*IQR,Q3+1,5*IQR].

    Parâmetros: reais finitos não vazios. Retorno: quartis, cercas,
    bigodes observados, valores/índices atípicos e contagem total.
    Valores exatamente nas cercas não são atípicos. Não remove dados.
    Erros: contrato de quartis. Complexidade: O(n log n).
    """
    numeros = validar_numeros(valores)
    primeiro, segundo, terceiro = quartis(numeros)
    intervalo = terceiro-primeiro
    inferior, superior = primeiro-1.5*intervalo, terceiro+1.5*intervalo
    indices = [indice for indice, numero in enumerate(numeros) if numero < inferior or numero > superior]
    internos = [numero for numero in numeros if inferior <= numero <= superior]
    return {'q1':primeiro, 'q2':segundo, 'q3':terceiro, 'iqr':intervalo,
            'limite_inferior':inferior, 'limite_superior':superior,
            'bigode_inferior':min(internos), 'bigode_superior':max(internos),
            'indices':indices, 'valores':[numeros[indice] for indice in indices],
            'quantidade':len(indices)}

def resumo(valores: Iteravel[float], amostral: bool = False) -> dict:
    """Reúne medidas próprias e explica casos matematicamente indefinidos.

    Parâmetros: reais finitos; amostral=False descreve o universo filtrado.
    Retorno: dicionário JSON-compatível com medidas, convenções e avisos.
    Medidas indefinidas são None (nunca NaN, infinito ou zero inventado).
    Erros: entrada vazia/inválida. Não confunde universo observado com Brasil.
    """
    numeros = validar_numeros(valores)
    caixa = detectar_atipicos(numeros)
    avisos = []
    def calcular_ou_indefinido(funcao, *argumentos):
        """Converte somente indefinições matemáticas em None com aviso."""
        try:
            return funcao(*argumentos)
        except ValueError as erro:
            avisos.append(str(erro))
            return None
    modas = moda(numeros)
    resultado = {'quantidade':len(numeros), 'media':media(numeros),
        'mediana':mediana(numeros), 'modas':modas[:50], 'numero_modas':len(modas),
        'minimo':min(numeros), 'maximo':max(numeros), 'amplitude':amplitude(numeros),
        'variancia':calcular_ou_indefinido(variancia,numeros,amostral),
        'desvio_padrao':calcular_ou_indefinido(desvio_padrao,numeros,amostral),
        'coeficiente_variacao':calcular_ou_indefinido(coeficiente_variacao,numeros,amostral),
        'assimetria':calcular_ou_indefinido(assimetria,numeros),
        'q1':caixa['q1'], 'q2':caixa['q2'], 'q3':caixa['q3'], 'iqr':caixa['iqr'],
        'atipicos':caixa['quantidade'], 'amostral':amostral, 'avisos':avisos}
    resultado['interpretacao'] = ('Variável constante: não há dispersão.' if resultado['assimetria'] is None else
        f"O terceiro momento padronizado é {resultado['assimetria']:.3f}. " +
        ('O sinal positivo indica assimetria à direita.' if resultado['assimetria'] > 0 else
         'O sinal negativo indica assimetria à esquerda.' if resultado['assimetria'] < 0 else
         'O terceiro momento é zero; isso, isoladamente, não prova simetria.') +
        ' Atípicos pelo IQR não são necessariamente erros; todos permanecem nos cálculos.')
    return resultado


def calcular_media(valores: Iteravel[float]) -> float:
    """Calcula a média ``x̄ = Σxᵢ/n`` de uma sequência de reais finitos.

    Args: valores, sequência não vazia; ausentes não são ignorados.
    Returns: média sem arredondamento.
    Raises: TypeError para item não numérico; ValueError para entrada vazia,
    NaN ou infinito. Uma única observação retorna a própria observação.
    """
    return media(valores)


def calcular_mediana(valores: Iteravel[float]) -> float:
    """Calcula a mediana, ou percentil 50 pelo método linear tipo 7.

    Args: valores, sequência não vazia de reais finitos.
    Returns: centro ordenado; para n par, média dos dois valores centrais.
    Raises: TypeError para item não numérico e ValueError para entrada vazia
    ou não finita. A entrada original não é modificada.
    """
    return mediana(valores)


def calcular_moda(valores: Iteravel[float]) -> list[float]:
    """Calcula todas as modas segundo a maior frequência absoluta.

    Args: valores, sequência não vazia de reais finitos.
    Returns: modas ordenadas; lista vazia quando cada valor ocorre uma vez.
    Raises: TypeError para item não numérico e ValueError para entrada vazia
    ou não finita. Empates repetidos são mantidos como multimodalidade.
    """
    return moda(valores)


def calcular_amplitude(valores: Iteravel[float]) -> float:
    """Calcula a amplitude ``máximo − mínimo`` de reais finitos.

    Args: valores, sequência não vazia.
    Returns: distância não negativa entre os extremos; zero para constante.
    Raises: TypeError para item não numérico e ValueError para entrada vazia,
    NaN ou infinito. Não arredonda nem altera a sequência recebida.
    """
    return amplitude(valores)


def calcular_variancia_populacional(valores: Iteravel[float]) -> float:
    """Calcula ``σ² = Σ(xᵢ−x̄)²/n`` em duas passagens.

    Args: valores, uma ou mais observações reais finitas.
    Returns: variância populacional em unidades ao quadrado; zero para uma
    constante. Raises: TypeError para item não numérico e ValueError para
    sequência vazia ou não finita.
    """
    return variancia(valores, False)


def calcular_variancia_amostral(valores: Iteravel[float]) -> float:
    """Calcula ``s² = Σ(xᵢ−x̄)²/(n−1)`` com correção de Bessel.

    Args: valores, ao menos duas observações reais finitas.
    Returns: variância amostral em unidades ao quadrado.
    Raises: TypeError para item não numérico e ValueError para menos de duas
    observações, NaN ou infinito.
    """
    return variancia(valores, True)


def calcular_desvio_padrao_populacional(valores: Iteravel[float]) -> float:
    """Calcula ``σ = √(Σ(xᵢ−x̄)²/n)`` para o universo observado.

    Args: valores, uma ou mais observações reais finitas.
    Returns: desvio populacional na unidade original; zero para constante.
    Raises: TypeError para item não numérico e ValueError para sequência vazia
    ou não finita.
    """
    return desvio_padrao(valores, False)


def calcular_desvio_padrao_amostral(valores: Iteravel[float]) -> float:
    """Calcula ``s = √(Σ(xᵢ−x̄)²/(n−1))`` para uma amostra.

    Args: valores, ao menos duas observações reais finitas.
    Returns: desvio amostral na unidade original.
    Raises: TypeError para item não numérico e ValueError para menos de duas
    observações, NaN ou infinito.
    """
    return desvio_padrao(valores, True)


def calcular_percentil(valores: Iteravel[float], percentual: float) -> float:
    """Calcula ``Pp`` por interpolação linear tipo 7 de Hyndman–Fan.

    Args: valores, sequência não vazia; percentual entre 0 e 100 inclusive.
    Returns: percentil interpolado; 0 e 100 devolvem mínimo e máximo.
    Raises: TypeError para argumento não numérico e ValueError para entrada
    vazia/não finita ou percentual fora do intervalo.
    """
    return percentil(valores, percentual)


def calcular_quartis(valores: Iteravel[float]) -> tuple[float, float, float]:
    """Calcula Q1, Q2 e Q3 como percentis 25, 50 e 75 do tipo 7.

    Args: valores, sequência não vazia de reais finitos.
    Returns: tupla ordenada ``(Q1, Q2, Q3)`` sem modificar a entrada.
    Raises: TypeError para item não numérico e ValueError para entrada vazia,
    NaN ou infinito.
    """
    return quartis(valores)


def calcular_coeficiente_variacao(valores: Iteravel[float], amostral: bool = True) -> float:
    """Calcula ``100 × desvio/|x̄|`` como dispersão relativa percentual.

    Args: valores em escala de razão; amostral escolhe s ou σ.
    Returns: coeficiente percentual não negativo.
    Raises: ValueError para média zero ou tamanho insuficiente e TypeError
    para item não numérico. Média próxima de zero exige cautela interpretativa.
    """
    return coeficiente_variacao(valores, amostral)
