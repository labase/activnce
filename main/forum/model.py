# -*- coding: utf-8 -*-
"""
################################################
Oi Tonomundo - NCE/UFRJ
################################################

:Author: Eduardo Paz
:Contact: edupaz@nce.ufrj.br
:Date: $Date: 2010/08/02  $
:Status: This is a "work in progress"
:Revision: $Revision: 0.01 $
:Home: ``
:Copyright:  
"""


from operator import itemgetter
from datetime import datetime

try:
  from couchdb.schema import Document, TextField, IntegerField, LongField, DateTimeField, DictField, ListField, Schema, FloatField
except ImportError:
  from couchdb.mapping import Document, TextField, IntegerField, LongField, DateTimeField, DictField, ListField, FloatField
  from couchdb.mapping import Mapping as Schema

import core.model
import database
from search.model import addTag, removeTag
from libs.dateformat import short_datetime
from libs.strformat import remove_diacritics


class Topic(core.model.ActivDB):
    #_id           = <couchdb_id>   
    # service       = "forum"
    # type          = "topic"
    # subtype       = None

    conteudo          = TextField()
    receber_email     = TextField(default="N") # "S" ou "N" se o dono do tópico recebe ou não emails em cada post
    ultimo_reply      = TextField()

    def retrieve(self, id, db=core.database.ACTIVDB):
        # chamada:
        #    _topic = model.Topic().retrieve(id)
        _tmp = super(Topic, self).retrieve(id,db)
        if _tmp: _tmp.__class__ = Topic
        return _tmp

    @classmethod
    def get_forum_list(self, registry_id):
        forums = []
        for obj in self.listForumTopics(registry_id):
            num_comment = self.countObjectsByGroup(obj["_id"])

            forums.append((obj["owner"], \
                           obj["titulo"], \
                           u"%d comentários." % num_comment, \
                           short_datetime(obj["ultimo_reply"]) if obj["ultimo_reply"] else ""))
        return forums
            
        
    
    @classmethod
    def retrieve_by_name_id(self, registry_id, name_id):
        # chamada: 
        #   _topic = model.Topic.retrieve_by_name_id(registry_id, name_id)
        _tmp = super(Topic, self).retrieve_by_name_id("forum", "topic", registry_id, name_id)
        
        if _tmp:
            _topic = Topic(**_tmp)       
            _topic._data["_rev"] = _tmp["_rev"]
            _topic._data["_id"] = _tmp["_id"]
            return _topic
        else:
            return None  

    
    @classmethod    
    def countObjectsByRegistryId(self, registry_id):
        return super(Topic, self).countObjectsByRegistryId("forum", "topic", registry_id)
     
    @classmethod 
    def countObjectsByRegistryIdTags(self, registry_id, tag):
        return super(Topic, self).countObjectsByRegistryIdTags("forum", "topic", registry_id, tag)
   
    @classmethod
    def listAllTags(self, registry_id, tag=None):
        return super(Topic, self).listAllTags("forum", "topic", registry_id)
        
    
    @classmethod    
    def listObjectByGroup(self, registry_id, group_id):
        return super(Topic, self).listObjectByGroup("forum", registry_id, group_id)

    @classmethod    
    def listObjectsByGroup(self, registry_id, page=None, page_size=None, tag=None):
        return super(Topic, self).listObjectsByGroup("forum", registry_id, page, page_size, tag)
        
    @classmethod
    def exists(self, registry_id, name_id):        
        return super(Topic, self).exists("forum", "topic", registry_id, name_id)


    @classmethod    
    def listForumTopics(self, registry_id, page=1, page_size=1, order="0", tag=None):
        """ Retorna uma lista de objetos de um tipo/registry_id provenientes do activDB.
            Filtros:
            Se page e pagesize forem omitidos é porque a chamada deve retornar apenas o último criado/comentado.
            Se tag for omitida, retorna os objetos independente das suas tags.
        """
        lista = []
        if tag:
            if order=="0":
                for row in core.database.ACTIVDB.view('forum/topic_list_by_tag', startkey=[registry_id, tag, {}], endkey=[registry_id, tag], 
                                              descending="true", skip=(page-1)*page_size , limit=page_size):
                    obj_data = dict()
                    obj_data.update(row.value)
                                
                    lista.append(obj_data)
            else:
                for row in core.database.ACTIVDB.view('forum/topic_list_by_tag', startkey=[registry_id, tag], endkey=[registry_id, tag, {}], 
                                              descending="false", skip=(page-1)*page_size , limit=page_size):
                    obj_data = dict()
                    obj_data.update(row.value)
                                
                    lista.append(obj_data)

        else:
            if order=="0":
                for row in core.database.ACTIVDB.view('forum/topic_list', startkey=[registry_id, {}], endkey=[registry_id], 
                                              descending="true", skip=(page-1)*page_size , limit=page_size):
                    obj_data = dict()
                    obj_data.update(row.value)
                                
                    lista.append(obj_data)
            else:
                for row in core.database.ACTIVDB.view('forum/topic_list', startkey=[registry_id], endkey=[registry_id, {}], 
                                              descending="false", skip=(page-1)*page_size , limit=page_size):
                    obj_data = dict()
                    obj_data.update(row.value)
                                
                    lista.append(obj_data)
                 
        return lista


    def saveTopic(self, id=None, old_tags=None):
        if id==None:
            self.save()
        else:
            self.save(id=id)
        
        # compara as tags anteriores com as modificadas, atualizando a lista de tags no BD
        data_tag = str(datetime.now())
        for tag in self.tags:
            if old_tags==None or tag not in old_tags:
                addTag(tag, self.registry_id, self.owner, "forum", self.registry_id+"/"+self.name_id, self.titulo, data_tag)

        if old_tags != None:
            for tag in old_tags:
                if tag not in self.tags:
                    removeTag(remove_diacritics(tag.lower()), "forum", registry_id+"/"+name_id)
                        

    def deleteTopic(self):
        registry_id = self.registry_id
        name_id = self.name_id
        tags = self.tags

        self.delete()
    
        #remove as tags
        for tag in tags:
            removeTag(remove_diacritics(tag.lower()), "forum", registry_id+"/"+name_id)

                
         
class Reply(core.model.ActivDB):
    #_id            = <couchdb_id>
    # service       = "forum"
    # type          = "reply"
    # subtype       = None
    
    conteudo        = TextField()
        
    def retrieve(self, id, db=core.database.ACTIVDB):
        # chamada:
        #    _reply = model.Reply().retrieve(id)
        _tmp = super(Reply, self).retrieve(id,db)
        if _tmp: _tmp.__class__ = Reply
        return _tmp      


          
    