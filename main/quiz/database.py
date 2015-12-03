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
# Uso: database.QUESTION.view('quiz/by_question',startkey=[registry_id],endkey=[id, {}, {}])
quiz_by_question = ViewDefinition('quiz', 'by_question', \
                          '''                          
                             function(doc) {
                                 if (doc.type=="question") {
                                    emit([doc._id, 0], {enunciado: doc.enunciado});
                                 }
                                 if (doc.type=="quiz") {
                                    for (q in doc.questions)
                                       emit([doc.questions[q], 1], {questions: doc.questions[q]});                            
                                 }
                              }
                           ''')

                                
# Retorna lista de quiz que foram resolvidos, com todas as informações adicionais
# 
# Uso: database.QUESTION.view('quiz/by_registry_id',startkey=["mauricio"],endkey=["mauricio", {}])
#
# Uso: database.QUESTION.view('quiz/answered',startkey="mauricio", group="true")
#
quiz_answered = ViewDefinition('quiz', 'answered', \
                           '''                          
                             function(doc) {
                                 if (doc.type=="answer") {
                                    emit([doc.quiz_id, doc.finalizado], 1);
                                 
                              }
                            }  
                            ''',
                            u'''
                                function(keys, values) {
                                   return sum(values);
                              } 
                            ''')   


# Retorna lista de respostas de num quiz, com todas as informações adicionais
# 
# Uso: database.QUESTION.view('answer/by_quiz',startkey=[quiz_id, owner],endkey=[{}])
answer_by_quiz  = ViewDefinition('answer', 'by_quiz', \
                            '''
                              function(doc) {
                                     if (doc.type=="answer") {
                                            emit ([doc.quiz_id, doc.owner], { "answer_id": doc._id, "finalizado": doc.finalizado, "respostas": doc.respostas, "nota": doc.nota, "owner": doc.owner } );
                                        }
                                      }
                            ''')                 

# Retorna lista de questões usadas num quiz, com todas as informações adicionais
# 
# Uso: database.QUESTION.view('answer/by_quiz',startkey=[quiz_id, owner],endkey=[{}])
answer_by_question = ViewDefinition('answer', 'by_question', \
                            '''
                              function(doc) {
                                     if (doc.type=="answer" && doc.finalizado=="S") {
                                        for (q in doc.respostas) {
                                            emit ([doc.quiz_id, q, doc.respostas[q]], 1);
                                        }
                                     }
                               }
                            ''',
                            u'''
                                function(keys, values) {
                                   return sum(values);
                              } 
                            ''')     

ViewDefinition.sync_many(core.database.ACTIVDB, [ 
                                                  quiz_by_question, \
                                                  quiz_answered, \
                                                  answer_by_quiz, \
                                                  answer_by_question \
                                                ])

