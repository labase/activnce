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

import tornado.web
from tornado.web import HTTPError
import tornado.template

import model
import database
import core.model
from core.database import DB_VERSAO_010
from core.model import isUserOrOwner, isUserOrMember, isFriendOrMember
import core.database

import log.model
from search.model import addTag, removeTag, splitTags

from core.dispatcher import BaseHandler, HANDLERS, URL_TO_PAGETITLE, \
                            NOMEUSERS, \
                            FILENAMECHARS, PAGENAMECHARS
                            

from libs.notify import Notify
import libs.permissions
from libs.permissions import isAllowedToDeleteObject, isAllowedToEditObject, isAllowedToComment, isAllowedToDeleteComment, \
                             isAllowedToWriteObject
from urllib import quote,unquote
import time
from datetime import datetime
import re
from datetime import datetime

''' importa definição do tutorial deste módulo, se existir _tutorial.py '''
from config import TUTORIAL
try:
    import _tutorial
except ImportError:
    pass

# Número máximo de itens exibidos na lista de favoritos de um usuário
NUM_MAX_FAVORITOS = 10


class BookmarkNewHandler(BaseHandler):
    ''' Inclusão de um link favorito do usuário '''
    
    @tornado.web.authenticated
    @core.model.userOrMember    
    @core.model.serviceEnabled('bookmarks')
    @libs.permissions.canWriteService ("bookmarks")
    def get(self, registry_id):
        user = self.get_current_user()
        self.render("modules/bookmarks/newbookmark-form.html", \
                    NOMEPAG='favoritos', REGISTRY_ID=registry_id, MSG="")

    @tornado.web.authenticated
    @core.model.userOrMember    
    @core.model.serviceEnabled('bookmarks')
    @libs.permissions.canWriteService ("bookmarks")
    def post(self, registry_id):
        user = self.get_current_user()
        url = self.get_argument("url","")
        if not url:
            self.render("modules/bookmarks/newbookmark-form.html", \
                        NOMEPAG='favoritos', REGISTRY_ID=registry_id, MSG=u"URL não preenchida")
            return
        if "://" not in url: url = "http://"+url
        bookmark_id = model.Bookmarks.searchIdByUrl(registry_id, url)
        if bookmark_id:
            self._bookmark = model.Bookmarks().retrieve(bookmark_id)
            self._bookmark.editBookmark(user, self.get_argument("title",""), 
                                self.get_argument("description",""), 
                                splitTags(self.get_argument("tags","")))
            log.model.log(user, u'alterou um link em favoritos de', objeto=registry_id, tipo="bookmarks")

        else:
            self._bookmarks = model.Bookmarks()
            self._bookmarks.url = url
            self._bookmarks.owner = self._bookmarks.alterado_por = user
            self._bookmarks.registry_id = registry_id
            self._bookmarks.title = self.get_argument("title","")
            self._bookmarks.description = self.get_argument("description","")
            self._bookmarks.tags = splitTags(self.get_argument("tags",""))
            self._bookmarks.data_cri = self._bookmarks.data_alt = str(datetime.now())
            self._bookmarks.saveBookmark()
            log.model.log(user, u'criou um link em favoritos de', objeto=registry_id, tipo="bookmarks")
        
        url = self.get_argument("url", "")
        tipo = self.get_argument("tipo","")
                
        if tipo == "popup":
            self.render("popup_msg.html", MSG="Favorito adicionado com sucesso!", REGISTRY_ID=registry_id)
        else:    
            self.redirect("/bookmarks/%s" % registry_id)


class BookmarkNewPopUpHandler(BaseHandler):
    ''' Inclusão de um link favorito do usuário '''
    
    @tornado.web.authenticated
    @core.model.userOrMember    
    @core.model.serviceEnabled('bookmarks')
    @libs.permissions.canWriteService ("bookmarks") 
    def get(self, registry_id):
        user = self.get_current_user()
        url = self.get_argument("url", "")
                    
        for row in database.BOOKMARKS.view('bookmarks/by_registry_id_and_url',startkey=[user,url],endkey=[user, url, {}]):        
            bookmark_id = row.key[2]
            self._bookmark = model.Bookmarks().retrieve(bookmark_id)
        
            self.render("modules/bookmarks/newbookmarkpopup-form.html", \
                        BOOKMARK=self._bookmark, \
                        NOMEPAG='favoritos', REGISTRY_ID=registry_id, MSG="", URL=url)
            return
        
        bookm = dict( title="",
                      description="",
                      tags=""
        )
        self.render("modules/bookmarks/newbookmarkpopup-form.html", \
                 BOOKMARK=bookm, \
                 NOMEPAG='favoritos', REGISTRY_ID=registry_id, MSG="", URL=url)     



class BookmarkListHandler(BaseHandler):
    ''' Exibe lista de favoritos do registry_id '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('bookmarks')
    @libs.permissions.canReadService ("bookmarks")
    def get(self, registry_id):
        user = self.get_current_user()
        page = int(self.get_argument("page","1"))

        bookm_count = model.Bookmarks.countBookmarksByRegistryId(registry_id)
        # Se forem todas as tags da página mostrada
        #(bookmarks, tags_list) = model.Bookmarks.listBookmarks(user, registry_id, page, NUM_MAX_FAVORITOS, all_tags=False)
        # Se forem todas as tags
        bookmarks = model.Bookmarks.listBookmarks(user, registry_id, page, NUM_MAX_FAVORITOS)

        tags_list = model.Bookmarks.listAllTags(registry_id)
        links = []
        if isAllowedToWriteObject(user, "bookmarks", registry_id):
            links.append((u"Criar novo favorito", "/static/imagens/icones/new32.png", "/bookmarks/new/"+registry_id))
        if isUserOrOwner(user, registry_id):
            links.append((u"Alterar permissões dos Favoritos", "/static/imagens/icones/permissions32.png", "/permission/bookmarks/"+registry_id, "", "", True))

        log.model.log(user, u'acessou os favoritos de', objeto=registry_id, tipo="bookmarks", news=False)
        
        self.render("modules/bookmarks/bookmarks-list.html", NOMEPAG='favoritos', \
                    REGISTRY_ID=registry_id, CRIAR=isUserOrMember(user,registry_id), \
                    TAG=None, LINKS=links, \
                    FOTO=False, \
                    BOOKMARKS=bookmarks, BOOKM_COUNT=bookm_count, \
                    TAGS = tags_list, \
                    PAGE=page, PAGESIZE=NUM_MAX_FAVORITOS, \
                    TITLE="Favoritos de %s"%registry_id, \
                    MSG="")


class BookmarkUserTagHandler(BaseHandler):
    ''' Exibe bookmarks de um usuário com uma tag específica '''
    
    @core.model.allowedToAccess
    @core.model.serviceEnabled('bookmarks')
    @libs.permissions.canReadService ("bookmarks")
    def get(self, registry_id, tag):
        user = self.get_current_user()
        page = int(self.get_argument("page","1"))
        bookm_count = model.Bookmarks.countBookmarksByRegistryIdAndTag(registry_id, tag)
        #(bookmarks, tags_list) = model.Bookmarks.listBookmarks(user, registry_id, page, NUM_MAX_FAVORITOS, tag)
        bookmarks = model.Bookmarks.listBookmarks(user, registry_id, page, NUM_MAX_FAVORITOS, tag)
        tags_list = model.Bookmarks.listAllTags(registry_id, tag)

        log.model.log(user, u'acessou os favoritos de', objeto=registry_id, tipo="bookmarks", news=False)
                
        self.render("modules/bookmarks/bookmarks-list.html", NOMEPAG='favoritos', \
                    REGISTRY_ID=registry_id, CRIAR=isUserOrMember(user,registry_id), \
                    TAG=tag, LINKS=[], \
                    FOTO=False, \
                    BOOKMARKS=bookmarks, BOOKM_COUNT=bookm_count, \
                    TAGS = tags_list, \
                    PAGE=page, PAGESIZE=NUM_MAX_FAVORITOS, \
                    TITLE="Favoritos de %s com a tag %s"%(registry_id,tag), \
                    MSG="")

class BookmarkDeleteHandler(BaseHandler):
    ''' Apaga favorito do usuário '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('bookmarks')
    @libs.permissions.canWriteService ("bookmarks")
    
    def get(self, registry_id):
        user = self.get_current_user()
        
        bookmark_id = self.get_argument("id","")
        self._bookmark = model.Bookmarks().retrieve(bookmark_id)
        
        if self._bookmark != None:
            bookmark_owner = self._bookmark.owner
            if not isAllowedToDeleteObject(user, bookmark_owner, registry_id+"/"+bookmark_id):
                raise HTTPError(403)
                return

            url = self._bookmark.url
            self._bookmark.deleteBookmark()
            
            # notifica o dono do arquivo excluído
            email_msg = "Favorito removido: "+url+"\n"+\
                        Notify.assinatura(user, registry_id, str(datetime.now()))+"\n\n"
            Notify.email_notify(bookmark_owner, user, u"removeu um favorito criado por você", \
                           message=email_msg, \
                           link="bookmarks/"+registry_id)
                            
            log.model.log(user, u'removeu um link de favoritos de', objeto=registry_id, tipo="bookmarks")
            
            self.redirect("/bookmarks/%s" % registry_id)
            return
        else:
            raise HTTPError(404)



class BookmarkEditHandler(BaseHandler):
    ''' Alteração de favoritos '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('bookmarks')
    @libs.permissions.canWriteService ("bookmarks")
    def get(self, registry_id):
        user = self.get_current_user()
        bookmark_id = self.get_argument("id","")
        self._bookmark = model.Bookmarks().retrieve(bookmark_id)
        
        if self._bookmark != None:
            #if isAllowedToEditObject(user, self._bookmark.owner, registry_id+"/"+bookmark_id):
            if isAllowedToWriteObject(user, "bookmarks", registry_id):
                self.render("modules/bookmarks/bookmark-edit.html", \
                            NOMEPAG='favoritos', REGISTRY_ID=registry_id, \
                            BOOKMARK=self._bookmark, MSG="")
            else:
                raise HTTPError(403)

        else:
            raise HTTPError(404)

    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('bookmarks')
    @libs.permissions.canWriteService ("bookmarks")
    def post(self, registry_id):
        user = self.get_current_user()
        bookmark_id = self.get_argument("id","")

        self._bookmark = model.Bookmarks().retrieve(bookmark_id)
        
        if self._bookmark != None:
            #if isAllowedToEditObject(user, self._bookmark.owner, registry_id+"/"+bookmark_id):
            if isAllowedToWriteObject(user, "bookmarks", registry_id):
                
                self._bookmark.editBookmark(user, self.get_argument("title",""), 
                                    self.get_argument("description",""), 
                                    splitTags(self.get_argument("tags","")))

                log.model.log(user, u'alterou um link de favoritos de', objeto=registry_id, tipo="bookmarks")
                self.redirect("/bookmarks/%s" % registry_id)
                
            else:
                raise HTTPError(403)

        else:
            raise HTTPError(404)



class BookmarkCommentHandler(BaseHandler):
    ''' Inclusão de um comentário de um arquivo '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('bookmarks')
    
    def get(self, registry_id):
        user = self.get_current_user()
        bookmark_id = self.get_argument("id","")

        self._bookmark = model.Bookmarks().retrieve(bookmark_id)
        if self._bookmark != None:
            self._bookmark.prepareCommentsToPrint(user)
            self.render("modules/bookmarks/comments-list.html", NOMEPAG='favoritos', \
                        REGISTRY_ID=registry_id, COMENTAR=isAllowedToComment(user, registry_id+"/"+bookmark_id, self._bookmark.owner), \
                        BOOKMARK=self._bookmark, MSG="")

        else:
            raise HTTPError(404)

    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('bookmarks')
    def post(self, registry_id):
        user = self.get_current_user()
        bookmark_id = self.get_argument("id","")
        comentario = self.get_argument("comment","")
        
        self._bookmark = model.Bookmarks().retrieve(bookmark_id)
        if self._bookmark:
            if isAllowedToComment(user, registry_id+"/"+bookmark_id, self._bookmark.owner):
            
                if comentario:
                    self._bookmark.addBookmarkComment(user, comentario)
                   
                   
                    # notifica o dono do favorito comentado
                    email_msg = "Favorito: "+self._bookmark.url+"\n"+\
                                self._bookmark.comentarios[-1]["comment"]+"\n"+\
                                Notify.assinatura(user, registry_id, self._bookmark.comentarios[-1]["data_cri"])+"\n\n"
                    Notify.email_notify(self._bookmark.owner, user, "comentou seu favorito", \
                                   message=email_msg, \
                                   link="bookmarks/comment/%s?id=%s"%(registry_id, self._bookmark.id))
                    
                    log.model.log(user, u'comentou um link favorito de', objeto=registry_id, tipo="bookmarks")
                    self.redirect("/bookmarks/comment/%s?id=%s" % (registry_id, self._bookmark.id))
                    
                else:
                    self.render("home.html", MSG=u"O comentário não pode ser vazio.", REGISTRY_ID=registry_id, NOMEPAG='favoritos')
            else:
                raise HTTPError(403)
        else:
            raise HTTPError(404)


class BookmarkDeleteCommentHandler(BaseHandler):
    ''' Apaga um comentário de um Favorito '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('bookmarks')
    def get(self, registry_id):
        user = self.get_current_user()
        bookmark_id = self.get_argument("id","")
        owner = self.get_argument("owner","")
        data_cri = self.get_argument("data_cri","")
        
        if isAllowedToDeleteComment(user, registry_id, owner):
            self._bookmark = model.Bookmarks().retrieve(bookmark_id)
            if self._bookmark:
                if self._bookmark.deleteBookmarkComment(owner, data_cri):
                    log.model.log(user, u'removeu um comentário do link favorito de', objeto=registry_id, tipo="bookmarks")
                    self.redirect("/bookmarks/comment/%s?id=%s" % (registry_id, bookmark_id))
                else:
                    raise HTTPError(404)
            else:
                raise HTTPError(404)
        else:
            raise HTTPError(403)

class BookmarkUrlHandler(BaseHandler):
    ''' Lista um favorito por URL '''
    
    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        url = self.get_argument("url","")
        page = int(self.get_argument("page","1"))

        bookm_count = model.Bookmarks.countBookmarksByUrl(url)
        bookmarks = model.Bookmarks.searchBookmarksByUrl(user, page, NUM_MAX_FAVORITOS, url)
        tags_list = model.Bookmarks.listAllTags(user)

        self.render("modules/bookmarks/bookmarks-list.html", NOMEPAG='favoritos', \
                    REGISTRY_ID=user, CRIAR=False, \
                    TAG=None, LINKS=[], \
                    TAGS=tags_list, \
                    FOTO=True, \
                    BOOKMARKS=bookmarks, BOOKM_COUNT=bookm_count, \
                    PAGE=page, PAGESIZE=NUM_MAX_FAVORITOS, \
                    TITLE=u"Usuários que marcaram %s"%url, \
                    MSG="")

                            
URL_TO_PAGETITLE.update ({
        "bookmarks":   "Favoritos"
    })

HANDLERS.extend([
            (r"/bookmarks/new/%s" % (NOMEUSERS),                BookmarkNewHandler),
            (r"/bookmarks/popup/%s" % (NOMEUSERS),              BookmarkNewPopUpHandler),            
            (r"/bookmarks/url",                                 BookmarkUrlHandler),                   # ?url=<url>
            (r"/bookmarks/comment/%s" % (NOMEUSERS),            BookmarkCommentHandler),               # ?id=<bookmark_id>
            (r"/bookmarks/comment/%s/delete" % (NOMEUSERS),     BookmarkDeleteCommentHandler),
            (r"/bookmarks/delete/%s" % (NOMEUSERS),             BookmarkDeleteHandler),                 # ?id=<bookmark_id>
            (r"/bookmarks/edit/%s" % (NOMEUSERS),               BookmarkEditHandler),                   # ?id=<bookmark_id>
            (r"/bookmarks/%s" % (NOMEUSERS),                    BookmarkListHandler),
            (r"/bookmarks/%s/%s" % (NOMEUSERS, PAGENAMECHARS),  BookmarkUserTagHandler)
    ])
