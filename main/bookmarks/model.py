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

def _strListSize(number, str, genero='M'):
    plural = lambda x: 's' if x!=1 else ''
    if number>0:
        return u"%d %s%s" % (number, str, plural(number))
    elif genero=='M':
        return u"nenhum %s" % str
    else:
        return u"nenhuma %s" % str

def _urlCount(url):
    for row in database.BOOKMARKS.view('bookmarks/count_by_url',startkey=url, group="true"):
        return row.value
    return 0
        
class Bookmarks(Document):
    # _id = <couchdb_id>
    registry_id    = TextField() # dono do bookmark: usuário ou comunidade
    owner          = TextField() # quem criou o bookmark.
                                 # caso bookmark seja de uma comunidade, owner!=registry_id
    url            = TextField()
    title          = TextField()
    description    = TextField()
    tags           = ListField(TextField())
    data_cri       = TextField()
    data_alt       = TextField()
    alterado_por   = TextField()
    comentarios    = ListField(DictField(Schema.build(
                            owner    = TextField(),
                            comment  = TextField(),
                            data_cri = TextField()
                     )))

    @classmethod
    def createBookmarkLink(self, user, url):
        for item in database.BOOKMARKS.view('bookmarks/by_registry_id_and_url',startkey=[user,url],endkey=[user, url, {}]):
            return ("Editar favorito", "/static/imagens/icones/bookmark32_true.png", "/bookmarks/popup/"+user+"?url="+url, "","",True)
        return ("Adicionar favorito", "/static/imagens/icones/bookmark32_false.png", "/bookmarks/popup/"+user+"?url="+url, "","",True)



    @classmethod
    def searchIdByUrl(self, registry_id, url):
        for row in database.BOOKMARKS.view('bookmarks/by_registry_id_and_url' ,startkey=[registry_id, url],endkey=[registry_id, url, {}]):
            return row.key[2]
        return None

    @classmethod
    def searchBookmarksByUrl(self, user, page, page_size, url):
        bookmarks = []
        # Obtem uma página de resultados no BD
        # descending=true para listar os mais recentes primeiro
        # como a árvore é percorrida em sentido inverso, endkey é o documento inicial e startkey é o final.           
        for row in database.BOOKMARKS.view('bookmarks/by_url' ,startkey=[url, {}, {}], endkey=[url], descending="true", skip=(page-1)*page_size , limit=page_size):
            (url, data_alt, bookmark_id) = row.key
            bookmark_data = dict()
            bookmark_data["registry_id"] = row.value["registry_id"]
            bookmark_data["owner"] = row.value["owner"]
            bookmark_data["description"] = row.value["description"]
            bookmark_data["title"] = row.value["title"]
            bookmark_data["url"] = row.value["url"]
            bookmark_data["tags"] = row.value["tags"]
            bookmark_data["id"] = bookmark_id
            
            bookmark_data["alterar"] = isAllowedToWriteObject(user, "bookmarks", row.value["registry_id"])
            bookmark_data["apagar"] = bookmark_data["alterar"] and isAllowedToDeleteObject(user, row.value["owner"], row.value["registry_id"]+"/"+bookmark_id)

           
            bookmark_data["data_nofmt"] = row.value["data_alt"]
            bookmark_data["data_alt"] = short_datetime(row.value["data_alt"])
            bookmark_data["alterado_por"] = row.value["alterado_por"]
            bookmark_data["num_comments"] = _strListSize (len(row.value["comentarios"]), u"comentário")
            #bookmark_data["url_count"] = _strListSize (_urlCount(bookmark_data["url"]), u"referência", genero='F')
            #url_count = _urlCount(bookmark_data["url"])
            bookmark_data["url_count"] = ""
            #if url_count > 1: bookmark_data["url_count"] = u"%d usuários marcaram esta página" % url_count

            bookmarks.append(bookmark_data)
            
        bookmarks = sorted(bookmarks, key=itemgetter("data_nofmt"), reverse = True)
        return bookmarks
       
    @classmethod
    def countBookmarksByUrl(self, url):
        for row in database.BOOKMARKS.view('bookmarks/count_by_url', \
                                           startkey=url, \
                                           group="true"):        
            return row.value
        return 0
        
    @classmethod
    def countBookmarksByRegistryId(self, registry_id):
        for row in database.BOOKMARKS.view('bookmarks/count_by_registry_id', \
                                           startkey=[registry_id],endkey=[registry_id, {}], \
                                           group_level=1, group="true"):        
            return row.value
        return 0

    @classmethod
    def countBookmarksByRegistryIdAndTag(self, registry_id, tag):
        for row in database.BOOKMARKS.view('bookmarks/count_by_registry_id_and_tag', \
                                           startkey=[registry_id, tag],endkey=[registry_id, tag, {}], \
                                           group_level=1, group="true"):        
            return row.value
        return 0
                
    @classmethod
    def listBookmarks(self, user, registry_id, page, page_size, tag=None):
        bookmarks = []
        if tag:
            view_name = 'bookmarks/by_registry_id_and_tag'
            start_key = [registry_id, tag]
            end_key = [registry_id, tag, {}, {}]
        else:
            view_name = 'bookmarks/by_registry_id'
            start_key = [registry_id]
            end_key = [registry_id, {}, {}]

        # Obtem uma página de resultados no BD
        # descending=true para listar os mais recentes primeiro
        # como a árvore é percorrida em sentido inverso, endkey é o documento inicial e startkey é o final.     
        for row in database.BOOKMARKS.view(view_name, startkey=end_key,endkey=start_key, descending="true", skip=(page-1)*page_size , limit=page_size):
            if tag:
                (registry_id, tag_found, data_alt, bookmark_id) = row.key
            else:
                (registry_id, data_alt, bookmark_id) = row.key

            bookmark_data = dict()
            bookmark_data["registry_id"] = registry_id
            bookmark_data["owner"] = row.value["owner"]
            bookmark_data["description"] = row.value["description"]
            bookmark_data["title"] = row.value["title"]
            bookmark_data["url"] = row.value["url"]
            bookmark_data["tags"] = row.value["tags"]
            bookmark_data["id"] = bookmark_id
            
            # _file = Files().retrieve(file_id)
            bookmark_data["alterar"] = isAllowedToWriteObject(user, "bookmarks", registry_id)
            bookmark_data["apagar"] = bookmark_data["alterar"] and isAllowedToDeleteObject(user, row.value["owner"], registry_id+"/"+bookmark_id)
            
            
            bookmark_data["data_nofmt"] = row.value["data_alt"]
            bookmark_data["data_alt"] = short_datetime(row.value["data_alt"])
            bookmark_data["alterado_por"] = row.value["alterado_por"]
            bookmark_data["num_comments"] = _strListSize (len(row.value["comentarios"]), u"comentário")
            #bookmark_data["url_count"] = _strListSize (url_count, u"referência", genero='F')
            url_count = _urlCount(bookmark_data["url"])
            bookmark_data["url_count"] = ""
            if url_count > 1: bookmark_data["url_count"] = u"%d usuários marcaram esta página" % url_count
            
            bookmarks.append(bookmark_data)
        return bookmarks

 
    @classmethod
    def listAllTags(self, registry_id, tag=None):
    
        tags_list = []
        for row in database.BOOKMARKS.view('bookmarks/by_registry_id_and_tag', startkey = [registry_id], endkey = [registry_id, {}, {}, {}]):
            (registry_id, tag_found, data_alt, bookmark_id) = row.key
            tags_list.append(tag_found)

        if tag and tag in tags_list:
            tags_list.remove(tag)
        tags_list = sorted(set(tags_list))    
        return tags_list

    def saveBookmark(self, id=None):
        self.save(id=id)
    
        # atualiza tabela de tags
        # vai para o tags.model
        data_tag = str(datetime.now())
        for tag in self.tags:
            if self.title:
                nome = self.title  
            else:
                url = self.url
                url = remove_special_chars(remove_diacritics(url.replace(" ","_")))
                nome = url
            addTag(tag, self.registry_id, self.owner, "bookmarks", self.id, nome, data_tag)
        
    def deleteBookmark(self):
        tags = self.tags
        self.delete()
    
        # atualiza tabela de tags
        # vai para o tags.model
        for tag in tags:
            removeTag(remove_diacritics(tag.lower()), "bookmarks", self.id)
        
    def editBookmark(self, user, newtitle, newdesc, newtags):
        # preserva tags anteriores
        old_tags = self.tags
    
        self.title = newtitle
        self.description = newdesc
        self.tags = newtags
        self.alterado_por = user
        self.data_alt = str(datetime.now())
        self.save()
    
        # compara as tags anteriores com as modificadas, atualizando a lista de tags no BD
        data_tag = str(datetime.now())
        if self.title:
            nome = self.title
        else:
            url = self.url
            url = remove_special_chars(remove_diacritics(url.replace(" ","_")))
            nome = url
        
        for tag in self.tags:
            if tag not in old_tags:
                addTag(tag, self.registry_id, user, "bookmarks", self.id, nome, data_tag)
        
        for tag in old_tags:
            if tag not in self.tags:
                removeTag(remove_diacritics(tag.lower()), "bookmarks", self.id)
    
    def addBookmarkComment(self, owner, comment):
        self.comentarios.append(dict(
                                  owner = owner,
                                  comment = comment,
                                  data_cri = str(datetime.now())
                                ))
        self.save()
    
    def prepareCommentsToPrint(self, user):
        for comment in self.comentarios:
            comment["apagar"] = isAllowedToDeleteComment(user, self.registry_id, comment["owner"])
            comment["data_fmt"] = short_datetime(comment["data_cri"])
            comment["comment"] = comment["comment"].replace("\r\n", "<br/>")
        self.comentarios = sorted(self.comentarios, key=itemgetter("data_cri"), reverse=True)
    
    def deleteBookmarkComment(self, owner, data_cri):
        for comentario in self.comentarios:
            if comentario["owner"]==owner and comentario["data_cri"]==data_cri:
                self.comentarios.remove(comentario)
                self.save()
                return True
        return False
    
    def save(self, id=None, db=database.BOOKMARKS):
        if not self.id and id: self.id = id
        self.store(db)
        
    def retrieve(self, id, db=database.BOOKMARKS):
        return Bookmarks.load(db, id)
    
    def delete(self, db=database.BOOKMARKS):
        #db.delete(self)
        del db[self.id]
        
        