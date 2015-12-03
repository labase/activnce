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

_DOCBASES = ['glossary']

class Activ(Server):
    "Active database"
    glossary = {}

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
GLOSSARY = __ACTIV.glossary


################################################
# CouchDB Permanent Views
################################################
#
# Retorna todos os registros de GLOSSARY incluindo registry_id como parte da chave
# Permite obter todos os itens do glossário de um determinado registry_id
#
# Retorno:
# todos os campos de GLOSSARY
#
# Uso: database.GLOSSARY.view('glossary/by_registry_id',startkey=["mauricio"],endkey=["mauricio", {}])
#
glossary_by_registry_id = ViewDefinition('glossary','by_registry_id', \
                               '''function(doc) { 
                                       emit([doc.registry_id, doc.item_id], doc);
                                   }
                                ''')

# Retorna todos os registros de GLOSSARY incluindo registry_id e a tag como parte da chave
# Permite obter todos os itens de glossário de um determinado registry_id e com uma determinada tag
#
# Retorno:
# todos os campos de GLOSSARY
#
# Uso: database.GLOSSARY.view('glossary/by_registry_id_and_tag',startkey=["mauricio","tag"],endkey=["mauricio", "tag", {}])
#
glossary_by_registry_id_and_tag = ViewDefinition('glossary','by_registry_id_and_tag', \
                               '''function(doc) { 
                                        for (t in doc.tags)
                                           emit([doc.registry_id, doc.tags[t], doc.item_id], doc);
                                   }
                                ''')

# Retorna todos os registros de GLOSSARY incluindo registry_id e item_id como parte da chave
#
# Retorno:
# todos os campos de GLOSSARY
#
# Uso: database.GLOSSARY.view('glossary/by_registry_id_and_item_id, startkey=["mauricio","termo_x"],endkey=["mauricio", "termo_x", {}])
#
glossary_by_registry_id_and_item_id = ViewDefinition('glossary','by_registry_id_and_item_id', \
                               '''function(doc) { 
                                     emit([doc.registry_id, doc.item_id], doc); 
                                   }
                                ''')


#
# Conta número total termos no glossário de um determinado registry_id
#
# Retorno:
# número de termos no glossário
#
# Uso: database.GLOSSARY.view('glossary/count_by_registry_id',startkey=["mauricio"],endkey=["mauricio", {}, group_level=1, group="true")
#
glossary_count_by_registry_id = ViewDefinition('glossary','count_by_registry_id', \
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

# Conta número total de termos no glossario de um determinado registry_id·e de uma determinada tag
#
# Retorno:
# número de termos no glossário
#
# Uso: database.GLOSSARY.view('glossary/count_by_registry_id_and_tag',startkey=["mauricio","tag"],endkey=["mauricio", "tag", {}, group_level=1, group="true")
#
glossary_count_by_registry_id_and_tag = ViewDefinition('glossary','count_by_registry_id_and_tag', \
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

# Totaliza numero de utilizações de um termo (item_id) por registry_id.
# Retorna total.
#
# Uso: database.GLOSSARY.view('glossary/count_by_item_id',startkey=["termo_x"],endkey=["termo_x", {}], group="true")

glossary_count_by_item_id = ViewDefinition('glossary','count_by_item_id', \
                              '''function(doc) { 
                                     emit(doc.item_id, 1); 
                                   }
                              ''',
                              u'''
                              function(keys, values) {
                                 return sum(values);
                              }
                              ''')

# Retorna todos os documentos por item_id
#
# Retorno:
# todos os campos do documento
#
# Uso: database.GLOSSARY.view('glossary/by_item_id',startkey=["termo_x"],endkey=["termo_x", {}])
#
glossary_by_item_id = ViewDefinition('glossary','by_item_id', \
                               '''function(doc) { 
                                     emit([doc.item_id, doc.registry_id], doc); 
                                   }
                                ''')


ViewDefinition.sync_many(GLOSSARY, [glossary_by_registry_id, \
                                    glossary_by_registry_id_and_item_id, \
                                    glossary_by_registry_id_and_tag, \
                                    glossary_count_by_registry_id, \
                                    glossary_count_by_registry_id_and_tag, \
                                    glossary_count_by_item_id, \
                                    glossary_by_item_id])
