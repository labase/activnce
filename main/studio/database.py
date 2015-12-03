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

_DOCBASES = ['studio']

class Activ(Server):
    "Active database"
    studio = {}

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
STUDIO = __ACTIV.studio


################################################
# CouchDB Permanent Views
################################################
#
# Retorna todos os registros de STUDIO incluindo registry_id como parte da chave
# Permite obter todos os arquivos de um determinado registry_id·
#
# Retorno:
# todos os campos de STUDIO
#
# Uso: model.STUDIO.view('studio/all_data',startkey=["mauricio"],endkey=["mauricio", {}])
#
studio_all_data = ViewDefinition('studio','all_data', \
                               '''function(doc) { 
                                     emit([doc.registry_id, doc._id], doc); 
                                   }
                                ''')


# Retorna todas os registros de STUDIO incluindo registry_id como parte da chave.
# Permite obter todas os arquivos de um determinado registry_id·
# Versão simplificada: retorna apenas os campos: data_upload e owner.
#
# Retorno:
# [registry_id, doc_id]: {
#     data_upload: doc.data_upload,
#     owner: doc.owner 
# }
#
# Uso: 
# model.STUDIO.view('studio/partial_data',startkey=["mauricio"],endkey=["mauricio", {}])
#
studio_partial_data = ViewDefinition('studio','partial_data', \
                               '''function(doc) { 
                                     emit([doc.registry_id, doc._id],  
                                     {data_upload: doc.data_upload, 
                                      owner: doc.owner, 
                                     }); 
                                  }
                               ''')



# Permite encontrar um comentário de uma imagem do studio
#
# Retorno:
# Comentário
#
# Uso: 
# model.STUDIO.view('studio/comment',key=[doc_id, user, data_cri])

studio_comment = ViewDefinition('studio','comment', \
                          '''
                          function(doc) { 
                            for (c in doc.comentarios)
                               emit([doc._id, doc.comentarios[c]['owner'], doc.comentarios[c]['data_cri']], doc.comentarios[c]['comment']);
                          }
                           ''')

ViewDefinition.sync_many(STUDIO, [studio_all_data, studio_partial_data, studio_comment])
