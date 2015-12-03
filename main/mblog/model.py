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
import core.database
from libs.dateformat import short_datetime, human_date
from core.model import isUserOrMember, isAUser

_EMPTYMBLOG = lambda:dict(
# _id = "couchdb_id"
          registry_id = ""  # dono do mblog: usuário ou comunidade
        , owner = ""        # quem postou. caso mblog seja de uma comunidade, owner!=registry_id
        , conteudo = ""
        , conteudo_original = "" # conteúdo do post original, caso este post seja um compartilhamento
        , tags = []
        , reply_to = ""     # mblog_id do post respondido por este
        , interessados = [] # lista dos registry_ids dos interessados neste post.
                            # esta informação é necessária para facilitar a exclusão do mblog.
        , mencionados = []  # lista dos registry_ids mencionados nesse post.
        , data_cri = ""
                # caso este post seja o compartilhamento de outro:
                # registry_id, owner e data_cri guardam informações de quem compartilhou
                # registry_id_original, owner_original e data_original guardam informações do post original
        , registry_id_original = "" 
        , owner_original = ""
        , data_original = ""
        , mblog_id_original = ""
                # caso este post tenha sido compartilhado por outros: 
                # share_list é a lista de compartilhamentos (mblog_ids) que ele possui.
        , share_list = []
)


class Mblog(Document):
    # _id = "couchdb_id"
    registry_id = TextField()             # dono do mblog: usuário ou comunidade
    owner = TextField()                   # quem postou. caso mblog seja de uma comunidade, owner!=registry_id
    conteudo = TextField()
    conteudo_original = TextField()       # conteúdo do post original, caso este post seja um compartilhamento
    tags = ListField(TextField())
    reply_to = TextField()                # mblog_id do post respondido por este
    interessados = ListField(TextField()) # lista dos registry_ids dos interessados neste post.
                                          # esta informação é necessária para facilitar a exclusão do mblog.
    mencionados = ListField(TextField())  # lista dos registry_ids mencionados nesse post.
    data_cri = TextField()
    
          # caso este post seja o compartilhamento de outro:
          # registry_id, owner e data_cri guardam informações de quem compartilhou
          # registry_id_original, owner_original e data_original guardam informações do post original
    registry_id_original = TextField()
    owner_original = TextField()
    data_original = TextField()
    mblog_id_original = TextField()
    
          # caso este post tenha sido compartilhado por outros: 
          # share_list é a lista de compartilhamentos (mblog_ids) que ele possui.
    share_list = ListField(TextField())

    # Extrai do documento do couchDB, o dicionário com todas as propriedades
    def props(self):
        return dict([(k,v) for k,v in self.items()])
        
    def propsWithoutId(self):
        return dict([(k,v) for k,v in self.items()
                                        if k not in ('_id', '_rev')])

    @classmethod 
    def listPosts(self, user, registry_id, page, page_size, myself=False, myposts=0):
        # Lista os posts de registry_id. Se user = registry_id, myself=True
        lista_posts = []
        if myself and myposts!=1:
            # Estou vendo meu próprio mblog: vejo mensagens que me interessam.
            
            for row in database.MBLOG.view('mblog/by_followers',startkey=[registry_id, {}],endkey=[registry_id], \
                                           descending="true", skip=(page-1)*page_size , limit=page_size):
                mblog_data = dict()
                mblog_data.update(row.value)
                mblog_data["apagar"] = (row.value["owner"] == user)
                mblog_data["data_nofmt"] = row.value["data_cri"]
                mblog_data["data_cri"] = human_date(row.value["data_cri"])
                if "data_original" in row.value:
                    mblog_data["data_original"] = human_date(row.value["data_original"])
                lista_posts.append(mblog_data)
                
        else:
            # Estou vendo o mblog de outra pessoa ou de uma comunidade: 
            # só vejo mensagens postadas por ela.
          
            for row in database.MBLOG.view('mblog/by_owners',startkey=[registry_id, {}],endkey=[registry_id], \
                                           descending="true", skip=(page-1)*page_size , limit=page_size):
                mblog_data = dict()
                mblog_data.update(row.value)
                mblog_data["apagar"] = (row.value["owner"] == user)
                mblog_data["data_nofmt"] = row.value["data_cri"]
                mblog_data["data_cri"] = human_date(row.value["data_cri"])
                if "data_original" in row.value:
                    mblog_data["data_original"] = human_date(row.value["data_original"])

                if isAUser(registry_id):
                    community_id = ""
                    if registry_id != mblog_data["registry_id"]:
                        community_id = mblog_data["registry_id"]
                    
                    if (not community_id) or \
                       (community_id in core.database.REGISTRY and \
                       core.database.REGISTRY[community_id]["privacidade"]!="Privada"):
                        lista_posts.append(mblog_data)
                else:
                    lista_posts.append(mblog_data)

        return lista_posts

    
    @classmethod 
    def countPosts(self, user, registry_id, myself=False):
        # Lista os posts de registry_id. Se user = registry_id, myself=True
        if myself:
            # Estou vendo meu próprio mblog: vejo mensagens que me interessam.
            for row in database.MBLOG.view('mblog/count_followers',key=registry_id, group="true"):
                return row.value
            return 0
                    
        else:
            # estou vendo o mblog de outra pessoa ou de uma comunidade: 
            # só vejo mensagens postadas por ela.
            for row in database.MBLOG.view('mblog/count_owners',key=registry_id, group="true"):
                return row.value
            return 0
        
            """      
            for row in database.MBLOG.view('mblog/by_owners',startkey=[registry_id],endkey=[registry_id, {}]):

                if isAUser(registry_id):
                    community_id = row.value["registry_id"] if registry_id != row.value["registry_id"] else ""
                    
                    if (not community_id) or \
                       (community_id in core.database.REGISTRY and \
                       core.database.REGISTRY[community_id]["privacidade"]!="Privada"):
                        total = total + 1
                else:
                    total = total + 1
            

        return total
        """

    @classmethod 
    def listMentions(self, user, registry_id, page, page_size):
        lista_posts = []
        for row in database.MBLOG.view('mblog/by_mentioned',startkey=[registry_id, {}],endkey=[registry_id], \
                                           descending="true", skip=(page-1)*page_size , limit=page_size):
            mblog_data = dict()
            mblog_data.update(row.value)
            
            mblog_data["apagar"] = (row.value["owner"] == user)
            mblog_data["data_cri"] = human_date(row.value["data_cri"])
            mblog_data["data_nofmt"] = row.value["data_cri"]
            mblog_data["data_original"] = human_date(row.value["data_original"])
            
            lista_posts.append(mblog_data)
        return lista_posts
 
    @classmethod 
    def countMentions(self, registry_id):
        for row in database.MBLOG.view('mblog/count_mentions',key=registry_id, group="true"):
            return row.value
        return 0
                    
    def save(self, id=None, db=database.MBLOG):
        if not self.id and id: self.id = id
        self.store(db)
        
    def retrieve(self, id, db=database.MBLOG):
        return Mblog.load(db, id)
  
    def delete(self, db=database.MBLOG):
        del db[self.id]  
