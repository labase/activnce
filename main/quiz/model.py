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


try:
  from couchdb.schema import Document, TextField, IntegerField, LongField, DateTimeField, DictField, ListField, Schema, FloatField
except ImportError:
  from couchdb.mapping import Document, TextField, IntegerField, LongField, DateTimeField, DictField, ListField, FloatField
  from couchdb.mapping import Mapping as Schema

import core.model
import database

"""
            n                       n
Quiz     <----------------------------> Question
----                                    --------
questions=[]
   | 1            n
   +----------------> Answer
                      ------
                      quiz_id     - qual o quiz
                      owner       - quem respondeu
                      respostas=[]
"""

class Quiz(core.model.ActivDB):
    #_id           = <couchdb_id>   

    descricao           = TextField()
    questions           = ListField(TextField())
    data_inicio         = TextField()
    data_fim            = TextField()
    exibicao            = TextField()

    def retrieve(self, id, db=core.database.ACTIVDB):
        # chamada:
        #    _quiz = model.Quiz().retrieve(id)
        _tmp = super(Quiz, self).retrieve(id,db)
        if _tmp: _tmp.__class__ = Quiz
        return _tmp

    @classmethod
    def retrieve_by_name_id(self, registry_id, name_id):
        # chamada: 
        #   _quiz = model.Quiz.retrieve_by_name_id(registry_id, name_id)
        _tmp = super(Quiz, self).retrieve_by_name_id("quiz", "quiz", registry_id, name_id)
        if _tmp:
            _quiz = Question(**_tmp)       
            _quiz._data["_rev"] = _tmp["_rev"]
            _quiz._data["_id"] = _tmp["_id"]
            return _quiz
        else:
            return None  

    @classmethod    
    def listObjects(self, registry_id,  page, page_size, tag=None):
        return super(Quiz, self).listObjects("quiz", "quiz", registry_id, page, page_size, tag)
    
    @classmethod    
    def countObjectsByRegistryId(self, registry_id):
        return super(Quiz, self).countObjectsByRegistryId("quiz", "quiz", registry_id)
        
    
    def listQuestionsInQuiz(self):
        #lista todas as questões do quiz
    
        rows = core.database.ACTIVDB.view('question/by_quiz', startkey=[self.id], endkey=[self.id,{}], include_docs = True)
        return [row.doc for row in rows if row.key[1]]
        
    @classmethod    
    def quizIsAnswered(self, id):
        if core.database.ACTIVDB.view('quiz/answered', startkey=[id], endkey=[id, {}]):
            return True
        else:
            return False
        

    @classmethod
    def getQuizAnswers(self, quiz_id, user=None):
        if user:
            # retorna a resposta de um usuário para um quiz
            for row in core.database.ACTIVDB.view('answer/by_quiz', key=[quiz_id, user]):
                if row:
                    return row.value
                else:
                    return None      
        else:
            # retorna as respostas de todos os usuários para um quiz
            rows = core.database.ACTIVDB.view('answer/by_quiz', startkey=[quiz_id], endkey=[quiz_id, {}])
            return [row.value for row in rows]    
                       
    def deleteQuiz(self):
        # só remove se esse quiz ainda não foi respondido
        if not Quiz.quizIsAnswered(self.id):
            self.delete()
            return True
        else:
            return False 
    
            
    @classmethod
    def respCertas(self, quiz_id):
        rows = core.database.ACTIVDB.view('question/by_quiz', startkey=[quiz_id], endkey=[quiz_id,{}], include_docs = True)
        return [ (row.doc['_id'], row.doc['resp_certa']) for row in rows if row.key[1]==1 ]

    @classmethod
    def respDadas(self, quiz_id):
        dict_temp={}
        
        #descobre quantas pessoas responderam o quiz 
        for row in core.database.ACTIVDB.view('answer/by_question', startkey=[quiz_id], endkey=[quiz_id,{}] ,group_level=1, group="true"):
            total = row.value 
        
        #retorna {(question_id, resp_certa): N} 
        rows = core.database.ACTIVDB.view('answer/by_question', startkey=[quiz_id], endkey=[quiz_id,{}], group="true")   
        for row in rows: 
            #{(question_id, resp_certa): "acertos/total", N%} + {"total" : total}
            if "total" not in dict_temp:
                dict_temp.update({"total": total})    
            if (row.key[1], row.key[2]) in dict_temp :
                dict_temp.update({(row.key[1], row.key[2]): (str(row.value+1)+"/"+str(total), str(row.value*100/total)+"%")})
            else:
                dict_temp.update({(row.key[1], row.key[2]): (str(row.value)+'/'+str(total), str(row.value*100/total)+"%")})
        return dict_temp
            
            
class Answer(core.model.ActivDB):
    #_id            = <couchdb_id>
    respostas      = DictField()
    #respostas      = ListField(ListField(TextField()))
    quiz_id        = TextField()
    nota           = TextField()
    finalizado     = TextField()
   
    @classmethod    
    def listObjects(self, registry_id,  page, page_size, tag=None):
        return super(Answer, self).listObjects("quiz", "answer", registry_id, page, page_size, tag)
    
    def retrieve(self, id, db=core.database.ACTIVDB):
        # chamada:
        #    _answer = model.Answer().retrieve(id)
        _tmp = super(Answer, self).retrieve(id,db)
        if _tmp: _tmp.__class__ = Answer
        return _tmp      
          
    def calculaNota(self):    
        # self.respostas = {<question_id>: <resp_do_usuario>, ...} 

        acertos=0
        respostas_certas = Quiz.respCertas(self.quiz_id)
        for i in range(len(respostas_certas)):
            (question_id, resp_certa) = respostas_certas[i]
            if question_id in self.respostas and self.respostas[question_id] == resp_certa:
                acertos = acertos +1
                
        #retorna a porcentagem de acertos
        return "%d (%d/%d)" % (acertos*100/len(respostas_certas), acertos, len(respostas_certas))
    
         