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

class Videoaula(core.model.ActivDB):
    #_id            = <couchdb_id>
    arqvideo      = TextField(default='')
    slides        = DictField()
    
    def retrieve(self, id, db=core.database.ACTIVDB):
        # chamada:
        #    _va0 = model.Videoaula().retrieve(id)
        _tmp = super(Videoaula, self).retrieve(id,db)
        if _tmp: _tmp.__class__ = Videoaula
        return _tmp

    @classmethod
    def retrieve_by_name_id(self, registry_id, name_id):
        # chamada: 
        #   _va = model.Videoaula.retrieve_by_name_id(registry_id, name_id)
        _tmp = super(Videoaula, self).retrieve_by_name_id("videoaula", "videoaula", registry_id, name_id)
        if _tmp:
            _va = Videoaula(**_tmp)       
            _va._data["_rev"] = _tmp["_rev"]
            _va._data["_id"] = _tmp["_id"]
            return _va
        else:
            return None  

    @classmethod    
    def listObjects(self, registry_id,  page, page_size, tag=None):
        return super(Videoaula, self).listObjects("videoaula", "videoaula", registry_id, page, page_size, tag)
    
    @classmethod    
    def countObjectsByRegistryId(self, registry_id):
        return super(Videoaula, self).countObjectsByRegistryId("videoaula", "videoaula", registry_id)
     
    @classmethod 
    def countObjectsByRegistryIdTags(self, registry_id, tag):
        return super(Videoaula, self).countObjectsByRegistryIdTags("videoaula", "videoaula", registry_id, tag)
     
    @classmethod
    def listAllTags(self, registry_id, tag=None):
        return super(Videoaula, self).listAllTags("videoaula", "videoaula", registry_id, tag)

    @classmethod
    def exists(self, registry_id, name_id):        
        return super(Videoaula, self).exists("videoaula", "videoaula", registry_id, name_id)


       