import csv
from src.auxiliares import Coordenada

class BarSemCoordenadaError(ValueError):
    def __init__(self, linha, mensagem):
        super().__init__(f"Linha {linha}: {mensagem}")
        self.linha = linha

class _Endereco:
    def __init__(self, tipoVia: str, nomeVia: str, comp: str, num: int, bairro: str, coord: Coordenada):
        self.tipoVia = tipoVia
        self.nomeVia = nomeVia
        self.comp = comp
        self.num = num
        self.bairro = bairro
        self.coord = coord

class Bar:
    def __init__(self, nome: str, ender: _Endereco):
        self._nome = nome
        self._ender = ender

    def coordenada(self):
        return self._ender.coord

    def geohash(self):
        return self._ender.coord.geohash()

    def latitude(self):
        return self._ender.coord.lat

    def longitude(self):
        return self._ender.coord.long

    def nome(self):
        return self._nome

    def chave_endereco(self):
        """
        Gera uma string padronizada que representa o endereço completo do bar.
        """
        partes = [self._ender.tipoVia, self._ender.nomeVia, str(self._ender.num), self._ender.bairro]
        return " ".join(p.strip().upper() for p in partes if p)

def le_bares(caminho):
    '''
    Processa todos o bares presentes de um arquivo .csv.
    '''
    bares = []
    erros = []

    with open(caminho, newline="", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)

        # enumerate comeca em 2 porque a primeira linha eh cabecalho
        for numeroLinha, linha in enumerate(leitor, start=2):
            latStr = (linha.get("LAT") or "").strip()
            longStr = (linha.get("LONG") or "").strip()

            # se falta coordenadas, registra e continua
            if not latStr or not longStr:
                erro = BarSemCoordenadaError(numeroLinha, "Bar sem latitude/longitude.")
                print(f"[AVISO] {erro}")
                erros.append(erro)
                continue

            # converte para float
            try:
                lat = float(latStr)
                long = float(longStr)

            except ValueError:
                erro = BarSemCoordenadaError(
                    numeroLinha,
                    f"Latitude/longitude inválida(s): ({latStr!r}, {longStr!r})."
                )
                print(f"[AVISO] {erro}")
                erros.append(erro)
                continue

            # cria um endereco
            # se a coluna nao possui valor, retorna "" (vazio)
            # se ha espacos extras, remove
            # converte para numero se todos os digitos sao numerais
            endereco = _Endereco(
                tipoVia=linha.get("DESC_LOGRADOURO", "").strip(),
                nomeVia=linha.get("NOME_LOGRADOURO", "").strip(),
                comp=linha.get("COMPLEMENTO", "").strip(),
                num=int(linha["NUMERO_IMOVEL"]) if (linha.get("NUMERO_IMOVEL") or "").strip().isdigit() else -1,
                bairro=linha.get("NOME_BAIRRO", "").strip(),
                coord=Coordenada(lat, long)
            )

            # cria um bar
            nomeFant = (linha.get("NOME_FANTASIA") or "").strip()
            nome = nomeFant if nomeFant else (linha.get("NOME") or "").strip()
            bar = Bar(nome=nome, ender=endereco)

            bares.append(bar)

    return bares, erros