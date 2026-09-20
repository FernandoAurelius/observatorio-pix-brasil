"""Verifica o recurso oficial antes de publicar resultados."""

import sys as sistema
from pathlib import Path as Caminho

RAIZ = Caminho(__file__).resolve().parents[1]
sistema.path[:0] = [str(RAIZ / "pacotes"), str(RAIZ / "aplicacoes/api")]
import argparse as argumentos
import json as serializacao

from observatorio_api.catalogo import CATEGORICAS, NUMERICAS
from observatorio_api.provedor_bcb import ProvedorBCB

if __name__ == "__main__":
    analisador = argumentos.ArgumentParser(description=__doc__)
    analisador.add_argument("--competencia", default="202512")
    opcoes = analisador.parse_args()
    conjunto = ProvedorBCB().obter_mes(opcoes.competencia)
    registros = conjunto["registros"]
    categorias = {campo: len({linha[campo] for linha in registros}) for campo in CATEGORICAS}
    categorias["codigo_municipio"] = len({linha["codigo_municipio"] for linha in registros})
    preenchidos = {
        campo: sum(linha[campo] is not None for linha in registros) for campo in NUMERICAS
    }
    relatorio = {
        "proveniencia": conjunto["proveniencia"],
        "registros": len(registros),
        "categorias_distintas": categorias,
        "numericas_preenchidas": preenchidos,
        "numero_variaveis_numericas": len(NUMERICAS),
        "apto_volume_esquema": len(registros) >= 1000
        and len(NUMERICAS) >= 4
        and sum(valor >= 2 for valor in categorias.values()) >= 2,
        "aviso": "Volume e esquema verificados. Os campos VL_* são reais (R$) conforme o Swagger oficial; a cobertura descrita pelo catálogo é SPI.",
    }
    destino = RAIZ / "documentacao/evidencias/fonte_bcb.json"
    destino.parent.mkdir(exist_ok=True, parents=True)
    destino.write_text(
        serializacao.dumps(relatorio, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(serializacao.dumps(relatorio, ensure_ascii=False, indent=2))
    sistema.exit(0 if relatorio["apto_volume_esquema"] else 1)
