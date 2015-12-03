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

from libs.strformat import remove_diacritics, remove_special_chars
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

# Número máximo de itens exibidos em uma página do glossário
NUM_MAX_ITENS_GLOSSARIO = 10

NOME_PAG_CLOSSARIO = u'glossário'


class GlossaryNewItemHandler(BaseHandler):
    ''' Inclusão de um item ao glossário do usuário '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('glossary')
    @libs.permissions.canWriteService ('glossary')
    def get(self, registry_id):
        user = self.get_current_user()
        if not isUserOrMember(user, registry_id):
            self.render("home.html", MSG=u"Você não tem permissão para criar termos neste glossário.", \
                        NOMEPAG=NOME_PAG_CLOSSARIO, REGISTRY_ID=registry_id)
            return

        self.render("modules/glossary/new_glossary_item-form.html", \
                    NOMEPAG=NOME_PAG_CLOSSARIO, DEFINITION=u"Digite a definição do termo. <br/>",
                    REGISTRY_ID=registry_id, MSG="")

    @tornado.web.authenticated
    @core.model.serviceEnabled('glossary')
    @libs.permissions.canWriteService ('glossary')
    def post(self, registry_id):
        user = self.get_current_user()
        if not isUserOrMember(user, registry_id):
            self.render("home.html", MSG=u"Você não tem permissão para criar termos neste glossário.", \
                        NOMEPAG=NOME_PAG_CLOSSARIO, REGISTRY_ID=registry_id)
            return
        MSG = ""
        glossary_term = self.get_argument("term","")
        if not glossary_term:
            MSG += u"Termo não pode ser vazio."
        glossary_definition = self.get_argument("definition","")
        if not glossary_definition:
                MSG += u"%sA definição do termo não pode estar vazia." % ("" if not MSG else "<br/>")
        if not MSG:
            glossary_item_id = remove_special_chars(remove_diacritics(glossary_term.replace(" ","_")))
            if model.Glossary.searchItemByRegistryIdAndItemId(user, registry_id, glossary_item_id, False):
                MSG += u"Termo já definido neste glossário."

        if MSG:
            self.render("modules/glossary/new_glossary_item-form.html", \
                        NOMEPAG=NOME_PAG_CLOSSARIO, DEFINITION=glossary_definition, REGISTRY_ID=registry_id, MSG=MSG)
            return
        else:
            self._glossary = model.Glossary()
            self._glossary.id = '/'.join([registry_id,glossary_item_id])
            self._glossary.registry_id = registry_id
            self._glossary.owner = user
            self._glossary.item_id = glossary_item_id
            self._glossary.term = self.get_argument("term","")
            self._glossary.definition = glossary_definition
            self._glossary.tags = splitTags(self.get_argument("tags",""))
            self._glossary.data_cri = self._glossary.data_alt = str(datetime.now())
            self._glossary.alterado_por = user
            self._glossary.saveGlossaryItem(glossary_item_id)
            log.model.log(user, u'criou um termo no glossário de', objeto=registry_id, tipo="glossary")

        self.redirect("/glossary/%s" % registry_id)

class GlossaryListHandler(BaseHandler):
    ''' Exibe glossário do registry_id '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('glossary')
    @libs.permissions.canReadService ('glossary')
    def get(self, registry_id):
        user = self.get_current_user()
        page = int(self.get_argument("page","1"))
        letra = self.get_argument("letra","")

        glossary = model.Glossary.listGlossary(user, registry_id, page, NUM_MAX_ITENS_GLOSSARIO)
        glossary_count = model.Glossary.countGlossaryByRegistryId(registry_id)
        tags_list = model.Glossary.listAllTags(registry_id)
        links = []
        if isAllowedToWriteObject(user, "glossary", registry_id):
            links.append((u"Criar novo termo", "/static/imagens/icones/new32.png", "/glossary/new/"+registry_id))
        if isUserOrOwner(user, registry_id):
            links.append((u"Alterar permissões deste Glossário", "/static/imagens/icones/permissions32.png", "/permission/glossary/"+registry_id, "", "", True))

        log.model.log(user, u'acessou o glossário de', objeto=registry_id, tipo="glossary", news=False)
                
        self.render("modules/glossary/glossary-list.html", NOMEPAG=NOME_PAG_CLOSSARIO, \
                    REGISTRY_ID=registry_id, CRIAR=isUserOrMember(user,registry_id), \
                    TAG=None, LINKS=links, \
                    FOTO=False, \
                    GLOSSARY=glossary, GLOSSARY_COUNT=glossary_count, \
                    TAGS_LIST = tags_list , \
                    PAGE=page, PAGESIZE=NUM_MAX_ITENS_GLOSSARIO, \
                    TITLE=u"Glossário de %s"%registry_id, \
                    MSG="")

class GlossaryListUserTagHandler(BaseHandler):
    ''' Exibe itens do glossário de um usuário com uma tag específica '''

    @core.model.allowedToAccess
    @core.model.serviceEnabled('glossary')
    @libs.permissions.canReadService ('glossary')
    def get(self, registry_id, tag):
        user = self.get_current_user()
        page = int(self.get_argument("page","1"))

        glossary = model.Glossary.listGlossary(user, registry_id, page, NUM_MAX_ITENS_GLOSSARIO, tag)
        glossary_count = model.Glossary.countGlossaryByRegistryIdAndTag(registry_id, tag)
        tags_list = model.Glossary.listAllTags(registry_id, tag)

        log.model.log(user, u'acessou o glossário de', objeto=registry_id, tipo="glossary", news=False)

        self.render("modules/glossary/glossary-list.html", NOMEPAG=NOME_PAG_CLOSSARIO, \
                    REGISTRY_ID=registry_id, CRIAR=isUserOrMember(user,registry_id), \
                    TAG=tag, LINKS=[], \
                    FOTO=False, \
                    GLOSSARY=glossary, GLOSSARY_COUNT=glossary_count, \
                    TAGS_LIST = tags_list, \
                    PAGE=page, PAGESIZE=NUM_MAX_ITENS_GLOSSARIO, \
                    TITLE=u"Glossário de %s com a tag %s"%(registry_id,tag),  \
                    MSG="")

class GlossaryViewItemHandler(BaseHandler):
    ''' Exibe um item do glossário de um usuário '''

    @core.model.allowedToAccess
    @core.model.serviceEnabled('glossary')
    @libs.permissions.canReadService ('glossary')
    def get(self, registry_id, glossary_item_id):
        user = self.get_current_user()

        glossary_id = registry_id+"/"+glossary_item_id
        
        glossary = model.Glossary.searchItemByRegistryIdAndItemId(user, registry_id, glossary_item_id, False)

        if not glossary:
            raise HTTPError(404)
        
        else:   # glossary encontrado
            tags_list = model.Glossary.listAllTags(registry_id)
            
            log.model.log(user, u'acessou o glossário de', objeto=registry_id, tipo="glossary", news=False)

            self.render("modules/glossary/glossary-list.html", NOMEPAG=NOME_PAG_CLOSSARIO, \
                        REGISTRY_ID=registry_id, CRIAR=False, \
                        TAG=None, LINKS=[], FOTO=False, \
                        GLOSSARY=glossary, GLOSSARY_COUNT=1, PAGE_LINKS=[], \
                        TAGS_LIST = tags_list, \
                        PAGE=1, PAGESIZE=1, \
                        TITLE="", MSG="" )

class GlossaryDeleteItemHandler(BaseHandler):
    ''' Apaga um termo do glossário do usuário '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('glossary')
    def get(self, registry_id):
        user = self.get_current_user()
        
        glossary_item_id = self.get_argument("item_id","")
        glossary_id = registry_id+"/"+glossary_item_id
        self._glossary = model.Glossary().retrieve(glossary_id)
        
        if self._glossary != None:
            glossary_owner = self._glossary.owner
            if not isAllowedToDeleteObject(user, glossary_owner, glossary_id):
                self.render("home.html", MSG=u"Você não tem permissão para remover este termo deste glossário.", \
                            NOMEPAG=NOME_PAG_CLOSSARIO, REGISTRY_ID=registry_id)
                return

            term = self._glossary.term
            self._glossary.deleteGlossaryItem()
            
            # notifica o dono do arquivo excluído
            email_msg = u"Item de glossário removido: "+term+"\n"+\
                        Notify.assinatura(user, registry_id, str(datetime.now()))+"\n\n"
            Notify.email_notify(glossary_owner, user, u"removeu um termo de glossário criado por você", \
                           message=email_msg, \
                           link="glossary/"+registry_id)
                            
            log.model.log(user, u'removeu um termo do glossário de', objeto=registry_id, tipo="glossary")
            
            self.redirect("/glossary/%s" % registry_id)

        else:
            raise HTTPError(404)


class GlossaryEditItemHandler(BaseHandler):
    ''' Alteração de um termo do glossário '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('glossary')
    @libs.permissions.canWriteService ('glossary')
    def get(self, registry_id):
        user = self.get_current_user()
        glossary_item_id = self.get_argument("item_id","")
        glossary_id = registry_id+"/"+glossary_item_id
        
        self._glossary = model.Glossary().retrieve(glossary_id)
        if self._glossary != None:
            #if isAllowedToEditObject(user, self._glossary.owner, glossary_id):
            if isAllowedToWriteObject(user, "glossary", registry_id):
                self.render("modules/glossary/glossary_item-edit.html", \
                            NOMEPAG=NOME_PAG_CLOSSARIO, REGISTRY_ID=registry_id, \
                            GLOSSARY=self._glossary, MSG="")
            else:
                self.render("home.html", MSG=u"Você não tem permissão para alterar este termo deste glossário.", \
                           NOMEPAG=NOME_PAG_CLOSSARIO, REGISTRY_ID=user)
        else:
            self.render("home.html", MSG=u"Erro: termo inexistente no glossário!", \
                        NOMEPAG=NOME_PAG_CLOSSARIO, REGISTRY_ID=registry_id)

    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('glossary')
    @libs.permissions.canWriteService ('glossary')
    def post(self, registry_id):
        user = self.get_current_user()
        glossary_item_id = self.get_argument("item_id","")
        glossary_id = registry_id+"/"+glossary_item_id
        glossary_definition = self.get_argument("definition","")

        self._glossary = model.Glossary().retrieve(glossary_id)
        if self._glossary != None:
            #if isAllowedToEditObject(user, self._glossary.owner, glossary_id):
            if isAllowedToWriteObject(user, "glossary", registry_id):
                if not glossary_definition:
                    MSG = u"A definição do termo não pode estar vazia."
                    self.render("modules/glossary/glossary_item-edit.html", \
                                NOMEPAG=NOME_PAG_CLOSSARIO, GLOSSARY=self._glossary,
                                REGISTRY_ID=registry_id, MSG=MSG)
                    return
                else:  # glossary_definition != ""
                    self._glossary.editGlossaryItem(user, glossary_definition, splitTags(self.get_argument("tags","")))
                    log.model.log(user, u'alterou um termo do glossário de', objeto=registry_id, tipo="glossary")
                    self.redirect("/glossary/%s" % registry_id)
            else:
                self.render("home.html", MSG=u"Você não tem permissão para alterar este termo deste glossário.", \
                           NOMEPAG=NOME_PAG_CLOSSARIO, REGISTRY_ID=user)
        else:
            self.render("home.html", MSG=u"Erro: termo inexistente no glossário!", \
                        NOMEPAG=NOME_PAG_CLOSSARIO, REGISTRY_ID=registry_id)

class GlossaryTermHandler(BaseHandler):
    ''' Lista usuários de definiram um dado termo em seus glossários '''
    
    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        glossary_item_id = self.get_argument("item_id","")
        glossary_term = self.get_argument("term","")
        page = int(self.get_argument("page","1"))

        glossary = model.Glossary.searchGlossaryByItemId(user, glossary_item_id, page, NUM_MAX_ITENS_GLOSSARIO)
        glossary_count = model.Glossary.countGlossaryByItemId(glossary_item_id)
        tags_list = model.Glossary.listAllTags(user)
                
        self.render("modules/glossary/glossary-list.html", NOMEPAG=NOME_PAG_CLOSSARIO, \
                    REGISTRY_ID=user, CRIAR=False, \
                    TAG=None, LINKS=[], \
                    TAGS_LIST=tags_list, \
                    FOTO=True, \
                    GLOSSARY=glossary, GLOSSARY_COUNT=glossary_count, \
                    PAGE=page, PAGESIZE=NUM_MAX_ITENS_GLOSSARIO, \
                    TITLE=u"Usuários que definiram o termo %s" % glossary_term, \
                    MSG="")
        
URL_TO_PAGETITLE.update ({
        "glossary":   "Glossário"
    })

HANDLERS.extend([
            (r"/glossary/new/%s" % (NOMEUSERS),                     GlossaryNewItemHandler),
            (r"/glossary/view/%s/%s" % (NOMEUSERS, PAGENAMECHARS),  GlossaryViewItemHandler),   # registry_id/glossary_item_id>
            (r"/glossary/term",                                     GlossaryTermHandler),       # ?item_id=<glossary_item_id>
            (r"/glossary/%s" % (NOMEUSERS),                         GlossaryListHandler),
            (r"/glossary/delete/%s" % (NOMEUSERS),                  GlossaryDeleteItemHandler), # ?item_id=<glossary_item_id>
            (r"/glossary/edit/%s" % (NOMEUSERS),                    GlossaryEditItemHandler),   # ?Item_id=<glossary_item_id>
            (r"/glossary/%s/%s"  % (NOMEUSERS, PAGENAMECHARS),      GlossaryListUserTagHandler)
    ])
