import os
import osmnx as ox
import dash
from dash import html
import dash_leaflet as dl
from triecompacta import TRIECompacta
'''PODE APAGAR AUXILIARES'''
#from auxiliares import geohash_coordenada
from auxiliares import busca_entregadores
from bar import le_bares
from entregador import gera_entregadores, encontra_vias_proximas

LATREGMIN, LATREGMAX = -20.1, -19.7
LONGREGMIN, LONGREGMAX = -44.1, -43.8

# carrega o grafo das vias
caminhoGrafo = "dados/bh_drive.graphml"

if os.path.exists(caminhoGrafo):
    G = ox.load_graphml(caminhoGrafo)
    print("Grafo carregado do disco.")

else:
    G = ox.graph_from_place("Belo Horizonte, Brazil", network_type="drive")
    ox.save_graphml(G, caminhoGrafo)
    print("Grafo baixado e salvo em disco.")

# numero de entregadores a ser gerado
N = 1000

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

# arvore TRIE COMPACTA para entregadores
trieBar = TRIECompacta()

# insere cada entregador na arvore
for bar in bares:
    trieBar.insere(bar.nome(), bar)

# integracao

prefixo = "MASCATE"

bares = trieBar.busca_prefixo(prefixo)

raio = 2000

baresBuscados = trieBar.busca_prefixo(prefixo)

resultado = busca_entregadores(baresBuscados, trieEntr, raio)

'''
resultado = []
    
for bar in bares:
    # busca candidatos por Geohash
    print(f'Bar: {bar.nome()}')
    print(f'Coordenadas reais: ({bar.latitude()}, {bar.longitude()})')
    print(f'Geohash: {bar.geohash()}')
    print(f'Coordenadas aproximadas: ({geohash_coordenada(bar.geohash()).lat}, {geohash_coordenada(bar.geohash()).long})')
    # geohashes = geohashes_vizinhos(bar.ender.coord)
    ghBar = bar.geohash()
    ghCurto = ghBar[:niveis_para_raio(raio)]
    #print(f'Geohashes: {geohashes}')

    # entregadoresCandidatos = []
    # vistos = set()

    for entregador in trieEntr.busca_prefixo(ghCurto):
        print(f'Chave: {entregador.chave()}')
        print(f'Coordenadas: ({entregador.latitude()}, {entregador.longitude()})')
        print(f'Geohash: {entregador.geohash()}')

    # filtro de raio
    for entregador in trieEntr.busca_prefixo(ghCurto):
        print(f'Entregador candidato {entregador.chave()}:')
        distReta = entregador.distancia_reta(bar.coordenada())
        
        print(f'{distReta} <=? {raio}?')
        if distReta <= raio:
            print('sim!')
            resultado.append((bar, entregador, distReta))

print(resultado)
'''
'''
# cria aplicacao dash
app = dash.Dash(__name__)

CORES = ['red', 'green', 'yellow', 'blue', 'pink', 'orange', 'brown']

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

print(chavesCapturadas)

# marcadores
marcBares = []
marcEntregadores = []

# TODOS os bares buscados recebem cor e círculo
corPorBar = {} # nome do bar: cor

for i, bar in enumerate(bares):
    cor = CORES[i % len(CORES)]
    corPorBar[bar.nome()] = cor

    marcBares.append(
        dl.CircleMarker(
            center=[bar.latitude(), bar.longitude()],
            radius=12,
            color=cor,
            weight=3,
            fill=True,
            fillColor=cor,
            fillOpacity=1,
            children=[dl.Tooltip(f"Bar: {bar.nome()}")]
        )
    )

# entregadores capturados: cor do bar correspondente
for nomeBar, listaEntregadores in entregadoresPorBar.items():
    cor = corPorBar[nomeBar]

    for entregador in listaEntregadores:
        marcEntregadores.append(
            dl.CircleMarker(
                center=[entregador.latitude(), entregador.longitude()],
                radius=6,
                color=cor,
                weight=2,
                fill=True,
                fillColor=cor,
                fillOpacity=0.6,
                children=[dl.Tooltip(f"Entregador {entregador.chave()} — Bar: {nomeBar}")]
            )
        )

# entregadores NAO capturados: cinza
for entregador in entregadores:
    if entregador.chave() in chavesCapturadas:
        continue

    marcEntregadores.append(
        dl.CircleMarker(
            center=[entregador.latitude(), entregador.longitude()],
            radius=6,
            color='gray',
            weight=2,
            fill=True,
            fillColor='gray',
            fillOpacity=0.6,
            children=[dl.Tooltip(f"Entregador {entregador.chave()}")]
        )
    )

# LAYOUT
app.layout = html.Div([
    dl.Map(
        center=[(LATREGMIN+LATREGMAX)/2, (LONGREGMIN+LONGREGMAX)/2],
        zoom=12,
        children=[
            dl.TileLayer(url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"),
            *marcBares,          # bares ao fundo (opacidade forte)
            *marcEntregadores,   # entregadores por cima (opacidade mediana)
        ],
        style={'width': '100%', 'height': '100vh'}
    )
])

if __name__ == '__main__':
    app.run(debug=True)
'''

# cria aplicacao dash
app = dash.Dash(__name__)

CORES = ['red', 'green', 'yellow', 'blue', 'pink', 'orange', 'brown']

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

#print(chavesCapturadas)

# marcadores
marcBares = []
marcEntregadores = []

# TODOS os bares buscados recebem cor e círculo
corPorBar = {} # nome do bar: cor

for i, bar in enumerate(bares):
    cor = CORES[i % len(CORES)]
    corPorBar[bar.nome()] = cor

    marcBares.append(
        dl.CircleMarker(
            center=[bar.latitude(), bar.longitude()],
            radius=12,
            color=cor,
            weight=3,
            fill=True,
            fillColor=cor,
            fillOpacity=1,
            children=[dl.Tooltip(f"Bar: {bar.nome()}")]
        )
    )

# entregadores capturados: cor do bar correspondente
for nomeBar, listaEntregadores in entregadoresPorBar.items():
    cor = corPorBar[nomeBar]

    for entregador in listaEntregadores:
        marcEntregadores.append(
            dl.CircleMarker(
                center=[entregador.latitude(), entregador.longitude()],
                radius=6,
                color=cor,
                weight=2,
                fill=True,
                fillColor=cor,
                fillOpacity=0.6,
                children=[dl.Tooltip(f"Entregador {entregador.chave()} — Bar: {nomeBar}")]
            )
        )

# monta GeoJSON dos entregadores NAO capturados
featuresNaoCapturados = [
    {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [entregador.longitude(), entregador.latitude()]
        },
        "properties": {
            "chave": entregador.chave()
        }
    }
    for entregador in entregadores
    if entregador.chave() not in chavesCapturadas
]

geojsonNaoCapturados = {
    "type": "FeatureCollection",
    "features": featuresNaoCapturados
}

# LAYOUT
app.layout = html.Div([
    dl.Map(
        center=[(LATREGMIN+LATREGMAX)/2, (LONGREGMIN+LONGREGMAX)/2],
        zoom=12,
        children=[
            dl.TileLayer(url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"),
            *marcBares,          # bares ao fundo (opacidade forte)
            dl.GeoJSON(          # entregadores nao capturados (cluster)
                data=geojsonNaoCapturados,
                cluster=True,
                zoomToBoundsOnClick=True,
            ),
            *marcEntregadores,   # entregadores capturados por cima (opacidade mediana)
        ],
        style={'width': '100%', 'height': '100vh'}
    )
])

if __name__ == '__main__':
    app.run(debug=True)