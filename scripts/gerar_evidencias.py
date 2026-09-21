"""Coleta dados oficiais e consolida as evidências calculadas pelo backend."""

import sys as sistema
from pathlib import Path as Caminho

RAIZ = Caminho(__file__).resolve().parents[1]
sistema.path[:0] = [str(RAIZ / "pacotes"), str(RAIZ / "aplicacoes/api")]
import argparse as argumentos

from observatorio_api import servicos
from observatorio_api.esquemas import Filtros
from observatorio_api.provedor_bcb import ProvedorBCB
from observatorio_api.relatorios import escrever_resumo, preparar_evidencias


def executar(inicio: str, fim: str) -> dict:
    """Recupera o recorte e calcula o resumo estatístico."""
    filtros = Filtros(inicio=inicio, fim=fim)
    provedor = ProvedorBCB()
    conjunto = provedor.obter_periodo(inicio, fim)
    registros = servicos.filtrar(conjunto, filtros)
    if len(registros) < 1000:
        raise ValueError(
            "A fonte retornou menos de 1.000 registros; este recorte não atende ao Módulo 0."
        )
    evidencias = preparar_evidencias(conjunto, registros, filtros)
    print(escrever_resumo(evidencias))
    return evidencias


if __name__ == "__main__":
    analisador = argumentos.ArgumentParser(description=__doc__)
    analisador.add_argument("--inicio", default="202501")
    analisador.add_argument("--fim", default="202512")
    opcoes = analisador.parse_args()
    executar(opcoes.inicio, opcoes.fim)
