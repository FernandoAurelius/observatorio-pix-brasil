"""Dicionário de campos: nomes externos somente na fronteira com o BCB."""
FONTE = 'https://dadosabertos.bcb.gov.br/dataset/pix'
DOCUMENTACAO_API = 'https://olinda.bcb.gov.br/olinda/servico/Pix_DadosAbertos/versao/v1/swagger'
ENDERECO_BCB = 'https://olinda.bcb.gov.br/olinda/servico/Pix_DadosAbertos/versao/v1/odata/TransacoesPixPorMunicipio(DataBase=@DataBase)'
NUMERICAS = {}
for papel, rotulo_papel in [('pagador','pagos'),('recebedor','recebidos')]:
    for pessoa in ('pf','pj'):
        sufixo = papel.capitalize()+pessoa.upper()
        descricao = 'pessoa física' if pessoa == 'pf' else 'pessoa jurídica'
        NUMERICAS[f'valor_{papel}_{pessoa}'] = {'original':f'VL_{sufixo}', 'rotulo':f'Valor {rotulo_papel} por {pessoa.upper()}', 'unidade':'real_brasileiro', 'tipo':'continua', 'descricao':f'Volume financeiro em reais (R$) de Pix {rotulo_papel} por {descricao}; sem reescalonamento do valor publicado.'}
        NUMERICAS[f'quantidade_{papel}_{pessoa}'] = {'original':f'QT_{sufixo}', 'rotulo':f'Transações {rotulo_papel} por {pessoa.upper()}', 'unidade':'transacoes', 'tipo':'discreta', 'descricao':f'Quantidade de transações {rotulo_papel} por {descricao}.'}
        NUMERICAS[f'pessoas_{papel}_{pessoa}'] = {'original':f'QT_PES_{sufixo}', 'rotulo':f'Pessoas {pessoa.upper()} ({papel})', 'unidade':'pessoas', 'tipo':'discreta', 'descricao':'Quantidade de pessoas na observação municipal mensal. Não somar entre meses para obter pessoas únicas.'}
CATEGORICAS = {'municipio':'Município', 'estado':'Estado', 'uf':'UF', 'regiao':'Região'}
UNIDADES_FEDERATIVAS = {'11':'RO','12':'AC','13':'AM','14':'RR','15':'PA','16':'AP','17':'TO','21':'MA','22':'PI','23':'CE','24':'RN','25':'PB','26':'PE','27':'AL','28':'SE','29':'BA','31':'MG','32':'ES','33':'RJ','35':'SP','41':'PR','42':'SC','43':'RS','50':'MS','51':'MT','52':'GO','53':'DF'}
