# -*- coding: utf-8 -*-
"""
################################################
Oi Tonomundo - NCE/UFRJ
################################################

:Author: Eduardo Paz
:Contact: edupaz@nce.ufrj.br
:Date: $Date: 2010/08/20  $
:Status: This is a "work in progress"
:Revision: $Revision: 0.01 $
:Home: ``
:Copyright:  
"""

import re
import time
from datetime import datetime
from uuid import uuid4
from urllib import quote,unquote

import tornado.web
import tornado.template

import model
from model import Noticias, Noticia

import core.database
import core.model
from core.model import isOwner
from core.dispatcher import BaseHandler, HANDLERS, URL_TO_PAGETITLE, \
                            NOMEUSERS, \
                            FILENAMECHARS, PAGENAMECHARS
from config import PRIV_GLOBAL_ADMIN

import log.model
from libs.dateformat import short_date
 
''' importa definição do tutorial deste módulo, se existir _tutorial.py '''
from config import TUTORIAL
try:
    import _tutorial
except ImportError:
    pass




def teste(texto):
    print "="*20 + " " + str(texto) + " " + "="*20
    
def eh_acesso_invalido(self, registry_id):
    ''' se a comunidade não existir retorna mensagem d erro '''
    user = self.get_current_user()
    if registry_id not in core.database.REGISTRY:
        msg = u"Comunidade inexistente."
        self.render("home.html", NOMEPAG=u'Notícias', MSG= msg, REGISTRY_ID= user)
        return True
    elif user not in core.database.REGISTRY[registry_id]["participantes"]:
        msg = u"Você não é membro desta comunidade."
        self.render("home.html", NOMEPAG=u'Notícias', MSG=msg, REGISTRY_ID=registry_id)
        return True
    else:
        return False

    


#=============== HANDLERS ======================================================

class ListaHandler(BaseHandler):
    ''' Lista as noticias de uma comunidade '''
        
    @tornado.web.authenticated
    @core.model.allowedToAccess    
    @core.model.serviceEnabled('noticia')
    def get (self, registry_id):
        user = self.get_current_user()
        # Validar acesso
        #if eh_acesso_invalido(self, registry_id): return

        # Classe noticias
        noticias = Noticias(registry_id)
        lista = noticias.get_obj_lista_noticias(user=user)
        
        links = []
        if isOwner(user, registry_id):
            links.append((u"Nova notícia", "/static/imagens/icones/add_news32.png", "/noticia/"+registry_id+"/new"))

        log.model.log(user, u'acessou as notícias de', objeto=registry_id, tipo="noticia", news=False)
                
        #chamando a página
        self.render("modules/noticia/noticia-list.html", NOMEPAG=u'Notícias', \
                    REGISTRY_ID=registry_id, \
                    LINKS=links, NOW=str(datetime.now())[0:11], \
                    LISTA=lista, EH_EDITOR=isOwner(user,registry_id))
        return


class NewHandler(BaseHandler):
    '''Criar nova notícia '''

    @tornado.web.authenticated
    @core.model.serviceEnabled('noticia')
    @core.model.owner
    def get (self, registry_id):
        # Validar acesso
        if eh_acesso_invalido(self, registry_id): return
        
        try:
            id = int(self.get_argument("n",""))
        except:
            id = -1
            
        noticia = Noticia(registry_id, id)
        if noticia.dt_validade != "":
            n = noticia.dt_validade
            n = n[8:]+"/"+n[5:7]+"/"+n[0:4]
            noticia.dt_validade = n
        
        self.render("modules/noticia/noticia-new.html", NOMEPAG=u'Notícias', \
                    REGISTRY_ID=registry_id, MSG="", \
                    NOTICIA=noticia)
        return

    @tornado.web.authenticated
    @core.model.serviceEnabled('noticia')
    @core.model.owner
    def post(self, registry_id):
        # Validar acesso
        if eh_acesso_invalido(self, registry_id): return
        
        user = self.get_current_user()
                
        id = int( self.get_argument("id","") )
        
        noticias = Noticias(registry_id)
        noticia  = Noticia(registry_id, id)
        
        noticia.id            = id
        noticia.titulo        = self.get_argument("titulo","Sem titulo")
        noticia.resumo        = self.get_argument("resumo", "")
        noticia.texto         = self.get_argument("texto","")
        noticia.dt_publicacao = str(datetime.now())
        noticia.url           = self.get_argument("url", "")
        noticia.dt_validade   = self.get_argument("dt_validade", "")
        noticia.fonte         = self.get_argument("fonte", "")
        noticia.popup         = self.get_argument("popup", "")
        
        if noticia.dt_validade != "":
            try:
                f = lambda n: ("00"+n)[-2:]
                x = noticia.dt_validade.split("/")
                x.reverse()
                x[1] = f(x[1])
                x[2] = f(x[2])
                x = "-".join(x)
                d = time.strptime(x, "%Y-%m-%d")
                noticia.dt_validade   = x
            except:
                self.render("modules/noticia/noticia-new.html", NOMEPAG=u'Notícias', \
                            REGISTRY_ID=registry_id, MSG="Data inválida", \
                            NOTICIA=noticia)
                return
        
        noticias.insert_noticia(noticia)
        
        log.model.log(user, u'criou ou alterou uma notícia em', objeto=registry_id, tipo="noticia")
        
        self.redirect("/noticia/"+registry_id)
        return

class NoticiaHandler(BaseHandler):
    '''Exibe uma notícia '''

    @tornado.web.authenticated
    @core.model.allowedToAccessPrivNoticias
    @core.model.serviceEnabled('noticia')
    def get (self, registry_id, id_noticia):
        # Validar acesso
        #if eh_acesso_invalido(self, registry_id): return
        
        user = self.get_current_user()
                
        tr = self.get_argument("tr","")
        
        try:
            id = int(id_noticia)
        except:
            msg = u"Notícia inválida."
            self.render("home.html", NOMEPAG=u'Notícias', MSG=msg, REGISTRY_ID=registry_id)
            
        noticia = Noticia(registry_id, id)
        noticia.dt_publicacao = short_date(noticia.dt_publicacao)
        
        if noticia.url != "":
            self.redirect(noticia.url)
        else:
            log.model.log(user, u'acessou uma notícia em', objeto=registry_id, tipo="noticia", news=False)            
            self.render("modules/noticia/noticia.html", NOMEPAG=u'Notícias', \
                        REGISTRY_ID=registry_id, \
                        NOTICIA=noticia, TR=tr)
        return

class XMLHandler(BaseHandler):
    ''' Retorna XML com as noticias de uma comunidade,
        utilizado para o pop-up de notícias.
    '''

    @tornado.web.authenticated
    @core.model.allowedToAccessPrivNoticias
    @core.model.serviceEnabled('noticia')
    def get (self, registry_id):
        # Classe noticias
        noticias = Noticias(registry_id)
        lista = noticias.get_obj_lista_noticias(popup="S")
        self.set_header("Content-Type", "application/xml")
        self.render("modules/noticia/noticias.xml", NOMEPAG=u'Notícias', \
                    LISTA=lista, NOW=str(datetime.now())[0:11], \
                    CHANGE_NAVIGATION=False, \
                    REGISTRY_ID=registry_id)


#==============================================================================
URL_TO_PAGETITLE.update ({
        "noticia": "Noticia"
    })

HANDLERS.extend([
            (r"/noticia/%s" % NOMEUSERS,                    ListaHandler), 
            (r"/noticia/%s/new" % NOMEUSERS,                NewHandler),
            (r"/noticia/xml/%s" % NOMEUSERS,                XMLHandler),
            (r"/noticia/%s/%s" % (NOMEUSERS,NOMEUSERS),     NoticiaHandler)
    ])

