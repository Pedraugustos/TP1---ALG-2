# Esse arquivo permite que seja feita toda a parte de interação entre o usuário e o sistema.

import dash
from dash import html, dcc
import sys
import os

# Adiciona a raiz do projeto ao caminho do Python
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Cria a instância principal da aplicação.
app = dash.Dash(__name__, use_pages=True, suppress_callback_exceptions=True)

# Tudo o que estiver aqui aparecerá em todas as páginas do sistema.
app.layout = html.Div([

    # 1. Uma variável "global" (dcc.Store)
    # Serve para guardar os dados e passá-los de uma página para outra sem precisar recarregar o site.
    dcc.Store(id='dados-usuario'),
    
    #permite mudar a url do navegador quando o usuário clica em um botão, por exemplo
    dcc.Location(id='url', refresh=False, pathname='/'),

    html.H1(
        "Seja Bem-Vindo(a)!",
        className="titulo-principal",
        style={'textAlign': 'center'}
    ),
    
    # Menu de navegação - cria um acesso a todas as páginas na páginas pages
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

# --- INICIALIZAÇÃO DO SERVIDOR ---
if __name__ == '__main__':
    app.run(debug=True)