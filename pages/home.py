#Essa página faz a coleta dos dados que o usuário digitar

import dash
from dash import html, dcc, Input, Output, State

dash.register_page(__name__, path='/', name='Início')

#Cria um layout externo para criar os cards de entrada de dados

'''
Os códigos abaixo utilizam elementos de css, os quias o dash possui suporte
'''

layout = html.Div([
   html.H2("Insira os dados para realizar a consulta de entregadores!", style={'textAlign': 'center', 'marginBottom': '30px'}, className="subtitulo"),
    
    # CARD 1 - Inserir a quantidade de entregadores.
    html.Div([
        html.Label(
            "Número de Entregadores *",
            className="campo-label"
        ),
        html.P(
            "Esse valor serve de base para gerar os entregadores",
            className="campo-descricao"
        ),
        html.Div(
            dcc.Input(
                id="input-numero", #Permite que seja inserido apenas números
                type="number",
                placeholder="Digite a quantidade de entregadores",
                className="campo-input",
                style={'width': '100%', 'boxSizing': 'border-box'}
            ),
            style={'width': '100%'}
        )
    ], className="campo-card"),

    # CARD 2 - Inserir o nome do bar
    html.Div([
        html.Label(
            "Nome do Bar *", 
            className="campo-label"
        ),
        html.P(
            "Digite o nome exato ou o prefixo do bar", 
            className="campo-descricao"
        ),
        html.Div(
            dcc.Input(
                id='input-nome', 
                type='text', 
                placeholder="Ex: Mascate", 
                className="campo-input",
                style={'width': '100%', 'boxSizing': 'border-box'}
            ),
            style={'width': '100%'}
        )
    ], className="campo-card"),
    
    # CARD 3 - Inserir o raio de busca
    html.Div([
        html.Label(
            "Raio de busca (metros) *", 
            className="campo-label"
        ),
        html.P(
            "Distância máxima em metros para buscar entregadores", 
            className="campo-descricao"
        ),
        html.Div(
            dcc.Input(
                id='input-raio', 
                type='number', 
                placeholder="Ex: 2000", 
                className="campo-input",
                style={'width': '100%', 'boxSizing': 'border-box'}
            ),
            style={'width': '100%'}
        )
    ], className="campo-card"),
    
    # Botão para o envio dos dados
    html.Button(
        'Enviar!', 
        id='btn-enviar', 
        n_clicks=0, 
        className="btn-enviar"
    ),
])

'''
Essa função 'observa' o botão de envio, toda vez que o 'n_clicks' é atualizado 
o dash é 'avisado' e roda a função salvar_e_redirecionar
'''


@dash.callback(
    [
        # Salva os dados que o usuário digitou em um 'acesso global' de todas as pa´ginas
        Output('dados-usuario', 'data'),
        
        # Muda a url da página atual
        Output('_pages_location', 'pathname')
    ],
    
    # O botão é o gatilho. Quando o 'n_clicks' mudar, a função roda.
    Input('btn-enviar', 'n_clicks'),
    
    [
        # Essas informações são lidas no exato momento em que o botão é clicado.
        State('input-numero', 'value'),
        State('input-nome', 'value'),
        State('input-raio', 'value')
    ],
    
    prevent_initial_call=True  #Impede que a função seja efetuada quando a página é carregada.
)
def salvar_e_redirecionar(n_clicks, numero, nome, raio):
    '''
    Confere se o botão foi clicado e se nenhum dos componenetes é vazio, 
    caso seja a página não é atualizada
    '''
    if not n_clicks or numero is None or nome is None or raio is None:
        return dash.no_update, dash.no_update

    # Monta o dicionário juntando os valores que o usuário digitou.
    caixa_de_dados = {
        "numero_entregadores": numero,
        "nome_bar": nome,
        "raio": raio
    }

    #Retorna para o Output lá de cima
    # 1. A caixa de dados - lida por todas as páginas
    # 2. A página que deve ser carregada
    return caixa_de_dados, '/mapa'