import math

LATMIN, LATMAX = -90, 90
LONGMIN, LONGMAX = -180, 180

BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"
BASE32MAPA = {c: i for i, c in enumerate(BASE32)}

NIVEIS = 8

ESTADOINICIAL = False

class Coordenada:
    def __init__(self, lat: float, long: float):
        self.lat = lat
        self.long = long

def coordenada_geohash(coordenada):
    """
    Transforma coordenadas (latitude, longitude) em um codigo Geohash.
    """

    # verifica se a coordenada esta dentro do intervalo aceito
    if not (LATMIN < coordenada.lat < LATMAX):
        raise ValueError(f"Latitude deve estar no intervalo ({LATMIN}, {LATMAX}).")

    if not (LONGMIN < coordenada.long < LONGMAX):
        raise ValueError(f"Longitude deve estar no intervalo ({LONGMIN}, {LONGMAX}).")

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

                if coordenada.lat >= media:
                    binario += 1
                    intervaloLat[0] = media

                else:
                    intervaloLat[1] = media

                lat = False

            else: # verifcar longitude
                media = (intervaloLong[0] + intervaloLong[1]) / 2

                if coordenada.long >= media:
                    binario += 1 
                    intervaloLong[0] = media

                else:
                    intervaloLong[1] = media
                
                lat = True
        
        # converte binario para a base 32
        codGeohash += BASE32[binario]

    return codGeohash

def niveis_para_raio(raioMestros):
    """
    Retorna o maior numero de caracteres do geohash cuja celula
    cobre pelo menos 2*raioMestros em latitude e longitude.

    Quanto mais caracteres, menor a celula e menos candidatos a filtrar.
    """

    ultimoNivel = 1

    for niveis in range(1, 9):
        totalBits = niveis * 5
        bitsLong = (totalBits + 1) // 2
        bitsLat = totalBits // 2

        dimLat = (LATMAX - LATMIN) / (2 ** bitsLat)
        dimLong = (LONGMAX - LONGMIN) / (2 ** bitsLong)

        latMedia = (LATMIN + LATMAX) / 2
        mPorGrauLat  = 111320.0
        mPorGrauLong = 111320.0 * math.cos(math.radians(latMedia))

        dimLatM = dimLat * mPorGrauLat
        dimLongM = dimLong * mPorGrauLong

        # enquanto a celula ainda cobre o raio, avanca
        if dimLatM >= 2 * raioMestros and dimLongM >= 2 * raioMestros:
            ultimoNivel = niveis
        else:
            break

    return ultimoNivel

'''PODE APAGAR'''
def geohash_coordenada(codGeohash):
    # verifica tamanho e alfabeto do geohash
    if len(codGeohash) != NIVEIS:
        raise ValueError(f"Geohash deve ter {NIVEIS} caracteres.")
    
    for c in codGeohash:
        if c not in BASE32MAPA:
            raise ValueError(f"Caractere inválido: {c!r}")

    intervaloLat  = [LATMIN, LATMAX]
    intervaloLong = [LONGMIN, LONGMAX]

    lat = ESTADOINICIAL

    for c in codGeohash:
        valor = BASE32MAPA[c]

        # analisa do mais significativo para o menos significativo
        # shift = 4..0
        for shift in range(4, -1, -1):
            # extrai o bit
            bit = (valor >> shift) & 1 

            if lat: # verificar latitude
                media = (intervaloLat[0] + intervaloLat[1]) / 2

                if bit == 1: # metade superior
                    intervaloLat[0] = media

                else: #metade inferior
                    intervaloLat[1] = media

                lat = False

            else: #verificar longitude
                media = (intervaloLong[0] + intervaloLong[1]) / 2

                if bit == 1:
                    intervaloLong[0] = media

                else:
                    intervaloLong[1] = media

                lat = True

    # ponto medio do intervalo final
    latitude  = (intervaloLat[0] + intervaloLat[1]) / 2
    longitude = (intervaloLong[0] + intervaloLong[1]) / 2

    return Coordenada(latitude, longitude)

def dimensao_celula():
    # NIVEIS caracteres * 5 bits = NIVEIS*5 bits alternados
    totalBits = NIVEIS * 5

    # caso NIVEIS for impar, bitsLong continuar ocupando as poicoes pares,
    # mas tera um bit a mais que bitsLat
    bitsLong = (totalBits + 1) // 2   # posicoes pares (0, 2, 4, ...)
    bitsLat  = totalBits // 2         # posicoes ímpares (1, 3, 5, ...)

    dimLat  = (LATMAX - LATMIN) / (2 ** bitsLat)
    dimLong = (LONGMAX - LONGMIN) / (2 ** bitsLong)

    return dimLat, dimLong

def geohashes_vizinhos(coord):
    dimLat, dimLong = dimensao_celula()

    resultados = []
    for dirY in (-1, 0, 1):       # direcao do deslocamento em latitude
        for dirX in (-1, 0, 1):   # direcao do deslocamento em longitude
            latViz = coord.lat + dirY * dimLat
            longViz = coord.long + dirX * dimLong

            # ignora vizinhos fora da regiao de interesse
            if not (LATMIN < latViz < LATMAX):
                continue
            if not (LONGMIN < longViz < LONGMAX):
                continue

            resultados.append(coordenada_geohash(Coordenada(latViz, longViz)))

    return resultados

# print(geohash_coordenada(coordenada_geohash(Coordenada(-19.917452,-43.9192819))))
