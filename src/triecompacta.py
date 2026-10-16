class _Noh:
    # construtor
    def __init__(self, rotulo = ""):
        # rotulo: sequencia de caracteres que satisfaz aquele noh
        self.rotulo = rotulo

        # dicionario onde cada CHAVE eh o PRIMEIRO CARACTERE do rotulo do filho
        self.filhos = {}

        # lista de valores do noh (nesse contexto, entregadores nessa localizacao)
        self.valores = []

    def eh_folha(self):
        return len(self.filhos) == 0

class TRIECompacta:
    def __init__(self):
        # raiz com rotulo vazio
        self.raiz = _Noh("")

    def _coleta(self, noh, resultado):
        # entregadores que terminam nesse noh
        resultado.extend(noh.valores)

        # entregadores que terminam nos nohs filhos
        for filho in noh.filhos.values():
            self._coleta(filho, resultado)

    def insere(self, palavra, valor):
        noh = self.raiz
        i = 0
        n = len(palavra)

        while i < n:
            primeiro = palavra[i]

            # nao existe filho comecando com esse caractere:
            # cria um noh novo com o restante da palavra como rotulo
            if primeiro not in noh.filhos:
                novo = _Noh(palavra[i:])
                novo.valores.append(valor)
                noh.filhos[primeiro] = novo
                return

            filho = noh.filhos[primeiro]
            rotulo = filho.rotulo
            j = 0

            # compara caractere a caractere
            # compara enquanto:
            #   rotulo nao foi totalment consumido
            #   palavra nao foi totalmente consumida
            #   caracteres do rotulo e da palavra sao iguais
            while (j < len(rotulo)) and (i + j < n) and (rotulo[j] == palavra[i + j]):
                j += 1

            # CASO 1: rotulo do filho eh totalmente consumido
            # ======> continua descendo na arvore
            if j == len(rotulo):
                noh = filho
                i += j
                continue

            # CASO 2: diferenca no meio do rotulo
            # ======> divide o noh
            prefixoComum = rotulo[:j]
            sufixoFilho = rotulo[j:]

            # cria o noh intermediario com o prefixo comum
            intermediario = _Noh(prefixoComum)

            # filho antigo perde o prefixo comum
            filho.rotulo = sufixoFilho

            # religa
            intermediario.filhos[sufixoFilho[0]] = filho
            noh.filhos[primeiro] = intermediario

            # decide o que fazer com o restante da palavra
            if i + j == n:
                # palavra termina EXATAMENTE no prefixo comum:
                # valor fica no noh intermediario
                intermediario.valores.append(valor)

            else:
                # palavra continua:
                # cria novo filho para o restante
                resto = palavra[i + j:]
                novo = _Noh(resto)
                novo.valores.append(valor)
                intermediario.filhos[resto[0]] = novo

            return

        # se saiu do loop, a palavra foi consumida por inteiro
        # palavra presente na trie e nao eh prefixo de nenhuma outra
        noh.valores.append(valor)

    def busca_prefixo(self, prefixo):
        noh = self.raiz
        i = 0
        n = len(prefixo)

        while i < n:
            primeiro = prefixo[i]

            if primeiro not in noh.filhos:
                return []

            filho = noh.filhos[primeiro]
            rotulo = filho.rotulo
            j = 0

            while (j < len(rotulo)) and (i + j < n) and (rotulo[j] == prefixo[i + j]):
                j += 1

            # CASO 1: diferenca
            # ======> prefixo nao existe
            if j < len(rotulo) and (i + j < n):
                return []

            # CASO 2: sem diferenca, mas prefixo termina no MEIO do rotulo
            # ======> todos os valores abaixo desse filho satisfazem o prefixo
            if i + j == n and j < len(rotulo):
                resultado = []
                self._coleta(filho, resultado)
                return resultado

            # CASO 3: rotulo todo consumido
            # ======> continua descendo
            noh = filho
            i += j

        # prefixo consumido exatamente em um noh existente
        resultado = []
        self._coleta(noh, resultado)
        return resultado
    