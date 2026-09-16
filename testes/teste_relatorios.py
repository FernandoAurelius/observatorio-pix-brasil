"""Verifica exportações e a composição dos relatórios."""
import pytest as testes
from observatorio_api.relatorios import preparar_evidencias, escrever_resumo
from observatorio_api.esquemas import Filtros
from observatorio_api.catalogo import FONTE
from nucleo_estatistico import simular_grandes_numeros, simular_limite_central, histograma

def teste_relatorio_exportado(cliente):
    resposta=cliente.post('/api/relatorio',json={})
    assert resposta.status_code==200
    assert 'descobertas_202512_202512.md' in resposta.headers['content-disposition']
    assert '1200' in resposta.text
    assert resposta.text.count('### ')==3
    assert 'proveniencia' in resposta.text


def teste_evidencias_preservam_origem(registros_teste):
    conjunto={'registros':registros_teste,'proveniencia':[],'modo':'bcb','fonte':FONTE,'inicio':'202512','fim':'202512'}
    evidencias=preparar_evidencias(conjunto,conjunto['registros'],Filtros())
    assert evidencias['contexto']['modo']=='bcb'
    assert evidencias['contexto']['atende_volume_minimo'] is True
    assert len(evidencias['descobertas'])==3
    assert evidencias['regressao']['modelo']['quantidade']==1200
    assert 'Banco Central do Brasil' in escrever_resumo(evidencias)


@testes.mark.parametrize('semente',[True,1.5,'texto',None])
def teste_simulacao_exige_semente_inteira(semente):
    with testes.raises(ValueError):
        simular_grandes_numeros(semente=semente)
    with testes.raises(ValueError):
        simular_limite_central([1,2,3],repeticoes=50,semente=semente)


@testes.mark.parametrize('resultado',[True,1.0,'cara'])
def teste_moeda_exige_resultado_inteiro(resultado):
    with testes.raises(ValueError):
        simular_grandes_numeros(resultado=resultado)


def teste_histograma_constante_grande():
    classes=histograma([1e20,1e20],20)
    assert sum(classe['frequencia'] for classe in classes)==2
    assert sum(classe['densidade']*(classe['superior']-classe['inferior']) for classe in classes)==testes.approx(1)
