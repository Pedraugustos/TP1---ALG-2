import dash
from dash import html, dcc
import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# cria a instância principal da aplicação.
app = dash.Dash(__name__, use_pages=True, suppress_callback_exceptions=True)

# tudo o que estiver aqui aparecerá em todas as páginas do sistema.
app.layout = html.Div([

    # uma variável "global" (dcc.Store)
    # serve para guardar os dados e passá-los de uma página para outra sem precisar recarregar o site.
    
    dcc.Store(id='dados-usuario'),
    
    # permite mudar a url do navegador quando o usuário clica em um botão, por exemplo
    dcc.Location(id='url', refresh=False, pathname='/'),

    html.H1(
        "Seja Bem-Vindo(a)!",
        className="titulo-principal",
        style={'textAlign': 'center'}
    ),
    
    # menu de navegação - cria um acesso a todas as páginas na pasta pages
    html.Div([
        html.Div(
            dcc.Link(
                f"{page['name']}",          
                href=page["relative_path"],  
                style={'marginRight': '20px', 'textDecoration': 'none', 'fontSize': '18px', 'fontWeight': 'bold'}
            )
        ) for page in dash.page_registry.values()
    ], style={'display': 'flex', 'justifyContent': 'center', 'padding': '10px'}),
    
    
    # O 'dash.page_container' é o local exato onde o Dash vai renderizar o conteúdo do arquivo 'home.py' ou 'mapa.py', dependendo da URL atual.
    dash.page_container
    
], style={'padding': '20px'}) 

# inicia o servidor local da aplicação
if __name__ == '__main__':
    app.run(debug=True)