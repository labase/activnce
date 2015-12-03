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

import core.database
from core.dispatcher import BaseHandler, HANDLERS,  URL_TO_PAGETITLE, \
                            NOMEUSERS
from search.model import cloudTag

class FindUserHandler(BaseHandler):
    ''' Retorna Json com lista de pessoas sugeridas para um autocomplete '''
    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        ret = dict()
        for row in core.database.REGISTRY.view('users/partial_data'):
            ret[row.key] = row.value["nome_completo"]
        self.write (ret)        
        
class FindCommunityHandler(BaseHandler):
    ''' Retorna Json com lista de comunidades sugeridas para um autocomplete '''
    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        ret = dict()
        for row in core.database.REGISTRY.view('communities/partial_data'):
            ret[row.key] = row.value["description"]
        self.write (ret)   
                
class FindTagHandler(BaseHandler):
    ''' Retorna Json com lista de tags sugeridas para um autocomplete '''
    @tornado.web.authenticated
    def get(self):
        self.write (cloudTag())  
                            
HANDLERS.extend([
            (r"/ajax/finduser",                    FindUserHandler),
            (r"/ajax/findcommunity",               FindCommunityHandler),
            (r"/ajax/findtag",                     FindTagHandler)
        ])
