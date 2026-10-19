import dash
from dash import html, dcc, Input, Output, State


dash.register_page(__name__, path='/', name='Início')

'''
Cria os cards, nos quais o usuário irá inserir os dados
Usa elementos de HTML e CSS, os quais a biblioteca Dash 
fornece suporte
'''

layout = html.Div([
   html.H2("Insira os dados para realizar a consulta de entregadores!", style={'textAlign': 'center', 'marginBottom': '30px'}, className="subtitulo"),
    
    # card 1 - inserir a quantidade de entregadores.
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
                id="input-numero",
                type="number",  # permite que seja inserido apenas números
                placeholder="Digite a qntd de entrega.",
                className="campo-input",
                style={'width': '100%', 'boxSizing': 'border-box'}
            ),
            style={'width': '100%'}
        )
    ], className="campo-card"),

    # card 2 - inserir o nome do bar
    html.Div([
        html.Label(
            "Nome do Bar *", 
            className="campo-label"
        ),
        html.P(
            "Digite o nome do bar ou o prefixo dele", 
            className="campo-descricao"
        ),
        html.Div(
            dcc.Input(
                id='input-nomeBar', 
                type='text', 
                placeholder="Ex: Mascate", 
                className="campo-input",
                style={'width': '100%', 'boxSizing': 'border-box'}
            ),
            style={'width': '100%'}
        )
    ], className="campo-card"),

    # card 3 - inserir o endereço
    html.Div([
        html.Label(
            "Endereço",
            className="campo-label"
        ),
        html.P(
            "Digite o endereço do bar ou o prefixo dele",
            className="campo-descricao"
        ),
        html.Div(
            dcc.Input(
                id='input-endereco',
                type='text',
                placeholder="Ex: RUA DA BAHIA 1234",
                className="campo-input",
                style={'width': '100%', 'boxSizing': 'border-box'}
            ),
            style={'width': '100%'}
        )
    ], className="campo-card"),
    
    # card 4 - inserir o raio de busca
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
                type='number', # permite que seja inserido apenas números
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
        
        # atualiza o armazenamento compartilhado de dados,
        # permitindo que outras páginas do aplicativo acessem as informações.
        Output('dados-usuario', 'data'),

        # altera a URL atual para navegar até outra página.
        Output('_pages_location', 'pathname')
    ],

    # esse é o gatilho do callback, toda vez que a propriedade n_clicks é atualizada
    # o dash executa a função salvar_e_redirecionar automaticamente
    Input('btn-enviar', 'n_clicks'),

    [
        # os state fornecem à função os valores atuais dos campos quando o Input é acionado. =
        State('input-numero', 'value'),
        State('input-nomeBar', 'value'),
        State('input-endereco', 'value'),
        State('input-raio', 'value')
    ],

    # impede que o callback seja executado automaticamente na inicialização.
    prevent_initial_call=True
)



def salvar_e_redirecionar(n_clicks, numero, nomeBar, endereco, raio):
    
    '''
    Esta função é chamada automaticamente pelo Dash quando o usuário clica
    no botão 'btn-enviar'.
    O Dash passa os valores do Input e dos State como argumentos.
    '''
    
    # verifica se o botão foi acionado e se os campos de número de entregadores e raio foram preenchidos,
    # se não foram, não atualiza os dados nem navega para outra página.
    if (not n_clicks) or (numero is None) or (raio is None):
        return dash.no_update, dash.no_update

    # remove espaços extras do início e do final dos textos.
    nomeBar = (nomeBar or "").strip()
    endereco = (endereco or "").strip()

    # exige que pelo menos um dos campos, nome ou endereço, esteja preenchido.
    # se ambos estiverem vazios, não atualiza os dados nem navega para outra página.
    if (not nomeBar) and (not endereco):
        return dash.no_update, dash.no_update

    # dicionário com os dados informados pelo usuário que será enviado ao primeiro Output do callback.
    caixa_de_dados = {
        "numero_entregadores": numero,
        "nomeBar": nomeBar,
        "endereco": endereco,
        "raio": raio
    }

    # atualiza 'dados-usuario' com o dicionário caixa_de_dados.
    # atualiza '_pages_location.pathname' para '/mapa'
    return caixa_de_dados, '/mapa'