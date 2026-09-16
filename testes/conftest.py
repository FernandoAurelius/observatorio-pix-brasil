"""Amostra determinística para testes isolados, sem chamadas de rede."""
import random as aleatoriedade
import pytest as testes
from fastapi.testclient import TestClient as ClienteTeste
from observatorio_api import principal
from observatorio_api.catalogo import NUMERICAS,FONTE

def gerar_amostra_teste(competencia: str = '202512') -> list[dict]:
    """Produz registros sintéticos apenas para verificar os serviços."""
    localidades = [('Norte','Pará','PA'),('Nordeste','Bahia','BA'),('Centro-Oeste','Goiás','GO'),('Sudeste','São Paulo','SP'),('Sul','Paraná','PR')]
    gerador = aleatoriedade.Random(int(competencia))
    registros = []
    for indice in range(1200):
        regiao,estado,uf = localidades[indice % len(localidades)]
        escala = 15000000/(indice+1)**0.9
        linha = {'competencia':competencia,'codigo_municipio':f'99{indice:05d}',
                 'municipio':f'Município de teste {indice+1:04d}','estado':estado,'uf':uf,'regiao':regiao}
        for papel in ('pagador','recebedor'):
            for pessoa in ('pf','pj'):
                fator = 1 if pessoa == 'pf' else 0.18
                quantidade = max(1,round(escala*fator*gerador.uniform(0.8,1.2)))
                valor_medio = gerador.uniform(80,600) if pessoa == 'pf' else gerador.uniform(800,4500)
                linha[f'quantidade_{papel}_{pessoa}'] = quantidade
                linha[f'valor_{papel}_{pessoa}'] = round(quantidade*valor_medio,2)
                linha[f'pessoas_{papel}_{pessoa}'] = max(1,round(quantidade/gerador.uniform(5,35)))
        registros.append(linha)
    return registros

class ProvedorTeste:
    """Entrega a amostra local usando o mesmo contrato da fonte oficial."""
    modo = 'bcb'
    def obter_periodo(self,inicio: str,fim: str) -> dict:
        registros = gerar_amostra_teste(inicio)
        qualidade = {'recebidos':len(registros),'aceitos':len(registros),'identificadores_excluidos':0,
                     'ausentes':{campo:0 for campo in NUMERICAS}}
        return {'registros':registros,'proveniencia':[{'competencia':inicio,'modo':'bcb','url':'teste local',
            'consultado_em':'2026-09-20T00:00:00-03:00','sha256_normalizado':'0'*64,'qualidade':qualidade}],
            'modo':'bcb','fonte':FONTE,'inicio':inicio,'fim':fim}

@testes.fixture
def registros_teste():
    """Disponibiliza a amostra determinística aos testes de serviço."""
    return gerar_amostra_teste()

@testes.fixture
def cliente():
    """Substitui a comunicação externa por um provedor controlado."""
    anterior = principal.provedor
    principal.provedor = ProvedorTeste()
    principal.acessos.clear()
    with ClienteTeste(principal.aplicacao) as instancia:
        yield instancia
    principal.provedor = anterior
