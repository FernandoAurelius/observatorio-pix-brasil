"""Gera evidência numérica real para a página Metodologia; execute da raiz."""

import sys as sistema
from pathlib import Path as Caminho

RAIZ = Caminho(__file__).resolve().parents[1]
sistema.path.insert(0, str(RAIZ / "pacotes"))
import hashlib as resumos_digitais
import json as serializacao
from datetime import UTC
from datetime import datetime as DataHora

import nucleo_estatistico as proprio
import numpy as referencia_numerica
import scipy as referencia_cientifica
from scipy import stats as referencia_estatistica


def gerar_validacao() -> dict:
    """Compara valores efetivamente calculados sob tolerância absoluta/relativa.

    Retorna a tabela com resultado próprio, referência, erro e aprovação.
    Não substitui pytest, que cobre multimodalidade, casos-limite e contratos.
    """
    valores = [1.0, 2.0, 2.0, 4.0, 7.0, 11.0, 18.0, 29.0]
    respostas = [3.0, 4.0, 5.0, 9.0, 12.0, 19.0, 26.0, 40.0]
    ajuste = proprio.regressao_linear(valores, respostas)
    reta = referencia_estatistica.linregress(valores, respostas)
    comparacoes = [
        ("soma", proprio.soma(valores), referencia_numerica.sum(valores)),
        ("media", proprio.media(valores), referencia_numerica.mean(valores)),
        ("mediana", proprio.mediana(valores), referencia_numerica.median(valores)),
        ("moda_unica", proprio.moda(valores)[0], float(referencia_estatistica.mode(valores).mode)),
        ("amplitude", proprio.amplitude(valores), referencia_numerica.ptp(valores)),
        (
            "variancia_populacional",
            proprio.variancia(valores, False),
            referencia_numerica.var(valores, ddof=0),
        ),
        (
            "variancia_amostral",
            proprio.variancia(valores, True),
            referencia_numerica.var(valores, ddof=1),
        ),
        (
            "desvio_populacional",
            proprio.desvio_padrao(valores, False),
            referencia_numerica.std(valores, ddof=0),
        ),
        (
            "desvio_amostral",
            proprio.desvio_padrao(valores, True),
            referencia_numerica.std(valores, ddof=1),
        ),
        (
            "percentil_90",
            proprio.percentil(valores, 90),
            referencia_numerica.percentile(valores, 90, method="linear"),
        ),
        (
            "q1",
            proprio.quartis(valores)[0],
            referencia_numerica.percentile(valores, 25, method="linear"),
        ),
        (
            "q2",
            proprio.quartis(valores)[1],
            referencia_numerica.percentile(valores, 50, method="linear"),
        ),
        (
            "q3",
            proprio.quartis(valores)[2],
            referencia_numerica.percentile(valores, 75, method="linear"),
        ),
        (
            "coeficiente_variacao",
            proprio.coeficiente_variacao(valores),
            100 * referencia_numerica.std(valores, ddof=1) / abs(referencia_numerica.mean(valores)),
        ),
        (
            "assimetria",
            proprio.assimetria(valores),
            referencia_estatistica.skew(valores, bias=True),
        ),
        (
            "covariancia_amostral",
            proprio.covariancia(valores, respostas),
            referencia_numerica.cov(valores, respostas, ddof=1)[0, 1],
        ),
        (
            "covariancia_populacional",
            proprio.covariancia(valores, respostas, False),
            referencia_numerica.cov(valores, respostas, ddof=0)[0, 1],
        ),
        (
            "correlacao_pearson",
            proprio.correlacao_pearson(valores, respostas),
            referencia_estatistica.pearsonr(valores, respostas).statistic,
        ),
        ("regressao_inclinacao", ajuste["inclinacao"], reta.slope),
        ("regressao_intercepto", ajuste["intercepto"], reta.intercept),
        ("r_quadrado", ajuste["r_quadrado"], reta.rvalue**2),
        (
            "predizer",
            proprio.predizer(8, ajuste["intercepto"], ajuste["inclinacao"]),
            reta.intercept + reta.slope * 8,
        ),
        (
            "densidade_normal",
            proprio.densidade_normal(1.2, 0, 2),
            referencia_estatistica.norm.pdf(1.2, loc=0, scale=2),
        ),
        (
            "densidade_exponencial",
            proprio.densidade_exponencial(1.2, 2),
            referencia_estatistica.expon.pdf(1.2, scale=0.5),
        ),
        (
            "densidade_uniforme",
            proprio.densidade_uniforme(1.2, 0, 3),
            referencia_estatistica.uniform.pdf(1.2, loc=0, scale=3),
        ),
        ("massa_poisson", proprio.massa_poisson(3, 2), referencia_estatistica.poisson.pmf(3, mu=2)),
    ]
    tolerancia = 1e-9
    linhas = [
        {
            "funcao": nome,
            "proprio": float(resultado),
            "referencia": float(referencia),
            "diferenca": abs(float(resultado) - float(referencia)),
            "aprovada": bool(
                abs(resultado - referencia) <= tolerancia + tolerancia * abs(referencia)
            ),
        }
        for nome, resultado, referencia in comparacoes
    ]
    resumo = resumos_digitais.sha256()
    for arquivo in sorted((RAIZ / "pacotes/nucleo_estatistico").glob("*.py")):
        resumo.update(arquivo.name.encode())
        resumo.update(arquivo.read_bytes())
    return {
        "executada": True,
        "gerada_em": DataHora.now(UTC).isoformat(),
        "tolerancia_relativa": tolerancia,
        "tolerancia_absoluta": tolerancia,
        "versoes": {
            "python": sistema.version.split()[0],
            "numpy": referencia_numerica.__version__,
            "scipy": referencia_cientifica.__version__,
        },
        "sha256_nucleo": resumo.hexdigest(),
        "linhas": linhas,
        "referencia": "NumPy/SciPy executados localmente; não representa verificação da API BCB.",
    }


if __name__ == "__main__":
    resultado = gerar_validacao()
    destino = RAIZ / "documentacao/evidencias/validacao.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(
        serializacao.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        f"{sum(linha['aprovada'] for linha in resultado['linhas'])}/{len(resultado['linhas'])} comparações aprovadas; {destino}"
    )
    sistema.exit(0 if all(linha["aprovada"] for linha in resultado["linhas"]) else 1)
