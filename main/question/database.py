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
# Uso: database.QUESTION.view('question/by_quiz',startkey=[],endkey=[, {},{}])
question_by_quiz = ViewDefinition('question', 'by_quiz', \
                            '''
                              function(doc) {
                                     if (doc.type=="quiz") {
                                            emit ([doc._id, 0], null);
                                            for (q in doc.questions)
                                               emit([doc._id, 1],{"_id": doc.questions[q]}  );                            
                                         }
                                      }
                            ''')

ViewDefinition.sync_many(core.database.ACTIVDB, [ question_by_quiz \
                                                ])

