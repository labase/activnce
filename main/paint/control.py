# -*- coding: utf-8 -*-
"""
###############################################
AgileUFRJ - Implementando as teses do PPGI
###############################################

:Author: *Carlo E. T. Oliveira*
:Contact: carlo@nce.ufrj.br
:Date: $Date: 2009/09/02  $
:Status: This is a "work in progress"
:Revision: $Revision: 0.01 $
:Home: `LABASE `__
:Copyright: ©2009, `GPL 
"""

import re
import time
from datetime import datetime
from urllib import quote,unquote

import tornado.web
import tornado.template

import model
from model import _EMPTYDESENHO
import core.model
from core.model import isAUser
from core.dispatcher import BaseHandler, HANDLERS, URL_TO_PAGETITLE, \
                            NOMEUSERS, PAGENAMECHARS
import log.model
from libs.dateformat import short_datetime

''' importa definição do tutorial deste módulo, se existir _tutorial.py '''
from config import TUTORIAL
try:
    import _tutorial
except ImportError:
    pass


class NewPaintHandler(BaseHandler):
    ''' Seleciona template para editar '''
    
    @tornado.web.authenticated
    @core.model.serviceEnabled('paint')
    def get(self, registry_id):
        self.render("modules/paint/picture-list.html", NOMEPAG='desenhos', MSG="", REGISTRY_ID=registry_id)
        
    @tornado.web.authenticated
    @core.model.serviceEnabled('paint')
    def post(self, registry_id):
        user = self.get_current_user()

        if not (isAUser(registry_id) and registry_id == user):
            msg = u"Você não tem permissão para editar este desenho."
            self.render("home.html", MSG=msg,NOMEPAG='desenhos', REGISTRY_ID=registry_id)
            return
        
        imagem = "nenhum"    
        
        if 'templates' in self.request.arguments:        
            for value in self.request.arguments['templates']:
                imagem = value 
        
        url = "/paint/new/" + registry_id + "/" + imagem
        self.redirect(url)
        
class EditNewPaintHandler(BaseHandler):
    ''' Edita novo desenho '''
     
    @tornado.web.authenticated
    @core.model.serviceEnabled('paint')
    def get(self, registry_id, image):
        msg = ""
        user = self.get_current_user()

        if not (isAUser(registry_id) and registry_id == user):
            msg = u"Você não tem permissão para editar este desenho."
            self.render("home.html", MSG=msg,NOMEPAG='desenhos', REGISTRY_ID=registry_id)
            return
        
        self.render("modules/paint/svg-editor.html", REGISTRY_ID=registry_id,
                    NOMEPAG='agenda',NEW_PICTURE=image, EDIT_PICTURE ="")
    
    @tornado.web.authenticated
    @core.model.serviceEnabled('paint')
    def post(self, registry_id, image):
        msg = ""
        user = self.get_current_user()

        if not (isAUser(registry_id) and registry_id == user):
            msg = u"Você não tem permissão para editar este desenho."
            self.render("home.html", MSG=msg,NOMEPAG='desenhos', REGISTRY_ID=registry_id)
            return
        
        nomeDesenho = self.get_argument("nomeDesenho", "").replace(" ", "_")
        desenho = self.get_argument("desenho", "")
        desenho_data = _EMPTYDESENHO()
        if registry_id in model.DESENHO:
            desenho_data.update(model.DESENHO[registry_id])
        desenho_data['desenhos'][nomeDesenho] = desenho
        try:
            model.DESENHO[registry_id] = desenho_data
        except:
            self.render("home.html", MSG=u"Erro: %s" % detail, NOMEPAG='desenhos')
            return
        
        #desenho = "data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIj8+Cjxzdmcgd2lkdGg9IjY0MCIgaGVpZ2h0PSI0ODAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiPgogPG1ldGFkYXRhIGlkPSJtZXRhZGF0YTMwNDIiPmltYWdlL3N2Zyt4bWw8L21l";
        #self.render("modules/paint/teste.html", REGISTRY_ID=registry_id, NOMEPAG='agenda',DESENHO=desenho)


class ListPaintHandler(BaseHandler):
    ''' Exibe lista de desenhos do registry_id '''
     
    @tornado.web.authenticated
    @core.model.serviceEnabled('paint')
    def get(self, registry_id):
        msg = ""
        user = self.get_current_user()
        permissao = False
        if (isAUser(registry_id) and registry_id == user):
            permissao = True
        desenho_data = _EMPTYDESENHO()
        desenhos = []
        if registry_id in model.DESENHO:
            desenho_data.update(model.DESENHO[registry_id])
            desenhos = desenho_data['desenhos'].items()
        self.render("modules/paint/desenhos.html", NOMEPAG='desenhos', \
                REGISTRY_ID=registry_id, DESENHOS = desenhos, MSG="", PERMISSAO = permissao)


class EditPaintHandler(BaseHandler):
    ''' Edita desenho '''
     
    @tornado.web.authenticated
    @core.model.serviceEnabled('paint')
    def get(self, registry_id, nomeDesenho):
        msg = ""
        desenho_data = _EMPTYDESENHO()
        desenho = ""
        if registry_id in model.DESENHO:
            desenho_data.update(model.DESENHO[registry_id])
            desenho = desenho_data['desenhos'][nomeDesenho]
            self.render("modules/paint/svg-editor.html", REGISTRY_ID=registry_id,
                    NOMEPAG='desenhos',IMAGE=desenho, EDIT_PICTURE = nomeDesenho)
            
    @tornado.web.authenticated
    @core.model.serviceEnabled('paint')
    def post(self, registry_id, nomeDesenho):
        msg = ""
        user = self.get_current_user()

        if not (isAUser(registry_id) and registry_id == user):
            msg = u"Você não tem permissão para editar este desenho."
            self.render("home.html", MSG=msg,NOMEPAG='desenhos', REGISTRY_ID=registry_id)
            return
        
        nomeDesenho = self.get_argument("nomeDesenho", "")
        desenho = self.get_argument("desenho", "")
        desenho_data = _EMPTYDESENHO()
        if registry_id in model.DESENHO:
            desenho_data.update(model.DESENHO[registry_id])
        desenho_data['desenhos'][nomeDesenho] = desenho
        try:
            model.DESENHO[registry_id] = desenho_data
        except:
            self.render("home.html", MSG=u"Erro: %s" % detail, NOMEPAG='desenhos')
            return

class DeletePaintHandler(BaseHandler):
    ''' Remove desenho '''
     
    @tornado.web.authenticated
    @core.model.serviceEnabled('paint')
    def get(self, registry_id, nomeDesenho):
        msg = ""
        desenho_data = _EMPTYDESENHO()
        desenho = ""
        if registry_id in model.DESENHO:
            desenho_data.update(model.DESENHO[registry_id])
            desenho = desenho_data['desenhos'][nomeDesenho]
            desenho_data['desenhos'].pop(nomeDesenho)
            
            try:
                model.DESENHO[registry_id] = desenho_data
            except:
                self.render("home.html", MSG=u"Erro: %s" % detail, NOMEPAG='desenhos')
                return
        self.redirect("/paint/%s" % registry_id )


URL_TO_PAGETITLE.update ({
        "paint":   "Desenhos"
    })

HANDLERS.extend([
            (r"/paint/templates/%s" % (NOMEUSERS),                  NewPaintHandler),
            (r"/paint/%s" % (NOMEUSERS),                            ListPaintHandler),
            (r"/paint/new/%s/%s" % (NOMEUSERS, PAGENAMECHARS),      EditNewPaintHandler),
            (r"/paint/edit/%s/%s" % (NOMEUSERS, PAGENAMECHARS),     EditPaintHandler),
            (r"/paint/delete/%s/%s" % (NOMEUSERS, PAGENAMECHARS),   DeletePaintHandler)
    ])
