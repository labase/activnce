# -*- coding: utf-8 -*-
"""
###############################################
AgileUFRJ - Implementando as teses do PPGI
###############################################

:Author: *Carlo E. T. Oliveira*
:Contact: carlo@nce.ufrj.br
:Date: $Date: 2010/09/07 $
:Status: This is a "work in progress"
:Revision: $Revision: 0.02 $
:Home: `LABASE <http://labase.nce.ufrj.br/>`__
:Copyright: ©2011, `GPL <http://is.gd/3Udt>`__.
"""

import tornado.web
import tornado.template
from tornado.escape import json_decode
import libs.methoddispatcher
from libs.methoddispatcher import MethodDispatcher
from datetime import datetime

import core.model
from core.dispatcher import BaseHandler, HANDLERS, URL_TO_PAGETITLE, \
                            NOMEUSERS, \
                            FILENAMECHARS, PAGENAMECHARS
import wcst

from plugins.api import model as model
import urllib

WISCPAGE ="modules/plugins/wisconsin/wisconsin.html"

CRITERIA = ['carta_resposta','categoria','acertos','cor', 'forma', 'numero', 'outros', 'time']
HEADINGS = ['Carta resposta', 'Categoria', 'Acertos', 'Cor', 'Forma', u'Número', 'Outros', 'Data/Hora']


class WisconsinHandler(MethodDispatcher):
    """
    Joga o Teste de Wisconsin
    """

    @libs.methoddispatcher.authenticated
    def index(self, init="2", level="1"):
        self.title = "Wisconsin"
        houses = {"indiceCartaAtual": -1,
                  "categoria": 0,
                  "acertosConsecutivos": 0,
                  "outrosConsecutivos": 0,
                  "wteste": None
                  }
        
        sessionid = self.get_current_gamesession()
        self._wisc = model.API_GAME().retrieve(sessionid)
        if init=="0":       # nova tentativa
           self._wisc.next(newtrial=True, houses=houses, markers=[], table=[])
        elif init=="1":     # novo nível
           self._wisc.next(newlevel=int(level), houses=houses, markers=[], criteria=CRITERIA, headings=HEADINGS)
        elif init=="2":     # novo jogo
           self._wisc.next(newgame="wisconsin", maxlevel=1, newlevel=int(level), houses=houses, markers=[], criteria=CRITERIA, headings=HEADINGS)

        self.redirect("/wisconsin/play")
        
        
        
    @libs.methoddispatcher.authenticated
    def play(self, result="", **kargs):
        sessionid = self.get_current_gamesession()
        cartasEstimulo=[]
        cartaPuxada=None
        if result != "Fim do Jogo":
            self._wisc = model.API_GAME().retrieve(sessionid)
            self._wisc.houses["indiceCartaAtual"] = self._wisc.houses["indiceCartaAtual"] + 1
            indiceCartaAtual = self._wisc.houses["indiceCartaAtual"]
            self._wisc.next(houses=self._wisc.houses)
            
            cartasEstimulo = wcst.listaCartasEstimulo
            cartaPuxada = wcst.listaCartasResposta[indiceCartaAtual]
        
        self.render(WISCPAGE, CRITERIA=CRITERIA, \
                    CARTAPUXADA=cartaPuxada, CARTASESTIMULO=cartasEstimulo, \
                    MSG=result, \
                    SESSIONID=sessionid, RESULT=model.RESULT)
        
        
        
    @libs.methoddispatcher.authenticated
    def click(self, opcao, **kargs):
        opcao = int(opcao)
        sessionid = self.get_current_gamesession()
        
        self._wisc = model.API_GAME().retrieve(sessionid)
        indiceCartaAtual = self._wisc.houses["indiceCartaAtual"]
        categoria = self._wisc.houses["categoria"]
        acertosConsecutivos = self._wisc.houses["acertosConsecutivos"]
        outrosConsecutivos = self._wisc.houses["outrosConsecutivos"]

        indiceCarta = (indiceCartaAtual % wcst.numCartasResposta) + 1
        cartaResposta = wcst.listaCartasResposta[indiceCartaAtual]
        cartaEstimulo = wcst.listaCartasEstimulo[opcao]

        tudoDiferente = cartaResposta.testaTudoDiferente(cartaEstimulo)

        if cartaResposta.testaMesmaCategoria(cartaEstimulo,
                            wcst.listaCategorias[categoria]):
            acertosConsecutivos += 1
            resultadoTeste = "Certo"
        else:
            acertosConsecutivos = 0
            resultadoTeste = "Errado"

        if tudoDiferente:
            outrosConsecutivos += 1
        else:
            outrosConsecutivos = 0

        if outrosConsecutivos == 3:
            outrosConsecutivos = 0
            resultadoTeste = u"%s.<br/>Leia atentamente as instruções: %s" % (resultadoTeste, wcst.instrucoes_teste())

        # Grava a jogada no banco de dados
        table = [dict(
            carta_resposta=indiceCarta,
            categoria=wcst.listaCategorias[categoria],
            acertos=acertosConsecutivos,
            cor=cartaResposta.testaMesmaCategoria(cartaEstimulo,
                                                  wcst.listaCategorias[0]),
            forma=cartaResposta.testaMesmaCategoria(cartaEstimulo,
                                                    wcst.listaCategorias[1]),
            numero=cartaResposta.testaMesmaCategoria(cartaEstimulo,
                                                     wcst.listaCategorias[2]),
            outros=tudoDiferente,
            time=str(datetime.now()))]

        #Se os acertos consecutivos chegarem a 10, troca a categoria
        if acertosConsecutivos == 10:
            acertosConsecutivos = 0
            categoria += 1
            
        houses = {"indiceCartaAtual": indiceCartaAtual,
                  "categoria": categoria,
                  "acertosConsecutivos": acertosConsecutivos,
                  "outrosConsecutivos": outrosConsecutivos,
                  "wteste": None
                  }
        self._wisc.next(houses=houses, table=table)

        # Termina o teste se esgotar as categorias ou fim das cartas respostas.
        if ((categoria >= len(wcst.listaCategorias)) or
            (indiceCartaAtual >= len(wcst.listaCartasResposta)-1)):
            resultadoTeste = "Fim do Jogo"
        
        self.redirect('/wisconsin/play?'+urllib.urlencode({"result":resultadoTeste.encode("UTF-8")}))
    
    

URL_TO_PAGETITLE.update ({
        "wisconsin": "Wisconsin"
    })

HANDLERS.extend([
            (r"/wisconsin/.*",      WisconsinHandler)
    ])
