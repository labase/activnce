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
import locale
from datetime import datetime
from random import shuffle
import logging

import core.model
import log.model
from core.dispatcher import BaseHandler, HANDLERS, URL_TO_PAGETITLE, \
                            NOMEUSERS, \
                            FILENAMECHARS, PAGENAMECHARS

from plugins.api import model as model

CANCELPAGE ="modules/plugins/cancel/cancel.html"

SHAPE_LINE = range(6)*6
SHAPE_MATRIX = [shuffle(SHAPE_LINE) or SHAPE_LINE[:] for row in range(15)]
SHAPE_CHECK = list()

CRITERIA = ['score','xpos','ypos','time','shape']
HEADINGS = ['Certo/Errado', 'Coluna', 'Linha', 'Tempo', 'Figura']

    
class CancelHandler(MethodDispatcher):
    """
    Joga o Teste de Cancelamento
    """

    def _show(self):
        sessionid = self.get_current_gamesession()
        self._cancel = model.API_GAME().retrieve(sessionid)
        return self._cancel.houses["matrix"]
    
    @libs.methoddispatcher.authenticated
    def index(self, init="2", level="1"):
        self.title = "Teste de Cancelamento"
        sessionid = self.get_current_gamesession()
        self._cancel = model.API_GAME().retrieve(sessionid)
        if init=="0":       # nova tentativa
           self._cancel.next(newtrial=True, markers=[], table=[])
        elif init=="1":     # novo nível
           shape_matrix = [shuffle(SHAPE_LINE) or SHAPE_LINE[:] for row in range(15)]
           self._cancel.next(newlevel=int(level), houses=dict(matrix=shape_matrix), markers=[], criteria=CRITERIA, headings=HEADINGS)
        elif init=="2":     # novo jogo
           shape_matrix = [shuffle(SHAPE_LINE) or SHAPE_LINE[:] for row in range(15)]
           self._cancel.next(newgame="cancel", maxlevel=1, newlevel=int(level), houses=dict(matrix=shape_matrix), markers=[], criteria=CRITERIA, headings=HEADINGS)
        self.render(CANCELPAGE, SHAPES = self._show(),
                    CHECK = self._cancel.markers, \
                    HAND = [0,3], CRITERIA=CRITERIA, \
                    SESSIONID=sessionid, RESULT=model.RESULT)
        
    @libs.methoddispatcher.authenticated
    def click(self,sessionid,y=0,x=0, shape='(0,0,0)',**kargs):
        shape = [int(it) for it in shape[1:-1].split(',')]
        clicked_shape = shape[0]
        shape[0] = (0,1)[shape[0] in [0,3]]
        shape.append(str(datetime.now()))
        shape.append(clicked_shape)

        self._cancel = model.API_GAME().retrieve(sessionid)
        markers = self._cancel.markers
        markers.append(shape)
        
        self._cancel.next(markers=markers)
        self.render(CANCELPAGE, SHAPES = self._show(),
                    CHECK = self._cancel.markers, \
                    HAND = [0,3], CRITERIA=CRITERIA,\
                    SESSIONID=sessionid, RESULT=model.RESULT)


URL_TO_PAGETITLE.update ({
        "can": "Teste de Cancelamento"
    })

HANDLERS.extend([
            (r"/can/.*",      CancelHandler)
    ])
