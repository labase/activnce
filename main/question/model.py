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


class Question(core.model.ActivDB):
    #_id            = <couchdb_id>

    enunciado      = TextField(default=u"Entre aqui o enunciado da questão.")
    respostas      = ListField(TextField())
    resp_certa     = TextField()
    tags           = ListField(TextField())
    nivel          = TextField()
    quizes         = ListField(TextField())
    

    def retrieve(self, id, db=core.database.ACTIVDB):
        # chamada:
        #    _question = model.Question().retrieve(id)
        _tmp = super(Question, self).retrieve(id,db)
        if _tmp: _tmp.__class__ = Question
        return _tmp

    @classmethod
    def retrieve_by_name_id(self, registry_id, name_id):
        # chamada: 
        #   _question = model.Question.retrieve_by_name_id(registry_id, name_id)
        _tmp = super(Question, self).retrieve_by_name_id("question", "question", registry_id, name_id)
        if _tmp:
            _question = Question(**_tmp)       
            _question._data["_rev"] = _tmp["_rev"]
            _question._data["_id"] = _tmp["_id"]
            return _question
        else:
            return None  

    @classmethod    
    def listObjects(self, registry_id, page=None, page_size=None, tag=None):
        return super(Question, self).listObjects("question", "question", registry_id, page, page_size, tag)
    
    @classmethod    
    def listObjectsBySubtype(self, subtype, registry_id, page=None, page_size=None, tag=None):
        return super(Question, self).listObjectsBySubtype("question", "question", subtype, registry_id, page, page_size, tag)
    
    @classmethod    
    def countObjectsByRegistryId(self, registry_id):
        return super(Question, self).countObjectsByRegistryId("question", "question", registry_id)
     
    @classmethod 
    def countObjectsByRegistryIdTags(self, registry_id, tag):
        return super(Question, self).countObjectsByRegistryIdTags("question", "question", registry_id, tag)
     
    @classmethod
    def listAllTags(self, registry_id, tag=None):
        return super(Question, self).listAllTags("question", "question", registry_id, tag)
    
    @classmethod
    def questionIsUsed(self, id): 
        if core.database.ACTIVDB.view('quiz/by_question', key=[id, 1]): 
            return True
        else:
            return False

    def deleteQuestion(self):
        # verifica se essa questão não é usada por nenhum quiz antes de remover
        if not Question.questionIsUsed(self.id):
            self.delete()
            return True
        else:
            return False
  
