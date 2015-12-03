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

from couchdb.design import ViewDefinition
import core.database


################################################
# CouchDB Permanent Views
################################################

                               
# Retorna lista de topicos do forum ordenadas por data do último comentário
#
# Esta view é baseada na objects/registry_id, incluindo a data do último reply na chave,
# de forma a permitir a ordenação cronológica dos tópicos
# 
# Uso: database.ACTIVDB.view('forum/topic_list', startkey=["topic", registry_id],endkey=["topic", registry_id, {}])
#
forum_topic_list = ViewDefinition('forum', 'topic_list', \
                               '''function(doc) {
                                       if (doc.type=="topic") {
                                           data = doc.ultimo_reply ? doc.ultimo_reply : doc.data_cri
                                           emit( [doc.registry_id, data], doc );
                                       }
                                    }
                               ''')

# Retorna lista de topicos do forum com uma tag, ordenadas por data do último comentário
#
# Esta view é baseada na objects/by_registry_id_and_tag, incluindo a data do último reply na chave,
# de forma a permitir a ordenação cronológica dos tópicos
# 
# Uso: database.ACTIVDB.view('forum/topic_list', startkey=["topic", registry_id],endkey=["topic", registry_id, {}])
#
forum_topic_list_by_tag = ViewDefinition('forum', 'topic_list_by_tag', \
                               '''function(doc) {
                                       if (doc.type=="topic") {
                                           for (tag in doc.tags){
                                               data = doc.ultimo_reply ? doc.ultimo_reply : doc.data_cri
                                               emit( [doc.registry_id, doc.tags[tag], data], doc );
                                            }
                                       }
                                    }
                               ''')

ViewDefinition.sync_many(core.database.ACTIVDB, [ 
                                                  forum_topic_list, \
                                                  forum_topic_list_by_tag \
                                                ])

