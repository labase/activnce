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

_DOCBASES = ['mblog']

class Activ(Server):
    "Active database"
    mblog = {}
    
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
MBLOG = __ACTIV.mblog


################################################
# CouchDB Permanent Views
################################################
#

# Permite verificar se um registry_id possui algum post no MBLOG
#
# Retorno:
# True se existe, False se não existe
#
# Uso: 
# database.MBLOG.view('mblog/exists',startkey=["mauricio"],endkey=["mauricio", {}])
#
mblog_exists = ViewDefinition('mblog','exists', \
                                      '''function(doc) {
                                            emit([doc.registry_id, doc._id], None); 
                                         }
                                      ''')

# Retorna todos os POSTS no MBLOG incluindo registry_id como parte da chave
# Permite obter todos os POSTS de um determinado registry_id·
# Antigo REGISTRYMBLOGOWNERS
#
# Retorno:
# todos os campos de MBLOG
#
# Uso: database.MBLOG.view('mblog/by_owners',startkey=["mauricio"],endkey=["mauricio", {}])
#
mblog_by_owners = ViewDefinition('mblog','by_owners', \
                                 '''function(doc) { 
                                       emit([doc.registry_id, doc.data_cri, doc._id], doc); 
                                       if (doc.registry_id != doc.owner)
                                          emit([doc.owner, doc.data_cri, doc._id], doc); 
                                     }
                                  ''')


# Conta número total de posts escritos por um registry_id
#
# Retorno:
# número de posts
#
# Uso: database.MBLOG.view('blog/count_owners',startkey="mauricio", group="true")
#
mblog_count_owners = ViewDefinition('mblog','count_owners', \
                               '''function(doc) { 
                                    emit(doc.registry_id, 1); 
                                    if (doc.registry_id != doc.owner)
                                       emit(doc.owner, 1); 
                                  }
                                ''',
                               u'''
                                function(keys, values) {
                                   return sum(values);
                                }
                                ''')

# Retorna todos os POSTS no MBLOG incluindo registry_id do interessado como parte da chave
# Permite obter todos os POSTS que interessam a um registry_id·
# Antigo REGISTRYMBLOG
#
# Retorno:
# todos os campos de MBLOG
#
# Uso: database.MBLOG.view('mblog/by_followers',startkey=["mauricio"],endkey=["mauricio", {}])
#
mblog_by_followers = ViewDefinition('mblog','by_followers', \
                                    '''function(doc) { 
                                          for (i in doc.interessados) 
                                             emit([doc.interessados[i], doc.data_cri, doc._id], doc); 
                                        }
                                     ''')


# Conta número total de posts na tiimeline de um registry_id (que interessam a um registry_id)
#
# Retorno:
# número de posts
#
# Uso: database.MBLOG.view('blog/count_followers',startkey="mauricio", group="true")
#
mblog_count_followers = ViewDefinition('mblog','count_followers', \
                               '''function(doc) { 
                                      for (i in doc.interessados) 
                                         emit(doc.interessados[i], 1); 
                                  }
                                ''',
                               u'''
                                function(keys, values) {
                                   return sum(values);
                                }
                                ''')

# Retorna todos os POSTS no MBLOG incluindo registry_id do interessado como parte da chave
# Permite obter todos os POSTS que interessam a um registry_id·
# Antigo REGISTRYMBLOG
#
# Retorno:
# todos os campos de MBLOG
#
# Uso: database.MBLOG.view('mblog/by_mentioned',startkey=["mauricio"],endkey=["mauricio", {}])
#
mblog_by_mentioned = ViewDefinition('mblog','by_mentioned', \
                                    '''function(doc) { 
                                          for (i in doc.mencionados) 
                                             emit([doc.mencionados[i], doc.data_cri, doc._id], doc); 
                                        }
                                     ''')


# Conta número total de menções no mblog a um determinado registry_id
#
# Retorno:
# número de posts
#
# Uso: database.MBLOG.view('blog/count_posts',startkey="mauricio", group="true")
#
mblog_count_mentions = ViewDefinition('mblog','count_mentions', \
                               '''function(doc) { 
                                      for (i in doc.mencionados) 
                                         emit(doc.mencionados[i], 1); 
                                  }
                                ''',
                               u'''
                                function(keys, values) {
                                   return sum(values);
                                }
                                ''')

ViewDefinition.sync_many(MBLOG, [mblog_exists, \
                                 mblog_by_owners, \
                                 mblog_count_owners, \
                                 mblog_by_followers, \
                                 mblog_count_followers, \
                                 mblog_by_mentioned, \
                                 mblog_count_mentions])

