import math

LATMIN, LATMAX = -90, 90
LONGMIN, LONGMAX = -180, 180

BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"
BASE32MAPA = {c: i for i, c in enumerate(BASE32)}

NIVEIS = 8

ESTADOINICIAL = False

class Coordenada:
    def __init__(self, lat: float, long: float):
        # verifica se a coordenada esta dentro do intervalo aceito
        if not (LATMIN < lat < LATMAX):
            raise ValueError(f"Latitude deve estar no intervalo ({LATMIN}, {LATMAX}).")
                
        if not (LONGMIN < long < LONGMAX):
            raise ValueError(f"Longitude deve estar no intervalo ({LONGMIN}, {LONGMAX}).")
                
        self.lat = lat
        self.long = long

    def geohash(self):
        """
        Transforma coordenadas (latitude, longitude) em um código Geohash.
        """
        
        lat = ESTADOINICIAL
        
        intervaloLat = [LATMIN, LATMAX]
        intervaloLong = [LONGMIN, LONGMAX]
        
        codGeohash = ""
        
        for _ in range(0, NIVEIS):
            binario = 0
        
            # calcula um caractere do geohash
            for i in range(0, 5):
                binario <<= 1
                # 1: lattitude/longitude eh maior ou igual a media
                # 0: caso contrario
        
                if lat: # verifiar latitude
                    media = (intervaloLat[0] + intervaloLat[1]) / 2
        
                    if self.lat >= media:
                        binario += 1
                        intervaloLat[0] = media
        
                    else:
                        intervaloLat[1] = media
        
                    lat = False
        
                else: # verifcar longitude
                    media = (intervaloLong[0] + intervaloLong[1]) / 2
        
                    if self.long >= media:
                        binario += 1 
                        intervaloLong[0] = media
        
                    else:
                        intervaloLong[1] = media
                        
                    lat = True
                
            # converte binario para a base 32
            codGeohash += BASE32[binario]
        
        return codGeohash

def _niveis_para_raio(raioMetros):
    """
    Retorna o maior número de caracteres do código Geohash cuja
    célula cobre pelo menos 2*raioMetros em latitude e longitude.

    Quanto mais caracteres, menor a célula e menos candidatos a filtrar.
    """

    ultimoNivel = 1

    for niveis in range(1, NIVEIS + 1):
        totalBits = niveis * 5
        bitsLong = (totalBits + 1) // 2
        bitsLat = totalBits // 2

        dimLat = (LATMAX - LATMIN) / (2 ** bitsLat)
        dimLong = (LONGMAX - LONGMIN) / (2 ** bitsLong)

        latMedia = (LATMIN + LATMAX) / 2
        # um grau em latitude possui 111.320,00 km
        mPorGrauLat  = 111320.0
        # um grau em longitude possui 111.320,00 * cos(grauLatitude km)
        mPorGrauLong = 111320.0 * math.cos(math.radians(latMedia))

        dimLatM = dimLat * mPorGrauLat
        dimLongM = dimLong * mPorGrauLong

        # enquanto a celula ainda cobre o raio, avanca
        if dimLatM >= 2 * raioMetros and dimLongM >= 2 * raioMetros:
            ultimoNivel = niveis
        else:
            break

    return ultimoNivel

def _dimensao_celula(niveis):
    """
    Retorna as dimensões da célula (em graus) para o nível informado.
    """
    totalBits = niveis * 5
    bitsLong = (totalBits + 1) // 2
    bitsLat  = totalBits // 2

    dimLat  = (LATMAX - LATMIN) / (2 ** bitsLat)
    dimLong = (LONGMAX - LONGMIN) / (2 ** bitsLong)

    return dimLat, dimLong

def _geohashes_vizinhos(coordenada, niveis):
    """
    Retorna 9 códigos Geohashes relativos às células (centro + 8 vizinhos) no nível informado.
    """
    dimLat, dimLong = _dimensao_celula(niveis)

    resultados = []
    # deslocamento sul e norte
    for dirY in (-1, 0, 1):
        # deslocamento oeste e leste
        for dirX in (-1, 0, 1):
            latViz  = coordenada.lat  + dirY * dimLat
            longViz = coordenada.long + dirX * dimLong

            if not (LATMIN < latViz < LATMAX):
                continue
            if not (LONGMIN < longViz < LONGMAX):
                continue

            gh = (Coordenada(latViz, longViz)).geohash()[:niveis]
            resultados.append(gh)

    return resultados

def busca_entregadores(bares, trieEntregadores, raio, Gproj):
    """
    Para cada bar, busca entregadores dentro do raio usando o código Geohash + 8 vizinhos.
    Retorna lista de (bar, entregador, distanciaReal).
    """
    niveis = _niveis_para_raio(raio)

    resultado = []

    for bar in bares:
        geohashes = _geohashes_vizinhos(bar.coordenada(), niveis)

        vistos = set()
        for gh in geohashes:
            for entregador in trieEntregadores.busca_prefixo(gh):
                if entregador.chave() in vistos:
                    continue
                vistos.add(entregador.chave())

                if entregador.distancia_reta(bar.coordenada()) <= raio:
                    resultado.append((bar, entregador, entregador.distancia_real(bar.coordenada(), Gproj)))

    return resultado

def cria_tabela(resultado, velocidade):
    """
    Recebe uma lista de (bar, entregador, distanciaReal) e uma velocidade (m/s).
    Retorna uma lista de tuplas (nomeBar, chaveEntregador, distanciaReal, tempoSegundos),
    ordenada por nome do bar e pela distância.
    """
    linhas = [(bar.nome(), entregador.chave(), distancia, distancia / velocidade) for bar, entregador, distancia in resultado]

    # ordena por nome do bar, distancia e tempo
    linhas.sort(key=lambda x: (x[0], x[2]))

    return linhas

def busca_por_endereco(trieEnder, prefixoEndereco):
    """
    Busca bares cujo endereço começa com o prefixo informado.
    Retorna uma lista de bares (pode ser vazia).
    """
    texto = prefixoEndereco.strip().upper()
    return trieEnder.busca_prefixo(texto)


def busca_inteligente(trieBar, trieEnder, prefixoBar, prefixoEndereco):
    """
    Implementa duas opções de pesquisa:
        1) prefixoBar não vazio: busca por prefixoBar (e filtra por prefixoEndereco, se informado);
        2) prefixoBar vazio + prefixoEndereco: busca por prefixoEndereco.
    Retorna uma lista de bares (pode ser vazia).
    """
    prefixoBar = (prefixoBar or "").strip().upper()
    prefixoEndereco = (prefixoEndereco or "").strip().upper()

    # Caso 1: nome do bar informado
    if prefixoBar:
        baresNome = trieBar.busca_prefixo(prefixoBar)

        if not prefixoEndereco:
            return baresNome

        # filtra por endereço
        return [
            b for b in baresNome
            if b.chave_endereco().startswith(prefixoEndereco)
        ]

    # Caso 2: nome vazio: busca por endereço
    if not prefixoEndereco:
        return []

    return busca_por_endereco(trieEnder, prefixoEndereco)
