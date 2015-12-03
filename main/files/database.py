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

_DOCBASES = ['files']

class Activ(Server):
    "Active database"
    files = {}

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
FILES = __ACTIV.files


################################################
# CouchDB Permanent Views
################################################
# Retorna se existe um item (pasta ou página) com um nome dado
#
# Retorno:
# 
#
# Uso: FILES.view('files/filename_exists',startkey=["filename"],endkey=["filename", {}])
#
files_filename_exists = ViewDefinition('files','filename_exists', \
                               '''function(doc) { 
                                     emit([doc.registry_id, doc.filename, doc._id], null); 
                                   }
                                ''')

#
# Retorna todos os registros de FILES incluindo registry_id como parte da chave
# Permite obter todos os arquivos de um determinado registry_id·
#
# Retorno:
# todos os campos de FILES
#
# Uso: model.FILES.view('files/all_data',startkey=["mauricio"],endkey=["mauricio", {}])
#
files_all_data = ViewDefinition('files','all_data', \
                               '''function(doc) { 
                                     emit([doc.registry_id, doc._id], doc); 
                                   }
                                ''')


# Retorna todas os registros de FILES incluindo registry_id como parte da chave.
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
# model.FILES.view('files/partial_data',startkey=["mauricio"],endkey=["mauricio", {}])
#
files_partial_data = ViewDefinition('files','partial_data', \
                               '''function(doc) { 
                                     emit([doc.registry_id, doc._id],  
                                     {data_upload: doc.data_upload, 
                                      owner: doc.owner, 
                                     }); 
                                  }
                               ''')


# Retorna todos os arquivos que estejam dentro de um folder.
# Permite obter todas as páginas de um determinado registry_id e folder·
#
#
# Uso: 
# database.FILES.view('files/folder_data',startkey=["mauricio", "folder", {}],endkey=["mauricio", "folder"], descending="true", skip=(page-1)*page_size , limit=page_size)
#
files_folder_data = ViewDefinition('files','folder_data', \
                               '''function(doc) { 
                                     emit([doc.registry_id, doc.parent_folder, doc.data_upload, doc._id],  doc);
                                  }
                               ''')


# Conta número total de arquivos/pastas da raiz de um determinado registry_id
# Retorno:
# número de arquivos
#
# Uso: database.FILES.view('files/count_rootfiles',startkey="mauricio", group="true")
#
files_count_rootfiles = ViewDefinition('files','count_rootfiles', \
                               '''function(doc) { 
                                      if (doc.parent_folder=="")
                                          emit(doc.registry_id, 1);
                                   }
                                ''',
                               u'''
                                function(keys, values) {
                                   return sum(values);
                                }
                                ''')


# Permite encontrar um comentário de uma página
#
# Retorno:
# Comentário
#
# Uso: 
# database.FILES.view('files/comment',key=[doc_id, user, data_cri])

files_comment = ViewDefinition('files','comment', \
                          '''
                          function(doc) { 
                            for (c in doc.comentarios)
                               emit([doc._id, doc.comentarios[c]['owner'], doc.comentarios[c]['data_cri']], doc.comentarios[c]['comment']);
                          }
                           ''')

ViewDefinition.sync_many(FILES, [files_filename_exists, files_all_data, files_partial_data, \
                                 files_folder_data, files_count_rootfiles, files_comment])
