import os
import sys
import dash
from dash import html, dcc

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# cria a instancia principal da aplicacao
app = dash.Dash(__name__, use_pages=True, suppress_callback_exceptions=True)

# tudo o que estiver aqui aparecerah em todas as paginas do sistema
app.layout = html.Div([

    # uma variavel "global" (dcc.Store)
    # serve para guardar os dados e passa-los de uma pagina para outra sem precisar recarregar o site
    
    dcc.Store(id='dados-usuario'),
    
    # permite mudar a url do navegador quando o usuario clica em um botao, por exemplo
    dcc.Location(id='url', refresh=False, pathname='/'),

    html.H1(
        "Seja Bem-Vindo(a)!",
        className="titulo-principal",
        style={'textAlign': 'center'}
    ),
    
    # menu de navegacao - cria um acesso a todas as paginas na pasta pages
    html.Div([
        html.Div(
            dcc.Link(
                f"{page['name']}",          
                href=page["relative_path"],  
                style={'marginRight': '20px', 'textDecoration': 'none', 'fontSize': '18px', 'fontWeight': 'bold'}
            )
        ) for page in dash.page_registry.values()
    ], style={'display': 'flex', 'justifyContent': 'center', 'padding': '10px'}),
    
    
    # o 'dash.page_container' eh o local exato onde o Dash vai renderizar o conteudo do arquivo 'home.py' ou 'mapa.py', dependendo da URL atual
    dash.page_container
    
], style={'padding': '20px'}) 

# inicia o servidor local da aplicacao
if __name__ == '__main__':
    app.run(debug=True)