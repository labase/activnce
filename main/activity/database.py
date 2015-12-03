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

                               
# Retorna lista de questões usadas num quiz, com todas as informações adicionais
# 
# Uso: database.ACTIVDB.view('activity/by_group',startkey=[registry_id],endkey=[id, {}, {}])
activity_by_group = ViewDefinition('activity', 'by_group', \
                          '''                          
                             function(doc) {
                                 if (doc.type=="activity") {
                                    emit([doc.registry_id, doc.group_id, doc.status], 1);
                                 
                                }
                            }  
                            ''',
                            u'''
                                function(keys, values) {
                                   return sum(values);
                            } 
                           ''')



# Retorna lista de questões usadas num quiz, com todas as informações adicionais
# 
# Uso: database.ACTIVDB.view('activity/finalized',startkey=[registry_id],endkey=[id, {}, {}])
activity_finalized_and_groups = ViewDefinition('activity', 'finalized_and_groups', \
                          '''                          
                             function(doc) {
                                 if (doc.type=="activity" && doc.status == "finalizado") {
                                    emit([doc.registry_id, doc.group_id, doc.data_cri, 1], doc);
                                 
                                }
                                if (doc.type=="group" ) {
                                    emit([doc.registry_id, doc._id, doc.data_cri, 0], doc);
                                 
                                }
                            }  
                            
                           ''')
# Retorna lista de questões usadas num quiz, sem a informação de grupos
# 
# Uso: database.ACTIVDB.view('activity/finalized',startkey=[registry_id],endkey=[id, {}, {}])


activity_list_by_registry = ViewDefinition('activity', 'list_by_registry', \
                          ''' 

                        function (doc) {           
                                
                                if (doc.type=="activity" ) {
                                                    emit([doc.registry_id, doc.group_id, doc.data_cri,1], doc);
                                        }
                                 
                                             
                                if (doc.type=="group") {
                                                    emit([doc.registry_id, doc._id, doc.data_cri, 0], doc);
                                                }
                                
                            }

                           ''')

# Retorna lista de questões usadas num quiz, com todas as informações adicionais
# 
# Uso: database.ACTIVDB.view('activity/finalized',startkey=[registry_id],endkey=[id, {}, {}])
activity_Nfinalized = ViewDefinition('activity', 'Nfinalized', \
                          '''                          
                             function(doc) {if (doc.type=="activity" && (!(doc.status == "finalizado"))) {
                                    emit([doc.registry_id, doc.group_id, doc.data_cri, 1], doc);
                                }
                                
                                if (doc.type=="group" ) {
                                    emit([doc.registry_id, doc._id, doc.data_cri, 0], doc);
                                }
                            }  
                            
                           ''')

activity_pendent = ViewDefinition('activity', 'pendent', \
                          '''                          
                             function(doc) {
                               if (doc.type=="activity" && (!(doc.status == "finalizado"))) {
                                    for (e in doc.encarregados){
                                        emit([doc.encarregados[e], doc.registry_id, doc.data_cri,  1], doc);
                                    }
                                }
                                
                                if (doc.type=="activity" && (!(doc.status == "finalizado"))) {
                                    for (e in doc.encarregados){
                                        emit([doc.encarregados[e], doc.registry_id, doc.data_cri, 0], doc.group_id);
                                    }
                                }
                            }
                            ''',)

ViewDefinition.sync_many(core.database.ACTIVDB, [ 
                                                  activity_by_group, \
                                                  activity_Nfinalized, \
                                                  activity_pendent, \
                                                  activity_finalized_and_groups, \
                                                  activity_list_by_registry \
                                                ])

