"""Matemática em Python puro; nenhuma dependência estatística externa."""

from .descritiva import (
    amplitude,
    assimetria,
    calcular_amplitude,
    calcular_coeficiente_variacao,
    calcular_desvio_padrao_amostral,
    calcular_desvio_padrao_populacional,
    calcular_media,
    calcular_mediana,
    calcular_moda,
    calcular_percentil,
    calcular_quartis,
    calcular_variancia_amostral,
    calcular_variancia_populacional,
    coeficiente_variacao,
    desvio_padrao,
    detectar_atipicos,
    frequencias_categoricas,
    histograma,
    media,
    mediana,
    moda,
    percentil,
    quartis,
    resumo,
    soma,
    variancia,
)
from .distribuicoes import (
    ajustar_distribuicao,
    densidade_exponencial,
    densidade_normal,
    densidade_uniforme,
    massa_poisson,
)
from .relacoes import (
    calcular_correlacao_pearson,
    calcular_covariancia,
    coeficiente_determinacao,
    correlacao_pearson,
    covariancia,
    predizer,
    regressao_linear,
)
from .simulacoes import simular_grandes_numeros, simular_limite_central
