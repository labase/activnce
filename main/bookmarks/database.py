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

_DOCBASES = ['bookmarks']

class Activ(Server):
    "Active database"
    bookmarks = {}

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
BOOKMARKS = __ACTIV.bookmarks


################################################
# CouchDB Permanent Views
################################################
#
# Retorna todos os registros de BOOKMARKS incluindo registry_id como parte da chave
# Permite obter todos os bookmarks de um determinado registry_id
#
# Retorno:
# todos os campos de BOOKMARKS
#
# Uso: database.BOOKMARKS.view('bookmarks/by_registry_id',startkey=["mauricio"],endkey=["mauricio", {}, {}])
#
bookmarks_by_registry_id = ViewDefinition('bookmarks','by_registry_id', \
                               '''function(doc) { 
                                       emit([doc.registry_id, doc.data_alt, doc._id], doc);
                                   }
                                ''')

# Retorna todos os registros de BOOKMARKS incluindo registry_id e a tag como parte da chave
# Permite obter todos os bookmarks de um determinado registry_id·e de uma determinada tag
#
# Retorno:
# todos os campos de BOOKMARKS
#
# Uso: database.BOOKMARKS.view('bookmarks/by_registry_id_and_tag',startkey=["mauricio","tag"],endkey=["mauricio", "tag", {}, {}])
#
bookmarks_by_registry_id_and_tag = ViewDefinition('bookmarks','by_registry_id_and_tag', \
                               '''function(doc) { 
                                        for (t in doc.tags)
                                           emit([doc.registry_id, doc.tags[t], doc.data_alt, doc._id], doc);
                                   }
                                ''')

#
# Conta número total de bookmarks de um determinado registry_id
#
# Retorno:
# número de bookmarks
#
# Uso: database.BOOKMARKS.view('bookmarks/count_by_registry_id',startkey=["mauricio"],endkey=["mauricio", {}, group_level=1, group="true")
#
bookmarks_count_by_registry_id = ViewDefinition('bookmarks','count_by_registry_id', \
                               '''function(doc) { 
                                       emit([doc.registry_id, doc._id], 1);
                                   }
                                ''',
                                '''function(keys, values, rereduce) {
                                  if (rereduce) {
                                    return sum(values);
                                  } else {
                                    return values.length;
                                  }
                                }
                                ''')

# Conta número total de bookmarks de um determinado registry_id·e de uma determinada tag
#
# Retorno:
# número de bookmarks
#
# Uso: database.BOOKMARKS.view('bookmarks/count_by_registry_id_and_tag',startkey=["mauricio","tag"],endkey=["mauricio", "tag", {}, group_level=1, group="true")
#
bookmarks_count_by_registry_id_and_tag = ViewDefinition('bookmarks','count_by_registry_id_and_tag', \
                               '''function(doc) { 
                                        for (t in doc.tags)
                                           emit([doc.registry_id, doc.tags[t], doc._id], 1);
                                   }
                                ''',
                                '''function(keys, values, rereduce) {
                                  if (rereduce) {
                                    return sum(values);
                                  } else {
                                    return values.length;
                                  }
                                }
                                ''')


# Retorna todos os registros de BOOKMARKS com a URL como chave
#
# Retorno:
# todos os campos de BOOKMARKS
#
# Uso: database.BOOKMARKS.view('bookmarks/by_url',startkey=["mauricio"],endkey=["mauricio", {}])
#
# Totaliza numero de utilizações de uma tag por registry_id.
# Retorna total.
#
# Uso: database.BOOKMARKS.view('bookmarks/by_url',startkey=["url"],endkey=["url", {}], group="true")

bookmarks_count_by_url = ViewDefinition('bookmarks','count_by_url', \
                              '''function(doc) { 
                                     emit(doc.url, 1); 
                                   }
                              ''',
                              u'''
                              function(keys, values) {
                                 return sum(values);
                              }
                              ''')



#
# Retorna todos os registros de BOOKMARKS incluindo owner como parte da chave
# Permite obter todos os bookmarks de um determinado owner·
#
# Retorno:
# todos os campos de BOOKMARKS
#
# Uso: database.BOOKMARKS.view('bookmarks/by_owner',startkey=["mauricio"],endkey=["mauricio", {}])
#
bookmarks_by_owner = ViewDefinition('bookmarks','by_owner', \
                               '''function(doc) { 
                                     emit([doc.registry_id, doc._id], doc); 
                                   }
                                ''')


# Retorna se o usuário já possui um documento com uma URL determinada
#
# Retorno:
# null
#
# Uso: database.BOOKMARKS.view('bookmarks/by_url',startkey=["mauricio","url"],endkey=["mauricio", "url", {}])
#
bookmarks_by_registry_id_and_url = ViewDefinition('bookmarks','by_registry_id_and_url', \
                               '''function(doc) { 
                                     emit([doc.registry_id,doc.url,doc._id], null); 
                                   }
                                ''')

# Retorna todos os documentos por url
#
# Retorno:
# todos os campos do documento
#
# Uso: database.BOOKMARKS.view('bookmarks/by_url',startkey=["http://www.nce.ufrj.br"],endkey=["http://www.nce.ufrj.br", {}])
#
bookmarks_by_url = ViewDefinition('bookmarks','by_url', \
                               '''function(doc) { 
                                     emit([doc.url,doc.data_alt,doc._id], doc); 
                                   }
                                ''')



ViewDefinition.sync_many(BOOKMARKS, [bookmarks_by_registry_id, \
                                     bookmarks_count_by_registry_id, \
                                     bookmarks_by_registry_id_and_tag, \
                                     bookmarks_count_by_registry_id_and_tag, \
                                     bookmarks_by_owner, \
                                     bookmarks_by_url, \
                                     bookmarks_by_registry_id_and_url, \
                                     bookmarks_count_by_url])
