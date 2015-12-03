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

import re
import time
from datetime import datetime
from uuid import uuid4
from urllib import quote,unquote
import operator
from operator import itemgetter

import tornado.web
from tornado.web import HTTPError
import tornado.template

from core.dispatcher import BaseHandler, HANDLERS, URL_TO_PAGETITLE, \
                            NOMEUSERS, \
                            FILENAMECHARS, PAGENAMECHARS, \
                            sortedKeys
import model
import core.model
from core.model import isUserOrOwner, isFriendOrMember, isUserOrMember, isAUser, isOwner
import bookmarks.model
from config import PLATAFORMA_URL
import core.database
import log.model
from search.model import addTag, removeTag, splitTags
from libs.notify import Notify
from libs.dateformat import full_week_date, short_datetime, _meses
from libs.strformat import remove_diacritics, remove_special_chars
import libs.permissions
from libs.permissions import isAllowedToDeleteObject, isAllowedToComment, isAllowedToDeleteComment, \
                             isAllowedToWriteObject

''' importa definição do tutorial deste módulo, se existir _tutorial.py '''
from config import TUTORIAL
try:
    import _tutorial
except ImportError:
    pass

# Número máximo de posts exibidos na página principal de um blog
NUM_MAX_POSTS = 3

# Número máximo de versões preservadas no History
BLOG_HISTORY_SIZE = 20

# marca de página removida
_CONTEUDO_REMOVIDO = "##@@$$%% REMOVED %%$$@@##"


def prepareBlogPosts(user, posts, include_removed=False):
    for post in posts:
        # permissões para remover e alterar um post
        post["alterar"] = isAllowedToWriteObject(user, "blog", post["registry_id"])
        post["apagar"] = post["alterar"] and isAllowedToDeleteObject(user, post["owner"], post["_id"])
        
        # datas formatadas
        post["data_fmt"] = short_datetime(post["data_cri"])
        if "data_alt" in post and post["data_alt"]:
            post["data_alt"] = short_datetime(post["data_alt"])
        
        post["num_comments"] =  model.Blog().retrieve(post["_id"], include_removed).getNumComments()

    return sorted(posts, key=itemgetter("data_cri"), reverse=True)

        
def prepareBlogPost(user, post_data):
        # acrescenta permissões para comentar um post e datas formatadas
        post_data["comentar"] = isAllowedToComment(user, post_data["_id"], post_data["owner"])
        post_data["data_cri_nofmt"] = post_data["data_cri"]
        post_data["data_cri"] = short_datetime(post_data["data_cri"])
        post_data["data_alt"] = short_datetime(post_data["data_alt"])

        # acrescenta permissões de cada comentário
        for comentario in post_data["comentarios"]:
            comentario["comment"] = comentario["comment"].replace("\r\n", "<br/>")
            comentario["apagar"] = isAllowedToDeleteComment(user, post_data["registry_id"], comentario["owner"])
            comentario["data_fmt"] = short_datetime(comentario["data_cri"])

        post_data["comentarios"] = sorted(post_data["comentarios"], key=itemgetter("data_cri"), reverse=True)
        return post_data
    
    
class BlogHandler(BaseHandler):
    ''' Lista o Blog de um usuario ou comunidade '''

    @core.model.allowedToAccess
    @core.model.serviceEnabled('blog')
    @libs.permissions.canReadService ("blog")   
    def get (self, registry_id):
        user = self.get_current_user()
        page = int(self.get_argument("page","1"))
         
        posts_count = model.Blog.countPostsByRegistryId(registry_id)
        lista_posts = prepareBlogPosts(user, model.Blog.listBlogPosts(registry_id, page, NUM_MAX_POSTS))

        links = []            
        if isAllowedToWriteObject(user, "blog", registry_id):
            links.append(("Novo post", "/static/imagens/icones/new32.png", "/blog/new/"+registry_id))
        if isUserOrOwner(user, registry_id):
            links.append((u"Ver lixeira", "/static/imagens/icones/recycle32.png", "/blog/deleted/"+registry_id))
            links.append((u"Alterar permissões deste blog", "/static/imagens/icones/permissions32.png", "/permission/blog/"+registry_id, "", "", True))   
         
        log.model.log(user, u'acessou o blog de', objeto=registry_id, tipo="blog", news=False)
                 
        self.render("modules/blog/blog.html", NOMEPAG="blog", REGISTRY_ID=registry_id, \
                                              ARCHIVE=model.Blog.get_blog_archive(registry_id), \
                                              SORTEDKEYS=sortedKeys, MESES=_meses, \
                                              POSTS=lista_posts, POSTS_COUNT=posts_count, \
                                              PAGE=page, PAGESIZE=NUM_MAX_POSTS, \
                                              LINKS=links)


class PostHandler(BaseHandler):
    ''' Lista um Post de um Blog de um usuario ou comunidade '''
      
    @core.model.allowedToAccess
    @core.model.serviceEnabled('blog')
    @libs.permissions.canReadService ("blog") 
    def get (self, registry_id, post_id):
        user = self.get_current_user()
        doc_id = "/".join([registry_id, post_id])
        versao = self.get_argument("versao","-1")
        
        self._blog = model.Blog().retrieve(doc_id, include_removed=True)
                
        if self._blog:
            post_data = prepareBlogPost(user, self._blog.getBlogPost(user, versao=int(versao)))
            
            links = []
            links.append(("Blog de "+registry_id, "/static/imagens/icones/back32.png", "/blog/"+registry_id))
            
            if user:
                reg = core.model.Registry().retrieve(user)
                if reg and "bookmarks"  in reg.getServices:                              
                    links.append(bookmarks.model.Bookmarks.createBookmarkLink(user, "http://"+PLATAFORMA_URL+self.request.path))            
                if isAllowedToWriteObject(user, "blog", registry_id):
                    links.append(("Alterar este post", "/static/imagens/icones/edit32.png", "/blog/edit/"+doc_id))
                if isUserOrOwner(user, registry_id):
                    links.append(("Ver histórico de versões", "/static/imagens/icones/versions32.png", "/blog/history/"+doc_id))
                    
                if isAllowedToDeleteObject(user, post_data["owner"], doc_id) and versao == "-1":
                    links.append(("Remover este post", "/static/imagens/icones/delete32.png", "/blog/delete/"+doc_id,
                                  "return confirm('Deseja realmente remover este Post?');"))

            log.model.log(user, u'acessou o post', objeto=post_id, tipo="blog", news=False)

            self.render("modules/blog/post.html", NOMEPAG="blog", POST_DATE=full_week_date(post_data["data_cri_nofmt"]), \
                        REGISTRY_ID=registry_id, \
                        ARCHIVE=model.Blog.get_blog_archive(registry_id), \
                        SORTEDKEYS=sortedKeys, MESES=_meses, \
                        POST=post_data, \
                        LINKS=links)
        else:
            raise HTTPError(404)


class NewPostHandler(BaseHandler):
    ''' Inclusão de um post '''

    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('blog')
    @libs.permissions.canWriteService ("blog")
    def get (self, registry_id):
        user = self.get_current_user()
        self.render("modules/blog/blog-form.html",  NOMEPAG="blog", BLOGDATA=model.Blog(), REGISTRY_ID=registry_id, MSG="")  

    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('blog')
    @libs.permissions.canWriteService ("blog")
    def post(self, registry_id):
        user = self.get_current_user()
        self._blog = model.Blog()
        msg = ""
        
        self._blog.titulo = self.get_argument("titulo","")
        if self._blog.titulo == "":
            msg += u"O título do Post não pode ser vazio.<br/>"
        else:
            self._blog.post_id = remove_special_chars(remove_diacritics(self._blog.titulo.replace(" ","_")))
            if self._blog.post_id == "":
                msg += u"Título do Post inválido<br/>"
                
        self._blog.tags = splitTags(self.get_argument("tags",""))
        
        self._blog.conteudo = self.get_argument("conteudo","")
        if self._blog.conteudo == "":
            msg += u"O conteúdo do Post não pode ser vazio.<br/>"
        
        if msg:
            self.render("modules/blog/blog-form.html", NOMEPAG="blog", REGISTRY_ID=registry_id, BLOGDATA=self._blog, MSG=msg)
            return
                
        else:
            self._blog.data_cri = str(datetime.now())
            self._blog.data_alt = self._blog.data_cri

            # A chave _id do documento no couchdb é nome/pagina
            doc_id = '/'.join([registry_id,self._blog.post_id])

            self._blog.registry_id = registry_id
            self._blog.owner = user
            
            historico_inicial = dict()
            historico_inicial["data_alt"] = self._blog.data_alt
            historico_inicial["alterado_por"] = user
            historico_inicial["conteudo"] = self._blog.conteudo
            
            self._blog.historico.append(historico_inicial)
            
            try:
                self._blog.save(id=doc_id)
            except Exception as detail:
                self.render("modules/blog/blog-form.html", NOMEPAG="blog", REGISTRY_ID=registry_id, BLOGDATA=self._blog, \
                            MSG=u"Já existe um post com este título.")
                return
            
            data_tag = str(datetime.now())
            for tag in self._blog.tags:
                addTag(tag, registry_id, user, "blog", doc_id, self._blog.titulo, data_tag)

            log.model.log(user, u'escreveu no blog', objeto=doc_id, tipo="blog")
            self.redirect("/blog/%s" % doc_id)



class CommentPostHandler(BaseHandler):
    ''' Inclusão de um comentário de um post '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('blog')
    def post(self, registry_id, post_id):
        user = self.get_current_user()
        doc_id = "/".join([registry_id, post_id])
        self._blog = model.Blog().retrieve(doc_id)
        
        if self._blog:
            if isAllowedToComment(user, doc_id, self._blog.owner):
                comment_data = self._blog.addComment(user, str(datetime.now()), self.get_argument("comment",""))
                if comment_data:
                    # notifica o dono do post comentado
                    email_msg = "Post: "+self._blog.titulo+"\n"+\
                                comment_data["comment"]+"\n"+\
                                Notify.assinatura(user, registry_id, comment_data["data_cri"])+"\n\n"
                    Notify.email_notify(self._blog.owner, user, "comentou seu post no Blog", \
                                   message=email_msg, \
                                   link="blog/"+doc_id)
                    
                    log.model.log(user, u'comentou no blog', objeto=doc_id, tipo="blog")
                    self.redirect("/blog/%s" % doc_id)
                
                else:
                    self.render("home.html", MSG=u"O comentário não pode ser vazio.", REGISTRY_ID=registry_id, NOMEPAG="blog")
            else:
                self.render("home.html", MSG=u"Somente amigos de um usuário ou membros de uma comunidade podem comentar.", REGISTRY_ID=registry_id, NOMEPAG="blog")

        else:
            raise HTTPError(404)
            

class EditPostHandler(BaseHandler):
    ''' Edição de post de um Blog '''

    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('blog')
    @libs.permissions.canWriteService ("blog")
    def get (self, registry_id, post_id):
        user = self.get_current_user()
        doc_id = '/'.join([registry_id, post_id])
        self._blog = model.Blog().retrieve(doc_id)
        if self._blog:
            self.render("modules/blog/blog-edit.html", NOMEPAG="blog", BLOGDATA=self._blog, REGISTRY_ID=registry_id, MSG="")
        else:
            raise HTTPError(404)

    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('blog')
    @libs.permissions.canWriteService ("blog")
    def post(self, registry_id, post_id):
        user = self.get_current_user()
        doc_id = '/'.join([registry_id, post_id])
        self._blog = model.Blog().retrieve(doc_id)
        if self._blog:
            msg = ""
            self._blog.titulo = self.get_argument("titulo","")
            if self._blog.titulo == "":
                msg += u"O título do Post não pode ser vazio.<br/>"
                            
            old_tags = self._blog.tags
            self._blog.tags = splitTags(self.get_argument("tags",""))
            
            self._blog.conteudo = self.get_argument("conteudo","")
            if self._blog.conteudo == "":
                msg += u"O conteúdo do Post não pode ser vazio.<br/>"
            
            if msg:
                self.render("modules/blog/blog-form.html", NOMEPAG="blog", REGISTRY_ID=registry_id, BLOGDATA=self._blog, MSG=msg)
                return
                    
            else:
                data_tag = str(datetime.now())
                for tag in self._blog.tags:
                    if tag not in old_tags:
                        addTag(tag, registry_id, user, "blog", doc_id, self._blog.titulo, data_tag)

                for tag in old_tags:
                    if tag not in self._blog.tags:
                        removeTag(remove_diacritics(tag.lower()), "blog", doc_id)
                
                # registro da atualização
                self._blog.data_alt = str(datetime.now())
                self._blog.alterado_por = user
            
                historico_inicial = dict()
                historico_inicial["data_alt"] = self._blog.data_alt
                historico_inicial["alterado_por"] = user
                historico_inicial["conteudo"] = self._blog.conteudo
                self._blog.historico.append(historico_inicial)

                # limita o número de versões no histórico em BLOG_HISTORY_SIZE
                history_len = len(self._blog.historico)
                if history_len > BLOG_HISTORY_SIZE:
                    inicio = history_len - BLOG_HISTORY_SIZE
                    self._blog.historico = self._blog.historico[inicio:history_len]

                self._blog.save()
                
                log.model.log(user, u'alterou o blog', objeto=doc_id, tipo="blog")    
                self.redirect("/blog/%s" % doc_id)       
                         
        else:
            self.render("home.html", MSG=u"Post não encontrado: ele pode ter sido removido por outro usuário enquanto você editava-o", REGISTRY_ID=registry_id, NOMEPAG="blog")
            return



class DeletePostHandler(BaseHandler):
    ''' Apaga um Post do Blog '''

    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('blog')
    @core.model.userOrMember 
    def get(self, registry_id, post_id):
        user = self.get_current_user()
        doc_id = '/'.join([registry_id,post_id])
        self._blog = model.Blog().retrieve(doc_id)
        if self._blog:
            if isAllowedToDeleteObject(user, self._blog.owner, doc_id):
                try:
                    tags = self._blog.tags
                    self._blog.deletePost(user)
                    #for tag in tags:
                    #    removeTag(remove_diacritics(tag.lower()), "blog", doc_id)
                                                
                except Exception as detail:
                    self.render("home.html", MSG=u"Erro: %s" % detail, REGISTRY_ID=registry_id, NOMEPAG="blog")
                    return
                                                    
                log.model.log(user, u'removeu o post', objeto=doc_id, tipo="none")     
                self.redirect("/blog/%s" %registry_id)
                
            else:
                raise HTTPError(403)
                
        else:
            raise HTTPError(404)


class DeleteCommentHandler(BaseHandler):
    ''' Apaga um comentário de um Post do Blog '''

    @tornado.web.authenticated
    # esses decorators não funcionam aqui pois o método get não recebe registry_id como parâmetro.
    #@core.model.allowedToAccess
    #@core.model.serviceEnabled('blog')
    
    def get(self):
        user = self.get_current_user()
        comment_id = self.get_argument("id","")
        self._comment = model.BlogComment().retrieve(comment_id)
        if self._comment:
        
            if isAllowedToDeleteComment(user, self._comment.registry_id, self._comment.owner):
                
                doc_id = '/'.join([self._comment.registry_id, self._comment.post_id])
                
                # remove o comentário
                try:
                    self._comment.delete()
                except Exception as detail:
                    self.render("home.html", MSG=u"Erro: %s" % detail, REGISTRY_ID=registry_id, NOMEPAG="blog")
                    return
                    
                log.model.log(user, u'removeu um comentário do blog', objeto=doc_id, tipo="none")
                self.redirect("/blog/%s#comment" %doc_id)
                
            else:
                raise HTTPError(403)
                
        else:
            raise HTTPError(404)

class ShowBlogHistoryHandler(BaseHandler):
    ''' mostra histórico de atualizações de um post do blog '''
    
    @tornado.web.authenticated
    @core.model.serviceEnabled('blog')
    @core.model.userOrOwner
    def get(self, registry_id, post_id):
        user = self.get_current_user()
        doc_id = '/'.join([registry_id, post_id])
        self._blog = model.Blog().retrieve(doc_id, include_removed=True)
        if self._blog: 
            blog_data = self._blog.getBlogHistory()
            
            log.model.log(user, u'acessou o histórico do post', objeto=doc_id, tipo="blog", news=False)
            self.render("modules/blog/blog_historico.html", BLOGDATA=blog_data, POST_ID=post_id, \
                        ARCHIVE=model.Blog.get_blog_archive(registry_id), \
                        SORTEDKEYS=sortedKeys, MESES=_meses, \
                        NOMEPAG='blog', REGISTRY_ID=registry_id, MSG="")
        else:
            raise HTTPError(404)
            
            
class RestoreBlogHandler(BaseHandler):
    ''' restaura uma versão anterior de um post do blog '''
    
    @tornado.web.authenticated
    @core.model.serviceEnabled('blog')
    @core.model.userOrOwner
    def get(self, registry_id, post_id):
        user = self.get_current_user()
        versao = self.get_argument("versao","-1")

        doc_id = '/'.join([registry_id, post_id])
        self._blog = model.Blog().retrieve(doc_id, include_removed=True)
        if self._blog: 
            self._blog.restoreVersion(int(versao))
            
            # notifica o dono da página restaurada
            email_msg = u"Post restaurado: "+doc_id+"\n"+\
                        u"Versão: " + versao + "\n" +\
                        Notify.assinatura(user, registry_id, self._blog.historico[-1]["data_alt"])+"\n\n"
            Notify.email_notify(self._blog.owner, user, u"restaurou uma versão de um post criado por você", \
                           message=email_msg, \
                           link="/blog/%s/%s"%(registry_id, post_id))
            
            log.model.log(user, u'restaurou o post', objeto=doc_id, tipo="blog")
            
        self.redirect("/blog/history/%s/%s"%(registry_id,post_id))


class ListDeletedPostsHandler(BaseHandler):
    ''' Lista páginas Blog apagadas de um usuário ou comunidade '''

    @tornado.web.authenticated
    @core.model.serviceEnabled('blog')
    @core.model.userOrOwner
    def get(self, registry_id):
        user = self.get_current_user()
        page = int(self.get_argument("page","1"))
        
        lista_posts = prepareBlogPosts(user, model.Blog.listBlogPosts(registry_id, page, NUM_MAX_POSTS, control_panel=False, only_removed=True), include_removed=True)
        page_count = model.Blog.countRemovedPosts(registry_id)
        
        links = []
        if isUserOrOwner(user, registry_id):
            links.append((u"Listar posts", "/static/imagens/icones/blog32.png", "/blog/"+registry_id))
    
        log.model.log(user, u'acessou a lixeira do blog de', objeto=registry_id, tipo="blog", news=False)
        self.render("modules/blog/blog-listaremovidas.html", NOMEPAG='blog', \
                    REGISTRY_ID=registry_id, \
                    LINKS=links, \
                    LISTA_POSTS=lista_posts, PAG_COUNT=page_count, \
                    PAGE=page, PAGESIZE=NUM_MAX_POSTS, \
                    MSG="")
        

class BlogPermanentlyRemoveHandler(BaseHandler):
    ''' remove um post definitivamente da lixeira '''
    
    @tornado.web.authenticated
    @core.model.serviceEnabled('blog')
    @core.model.userOrOwner
    def get(self, registry_id, post_id):
        user = self.get_current_user()
        
        doc_id = '/'.join([registry_id, post_id])
        self._blog = model.Blog().retrieve(doc_id, include_removed=True)
        if self._blog:
            # salva variáveis para poder ter acesso a elas depois de remover do banco
            owner = self._blog.owner
            
            # se é uma página e está na lixeira, remove-a
            if self._blog.historico[-1]["conteudo"] == _CONTEUDO_REMOVIDO:
                self._blog.deletePost(user, permanently=True)
                
                # notifica o dono da página excluída
                email_msg = u"Post removido da lixeira: "+doc_id+"\n"+\
                            Notify.assinatura(user, registry_id, str(datetime.now()))+"\n\n"
                Notify.email_notify(owner, user, u"removeu um post seu da lixeira", \
                               message=email_msg, \
                               link="blog/"+registry_id)

                log.model.log(user, u'removeu da lixeira o post', objeto=doc_id, tipo="none")
                
            self.redirect("/blog/deleted/%s" % registry_id )
        else:
            raise HTTPError(404)


URL_TO_PAGETITLE.update ({
        "blog": "Blog"
    })

HANDLERS.extend([
            (r"/blog/new/%s"                % (NOMEUSERS),                          NewPostHandler),
            (r"/blog/edit/%s/%s"            % (NOMEUSERS, PAGENAMECHARS),           EditPostHandler),
            (r"/blog/deleted/%s"            % (NOMEUSERS),                          ListDeletedPostsHandler),
            (r"/blog/delete/%s/%s"          % (NOMEUSERS, PAGENAMECHARS),           DeletePostHandler),
            (r"/blog/comment/%s/%s"         % (NOMEUSERS, PAGENAMECHARS),           CommentPostHandler),
            (r"/blog/comment/delete",                                               DeleteCommentHandler),
            (r"/blog/%s"                    % (NOMEUSERS),                          BlogHandler),
            (r"/blog/%s/%s"                 % (NOMEUSERS, PAGENAMECHARS),           PostHandler),
            (r"/blog/history/%s/%s"         % (NOMEUSERS, PAGENAMECHARS),           ShowBlogHistoryHandler),
            (r"/blog/restore/%s/%s"         % (NOMEUSERS, PAGENAMECHARS),           RestoreBlogHandler),
            (r"/blog/remove/%s/%s"          % (NOMEUSERS, PAGENAMECHARS),           BlogPermanentlyRemoveHandler),
    ])
