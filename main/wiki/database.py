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

# marca de página removida
_CONTEUDO_REMOVIDO = "##@@$$%% REMOVED %%$$@@##"

_DOCBASES = ['wiki']

class Activ(Server):
    "Active database"
    wiki = {}

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
WIKI = __ACTIV.wiki


################################################
# CouchDB Permanent Views
################################################
#
# Retorna se existe um item (pasta ou página) com um nome dado
#
# Retorno:
# 
#
# Uso: WIKI.view('wiki/nomepag_exists',startkey=["nomepag"],endkey=["nomepag", {}])
#
wiki_nomepag_exists = ViewDefinition('wiki','nomepag_exists', \
                                '''function(doc) { 
                                     emit([doc.registry_id, doc.nomepag, doc._id], null); 
                                   }
                                ''')



# Retorna a ultima versão de todas as páginas da WIKI incluindo registry_id como parte da chave
# Não retorna páginas da lixeira nem folders.
# Permite obter todas as páginas de um determinado registry_id·
#
# Retorno:
# todos os campos da WIKI
#
# Uso: WIKI.view('wiki/portfolio',startkey=["mauricio"],endkey=["mauricio", {}])
#
wiki_portfolio = ViewDefinition('wiki','portfolio', \
                               '''function(doc) { 
                                       if (doc.is_folder!="S" && doc.historico[doc.historico.length-1].conteudo != "''' + _CONTEUDO_REMOVIDO + '''") {
                                         data_alt = doc.historico[doc.historico.length-1].data_alt;
                                         emit([doc.registry_id, data_alt, doc._id],  
                                              {nomepag: doc.nomepag,
                                              data_alt: data_alt, 
                                              alterado_por: doc.historico[doc.historico.length-1].alterado_por,
                                              owner: doc.owner, 
                                              conteudo: doc.historico[doc.historico.length-1].conteudo,
                                              nomepag_id: doc.nomepag_id});
                                       }
                                   }
                                ''')


# Conta número total de um determinado registry_id que não estejam na lixeira
#
# Retorno:
# número de páginas
#
# Uso: database.WIKI.view('wiki/count_portfolio',startkey="mauricio", group="true")
#
wiki_count_portfolio = ViewDefinition('wiki','count_portfolio', \
                               '''function(doc) { 
                                     if (doc.is_folder != "S" && doc.historico[doc.historico.length-1].conteudo != "''' + _CONTEUDO_REMOVIDO + '''")
                                          emit(doc.registry_id, 1);
                                   }
                                ''',
                               u'''
                                function(keys, values) {
                                   return sum(values);
                                }
                                ''')

# Retorna todas as páginas da WIKI incluindo registry_id como parte da chave.
# Retorna inclusive folders e páginas da lixeira.
# Permite obter todas as páginas de um determinado registry_id·
#
#
# Uso: 
# database.WIKI.view('wiki/partial_data',startkey=["mauricio"],endkey=["mauricio", {}])
#
wiki_partial_data = ViewDefinition('wiki','partial_data', \
                               '''function(doc) { 
                                     emit([doc.registry_id, doc._id],  
                                          {nomepag: doc.nomepag,
                                          is_folder: doc.is_folder, 
                                          parent_folder: doc.parent_folder,
                                          folder_items: doc.folder_items,
                                          data_alt: doc.is_folder == "S" ? doc.data_alt : doc.historico[doc.historico.length-1].data_alt, 
                                          alterado_por: doc.is_folder == "S" ? doc.alterado_por : doc.historico[doc.historico.length-1].alterado_por,
                                          removido: doc.is_folder != "S" && doc.historico[doc.historico.length-1].conteudo == "''' + _CONTEUDO_REMOVIDO + '''",
                                          owner: doc.owner, 
                                          nomepag_id: doc.nomepag_id}); 
                                  }
                               ''')

# Retorna todas as páginas da WIKI que estejam dentro de um folder.
# Não retorna páginas da lixeira.
#
# Uso: 
# database.WIKI.view('wiki/folder_data',startkey=[registry_id, folder, {}],endkey=[registry_id, folder], descending="true", skip=(page-1)*page_size , limit=page_size)
#
wiki_folder_data = ViewDefinition('wiki','folder_data', \
                               '''function(doc) { 
                                     if (doc.is_folder == "S" || doc.historico[doc.historico.length-1].conteudo != "''' + _CONTEUDO_REMOVIDO + '''") {
                                         dt_alt = (doc.is_folder == "S") ? doc.data_alt : doc.historico[doc.historico.length-1].data_alt;
                                         emit([doc.registry_id, doc.parent_folder, dt_alt, doc._id],
                                              {nomepag: doc.nomepag,
                                              is_folder: doc.is_folder, 
                                              parent_folder: doc.parent_folder,
                                              folder_items: doc.folder_items,
                                              data_alt: dt_alt,
                                              alterado_por: doc.is_folder == "S" ? doc.alterado_por : doc.historico[doc.historico.length-1].alterado_por,
                                              owner: doc.owner, 
                                              nomepag_id: doc.nomepag_id});
                                     }
                                  }
                               ''')

# Retorna todas as páginas WIKI de um usuário/comunidade que estejam na lixeira.
#
#
# Uso: 
# database.WIKI.view('wiki/removed_data',startkey=[registry_id, {}],endkey=[registry_id], descending="true", skip=(page-1)*page_size , limit=page_size)
#
wiki_removed_data = ViewDefinition('wiki','removed_data', \
                               '''function(doc) { 
                                     if (doc.is_folder != "S" && doc.historico[doc.historico.length-1].conteudo == "''' + _CONTEUDO_REMOVIDO + '''") {
                                         dt_alt = (doc.is_folder == "S") ? doc.data_alt : doc.historico[doc.historico.length-1].data_alt;
                                         emit([doc.registry_id, dt_alt, doc._id],  
                                              {nomepag: doc.nomepag,
                                              is_folder: doc.is_folder, 
                                              parent_folder: doc.parent_folder,
                                              folder_items: doc.folder_items,
                                              data_alt: dt_alt, 
                                              alterado_por: doc.is_folder == "S" ? doc.alterado_por : doc.historico[doc.historico.length-1].alterado_por,
                                              owner: doc.owner, 
                                              nomepag_id: doc.nomepag_id}); 
                                     }
                                  }
                               ''')

# Conta número total de páginas da lixeira de um determinado registry_id
#
# Retorno:
# número de páginas
#
# Uso: database.WIKI.view('wiki/count_removedpages',startkey="mauricio", group="true")
#
wiki_count_removedpages = ViewDefinition('wiki','count_removedpages', \
                               '''function(doc) { 
                                     if (doc.is_folder != "S" && doc.historico[doc.historico.length-1].conteudo == "''' + _CONTEUDO_REMOVIDO + '''")
                                          emit(doc.registry_id, 1);
                                   }
                                ''',
                               u'''
                                function(keys, values) {
                                   return sum(values);
                                }
                                ''')

# Conta número total de páginas/pastas da raiz de um determinado registry_id
# (exclui páginas na lixeira)
# Retorno:
# número de páginas
#
# Uso: database.WIKI.view('wiki/count_rootpages',startkey="mauricio", group="true")
#
wiki_count_rootpages = ViewDefinition('wiki','count_rootpages', \
                               '''function(doc) { 
                                      if ((doc.is_folder == "S" || doc.historico[doc.historico.length-1].conteudo != "''' + _CONTEUDO_REMOVIDO + '''") &&
                                           doc.parent_folder=="")
                                          emit(doc.registry_id, 1);
                                   }
                                ''',
                               u'''
                                function(keys, values) {
                                   return sum(values);
                                }
                                ''')

# Retorna todas as páginas da WIKI que estejam dentro de um folder.
# Retorna inclusive folders e páginas da lixeira.
# Permite obter todas as páginas de um determinado registry_id e folder·
#
#
# Uso: 
# database.WIKI.view('wiki/folder_itens',startkey=["mauricio"],endkey=["mauricio", {}])
#
wiki_folder_itens = ViewDefinition('wiki','folder_itens', \
                               '''function(doc) { 
                                     if (doc.is_folder=='S')
                                         emit([doc.registry_id, doc.nomepag_id],  
                                              {nomepag: doc.nomepag,
                                              folder_items: doc.folder_items
                                              }); 
                                  }
                               ''')


# Permite verfificar se um usuário é dono de uma página Wiki
#
# Retorno:
# None
#
# Uso: 
# database.WIKI.view('wiki/isowner',key=[user, doc_id])
#
wiki_isowner = ViewDefinition('wiki','isowner', \
                          '''
                          function(doc) { 
                             emit([doc.owner, doc._id], null); 
                          }
                           ''')


# Permite encontrar um comentário de uma página
#
# Retorno:
# Comentário
#
# Uso: 
# database.WIKI.view('wiki/comment',key=[doc_id, user, data_cri])

wiki_comment = ViewDefinition('wiki','comment', \
                          '''
                          function(doc) { 
                            for (c in doc.comentarios)
                               emit([doc._id, doc.comentarios[c]['owner'], doc.comentarios[c]['data_cri']], doc.comentarios[c]['comment']);
                          }
                           ''')

ViewDefinition.sync_many(WIKI, [wiki_nomepag_exists, wiki_portfolio, wiki_partial_data, \
                                wiki_count_portfolio, \
                                wiki_folder_data, wiki_removed_data, \
                                wiki_count_removedpages, wiki_count_rootpages, \
                                wiki_folder_itens, wiki_isowner, wiki_comment])

