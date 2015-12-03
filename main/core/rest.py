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
import hashlib
import time
from datetime import datetime
import string
import re
import operator
from operator import itemgetter
import random
from random import choice
from datetime import date, timedelta
from uuid import uuid4

  
from couchdb.client import Document, View

import model
from model import _EMPTYMEMBER, _EMPTYCOMMUNITY, _EMPTYDBINTRANET
from model import isOwner, isMember, isUserOrMember
from model import usersByEmail, isACommunity, isAUser, isOnline
import database

import wiki.model
import log.model
from log.model import get_news_list, get_log_list
import log.database

from config import SMTP, VERSAO_TNM, PLATAFORMA, PLATAFORMA_URL, \
                   ENTRY_POINTS, DEFAULT_ENTRY_POINT
                   
from libs.notify import Notify
from libs.strformat import has_diacritics

from dispatcher import BaseHandler, HANDLERS, TAMMINPWD


class RestLoginHandler(BaseHandler):
    ''' Autenticação de usuários redirecionando para o painel de controle do usuário '''
    def get(self):
        next = self.get_argument("next", "")
        user = self.get_current_user()
        if user:
            url_home = ("/user/%s" % user, next)[next!=""]
            self.redirect (url_home)
        else:
            
            form = dict(
                      action="",
                      login=dict(type="@text",value=""),
                      senha=dict(type="@text",value=""),
                      next=dict(type="@hidden",value=""),
                      remember_me=dict(type=("S","N"),value="N"),
                      
                      )
            self.write (dict(status=0, result=form))
            

    def post(self):
        user   = self.get_argument("user", "")
        passwd = self.get_argument("passwd", "")
        next   = self.get_argument("next", "")

        url_home = ("/user/%s" % user, next)[next!=""]
        #url_erro = "modules/core/login-form.html"
        url_erro = self.searchEntryPoint()
        if passwd != "" and user != "":
            hash = hashlib.md5()
            hash.update(user.encode('utf-8') + passwd.encode('utf-8'))             
            passwd = hash.hexdigest()
            _user = model.Registry().retrieve(user)
            if _user and _user.getType()=="member" and _user.passwd==passwd:
                if self.get_argument("remember", "0") == "1":
                    self.set_secure_cookie("user", user)
                    self.set_secure_cookie("nome", _user.name.encode('utf-8'))
                else:
                    self.set_secure_cookie("user", user, None)
                    self.set_secure_cookie("nome", _user.name.encode('utf-8'), None)
                self.clear_cookie("navigation")
                    
                log.model.log(user, u'entrou no '+PLATAFORMA, news=False)
                self.redirect("rest/wiki/%s/home" % user)
            else:
                self.write (dict(status=1, msg=u"Senha incorreta ou usuário inexistente."))
        else:
            self.write (dict(status=1, msg=u"Senha ou usuário não especificados."))


class RestChangePasswdHandler(BaseHandler):
    ''' Alteração da senha do usuário '''
    
    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        user_data = database.REGISTRY[user]
        
        form = dict(
                      action="",
                      oldpasswd=dict(type="@text",value=""),
                      newpasswd=dict(type="@text",value=""),
                      confpasswd=dict(type="@text",value="")
                      
                      )
        self.write (dict(status=0, result=form))

    @tornado.web.authenticated
    def post(self):
        user = self.get_current_user()
        
        oldpasswd = self.get_argument("oldpasswd", "")
        newpasswd = self.get_argument("newpasswd", "")
        confpasswd = self.get_argument("confpasswd", "")
        msg = ""
        
        if oldpasswd == "" or newpasswd == "":
            msg = u"Há campos não preenchidos!<br/>"
        elif newpasswd != confpasswd:
            msg = u"Senha diferente da confirmação!<br/>"
        elif  len(newpasswd) < TAMMINPWD:
            msg = u"Senha deve ter no mínimo %s caracteres.<br/>" % (TAMMINPWD)
        elif has_diacritics(newpasswd):
            msg = u"Senha não deve conter caracteres acentuados.<br/>"
        else:
            user_data = _EMPTYMEMBER()
            user_data.update(database.REGISTRY[user])
            
            hash = hashlib.md5()
            hash.update(user.encode('utf-8') + oldpasswd.encode('utf-8'))
            cryptpasswd = hash.hexdigest()
            
            if user_data["passwd"] == cryptpasswd:
                hash = hashlib.md5()
                hash.update(user+newpasswd)
                user_data["passwd"] = hash.hexdigest()

            else:
                msg = u"Senha antiga incorreta!<br/>"

        if msg:
            self.write (dict(status=1, msg=msg))
            
        else:
            database.REGISTRY[user] = user_data

            # notifica o usuário que sua senha foi alterada
            email_msg = u"A senha da conta '" + user + u"' foi alterada recentemente.\n" + \
                        u"Se você mesmo realizou essa alteração, não é necessário fazer mais nada.\n" + \
                        u"Se você não alterou sua senha, isso significa que sua conta pode ter sido invadida. " + \
                        u"Para voltar a ter acesso à sua conta, será necessário redefinir sua senha. " + \
                        u"Para isso, clique no botão abaixo, ou em 'esqueci minha senha' na página de login do " + PLATAFORMA + u" e altere sua senha agora.\n" + \
                        Notify.assinatura(user, user, str(datetime.now()))+"\n\n"
            
            Notify.email_notify(user, user, "A senha da sua conta no "+PLATAFORMA+" foi alterada", \
                           message=email_msg, link="forgotpasswd", sendToMyself=True)
            
            self.write (dict(status=0, msg=u"Senha alterada com sucesso!"))                    

            
HANDLERS.extend([
                (r"/rest/login",                       RestLoginHandler),
                (r"/rest/profile/changepasswd",        RestChangePasswdHandler)
            ])
