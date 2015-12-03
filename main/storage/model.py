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

import database

from datetime import datetime


class Storage(Document):
    user           = DictField() 
    #    Schema.build(
    #                    key1           = TextField(), # string json
    #                    key2           = TextField(), # string json
    #                    keyN           = TextField(), # string json
    #                    data_alt       = TextField(),
    #                    alterado_por   = TextField()
    #                 )
     
         
           

    def getValue(self, registry_id, key):
        if registry_id in self and key in self[registry_id]:
           return self[registry_id][key]
        else:
            return None
       
    def setValue(self, registry_id, key, value):
        if registry_id in self:
            self[registry_id][key] = value
        else:
            self[registry_id]  = { key:value }
             
    def save(self, id=None, db=database.STORAGE):
        if not self.id and id: self.id = id
        self.store(db)
        
    def retrieve(self, id, db=database.STORAGE):
        return Storage.load(db, id)
        
    def delete(self, db=database.STORAGE):
        #db.delete(self)
        del db[self.id]
        
class Activlet(Document):
    owner        = TextField()
    access_key   = TextField()
    source_code  = TextField()
    data_cri     = TextField()  

    def save(self, id=None, db=database.ACTIVLETS):
        if not self.id and id: self.id = id
        self.store(db)
        
    def retrieve(self, id, db=database.ACTIVLETS):
        return Activlet.load(db, id)
        
    def delete(self, db=database.ACTIVLETS):
        #db.delete(self)
        del db[self.id]
        
        