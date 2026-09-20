"""Guardas que impedem substituir o núcleo próprio por bibliotecas prontas."""

import ast as sintaxe
import inspect as inspecao
from pathlib import Path as Caminho

import nucleo_estatistico as nucleo


def teste_nucleo_sem_bibliotecas_estatisticas():
    raiz = Caminho(__file__).resolve().parents[1]
    for pasta in [raiz / "pacotes", raiz / "aplicacoes/api"]:
        for caminho in pasta.rglob("*.py"):
            arvore = sintaxe.parse(caminho.read_text(encoding="utf-8"))
            for no in sintaxe.walk(arvore):
                if isinstance(no, sintaxe.Import):
                    modulos = [apelido.name.split(".")[0] for apelido in no.names]
                elif isinstance(no, sintaxe.ImportFrom):
                    modulos = [(no.module or "").split(".")[0]]
                else:
                    continue
                assert not {"numpy", "scipy", "pandas", "statistics"} & set(modulos), str(caminho)


def teste_docstrings_e_nomes():
    for nome, funcao in inspecao.getmembers(nucleo, inspecao.isfunction):
        assert funcao.__doc__ and len(funcao.__doc__) > 70, nome
        assert nome not in {
            "mean",
            "median",
            "mode",
            "std",
            "variance",
            "covariance",
            "correlation",
            "predict",
        }
