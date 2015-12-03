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


TRAINZPAGE ="modules/plugins/trainz/trainz.html"

CRITERIA = ['marker','house','state','score','time']
HEADINGS = ['Marcador', 'Casa', 'Movimento', 'Pontos', 'Tempo']

class TrainzHandler(MethodDispatcher):
    """
    Manobrando o Trem no Desvio
    """

    @libs.methoddispatcher.authenticated
    def index(self, init="1"):
        self.title = "Manobrando o Trem"
        sessionid = self.get_current_gamesession()
        if init=="1": 
            self._trainz = model.API_GAME().retrieve(sessionid)
            self._trainz.next(newgame="trainz", newlevel=1, criteria=CRITERIA, headings=HEADINGS)

        self.render(TRAINZPAGE, TITLE=self.title, BEADS={}, HAND=[], CRITERIA=CRITERIA, \
                    SESSIONID=sessionid, RESULT=model.RESULT)
        
URL_TO_PAGETITLE.update ({
        "trainz": "Manobrando o Trem",
    })

HANDLERS.extend([
            (r"/trainz/.*",      TrainzHandler),
    ])
