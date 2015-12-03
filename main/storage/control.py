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

import model
import database

import core.model

from core.dispatcher import BaseHandler, HANDLERS, URL_TO_PAGETITLE, \
                            NOMEUSERS, \
                            FILENAMECHARS, PAGENAMECHARS
                            
from libs.permissions import isAllowedToDeleteObject, isAllowedToComment, isAllowedToDeleteComment

from datetime import datetime

                
                
class StorageStartAppHandler(BaseHandler):
    ''' executa o código de um activlet '''
    
    @tornado.web.authenticated
    def get(self, app_name):
        user = self.get_current_user()        
  
        self._activlet = model.Activlet().retrieve(app_name)
        if self._activlet: 
            self.write (self._activlet.source_code)
        else:
            self.write (dict(status=1, msg=u"Aplicação não encontrada"))
            
                        
class StorageItemHandler(BaseHandler):
    ''' salva e recupera um item do storage '''
    ''' Falta garantir que uma aplicação só possa alterar seus próprios dados. '''
    ''' Idem para um usuário. '''
    
    
    @tornado.web.authenticated
    def get(self, app_name, registry_id, key):
        # obtem valor de <key> do storage
        if registry_id == "current_user":
           registry_id = self.get_current_user() 
        self._storage = model.Storage().retrieve(app_name)
        if self._storage: 
            value = self._storage.getValue(registry_id, key)
            self.write (dict(status=0, value=value))
        else:
            self.write (dict(status=1, msg=u"Item não encontrado"))
    
    @tornado.web.authenticated
    def post(self, app_name, registry_id, key):
        # armazena <key>:<value> no storage
        if registry_id == "current_user":
           registry_id = self.get_current_user() 
        value = self.get_argument("value","")

        self._storage = model.Storage().retrieve(app_name)
        if self._storage: 
            self._storage.setValue(registry_id, key, value)
            self._storage.save()
            
        else:
            self._storage = model.Storage()  
            self._storage.setValue(registry_id, key, value)
            self._storage.save(id=app_name)
           
        self.write (dict(status=0, msg=u"Valor armazenado."))
            
            
URL_TO_PAGETITLE.update ({
        "storage":   u"Storage"
    })

HANDLERS.extend([
            (r"/storage/%s"       % (NOMEUSERS),                             StorageStartAppHandler), # GET  /storage/<app_name>
            (r"/storage/%s/%s/%s" % (NOMEUSERS, NOMEUSERS, PAGENAMECHARS),   StorageItemHandler),     # GET  /storage/<app_name>/<registry_id>/<key>
                                                                                                      # GET  /storage/<app_name>/current_user/<key>
                                                                                                      # POST /storage/<app_name>/<registry_id>/<key>
                                                                                                      # POST /storage/<app_name>/current_user/<key>
])
