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
import tornado.template

from core.dispatcher import BaseHandler, HANDLERS, URL_TO_PAGETITLE, \
                            NOMEUSERS, \
                            FILENAMECHARS, PAGENAMECHARS, \
                            sortedKeys
import core.model
from core.model import isUserOrOwner
import core.database
import log.model

''' importa definição do tutorial deste módulo, se existir _tutorial.py '''
from config import TUTORIAL
try:
    import _tutorial
except ImportError:
    pass

class GoogleCalendarHandler(BaseHandler, tornado.auth.GoogleMixin):
    ''' Exibe a agenda de um usuário/comunidade '''

    registry_id=""

    @tornado.web.asynchronous
    @tornado.web.authenticated
    @core.model.serviceEnabled('gcalendar')
    @tornado.gen.coroutine
    def get (self, registry_id):
        self.registry_id = registry_id
        print registry_id
        self._registry = core.model.Registry().retrieve(self.registry_id)
        if self._registry and self._registry.conta_google:
                   
            if self.get_argument("openid.mode", None):
                print "vou no google"
                #self.get_authenticated_user(self.async_callback(self._on_auth))
                google_user = yield self.get_authenticated_user()
                print "google_user=", google_user
                
                self._on_auth(google_user)

            else:
                yield self.authenticate_redirect()
            
        else:
            # senão escreve mensagem "Você ainda não registrou sua conta no Google"
            links = []
            if isUserOrOwner(self.get_current_user(), self.registry_id):
                links.append(("Registrar conta Google no Activ", "/static/imagens/icones/google32.png", "/google/init/"+self.registry_id))            
            self.render("modules/google/calendar.html", NOMEPAG="agenda", GOOGLE_ACCOUNT="", LINKS=links, \
                        REGISTRY_ID=self.registry_id, LOGOUT="")
                   
    def _on_auth(self, user):
        print "voltei"
        if not user:
            #raise tornado.web.HTTPError(500, "Google auth failed")    
            # caso o usuário recarregue a página do calendário com os parâmetros da query_string devolvidos pela autenticação do google,
            # faz redirect para o calendar sem parâmetro nenhum. 
            print "redirect"
            self.redirect("/google/%s" % self.registry_id)  
            return
             
        print "mostrando"
        #link para registrar conta google
        links = []
        if isUserOrOwner(self.get_current_user(), self.registry_id):
            links.append(("Registrar conta Google no Activ", "/static/imagens/icones/google32.png", "/google/init/"+self.registry_id))
        #links.append(("Realizar logoff do Google", "/static/imagens/icones/add_event32.png", "/google/logoff"))
        
        # monta iframe do calendario
        account_google = self._registry.conta_google
        logged_email = user["email"]
        logged_name = user["name"]
        logged_firstname = user["first_name"]
        self.render("modules/google/calendar.html", NOMEPAG="agenda", GOOGLE_ACCOUNT=account_google, \
                    LOGGED_EMAIL=logged_email, \
                    LOGGED_NAME=logged_name, \
                    LOGGED_FIRSTNAME=logged_firstname, \
                    LINKS=links, REGISTRY_ID=self.registry_id, LOGOUT="")        
            

        
        
class GoogleInitHandler(BaseHandler):
    ''' Registra o id google de um usuário/comunidade '''
    
    @tornado.web.authenticated
    @core.model.serviceEnabled('gcalendar')
    @core.model.userOrOwner
    def get (self, registry_id):
        user = self.get_current_user()

        account_google = ""
        self._registry = core.model.Registry().retrieve(registry_id)
        if self._registry and self._registry.conta_google:
            account_google = self._registry.conta_google
                    
        self.render("modules/google/add-account.html", NOMEPAG='agenda', \
                    REGISTRY_ID=registry_id, ACCOUNT_GOOGLE=account_google, \
                    MSG="")
  
    @tornado.web.authenticated
    @core.model.serviceEnabled('gcalendar')
    @core.model.userOrOwner
    def post (self, registry_id):
        user = self.get_current_user()
        
        # salva no registry de registry_id o email google do usuário.
        email_google = self.get_argument("email-google","")
        self._registry = core.model.Registry().retrieve(registry_id)
        self._registry.conta_google = email_google
        self._registry.save()

        self.redirect("/google/" + registry_id)
        

class GoogleLogoffHandler(BaseHandler):
    ''' Desloga google de um usuário/comunidade '''

    @tornado.web.authenticated
    def get (self):
        # Esta página google-logout possui 2 frames com 2 urls diferentes que desconectam do google.
        # São usadas 2 urls diferentes para caso de erro em uma delas 
        self.render("modules/google/google-logout.html", NOMEPAG="agenda")
        



                        
URL_TO_PAGETITLE.update ({
        "google": "Agenda Google"
    })

HANDLERS.extend([
            (r"/google/logoff",                    GoogleLogoffHandler),
            (r"/google/init/%s" % NOMEUSERS,       GoogleInitHandler),
            (r"/google/%s" % NOMEUSERS,          GoogleCalendarHandler)
    ])

