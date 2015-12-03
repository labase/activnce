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
from libs.dateformat import short_datetime

#import operator
#from operator import itemgetter


class Rating(Document):
    user           = TextField() # usuário que fez a avaliação
    tipo           = TextField() # tipo do objeto avaliado: wiki, file ou blog
    escopo         = TextField() # registry_id do objeto avaliado
    objeto         = TextField() # nome do objeto avaliado: nome da página, nome do arquivo ou nome do post
    rating         = TextField() # valor da avaliação: 1 a 5
    data_cri       = TextField() # data em que a avaliação foi feita

    @classmethod
    def listRatingsFromObject(self, tipo, escopo, objeto):
        # retorna lista de tuplas com todas as avaliações de um objeto
        result = []
        for row in database.RATING.view("rating/partial_data",startkey=[tipo,escopo,objeto],endkey=[tipo,escopo,objeto, {}]):
            user = row.key[3]
            result.append([user, row.value["rating"], short_datetime(row.value["data_cri"], include_year=True)])
        # result = sorted(paginas, key=itemgetter("data_nofmt"), reverse = True)
        return result
    
    @classmethod
    def getRatingsFromObject(self, tipo, escopo, objeto):
        # retorna uma tupla com a média e o número de avaliações de um objeto
#        n = 0
#        soma = 0
#        for row in database.RATING.view("rating/partial_data",startkey=[tipo,escopo,objeto],endkey=[tipo,escopo,objeto, {}]):
#            soma = soma + int(row.value["rating"])
#            n = n + 1
#        media = 0
#        if n>0: media = float(soma)/n
#        return ([media, n])
        
        for row in database.RATING.view("rating/mean_by_object",startkey=[tipo,escopo,objeto],endkey=[tipo,escopo,objeto, {}]):
            return(row.value)
        return ([0, 0])



        
    @classmethod
    def getUserRatingFromObject(self, user, tipo, escopo, objeto):
        # retorna uma tupla com a avaliação que um dado usuário fez de um objeto
        result = []
        for row in database.RATING.view("rating/partial_data",startkey=[tipo,escopo,objeto,user],endkey=[tipo,escopo,objeto,user, {}]):
            result = [user, row.value["rating"], short_datetime(row.value["data_cri"], include_year=True)]
        return result
        
    def save(self, id=None, db=database.RATING):
        if not self.id and id: self.id = id
        self.store(db)
        
    def retrieve(self, id, db=database.RATING):
        return Recommendation.load(db, id)
    
    def delete(self, db=database.RATING):
        #db.delete(self)
        del db[self.id]
        
        
        
