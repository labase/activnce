# -*- coding: utf-8 -*-
"""
################################################
Plataforma ActivUFRJ
################################################

:Author: *Núcleo de Computação Eletrônica (NCE/UFRJ)*
:Contact: carlo@nce.ufrj.br
:Date: $Date: 2009-2010  $
:Status: This is a "work in progress"
:Revision: $Revision: 0.01 $
:Home: `LABASE `__
:Copyright: ©2009, `GPL 
"""

try:
  from couchdb.schema import Document, TextField, IntegerField, LongField, DateTimeField, DictField, ListField, Schema, FloatField
except ImportError:
  from couchdb.mapping import Document, TextField, IntegerField, LongField, DateTimeField, DictField, ListField, FloatField
  from couchdb.mapping import Mapping as Schema

import database
from libs.dateformat import human_date
from core.model import isFriendOrMember, isAUser, isFriend, isMember

import operator
from operator import itemgetter
from datetime import datetime

class Scrapbook(Document):
    user_to = TextField()
    recados = ListField(DictField(Schema.build(
                            user_from = TextField(),
                            recado = TextField(),
                            data = TextField()
              )))
    
    def saveScrap(self, user_from, scrap):
        self.recados.insert(0,dict(user_from = user_from, recado = scrap, data=str(datetime.now())))
        self.save(id=self.user_to)

    def removeScrap(self, item):
        _recados=[]
        _recados.extend(self.recados)
        _recados.pop(item)
        self.recados = _recados
        self.save()

    def getScrapbookList(self, user, page=1, page_size=1, filter=False):
        # antiga BaseHandler.get_scrapbook_list (dispatcher.py)
        #
        # user: usuário logado, que quer visualizar os recados
        # filter: indica se deve filtrar apenas as mensagens enviadas por user
        #       se filter=False então lista todos os recados na lista self.recados
        #       senão lista somente os recados enviados por user
        # retorna lista de (sender_id,msg,data,data_fmt,reply_to)
        def replyTo (user, user_to, user_from):
            reply_to = ""
            if isAUser(user_to):
                if isFriend(user, user_from):
                    reply_to = user_from
            else:
                if isMember(user, user_to):
                    reply_to = user_to
            return reply_to
        
        scraps = []
        inicio = (page-1)*page_size
        fim = min(inicio+page_size, len(self.recados))

        for i in range(inicio,fim):
            if not filter or self.recados[i]["user_from"] == user:
                sender = self.recados[i]["user_from"]
                msg    = self.recados[i]["recado"]
                data   = self.recados[i]["data"]
                data_fmt = human_date(data)
                reply_to = replyTo(user, self.user_to, self.recados[i]["user_from"])
                scraps.append( (sender,msg,data,data_fmt,reply_to) )
        scraps.sort(key=itemgetter(2),reverse=True)
        return scraps

    def countScraps(self, user, filter=False):
        count = 0
        for item in self.recados:
            if not filter or item["user_from"] == user:
                count = count + 1
        return count
        
    def save(self, id=None, db=database.SCRAPBOOK):
        if not self.id and id: self.id = id
        self.store(db)
        
    def retrieve(self, id, db=database.SCRAPBOOK):
        return Scrapbook.load(db, id)
    