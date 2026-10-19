import os
import re
import sys
import dash
from dash import html, dcc, Input, Output
import dash_leaflet as dl
import osmnx as ox
from src.auxiliares import busca_inteligente, busca_entregadores, cria_tabela
from src.bar import le_bares
from src.entregador import gera_entregadores, encontra_vias_proximas
from src.triecompacta import TRIECompacta

# necessario para configurar o caminho entre as paginas 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# coordenadas da regiao a ser plotada
LATREGMIN, LATREGMAX = -20.1, -19.7
LONGREGMIN, LONGREGMAX = -44.1, -43.8

# limite de bares a serem plotados
LIMITEBARES = 8

# velocidade media dos entregadores
VELOCIDADE = 8  # m/s corresponde a aproximadamente 30 km

# cores para a plotagem dos bares
CORES = ['#e74c3c', "#f843bc", '#f1c40f', '#3498db', '#9b59b6', '#e67e22']

dash.register_page(__name__, path='/mapa', name='Resultado')

# carrega o grafo das vias
caminhoGrafo = "dados/bh_drive.graphml"

if os.path.exists(caminhoGrafo):
    G = ox.load_graphml(caminhoGrafo)
    print("Grafo carregado do disco.")

else:
    G = ox.graph_from_place("Belo Horizonte, Brazil", network_type="drive")
    ox.save_graphml(G, caminhoGrafo)
    print("Grafo baixado e salvo em disco.")

# projeta
Gproj = ox.project_graph(G)
print("Grafo projetado.")

# essa parte define o que o usuario ve assim que a pagina do mapa eh carregada
layout = html.Div([
    html.H2("Resultado da Consulta", style={'textAlign': 'center', 'marginBottom': '20px'}, className="subtitulo"),
    
    # botao que permite ao usuario voltar para a pagina inicial e fazer uma nova busca
    html.Div([
        dcc.Link("← Voltar para nova consulta", href="/", className="btn-voltar"),
    ], style={'textAlign': 'center', 'marginBottom': '15px'}),
    
    # essa eh um espaço vazio, no qual o mapa serah carregado
    html.Div(id='resultado-main', style={'maxWidth': '1000px', 'margin': '0 auto', 'borderRadius': '12px', 'overflow': 'hidden', 'boxShadow': '0 4px 12px rgba(0,0,0,0.1)'}) 
], style={'padding': '20px'})


# o Dash serah responsavel por chamar executar_main quando a propriedade 'data' do componente 'dados-usuario' for atualizada

@dash.callback(
    # define onde o resultado da funcao serah exibido:
    # no espaço reservado acima
    Output('resultado-main', 'children'),

    # define o gatilho do callback
    # quando os dados do dcc.Store forem atualizados, o Dash executarah
    # executar_main e passarah os dados armazenados como argumento
    Input('dados-usuario', 'data')
)

def executar_main(dados_recebidos):
    '''
    Recebe os dados informados pelo usuário na página inicial e executa
    a lógica principal do sistema: busca os bares correspondentes, identifica
    os entregadores dentro do raio definido e apresenta os resultados em um
    mapa interativo e em uma tabela.
    '''

    # caso a pagina seja acessada sem passar pela inicial
    if dados_recebidos is None:
        return "Nenhum dado recebido. Volte para a página inicial."

    try:
        # extraindo as variaveis do dicionario recebido
        N = dados_recebidos["numero_entregadores"]
        raio = dados_recebidos["raio"]
        
        # tranforma o nome do bar todo em maiusculo, jah que eh assim que estah no banco de dados
        nomeBar = str(dados_recebidos["nomeBar"]).upper()

        # caminho do arquivo fonte dos bares
        caminhoArquivo = "dados/bares_coordenadas.csv"

        # seleciona os bares validos do arquivo
        bares, erros = le_bares(caminhoArquivo)

        # sorteia N entregadores nos limites delimitados por (LATMIN, LATMAX) e (LONGMIN, LONGMAX)
        entregadores = gera_entregadores(bares, N)
        
        # projeta os entregadores nas vias mais proximas
        entregadores = encontra_vias_proximas(entregadores, G)

        # arvore TRIE COMPACTA para entregadores
        trieEntr = TRIECompacta()

        # insere cada entregador na arvore
        for entregador in entregadores:
            trieEntr.insere(entregador.geohash(), entregador)

        # arvore TRIE COMPACTA para bares (nome)
        trieBar = TRIECompacta()

        # insere cada bar na arvore
        for bar in bares:
            trieBar.insere(bar.nome(), bar)

        # arvore TRIE COMPACTA para bares (endereco)
        trieEnder = TRIECompacta()
        for bar in bares:
            trieEnder.insere(bar.chave_endereco(), bar)

        # --- BUSCA ---
        enderecoBar = str(dados_recebidos.get("endereco") or "").upper()
        enderecoBar = re.sub(r'[,.;]', ' ', enderecoBar) # troca virgula/ponto por espaço
        enderecoBar = " ".join(enderecoBar.split()) # remove espacos extras

        prefixoBar = nomeBar

        # busca os bares que batem com o prefixo do nome digitado
        bares = busca_inteligente(trieBar, trieEnder, prefixoBar, enderecoBar)

        if len(bares) == 0:
            return html.Div([
                html.H3("Nenhum bar encontrado", style={'color': '#c0392b'}),
                html.P("Verifique o nome ou o endereço informado e tente novamente.",
                    style={'color': 'white'}),
                dcc.Link("← Voltar e tentar de novo", href="/", className="btn-voltar"),
            ], style={'textAlign': 'center', 'padding': '40px'})

        if len(bares) > LIMITEBARES:
            return html.Div([
                html.H3(f"Muitos bares encontrados! ({len(bares)})",
                        style={'color': '#e67e22'}),
                html.P(
                    f"A busca retornou {len(bares)} bares! "
                    "Seja mais específico: informe mais caracteres do nome ou do endereço.",
                    style={'color': 'white'}
                ),
                dcc.Link("← Voltar e refinar a busca", href="/", className="btn-voltar"),
            ], style={'textAlign': 'center', 'padding': '40px'})
        
        # chama a funcao que encontra os entregadores dentro do raio do bar
        resultado = busca_entregadores(bares, trieEntr, raio, Gproj)

        # cria a tabela com os dados dos entregadores
        tabela = cria_tabela(resultado, VELOCIDADE)

        # agrupa entregadores por bar
        entregadoresPorBar = {}
        for bar, entregador, distReta in resultado:
            if bar.nome() not in entregadoresPorBar:
                entregadoresPorBar[bar.nome()] = []
            entregadoresPorBar[bar.nome()].append(entregador)

        # conjunto de chaves capturadas
        chavesCapturadas = set()
        for listaEntregadores in entregadoresPorBar.values():
            for entregador in listaEntregadores:
                chavesCapturadas.add(entregador.chave())

        # preparacao visual (mapa e legenda)

        marcBares = []
        marcEntregadores = []
        corPorBar = {}
        legenda_itens = []
        
        # loop para desenhar os bares selecionados (pinos coloridos)
        for i, bar in enumerate(bares):
            cor = CORES[i % len(CORES)] # pega uma cor ciclica da lista
            corPorBar[bar.nome()] = cor # associa a cor ao nome do bar
            
            # HTML para criar o formato de pino de mapas
            icone_bar_html = f"""
                <div style="
                    background-color: {cor};
                    width: 22px;
                    height: 22px;
                    border-radius: 50% 50% 50% 0;
                    transform: rotate(-45deg);
                    border: 3px solid white;
                    box-shadow: 0 0 5px rgba(0,0,0,0.5);
                "></div>
            """
            
            # define as opcoes de aparencia e posicionamento do icone personalizado do bar
            opcoes_icone = {
                'html': icone_bar_html,
                'iconSize': [25, 25],  
                'iconAnchor': [22, 22] 
            }

            # adiciona a lista de marcadores um pino para representar o bar no mapa
            marcBares.append(
                dl.DivMarker(
                    position=[bar.latitude(), bar.longitude()],
                    children=[dl.Tooltip(f"📍 Bar: {bar.nome()}")],
                    iconOptions=opcoes_icone
                )
            )
            
            # cria um quadrado colorido na legenda para cada bar
            legenda_itens.append(
                html.Div([
                    html.Div(style={
                        'width': '16px', 'height': '16px', 'backgroundColor': cor, 
                        'borderRadius': '50%', 'display': 'inline-block', 'marginRight': '10px',
                        'border': '2px solid white', 'boxShadow': '0 0 3px rgba(0,0,0,0.3)'
                    }),
                    html.Span(bar.nome(), style={'fontSize': '14px', 'fontWeight': 'bold'})
                ], style={'marginBottom': '8px', 'display': 'flex', 'alignItems': 'center'})
            )

        # entregadores capturados: cor do bar correspondente
        for nomeBar, listaEntregadores in entregadoresPorBar.items():
            cor = corPorBar[nomeBar] 
            for entregador in listaEntregadores:
                marcEntregadores.append(
                    dl.CircleMarker(
                        center=[entregador.latitude(), entregador.longitude()],
                        radius=6, color=cor, weight=2, fill=True, fillColor=cor, fillOpacity=0.6,
                        children=[dl.Tooltip(f"Entregador {entregador.chave()} — Bar: {nomeBar}")]
                    )
                )

        # monta GeoJSON dos entregadores NAO capturados
        featuresNaoCapturados = [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [entregador.longitude(), entregador.latitude()]},
                "properties": {"chave": entregador.chave()}
            }
            for entregador in entregadores if entregador.chave() not in chavesCapturadas
        ]
        geojsonNaoCapturados = {"type": "FeatureCollection", "features": featuresNaoCapturados}

        # monta o painel flutuante da Legenda em HTML
        legenda_painel = html.Div([
            html.H4("Legenda", style={'margin': '0 0 15px 0', 'color': '#1565C0', 'borderBottom': '2px solid #e5dcc8', 'paddingBottom': '5px'}),
            html.Div(legenda_itens),
            html.Hr(style={'borderColor': '#e5dcc8'}),
            html.Div([
                html.Div(style={'width': '10px', 'height': '10px', 'backgroundColor': 'gray', 'borderRadius': '50%', 'display': 'inline-block', 'marginRight': '10px'}),
                html.Span("Outros Entregadores", style={'fontSize': '12px', 'color': '#666'})
            ], style={'display': 'flex', 'alignItems': 'center'})
        ], style={
            'position': 'absolute', 'top': '20px', 'right': '20px', 'zIndex': '1000',
            'backgroundColor': 'rgba(255, 250, 240, 0.95)', 'padding': '15px',
            'borderRadius': '10px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.2)', 'border': '1px solid #e5dcc8'
        })

        # monta a tabela HTML dos entregadores selecionados
        cabecalho = html.Thead(html.Tr([
            html.Th("BAR"),
            html.Th("ENTREGADOR"),
            html.Th("DISTÂNCIA (m)", className="num"),
            html.Th("TEMPO (min)", className="num"),
        ]))

        linhas = []
        for nomeBar, chaveEntr, dist, tempo in tabela:
            corLinha = corPorBar.get(nomeBar, '#999999')
            linhas.append(html.Tr([
                html.Td([html.Span(className="bolinha-bar"), nomeBar], className="nome-bar"),
                html.Td(str(chaveEntr)),
                html.Td(f"{dist:.1f}", className="num"),
                html.Td(f"{tempo:.1f}", className="num"),
            ], style={'--cor-bar': corLinha}))

        tabela_html = html.Div([
            html.H4("Entregadores selecionados", className="tabela-titulo"),
            html.Div(
                html.Table([cabecalho, html.Tbody(linhas)], className="tabela-entregadores"),
                className="tabela-scroll"
            )
        ], className="tabela-painel")


        
        # envolve a legenda e o mapa em uma div com position: relative, permitindo que a legenda flutue no canto do mapa
        return html.Div([
            legenda_painel,
            dl.Map(
                center=[(LATREGMIN+LATREGMAX)/2, (LONGREGMIN+LONGREGMAX)/2],
                zoom=12,
                children=[
                    dl.TileLayer(url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"),
                    *marcBares,           # bares ao fundo (opacidade forte)
                    dl.GeoJSON(data=geojsonNaoCapturados, cluster=True, zoomToBoundsOnClick=True),  # entregadores nao capturados (cluster)
                    *marcEntregadores,   # entregadores capturados por cima (opacidade mediana)
                ],
                style={'width': '100%', 'height': '70vh'}
            ),
            tabela_html
        ], style={'position': 'relative'})

    except Exception as e:
        # se der qualquer erro, ele eh capturado aqui
        import traceback
        traceback.print_exc() # imprime o erro completo no terminal
        return html.Div([
            html.H3("Erro:", style={'color': 'red'}),
            html.Pre(str(e), style={'backgroundColor': '#f8d7da', 'padding': '15px'})
        ])