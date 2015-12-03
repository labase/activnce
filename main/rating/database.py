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
from couchdb import Server
from couchdb.design import ViewDefinition
from config import COUCHDB_URL

_DOCBASES = ['rating']

class Activ(Server):
    "Active database"
    rating = {}

    def __init__(self, url):
        Server.__init__(self, url)
        act = self
        test_and_create = lambda doc: doc in act and act[doc] or act.create(doc)
        for attribute in _DOCBASES:
            setattr(Activ, attribute, test_and_create(attribute))

    def erase_database(self):
        'erase tables'
        for table in _DOCBASES:
            try:
                del self[table]
            except:
                pass


__ACTIV = Activ(COUCHDB_URL)
RATING = __ACTIV.rating


################################################
# CouchDB Permanent Views
################################################
#
# Retorna todas as avaliações de um objeto ou
# Retorna o valor da avaliação que um usuário fez de um objeto
#
# Retorno:
# valor da avaliação e data em que foi feita
#
# Uso: database.RATING.view('rating/partial_data',startkey=[tipo, escopo, objeto], endkey=[tipo, escopo, objeto, {}])
#
rating_partial_data = ViewDefinition('rating','partial_data', \
                               '''function(doc) { 
                                     emit([doc.tipo, doc.escopo, doc.objeto, doc.user, doc._id], {rating:doc.rating, data_cri:doc.data_cri}); 
                                   }
                               ''')

# Retorna a média das avaliações de um objeto
#
# Retorno:
# média das avaliações
#
# Uso: database.RATING.view('rating/mean_by_object',startkey=[tipo, escopo, objeto],endkey=[tipo, escopo, objeto, {}], group="true")

rating_mean_by_object = ViewDefinition('rating','mean_by_object', \
                              u'''
                                    // map
                                    function(doc){
                                        emit([doc.tipo, doc.escopo, doc.objeto], parseInt(doc.rating,10));
                                    }
                              ''',
                              u'''
                                    // reduce
                                    function(keys, values, rereduce) {
                                        if (!rereduce){
                                            var length = values.length
                                            return [sum(values) / length, length]
                                        }else{
                                            var length = sum(values.map(function(v){return v[1]}))
                                            var avg = sum(values.map(function(v){
                                                return v[0] * (v[1] / length)
                                                }))
                                            return [avg, length]
                                        }
                                    }
                              ''')


ViewDefinition.sync_many(RATING, [rating_partial_data, rating_mean_by_object])
