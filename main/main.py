#!/usr/bin/python
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
:Home: `LABASE <http://labase.nce.ufrj.br/>`__
:Copyright: ©2009, `GPL <http://is.gd/3Udt>__. 
"""

import sys, errno
import os.path
import locale
from threading import Thread
import thread
from time import sleep
import datetime
import base64
import uuid

import tornado.auth
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.wsgi
from tornado.options import define, options

import core.uimodules
import core.uimethods
from core.dispatcher import HANDLERS
import wiki.control
import friends.control
import community.control
import scrapbook.control
import log.control
import blog.control
import mblog.control
import evaluation.control
import chat.control
import agenda.control
import admin.control
import forum.control
import noticia.control
import invites.control
import files.control
import paint.control
import studio.control
import bookmarks.control
import glossary.control
import rating.control
import storage.control
import permission.control
import google.control
import ajax.control
import task.control
import question.control
import quiz.control
import skills.control
import videoaula.control
import tutorial.control
import activity.control

import plugins.api.control
import plugins.trainz.control
import plugins.tol.control
import plugins.cancel.control
import plugins.game.control
import plugins.wisconsin.control

import core.rest
import wiki.rest
import studio.rest
import evaluation.rest

# devem ser os últimos controladores a serem importados (nessa ordem)
import search.control   # usa URL_TO_PAGETITLE para criar legenda da página de reultados de uma busca por tags
import error.control    # redireciona para tela padrão de erro 404



import core.model
import wiki.model
import log.model

from config import PLATAFORMA, PLATAFORMA_URL, COUCHDB_URL, USER_ADMIN, SENHA_USER_ADMIN, PRIVILEGIOS
from config import THREAD_PROCESSES, DATED_THREAD_PROCESSES

from libs.notify import Notify
from libs.dateformat import seconds_to_weekday

tornado.locale.load_translations(
    os.path.join(os.path.dirname(__file__), "translations"))


class Application(tornado.web.Application):
    def __init__(self):
        handlers = HANDLERS
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            autoescape=None,
            #cookie_secret="11oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            #cookie_secret=base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes),
            login_url="/",
            ui_modules=core.uimodules,
            ui_methods=core.uimethods
        )
        if PLATAFORMA_URL=="localhost:8888":
            settings["cookie_secret"] = "11oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo="
        else:
            settings["cookie_secret"] = base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)
        
        tornado.web.Application.__init__(self, handlers, **settings)

class WsgiApp(tornado.wsgi.WSGIApplication):
    def __init__(self):
        handlers = HANDLERS
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=False,
            #cookie_secret="11oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            cookie_secret=base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes),
            login_url="/login",
            ui_modules=core.uimodules,
            ui_methods=core.uimethods
        )
        tornado.wsgi.WSGIApplication.__init__(self, handlers, **settings)


# ------ Threads ---------------------------------------------------------

class Log(Thread):
    """ Copia o log e o news para o banco de dados e processa a ordenação das listas de amigos e comunidades. """
       
    def run(self):
        log.model.saveLog()
       

class Logger(Thread):
    """ Loop para execução do Log """
       
    def run(self):
        while 1:
            proc_log = Log()
            proc_log.start()
            sleep (self._Thread__kwargs["minutos"] * 60)


class Notify(Thread):
    """ Envia email com notificação do chat """
       
    def run(self):
        chat.model.batch_notify()
      
        
class ChatNotify(Thread):
    """ Loop para execução do envio de email com notificação do chat """
       
    def run(self):
        while 1:
            proc = Notify()
            proc.start()
            sleep (self._Thread__kwargs["minutos"] * 60)


class Load_Autocomplete(Thread):
    """ Carrega lista de tags para o autocomplete """
       
    def run(self):
        core.model.saveAutocompleteStrings()
       

class AutocompleteLoader(Thread):
    """ Loop para execução da carga do autocomplete """
       
    def run(self):
        while 1:
            proc_log = Load_Autocomplete()
            proc_log.start()
            sleep (self._Thread__kwargs["minutos"] * 60)
            
            
class UsersNotify(Thread):
   """ Envia todas as notificações pendentes em batch """
       
   def run(self):
       Notify.batch_notify()


class Notifier(Thread):
    """ Loop para execução de Notify """
    
    def run(self):
        # Programa a primeira execução para daqui ao número de segundos que faltam
        # para o dia da semana/hora definidos
        seconds = seconds_to_weekday(self._Thread__kwargs["process_date"]["wkday"], 
                                  self._Thread__kwargs["process_date"]["hh"], 
                                  self._Thread__kwargs["process_date"]["mm"], 
                                  self._Thread__kwargs["process_date"]["ss"])
        sleep (seconds)
        proc_log = UsersNotify()
        proc_log.start()
        
        # Continua executando a cada semana subsequente
        while 1:
            sleep (7 * 24 * 60 * 60)
            proc_log = UsersNotify()
            proc_log.start()


class NewsCleaner(Thread):
    """ Remove as novidades antigas do banco de dados """
       
    def run(self):
        # Programa a primeira execução para daqui ao número de segundos que faltam
        # para o dia da semana/hora definidos
        seconds = seconds_to_weekday(self._Thread__kwargs["process_date"]["wkday"], 
                                  self._Thread__kwargs["process_date"]["hh"], 
                                  self._Thread__kwargs["process_date"]["mm"], 
                                  self._Thread__kwargs["process_date"]["ss"])
        sleep (seconds)
        log.model.cleanNews()
        
        # Continua executando a cada dia subsequente
        while 1:
            sleep (24 * 60 * 60)
            log.model.cleanNews()

def main():
    define("port", default=8888, help="run on the given port", type=int)
   
    i = 0
    proc = []
    for nome_classe, minutos in THREAD_PROCESSES.iteritems():
        if minutos > 0:
            exec "proc.append(%s(kwargs={'minutos':%s}))" % (nome_classe, minutos)
            proc[i].start()
            i = i + 1
            
    for nome_classe, process_date in DATED_THREAD_PROCESSES.iteritems():
        exec "proc.append(%s(kwargs={'process_date':%s}))" % (nome_classe, process_date)
        proc[i].start()
        i = i + 1

    # Cria usuário padrão
    _usr = core.model.Member().createUser(USER_ADMIN, SENHA_USER_ADMIN, u"Administrador", u" do %s" % PLATAFORMA, u"Privada")
    
    # Cria todas as comunidades de privilégios
    for priv in PRIVILEGIOS:
        _prv = core.model.Community().createPrivilege(priv, PRIVILEGIOS[priv]['desc'], PRIVILEGIOS[priv]['apps'], PRIVILEGIOS[priv]['services'], _usr)
        
        # cria páginas home e indice da comunidade do privilégio
        #cria_pagina("home", priv, USER_ADMIN)
        #cria_pagina("indice", priv, USER_ADMIN)
        _wiki = wiki.model.Wiki().retrieve(priv+"/home")
        if not _wiki: wiki.model.Wiki().createInitialPage("home", priv, USER_ADMIN)

        _wiki = wiki.model.Wiki().retrieve(priv+"/indice")
        if not _wiki: wiki.model.Wiki().createInitialPage("indice", priv, USER_ADMIN)

#    # iniciando logger...
#    proc_logger = Logger()
#    proc_logger.start()
#
#    # iniciando NewsCleaner...
#    proc_NewsCleaner = NewsCleaner()
#    proc_NewsCleaner.start()
    
           
    # iniciando tornado...
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()

