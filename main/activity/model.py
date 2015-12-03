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
            1                         n
group     <----------------------------> atividade
-----                                    ------
group=[list_tesk]
   
"""

class Group(core.model.ActivDB):
    #_id           = <couchdb_id>   

    observacoes         = TextField()
 
 
    @classmethod
    def countObjectsByGroup(self, id):
        return super(Group, self).countObjectsByGroup(id)
    
    def GroupIsFilled(self, registry_id, finalized = None):
        dict_temp = {}
        if finalized == None:
            for row in core.database.ACTIVDB.view('activity/by_group', startkey=[registry_id], endkey=[registry_id,{}], group=True, group_level=2):
                
                if row.value > 0:   
                    dict_temp.update({row.key[1]: True})
                   
        else:
            
            for row in core.database.ACTIVDB.view('activity/by_group', startkey=[registry_id], endkey=[registry_id,{}], group=True, group_level=3):
               
                if row.key[2]=="finalizado" and row.value > 0:   
                    dict_temp.update({row.key[1]: True})
                   
        return dict_temp
    
    def retrieve(self, id, db=core.database.ACTIVDB):
        _tmp = super(Group, self).retrieve(id,db)
        if _tmp: _tmp.__class__ = Group
        return _tmp
    
    def save(self, id=None, db=core.database.ACTIVDB):
            if not self.id and id: self.id = id
            self.store(db)          
            
            
class Activity(core.model.ActivDB):
    #_id                = <couchdb_id>
    observacao          = TextField()
    data_start          = TextField()
    data_end            = TextField()
    data_conclusion     = TextField()
    prioritario         = TextField()
    status              = TextField()
    encarregados        = ListField(TextField())
    
    @classmethod    
    def listfinalizedByRegistry_id(self, registry_id):
        list_tmp=[]
        
        for row in core.database.ACTIVDB.view('activity/finalized_and_groups', startkey=[registry_id], endkey=[registry_id,{}]):
            list_tmp.append(row) 
        return list_tmp


    @classmethod    
    def listPendentActivities(self, registry_id):
        list_tmp=[]
        
        for row in core.database.ACTIVDB.view('activity/pendent', startkey=[registry_id], endkey=[registry_id,{}]):
                list_tmp.append(row)
        return list_tmp
 
    @classmethod    
    def listActivities(self, registry_id):
        list_tmp=[]
        n=1
        for row in core.database.ACTIVDB.view('activity/list_by_registry', startkey=[registry_id], endkey=[registry_id,{}]):
             
            if row.key[3] and row.value['status'] =="finalizado" and n <= 10:
                list_tmp.append(row)
                n = n+1 
            elif row.key[3]== 0 or (row.key[3]==1 and row.value['status'] != "finalizado"):
                list_tmp.append(row)
              
        return list_tmp 
 
    
    def retrieve(self, id, db=core.database.ACTIVDB):
        # chamada:
        #    _task = model.Task().retrieve(id)
        _tmp = super(Activity, self).retrieve(id,db)
        if _tmp: _tmp.__class__ = Activity
        return _tmp      
    
    def save(self, id=None, db=core.database.ACTIVDB):
            if not self.id and id: self.id = id
            self.store(db)          


