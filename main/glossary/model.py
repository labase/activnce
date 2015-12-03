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
from search.model import addTag, removeTag
from libs.permissions import isAllowedToDeleteObject, isAllowedToWriteObject, isAllowedToDeleteComment
from libs.dateformat import short_datetime
from libs.strformat import remove_diacritics, remove_special_chars

from datetime import datetime
import operator
from operator import itemgetter


def _itemIdCount(item_id):
    for row in database.GLOSSARY.view('glossary/count_by_item_id',startkey=item_id, group="true"):
        return row.value
    return 0
        
class Glossary(Document):
    # _id = "registry_id/term_id
    registry_id    = TextField() # dono do item de glossário: usuário ou comunidade
    owner          = TextField() # quem criou o item de glossário.
                                 # caso o glossário seja de uma comunidade, owner!=registry_id
    item_id        = TextField()
    term           = TextField()
    definition    = TextField()
    tags           = ListField(TextField())
    data_cri       = TextField()
    data_alt       = TextField()
    alterado_por   = TextField()

    @classmethod
    def searchItemByRegistryIdAndItemId(self, user, registry_id, item_id, pode_modificar=False):
        glossary = []

        view_name = 'glossary/by_registry_id_and_item_id'
        start_key = [registry_id, item_id]
        end_key   = [registry_id, item_id, {}]
        
        for row in database.GLOSSARY.view(view_name,startkey=start_key,endkey=end_key):
            (registry_id, glossary_item_id) = row.key                
            glossary_data = dict()
            glossary_data["id"] = glossary_id = registry_id+"/"+glossary_item_id
            glossary_data["registry_id"] = registry_id
            glossary_data["owner"] = row.value["owner"]
            glossary_data["item_id"] = glossary_item_id
            glossary_data["term"] = row.value["term"]
            glossary_data["definition"] = row.value["definition"]
            glossary_data["tags"] = row.value["tags"]
            
            # _file = Files().retrieve(file_id)
            if pode_modificar:
                glossary_data["alterar"] = isAllowedToWriteObject(user, "glossary", registry_id)
                glossary_data["apagar"] = glossary_data["alterar"] and isAllowedToDeleteObject(user, row.value["owner"], glossary_id)
                
            else:
                glossary_data["apagar"] = glossary_data["alterar"] = False
                
            glossary_data["data_nofmt"] = row.value["data_alt"]
            glossary_data["data_alt"] = short_datetime(row.value["data_alt"])
            glossary_data["alterado_por"] = row.value["alterado_por"]
            #glossary_data["term_count"] = _strListSize (term_count, u"referência", genero='F')
            term_count = _itemIdCount(glossary_data["item_id"])
            glossary_data["term_count"] = ""
            if term_count > 1: glossary_data["term_count"] = u"%d usuários definiram este termo" % term_count
            
            glossary.append(glossary_data)
            
        return glossary
                    
    @classmethod
    def searchGlossaryByItemId(self, user, item_id, page, page_size):
        glossary = []
        for row in database.GLOSSARY.view('glossary/by_item_id', startkey=[item_id], endkey=[item_id, {}], skip=(page-1)*page_size , limit=page_size):
            (item_id, registry_id) = row.key
            glossary_data = dict()
            glossary_data["id"] = glossary_id = registry_id+"/"+item_id
            glossary_data["registry_id"] = registry_id
            glossary_data["owner"] = row.value["owner"]
            glossary_data["item_id"] = item_id
            glossary_data["term"] = row.value["term"]
            glossary_data["definition"] = row.value["definition"]
            glossary_data["tags"] = row.value["tags"]
            
            glossary_data["alterar"] = isAllowedToWriteObject(user, "glossary", registry_id)
            glossary_data["apagar"] = glossary_data["alterar"] and isAllowedToDeleteObject(user, row.value["owner"], glossary_id)
            
            glossary_data["data_nofmt"] = row.value["data_alt"]
            glossary_data["data_alt"] = short_datetime(row.value["data_alt"])
            glossary_data["alterado_por"] = row.value["alterado_por"]

            #term_count = _itemIdCount(glossary_data["item_id"])
            glossary_data["term_count"] = ""
            #if term_count > 1: glossary_data["term_count"] = u"%d usuários definiram este termo" % term_count
            
            glossary.append(glossary_data)
            
        glossary = sorted(glossary, key=itemgetter("data_nofmt"), reverse = True)
        return glossary

    @classmethod
    def countGlossaryByItemId(self, item_id):
        for row in database.GLOSSARY.view('glossary/count_by_item_id', \
                                           startkey=item_id, \
                                           group="true"):        
            return row.value
        return 0
        
    @classmethod
    def countGlossaryByRegistryId(self, registry_id):
        for row in database.GLOSSARY.view('glossary/count_by_registry_id', \
                                           startkey=[registry_id],endkey=[registry_id, {}], \
                                           group_level=1, group="true"):        
            return row.value
        return 0

    @classmethod
    def countGlossaryByRegistryIdAndTag(self, registry_id, tag):
        for row in database.GLOSSARY.view('glossary/count_by_registry_id_and_tag', \
                                           startkey=[registry_id, tag],endkey=[registry_id, tag, {}], \
                                           group_level=1, group="true"):        
            return row.value
        return 0
    
    @classmethod
    def listGlossary(self, user, registry_id, page, page_size, tag=None):
        glossary = []
        if tag:
            view_name = 'glossary/by_registry_id_and_tag'
            start_key = [registry_id, tag]
            end_key = [registry_id, tag, {}]
        else:
            view_name = 'glossary/by_registry_id'
            start_key = [registry_id]
            end_key = [registry_id, {}]
            
        # Obtem uma página de resultados no BD
        for row in database.GLOSSARY.view(view_name, startkey=start_key, endkey=end_key, skip=(page-1)*page_size , limit=page_size):
            if tag:
                (registry_id, tag_found, glossary_item_id) = row.key
            else:
                (registry_id, glossary_item_id) = row.key
                
            glossary_data = dict()
            glossary_data["id"] = glossary_id = registry_id+"/"+glossary_item_id
            glossary_data["registry_id"] = registry_id
            glossary_data["owner"] = row.value["owner"]
            glossary_data["item_id"] = glossary_item_id
            glossary_term = glossary_data["term"] = row.value["term"]
            glossary_data["key_to_compare"] = remove_diacritics(" ".join(glossary_term.lower().split()))
            glossary_data["definition"] = row.value["definition"]
            glossary_data["tags"] = row.value["tags"]
            
            # _file = Files().retrieve(file_id)
            glossary_data["alterar"] = isAllowedToWriteObject(user, "glossary", registry_id)
            glossary_data["apagar"] = glossary_data["alterar"] and isAllowedToDeleteObject(user, row.value["owner"], glossary_id)
            
            glossary_data["data_nofmt"] = row.value["data_alt"]
            glossary_data["data_alt"] = short_datetime(row.value["data_alt"])
            glossary_data["alterado_por"] = row.value["alterado_por"]
            #glossary_data["term_count"] = _strListSize (term_count, u"referência", genero='F')
            term_count = _itemIdCount(glossary_data["item_id"])
            glossary_data["term_count"] = ""
            if term_count > 1: glossary_data["term_count"] = u"%d usuários definiram este termo" % term_count
            
            glossary.append(glossary_data)
            
        glossary = sorted(glossary, key=itemgetter("key_to_compare"), reverse = False)
        return glossary

    @classmethod
    def listAllTags(self, registry_id, tag=None):
        tags_list = []
            
        # Obtém os resultados do filtro de todos as chaves por registry_id
        for row in database.GLOSSARY.view('glossary/by_registry_id_and_tag',  startkey = [registry_id], endkey = [registry_id, {}, {}, {}]):
            (registry_id, tag_found, glossary_item_id) = row.key
            tags_list.append(tag_found) 
        if tag and tag in tags_list:
            tags_list.remove(tag)
        tags_list = sorted(set(tags_list))
        return tags_list

    def saveGlossaryItem(self, id=None):
        self.save(id=id)
    
        # atualiza tabela de tags
        # vai para o tags.model
        data_tag = str(datetime.now())
        for tag in self.tags:
            addTag(tag, self.registry_id, self.owner, "glossary", self.id, self.term, data_tag)
        
    def deleteGlossaryItem(self):
        tags = self.tags
        self.delete()
    
        # atualiza tabela de tags
        # vai para o tags.model
        for tag in tags:
            removeTag(remove_diacritics(tag.lower()), "glossary", self.id)
        
    def editGlossaryItem(self, user, newdef, newtags):
        # preserva tags anteriores
        old_tags = self.tags
    
        self.definition = newdef
        self.tags = newtags
        self.alterado_por = user
        self.data_alt = str(datetime.now())
        self.save()
    
        # compara as tags anteriores com as modificadas, atualizando a lista de tags no BD
        data_tag = str(datetime.now())
        for tag in self.tags:
            if tag not in old_tags:
                addTag(tag, self.registry_id, user, "glossary", self.id, self.term, data_tag)
        
        for tag in old_tags:
            if tag not in self.tags:
                removeTag(remove_diacritics(tag.lower()), "glossary", self.id)
    
    def save(self, id=None, db=database.GLOSSARY):
        if not self.id and id: self.id = id
        self.store(db)
        
    def retrieve(self, id, db=database.GLOSSARY):
        return Glossary.load(db, id)
    
    def delete(self, db=database.GLOSSARY):
        #db.delete(self)
        del db[self.id]
        
        