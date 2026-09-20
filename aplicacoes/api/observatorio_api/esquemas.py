"""Modelos de entrada em português, com limites de custo e validação."""

from typing import Literal as LiteralPermitido

from pydantic import BaseModel as ModeloBase
from pydantic import ConfigDict as ConfiguracaoModelo
from pydantic import Field as Campo


class Filtros(ModeloBase):
    """Janela de até um ano e categorias geográficas; sem código OData livre."""

    model_config = ConfiguracaoModelo(extra="forbid", allow_inf_nan=False)
    inicio: str = Campo(default="202512", pattern=r"^\d{6}$")
    fim: str = Campo(default="202512", pattern=r"^\d{6}$")
    regiao: str = Campo(default="", max_length=60)
    uf: str = Campo(default="", max_length=2)
    municipio: str = Campo(default="", max_length=7)


class Analise(Filtros):
    """Variável e convenções da análise univariada."""

    variavel: str = Campo(default="quantidade_pagador_pf", max_length=60)
    classes: int = Campo(default=25, ge=1, le=100)
    amostral: bool = False
    percentual: float = Campo(default=90, ge=0, le=100)


class ConsultaTabela(Filtros):
    """Pesquisa paginada; a exportação completa usa rota dedicada."""

    pagina: int = Campo(default=1, ge=1, le=10000)
    tamanho: int = Campo(default=25, ge=10, le=100)
    busca: str = Campo(default="", max_length=100)
    ordenar: str = Campo(default="valor_pagador_pf", max_length=60)
    decrescente: bool = True


class ConsultaPanorama(Filtros):
    """Perspectiva do fluxo: nunca soma pagadores e recebedores."""

    papel: LiteralPermitido["pagador", "recebedor"] = "pagador"
    pessoa: LiteralPermitido["todos", "pf", "pj"] = "todos"


class ConsultaRegressao(Filtros):
    """Pares de variáveis originais; predição opcional no backend."""

    variavel_x: str = Campo(default="quantidade_pagador_pf", max_length=60)
    variavel_y: str = Campo(default="valor_pagador_pf", max_length=60)
    valor_predicao: float | None = None


class ConsultaDistribuicao(Analise):
    """Escolhe uma família candidata, sem declarar ajuste aprovado."""

    distribuicao: LiteralPermitido["normal", "exponencial", "uniforme", "poisson"] = "normal"


class ConsultaTCL(Analise):
    """Amostragem com reposição; produto tamanho*repetições limitado no núcleo."""

    tamanho_amostra: int = Campo(default=30, ge=2, le=1000)
    repeticoes: int = Campo(default=1000, ge=50, le=10000)
    semente: int = Campo(default=42, ge=0, le=2147483647)


class ConsultaLGN(ModeloBase):
    """Moeda ou dado justos, evento específico e semente reproduzível."""

    model_config = ConfiguracaoModelo(extra="forbid")
    experimento: LiteralPermitido["moeda", "dado"] = "moeda"
    repeticoes: int = Campo(default=2000, ge=10, le=100000)
    resultado: int = Campo(default=1, ge=1, le=6)
    semente: int = Campo(default=42, ge=0, le=2147483647)
