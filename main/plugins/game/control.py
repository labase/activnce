# -*- coding: utf-8 -*-
"""
################################################
I-Games - Games Inteligentes - Trilha Topológica
################################################

:Author: *Carlo E. T. Oliveira*
:Contact: carlo@nce.ufrj.br
:Date: $Date: 2012/06/02 $
:Status: This is a "work in progress"
:Revision: $Revision: 0.01 $
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


GAMEPAGE ="modules/plugins/game/game.html"

CRITERIA = ['state','marker','house','xpos','ypos', 'time']
HEADINGS = ['Tipo', 'Marcador', 'Casa', 'Coluna', 'Linha', 'Tempo']

class GameHandler(MethodDispatcher):
    """
    Trilha Topológica
    """

    @libs.methoddispatcher.authenticated
    def index(self, init="1"):
        self.title = "Trilha Topológica"
        sessionid = self.get_current_gamesession()
        if init=="1": 
            self._trainz = model.API_GAME().retrieve(sessionid)
            self._trainz.next(newgame="trilha", newlevel=1, criteria=CRITERIA, headings=HEADINGS)

        self.render(GAMEPAGE, TITLE=self.title, BEADS={}, HAND=[], CRITERIA=CRITERIA, \
                    SESSIONID=sessionid, RESULT=model.RESULT)
        
URL_TO_PAGETITLE.update ({
        "game": "Trilha Topológica",
    })

HANDLERS.extend([
            (r"/game/.*",      GameHandler),
    ])
