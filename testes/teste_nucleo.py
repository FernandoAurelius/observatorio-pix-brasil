"""Compara todas as funções principais com bibliotecas de referência."""
import math as matematica
import statistics as estatistica_padrao
import numpy as referencia_numerica
from scipy import stats as referencia_estatistica
import pytest as testes
from nucleo_estatistico import *

TOLERANCIA_RELATIVA = 1e-9
TOLERANCIA_ABSOLUTA = 1e-9
CONJUNTOS = [[1,2,3,4,5],[1,1,2,2,8],[4],[-20,-2,0,3,12],
    [0.1,0.2,0.3,0.4],[1000000000000+indice*0.5 for indice in range(100)],
    referencia_numerica.random.default_rng(123).normal(20,5,1000).tolist()]

def comparar(obtido,esperado):
    """Combina tolerância relativa e absoluta; ambas são documentadas."""
    assert obtido == testes.approx(esperado,rel=TOLERANCIA_RELATIVA,abs=TOLERANCIA_ABSOLUTA)

@testes.mark.parametrize('valores',CONJUNTOS)
def teste_medidas_basicas(valores):
    comparar(soma(valores),referencia_numerica.sum(valores))
    comparar(media(valores),referencia_numerica.mean(valores))
    comparar(mediana(valores),referencia_numerica.median(valores))
    comparar(amplitude(valores),referencia_numerica.ptp(valores))
    comparar(quartis(valores),referencia_numerica.percentile(valores,[25,50,75],method='linear'))
    maior_contagem = max(valores.count(valor) for valor in valores)
    esperado = sorted(estatistica_padrao.multimode(valores)) if maior_contagem>1 else []
    assert moda(valores) == esperado

@testes.mark.parametrize('valores',CONJUNTOS)
@testes.mark.parametrize('amostral',[False,True])
def teste_dispersao(valores,amostral):
    if amostral and len(valores)<2:
        with testes.raises(ValueError):variancia(valores,amostral)
        return
    comparar(variancia(valores,amostral),referencia_numerica.var(valores,ddof=int(amostral)))
    comparar(desvio_padrao(valores,amostral),referencia_numerica.std(valores,ddof=int(amostral)))
    if referencia_numerica.mean(valores)!=0:
        comparar(coeficiente_variacao(valores,amostral),100*abs(referencia_estatistica.variation(valores,ddof=int(amostral))))

@testes.mark.parametrize('percentual',[0,1,10,25,33.3,50,75,90,99,100])
@testes.mark.parametrize('valores',CONJUNTOS)
def teste_percentis(percentual,valores):
    comparar(percentil(valores,percentual),referencia_numerica.percentile(valores,percentual,method='linear'))

@testes.mark.parametrize('amostral',[False,True])
def teste_covariancia(amostral):
    valores_x = [1,2,5,8,20]
    valores_y = [3,1,12,8,11]
    comparar(covariancia(valores_x,valores_y,amostral),referencia_numerica.cov(valores_x,valores_y,ddof=int(amostral))[0,1])


def teste_api_academica_com_nomes_explicitos():
    valores = [-2.5, 0.0, 3.5, 3.5, 9.0]
    respostas = [8.0, 4.0, 1.0, 1.0, -3.0]
    comparar(calcular_media(valores), referencia_numerica.mean(valores))
    comparar(calcular_mediana(valores), referencia_numerica.median(valores))
    assert calcular_moda(valores) == [3.5]
    comparar(calcular_amplitude(valores), referencia_numerica.ptp(valores))
    comparar(calcular_variancia_populacional(valores), referencia_numerica.var(valores))
    comparar(calcular_variancia_amostral(valores), referencia_numerica.var(valores, ddof=1))
    comparar(calcular_desvio_padrao_populacional(valores), referencia_numerica.std(valores))
    comparar(calcular_desvio_padrao_amostral(valores), referencia_numerica.std(valores, ddof=1))
    comparar(calcular_percentil(valores, 90), referencia_numerica.percentile(valores, 90))
    comparar(calcular_quartis(valores), referencia_numerica.percentile(valores, [25, 50, 75]))
    comparar(calcular_coeficiente_variacao(valores),
             100 * referencia_numerica.std(valores, ddof=1) / abs(referencia_numerica.mean(valores)))
    comparar(calcular_covariancia(valores, respostas), referencia_numerica.cov(valores, respostas)[0, 1])
    comparar(calcular_correlacao_pearson(valores, respostas),
             referencia_numerica.corrcoef(valores, respostas)[0, 1])

@testes.mark.parametrize('semente',range(10))
def teste_regressao_pearson_determinacao(semente):
    gerador = referencia_numerica.random.default_rng(semente)
    valores_x = gerador.normal(100,20,150).tolist()
    valores_y = (3*referencia_numerica.array(valores_x)+gerador.normal(0,15,150)-5).tolist()
    modelo = regressao_linear(valores_x,valores_y)
    referencia = referencia_estatistica.linregress(valores_x,valores_y)
    comparar(modelo['inclinacao'],referencia.slope)
    comparar(modelo['intercepto'],referencia.intercept)
    comparar(modelo['pearson'],referencia.rvalue)
    comparar(correlacao_pearson(valores_x,valores_y),referencia_numerica.corrcoef(valores_x,valores_y)[0,1])
    comparar(modelo['r_quadrado'],referencia.rvalue**2)
    comparar(coeficiente_determinacao(valores_y,modelo['previstos']),referencia.rvalue**2)
    comparar(predizer(150,modelo['intercepto'],modelo['inclinacao']),referencia.intercept+150*referencia.slope)

@testes.mark.parametrize('classes',[1,3,10,25,100])
@testes.mark.parametrize('valores',CONJUNTOS)
def teste_histograma(classes,valores):
    linhas = histograma(valores,classes)
    limites = [linha['inferior'] for linha in linhas]+[linhas[-1]['superior']]
    esperado,_limites = referencia_numerica.histogram(valores,bins=limites)
    assert [linha['frequencia'] for linha in linhas] == esperado.tolist()
    comparar(sum(linha['relativa'] for linha in linhas),1)
    comparar(sum(linha['densidade']*(linha['superior']-linha['inferior']) for linha in linhas),1)
    assert linhas[-1]['acumulada'] == len(valores)
    comparar(linhas[-1]['relativa_acumulada'],1)


def teste_atipicos():
    valores = [1,2,3,4,5,6,7,8,9,100]
    caixa = detectar_atipicos(valores)
    primeiro,terceiro = referencia_numerica.percentile(valores,[25,75])
    intervalo = referencia_estatistica.iqr(valores)
    esperado = [valor for valor in valores if valor<primeiro-1.5*intervalo or valor>terceiro+1.5*intervalo]
    assert caixa['valores'] == esperado
    comparar(caixa['iqr'],intervalo)
    assert caixa['bigode_superior'] == 9


def teste_assimetria():
    valores = [0,1,1,2,2,3,5,25]
    comparar(assimetria(valores),referencia_estatistica.skew(valores,bias=True))


def teste_categoricas():
    valores = ['DF','SP','DF','GO','GO','GO']
    obtido = frequencias_categoricas(valores)
    categorias,contagens = referencia_numerica.unique(valores,return_counts=True)
    assert {linha['categoria']:linha['frequencia'] for linha in obtido} == dict(zip(categorias,contagens))
    comparar(sum(linha['relativa'] for linha in obtido),1)

@testes.mark.parametrize('valor',[-10,-1,0,0.5,1,2,5,10,100])
def teste_densidades(valor):
    comparar(densidade_normal(valor,1,3),referencia_estatistica.norm.pdf(valor,loc=1,scale=3))
    comparar(densidade_exponencial(valor,0.2),referencia_estatistica.expon.pdf(valor,scale=5))
    comparar(densidade_uniforme(valor,-1,5),referencia_estatistica.uniform.pdf(valor,loc=-1,scale=6))
    comparar(massa_poisson(valor,4),referencia_estatistica.poisson.pmf(valor,4))

@testes.mark.parametrize('intensidade',[0,0.1,3,100,100000])
def teste_poisson_numerica(intensidade):
    for valor in [0,1,2,round(intensidade),round(intensidade+matematica.sqrt(intensidade))]:
        comparar(massa_poisson(valor,intensidade),referencia_estatistica.poisson.pmf(valor,intensidade))

@testes.mark.parametrize('familia',['normal','exponencial','uniforme','poisson'])
def teste_estimacao(familia):
    valores = [1,2,3,4,8,10]
    ajuste = ajustar_distribuicao(valores,familia)
    parametros = ajuste['parametros']
    if familia=='normal':
        centro,desvio = referencia_estatistica.norm.fit(valores)
        comparar(parametros['media'],centro);comparar(parametros['desvio_populacional'],desvio)
    if familia=='exponencial':
        _localizacao,escala = referencia_estatistica.expon.fit(valores,floc=0)
        comparar(parametros['taxa'],1/escala)
    if familia=='uniforme':
        localizacao,escala = referencia_estatistica.uniform.fit(valores)
        comparar(parametros['inferior'],localizacao);comparar(parametros['superior'],localizacao+escala)
    if familia=='poisson':comparar(parametros['intensidade'],referencia_numerica.mean(valores))

@testes.mark.parametrize('funcao',[media,mediana,moda,amplitude,variancia,desvio_padrao,quartis,coeficiente_variacao,assimetria,detectar_atipicos,resumo])
def teste_vazio(funcao):
    with testes.raises(ValueError):funcao([])

@testes.mark.parametrize('valor',[float('nan'),float('inf'),-float('inf')])
def teste_nao_finitos(valor):
    with testes.raises(ValueError):media([1,valor])

@testes.mark.parametrize('valor',[True,False,'2',None])
def teste_nao_numericos(valor):
    with testes.raises(TypeError):media([1,valor])


def teste_casos_limite():
    assert soma([])==0
    assert moda([1,2,3])==[]
    assert moda([2,2,3,3])==[2.0,3.0]
    assert variancia([4],False)==0
    with testes.raises(ValueError):coeficiente_variacao([-1,1])
    with testes.raises(ValueError):correlacao_pearson([1,1],[2,3])
    with testes.raises(ValueError):regressao_linear([1,1],[2,3])
    with testes.raises(ValueError):covariancia([1,2],[2,3,4])
    with testes.raises(ValueError):percentil([1,2],101)
    with testes.raises(ValueError):percentil([1,2],-1)
    with testes.raises(ValueError):densidade_normal(0,0,0)
    with testes.raises(ValueError):densidade_uniforme(0,2,2)
    with testes.raises(ValueError):densidade_exponencial(0,-1)
    with testes.raises(ValueError):massa_poisson(0,-1)
    with testes.raises(ValueError):ajustar_distribuicao([0.5,1.2],'poisson')
    with testes.raises(ValueError):ajustar_distribuicao([-1,2],'exponencial')
    with testes.raises(ValueError):ajustar_distribuicao([1,2],'inexistente')
    with testes.raises(ValueError):histograma([1,2],0)
    constante = regressao_linear([1,2,3],[7,7,7])
    assert constante['r_quadrado'] is None and constante['pearson'] is None
    assert constante['inclinacao']==0 and constante['intercepto']==7
    assert resumo([0,0])['coeficiente_variacao'] is None


def teste_imutabilidade():
    valores = [5,1,3,2,9]
    original = list(valores)
    mediana(valores);quartis(valores);detectar_atipicos(valores);resumo(valores)
    assert valores == original


def teste_lgn_reprodutivel():
    primeiro = simular_grandes_numeros(10000,'dado',3,123)
    segundo = simular_grandes_numeros(10000,'dado',3,123)
    assert primeiro == segundo
    assert primeiro['frequencia_final'] == primeiro['acertos']/10000
    assert abs(primeiro['frequencia_final']-1/6)<0.03
    assert primeiro['pontos'][-1]['repeticao']==10000
    with testes.raises(ValueError):simular_grandes_numeros(10,'moeda',6)


def teste_tcl_reprodutivel_e_erro_padrao():
    valores = [1,2,2,3,3,5,8,30]
    resultado = simular_limite_central(valores,30,1000,42)
    assert resultado == simular_limite_central(valores,30,1000,42)
    comparar(resultado['media_das_medias'],referencia_numerica.mean(resultado['medias']))
    comparar(resultado['desvio_das_medias'],referencia_numerica.std(resultado['medias'],ddof=1))
    comparar(resultado['erro_padrao'],referencia_numerica.std(valores)/matematica.sqrt(30))
    assert abs(resultado['media_das_medias']-media(valores))<0.3
    with testes.raises(ValueError):simular_limite_central(valores,1000,10000)
    assert simular_limite_central([2,2,2],5,50)['curva']==[]
