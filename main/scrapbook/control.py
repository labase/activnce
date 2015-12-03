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
from datetime import datetime
from string import find, replace

import tornado.web
from tornado.web import HTTPError
import tornado.template

import model
import core.model
from core.model import isUserOrMember, isFriendOrMember, isUserOrOwner, getType
import core.database
import log.model
from core.dispatcher import BaseHandler, HANDLERS,  URL_TO_PAGETITLE, NOMEUSERS
from libs.notify import Notify
from config import PLATAFORMA, PRIV_SUPORTE_ACTIV, USER_ADMIN, PRIV_GLOBAL_ADMIN

''' importa definição do tutorial deste módulo, se existir _tutorial.py '''
from config import TUTORIAL
try:
    import _tutorial
except ImportError:
    pass


NUM_MAX_SCRAPS = 10

def processa_url (conteudo):
    r1 = r"(\b(http|https)://([-A-Za-z0-9+&@#/%?=~_()|!:,.;]*[-A-Za-z0-9+&@#/%=~_()|]))"
    return re.sub(r1, r'<a title="\1" href="\1">\1</a>', conteudo)


class ListScrapbookHandler(BaseHandler):
    ''' Lista os recados de um usuário ou comunidade '''

    @tornado.web.authenticated
    @core.model.allowedToAccess
    def get(self, registry_id):
        user = self.get_current_user()
        page = int(self.get_argument("page","1"))
        
        if isFriendOrMember(user, registry_id):
            self._scrap = model.Scrapbook().retrieve(registry_id)
            scrap_list = []
            scraps_count = 0
            if self._scrap!=None:
                filter = not isUserOrMember(user, registry_id)
                scrap_list = self._scrap.getScrapbookList(user, page=page, page_size=NUM_MAX_SCRAPS, \
                                                      filter=filter)
                scraps_count = self._scrap.countScraps(user, filter=filter)
                
            self.render("modules/scrapbook/scrap-list.html", REGISTRY_ID=registry_id, \
                        USER=user, NOMEPAG='recados', \
                        APAGAR=isUserOrOwner(user, registry_id), \
                        SCRAPDATA=scrap_list, SCRAPS_COUNT = scraps_count, \
                        PAGE=page, PAGESIZE=NUM_MAX_SCRAPS)
            
        else:
            raise HTTPError(403)            


class NewScrapHandler(BaseHandler):
    ''' Envia um recado para um usuário ou comunidade  '''
    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        friend = self.get_argument('friend', "")
        if isFriendOrMember(user, friend):
            self.render("modules/scrapbook/scrap-form.html", MSG="",NOMEPAG='recados', REGISTRY_ID=user, FRIEND=friend)
        else:
            self.render("home.html", MSG=u"Você só pode enviar recados para seus amigos ou para comunidades que participa.", \
                        NOMEPAG='recados', REGISTRY_ID=friend)

    @tornado.web.authenticated
    def post(self):
        user = self.get_current_user()
        friend = self.get_argument('friend', "")
        scrap = self.get_argument('scrap', "")
        
        # trata injeção de tags html e acrescenta links nas urls
        scrap = replace(scrap,"<","&lt;")
        scrap = replace(scrap,">","&gt;")
        scrap = processa_url(scrap)
        
        if isFriendOrMember(user, friend):
            msg = ''
            if friend and getType(friend)[0] in ["member" , "community"]:
                if scrap:
                    
                    # saveScrap -----------------------------------------
                    self._scrap = model.Scrapbook().retrieve(friend)
                    if not self._scrap: self._scrap = model.Scrapbook(user_to=friend)
                    
                    self._scrap.saveScrap(user_from=user, scrap=scrap)
                    # ---------------------------------------------------
                    
                    # notifica quem recebeu o recado
                    email_msg = scrap+"\n"+\
                                Notify.assinatura (user, friend, self._scrap.recados[0].data)+"\n\n"
                    Notify.email_notify(friend, user, u"enviou um recado para %s" % friend, \
                                           message=email_msg, link="scrap/"+friend)
                    log.model.log(user, u'enviou recado para', objeto=friend, tipo="user", news=False)
                    self.redirect ("/scrap/%s" % friend)
                
                else:
                    self.render("home.html", MSG=u'Você não escreveu o seu recado.',\
                                NOMEPAG='recados', REGISTRY_ID=friend)
            else:
                raise HTTPError(404)
        else:
            raise HTTPError(403)


class DeleteScrapHandler(BaseHandler):
    ''' Apaga um Recado do Scrapbook '''
    
    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        registry_id = self.get_argument("id","")
        item = self.get_argument("item","")
        
        if registry_id == "" or item == "":
            raise HTTPError(404)
        
        elif not isUserOrOwner(user, registry_id):
            raise HTTPError(403)

        else:
            # remove o post
            self._scrap = model.Scrapbook().retrieve(registry_id)
            if self._scrap:
                self._scrap.removeScrap(int(item))
    
            log.model.log(user, u'removeu o recado de', objeto=registry_id, tipo="none", news=False)     
            self.redirect("/scrap/%s" % registry_id)


URL_TO_PAGETITLE.update ({
        "scrap": "Recados"
    })

HANDLERS.extend([
            (r"/scrap/%s" % (NOMEUSERS),    ListScrapbookHandler),
            (r"/new/scrap",                 NewScrapHandler),
            (r"/delete/scrap",              DeleteScrapHandler)
        ])
