# -*- coding: utf-8 -*-
"""
###############################################
AgileUFRJ - Implementando as teses do PPGI
###############################################

:Author: *Carlo E. T. Oliveira*
:Contact: carlo@nce.ufrj.br
:Date: $Date: 2010/08/25  $
:Status: This is a "work in progress"
:Revision: $Revision: 0.02 $
:Home: `Labase <http://labase.nce.ufrj.br/>`__
:Copyright: ©2011, `GPL <http://is.gd/3Udt>`__. 
"""
from couchdb import Server
from tornado.web import HTTPError
try:
  from couchdb.schema import Document, TextField, IntegerField, LongField, DateTimeField, DictField, ListField, Schema, FloatField
except ImportError:
  from couchdb.mapping import Document, TextField, IntegerField, LongField, DateTimeField, DictField, ListField, FloatField
  from couchdb.mapping import Mapping as Schema

from datetime import datetime
from time import mktime, strptime
from random import shuffle
import database
import logging

ANY, INI = 'A_N_Y', 'I_N_I'


class RESULT:
    QUIT,CHEAT,CALLOUT,ABORT,FAILURE,TIMEOUT,NORMAL,BELATED,RETRY,ALMOST,SUCCESS = range(-5,6)
    NAMES ='TIMEOUT,NORMAL,BELATED,RETRY,ALMOST,SUCCESS,QUIT,CHEAT,CALLOUT,ABORT,FAILURE'.split(',')


class Api(Document):
    
    # _id = identificador da sessão
    
    session = DictField(Schema.build(
        escola     = TextField(),
        tipoescola = TextField(),
        sexo1      = TextField(),
        idade1     = IntegerField(default=0),
        ano1       = IntegerField(default=0),
        sexo2      = TextField(default=""),
        idade2     = IntegerField(default=0),
        ano2       = IntegerField(default=0),
        starttime  = TextField(),
        endtime    = TextField()
    ))
    games = ListField(DictField(Schema.build(
        name = TextField(),
        maxlevel = IntegerField(default=1),
        time = TextField(),
        goal = ListField(DictField(Schema.build(
            level = IntegerField(default=-1),
            time = TextField(),
            markers = ListField(
                ListField(TextField())
            ),
            houses = DictField(),               # modificado para uso do tol. 
                                                # os pinos são representados como:
                                                # dict(h=[], b=[], m=[], l=[])
            #houses = ListField(
            #    ListField(TextField())
            #),
            criteria = ListField(TextField()),
            headings = ListField(TextField()),
            trial = ListField(ListField(DictField(Schema.build(
                        player = IntegerField(default=0),
                        marker = TextField(default=INI),
                        house = TextField(default=INI),
                        state = TextField(default=INI),
                        xpos = IntegerField(default=0),
                        ypos = IntegerField(default=0),
                        score = FloatField(default=1),
                        result = IntegerField(default=1),
                        #time = FloatField(default=1)
                        time = TextField()
            ))),default=[])
        )))
    )))
    
    @property
    def markers(self):
        if self.games and self.games[-1]["goal"] and self.games[-1]["goal"][-1]["markers"]:
            return self.games[-1]["goal"][-1]["markers"]
        else:
            return []
        
    @property
    def houses(self):
        if self.games and self.games[-1]["goal"] and self.games[-1]["goal"][-1]["houses"]:
            return self.games[-1]["goal"][-1]["houses"]
        else:
            return {}

    @property
    def maxlevel(self):
        if self.games and self.games[-1]["maxlevel"]:
            return self.games[-1]["maxlevel"]
        else:
            return 0
        
    @property
    def level(self):
        #print "self.games=", self.games
        #print "self.games[-1][goal]=", self.games[-1]["goal"]
        #print "self.games[-1][goal][-1][level]=", self.games[-1]["goal"][-1]["level"]
        
        if self.games and self.games[-1]["goal"] and self.games[-1]["goal"][-1]["level"]:
            return self.games[-1]["goal"][-1]["level"]
        else:
            return -1
        
    @property
    def trial(self):
        if self.games and self.games[-1]["goal"] and self.games[-1]["goal"][-1]["trial"]:
            return self.games[-1]["goal"][-1]["trial"]
        else:
            return []
        
    @property
    def state(self):
        #print "self.games=", self.games
        #print "self.games[-1][goal]=", self.games[-1]["goal"]
        #print "self.games[-1][goal][-1][level]=", self.games[-1]["goal"][-1]["trial"]
        if self.games and self.games[-1]["goal"] and self.games[-1]["goal"][-1]["trial"] and self.games[-1]["goal"][-1]["trial"][-1] and self.games[-1]["goal"][-1]["trial"][-1][-1]["state"]:
            return self.games[-1]["goal"][-1]["trial"][-1][-1]["state"]
        else:
            return ""
        
    def next(self, session={}, endtime=None, newgame=None, maxlevel=1, newlevel=None, newtrial=False, markers=None, houses={}, criteria=[], headings=[], table=[]):
        if session:  self.session = session
        if endtime:  self.session["endtime"] = endtime
        if newgame:  self.games.append(dict(name=newgame,maxlevel=maxlevel,time=str(datetime.now()),goal=list()))
        if newlevel: self.games[-1]["goal"].append(dict(level=newlevel, time=str(datetime.now()), markers=[], houses={}, criteria=[], headings=[], trial=[])) 
        if markers!=None:  self.games[-1]["goal"][-1]["markers"] = markers
        if houses:   self.games[-1]["goal"][-1]["houses"].update(houses)
        if criteria: self.games[-1]["goal"][-1]["criteria"] = criteria
        if headings: self.games[-1]["goal"][-1]["headings"] = headings
        if table: 
            new_table=[]
            for item in table:
                default_item = dict(player=0,marker=INI,house=INI,state='',xpos=0,ypos=0,score=1,result=1,time=str(datetime.now()))
                default_item.update(item)
                new_table.append(default_item)
            if newtrial or not self.games[-1]["goal"][-1]["trial"]:
                self.games[-1]["goal"][-1]["trial"].append(new_table)
            else:
                self.games[-1]["goal"][-1]["trial"][-1].extend(new_table)
        self.save()
        return True

    def retry(self, newtrial=False, table=[]):
        # salva movimentos da tentativa anterior
        if table: 
            new_table=[]
            for item in table:
                default_item = dict(player=0,marker=INI,house=INI,state='',xpos=0,ypos=0,score=1,result=1,time=str(datetime.now()))
                default_item.update(item)
                new_table.append(default_item)
            if newtrial or not self.games[-1]["goal"][-1]["trial"]:
                self.games[-1]["goal"][-1]["trial"].append(new_table)
            else:
                self.games[-1]["goal"][-1]["trial"][-1].extend(new_table)
                self.games[-1]["goal"][-1]["trial"].append(list())
            self.save()
    
    def _label_result(self,result): return RESULT.NAMES[result]

    def show_score(self, game, goal):
        '''
        Lista a tabela de pontuação
        '''
        if self.games and self.games[game] and self.games[game]["goal"] and self.games[game]["goal"][goal]:
            criteria = self.games[game]["goal"][goal]["criteria"]
            head = self.games[game]["goal"][goal]["headings"]
            # acrescenta coluna com o resultado de cada operação
            criteria.append('result')
            head.append('Resultado')
            
            op = dict((k,str) for k in criteria)
            op['result']= self._label_result
            
            return ("Resultado do Jogo %s" % self.games[game]["name"], head,
                [[op[key](move[key] if key in move else "")for key in criteria]
                    for phase in self.games[game]["goal"][goal]["trial"] for move in phase 
                 ])
        else:
            return ("Resultado inexistente", [], [])
        
    def save(self, db=database.DAPP):
        self.store(database.DAPP)
        
    def retrieve(self, id, db=database.DAPP):
        return Api.load(database.DAPP, id)
        
        
API_GAME = Api
