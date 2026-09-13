"""Matemática em Python puro; nenhuma dependência estatística externa."""
from .descritiva import (soma, media, mediana, moda, amplitude, variancia,
    desvio_padrao, percentil, quartis, coeficiente_variacao, assimetria,
    frequencias_categoricas, histograma, resumo, detectar_atipicos,
    calcular_media, calcular_mediana, calcular_moda, calcular_amplitude,
    calcular_variancia_populacional, calcular_variancia_amostral,
    calcular_desvio_padrao_populacional, calcular_desvio_padrao_amostral,
    calcular_percentil, calcular_quartis, calcular_coeficiente_variacao)
from .relacoes import (covariancia, correlacao_pearson, regressao_linear,
    predizer, coeficiente_determinacao, calcular_covariancia,
    calcular_correlacao_pearson)
from .distribuicoes import densidade_normal, densidade_exponencial, densidade_uniforme, massa_poisson, ajustar_distribuicao
from .simulacoes import simular_grandes_numeros, simular_limite_central
