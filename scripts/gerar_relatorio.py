"""Coleta dados oficiais e gera as descobertas e figuras do estudo."""
import sys as sistema
from pathlib import Path as Caminho
RAIZ = Caminho(__file__).resolve().parents[1]
sistema.path[:0] = [str(RAIZ/'pacotes'),str(RAIZ/'aplicacoes/api')]
import argparse as argumentos
import json as serializacao
import html as marcacao
from observatorio_api.provedor_bcb import ProvedorBCB
from observatorio_api.esquemas import Filtros
from observatorio_api.relatorios import preparar_evidencias, escrever_resumo
from observatorio_api import servicos

def gravar_figura(destino: Caminho, titulo: str, elementos: str):
    """Grava SVG acessível com valores já calculados; não calcula estatística."""
    selo = 'Fonte: Banco Central do Brasil / núcleo próprio'
    texto = f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="450" viewBox="0 0 900 450" role="img"><title>{marcacao.escape(titulo)}</title><rect width="900" height="450" fill="#faf8ff"/><text x="50" y="38" font-family="sans-serif" font-size="20" fill="#004331">{marcacao.escape(titulo)}</text><text x="50" y="63" font-family="sans-serif" font-size="11" fill="#667080">{selo}</text>{elementos}<text x="50" y="425" font-family="sans-serif" font-size="10" fill="#667080">Coordenadas de visualizacao; resultados do mesmo servico da aplicacao.</text></svg>'
    destino.write_text(texto,encoding='utf-8')

def gerar_figuras(evidencias: dict, destino: Caminho):
    """Desenha concentração, histograma e dispersão a partir das respostas da API."""
    municipios = evidencias['panorama']['municipios'][:8]
    pico = max((linha['valor'] for linha in municipios),default=1) or 1
    elementos = ''
    for indice,linha in enumerate(municipios):
        altura = 95+indice*36
        elementos += f'<text x="50" y="{altura+15}" font-family="sans-serif" font-size="10">{marcacao.escape(linha["municipio"][:31])}</text><rect x="265" y="{altura}" width="{linha["valor"]/pico*450}" height="24" fill="#0d5c46"/><text x="725" y="{altura+15}" font-family="monospace" font-size="10">{linha["valor"]:.4g}</text>'
    gravar_figura(destino/'concentracao.svg','Maiores valores pagos (PF + PJ; lado pagador)',elementos)
    classes = evidencias['descritiva']['frequencias']
    pico = max(classe['frequencia'] for classe in classes) or 1
    elementos = ''
    for indice,classe in enumerate(classes):
        altura = classe['frequencia']/pico*270
        elementos += f'<rect x="{65+indice*760/len(classes)}" y="{365-altura}" width="{760/len(classes)-1}" height="{altura}" fill="#0d5c46"><title>{classe["inferior"]:.6g} a {classe["superior"]:.6g}: {classe["frequencia"]}</title></rect>'
    elementos += f'<text x="60" y="390" font-size="11" font-family="monospace">{classes[0]["inferior"]:.6g}</text><text x="730" y="390" font-size="11" font-family="monospace">{classes[-1]["superior"]:.6g}</text><text x="65" y="88" font-size="11" font-family="sans-serif">Frequencia maxima: {pico}</text>'
    gravar_figura(destino/'histograma.svg','Distribuicao da quantidade de Pix pagos por PF',elementos)
    regressao = evidencias['regressao']; pontos = regressao['pontos']; reta = regressao['reta']
    menor_x = min(ponto['valor_x'] for ponto in pontos); maior_x = max(ponto['valor_x'] for ponto in pontos)
    menor_y = min(ponto['valor_y'] for ponto in pontos+reta); maior_y = max(ponto['valor_y'] for ponto in pontos+reta)
    def coordenada_x(valor):
        """Transforma a escala de X em posição na figura."""
        return 65+760*(valor-menor_x)/(maior_x-menor_x or 1)
    def coordenada_y(valor):
        """Transforma a escala de Y em posição na figura."""
        return 365-270*(valor-menor_y)/(maior_y-menor_y or 1)
    elementos = ''.join(f'<circle cx="{coordenada_x(ponto["valor_x"])}" cy="{coordenada_y(ponto["valor_y"])}" r="2" fill="#0d5c46" opacity=".35"/>' for ponto in pontos)
    elementos += f'<line x1="{coordenada_x(reta[0]["valor_x"])}" y1="{coordenada_y(reta[0]["valor_y"])}" x2="{coordenada_x(reta[1]["valor_x"])}" y2="{coordenada_y(reta[1]["valor_y"])}" stroke="#4764ed" stroke-width="2"/><text x="65" y="389" font-family="monospace" font-size="11">X: quantidade de transacoes ({menor_x:.4g} a {maior_x:.4g}); Y: valor pago ({menor_y:.4g} a {maior_y:.4g})</text>'
    gravar_figura(destino/'regressao.svg','Quantidade x valor pago por PF; reta de minimos quadrados',elementos)

def executar(inicio: str, fim: str) -> Caminho:
    """Recupera o recorte completo e grava somente evidências, não um banco local."""
    filtros = Filtros(inicio=inicio,fim=fim)
    provedor = ProvedorBCB()
    conjunto = provedor.obter_periodo(inicio,fim)
    registros = servicos.filtrar(conjunto,filtros)
    if len(registros)<1000:
        raise ValueError('A fonte retornou menos de 1.000 registros; este recorte não atende ao Módulo 0.')
    evidencias = preparar_evidencias(conjunto,registros,filtros)
    destino = RAIZ/'documentacao/resultados_bcb'
    destino.mkdir(parents=True,exist_ok=True)
    (destino/'evidencias.json').write_text(serializacao.dumps(evidencias,ensure_ascii=False,indent=2),encoding='utf-8')
    texto = escrever_resumo(evidencias)+'\n## Gráficos gerados pelo mesmo serviço\n\n![Concentração](concentracao.svg)\n\n![Histograma](histograma.svg)\n\n![Regressão](regressao.svg)\n'
    (destino/'DESCOBERTAS.md').write_text(texto,encoding='utf-8')
    gerar_figuras(evidencias,destino)
    print(f"Modo={provedor.modo}; {len(registros)} registros; evidências gravadas em {destino}.")
    return destino

if __name__ == '__main__':
    analisador = argumentos.ArgumentParser(description=__doc__)
    analisador.add_argument('--inicio',default='202501');analisador.add_argument('--fim',default='202512')
    opcoes = analisador.parse_args()
    executar(opcoes.inicio,opcoes.fim)
