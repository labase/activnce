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

_DOCBASES = ['blog', 'comment']

class Activ(Server):
    "Active database"
    blog = {}
    comment = {}
    
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
BLOG = __ACTIV.blog
COMMENT = __ACTIV.comment


################################################
# CouchDB Permanent Views
################################################
#
# Retorna todos os POSTS no BLOG incluindo registry_id como parte da chave
# Permite obter todos os POSTS de um determinado registry_id·
#
# Retorno:
# todos os campos de BLOG
#
# Uso: model.BLOG.view('blog/all_data',startkey=["mauricio"],endkey=["mauricio", {}])
#
blog_all_data = ViewDefinition('blog','all_data', \
                               '''function(doc) {
                                        if (doc.historico[doc.historico.length-1].conteudo != "''' + _CONTEUDO_REMOVIDO + '''") {
                                            emit([doc.registry_id, doc.data_cri, doc._id], doc);
                                        }
                                    }
                                ''')


# Retorna todos os POSTS no BLOG incluindo registry_id como parte da chave
# Permite obter todos os POSTS de um determinado registry_id·
#
# Retorno:
# None
#
# Uso: 
# model.BLOG.view('blog/partial_data',startkey=["mauricio"],endkey=["mauricio", {}])
#
blog_partial_data = ViewDefinition('blog','partial_data', \
                               '''function(doc) { 
                                     emit([doc.registry_id, doc._id], null); 
                                  }
                               ''')


# Conta número total de posts do blog de um determinado registry_id
#
# Retorno:
# número de posts
#
# Uso: database.BLOG.view('blog/count_posts',startkey="mauricio", group="true")
#
blog_count_posts = ViewDefinition('blog','count_posts', \
                               '''function(doc) { 
                                       if (doc.historico[doc.historico.length-1].conteudo != "''' + _CONTEUDO_REMOVIDO + '''")
                                          emit(doc.registry_id, 1);
                                  }
                                ''',
                               u'''
                                function(keys, values) {
                                   return sum(values);
                                }
                                ''')

# Retorna todos os POSTS no BLOG por registry_id/ano/mes/post_id
#
# Retorno:
# titulo do BLOG
#
# Uso: model.BLOG.view('blog/archive',startkey=["mauricio"],endkey=["mauricio", {}])
#
blog_archive = ViewDefinition('blog','archive', \
                               u'''function(doc) {
                                       if (doc.historico[doc.historico.length-1].conteudo != "''' + _CONTEUDO_REMOVIDO + '''") {                               
                                         ano = doc.data_cri.substr(0,4);
                                         mes = doc.data_cri.substr(5,2);
                                         emit([doc.registry_id, ano, mes, doc.data_cri, doc._id], doc.titulo); 
                                       }
                                   }
                                ''')


# Retorna todos os comentários de um POST incluindo registry_id/post_id como parte da chave
# Permite obter todos os comentários de um determinado POST·
#
# Retorno:
# todos os campos de COMMENT
#
# Uso: model.COMMENT.view('blog/all_comments',startkey=["mauricio/post1"],endkey=["mauricio/post1", {}])
#
blog_all_comments = ViewDefinition('blog','all_comments', \
                                '''function(doc) { 
                                     emit([doc.registry_id+"/"+doc.post_id, doc._id], doc); 
                                   }
                                ''')

# Retorna todos os posts do BLOG de um usuário/comunidade que estejam na lixeira.
#
#
# Uso: 
# database.BLOG.view('blog/removed_data',startkey=[registry_id, {}],endkey=[registry_id], descending="true", skip=(page-1)*page_size , limit=page_size)
#
blog_removed_data = ViewDefinition('blog','removed_data', \
                               '''function(doc) { 
                                     if (doc.historico[doc.historico.length-1].conteudo == "''' + _CONTEUDO_REMOVIDO + '''") {
                                         dt_alt = doc.historico[doc.historico.length-1].data_alt;
                                         emit([doc.registry_id, dt_alt, doc._id],  
                                              {_id: doc._id,
                                              data_alt: dt_alt,
                                              data_cri: doc.data_cri,
                                              alterado_por: doc.historico[doc.historico.length-1].alterado_por,
                                              owner: doc.owner,
                                              titulo: doc.titulo,
                                              post_id: doc.post_id}); 
                                     }
                                  }
                               ''')

# Conta número total de posts da lixeira do blog de um determinado registry_id
#
# Retorno:
# número de páginas
#
# Uso: database.BLOG.view('blog/count_removedposts',startkey="mauricio", group="true")
#
blog_count_removedposts = ViewDefinition('blog','count_removedposts', \
                               '''function(doc) { 
                                     if (doc.historico[doc.historico.length-1].conteudo == "''' + _CONTEUDO_REMOVIDO + '''")
                                          emit(doc.registry_id, 1);
                                   }
                                ''',
                               u'''
                                function(keys, values) {
                                   return sum(values);
                                }
                                ''')

ViewDefinition.sync_many(BLOG, [blog_all_data, blog_partial_data, blog_count_posts, blog_archive, blog_removed_data, blog_count_removedposts])
ViewDefinition.sync_many(COMMENT, [blog_all_comments])