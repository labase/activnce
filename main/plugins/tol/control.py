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
from plugins.api.model import RESULT, API_GAME

TOLPAGE ="modules/plugins/tol/tol.html"

BEAD_COLOR = ['red','red','nav','gre','yel']

PUT_BEAD, TAKE_BEAD = 1,2
HOUSES_DEFAULT={'h':[], 'b':[1,2], 'm':[], 'l':[3,4]}
BEAD_COLOR = ['red','red','nav','gre','yel']
BEAD_SIEVE = [[[int(bead) for bead in pin] for pin in model.split('_')] for model in
    ',_12_43,4321__,_234_1,3_42_1,41__32,_43_21,2_13_4,_413_2,3_241_,_231_4'.split(',')]
BEAD_MOVES = [int(moves) for moves in '02345566799']        # inclui um 0 na frente pois as fases vão de 1 a 10
BEAD_MODEL = [dict([(550, dict((pin*60,[BEAD_COLOR[bead] for bead in beads[::-1]])
            for pin, beads in enumerate(model)))]) for model in BEAD_SIEVE]
MOVE_SIEVE = '''n2r2","y2g1y1",["n2y2r2g1r3","n2y2g2r3g1"],["y2g2n3g3y1","n2y1g1n3g3"]
             ,"y1g2y2n2r3n3","y1g2y3n3r2n1","y1g2y2n3y3r2y2"
             ,["n2r2y1r1n3r2y2n2g1","y2n2r3n1y1r2y2n2g1","y2g2n3r3g1y1r2y2n2"]
             ,["n2r2y1r3n1r2g2n2y3","y2n2r3n1y1r2g2y3n2"]'''
PINMAX =(1,4,3,2)

CRITERIA = ['house','marker','state','time']
HEADINGS = ['Pino','Conta','Estado','Tempo']


class TolHandler(MethodDispatcher):
    """
    Jogo Torre de Londres
    """

    def _show(self):
        return dict([(50, dict((pin*60,[BEAD_COLOR[bead] for bead in beads])
            for pin, beads in enumerate([self._tol.houses[pino] for pino in 'bml'])))
            , BEAD_MODEL[self._tol.level].items()[0]])
            #(550,{0:[],60:[],120:[]})])
    
    @libs.methoddispatcher.authenticated
    def index(self, init="2", level="1"):
        self.title = "Torre de Londres"
        sessionid = self.get_current_gamesession()
        self._tol = API_GAME().retrieve(sessionid)
        if init=="0":       # nova tentativa
           self._tol.next(newtrial=True, houses=HOUSES_DEFAULT, table=[])
        elif init=="1":     # novo nível
           self._tol.next(newlevel=int(level), houses=HOUSES_DEFAULT, criteria=CRITERIA, headings=HEADINGS)
        elif init=="2":     # novo jogo
           self._tol.next(newgame="tol", maxlevel=10, newlevel=int(level), houses=HOUSES_DEFAULT, criteria=CRITERIA, headings=HEADINGS)
        self.render(TOLPAGE, TITLE = self.title, BEADS = self._show(), HAND = [], LEVEL=self._tol.level,
                    CRITERIA=CRITERIA, SESSIONID=sessionid, RESULT=RESULT)

    def _take_bead_into_hand(self, nome_do_pino):
        '''
        Pega a bola de um pino
        '''
        if len(self._tol.houses[nome_do_pino])>0:
            self._bead = self._tol.houses[nome_do_pino].pop()
            self._tol.houses['h'].append(self._bead)
            self._next = PUT_BEAD
        else:
            self._bead = 0    # pino vazio foi clicado
            self._next = TAKE_BEAD
        return self._tol.houses['h']

    def _put_hand_bead_to_a_pin(self, nome_do_pino):
        '''
        Pega bola da mão e bota em um pino
        '''
        self._bead= self._tol.houses['h'].pop()
        self._tol.houses[nome_do_pino].append(self._bead)
        self._next = TAKE_BEAD
        return self._tol.houses['h']
        
    def _check_result(self, result = RESULT.NORMAL):
        cheat = any(len(pin)> pin_max for pin, pin_max in
                    zip([self._tol.houses[pin] for pin in 'hbml'],PINMAX))
        model = BEAD_SIEVE[self._tol.level]
        correct = not any(game_pin != model_pin for game_pin, model_pin in
            zip([self._tol.houses[pin] for pin in 'bml']
                ,[model[pin][::-1] for pin in [0,1,2]]))
        moves = 0
        if self._tol.trial: moves = len(self._tol.trial[-1]) // 2
        #logging.info("game:  %s  model:  %s" ,[self._tol.houses[pin] for pin in 'bml']
        #             , [model[pin][::-1] for pin in [0,1,2]])    
        return cheat and RESULT.CHEAT or \
            correct and moves == BEAD_MOVES[self._tol.level] and RESULT.SUCCESS \
            or correct and moves == BEAD_MOVES[self._tol.level]+1 and RESULT.ALMOST \
            or correct and moves > BEAD_MOVES[self._tol.level]+1 and RESULT.BELATED \
            or result
        
    def _move_bead(self, pin, result=RESULT.NORMAL):
        _MOVE_BEAD= { 
            PUT_BEAD:  self._put_hand_bead_to_a_pin,
            TAKE_BEAD: self._take_bead_into_hand
        }
        hand = _MOVE_BEAD[self._tol.state or TAKE_BEAD](pin)
        result = self._check_result(result)
        
        self._tol.next(houses=self._tol.houses, 
                       table=[dict(house=pin, marker=self._bead, result=result, state=self._next, time=str(datetime.now()))])
        return hand
    
    def _move(self,sessionid,pin):
        self._tol = API_GAME().retrieve(sessionid)
        self.title = "Torre de Londres"
        # self._tol.save()
        hand = [BEAD_COLOR[hand] for hand in self._move_bead(pin)]
        self.render(TOLPAGE, TITLE = self.title, BEADS = self._show(), HAND =  hand, LEVEL=self._tol.level,\
                    CRITERIA=CRITERIA, SESSIONID=sessionid, RESULT=RESULT)
    
    @libs.methoddispatcher.authenticated
    def big(self,sessionid,y=0,x=0, **kargs):
        self._move(sessionid,'b')
    
    @libs.methoddispatcher.authenticated
    def mid(self,sessionid,y=0,x=0, **kargs):
        self._move(sessionid,'m')
    
    @libs.methoddispatcher.authenticated
    def lit(self,sessionid,y=0,x=0, **kargs):
        self._move(sessionid,'l')

URL_TO_PAGETITLE.update ({
        "tol": "Torre de Londres"
    })

HANDLERS.extend([
            (r"/tol/.*",      TolHandler),
    ])
