from auxiliares import LATMIN, LATMAX, LONGMIN, LONGMAX
from auxiliares import Coordenada
import random
import networkx as nx
import osmnx as ox

class Entregador:
    def __init__(self, chave: str, coord: Coordenada):
        self._chave = chave
        self._coord = coord

    def chave(self):
        return self._chave

    def coordenada(self):
        return self._coord

    def latitude(self):
        return self._coord.lat

    def longitude(self):
        return self._coord.long

    def geohash(self):
        return self._coord.geohash()

    def distancia_reta(self, coordenada):
        return ox.distance.great_circle(
            self._coord.lat, self._coord.long,
            coordenada.lat,  coordenada.long
        )

    def distancia_real(self, coordenada, G):
        """
        Retorna a distancia (em metros) percorrendo as vias do grafo G.
        Se nao houver caminho, retorna a distancia em linha reta.
        """
        # econtra os nos mais proximos
        noOrigem = ox.distance.nearest_nodes(G, X=self._coord.long, Y=self._coord.lat)
        no_destino = ox.distance.nearest_nodes(G, X=coordenada.long, Y=coordenada.lat)

        # Mesmo no: distancia zero
        if noOrigem == no_destino:
            return 0.0

        # tenta o caminho pelas vias
        try:
            rota = ox.routing.shortest_path(G, noOrigem, no_destino, weight="length")

        # em caso de erro: distancia em linha reta
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return self.distancia_reta(coordenada)

        if rota is None:
            return self.distancia_reta(coordenada)

        # soma os comprimentos
        distancia = 0.0

        # rota = [A, B, C, D]
        # zip(...) = [(A, B), (B, C), (C, D)]
        for u, v in zip(rota[:-1], rota[1:]):
            distancia += G.edges[u, v, 0].get("length", 0.0)

        return distancia

# quanto menor sigma, mais perto dos bares estarao os entregadores
def gera_entregadores(bares, N, sigma=0.006, maxTentativas=50):
    '''
    Dada uma lista de bares, plota N entregadores ao redor de bares aleatorios
    seguindo uma distribuicao normal com desvio padrao sigma.
    '''
    # verifica se a lista eh vazia
    if not bares:
        raise ValueError("Lista de bares vazia.")

    entregadores = []

    for i in range(N):
        # seleciona bar aleatorio
        coordBar = (random.choice(bares)).coordenada()

        # tenta ate encontrar bar na regiao valida
        for _ in range(maxTentativas):
            dlat  = random.gauss(0, sigma)
            dlong = random.gauss(0, sigma)

            lat = coordBar.lat + dlat
            long = coordBar.long + dlong

            if LATMIN < lat < LATMAX and LONGMIN < long < LONGMAX:
                entregadores.append(Entregador(i, Coordenada(lat, long)))
                break
        else:
            # se nao conseguiu em maxTentativas,
            # coloca exatamente na coordenada do bar
            entregadores.append(Entregador(i, Coordenada(lat, long)))

    return entregadores

def encontra_vias_proximas(entregadores, G):
    '''
    Dada uma lista de entregadores e um grafo de vias,
    projeta cada entregador no ponto de via mais próximo dele.
    '''
    # verifica se a lista eh vazia
    if not entregadores:
        return []

    '''
    # OSMnx recebe longitude, latitude, nessa ordem
    longitudes = [c.long for c in entregadores]
    latitudes = [c.lat for c in entregadores]
    
    # encontra a aresta (u, v, ith) mais proxima para CADA ponto
    # ith: i-esima aresta de u a v
    arestas = ox.distance.nearest_edges(G, longitudes, latitudes)
    '''
    longitudes = [e.longitude() for e in entregadores]
    latitudes = [e.latitude() for e in entregadores]
    listaArestas = ox.distance.nearest_edges(G, longitudes, latitudes)

    arestas = list(zip(entregadores, listaArestas))  
    
    # para cada aresta, extrai o ponto dela mais proximo do ponto
    resultado = []
    
    for entregador, (u, v, ith) in arestas:
        # obtem a curvatura da rua 
        dadosAresta = G.edges[u, v, ith]
        geometria = dadosAresta.get('geometry')

        # se nao ha geometria detalhada, usa as coordenadas dos nos u e v
        if geometria is None:
            uLat = G.nodes[u]['y']
            uLong = G.nodes[u]['x']
            vLat = G.nodes[v]['y']
            vLong = G.nodes[v]['x']
            
            # calcula quais dos dois nos esta mais proximo do ponto
            '''
            nesse caso eu nao posso simular a reta que liga esses dois pontos e projetar nela,
            porque nao sei se no mapa isso dara numa via
            por isso projeto num dos pontos porque, como é interseção,
            tenho certeza que ali sera via
            '''
            pLat, pLong = entregador.latitude(), entregador.longitude()
            du = (uLat - pLat)**2 + (uLong - pLong)**2
            dv = (vLat - pLat)**2 + (vLong - pLong)**2
            
            if du <= dv:
                resultado.append(Entregador(entregador.chave(), Coordenada(uLat, uLong)))

            else:
                resultado.append(Entregador(entregador.chave(), Coordenada(vLat, vLong)))
        else:
            # encontra o ponto da geometria mais perto
            pLat, pLong = entregador.latitude(), entregador.longitude()
            coordsGeometria = list(geometria.coords)
            
            menorDistancia = float('inf')
            lon0, lat0 = coordsGeometria[0]
            pMaisProx = Coordenada(lat0, lon0)
            
            for qLong, qLat in coordsGeometria:
                d = (qLat - pLat)**2 + (qLong - pLong)**2
                if d < menorDistancia:
                    menorDistancia = d
                    pMaisProx = Coordenada(qLat, qLong)
            
            resultado.append(Entregador(entregador.chave(), pMaisProx))
    
    return resultado