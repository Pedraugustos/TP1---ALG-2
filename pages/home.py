import dash
from dash import html, dcc, Input, Output, State

dash.register_page(__name__, path='/', name='Início')

'''
Cria os cards, nos quais o usuário irá inserir os dados
Usa elementos de HTML e CSS, os quais a biblioteca Dash 
fornece suporte.
'''

layout = html.Div([
   html.H2("Insira os dados para realizar a consulta de entregadores!", style={'textAlign': 'center', 'marginBottom': '30px'}, className="subtitulo"),
    
    # card 1 - inserir a quantidade de entregadores
    html.Div([
        html.Label(
            "NÚMERO DE ENTREGADORES",
            className="campo-label"
        ),
        html.P(
            "Esse valor serve de base para gerar os entregadores.",
            className="campo-descricao"
        ),
        html.Div(
            dcc.Input(
                id="input-numero",
                type="number",  # permite que seja inserido apenas números
                placeholder="Quant. de entregadores",
                className="campo-input",
                style={'width': '100%', 'boxSizing': 'border-box'}
            ),
            style={'width': '100%'}
        )
    ], className="campo-card"),

    # card 2 - inserir o nome do bar
    html.Div([
        html.Label(
            "NOME DO BAR", 
            className="campo-label"
        ),
        html.P(
            "Digite o nome do bar ou o prefixo dele.", 
            className="campo-descricao"
        ),
        html.Div(
            dcc.Input(
                id='input-nomeBar', 
                type='text', 
                placeholder="EX: Mascate", 
                className="campo-input",
                style={'width': '100%', 'boxSizing': 'border-box'}
            ),
            style={'width': '100%'}
        )
    ], className="campo-card"),

    # card 3 - inserir o endereco
    html.Div([
        html.Label(
            "ENDEREÇO",
            className="campo-label"
        ),
        html.P(
            "Digite o endereço do bar ou o prefixo dele.",
            className="campo-descricao"
        ),
        html.Div(
            dcc.Input(
                id='input-endereco',
                type='text',
                placeholder="EX: Rua da bahia, 1234",
                className="campo-input",
                style={'width': '100%', 'boxSizing': 'border-box'}
            ),
            style={'width': '100%'}
        )
    ], className="campo-card"),
    
    # card 4 - inserir o raio de busca
    html.Div([
        html.Label(
            "RAIO DE BUSCA (metros)", 
            className="campo-label"
        ),
        html.P(
            "Distância máxima em metros para buscar entregadores.", 
            className="campo-descricao"
        ),
        html.Div(
            dcc.Input(
                id='input-raio', 
                type='number', # permite que seja inserido apenas numeros
                placeholder="EX: 2000", 
                className="campo-input",
                style={'width': '100%', 'boxSizing': 'border-box'}
            ),
            style={'width': '100%'}
        )
    ], className="campo-card"),
    
    # botao para o envio dos dados
    html.Button(
        'Enviar!', 
        id='btn-enviar', 
        n_clicks=0, 
        className="btn-enviar"
    ),
])

'''
Essa função 'observa' o botão de envio, toda vez que o 'n_clicks' é atualizado 
o dash é 'avisado' e roda a função salvar_e_redirecionar.
'''

@dash.callback(
    [
        # atualiza o armazenamento compartilhado de dados, 
        # permitindo que outras paginas do aplicativo acessem as informacoes
        Output('dados-usuario', 'data'),

        # altera a URL atual para navegar ateh outra pagina
        Output('_pages_location', 'pathname')
    ],

    # esse eh o gatilho do callback, toda vez que a propriedade n_clicks eh
    # atualizada, o dash executa a funcao salvar_e_redirecionar automaticamente
    Input('btn-enviar', 'n_clicks'),

    [
        # os states fornecem a funcao os valores atuais dos campos quando o input eh acionado
        State('input-numero', 'value'),
        State('input-nomeBar', 'value'),
        State('input-endereco', 'value'),
        State('input-raio', 'value')
    ],

    # impede que o callback seja executado automaticamente na inicializacao
    prevent_initial_call=True
)

def salvar_e_redirecionar(n_clicks, numero, nomeBar, endereco, raio):   
    '''
    Esta função é chamada automaticamente pelo Dash quando o usuário clica
    no botão 'btn-enviar'.
    O Dash passa os valores do Input e dos State como argumentos.
    '''
    
    # verifica se o botao foi acionado e se os campos de numero de entregadores e raio
    # foram preenchidos, se nao foram, nao atualiza os dados nem navega para outra pagina
    if (not n_clicks) or (numero is None) or (raio is None):
        return dash.no_update, dash.no_update

    # remove espacos extras do inicio e do final dos textos
    nomeBar = (nomeBar or "").strip()
    endereco = (endereco or "").strip()

    # exige que pelo menos um dos campos, nome ou endereco, esteja preenchido
    # se ambos estiverem vazios, nao atualiza os dados nem navega para outra pagina
    if (not nomeBar) and (not endereco):
        return dash.no_update, dash.no_update

    # dicionario com os dados informados pelo usuario que serah enviado ao primeiro output do callback
    caixa_de_dados = {
        "numero_entregadores": numero,
        "nomeBar": nomeBar,
        "endereco": endereco,
        "raio": raio
    }

    # atualiza 'dados-usuario' com o dicionario caixa_de_dados
    # atualiza '_pages_location.pathname' para '/mapa'
    return caixa_de_dados, '/mapa'