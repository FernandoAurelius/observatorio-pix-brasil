"""Coleta dados oficiais e consolida as evidências calculadas pelo backend."""

import sys as sistema
from pathlib import Path as Caminho

RAIZ = Caminho(__file__).resolve().parents[1]
sistema.path[:0] = [str(RAIZ / "pacotes"), str(RAIZ / "aplicacoes/api")]
import argparse as argumentos
import json as serializacao

from observatorio_api import servicos
from observatorio_api.esquemas import Filtros
from observatorio_api.provedor_bcb import ProvedorBCB
from observatorio_api.relatorios import escrever_resumo, preparar_evidencias


def executar(inicio: str, fim: str) -> Caminho:
    """Recupera o recorte e grava dados estruturados e um resumo textual."""
    filtros = Filtros(inicio=inicio, fim=fim)
    provedor = ProvedorBCB()
    conjunto = provedor.obter_periodo(inicio, fim)
    registros = servicos.filtrar(conjunto, filtros)
    if len(registros) < 1000:
        raise ValueError(
            "A fonte retornou menos de 1.000 registros; este recorte não atende ao Módulo 0."
        )
    evidencias = preparar_evidencias(conjunto, registros, filtros)
    destino = RAIZ / "documentacao/resultados_bcb"
    destino.mkdir(parents=True, exist_ok=True)
    (destino / "evidencias.json").write_text(
        serializacao.dumps(evidencias, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (destino / "DESCOBERTAS.md").write_text(escrever_resumo(evidencias), encoding="utf-8")
    print(f"Modo={provedor.modo}; {len(registros)} registros; evidências gravadas em {destino}.")
    return destino


if __name__ == "__main__":
    analisador = argumentos.ArgumentParser(description=__doc__)
    analisador.add_argument("--inicio", default="202501")
    analisador.add_argument("--fim", default="202512")
    opcoes = analisador.parse_args()
    executar(opcoes.inicio, opcoes.fim)
