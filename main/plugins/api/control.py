# -*- coding: utf-8 -*-
"""
################################################
I-Games - Games Inteligentes Neuropedagógicos
################################################

:Author: *Instituto Tércio Pacitti (NCE/UFRJ)*
:Contact: carlo@nce.ufrj.br
:Date: $Date: 2012/06/02 $
:Status: This is a "work in progress"
:Revision: $Revision: 0.01 $
:Home: `LABASE <http://labase.nce.ufrj.br/>`__
:Copyright: ©2011, `GPL <http://is.gd/3Udt>`__.
"""

import tornado.web
import tornado.template

import model
from model import API_GAME

from core.dispatcher import BaseHandler, HANDLERS, URL_TO_PAGETITLE, \
                            NOMEUSERS, \
                            FILENAMECHARS, PAGENAMECHARS

from libs.dateformat import full_week_date, short_datetime, _meses
import libs.methoddispatcher
from libs.methoddispatcher import MethodDispatcher

import re
import time
from datetime import datetime
from uuid import uuid4
from tornado.escape import json_decode

TITLE,HEAD,BODY = 0,1,2
API_URL = "/api/index"

# _GAMESLIST:
# legenda; caminho para o jogo; nome do arquivo png, coluna na tela que lista os jogos
#
_GAMESLIST = [ (u"Manobrando o Trem", "/trainz/index", "trainz", 1),
               (u"Torre de Londres", "/tol/index", "tol", 1),
               (u"Jogo do Cancelamento", "/can/index", "can", 1),
               (u"Trilha Topológica", "/game/index", "game", 2),
               (u"Teste do Wisconsin", "/wisconsin/index", "wisconsin", 2),
               (u"Resultado da Última Fase Jogada", "/api/showscore", "", 2),
               (u"Encerrar Sessão", "/api/endsession", "", 2) ]
               
NEWSESSIONPAGE = "modules/plugins/api/newsession-form.html"
GAMESLISTPAGE = "modules/plugins/api/games-list.html"
SCOREPAGE = "modules/plugins/api/score.html"

class APIHandler(MethodDispatcher):
    
    def _compute_score(self,score,criteria=None):
        scored = score.replace("'",'"')
        score = json_decode(scored)
        criteria = criteria or ['marker','house','state','score','time']
        return [dict((key,s[ind])
            for ind, key in enumerate(criteria) ) for s in score]

    def _save(self, status, score, criteria):
        criteria = criteria and json_decode(criteria.replace("'",'"'))
        sessionid = self.get_current_gamesession()
        self._apidoc = model.API_GAME().retrieve(sessionid)
        if score:
            table = self._compute_score(score, criteria)
            table.append(dict(result=int(status)))
            self._apidoc.retry(newtrial=True, table=table)
        else:
            table = [dict(result=int(status))]
            self._apidoc.retry(newtrial=False, table=table)

    def index (self):
        ''' Formulário de cadastro de uma sessão '''
        self._apidoc = model.API_GAME()
        self._apidoc.next()
        
        session_info = dict(escola="", 
                    tipoescola="",
                    idade1=None, 
                    sexo1="", 
                    ano1=None, 
                    idade2=None, 
                    sexo2="", 
                    ano2=None)
                
        self.render(NEWSESSIONPAGE, SESSIONID=self._apidoc.id, \
                    NOMEPAG="cadastro", GAMESESSION=session_info, MSG="")
    
    def newsession(self, sessionid, escola="", tipoescola="", idade1=None, sexo1="", ano1=None, idade2=None, sexo2="", ano2=None, **kargs):
        ''' 
        Cadastro de uma nova sessão de jogos 
        '''
        
        session_info = dict(escola=escola.decode('UTF-8'), 
                            tipoescola=tipoescola,
                            idade1=int(idade1) if idade1 else 0, 
                            sexo1=sexo1, 
                            ano1=int(ano1) if ano1 else 0, 
                            idade2=int(idade2) if idade2 else 0, 
                            sexo2=sexo2, 
                            ano2=int(ano2) if ano2 else 0,
                            starttime=str(datetime.now()),
                            endtime="")
        msg = ""
        if escola == "" and tipoescola != "nenhuma": msg += u"Escreva o nome da sua Escola.<br/>"
        if escola != "" and tipoescola == "nenhuma": msg += u"Escolha escola pública ou privada; ou apague o nome da escola.<br/>"
        if tipoescola == "": msg += u"Escolha escola pública, privada ou nenhuma.<br/>"
        if sexo1 == "":   msg += u"Aluno1: Escolha Masculino ou Feminino.<br/>"
        if not idade1:  msg += u"Aluno1: Escreva a sua idade.<br/>"
        if not ano1:    msg += u"Aluno1: Escolha o seu ano.<br/>"
        if sexo2 or idade2 or ano2:
            if sexo2 == "": msg += u"Aluno2: Escolha Masculino ou Feminino.<br/>"
            if not idade2:  msg += u"Aluno2: Escreva a sua idade.<br/>"
            if not ano2:    msg += u"Aluno2: Escolha o seu ano.<br/>"
         
        if msg:
            self.render(NEWSESSIONPAGE, NOMEPAG="cadastro", \
                        SESSIONID=sessionid, GAMESESSION=session_info, MSG=msg)
        else:
            # salva informações da sessão no banco
            self._apidoc = model.API_GAME().retrieve(sessionid)
            print sessionid
            print session_info
            print self._apidoc
            self._apidoc.next(session=session_info)

            # salva cookie com a sessão
            self.set_secure_cookie("gamesession", sessionid, None)
            
            self.render(GAMESLISTPAGE, NOMEPAG="jogos", \
                        GAMESLIST=_GAMESLIST, MSG="")

    @libs.methoddispatcher.authenticated
    def endsession(self):
        '''
        Finaliza uma sessão
        '''
        sessionid = self.get_current_gamesession()
        self._apidoc = model.API_GAME().retrieve(sessionid)
        self._apidoc.next(endtime=str(datetime.now()))
        self.clear_cookie("gamesession")
        self.redirect(API_URL)
        
    @libs.methoddispatcher.authenticated
    def retry(self, score=None, criteria=None, return_url=API_URL, **kargs):
        '''
        Tenta novamente a mesma fase de um jogo
        '''
        self._save(model.RESULT.RETRY, score, criteria)
        self.redirect(return_url)

    @libs.methoddispatcher.authenticated
    def next(self, status, score=None, criteria=None, return_url=API_URL, **kargs):
        '''
        Passa para a próxima fase do mesmo jogo
        '''
        # status = ALMOST  Terminei mas acho que está errado
        #          SUCCESS Terminei e acho que está certo
        #          QUIT    Não quero jogar
        #          ABORT   Desisto

        sessionid = self.get_current_gamesession()
        self._apidoc = model.API_GAME().retrieve(sessionid)
        newlevel = self._apidoc.level + 1
         
        self._save(status, score, criteria)
        if newlevel > self._apidoc.maxlevel:
            self.render(GAMESLISTPAGE, NOMEPAG="", \
                        GAMESLIST=_GAMESLIST, MSG="")
        else:
            return_url = "%s&level=%d" % (return_url, newlevel)
            self.redirect(return_url)

    @libs.methoddispatcher.authenticated
    def quit(self, status, score=None, criteria=None, **kargs):
        '''
        Termina de jogar um jogo e volta para o menu de jogos
        '''
        # status = ALMOST  Terminei mas acho que está errado
        #          SUCCESS Terminei e acho que está certo
        #          QUIT    Não quero jogar
        #          ABORT   Desisto
        
        self._save(status, score, criteria)
        self.render(GAMESLISTPAGE, NOMEPAG="", \
                    GAMESLIST=_GAMESLIST, MSG="")

    @libs.methoddispatcher.authenticated
    def savegame(self, score, criteria=None, **kargs):
        criteria = criteria and json_decode(criteria.replace("'",'"'))
        table = self._compute_score(score, criteria)
        
        sessionid = self.get_current_gamesession()
        self._apidoc = model.API_GAME().retrieve(sessionid)
        self._apidoc.next(newtrial=True, table=table)
        return ('{"result":true}')

    @libs.methoddispatcher.authenticated
    def showscore(self, sessionid=None, game=-1, goal=-1):
        '''
        Exibe tabela com os movimentos de uma fase de um jogo
        '''
        if not sessionid: sessionid = self.get_current_gamesession()
        self._apidoc = model.API_GAME().retrieve(sessionid)
        score_table = self._apidoc.show_score(int(game), int(goal))
        self.title = score_table[TITLE]
        self.render(SCOREPAGE, TITLE=self.title, GAME=game, GOAL=goal, BEADS={}, ROW=score_table[HEAD], BODY=score_table[BODY])

URL_TO_PAGETITLE.update ({
        "newsession": u"Cadastro de Sessão",
        "next":       u"Próxima Fase",
        "quit":       u"Fim de Jogo",
        "showscore":  u"Resultados do Jogo"
    })

HANDLERS.extend([
            (r"/api/.*",      APIHandler),
    ])

