# -*- coding: utf-8 -*-
"""Programa baseado no Teste Wisconsin
Autor: Neno Henrique Albernaz
Criado em Junho de 2008"""

########################################################################

class Carta:
    # Definição dos itens de uma carta.
    _numeros = [(u"Um", u"Uma"),
                (u"Dois", u"Duas"),
                (u"Três", u"Três"),
                (u"Quatro", u"Quatro")]
    _formas = [(u"Triângulo", u"Triângulos", "triangulo"),
               (u"Estrela", u"Estrelas", "estrela"),
               (u"Cruz", u"Cruzes", "cruz"),
               (u"Círculo", u"Círculos", "circulo")]

    _cores = [((u"Vermelho", u"Vermelha"), (u"Vermelhos", u"Vermelhas"), "vermelho"),
              ((u"Verde", u"Verde"), (u"Verdes", u"Verdes"), "verde"),
              ((u"Amarelo", u"Amarela"), (u"Amarelos", u"Amarelas"), "amarelo"),
              ((u"Azul", u"Azul"), (u"Azuis", u"Azuis"), "azul")]

    _atributos = dict(numero='num', forma='img', cor='color')

    def __init__(self, numero, forma, cor):
        genero = 0 if forma not in [1, 2] else 1
        num = 0 if numero == 1 else 1

        self.numero = self._numeros[numero-1][genero]
        self.forma = self._formas[forma][num]
        self.cor = self._cores[cor][num][genero]

        self.num = numero
        self.img = u"/static/plugins/wisconsin/images/%s.png" % self._formas[forma][2]
        self.color = self._cores[cor][2]

    def pegaAtributosCarta(self):
        return u"%s %s %s" % (self.numero, self.forma, self.cor)

    def testaMesmaCategoria(self, outra_carta, categoria):
        """Testa se as cartas são iguais na categoria.
        Categoria pode ter atribuido três valores: numero, forma ou cor."""
        return (getattr(self, self._atributos[categoria]) ==
                getattr(outra_carta, self._atributos[categoria]))

    def testaTudoDiferente(self, outra_carta):
        """Testa se as cartas são diferentes em todas as categorias."""
        for categoria in self._atributos:
            if self.testaMesmaCategoria(outra_carta, categoria):
                return False
        return True

########################################################################

def criaListaEstimulo():
    """Cria a lista de cartas estimulo. O conteudo de cada item da lista é uma carta."""
    return [Carta(1, 0, 0),
            Carta(2, 1, 1),
            Carta(3, 2, 2),
            Carta(4, 3, 3)]

########################################################################

def criaListaResposta():
    """Cria a lista de cartas resposta. O conteudo de cada item da lista é uma carta."""

    lista = ['101', '420', '203', '130', '411', '122', '403', '330', '421', '232',
             '113', '300', '223', '112', '301', '433', '210', '332', '400', '132',
             '213', '321', '212', '303', '410', '202', '323', '430', '211', '120',
             '431', '110', '333', '422', '111', '402', '233', '312', '131', '423',
             '100', '313', '432', '201', '310', '222', '133', '302', '221', '412',
             '103', '311', '230', '401', '123', '331', '220', '102', '320', '231',
             '423', '322', '200', '122']

    for indice in range(len(lista)):
        lista[indice] = Carta(int(lista[indice][0]),
                              int(lista[indice][1]),
                              int(lista[indice][2]))

    return 2 * lista

########################################################################

def criaListaCategorias():
    """Cria a lista de categorias.

    Cria a lista com as três categorias: cor, forma e numero. Repete
    devido ao teste passar duas vezes nas categorias."""

    return ["cor", "forma", "numero", "cor", "forma", "numero"]

########################################################################

def instrucoes_teste():
    """Imprimi na tela as instruções do teste. """

    return u"""Este é um teste um pouco diferente, porque eu não posso lhe
    dizer muito a respeito do que fazer. Você vai ser solicitado a associar
    cada uma das cartas que vou te dar com uma dessas quatro cartas-chave
    mostradas na tela. Sempre selecione o link da carta-chave que você achar
    que combine com a carta que vou te dar. Eu não posso lhe dizer como
    associar as cartas, mas lhe direi, cada vez, se você está certo ou errado.
    Não há limite de tempo neste teste. Está Pronto? Vamos começar."""

########################################################################

# Inicializa as variaveis.
listaCartasResposta = criaListaResposta()
listaCartasEstimulo = criaListaEstimulo()
listaCategorias = criaListaCategorias()
numCartasResposta = 64
