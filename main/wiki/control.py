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

import operator
from operator import itemgetter
from uuid import uuid4
from urllib import quote,unquote
import time
from datetime import datetime
import re

import tornado.web
from tornado.web import HTTPError
import tornado.template

import model
import database
from database import _CONTEUDO_REMOVIDO
import core.model
from core.model import isOwner, isUserOrMember, isUserOrOwner, isAUser, getType, isFriend, isOnline
from core.database import DB_VERSAO_010
import log.model
import chat.model
from search.model import addTag, removeTag, splitTags
import permission.model
import bookmarks.model
from config import PLATAFORMA_URL
from core.dispatcher import BaseHandler, HANDLERS, URL_TO_PAGETITLE, \
                            NOMEUSERS, \
                            FILENAMECHARS, PAGENAMECHARS
                            
from libs.dateformat import short_datetime
from libs.strformat import remove_diacritics, remove_special_chars
from libs.notify import Notify
import libs.permissions
from libs.permissions import isAllowedToDeleteObject, isAllowedToComment, isAllowedToDeleteComment, \
                             isAllowedToReadObject, isAllowedToWriteObject, objectOwnerFromService

''' importa definição do tutorial deste módulo, se existir _tutorial.py '''
from config import TUTORIAL
try:
    import _tutorial
except ImportError:
    pass

_revision = ""

# Número máximo de itens exibidos na lista de páginas de um usuário
NUM_MAX_WIKIPAGES = 10

# Número máximo de itens exibidos no portfolio de páginas de um usuário
NUM_MAX_PORTFOLIOPAGES = 10

# Número máximo de páginas preservadas no History
WIKI_HISTORY_SIZE = 20

def prepareFolderPages(user, paginas, registry_type, privacidade, user_or_owner):
    # chamadas:
    # only_removed = False
    # /wiki/%s -> lista pastas e páginas não removidas do registry_id
    # only_removed = True
    # /wiki/deleted/%s -> lista todas as páginas removidas
    
    sel_multipla = False
    for pagina in paginas:
        pagina["data_nofmt"] = pagina["data_alt"]
        pagina["data_alt"]   = short_datetime(pagina["data_nofmt"], include_year=True)

        pagina["apagar"]     = isAllowedToDeleteObject(user, pagina["owner"], pagina["doc_id"], wiki="S")
        pagina["mudarpermissao"] = pagina["apagar"] or (pagina["nomepag_id"] in ["home", "indice"] and user_or_owner)
        pagina["alterar"]    = isAllowedToWriteObject(user, "wiki", pagina["registry_id"], nomeobj=pagina["nomepag_id"])
        pagina["ler"]        = isAllowedToReadObject(user, "wiki", pagina["registry_id"], nomeobj=pagina["nomepag_id"])

        parent_id = pagina["registry_id"]+"/"+pagina["parent_folder"]
        parent = model.Wiki().retrieve(parent_id)
        # Vc só pode mover um item para uma pasta se:
        #    vc pode apagar o item e o dono da pasta permite que vc crie items nela.
        pagina["mover"] = pagina["apagar"]
        if parent:
            pagina["mover"] = pagina["mover"] and isAllowedToWriteObject(user, "wiki", pagina["registry_id"], pagina["parent_folder"])
          
        # se houver pelo menos um checkbox, ativa seleção múltipla
        if  pagina["alterar"] and pagina["mover"] and pagina["nomepag_id"] not in ["home", "indice"]:
            sel_multipla = True

        # obtem permissões da página
        _perm = permission.model.Permission().retrieve("wiki/"+pagina["doc_id"])
        if _perm:
            pagina["escrita"] = _perm.escrita
            pagina["leitura"] = _perm.leitura
        else:
            pagina["escrita"] = permission.model.default_permission("W", "wiki", registry_type, privacidade)
            pagina["leitura"] = permission.model.default_permission("R", "wiki", registry_type, privacidade)   
   
                                                      
    #paginas = sorted(paginas, key=itemgetter("data_nofmt"), reverse = True)
    return (sel_multipla, paginas)


def prepareWikiPage(user, pagina):
    # acrescenta permissões para o usuário user e datas formatadas
    pagina["apagar"]       = isAllowedToDeleteObject(user, pagina["owner"], pagina["pag"], wiki="S")
    pagina["alterar"]      = isAllowedToWriteObject(user, "wiki", pagina["registry_id"], nomeobj=pagina["nomepag_id"])
    pagina["ler"]          = isAllowedToReadObject(user, "wiki", pagina["registry_id"], nomeobj=pagina["nomepag_id"])
    pagina["data_cri_fmt"] = short_datetime(pagina["data_cri"])
    pagina["data_alt_fmt"] = short_datetime(pagina["data_alt"])
    pagina["comentar"]     = isAllowedToComment(user, pagina["pag"], pagina["owner"])

    for comentario in pagina["comentarios"]:
        comentario["comment"] = comentario["comment"].replace("\r\n", "<br/>")
        comentario["apagar"]   = isAllowedToDeleteComment(user, pagina["registry_id"], comentario["owner"])
        comentario["data_fmt"] = short_datetime(comentario["data_cri"])
    return pagina
    
    
class WikiHandler(BaseHandler):
    ''' Lista conteúdo de uma pasta Wiki de um usuário ou comunidade '''

    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('wiki')
    def get (self, registry_id):
        user = self.get_current_user()
        folder = self.get_argument("folder","")
        page = int(self.get_argument("page","1"))
        paginas = []
        (registry_type, privacidade) = getType(registry_id)
        
        # se não estou vendo a pasta raiz...
        if folder:
            folder_id = registry_id+"/"+folder

            self._wiki = model.Wiki().retrieve(folder_id)
            
            if self._wiki and self._wiki.is_folder=="S":
                path = self._wiki.getPagePath()
                pag_count = self._wiki.countFolderPages()
                
                # inclui referência .. para subir na árvore
                paginas.append(self._wiki)
                nomefolder = paginas[0]["nomepag"]
                paginas[0]["nomepag"]      = ".."
                #paginas[0]["owner"]        = self._wiki.owner
                paginas[0]["owner"]        = ""
                paginas[0]["nomepag_id"]   = paginas[0]["parent_folder"]
                paginas[0]["apagar"]       = False
                paginas[0]["mudarpermissao"] = False
                
                paginas[0]["alterar"]      = False
                paginas[0]["data_alt"]     = ""
                paginas[0]["data_nofmt"]   = ""
                paginas[0]["alterado_por"] = ""
                paginas[0]["registry_id"]  = registry_id
                paginas[0]["mover"]        = False
                paginas[0]["escrita"] = permission.model.default_permission("W", "wiki", registry_type, privacidade)
                paginas[0]["leitura"] = permission.model.default_permission("R", "wiki", registry_type, privacidade)
            
                if not isAllowedToReadObject(user, "wiki", registry_id, folder):
                    raise HTTPError(403)
                    return
                
            else:
                raise HTTPError(404)
                return
        else:
            path = "/"+registry_id+"/"
            pag_count = model.Wiki.countRootFolderPages(registry_id)

        user_or_owner = isUserOrOwner(user, registry_id)
        (sel_multipla, pags) = prepareFolderPages(user, model.Wiki.listFolderPages(user, registry_id, folder, page, NUM_MAX_WIKIPAGES), registry_type, privacidade, user_or_owner)
        paginas.extend(pags)
        
        links = []
        if user_or_owner:
            links.append((u"Ver lixeira", "/static/imagens/icones/recycle32.png", "/wiki/deleted/"+registry_id))
        if folder and (user_or_owner or user == objectOwnerFromService("wiki", registry_id, folder)):
            links.append((u"Alterar permissões desta pasta", "/static/imagens/icones/permissions32.png", "/permission/wiki/"+folder_id, "", "", True))
            
        if isUserOrMember(user, registry_id):
            if not folder or isAllowedToWriteObject(user, "wiki", registry_id, folder):
                links.append((u"Criar nova pasta", "/static/imagens/icones/add_folder32.png", "/wiki/newfolder/"+registry_id+"?folder="+folder))
                links.append((u"Criar nova página", "/static/imagens/icones/new32.png", "/wiki/newpage/"+registry_id+"?folder="+folder))
                
            links.append((u"Exportar portfólio", "/static/imagens/icones/export32.png", "/wiki/portfolio/"+registry_id))

        log.model.log(user, u'listou as páginas de', objeto=registry_id, tipo="wiki", news=False)
        self.render("modules/wiki/wiki-listapaginas.html", NOMEPAG=u'páginas', \
                    REGISTRY_ID=registry_id, \
                    FOLDER= folder, PATH=path, \
                    LINKS=links, \
                    PAGINAS=paginas, PAG_COUNT=pag_count, \
                    PAGE=page, PAGESIZE=NUM_MAX_WIKIPAGES, \
                    PERM=permission.model.service_permissions ("wiki", registry_type), \
                    SEL_MULTIPLA=sel_multipla, MSG="")


class WikiNewPageHandler(BaseHandler):
    ''' Inclusão de nova página '''

    @tornado.web.authenticated
    @core.model.serviceEnabled('wiki')
    @core.model.userOrMember
    def get (self, registry_id):
        user = self.get_current_user()
        folder = self.get_argument("folder","")
        if folder:
            if not isAllowedToWriteObject(user, "wiki", registry_id, folder):
                raise HTTPError(403)
                return

            folder_id = registry_id+"/"+folder
            self._pai = model.Wiki().retrieve(folder_id)
            if self._pai:
                parent_name = self._pai.nomepag
                
            else:
                raise HTTPError(404)
                return
                

        else:
            parent_name = registry_id+"/"
        
        self._wiki = model.Wiki(parent_folder=folder)
        (registry_type, privacidade) = getType(registry_id)
        self.render("modules/wiki/wiki-form.html", NOMEPAG=u'páginas', \
                    PARENT_NAME=parent_name, \
                    DEFAULT_PERM = permission.model.default_all_permissions("wiki", registry_type, privacidade), \
                    WIKIDATA=self._wiki, REGISTRY_ID=registry_id, MSG="")
        
    @tornado.web.authenticated
    @core.model.serviceEnabled('wiki')
    @core.model.userOrMember
    def post(self, registry_id):
        msg = ""
        user = self.get_current_user()
        folder = self.get_argument("parent_folder","")
        if folder:
            folder_id = registry_id+"/"+folder
            self._pai = model.Wiki().retrieve(folder_id)
            if self._pai:
                parent_name = self._pai.nomepag
                
            else:
                raise HTTPError(404)
                return
        else:
            parent_name = registry_id+"/"
            
        nomepag = self.get_argument("nomepag","")
        if nomepag=="":
            msg += u"* Nome da página não preenchido<br/>"

        nomepag_id = remove_special_chars(remove_diacritics(nomepag.replace(" ","_")))
        if nomepag_id=="":
            msg += u"* Nome da página inválido<br/>"

        doc_id = '/'.join([registry_id,nomepag_id])
        if model.Wiki.nomepagExists(registry_id, nomepag) or model.Wiki().retrieve(doc_id):
            msg += u"* Já existe uma página ou pasta com este nome<br/>"
        
        self._wiki = model.Wiki()
        conteudo = self.get_argument("conteudo","")
        if conteudo=="": msg += u"* Conteúdo não preenchido<br/>"
        
        historico = dict(
                         conteudo=conteudo,
                         data_alt=str(datetime.now()),
                         alterado_por = user
        )
        self._wiki.historico.append(historico)
        self._wiki.tags = splitTags(self.get_argument("tags",""))
        self._wiki.parent_folder = self.get_argument("parent_folder","")
        if self._wiki.parent_folder!="":
            parent_id = '/'.join([registry_id,self._wiki.parent_folder])
            test_parent_folder = model.Wiki().retrieve(parent_id)
            if not test_parent_folder:
                msg += u"* Impossível criar página dentro de uma pasta inexistente (%s)<br/>" % parent_id
            elif not isAllowedToWriteObject(user, "wiki", registry_id, self._wiki.parent_folder):
                msg += u"* Você não tem permissão para criar páginas nesta pasta."

        if msg:
            (registry_type, privacidade) = getType(registry_id)
            self.render("modules/wiki/wiki-form.html", NOMEPAG=u'páginas', \
                    PARENT_NAME=parent_name, \
                    DEFAULT_PERM = permission.model.default_all_permissions("wiki", registry_type, privacidade), \
                    REGISTRY_ID=registry_id, WIKIDATA=self._wiki, MSG=msg)
        else:
            self._wiki.nomepag = nomepag
            self._wiki.nomepag_id = nomepag_id
            self._wiki.user = user
            self._wiki.owner = user
            self._wiki.registry_id = registry_id
            self._wiki.data_cri = self._wiki.historico[-1]["data_alt"]

            
            self._wiki.saveWiki(id=doc_id)

            # inclui a página recem criada na lista de filhos do parent_folder
            if self._wiki.parent_folder:
                parent = model.Wiki().retrieve(registry_id+"/"+self._wiki.parent_folder)
                parent.addItemToParent(user, self._wiki.nomepag_id)

            log.model.log(user, u'criou a página', objeto=doc_id, tipo="wiki")
            self.redirect("/wiki/%s" % doc_id)


class EditWikiPageHandler(BaseHandler):
    ''' Edição de página Wiki '''

    @tornado.web.authenticated
    @core.model.serviceEnabled('wiki')
    @libs.permissions.hasWritePermission ('wiki')    
    def get (self, registry_id, pagina):
        user = self.get_current_user()
        doc_id = '/'.join([registry_id, pagina])
        self._wiki = model.Wiki().retrieve(doc_id)
        if self._wiki: 
                _revision = self._wiki.rev
                
                conteudo = self._wiki.historico[-1]["conteudo"]
                self.render("modules/wiki/wiki-edit.html", NOMEPAG=u'páginas', \
                            REGISTRY_ID=registry_id, WIKIDATA=self._wiki, PAGINA=pagina, \
                            CONTEUDO=conteudo, CONTEUDODB='', TAGSDB=[], \
                            MSG="")
        else:
            raise HTTPError(404)

   
    @tornado.web.authenticated
    @core.model.serviceEnabled('wiki')
    @libs.permissions.hasWritePermission ('wiki')  
    def post(self, registry_id, pagina):
        user = self.get_current_user()
        doc_id = '/'.join([registry_id, pagina])
        self._wiki = model.Wiki().retrieve(doc_id)
        if self._wiki: 
            msg = ""
            conteudo_db = ''
            tags_db = []
            if self._wiki.rev != self.get_argument("revision",""):
                # Document Update Conflict.
                msg += u"Conflito ao salvar o documento. Enquanto você editava-o, ele foi alterado por outro usuário.<br/>"
                msg += u"Compare as duas versões abaixo e refaça as alterações que ainda achar pertinentes.<br/>"
                msg += u"Ao final envie novamente o formulário.<br/>"
                
                # preserva os dados alterados pelo outro usuário
                conteudo_db = self._wiki.historico[-1]["conteudo"]
                tags_db = self._wiki.tags
                
            if self.get_argument("conteudo","") != "" :
                conteudo = self.get_argument("conteudo")
            else:
                msg += u"Conteúdo não preenchido<br/>"
                conteudo = " "
            
            old_tags = self._wiki.tags # preserva tags anteriores
            self._wiki.tags = splitTags(self.get_argument("tags",""))     # suas tags
            
            if msg:
                self.render("modules/wiki/wiki-edit.html", NOMEPAG=u'páginas', \
                            WIKIDATA=self._wiki, PAGINA=pagina, CONTEUDO=conteudo, CONTEUDODB=conteudo_db, TAGSDB=tags_db, \
                            MSG=msg, REGISTRY_ID=registry_id)
            else:
                # registro da atualização
                self._wiki.historico.append(dict(
                                conteudo=conteudo,
                                data_alt = str(datetime.now()),
                                alterado_por = user
                                ))

                # limita o número de versões no histórico em WIKI_HISTORY_SIZE
                history_len = len(self._wiki.historico)
                if history_len > WIKI_HISTORY_SIZE:
                    inicio = history_len - WIKI_HISTORY_SIZE
                    self._wiki.historico = self._wiki.historico[inicio:history_len]
      
                # salva o documento alterado
                self._wiki.saveWiki(old_tags=old_tags)
    
                # notifica o dono da página alterada
                email_msg = u"Página alterada: "+doc_id+"\n"+\
                            Notify.assinatura(user, registry_id, self._wiki.historico[-1]["data_alt"])+"\n\n"
                Notify.email_notify(self._wiki.owner, user, u"alterou uma página criada por você", \
                               message=email_msg, \
                               link="wiki/"+doc_id)
                
                log.model.log(user, u'alterou a página', objeto=doc_id, tipo="wiki")
                self.redirect("/wiki/%s" % doc_id)
            
        else:
            self.render("home.html", MSG=u"Documento não encontrado: provavelmente o mesmo foi removido enquanto você editava-o.", \
                        NOMEPAG=u'páginas', REGISTRY_ID=registry_id)


class PortfolioHandler(BaseHandler):
    ''' Lista do conteudo das paginas Wiki de um registry_id '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('wiki')
    def get (self, registry_id):
        user = self.get_current_user()
        page = int(self.get_argument("page","1"))
        
        paginas = model.Wiki.listPortfolio(user, registry_id, page, NUM_MAX_PORTFOLIOPAGES)
        pag_count = model.Wiki.countPortfolioPages(registry_id)
        
        log.model.log(user, u'acessou o portfolio de', objeto=registry_id, tipo="wiki", news=False)
        self.render("modules/wiki/portfolio.html", \
                    NOMEPAG=u'páginas', REGISTRY_ID=registry_id, \
                    PAGINAS=paginas, PAG_COUNT=pag_count, \
                    PAGE=page, PAGESIZE=NUM_MAX_PORTFOLIOPAGES, \
                    MSG="")


class CommentWikiHandler(BaseHandler):
    ''' Inclusão de um comentário de uma página '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('wiki')
    @core.model.friendOrMember
    def post(self, registry_id, pagina):
        user = self.get_current_user()
        doc_id = "/".join([registry_id, pagina])
        
        self._wiki = model.Wiki().retrieve(doc_id)
        if self._wiki:
            comentario = dict()
            comentario["comment"] = self.get_argument("comment","")
            comentario["owner"] = user
            comentario["data_cri"] = str(datetime.now())
            
            if comentario["comment"]:
                self._wiki.comentarios.append(comentario)
                self._wiki.save()
                
                # notifica o dono do post comentado
                email_msg = u"Página: "+self._wiki.nomepag+"\n"+\
                            comentario["comment"]+"\n"+\
                            Notify.assinatura(user, registry_id, comentario["data_cri"])+"\n\n"
                Notify.email_notify(self._wiki.owner, user, u"comentou sua página", \
                               message=email_msg, \
                               link="wiki/"+doc_id)
                
                log.model.log(user, u'comentou a página', objeto=doc_id, tipo="wiki")
                self.redirect("/wiki/%s" % doc_id)
                
            else:
                self.render("home.html", MSG=u"O comentário não pode ser vazio.", REGISTRY_ID=registry_id, NOMEPAG=u'páginas',)

        else:
            raise HTTPError(404)


class DeleteCommentHandler(BaseHandler):
    ''' Apaga um comentário de uma Página '''

    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('wiki')
    def get(self, registry_id, pagina):
        user = self.get_current_user()
        owner = self.get_argument("owner","")
        data_cri = self.get_argument("data","")
        
        if isAllowedToDeleteComment(user, registry_id, owner):
            doc_id = "/".join([registry_id, pagina])
            self._wiki = model.Wiki().retrieve(doc_id)
            if self._wiki:
                if self._wiki.deleteWikiComment(owner, data_cri):
                    log.model.log(user, u'removeu um comentário da página', objeto=doc_id, tipo="wiki")
                    self.redirect("/wiki/%s#comment" %doc_id)
                else:
                    raise HTTPError(404)
            else:
                raise HTTPError(404)
        else:
            raise HTTPError(403)


class WikiNewFolderHandler(BaseHandler):
    ''' Criação de uma nova pasta '''

    @tornado.web.authenticated
    @core.model.serviceEnabled('wiki')
    @core.model.userOrMember
    def get (self, registry_id):
        user = self.get_current_user()
        parent_folder = self.get_argument("folder","")
        if parent_folder:
            parent_id = registry_id+"/"+parent_folder
            self._pai = model.Wiki().retrieve(parent_id)
            parent_name = self._pai.nomepag
            
            if not isAllowedToWriteObject(user, "wiki", registry_id, parent_folder):
                 raise HTTPError(403)
                 return
        else:
            parent_name = registry_id+"/"
        
        self._wiki = model.Wiki(nomepag="Nova Pasta", nomepag_id="NovaPasta", parent_folder=parent_folder)
        self.render("modules/wiki/newfolder-form.html", NOMEPAG=u'páginas', \
                    PARENT_NAME=parent_name, \
                    WIKIDATA=self._wiki, REGISTRY_ID=registry_id, MSG="")
        
    @tornado.web.authenticated
    @core.model.serviceEnabled('wiki')
    @core.model.userOrMember
    def post(self, registry_id):
        msg = ""
        user = self.get_current_user()

        nomepag = self.get_argument("nomepag","")
        if nomepag=="":
            msg += u"* Nome de pasta não preenchido<br/>"
        elif "/" in nomepag:
            msg += u"* Nome de pasta não pode conter o caractere '/'<br/>"
        elif model.Wiki.nomepagExists(registry_id, nomepag):
            msg += u"* Já existe uma página ou pasta com este nome<br/>"

        self._wiki = model.Wiki(nomepag=nomepag)
        self._wiki.is_folder = "S"
        parent_folder = self.get_argument("parent_folder","")
        if parent_folder!="":
            parent_id = '/'.join([registry_id,parent_folder])
            test_parent_folder = model.Wiki().retrieve(parent_id)
            if not test_parent_folder:
                msg += u"* Impossível criar pasta em baixo de uma pasta inexistente (%s)<br/>" % parent_id
            elif not isAllowedToWriteObject(user, "wiki", registry_id, parent_folder):
                msg += u"* Você não tem permissão para criar páginas nesta pasta."

        self._wiki.parent_folder = parent_folder
        #self._wiki.tags = splitTags(self.get_argument("tags",""))
        
        if msg:
            if parent_folder:
                self._pai = model.Wiki().retrieve(registry_id+"/"+parent_folder)
                parent_name = self._pai.nomepag
            else:
                parent_name = registry_id+"/"

            self.render("modules/wiki/newfolder-form.html", NOMEPAG=u'páginas', \
                    PARENT_NAME=parent_name, \
                    REGISTRY_ID=registry_id, WIKIDATA=self._wiki, MSG=msg)
        else:
            nomepag_id = uuid4().hex
            doc_id = '/'.join([registry_id,nomepag_id])
            self._wiki.nomepag = nomepag
            self._wiki.nomepag_id = nomepag_id
            self._wiki.user = user
            self._wiki.owner = user
            self._wiki.registry_id = registry_id
            self._wiki.data_cri = str(datetime.now())
            self._wiki.alterado_por = user
            self._wiki.data_alt = self._wiki.data_cri
            
            self._wiki.saveWiki(id=doc_id)

            # inclui a pasta recem criada na lista de filhos do pai
            if parent_folder:
                parent = model.Wiki().retrieve(registry_id+"/"+parent_folder)
                parent.addItemToParent(user, self._wiki.nomepag_id)
            
            log.model.log(user, u'criou a pasta', objeto=registry_id+"/"+self._wiki.nomepag, link="/wiki/%s?folder=%s"%(registry_id,nomepag_id), tipo="wiki")
            self.redirect("/wiki/%s?folder=%s" % (registry_id, parent_folder))


class WikiDeleteHandler(BaseHandler):
    ''' Apaga uma página ou pasta Wiki '''

    @tornado.web.authenticated
    @core.model.serviceEnabled('wiki')
    @core.model.userOrMember 
    def get(self, registry_id, pagina):
        user = self.get_current_user()
        if pagina in ["home", "indice"]:
           self.render("home.html", MSG=u"Esta página não pode ser removida.", \
                       NOMEPAG=u'páginas', REGISTRY_ID=registry_id)
        else:
            doc_id = '/'.join([registry_id, pagina])
            self._wiki = model.Wiki().retrieve(doc_id)
            if self._wiki:
                # salva variáveis para poder ter acesso a elas depois de remover do banco
                nomepag = self._wiki.nomepag
                owner = self._wiki.owner
                is_folder = self._wiki.is_folder
                
                legenda = "pasta" if self._wiki.is_folder=="S" else u"página"
                if isAllowedToDeleteObject(user, self._wiki.owner, doc_id, wiki="S"):
                    if self._wiki.is_folder=="S" and self._wiki.folder_items!=[]:
                        self.render("home.html", MSG=u"Você não pode apagar uma pasta que não esteja vazia.", \
                                    NOMEPAG=u'páginas', REGISTRY_ID=registry_id)
                        return
                    parent_folder = self._wiki.parent_folder 
                    self._wiki.deleteWiki(user)
                    
                    # notifica o dono da página excluída
                    email_msg = legenda + u" removida: "+doc_id+"\n"+\
                                Notify.assinatura(user, registry_id, str(datetime.now()))+"\n\n"
                    Notify.email_notify(owner, user, u"removeu uma %s criada por você"%legenda, \
                                   message=email_msg, \
                                   link="wiki/"+registry_id)

                    if is_folder=="S":
                        log.model.log(user, u'removeu a pasta', objeto=registry_id+"/"+nomepag, tipo="none")
                    else:
                        log.model.log(user, u'removeu a página', objeto=doc_id, tipo="none")
                        
                    self.redirect("/wiki/%s?folder=%s" % (registry_id, parent_folder) )
                else:
                    raise HTTPError(403)
            else:
                raise HTTPError(404)


class WikiDeleteAllHandler(BaseHandler):
    ''' Apaga várias páginas/pastas Wiki '''

    @tornado.web.authenticated
    @core.model.serviceEnabled('wiki')
    @core.model.userOrMember 
    def post(self, registry_id):
        user = self.get_current_user()
        if "items" not in self.request.arguments:
            msg = u"Página a ser excluída não foi selecionada.<br/>"
            self.render("popup_msg.html", MSG=msg, REGISTRY_ID=registry_id)
            return
        
        items = self.request.arguments["items"] # items é uma lista
        folder = self.get_argument("folder", "")
        
        for item in items:
        
            if item in ["home", "indice"]:
                continue
            doc_id = '/'.join([registry_id, item])
            self._wiki = model.Wiki().retrieve(doc_id)
            if self._wiki:
                # salva variáveis para poder ter acesso a elas depois de remover do banco
                nomepag = self._wiki.nomepag
                owner = self._wiki.owner
                is_folder = self._wiki.is_folder
                
                legenda = "pasta" if self._wiki.is_folder=="S" else u"página"
                if isAllowedToDeleteObject(user, self._wiki.owner, doc_id, wiki="S"):
                    if self._wiki.is_folder=="S" and self._wiki.folder_items!=[]:
                        # Você não pode apagar uma pasta que não esteja vazia.
                        continue
                    parent_folder = self._wiki.parent_folder 
                    self._wiki.deleteWiki(user)
                    
                    # notifica o dono da página excluída
                    email_msg = legenda + u" removida: "+doc_id+"\n"+\
                                Notify.assinatura(user, registry_id, str(datetime.now()))+"\n\n"
                    Notify.email_notify(owner, user, u"removeu uma %s criada por você"%legenda, \
                                   message=email_msg, \
                                   link="wiki/"+registry_id)

                    #log.model.log(user, u'removeu a '+legenda, objeto=doc_id, tipo="none")
                    if is_folder=="S":
                        log.model.log(user, u'removeu a pasta', objeto=registry_id+"/"+nomepag, tipo="none")
                    else:
                        log.model.log(user, u'removeu a página', objeto=doc_id, tipo="none")
        self.redirect("/wiki/%s?folder=%s" % (registry_id, folder) )


class WikiMoveHandler(BaseHandler):
    ''' Move página ou pasta entre pastas Wiki '''

    @tornado.web.authenticated
    @core.model.serviceEnabled('wiki')
    @core.model.userOrMember
    def get (self, registry_id, pagina):
        user = self.get_current_user()
        doc_id = '/'.join([registry_id, pagina])
        self._wiki = model.Wiki().retrieve(doc_id)
        if self._wiki: 
            if isAllowedToWriteObject(user, "wiki", registry_id, pagina):
                self.render("modules/wiki/wiki-move.html", NOMEPAG=u'páginas', \
                            PATH = self._wiki.getPagePath(links=False), \
                            FOLDERS = [f for f in model.Wiki.listWikiFolders(registry_id) if f not in self._wiki.getDescendentsList()], \
                            REGISTRY_ID=registry_id, WIKIDATA=self._wiki, PAGINA=pagina, \
                            MSG="")
            else:
                 raise HTTPError(403)
        else:
            raise HTTPError(404)

   
    @tornado.web.authenticated
    @core.model.serviceEnabled('wiki')
    @core.model.userOrMember
    def post(self, registry_id, pagina):
        user = self.get_current_user()
        doc_id = '/'.join([registry_id, pagina])
        self._wiki = model.Wiki().retrieve(doc_id)
        if self._wiki: 
            legenda = "pasta" if self._wiki.is_folder=="S" else u"página"
            old_parent = self._wiki.parent_folder
            new_parent = self.get_argument("destino","")
            
            if new_parent!="":
                parent_id = '/'.join([registry_id,new_parent])
                test_parent_folder = model.Wiki().retrieve(parent_id)
                if not test_parent_folder:
                    msg = u"Impossível mover objetos para pasta inexistente (%s)<br/>" % test_parent_folder.nomepag
                    self.render("popup_msg.html", MSG=msg, REGISTRY_ID=registry_id)
                    return

                elif not isAllowedToWriteObject(user, "wiki", registry_id, new_parent):
                    msg = u"Você não tem permissão para mover objetos para esta pasta."
                    self.render("popup_msg.html", MSG=msg, REGISTRY_ID=registry_id)
                    return
            old_path = self._wiki.getPagePath(links=False, includefolder=False)
            self._wiki.moveWiki (registry_id, user, old_parent, new_parent)
            new_path = self._wiki.getPagePath(links=False, includefolder=False)
            
            # notifica o dono da página movida
            
            email_msg = legenda + u" movida: "+self._wiki.nomepag+"\n"+\
                        u"De: " + old_path + \
                        " Para: " + new_path + "\n" +\
                        Notify.assinatura(user, registry_id, self._wiki.data_alt if self._wiki.is_folder=="S" else self._wiki.historico[-1]["data_alt"])+"\n\n"
            
            Notify.email_notify(self._wiki.owner, user, u"moveu uma " + legenda + u" criada por você", \
                           message=email_msg, \
                           link="/wiki/%s?folder=%s"%(registry_id, pagina) if legenda=="pasta" else "wiki/"+doc_id)
            
            #log.model.log(user, u'moveu a página', objeto=doc_id, tipo="wiki")
            if self._wiki.is_folder=="S":
                log.model.log(user, u'moveu a pasta', objeto=registry_id+"/"+self._wiki.nomepag, link="/wiki/%s?folder=%s"%(registry_id, pagina), tipo="wiki")
            else:
                log.model.log(user, u'moveu a página', objeto=doc_id, tipo="wiki")
            
            self.render("popup_msg.html", MSG=u"Página/Pasta movida com sucesso.", REGISTRY_ID=registry_id)
        else:
            self.render("popup_msg.html", MSG=u"Documento não encontrado: provavelmente o mesmo foi removido enquanto você editava-o.", \
                        REGISTRY_ID=registry_id)


class WikiMoveAllHandler(BaseHandler):
    ''' Move várias páginas ou pastas entre pastas Wiki '''

    @tornado.web.authenticated
    @core.model.serviceEnabled('wiki')
    @core.model.userOrMember
    def get (self, registry_id):
        user = self.get_current_user()
        folder = self.get_argument("folder","")
        if "items" not in self.request.arguments:
            msg = u"Página a ser movida não foi selecionada.<br/>"
            self.render("popup_msg.html", MSG=msg, REGISTRY_ID=registry_id)
            return
        
        items = self.request.arguments["items"]
        desc_list = []
        for item in items:
            doc_id = '/'.join([registry_id, item])
            self._wiki = model.Wiki().retrieve(doc_id)
            desc = self._wiki.getDescendentsList()
            if desc: 
                desc_list.extend(desc)
        select_folders = [ f for f in model.Wiki.listWikiFolders(registry_id) if f not in desc_list]
        
        if folder:
            doc_id = '/'.join([registry_id, folder])
            self._folder = model.Wiki().retrieve(doc_id)
            if self._folder: 
                self.render("modules/wiki/wiki-move-all.html", NOMEPAG=u'páginas', \
                            PATH=self._folder.getPagePath(links=False), \
                            ITEMS=items, \
                            FOLDER=folder, \
                            FOLDERS=select_folders, \
                            REGISTRY_ID=registry_id, \
                            MSG="")
        else:
            self.render("modules/wiki/wiki-move-all.html", NOMEPAG=u'páginas', \
                        PATH="/%s/"%registry_id, \
                        ITEMS=items, \
                        FOLDER=folder, \
                        FOLDERS=select_folders, \
                        REGISTRY_ID=registry_id, \
                        MSG="")

   
    @tornado.web.authenticated
    @core.model.serviceEnabled('wiki')
    @core.model.userOrMember
    def post(self, registry_id):
        user = self.get_current_user()
        old_parent = self.get_argument("folder","")
        if "items" not in self.request.arguments:
            msg = u"Página a ser movida não foi selecionada.<br/>"
            self.render("popup_msg.html", MSG=msg, REGISTRY_ID=registry_id)
            return
        
        items = self.request.arguments["items"]
        new_parent = self.get_argument("destino","")
            
        if new_parent!="":
            parent_id = '/'.join([registry_id,new_parent])
            test_parent_folder = model.Wiki().retrieve(parent_id)
            if not test_parent_folder:
                msg = u"Impossível mover objetos para pasta inexistente (%s)<br/>" % test_parent_folder.nomepag
                self.render("popup_msg.html", MSG=msg, REGISTRY_ID=registry_id)
                return

            elif not isAllowedToWriteObject(user, "wiki", registry_id, new_parent):
                msg = u"Você não tem permissão para mover objetos para esta pasta."
                self.render("popup_msg.html", MSG=msg, REGISTRY_ID=registry_id)
                return
        
        for item in items:
            doc_id = registry_id+"/"+item
            self._wiki = model.Wiki().retrieve(doc_id)
            
            old_path = self._wiki.getPagePath(links=False, includefolder=False)
            self._wiki.moveWiki (registry_id, user, old_parent, new_parent)
            new_path = self._wiki.getPagePath(links=False, includefolder=False)
            
            legenda = "pasta" if self._wiki.is_folder=="S" else u"página"
            # notifica o dono da página movida
            email_msg = legenda+u" movida: "+self._wiki.nomepag+"\n"+\
                        u"De: " + old_path + " Para: " + new_path + "\n" +\
                        Notify.assinatura(user, registry_id, self._wiki.data_alt if self._wiki.is_folder=="S" else self._wiki.historico[-1]["data_alt"])+"\n\n"
            Notify.email_notify(self._wiki.owner, user, u"moveu uma "+legenda+u" criada por você", \
                           message=email_msg, \
                           link="/wiki/%s?folder=%s"%(registry_id, item) if legenda=="pasta" else "wiki/"+doc_id)
            
            
            #log.model.log(user, u'moveu a '+legenda, objeto=doc_id, tipo="wiki")
            if self._wiki.is_folder=="S":
                log.model.log(user, u'moveu a pasta', objeto=registry_id+"/"+self._wiki.nomepag, link="/wiki/%s?folder=%s"%(registry_id, item), tipo="wiki")
            else:
                log.model.log(user, u'moveu a página', objeto=doc_id, tipo="wiki")
            
            
        self.render("popup_msg.html", MSG=u"Páginas/Pastas movidas com sucesso.", REGISTRY_ID=registry_id)


class FolderRenameHandler(BaseHandler):
    ''' Renomeia pasta da Wiki '''

    @tornado.web.authenticated
    @core.model.serviceEnabled('wiki')
    @libs.permissions.hasWritePermission('wiki')
    def get (self, registry_id, pagina):
        user = self.get_current_user()
        doc_id = '/'.join([registry_id, pagina])
        self._wiki = model.Wiki().retrieve(doc_id)
        if self._wiki: 
            self.render("modules/wiki/wiki-rename.html", NOMEPAG=u'páginas', \
                        PATH = self._wiki.getPagePath(links=False), \
                        NEWNAME = "", \
                        REGISTRY_ID=registry_id, WIKIDATA=self._wiki, PAGINA=pagina, \
                        MSG="")
        else:
            raise HTTPError(404)
            
            
    @tornado.web.authenticated
    @core.model.serviceEnabled('wiki')
    @libs.permissions.hasWritePermission('wiki')
    def post(self, registry_id, pagina):
        user = self.get_current_user()
        doc_id = '/'.join([registry_id, pagina])
        self._wiki = model.Wiki().retrieve(doc_id)
        if self._wiki: 
            old_name = self._wiki.nomepag
            new_name = self.get_argument("nomepag_novo","")
            if new_name:
                if "/" in new_name:
                    msg = u"* Nome de pasta não pode conter o caractere '/'<br/>"
                    self.render("modules/wiki/wiki-rename.html", NOMEPAG=u'páginas', \
                                PATH = self._wiki.getPagePath(links=False), \
                                NEWNAME=new_name, \
                                REGISTRY_ID=registry_id, WIKIDATA=self._wiki, PAGINA=pagina, \
                                MSG=msg)
                    
                    
                elif model.Wiki.nomepagExists(registry_id, new_name):
                    msg = u"Já existe uma página ou pasta com este nome<br/>"
                    self.render("modules/wiki/wiki-rename.html", NOMEPAG=u'páginas', \
                                PATH = self._wiki.getPagePath(links=False), \
                                NEWNAME=new_name, \
                                REGISTRY_ID=registry_id, WIKIDATA=self._wiki, PAGINA=pagina, \
                                MSG=msg)
                    
                else:
                    # atualiza nome da pasta
                    self._wiki.nomepag = new_name
                    self._wiki.data_alt = str(datetime.now())
                    self._wiki.alterado_por = user
                    self._wiki.save()
                    
                    # notifica o dono da página movida
                    email_msg = u"Pasta renomeada: "+doc_id+"\n"+\
                                u"De: " + old_name + " Para: " + new_name + "\n" +\
                                Notify.assinatura(user, registry_id, self._wiki.data_alt)+"\n\n"
                    Notify.email_notify(self._wiki.owner, user, u"renomeou uma pasta criada por você", \
                                   message=email_msg, \
                                   link="/wiki/%s?folder=%s"%(registry_id, pagina))
                    
                    log.model.log(user, u'renomeou a pasta', objeto=registry_id+"/"+self._wiki.nomepag, link="/wiki/%s?folder=%s"%(registry_id, pagina), tipo="wiki")
                    self.render("popup_msg.html", MSG=u"Pasta renomeada com sucesso.", REGISTRY_ID=registry_id)
            else:
                msg = u"Nome da pasta não preenchido."
                self.render("modules/wiki/wiki-rename.html", NOMEPAG=u'páginas', \
                            PATH = self._wiki.getPagePath(links=False), \
                            NEWNAME=new_name, \
                            REGISTRY_ID=registry_id, WIKIDATA=self._wiki, PAGINA=pagina, \
                            MSG=msg)
                
        else:
            self.render("popup_msg.html", MSG=u"Documento não encontrado: provavelmente o mesmo foi removido enquanto você editava-o.", \
                        REGISTRY_ID=registry_id)
            
            
class ShowWikiHistoryHandler(BaseHandler):
    ''' mostra histórico de atualizações de uma página Wiki '''
    
    @tornado.web.authenticated
    @core.model.serviceEnabled('wiki')
    @core.model.userOrOwner
    def get(self, registry_id, pagina):
        user = self.get_current_user()
        doc_id = '/'.join([registry_id, pagina])
        self._wiki = model.Wiki().retrieve(doc_id, include_removed=True)
        if self._wiki and self._wiki.is_folder!="S": 
            wiki_data = self._wiki.getWikiHistory()

            links = []
            if len(wiki_data["historico"]) > 10:
                links.append((u"Compactar histórico de versões", "/static/imagens/icones/compress32.png", "/wiki/compact/"+doc_id))

            log.model.log(user, u'acessou o histórico da página', objeto=doc_id, tipo="wiki", news=False)
            self.render("modules/wiki/wiki_historico.html", WIKIDATA=wiki_data, PAGINA=pagina, \
                        PATH= self._wiki.getPagePath(), \
                        INDEX=model.Wiki().retrieve(registry_id+"/indice"), \
                        LINKS=links, \
                        NOMEPAG=u'páginas', REGISTRY_ID=registry_id, MSG="")
        else:
            raise HTTPError(404)
        


class RestoreWikiHandler(BaseHandler):
    ''' restaura uma versão anterior de uma página Wiki '''
    
    @tornado.web.authenticated
    @core.model.serviceEnabled('wiki')
    @core.model.userOrOwner
    def get(self, registry_id, pagina):
        user = self.get_current_user()
        versao = self.get_argument("versao","-1")

        doc_id = '/'.join([registry_id, pagina])
        self._wiki = model.Wiki().retrieve(doc_id, include_removed=True)
        if self._wiki and self._wiki.is_folder!="S": 
            self._wiki.restoreVersion(int(versao))
            
            # notifica o dono da página restaurada
            email_msg = u"Página restaurada: "+doc_id+"\n"+\
                        u"Versão: " + versao + "\n" +\
                        Notify.assinatura(user, registry_id, self._wiki.historico[-1]["data_alt"])+"\n\n"
            Notify.email_notify(self._wiki.owner, user, u"restaurou uma versão de uma página criada por você", \
                           message=email_msg, \
                           link="/wiki/%s/%s"%(registry_id, pagina))
            
            log.model.log(user, u'restaurou a página', objeto=doc_id, tipo="wiki")
            
        self.redirect("/wiki/history/%s/%s"%(registry_id,pagina))
        

class CompactHistoryHandler(BaseHandler):
    ''' compacta histórico de atualizações de uma página Wiki removendo versões antigas '''
    
    @tornado.web.authenticated
    @core.model.serviceEnabled('wiki')
    @core.model.userOrOwner
    def get(self, registry_id, pagina):
        user = self.get_current_user()
        doc_id = '/'.join([registry_id, pagina])
        self._wiki = model.Wiki().retrieve(doc_id, include_removed=True)
        if self._wiki and self._wiki.is_folder!="S": 
            wiki_data = self._wiki.getWikiHistory()

            impossible = ""
            nversoes = len(wiki_data["historico"])
            if nversoes <= 10:
                impossible = u"Não é possível compactar este documento, pois ele possui somente %d " % nversoes + (u"versão.", u"versões.")[nversoes>1]
                
            self.render("modules/wiki/wiki_compact.html", HISTORY_LEN=nversoes, \
                        NOMEWIKIPAG=wiki_data["nomepag"], \
                        PATH=self._wiki.getPagePath(), \
                        IMPOSSIBLE=impossible, \
                        NOMEPAG=u'páginas', REGISTRY_ID=registry_id, MSG="")
                
        else:
            raise HTTPError(404)
              
    @tornado.web.authenticated
    @core.model.serviceEnabled('wiki')
    @core.model.userOrOwner
    def post(self, registry_id, pagina):
        user = self.get_current_user()
        doc_id = '/'.join([registry_id, pagina])
        
        self._wiki = model.Wiki().retrieve(doc_id, include_removed=True)
        if self._wiki and self._wiki.is_folder!="S": 
            history_len = len(self._wiki.historico)
            try:
                nversoes = int(self.get_argument("nversoes","0"))
            except Exception as detail:
                msg = u"Número de versões inválido."
                self.render("modules/wiki/wiki_compact.html", HISTORY_LEN=history_len, \
                            NOMEWIKIPAG=self._wiki.nomepag, \
                            PATH=self._wiki.getPagePath(), \
                            IMPOSSIBLE="", \
                            NOMEPAG=u'páginas', REGISTRY_ID=registry_id, MSG=msg)
                return
            
            if history_len > nversoes and nversoes >= 10:
                inicio = history_len - nversoes
                self._wiki.historico = self._wiki.historico[inicio:history_len]
                self._wiki.save()

                log.model.log(user, u'compactou o histórico da página', objeto=doc_id, tipo="wiki", news=False)
                self.redirect ("/wiki/history/"+doc_id)
                
            else:
                msg = u"Número de versões inválido."
                self.render("modules/wiki/wiki_compact.html", HISTORY_LEN=history_len, \
                            NOMEWIKIPAG=self._wiki.nomepag, \
                            PATH=self._wiki.getPagePath(), \
                            IMPOSSIBLE="", \
                            NOMEPAG=u'páginas', REGISTRY_ID=registry_id, MSG=msg)
                return
                    
        else:
            raise HTTPError(404)
        
          
class ListDeletedPagesHandler(BaseHandler):
    ''' Lista páginas Wiki apagadas de um usuário ou comunidade '''

    @tornado.web.authenticated
    @core.model.serviceEnabled('wiki')
    @core.model.userOrOwner
    def get (self, registry_id):
        user = self.get_current_user()
        page = int(self.get_argument("page","1"))
        (registry_type, privacidade) = getType(registry_id)
        user_or_owner = isUserOrOwner(user, registry_id)    
        (sel_multipla, pags) = prepareFolderPages(user, model.Wiki.listFolderPages(user, registry_id, "", page, NUM_MAX_WIKIPAGES, True), registry_type, privacidade, user_or_owner)
        pag_count = model.Wiki.countRemovedPages(registry_id)
        
        links = []
        if user_or_owner:
            links.append((u"Listar páginas", "/static/imagens/icones/wiki32.png", "/wiki/"+registry_id))
    
        log.model.log(user, u'acessou a lixeira das páginas de', objeto=registry_id, tipo="wiki", news=False)
        self.render("modules/wiki/wiki-listaremovidas.html", NOMEPAG=u'páginas', \
                    REGISTRY_ID=registry_id, \
                    LINKS=links, \
                    PAGINAS=pags, PAG_COUNT=pag_count, \
                    PAGE=page, PAGESIZE=NUM_MAX_WIKIPAGES, \
                    MSG="")


class WikiPermanentlyRemoveHandler(BaseHandler):
    ''' remove uma página definitivamente da lixeira '''
    
    @tornado.web.authenticated
    @core.model.serviceEnabled('wiki')
    @core.model.userOrOwner
    def get(self, registry_id, pagina):
        user = self.get_current_user()
        if pagina in ["home", "indice"]:
           self.render("home.html", MSG=u"Esta página não pode ser removida.", \
                       NOMEPAG=u'páginas', REGISTRY_ID=registry_id)
        else:
            doc_id = '/'.join([registry_id, pagina])
            self._wiki = model.Wiki().retrieve(doc_id, include_removed=True)
            if self._wiki:
                # salva variáveis para poder ter acesso a elas depois de remover do banco
                owner = self._wiki.owner
                
                # se é uma página e está na lixeira, remove-a
                if self._wiki.is_folder!="S" and self._wiki.historico[-1]["conteudo"] == _CONTEUDO_REMOVIDO:
                    self._wiki.deleteWiki(user, permanently=True)
                    
                    # notifica o dono da página excluída
                    email_msg = u"Página removida da lixeira: "+doc_id+"\n"+\
                                Notify.assinatura(user, registry_id, str(datetime.now()))+"\n\n"
                    Notify.email_notify(owner, user, u"removeu uma página sua da lixeira", \
                                   message=email_msg, \
                                   link="wiki/"+registry_id)
    
                    log.model.log(user, u'removeu da lixeira a página', objeto=doc_id, tipo="none")
                    
                self.redirect("/wiki/deleted/%s" % registry_id )
            else:
                raise HTTPError(404)
                
                
class ShowWikiPageHandler(BaseHandler):
    ''' mostra uma página Wiki '''
    
    @core.model.allowedToAccess
    @core.model.serviceEnabled('wiki')
    @libs.permissions.hasReadPermission ('wiki')
    def get(self, registry_id, pagina):
        user = self.get_current_user()
        versao = self.get_argument("versao","-1")

        doc_id = '/'.join([registry_id, pagina])
        self._wiki = model.Wiki().retrieve(doc_id, include_removed=True)
        if self._wiki and self._wiki.is_folder!="S": 
            wiki_data = prepareWikiPage(user, self._wiki.getWikiPage(user, versao=int(versao)))

            links = []
            if user:
                links.append(("Ver perfil de "+registry_id, "/static/imagens/icones/profile32.png", "/profile/"+registry_id))
                
                if isFriend(user, registry_id):
                    #links.append(("Enviar recado", "/static/imagens/icones/scrap32.png", "/scrap/"+registry_id))
                    if isOnline(registry_id):
                        links.append((u"Iniciar Chat com "+registry_id, "/static/imagens/icones/talk32.png", "/chat/"+registry_id))
                    else:
                        links.append((registry_id+u" não está online. Deixe uma mensagem.", "/static/imagens/icones/nottalk32.png", "/chat/"+registry_id))
                elif isAUser(registry_id) and user != registry_id:
                    self._reg = core.model.Member().retrieve(registry_id)

                    if user in self._reg.amigos_pendentes:
                        links.append((u"Já convidado. Aguardando resposta.", "/static/imagens/icones/invited_friend32.png", ""))
                    elif user in self._reg.amigos_convidados:
                        links.append(("Aceite convite de "+registry_id, "/static/imagens/icones/add_friend32.png", "/invites"))
                    else:
                        links.append(("Adicionar amigo", "/static/imagens/icones/add_friend32.png", "/newfriend?friend="+registry_id))
                                    
                self._reg_user = core.model.Registry().retrieve(user)
                user_or_owner = isUserOrOwner(user, registry_id)
                if self._reg_user and "bookmarks"  in self._reg_user.getServices:                              
                    links.append(bookmarks.model.Bookmarks.createBookmarkLink(user, "http://"+PLATAFORMA_URL+self.request.path))
                if user_or_owner:
                    links.append((u"Ver histórico de versões", "/static/imagens/icones/versions32.png", "/wiki/history/"+doc_id))
                if isAllowedToWriteObject(user, "wiki", registry_id, pagina):
                    links.append((u"Alterar esta página", "/static/imagens/icones/edit32.png", "/wiki/edit/"+doc_id))
                if isAllowedToDeleteObject(user, wiki_data["owner"],doc_id, wiki="S") or (pagina in ["home", "indice"] and user_or_owner):
                    links.append((u"Alterar permissões desta página", "/static/imagens/icones/permissions32.png", "/permission/wiki/"+doc_id, "", "", True))
                if isAllowedToDeleteObject(user, wiki_data["owner"],doc_id, wiki="S"):
                    links.append((u"Apagar esta página", "/static/imagens/icones/delete32.png", "/wiki/delete/"+doc_id,\
                                  "return confirm('Deseja realmente apagar esta página?');"))

            indice_links = []
            index = []
            if isAllowedToReadObject(user, "wiki", registry_id, "indice"):
                index = model.Wiki().retrieve(registry_id+"/indice")
                if wiki_data["alterar"]:
                    indice_links.append((u"Editar índice", "/static/imagens/icones/edit16.png", "/wiki/edit/"+registry_id+"/indice"))

            
            log.model.log(user, u'acessou a página', objeto=doc_id, tipo="wiki", news=False)
            self.render("modules/wiki/wiki_pagina.html", WIKIDATA=wiki_data, PAGINA=pagina, \
                        PATH= self._wiki.getPagePath(), \
                        USUARIOS_NO_CHAT=chat.model.getUsuariosNoChat(registry_id), \
                        LINKS=links, \
                        INDEX=index, \
                        INDICE_LINKS=indice_links, \
                        NOMEPAG=u'páginas', REGISTRY_ID=registry_id, MSG="")
        else:
            raise HTTPError(404)
            
            
URL_TO_PAGETITLE.update ({
        "wiki":   u"Páginas"
    })

HANDLERS.extend([
            (r"/wiki/%s" % (NOMEUSERS),                                     WikiHandler),
            (r"/wiki/newpage/%s" % (NOMEUSERS),                             WikiNewPageHandler),
            (r"/wiki/edit/%s/%s" % (NOMEUSERS, PAGENAMECHARS),              EditWikiPageHandler),
            (r"/wiki/portfolio/%s" % (NOMEUSERS),                           PortfolioHandler),
            (r"/wiki/comment/%s/%s" % (NOMEUSERS, PAGENAMECHARS),           CommentWikiHandler),
            (r"/wiki/comment/delete/%s/%s" % (NOMEUSERS, PAGENAMECHARS),    DeleteCommentHandler),
            (r"/wiki/newfolder/%s" % (NOMEUSERS),                           WikiNewFolderHandler),
            (r"/wiki/delete/%s/%s" % (NOMEUSERS, PAGENAMECHARS),            WikiDeleteHandler),
            (r"/wiki/delete/%s" % NOMEUSERS,                                WikiDeleteAllHandler),
            (r"/wiki/move/%s/%s" % (NOMEUSERS, PAGENAMECHARS),              WikiMoveHandler),
            (r"/wiki/move/%s" % NOMEUSERS,                                  WikiMoveAllHandler),
            (r"/wiki/rename/%s/%s" % (NOMEUSERS, PAGENAMECHARS),            FolderRenameHandler),
            (r"/wiki/history/%s/%s" % (NOMEUSERS, PAGENAMECHARS),           ShowWikiHistoryHandler),
            (r"/wiki/restore/%s/%s" % (NOMEUSERS, PAGENAMECHARS),           RestoreWikiHandler),
            (r"/wiki/compact/%s/%s" % (NOMEUSERS, PAGENAMECHARS),           CompactHistoryHandler),
            (r"/wiki/deleted/%s" % (NOMEUSERS),                             ListDeletedPagesHandler),
            (r"/wiki/remove/%s/%s" % (NOMEUSERS, PAGENAMECHARS),            WikiPermanentlyRemoveHandler),
            (r"/wiki/%s/%s" % (NOMEUSERS, PAGENAMECHARS),                   ShowWikiPageHandler)
])
