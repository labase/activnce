# -*- coding: utf-8 -*-
"""
################################################
Plataforma Oi Tonomundo - ActivUFRJ - Educopédia
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

import core.model
from core.dispatcher import BaseHandler, HANDLERS, URL_TO_PAGETITLE, \
                            PAGENAMECHARS, NUMERO                  
import log.model
from config import TUTORIAL


class TutorialChangeStatusHandler(BaseHandler):
    ''' Altera estado de visualização dos tutoriais de um usuário '''
   
    @tornado.web.authenticated
    def post (self):
        user = self.get_current_user()
        status = self.get_argument("status", "")
        
        _member = core.model.Member().retrieve(user)
        _member.show_tutorial = status
        _member.save()

        # atualiza o cookie
        self.set_secure_cookie("show_tutorial", status)            
        
        
class TutorialIndexHandler(BaseHandler):
    ''' Lista tutoriais existentes para um serviço '''
   
    @tornado.web.authenticated
    def get (self, service):
        user = self.get_current_user()

        if service in TUTORIAL:
            if len(TUTORIAL[service]) > 1 :
                # exibe uma lista de tutoriais existentes.     
                log.model.log(user, u'acessou a lista de tutoriais de', objeto=service, tipo="tutorial", news=False)       
                self.render("modules/tutorial/tutorial-list.html", \
                            ITENS=TUTORIAL[service], SERVICE=service)
            else:
                # não exibe índice se só existe um único tutorial
                self.redirect("/tutorial/%s/0/0" %service)
        else:
             raise HTTPError(404)


class TutorialHandler(BaseHandler):
    ''' Redireciona para a primeira tela de um tutorial de um serviço '''
   
    @tornado.web.authenticated
    def get (self, service, index_tutorial):
        self.redirect("/tutorial/%s/%s/0" % (service, index_tutorial))



class TutorialScreenHandler(BaseHandler):
    ''' Lista uma tela de um tutorial de um serviço '''
   
    @tornado.web.authenticated
    def get (self, service, index_tutorial, index_tela):
        user = self.get_current_user()
                
        if service in TUTORIAL and \
            int(index_tutorial) < len(TUTORIAL[service]["tutoriais"]) and \
            "telas" in TUTORIAL[service]["tutoriais"][int(index_tutorial)] and \
            int(index_tela) < len(TUTORIAL[service]["tutoriais"][int(index_tutorial)]["telas"]):

            log.model.log(user, u'acessou uma tela do tutorial ', objeto=service+"/"+index_tutorial, tipo="tutorial", news=False)
               
            self.render("modules/tutorial/tutorial.html", \
                        TUTORIAL=TUTORIAL[service]["tutoriais"][int(index_tutorial)], \
                        VOLTAR=len(TUTORIAL[service]["tutoriais"])>1, \
                        SERVICE=service, INDEX_TUTORIAL=int(index_tutorial), INDEX_TELA=int(index_tela))

        else:
             raise HTTPError(404)


URL_TO_PAGETITLE.update ({
        "tutorial": u"Tutorial"
    })

HANDLERS.extend([
            (r"/tutorial/change_status",                                     TutorialChangeStatusHandler),
            (r"/tutorial/%s"            % (PAGENAMECHARS),                   TutorialIndexHandler),
            (r"/tutorial/%s/%s"         % (PAGENAMECHARS,NUMERO),            TutorialHandler),
            (r"/tutorial/%s/%s/%s"      % (PAGENAMECHARS,NUMERO,NUMERO),     TutorialScreenHandler)
    ])
