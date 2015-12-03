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

_DOCBASES = ['evaluation']

class Activ(Server):
    "Active database"
    evaluation = {}
    
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
EVALUATION = __ACTIV.evaluation

################################################
# CouchDB Permanent Views
################################################
#
# Retorna todas as avaliações de uma comunidade incluindo registry_id como parte da chave
#
# Retorno:
# todos os campos de EVALUATION
#
# Uso: model.BLOG.view('evaluation/all_data',startkey=["comunidade1"],endkey=["comunidade1", {}])
#
evaluation_all_data = ViewDefinition('evaluation','all_data', \
                               '''function(doc) { 
                                     emit([doc._id.split("/")[0], doc._id], doc); 
                                   }
                                ''')


ViewDefinition.sync_many(EVALUATION, [evaluation_all_data])

