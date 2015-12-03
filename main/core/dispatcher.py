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
import tornado.escape
from tornado.escape import json_decode

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
import traceback
import json


# pymssql é utilizado apenas para acesso ao banco da Intranet/SIGA.
try:
    import pymssql
except ImportError:
    pass
  
from couchdb.client import Document, View

import model
from model import _EMPTYMEMBER, _EMPTYCOMMUNITY, _EMPTYDBINTRANET
from model import isOwner, isMember, isUserOrMember
from model import emailExists, usersByEmail, isACommunity, isAUser, isOnline
import database
from database import PASSWD_USER_SUSPENDED

import agenda.model
import wiki.model
import scrapbook.model
import log.model
from log.model import get_news_list, get_log_list
import log.database
import blog.model
import mblog.model
import forum.model
import chat.model
import skills.model
from search.model import TAGS, addTag, removeTag, cloudTag, removeUserTags, splitTags, formatTags
import invites.model
from invites.model import _EMPTYKEYS, _EMPTYINVITES
from config import PRIV_GLOBAL_ADMIN, PRIV_CRIAR_COMUNIDADES, SERVICES, MENU, USER_ADMIN, COMUNIDADE_BEMVINDO
from config import SMTP, VERSAO_TNM, PLATAFORMA, PLATAFORMA_URL, \
                   ENTRY_POINTS, DEFAULT_ENTRY_POINT, EMAIL_ERROR_NOTIFY

from noticia.model import Noticias

''' importa definição do tutorial deste módulo, se existir _tutorial.py '''
from config import TUTORIAL
try:
    import _tutorial
except ImportError:
    pass
               
from libs.notify import Notify
from libs.strformat import remove_diacritics, remove_special_chars, has_diacritics
from libs.images import thumbnail
from libs.dateformat import elapsed_time

# no cadastro de usuários e na criação de comunidades, os identificadores devem:
# começar com uma letra ou número, seguida de uma sequência de letras, números, sublinhado e ponto e não pode terminar com ponto.
VALID_LOGIN = "(^[a-zA-Z0-9][\w\.]+\w$)"

# máscaras para identificação e crítica da query_string
NOME = "([\w\.\@\-]+)"
NUMERO = "([\d]+)"

# máscaras para identificação e crítica de um registry_id
# na url rest: aceita também @ e - (na educopédia os emails eram utilizados como login)
NOMEUSERS = "([\w\.\@\-]+)"

# máscaras para identificação e crítica de um nome de página wiki
# usar também para criticar tags
# PAGENAMECHARS inclui:
#   letras, letras acentuadas, números, sublinhado(_), menos(-), ponto(.) e % (escape character na URL)
PAGENAMECHARS  = "([a-zA-Z0-9_\-.àáãéêíóõôúüçÀÁÃÉÊÍÓÕÔÚÜÇ%@]+)"

# máscaras para identificação de um nome de arquivo
FILENAMECHARS = "([a-zA-Z0-9àáãéêíóõôúüçÀÁÃÉÊÍÓÕÔÚÜÇ!#$%&'()+,-.;=@^_`{}~]+)"

# Palavras reservadas para nomes de usuários e comunidades
RESERVED_WORDS = [ "new", "edit", "delete", "comment", "search", \
                   "changepasswd", "newpage", "portfolio", "current_user" ]

# Número mínimo de caracteres de uma senha
TAMMINPWD = 4                                        

# Campos de preenchimento obrigatório no formulário de cadastro de usuários
_EMPTYMEMBERFORM = ["user", "passwd", "npasswd", "name", "lastname", "email", "mkey"]


# Campos de preenchimento obrigatório no formulário de alteração do perfil de usuários
_EDITFORMKEYS = ['name', 'lastname', 'email', 'notify']

# Campos de preenchimento obrigatório no formulário de criação de comunidades
_EMPTYCOMMUNITYFORM = ["name", "description", "privacidade", "participacao"]


# Numero de iten no Painel de Controle
QTD_AMIGOS_PAINEL_CONTROLE = 15
QTD_COMUNIDADES_PAINEL_CONTROLE = 15
QTD_MBLOG_PAINEL_CONTROLE = 1
QTD_RECADOS_PAINEL_CONTROLE = 1
QTD_NOVIDADES_PAINEL_CONTROLE = 3
QTD_EVENTOS_PAINEL_CONTROLE = 3

QTD_MEMBROS_PAINEL_CONTROLE = 15
QTD_BLOG_PAINEL_CONTROLE = 1
QTD_FORUM_PAINEL_CONTROLE = 1
QTD_PAGINAS_PAINEL_CONTROLE = 1
      
        
def GenMagicKey(length=24, chars=string.letters + string.digits):
    # formato antigo das chaves:
    # char(2)  - tipo de chave, indica se é de comunidade ou papel do usuário
    # char(4)  - código da instituição do usuário/comunidade
    # char(24) - string gerada aleatoriamente
    
    return 'ACTIV_' + ''.join([choice(chars) for i in range(length)])

        
def GenPasswd(length=6, chars=string.letters + string.digits):
    return ''.join([choice(chars) for i in range(length)])

def validateEmail(email):
    if len(email) > 7:
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
            return 1
    return 0

def sortedKeys (d, rev_order=False):
    k = d.keys()
    k.sort()
    if rev_order: k.reverse()
    return k

def sortedKeys_ignorecase (d):
    k = d.keys()
    k.sort(key=lambda x: x.lower())
    return k







# -----------------------------------------------------------------------------
# BaseHandler

    
class BaseHandler(tornado.web.RequestHandler):
    
    navigation = [] # lista de urls dos registry_ids navegados pelo usuário
   
    def get_current_user(self):
        return self.get_secure_cookie("user")

    def get_current_user_name(self):
        return self.get_secure_cookie("nome")
    
    def get_current_user_services(self):
        txtcookie = self.get_secure_cookie("services")
        return txtcookie.split(":") if txtcookie else []
    
    def get_current_show_tutorial(self):
        return self.get_secure_cookie("show_tutorial")

    """
    def isAllowedToAccess(self, user, registry_id, display_error=True):
        # Bloqueia acesso aos usuários/comunidades privadas se o usuário logado não for amigo/participante.
        # Apesar de existir um decorator para isso, este método continua tendo utilidade para, por exemplo, evitar que a busca encontre 
        # usuários privados e seus conteúdos.
        
        msg = ""
        if registry_id in database.REGISTRY:
            if database.REGISTRY[registry_id]["privacidade"]=="Privada":
                if "passwd" in database.REGISTRY[registry_id]:
                    if user != registry_id and user not in database.REGISTRY[registry_id]["amigos"]:
                        msg = u"Acesso negado: %s é um usuário privado." % registry_id
                else:
                    if user not in database.REGISTRY[registry_id]["participantes"]:
                        msg = u"Este conteúdo só pode ser acessado pelos participantes da comunidade %s." % registry_id
        else:
            msg = u"Usuário ou comunidade inexistentes."
            
        if msg:
            if display_error:
                self.render("home.html", MSG=msg, REGISTRY_ID=user, NOMEPAG="perfil")
            return False
        else:
            return True
    """
#    def redirect (self, url):
#        """ preserva o argumento noframe da query_string ao redirecionar para uma URL """
#        
#        if self.get_argument("noframe", ""):
#            separador = "&" if "?" in url else "?"
#            url += separador + "noframe=" + self.get_argument("noframe", "")
#
#        super(BaseHandler,self).redirect(url)

    def gera_lista_notificacoes(self, user):
        lista_notificacoes = []

        if user : 
            try:
                model.Registry().retrieve(user)["_attachments"]
            except:
                lista_notificacoes.append((u"Você ainda não adicionou uma foto ao seu perfil!", "/profile/edit"))
                
            try:                
                documentoSkills=skills.model.Skill().retrieve(user)
            except:
                documentoSkills = ""
                
            if documentoSkills:
                if not documentoSkills["formacao"]:
                    lista_notificacoes.append((u"Você ainda não adicionou suas formações acadêmicas!", "/profile/skills/new/experience#Formacao"))
                
                if not documentoSkills["experiencias"]:
                    lista_notificacoes.append((u"Você ainda não adicionou experiências profissionais!", "/profile/skills/new/experience#Experiencias"))
                
                if not documentoSkills["habilidades"]:
                    lista_notificacoes.append((u"Você ainda não adicionou habilidades ao seu perfil!", "/profile/skills/"+user+"#adicionarHabilidade"))          
            else: 
                lista_notificacoes.append((u"Você ainda não adicionou experiências profissionais!", "/profile/skills/new/experience#Formacao"))
                lista_notificacoes.append((u"Você ainda não adicionou suas formações acadêmicas!", "/profile/skills/new/experience#Formacao"))
                lista_notificacoes.append((u"Você ainda não adicionou habilidades ao seu perfil!", "/profile/skills/new/experience#Formacao"))
                
        return lista_notificacoes
    
            
        """
        ###Barra de compleção do perfil
        contadorComplecao = 0
        if user == registry_id:
            percentualPerfil=20
            msgPercentualPerfil = ""
            caminhoCompPerfil= ""
            
            try:
                model.Registry().retrieve(registry_id)["_attachments"]
                percentualPerfil+=20
            except:
                contadorComplecao+=1
                caminhoCompPerfil = "/profile/edit"
                msgPercentualPerfil+= u"Você ainda não adicionou uma foto ao seu perfil!\n<br>"
            try:                
                documentoSkills=skills.model.Skill().retrieve(registry_id)
            except:
                documentoSkills = ""
                
            if documentoSkills:
                if (documentoSkills["formacao"]):
                    percentualPerfil+=20
                else:
                    contadorComplecao+=1
                    msgPercentualPerfil+= u"Você ainda não adicionou suas formações acadêmicas!\n<br>"
                    if caminhoCompPerfil == "":
                        caminhoCompPerfil= "/profile/skills/new/experience#Formacao"
                
                if (documentoSkills["experiencias"]):
                    percentualPerfil+=20
                else:
                    contadorComplecao+=1
                    msgPercentualPerfil+= u"Você ainda não adicionou experiências profissionais!\n<br>"
                    if caminhoCompPerfil == "":
                        caminhoCompPerfil="/profile/skills/new/experience#Experiencias"
                
                if (documentoSkills["habilidades"]):
                     percentualPerfil+=20
                else:
                    contadorComplecao+=1
                    msgPercentualPerfil+= u"Você ainda não adicionou habilidades ao seu perfil!\n<br>"
                    if caminhoCompPerfil == "":
                        caminhoCompPerfil = "/profile/skills/"+user+"#adicionarHabilidade"            
            else: 
                contadorComplecao+=1
                msgPercentualPerfil+= u"Você ainda não adicionou experiências profissionais!\n<br>Você ainda não adicionou suas formações acadêmicas!\n<br>Você ainda não adicionou habilidades ao seu perfil!\n<br>"
                if caminhoCompPerfil == "":
                    caminhoCompPerfil = "/profile/skills/new/experience#Formacao"
            
            if percentualPerfil == 20:
                links.append((msgPercentualPerfil, "/static/imagens/icones/barra20.png", caminhoCompPerfil))
            elif percentualPerfil == 40:     
                links.append((msgPercentualPerfil, "/static/imagens/icones/barra40.png", caminhoCompPerfil))
            elif percentualPerfil == 60:     
                links.append((msgPercentualPerfil, "/static/imagens/icones/barra60.png", caminhoCompPerfil))
            elif percentualPerfil == 80:     
                links.append((msgPercentualPerfil, "/static/imagens/icones/barra80.png", caminhoCompPerfil))
        ###Fim da barra de compleção do perfil
        """

            

        

    def searchEntryPoint(self):
        for point in ENTRY_POINTS:
            if point in self.request.host:
                return ENTRY_POINTS[point]["arq_home"]
        return DEFAULT_ENTRY_POINT["arq_home"]        
        
            
                  
    def render(self, template_name, REGISTRY_ID="", CHANGE_NAVIGATION=True, **kwargs):  
        user_logado = self.get_current_user()
        if not REGISTRY_ID:
           REGISTRY_ID = user_logado
        nome_usuario = self.get_current_user_name()
        show_tutorial = self.get_current_show_tutorial()
        
        # instancia um objeto com as informações de registry_id
        # que serão necessárias nos templates
        tipo_registry = ""
        user_data = {}
        if REGISTRY_ID:
            user_data = model.Registry().retrieve(REGISTRY_ID)
            if user_data:
                tipo_registry = user_data.getType() 
        
        # Procura o título da página em função da URL carregada
        str_path = self.request.path.split("/")
        str_path = str_path[1] if len(str_path) > 1 else ""
        """
        if str_path1=="permission":
            str_path = str_path[2] if len(str_path) > 2 else ""
        else:
            str_path = str_path1
        """
        
        page_title = PLATAFORMA
        url_retorno = ""
        if str_path in URL_TO_PAGETITLE:
            page_title += (": " + URL_TO_PAGETITLE[str_path])
            if REGISTRY_ID:
                url_retorno = "/"+str_path if str_path=="invites" else "/%s/%s" % (str_path,REGISTRY_ID)
          
        # se não tem usuário logado, não mostra link se o serviço for do tipo object (wiki, file, etc)
        if not user_logado and tipo_registry and str_path in SERVICES[tipo_registry] and SERVICES[tipo_registry][str_path]["perm_type"]=="object":
            url_retorno = ""     
            
        self.navigation = []
        if user_logado:
            model.USUARIOS_LOGADOS[user_logado] = str(datetime.now())
            
            # obtem caminho de navegação do usuário no cookie e transforma numa lista
            self.navigation = self.get_secure_cookie("navigation") or "/user/%s"%user_logado
            self.navigation = self.navigation.split(";")
            
            # altera o caminho de acordo com a url visitada
            if CHANGE_NAVIGATION:
                url = "/user/%s"%REGISTRY_ID if tipo_registry == "member" else "/community/%s"%REGISTRY_ID
                
                # acrescenta a url atual à lista de urls navegadas
                # ou reposiciona numa url anterior caso o usuário tenha voltado a uma url já navegada.
                if url in self.navigation:
                    i = self.navigation.index(url)
                    self.navigation = self.navigation[0:i+1]
                    
                else:
                    self.navigation.append(url)

                # salva novo caminho no cookie
                self.set_secure_cookie("navigation", ";".join(self.navigation).encode('utf-8'), None)
         
        """
        print "kwargs=", kwargs
        if self.get_argument("rest", None) == None:
            self.write (kwargs)
        else:
        """
        super(BaseHandler,self).render(template_name, REGISTRY_ID=REGISTRY_ID, \
                                       USERDATA=user_data, \
                                       TIPO_REGISTRY=tipo_registry, \
                                       LOGADO=user_logado, \
                                       LOGADO_SERVICES=self.get_current_user_services(), \
                                       NOME_USUARIO=nome_usuario, \
                                       SHOW_TUTORIAL=show_tutorial, \
                                       PAGETITLE=page_title, \
                                       URL_RETORNO=url_retorno, \
                                       SERVICES=SERVICES, \
                                       MENU=MENU, \
                                       LISTA_NOTIFICACOES=self.gera_lista_notificacoes(user_logado), \
                                       NAVIGATION=self.navigation, \
                                       VERSAO_TNM=VERSAO_TNM, \
                                       PLATAFORMA=PLATAFORMA, \
                                       PLATAFORMA_URL=PLATAFORMA_URL, \
                                       TUTORIAL_ICON=str_path in TUTORIAL, \
                                       STR_PATH=str_path, \
                                       RECENT_ACTIONS = log.model.get_recent_actions(user_logado, limit=15, news=True), \
                                       AUTOCOMPLETE_TAGS=model.getAutocompleteTags(), \
                                       AUTOCOMPLETE_USERS=model.getAutocompleteUsers(), \
                                       AUTOCOMPLETE_COMMUNITIES=model.getAutocompleteCommunities(), \
                                       AUTOCOMPLETE_CONFIRMED_SKILLS=model.getAutocompleteConfirmedSkills(), \
                                       **kwargs)


    def write_error(self, status_code, **kwargs): 
        #Customização das páginas de erro.
        msg = ""

        if status_code == 403:
            # Forbidden
            msg = u"Você não tem permissão para acessar esse conteúdo."
            img_src = "/static/error/forbidden.png"
            self.render("modules/error/template-error.html", NOMEPAG="", LINKS="", MSG=msg, STATUS_CODE=str(status_code), IMG_SRC=img_src)
            
        elif status_code == 404:
            # File not found
            msg = u"Oops! Página não encontrada. Tem certeza que digitou o endereço correto?"
            img_src = "/static/error/notfound.png"
            self.render("modules/error/template-error.html", NOMEPAG="", LINKS="", MSG=msg, STATUS_CODE=str(status_code), IMG_SRC=img_src)
                        
        elif status_code in [400, 500, 503]:
            
            import traceback
            user = self.get_current_user()
            if not user:
                user = u"usuario nao logado"
            self._blog = blog.model.Blog()
            error_time = str(datetime.now())
            error_id = remove_special_chars(remove_diacritics(error_time.replace(" ","_")))
            self._blog.post_id = error_id
            self._blog.titulo = "Erro "+str(status_code)+" "+error_id
            
            exc_info = kwargs["exc_info"]
            trace_info = ''.join(["%s</br>" % tornado.escape.xhtml_escape(line) for line in traceback.format_exception(*exc_info)])
            
            error_name = ""
            
            for line in traceback.format_exception(*exc_info):
                if line == traceback.format_exception(*exc_info)[-1]:
                    error_name = line.split(" ")[0] 
            
            error_name = error_name.split(":")[0]
            
            self._blog.tags = splitTags(error_name)
            
            self._blog.conteudo = u"<p>Reportado erro "+ str(status_code) \
                                + u"</br>\nUsuário: " + user \
                                + u"</br>\nPágina requisitada: " + str(self.request.uri) \
                                + u"</br>\nHorário do erro: " + error_time \
                                + u"</br></br>\n\n"+ trace_info + u"</p>"
                                 
            self._blog.registry_id = PRIV_GLOBAL_ADMIN
            self._blog.data_cri = str(datetime.now())
            self._blog.data_alt = self._blog.data_cri
            self._blog.owner = USER_ADMIN
            doc_id = PRIV_GLOBAL_ADMIN+"/"+error_id
            
            for tag in self._blog.tags:
                addTag(tag, PRIV_GLOBAL_ADMIN, USER_ADMIN, "blog", doc_id, self._blog.titulo, error_time)
            
            historico_inicial = dict()
            historico_inicial["data_alt"] = self._blog.data_alt
            historico_inicial["alterado_por"] = USER_ADMIN
            historico_inicial["conteudo"] = self._blog.conteudo
            
            self._blog.historico.append(historico_inicial)
            
            self._blog.save(id=doc_id)
            
            if EMAIL_ERROR_NOTIFY != "":
                Notify.enviaEmail(EMAIL_ERROR_NOTIFY, u"Notificação de erro na aplicação "+PLATAFORMA, "", self._blog.conteudo, "blog/"+doc_id)

            msg = ""
            if status_code == 400:
                # Bad Request
                msg = u"Oops! Chamada inválida"
            elif status_code == 500:
                # Internal Server Error
                msg = u"Oops! Ocorreu um erro inesperado e não foi possível atender a sua solicitação. Nossa equipe de desenvolvimento já foi notificada e tentará solucioná-lo o mais rápido possível."
            elif status_code == 503:
                # Service unavailable
                msg = u"Oops! Não foi possível atender a sua solicitação neste momento. Tente novamente em alguns instantes."

            img_src = "/static/error/internalerror.png"
            self.render("modules/error/template-error.html", NOMEPAG="", LINKS="", REGISTRY_ID=user, MSG=msg, STATUS_CODE=str(status_code), IMG_SRC=img_src)
            
        else:
            super(BaseHandler,self).write_error(status_code)   
   
            
# -----------------------------------------------------------------------------
# Controladores deste módulo

class MainHandler(BaseHandler):
    ''' Redireciona para a página inicial. Artifício para que o nginx possa usar SSL no login da tela de entrada. '''

    def get(self):
        query_string = self.request.query
        url = "/homepage"
        if query_string:
            url += "?" + query_string
        self.redirect(url)


class HomePageHandler(BaseHandler):
    ''' Página inicial do ActivUFRJ '''

    def get(self):
        next = self.get_argument("next", "")
        msg = u"Você precisa estar autenticado para acessar este conteúdo" if next else ""
        self.render(self.searchEntryPoint(), MSG=msg, NEXT=next)


class LoginHandler(BaseHandler):
    ''' Autenticação de usuários redirecionando para o painel de controle do usuário '''
    
    def get(self):
        next = self.get_argument("next", "")
        user = self.get_current_user()
        if user:
            url_home = ("/user/%s" % user, next)[next!=""]
            self.redirect (url_home)
        else:
            self.render("modules/core/login-form.html", NEXT=next, MSG="", \
                        NOMEPAG="")

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
                    self.set_secure_cookie("show_tutorial", _user.getShowTutorial())
                    self.set_secure_cookie("services", ":".join(_user.getServices))
                else:
                    self.set_secure_cookie("user", user, None)
                    self.set_secure_cookie("nome", _user.name.encode('utf-8'), None)
                    self.set_secure_cookie("show_tutorial", _user.getShowTutorial())
                    self.set_secure_cookie("services", ":".join(_user.getServices))
                self.clear_cookie("navigation")
                    
                log.model.log(user, u'entrou no '+PLATAFORMA, news=False)
                self.redirect(url_home)
            else:
                self.render(url_erro, NEXT=next, MSG=u"Senha incorreta ou usuário inexistente.", \
                        NOMEPAG="")
        else:
            self.render(url_erro, NEXT=next, MSG="Senha ou usuário não especificados.", \
                        NOMEPAG="")


class LogoutHandler(BaseHandler):
    ''' Encerra uma sessão '''
    
    def get(self):
        user = self.get_current_user()
        
        if user in model.USUARIOS_LOGADOS:
            del model.USUARIOS_LOGADOS[user]
        
        #self.clear_all_cookies()
        self.clear_cookie("user")
        self.clear_cookie("nome")
        self.clear_cookie("navigation")
        log.model.log(user, u'saiu do '+PLATAFORMA, news=False)
        self.redirect("/")


class LoginIntranetHandler(BaseHandler):
    ''' Autenticação de usuários através da Intranet da UFRJ redirecionando para o painel de controle do usuário '''

    def get(self):
        idUFRJ   = self.get_argument("idufrj", "")
        idSessao = self.get_argument("idSessao", "")  
        if idUFRJ=="" or idSessao=="":
            self.render(self.searchEntryPoint(), NEXT="", MSG=u"Chamada inválida.", \
                        NOMEPAG="cadastro")
            return
            
        # verifica se a sessão é válida
        dbinfo = _EMPTYDBINTRANET()
        dbinfo.update(database.DBINTRANET["intranet"])
        
        try:
            conn = pymssql.connect(host=dbinfo["host"], user=dbinfo["user"], password=dbinfo["passwd"], database=dbinfo["database"])
        except Exception as e:
            self.render(self.searchEntryPoint(), NEXT="", MSG=u"Erro na conexão ao servidor de BD da Intranet.", \
                        NOMEPAG="cadastro")
            return
            
        cur = conn.cursor()
        cur.execute('''SELECT P.nome, P.email FROM UsuariosLogados U
                       JOIN Intranet_Pessoa P ON U.identificacaoUFRJ = P.identificacaoUFRJ
                       WHERE U.identificacaoUFRJ=%s AND U.SessionID=%s''', (idUFRJ, idSessao))
        
        row = cur.fetchone()
        if not row:
            self.render(self.searchEntryPoint(), NEXT="", MSG=u"Autenticação da intranet não reconhecida.", \
                        NOMEPAG="cadastro")
            return

        # obtém nome e email do usuário
        # estava dando erro 500 quando o nome na intranet tem acento.
        # verificar se decode('iso-8859-1') resolveu.
        nomeIntranet = row[0].decode('iso-8859-1')
        email = row[1]
        
        # verifica se o CPF autenticado existe no registry
        userlist = model.usersByCPF(idUFRJ)
        
        if userlist:
            user = userlist[0]    # Pega o primeiro. E se existir mais de um ???????
            
            # usuário autenticado
            self.set_secure_cookie("user", user, None)
            self.set_secure_cookie("nome", database.REGISTRY[user]["name"].encode('utf-8'), None) # 
            
            log.model.log(user, u'entrou no '+PLATAFORMA+' pela IntranetUFRJ', news=False)
            self.redirect("/user/%s" % user)

        else:
            if not email:
                msg = u"Não é possível acessar o ActivUFRJ pois você não tem email cadastrado na Intranet. " + \
                      u"Para cadastrar um email agora, <a href='https://intranet.ufrj.br/utilidades2006/aEmailF.asp'>clique aqui</a>."
                self.render("home.html", MSG=msg, \
                            NOMEPAG="cadastro")  
                return                  
                
                
            # verifica se o email existe no registry
            userlist = model.usersByEmail(email)
            if userlist:
                user = userlist[0]  # Pega o primeiro. E se existir mais de um ???????

                # usuário autenticado
                self.set_secure_cookie("user", user, None)
                self.set_secure_cookie("nome", database.REGISTRY[user]["name"].encode('utf-8'), None)
                
                # armazena o cpf no registry
                user_data = model.Registry().retrieve(user)
                user_data.cpf = idUFRJ
                user_data.save()

                log.model.log(user, u'entrou no '+PLATAFORMA+' pela IntranetUFRJ', news=False)
                self.redirect("/user/%s" % user)
    
            else:
                # 1o acesso: cpf e email do usuário autenticado na intranet não existem no registry
                # exibe um formulário de cadastro no Activ
                
                registry_data = model.Member()
                nomes = nomeIntranet.split()
                registry_data.name = nomes[0]
                registry_data.lastname = ' '.join(nomes[1:])
                
                #registry_data.name = ""
                #registry_data.lastname = ""
                registry_data.cpf = idUFRJ
                registry_data.email = email
                registry_data.user = ""
                registry_data.passwd = ""
                registry_data.vinculos = []

                # verifica se é professor ou tec_adm para atribuir o privilégio de criar comunidades
                # busca as informacoes para prencher a lista de vinculos - agora temos que testar todos os vinculos

                criar_comunidades = "N"
                
                # É professor ?
                cur = conn.cursor()
                
                cur.execute('''SELECT IdentificacaoUFRJ, MatriculaSiape, Ativo, DescricaoLocal, Email FROM View_eh_professor
                               WHERE IdentificacaoUFRJ=%s''', idUFRJ)
                row = cur.fetchone()
                if row:
                    criar_comunidades = "S"
                while row:
                    registry_data.vinculos.append({"vinculo":"P", \
                                                   "instituicao":"UFRJ", \
                                                   "cpfufrj":row[0], \
                                                   "emailufrj": row[4], \
                                                   "ativo": row[2], \
                                                   "siape": row[1], \
                                                   "localizacao": row[3].strip().decode('iso-8859-1')})
                    row = cur.fetchone()
                cur.close()
                     
                # É (tambem) funcionario ?
                cur = conn.cursor()
                cur.execute('''SELECT IdentificacaoUFRJ, MatriculaSiape, Ativo, DescricaoLocal, Email FROM View_eh_tec_adm 
                               WHERE IdentificacaoUFRJ=%s''', idUFRJ)
                row = cur.fetchone()
                if row:
                    criar_comunidades = "S"
                while row:              
                    registry_data.vinculos.append({"vinculo":"F", \
                                                   "instituicao":"UFRJ", \
                                                   "cpfufrj":row[0], \
                                                   "emailufrj": row[4], \
                                                   "siape": row[1], \
                                                   "ativo": row[2], \
                                                   "localizacao": row[3].strip().decode('iso-8859-1')})
                    row = cur.fetchone()
                cur.close()
                
                # É (tambem) aluno de graduação ?
                cur = conn.cursor()
                cur.execute('''SELECT IdentificacaoUFRJ, registroSIRA, ativo, nome, Email FROM view_eh_aluno_grad
                               WHERE IdentificacaoUFRJ=%s''', idUFRJ)                
                row = cur.fetchone()
                while row:
                    registry_data.vinculos.append({"vinculo":"A", \
                                                   "instituicao":"UFRJ", \
                                                   "tipo": "Grad", \
                                                   "cpfufrj":row[0], \
                                                   "emailufrj": row[4], \
                                                   "dre": row[1], \
                                                   "ativo": row[2], \
                                                   "curso": row[3].strip().decode('iso-8859-1')})
                    row = cur.fetchone()
                cur.close()   
                
                # É (tambem) aluno de pós-graduação ?
                cur = conn.cursor()
                cur.execute('''SELECT IdentificacaoUFRJ, registroSIRA, ativo, nome, Email FROM view_eh_aluno_pos
                               WHERE IdentificacaoUFRJ=%s''', idUFRJ)
                row = cur.fetchone()
                while row:
                    registry_data["vinculos"].append({"vinculo":"A", \
                                                      "instituicao":"UFRJ", \
                                                      "tipo": "Pos", \
                                                      "cpfufrj":row[0], \
                                                      "emailufrj": row[4], \
                                                      "dre": row[1], \
                                                      "ativo": row[2], \
                                                      "curso": row[3].strip().decode('iso-8859-1')})
                    row = cur.fetchone()
                cur.close()
                                          
                self.render("modules/member/intranet-form.html", REGISTRYDATA=registry_data, MSG="", \
                            NOMEPAG="cadastro", CRIARCOMUNIDADES=criar_comunidades)                    
        
        
class ShutdownHandler(BaseHandler):
    ''' Força o salvamento do log para que a aplicação possa ser finalizada '''
    @tornado.web.authenticated
    @model.userIsCommunityMember (PRIV_GLOBAL_ADMIN)
    def get(self):
        user = self.get_current_user()
        log.model.saveLog()
        
        # Persiste dados do chat
        chat.model.REDIS.save()

        self.render("home.html", MSG=u"Aplicação finalizada. Agora o processo pode ser parado com segurança.", REGISTRY_ID=PRIV_GLOBAL_ADMIN, \
                        NOMEPAG="")


class UserHandler(BaseHandler):
    ''' Lista tela principal de um usuário '''
    @tornado.web.authenticated
    @model.allowedToAccess
    def get (self,user_id):
        user = self.get_current_user()
        if user == user_id or "wiki" not in database.REGISTRY[user_id]['services']:
            self.redirect ("/profile/%s" % user_id)
        else:
            self.redirect ("/wiki/%s/home" % user_id)


class RegistryUserHandler(BaseHandler):
    ''' Cadastro de novo usuário do Activ '''
        
    def get(self):
        mkey = self.get_argument("mkey", "")
        # verifica se a mkey é válida
        if mkey and (mkey not in invites.model.MAGKEYS):
            self.render("home.html", MSG=u"Convite inexistente ou expirado.<br/>", \
                        NOMEPAG="")
        else:
            # Redireciona para formulário de cadastro de usuários
            registry_data = _EMPTYMEMBER()
            if mkey and "nome" in invites.model.MAGKEYS[mkey]:
                    nomes = invites.model.MAGKEYS[mkey]["nome"].split()
                    registry_data["name"] = nomes[0]
                    registry_data["lastname"] = ' '.join(nomes[1:])
            self.render("modules/member/profile-form.html", REGISTRYDATA=registry_data, MSG="", \
                        MKEY=mkey, INPUT_MKEY=not mkey, EMAIL=invites.model.MAGKEYS[mkey]["email"] if mkey else "", \
                        NOMEPAG="")

    def post(self):

        user_data = _EMPTYMEMBER()
        msg = ""
        erros = 0

        for key in _EMPTYMEMBERFORM:
            if self.get_argument(key, "") != "" :
                if key == "passwd":
                    passwd = self.get_argument(key)
                    if  len(passwd) < TAMMINPWD:
                        msg += u"Senha deve ter no mínimo %s caracteres.<br/>" % (TAMMINPWD)
                    elif has_diacritics(passwd):
                        msg += u"Senha não deve conter caracteres acentuados.<br/>"                        
                    else:
                        if passwd != self.get_argument("npasswd", ""):
                            msg += u"Senha diferente da confirmação!<br/>"
                elif key == "user":
                    if self.get_argument(key) in RESERVED_WORDS:
                        msg += u"Login inválido."
                    elif self.get_argument(key).isdigit():
                        msg += u"Login não pode ser composto somente de números. Escolha um nome pelo qual você será identificado na plataforma."
                    else:
                        p = re.compile(VALID_LOGIN)
                        if p.match(self.get_argument(key)):
                            user_data[key] = self.get_argument(key)
                        else:
                            msg += u"Login inválido. Deve ter no mínimo 3 caracteres, começando e terminando com letras ou números e utilizando apenas letras, números, '_' e '.' em sua composição. Não utilize acentuação!<br/>"
                            
                elif key in _EMPTYMEMBER():
                    user_data[key] = self.get_argument(key)
            elif key != "mkey" or self.get_argument("origin", "") != "intranet":
                    erros += 1

        if erros > 0:
            msg += u"Há %d campos obrigatórios não preenchidos!<br/>" % erros

        user = user_data["user"]
        if user and model.registryIdExists(user):
            msg += u"Login já existe.<br/>"
        
        
        mkey = self.get_argument("mkey", "")
        origin = self.get_argument("origin", "convidado")
        # Trouxe esta chamada para este local pois precisamos ter se houver msg 
        criar_comunidades = self.get_argument("criar_comunidades", "N")  
        if mkey:
            if mkey not in invites.model.MAGKEYS:
                msg += u"Chave mágica incorreta ou expirada.<br/>Se você já se cadastrou anteriormente, <a href='/'>clique aqui</a>.<br/>"
            elif user_data["email"] and user_data["email"] != invites.model.MAGKEYS[mkey]["email"]:
                msg += u"E-mail não corresponde a chave.<br/>"
            
        if user_data["email"] and emailExists(user_data["email"]):
            msg += u"O email %s já está cadastrado na plataforma. <a href='/forgotpasswd'>Clique aqui para recuperar a sua senha</a>.<br/>" % user_data["email"]

        user_data["cpf"] = self.get_argument("cpf", "")
        
        #Pegando o vinculo oriundo do intranet-form. Caso não seja do intranet form, o vinculo sera umalista vazia
        if origin == 'intranet':
            vinculos=self.get_argument("vinculos")            
            user_data["vinculos"] = vinculos and json_decode(vinculos.replace("'",'"'))
        else:
            user_data["vinculos"] = []
            
        if msg:
            user_data["passwd"] = user_data["npasswd"] = ""
            if origin == "intranet":
                self.render("modules/member/intranet-form.html", REGISTRYDATA=user_data, MSG=msg, \
                        NOMEPAG="", CRIARCOMUNIDADES=criar_comunidades)
            else:
                self.render("modules/member/profile-form.html", REGISTRYDATA=user_data, MSG=msg, \
                        MKEY=mkey, INPUT_MKEY=self.get_argument("input_mkey", "")=="True", EMAIL=user_data["email"], \
                        NOMEPAG="")
        else:
            # gera a senha criptografada
            hash = hashlib.md5()
            hash.update(user+passwd)
            user_data["passwd"] = hash.hexdigest()
            
            # privacidade default de todos os usuários
            user_data["privacidade"] = u"Pública"
            
            user_data["origin"] = origin
            user_data["data_cri"] = str(datetime.now())
            user_data["data_alt"] = user_data["data_cri"]

            user_data["services"] = ["wiki", "mblog", "file"]
            
            
            # atribui privilegio de criar comunidades para professores e tec_adm da UFRJ
            # A variavel criar_comunidades ja esta sendo associada la em cima
            #criar_comunidades = self.get_argument("criar_comunidades", "N")
            if criar_comunidades=="S":
                priv = "Priv_Criar_Comunidades"

                if priv not in user_data["comunidades"]:
                    user_data["comunidades"].append(priv)
            
                community_data = _EMPTYCOMMUNITY()
                community_data.update(database.REGISTRY[priv])
                if user not in community_data["participantes"]:
                    community_data["participantes"].append(user)
                    database.REGISTRY[priv] = community_data
                    
            # Inserindo usuario automaticamente na COMUNIDADE_BEMVINDO
            """
            user_data["comunidades"].append(COMUNIDADE_BEMVINDO)
            community_data = _EMPTYCOMMUNITY()
            community_data.update(database.REGISTRY[COMUNIDADE_BEMVINDO])
            if user not in community_data["participantes"]:
                community_data["participantes"].append(user)
                database.REGISTRY[COMUNIDADE_BEMVINDO] = community_data
            """
                        
            # trata os atributos da chave utilizada no cadastro
            if mkey and mkey in invites.model.MAGKEYS:
                
                # copia todos os outros parâmetros de MAGKEYS para o REGISTRY
                # exceto magic, user e comunidades
                key_data = invites.model.MAGKEYS[mkey]
                
                for param in key_data:
                    if param not in ["_rev", "_id", "magic", "user", "comunidades"]:
                        user_data[param] = key_data[param]
             
                # inclui o usuário nas suas comunidades default
                if "comunidades" in invites.model.MAGKEYS[mkey]:
                    for comu in invites.model.MAGKEYS[mkey]["comunidades"]:
                        if isACommunity(comu):
                            comu_data = _EMPTYCOMMUNITY()
                            user_data["comunidades"].append(comu)
                            
                            comu_data.update(database.REGISTRY[comu])
                            comu_data["participantes"].append(user)
                            
                            database.REGISTRY[comu] = comu_data

            # verifica se há algum convite para esse email pendente em usuarios_chamados de alguma comunidade
            for (email, community_id, participacao) in model.Community.getCalledCommunities(user_data["email"]):
                if participacao == "Mediante Convite":
                    user_data["comunidades_pendentes"].append(community_id)
                    
                    comu_data = _EMPTYCOMMUNITY()
                    comu_data.update(database.REGISTRY[community_id])
                    comu_data["participantes_pendentes"].append(user)
                    database.REGISTRY[community_id] = comu_data
                    
                elif participacao == u"Obrigatória":
                    user_data["comunidades"].append(community_id)

                    comu_data = _EMPTYCOMMUNITY()
                    comu_data.update(database.REGISTRY[community_id])
                    comu_data["participantes"].append(user)
                    database.REGISTRY[community_id] = comu_data
            
            
            if self.request.files:
                # usuário tem foto

                # este split é para resolver o problema do IE, que manda o caminho completo.
                #user_data["photo"] = self.request.files["photo"][0]["filename"].split("\\")[-1]
                #user_data["photo"] = remove_diacritics(user_data["photo"])

                # cria os thumbnails da foto
                thumb_g = thumbnail(self.request.files["photo"][0]["body"], "G")
                if not thumb_g:
                    self.render("home.html", MSG=u"Não foi possível ler o arquivo com a foto", \
                        NOMEPAG="")
                    return
              
                thumb_m = thumbnail(self.request.files["photo"][0]["body"], "M")
                if not thumb_m:
                    self.render("home.html", MSG=u"Não foi possível ler o arquivo com a foto", \
                        NOMEPAG="")
                    return

                thumb_p = thumbnail(self.request.files["photo"][0]["body"], "P")
                if not thumb_p:
                    self.render("home.html", MSG=u"Não foi possível ler o arquivo com a foto", \
                        NOMEPAG="")
                    return
              
              
                try:
                    database.REGISTRY[user] = user_data

                    database.REGISTRY.put_attachment(database.REGISTRY[user],
                           thumb_g, "thumbG.png", "image/png")
                    database.REGISTRY.put_attachment(database.REGISTRY[user],
                           thumb_m, "thumbM.png", "image/png")
                    database.REGISTRY.put_attachment(database.REGISTRY[user],
                           thumb_p, "thumbP.png", "image/png")
                   
                except Exception as detail:
                    if database.REGISTRY[user]:
                        del database.REGISTRY[user]
                    self.render("home.html", MSG=u"Erro: %s" % detail, \
                        NOMEPAG="")
                    return
            else:
                # usuário não tem foto
                try:
                   database.REGISTRY[user] = user_data
                except Exception as detail:
                    self.render("home.html", MSG=u"Erro: %s" % detail, \
                        NOMEPAG="")
                    return
            
            if mkey and mkey in invites.model.MAGKEYS:
                # Guarda log com informações do convite
                quem_convidou = invites.model.MAGKEYS[mkey]["user"]
    
                invite_data = _EMPTYINVITES()
                invite_data["convidado_por"] = quem_convidou
                invite_data["mkey"] = mkey
                invites.model.INVITES[user] = invite_data
                
                invite_data = _EMPTYINVITES()
                if quem_convidou in invites.model.INVITES:
                    invite_data.update(invites.model.INVITES[quem_convidou])
                invite_data["usuarios_convidados"].append (user)
                invites.model.INVITES[quem_convidou] = invite_data
                
                # remove chave usada para este cadastro da lista do usuário que convidou
                invitor = invites.model.MAGKEYS[mkey]["user"]
                if invitor in database.REGISTRY:
                    invitor_data = _EMPTYMEMBER()
                    invitor_data.update(database.REGISTRY[invitor])
                    if mkey in invitor_data["mykeys"]:
                        invitor_data["mykeys"].remove(mkey)
                        database.REGISTRY[invitor] = invitor_data
                    
                # remove a chave do documento MAGKEYS
                del invites.model.MAGKEYS[mkey]

            # cria páginas home e indice do usuário
            #cria_pagina("home", user, user)
            #cria_pagina("indice", user, user)
            self._wiki = wiki.model.Wiki().retrieve(user+"/home")
            if not self._wiki: wiki.model.Wiki().createInitialPage("home", user, user)

            self._wiki = wiki.model.Wiki().retrieve(user+"/indice")
            if not self._wiki: wiki.model.Wiki().createInitialPage("indice", user, user)

            if origin == "intranet":
                log.model.log(user, u'cadastrou-se no '+PLATAFORMA+' pela IntranetUFRJ', news=False)
            else:
                log.model.log(user, u'cadastrou-se no '+PLATAFORMA, news=False)
            
            self.render(self.searchEntryPoint(), MSG=u"Cadastro criado com sucesso.", NEXT="", \
                        NOMEPAG="")


class RegistryCommunityHandler(BaseHandler):
    ''' Criação de nova comunidade '''
    
    @tornado.web.authenticated
    @model.userIsCommunityMember (PRIV_CRIAR_COMUNIDADES)
    def get(self):
        user = self.get_current_user()
        self.render("modules/community/newcommunity-form.html", NOMEPAG="comunidades", \
                    IS_ADMIN= isMember(user, PRIV_GLOBAL_ADMIN),\
                    REGISTRY_ID=user, REGISTRYDATA=_EMPTYCOMMUNITY(), TAGS=formatTags, MSG="")

    @tornado.web.authenticated
    @model.userIsCommunityMember (PRIV_CRIAR_COMUNIDADES)
    def post(self):
        user = self.get_current_user()
        community_data = _EMPTYCOMMUNITY()
        msg = u""
        erros = 0

        for key in _EMPTYCOMMUNITYFORM:
            if self.get_argument(key, "") != "" :
                if key in _EMPTYCOMMUNITY():
                    community_data[key] = self.get_argument(key)
                    if key == "name":
                        if self.get_argument(key) in RESERVED_WORDS:
                            msg += u"Nome inválido."
                        else:
                            p = re.compile(VALID_LOGIN)
                            if not p.match(self.get_argument(key)):
                                msg += u"Nome inválido. Deve ter no mínimo 3 caracteres, começando e terminando com letras ou números e utilizando apenas letras, números, '_' e '.' em sua composição. Não utilize acentuação!<br/>"                  
            else:
                erros += 1
    
        if erros > 0:
            msg += u"Há %d campos obrigatórios não preenchidos.<br/>" % erros
            
        community_data["owner"] = user
        name = community_data["name"]
        
        if name and model.registryIdExists(name):
            msg += u"Já existe um usuário ou comunidade com este nome.<br/>"
        if community_data['participacao'] == u"Obrigatória" and not isMember(user, PRIV_GLOBAL_ADMIN):
            msg += u"Você não tem permissão para criar comunidades obrigatórias.<br/>"
        
        community_data["tags"] = splitTags(self.get_argument("tags",""))
        
        
        if msg:
            self.render("modules/community/newcommunity-form.html", NOMEPAG="comunidades", \
                        IS_ADMIN=isMember(user, PRIV_GLOBAL_ADMIN), \
                        REGISTRY_ID=user, REGISTRYDATA=community_data, TAGS=formatTags, MSG=msg)
        else:
            user_data = _EMPTYMEMBER()
            user_data.update(database.REGISTRY[user])
            user_data['comunidades'].append(name)
            database.REGISTRY[user] = user_data

            community_data["services"] = ["wiki", "mblog", "file"]
            community_data["participantes"].append(user) 
            community_data["data_cri"] = str(datetime.now())
            community_data["data_alt"] = community_data["data_cri"]
            database.REGISTRY[name] = community_data

            if self.request.files:
                if "photo" in self.request.files:
                    # comunidade tem foto
                    
                    # este split é para resolver o problema do IE, que manda o caminho completo.
                    #community_data["photo"] = self.request.files["photo"][0]["filename"].split("\\")[-1]
                    #community_data["photo"] = remove_diacritics(community_data["photo"])
    
                    # cria os thumbnails da foto
                    thumb_g = thumbnail(self.request.files["photo"][0]["body"], "G")
                    if not thumb_g:
                        self.render("home.html", MSG=u"Não foi possível ler o arquivo com a foto", \
                            NOMEPAG="comunidades")
                        return
                  
                    thumb_m = thumbnail(self.request.files["photo"][0]["body"], "M")
                    if not thumb_m:
                        self.render("home.html", MSG=u"Não foi possível ler o arquivo com a foto", \
                            NOMEPAG="comunidades")
                        return
    
                    thumb_p = thumbnail(self.request.files["photo"][0]["body"], "P")
                    if not thumb_p:
                        self.render("home.html", MSG=u"Não foi possível ler o arquivo com a foto", \
                            NOMEPAG="comunidades")
                        return

                    try:
                        database.REGISTRY.put_attachment(database.REGISTRY[name],
                               thumb_g, "thumbG.png", "image/png")
                        database.REGISTRY.put_attachment(database.REGISTRY[name],
                               thumb_m, "thumbM.png", "image/png")
                        database.REGISTRY.put_attachment(database.REGISTRY[name],
                               thumb_p, "thumbP.png", "image/png")
                    except Exception as detail:
                        if database.REGISTRY[name]:
                            del database.REGISTRY[name]
                        self.render("home.html", MSG=u"Erro: %s" % detail, \
                            NOMEPAG="comunidades")
                        return
                    
                if "arquivo_css" in self.request.files:
                    # comunidade tem css
                    
                    try:
                        database.REGISTRY.put_attachment(database.REGISTRY[name],
                               self.request.files["arquivo_css"][0]["body"], "arquivo_css.css", "text/css")
                    except Exception as detail:
                        if database.REGISTRY[name]:
                            del database.REGISTRY[name]
                        self.render("home.html", MSG=u"Erro: %s" % detail, \
                            NOMEPAG="comunidades")
                        return
                
            # Acrescenta as tags da comunidade em SEARCHTAGS
            data_tag = str(datetime.now())
            for tag in community_data["tags"]:
                addTag(tag, name, user, "community", name, community_data["description"], data_tag)

            # cria páginas home e indice da comunidade
            #cria_pagina("home", community_data["name"], user)
            #cria_pagina("indice", community_data["name"], user)
            self._wiki = wiki.model.Wiki().retrieve(community_data["name"]+"/home")
            if not self._wiki: wiki.model.Wiki().createInitialPage("home", community_data["name"], user)

            self._wiki = wiki.model.Wiki().retrieve(community_data["name"]+"/indice")
            if not self._wiki: wiki.model.Wiki().createInitialPage("indice", community_data["name"], user)
            
            log.model.log(user, u'criou a comunidade', objeto=community_data["name"], tipo="community")
            self.redirect("/community/%s" % community_data["name"])


class ChangePasswdHandler(BaseHandler):
    ''' Alteração da senha do usuário '''
    
    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        user_data = database.REGISTRY[user]
        tabs = []
        tabs.append(("Editar Perfil", "/profile/edit"))
        tabs.append(("Alterar Senha", ""))
        tabs.append(("Formação e Experiências", "/profile/skills/new/experience"))
        tabs.append(("Produção Acadêmica - Lattes", "/profile/skills/productions"))
        tabs.append(("Habilidades", "/profile/skills/"+user))
        
        self.render("modules/member/change-passwd.html", REGISTRY_ID=user, MSG="", \
                    TABS=tabs, \
                    NOMEPAG="perfil")

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

        tabs = []
        tabs.append(("Editar Perfil", "/profile/edit"))
        tabs.append(("Alterar Senha", ""))
        tabs.append(("Formação e Experiências", "/profile/skills/new/experience"))
        tabs.append(("Produção Acadêmica - Lattes", "/profile/skills/productions"))
        tabs.append(("Habilidades", "/profile/skills/"+user))
        if msg:            
            self.render("modules/member/change-passwd.html", REGISTRY_ID=user, MSG=msg, \
                    TABS=tabs, \
                    NOMEPAG="perfil")
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

            log.model.log(user, u'trocou sua senha no '+PLATAFORMA, news=False)                                
            self.render("modules/member/change-passwd.html", REGISTRY_ID=user, MSG=u"Senha alterada com sucesso!", \
                    TABS=tabs, \
                    NOMEPAG="perfil")


class AboutHandler(BaseHandler):
    ''' Sobre o ActivUFRJ '''

    def get(self):
        self.render("modules/member/about.html", NOMEPAG="")
        
        
class ForgotPasswdHandler(BaseHandler):
    ''' Reinicialização da senha do usuário '''
   
    def enviaLembrete(self, email, nome, user, activate_id, ip):
        
        assunto = u"Pedido de alteração de senha no %s" % PLATAFORMA
        msgTxt =  u"""
        Um pedido de alteração da senha de acesso do usuário %s no %s foi realizado a partir do IP %s.
        Caso você não tenha feito esta solicitação, por favor, desconsidere esta mensagem.
        Para completar esta operação e alterar sua senha, clique no link abaixo: \n
        https://%s/changeforgotpasswd?id=%s""" % \
        (user, PLATAFORMA, ip, PLATAFORMA_URL, activate_id)
    
        if Notify.enviaEmail (email, assunto, nome, msgTxt, ""):
           return u"<br/>Foi enviado um email para %s com instruções para continuar esta operação." % email
        else:
           return u"<br/>Erro no envio do email."
   
    def get(self):
        self.render("modules/member/forgot-passwd.html", MSG="", \
                        NOMEPAG="")

    def post(self):
        user = self.get_argument("user", "")
        msg = ""

        if user == "":
            msg = u"Especifique o seu login!<br/>"
            self.render("modules/member/forgot-passwd.html", REGISTRY_ID=user, MSG=msg, \
                        NOMEPAG="")
            return
            
        else:
            _user = model.Registry().retrieve(user)
            if not _user:
                email = user
                user_list = usersByEmail(email)
                if not user_list:
                    msg = u"Usuário não encontrado!<br/>"
                    self.render("modules/member/forgot-passwd.html", MSG=msg, \
                                NOMEPAG="")
                    return
                
                elif len(user_list) > 1:
                    # Existe mais de um usuário com este email
                    # Exibe formulário para que seja selecionado o usuário correto. 
                    self.render("modules/member/forgot-passwd.html", MSG="", USERLIST=user_list, \
                                NOMEPAG="")
                    return

                else:
                    #Existe um único usuário com este email
                    user=user_list[0]
                    _user = model.Registry().retrieve(user)

        if _user.getType()!="member":
            msg = u"Este login não corresponde a um usuário válido!<br/>"
            self.render("modules/member/forgot-passwd.html", REGISTRY_ID=user, MSG=msg, \
                        NOMEPAG="")
            
        else:
            #Gerar o activate_id
            activate_id = uuid4().hex
            
            #Gravar o documento no banco
            self._forgottenpasswd = model.ForgottenPasswd()
            self._forgottenpasswd.data_pedido = str(datetime.now())
            self._forgottenpasswd.user = user
            #self._forgottenpasswd.ip = self.request.remote_ip
            
            # Pega o IP que fez a requisição através do NGINX
            self._forgottenpasswd.ip = self.request.headers.get('X-Forwarded-For', self.request.headers.get('X-Real-Ip', self.request.remote_ip))
            
            self._forgottenpasswd.save(id=activate_id)

            # Envio de e-mail
            msg += self.enviaLembrete(_user.email, _user.name, user, activate_id, self._forgottenpasswd.ip)

            log.model.log(user, u'solicitou alteração de sua senha no '+PLATAFORMA, news=False)                                
            self.render("modules/member/forgot-passwd.html", MSG=msg, \
                        NOMEPAG="")

class ChangeForgotPasswdHandler(BaseHandler):
    ''' Alteração da senha do usuário '''
    
    #  @tornado.web.authenticated
    def get(self):
        TEMPO_EXPIRACAO = 2
        activate_id = self.get_argument("id", "")
        if activate_id == "":
            self.render(self.searchEntryPoint(), MSG= u"Pedido de alteração de senha inválido (id não especificado).<br/>", \
                            NEXT="", NOMEPAG="")
            return
                    
        self._forgot = model.ForgottenPasswd().retrieve(activate_id)
        
        if self._forgot:
            user = self._forgot.user
            
            if self._forgot.data_execucao == "":
            
                if elapsed_time(self._forgot.data_pedido).days <= TEMPO_EXPIRACAO:  
                    self.render("modules/member/changeforgot-passwd.html", REGISTRY_ID=user, ACTIVATE_ID=activate_id, MSG="", \
                            NOMEPAG="")
        
                else:
                    #pedido de alteração de senha expirado
                    self.render(self.searchEntryPoint(), MSG= u"Pedido de alteração de senha expirado<br/>", \
                            NEXT="", NOMEPAG="")
            else:                
                #pedido de alteração de senha já executado
                msg = u"Pedido de alteração de senha executado anteriormente<br/>Favor realizar nova solicitação<br/>"
                self.render(self.searchEntryPoint(), MSG=msg , \
                        NEXT="", NOMEPAG="")
                
        else:
            #pedido de alteração de senha inexistente
            self.render(self.searchEntryPoint(), MSG= u"Pedido de alteração de senha inexistente<br/>", \
                            NEXT="", NOMEPAG="")
            
    #@tornado.web.authenticated
    def post(self):
        
        user = self.get_argument("name", "")
        newpasswd = self.get_argument("newpasswd", "")
        confpasswd = self.get_argument("confpasswd", "")
        activate_id = self.get_argument("activate_id", "")
        msg = ""
        
        if newpasswd != confpasswd:
            msg = u"Senha diferente da confirmação!<br/>"
        elif  len(newpasswd) < TAMMINPWD:
            msg = u"Senha deve ter no mínimo %s caracteres.<br/>" % (TAMMINPWD)
        elif has_diacritics(newpasswd):
            msg = u"Senha não deve conter caracteres acentuados.<br/>"            
        else:
            user_data = _EMPTYMEMBER()
            user_data.update(database.REGISTRY[user])
                        
            hash = hashlib.md5()
            hash.update(user+newpasswd)
            user_data["passwd"] = hash.hexdigest()
        if msg:
            self.render("modules/member/changeforgot-passwd.html", REGISTRY_ID=user, ACTIVATE_ID=activate_id, MSG=msg, \
                    NOMEPAG="")
        else:
            
            #Gravar a data de execução no banco
            self._forgottenpasswd = model.ForgottenPasswd().retrieve(activate_id)
            self._forgottenpasswd.data_execucao = str(datetime.now())
            
            self._forgottenpasswd.save(id=activate_id)
            
            database.REGISTRY[user] = user_data

            log.model.log(user, u'confirmou a alteração de sua senha no '+PLATAFORMA, news=False)                                
            self.render(self.searchEntryPoint(), REGISTRY_ID=user, ACTIVATE_ID=activate_id, MSG=u"Senha alterada com sucesso!", \
                    NEXT="", NOMEPAG="")
            

class EditProfileHandler(BaseHandler):
    ''' Edição de perfil do usuário '''
    
    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        user_data = _EMPTYMEMBER()
        user_data.update(database.REGISTRY[user])
        #teste para o loginintranet
        #if "vinculos" not in user_data:
        #    user_data["vinculos"] = []
        #print "vinculos"
        # '\xc1rea de Sistemas de Informa\xe7\xe3o/NCE'
        # A linha abaixo so serve Para testes de inclusao de vinculos
        '''
        user_data["vinculos"]=[{'emailufrj': 'marcia@nce.ufrj.br', 'localizacao': 'Area de Sistemas de Informacao/NCE', \
                                 'siape': '0000000', 'cpfufrj': '11111111111', 'instituicao': 'UFRJ', 'vinculo': 'F', 'ativo': 1},
                                {'emailufrj': 'omarcia@nce.ufrj.br', 'localizacao': 'Area de Sistemas de Informacao/NCE', \
                                 'siape': '0000001', 'cpfufrj': '11111111112', 'instituicao': 'UFRJ','vinculo': 'F', 'ativo': 1}]
    
        
        print user_data["vinculos"]
        '''
       
        tabs = []
        tabs.append(("Editar Perfil", ""))
        tabs.append(("Alterar Senha", "/profile/changepasswd"))
        tabs.append(("Formação e Experiências", "/profile/skills/new/experience"))
        tabs.append(("Produção Acadêmica - Lattes", "/profile/skills/productions"))
        tabs.append(("Habilidades", "/profile/skills/"+user))
        self.render("modules/member/profile-edit.html", REGISTRY_ID=user, FORMDATA=user_data, MSG="", TAGS=formatTags, \
                        TABS=tabs, NOMEPAG="perfil")
        
    @tornado.web.authenticated
    def post(self):
        user = self.get_current_user()
        user_data = _EMPTYMEMBER()
        user_data.update(database.REGISTRY[user])
        msg = ""
        erros = 0
        tabs = []
        tabs.append(("Editar Perfil", ""))
        tabs.append(("Formação e Experiências", "/profile/skills/new/experience"))
        tabs.append(("Habilidades", "/profile/skills/"+user))

        for key in _EDITFORMKEYS:
            if self.get_argument(key, "") != "" :
                if key == "email":
                    if validateEmail(self.get_argument(key)):
                        user_data[key] = self.get_argument(key)
                    else:
                        msg += u"* E-mail inválido.<br/>"
                else:
                    user_data[key] = self.get_argument(key)  
            else:
                erros += 1

        user_data['services'] = [ key for key in SERVICES["member"].keys() if self.get_argument(key, "") != "" ]
       
        if erros > 0:
            msg += u"* Há %d campos obrigatórios não preenchidos!<br/>" % erros

        if msg:
            self.render("modules/member/profile-edit.html", REGISTRY_ID=user, FORMDATA=user_data, MSG=msg, TAGS=formatTags, \
                        TABS=tabs, NOMEPAG="perfil")
        else:
            #user_data["description"] = self.get_argument("description","")
            #user_data["blog_aberto"] = self.get_argument("blog_aberto","N")
            # Deixando estas duas linhas para fazer testes de entrada de vinculos pela intranet
            # so liberar para testes - no metodo get deve ser liberado o dicionario de vinculos
            # E no template profile-edit, deve ser colocada a seguinte linha:
            #<input name="vinculos" id="vinculos" value='{{ json_encode(FORMDATA["vinculos"]) }}' type="hidden" />
            #vinculos=self.get_argument("vinculos")            
            #user_data[vinculos] = vinculos and json_decode(vinculos.replace("'",'"'))
            
            old_tags = database.REGISTRY[user]["tags"]
            user_data["tags"] = splitTags(self.get_argument("tags", ""))
            user_data["data_alt"] = str(datetime.now())

            username = user_data["name"]+' '+user_data["lastname"]
            data_tag = str(datetime.now())
            for tag in user_data["tags"]:
                if tag not in old_tags:
                    addTag(tag, user, user, "user", user, username, data_tag)

            for tag in old_tags:
                if tag not in user_data["tags"]:
                    removeTag(remove_diacritics(tag.lower()), "user", user)
                    
            database.REGISTRY[user] = user_data

            # atualiza cookie para que alteração nos serviços seja refletida no menu imediatamente           
            self.set_secure_cookie("services", ":".join(user_data["services"]))
            
            if self.request.files:
                if "photo" in self.request.files:
                    
                    # cria os thumbnails da foto
                    thumb_g = thumbnail(self.request.files["photo"][0]["body"], "G")
                    if not thumb_g:
                        self.render("home.html", MSG=u"Não foi possível ler o arquivo com a foto", \
                            NOMEPAG="perfil")
                        return
                  
                    thumb_m = thumbnail(self.request.files["photo"][0]["body"], "M")
                    if not thumb_m:
                        self.render("home.html", MSG=u"Não foi possível ler o arquivo com a foto", \
                            NOMEPAG="perfil")
                        return
    
                    thumb_p = thumbnail(self.request.files["photo"][0]["body"], "P")
                    if not thumb_p:
                        self.render("home.html", MSG=u"Não foi possível ler o arquivo com a foto", \
                            NOMEPAG="perfil")
                        return
    
                    try:
                        database.REGISTRY.put_attachment(database.REGISTRY[user],
                               thumb_g, "thumbG.png", "image/png")
                        database.REGISTRY.put_attachment(database.REGISTRY[user],
                               thumb_m, "thumbM.png", "image/png")
                        database.REGISTRY.put_attachment(database.REGISTRY[user],
                               thumb_p, "thumbP.png", "image/png")
                    except Exception as detail:
                        self.render("home.html", MSG=u"Erro: %s" % detail, \
                            NOMEPAG="perfil")
                        return
                    
                if "arquivo_css" in self.request.files:
                    
                    try:
                        database.REGISTRY.put_attachment(database.REGISTRY[user],
                               self.request.files["arquivo_css"][0]["body"], "arquivo_css.css", "text/css")
                    except Exception as detail:
                        self.render("home.html", MSG=u"Erro: %s" % detail, \
                            NOMEPAG="perfil")
                        return
            
            log.model.log(user, u'alterou o seu perfil')
            self.redirect("/profile/%s" % user)
            

class EditCommunityProfileHandler(BaseHandler):
    ''' Edição de perfil de comunidade '''
    
    @tornado.web.authenticated
    def get(self, community_id):
        user = self.get_current_user()
        if isACommunity(community_id):
            if isOwner(user, community_id):
                community_data = _EMPTYCOMMUNITY()
                community_data.update(database.REGISTRY[community_id])
                self.render("modules/community/profile-edit.html", NOMEPAG="comunidades", TAGS=formatTags, \
                              REGISTRY_ID=community_id, COMMUNITYDATA=community_data, MSG="")
            else:
                self.render("home.html", MSG=u"Você não tem permissão para alterar o perfil desta comunidade.", REGISTRY_ID=community_id, \
                            NOMEPAG="comunidades")
        else:
            self.render("home.html", MSG=u"Comunidade não existe.", REGISTRY_ID=user, \
                        NOMEPAG="comunidades")

    @tornado.web.authenticated
    def post(self, community_id):
        
        user = self.get_current_user()
        if isOwner(user, community_id):
            community_data = _EMPTYCOMMUNITY()
            community_data.update(database.REGISTRY[community_id])

            community_data["description"] = self.get_argument("description","")
            #community_data["blog_aberto"] = self.get_argument("blog_aberto","N")

            old_tags = database.REGISTRY[community_id]["tags"]
            community_data["tags"] = splitTags(self.get_argument("tags", ""))
            community_data["data_alt"] = str(datetime.now())

            community_data['services'] = [ key for key in SERVICES["community"].keys() if self.get_argument(key, "") != "" ]
            data_tag = str(datetime.now())
            for tag in community_data["tags"]:
                if tag not in old_tags:
                    addTag(tag, community_id, user, "community", community_id, community_data["description"], data_tag)

            for tag in old_tags:
                if tag not in community_data["tags"]:
                    removeTag(remove_diacritics(tag.lower()), "community", community_id)  

            database.REGISTRY[community_id] = community_data
                
            if self.request.files:
                if "photo" in self.request.files:

                    # old_photo = community_data["photo"]
                    # este split é para resolver o problema do IE, que manda o caminho completo.
                    # community_data["photo"] = self.request.files["photo"][0]["filename"].split("\\")[-1]
                    # community_data["photo"] = remove_diacritics(community_data["photo"])
    
                    # cria os thumbnails da foto
                    thumb_g = thumbnail(self.request.files["photo"][0]["body"], "G")
                    if not thumb_g:
                        self.render("home.html", MSG=u"Não foi possível ler o arquivo com a foto", \
                                NOMEPAG="comunidades")
                        return
                  
                    thumb_m = thumbnail(self.request.files["photo"][0]["body"], "M")
                    if not thumb_m:
                        self.render("home.html", MSG=u"Não foi possível ler o arquivo com a foto", \
                                NOMEPAG="comunidades")
                        return
    
                    thumb_p = thumbnail(self.request.files["photo"][0]["body"], "P")
                    if not thumb_p:
                        self.render("home.html", MSG=u"Não foi possível ler o arquivo com a foto", \
                                NOMEPAG="comunidades")
                        return
    
                    try:
                        database.REGISTRY.put_attachment(database.REGISTRY[community_id],
                               thumb_g, "thumbG.png", "image/png")
                        database.REGISTRY.put_attachment(database.REGISTRY[community_id],
                               thumb_m, "thumbM.png", "image/png")
                        database.REGISTRY.put_attachment(database.REGISTRY[community_id],
                               thumb_p, "thumbP.png", "image/png")
                    except Exception as detail:
                        self.render("home.html", MSG=u"Erro: %s" % detail, \
                                NOMEPAG="comunidades")
                        return   
                    
                if "arquivo_css" in self.request.files:
                    # comunidade tem css
                    
                    try:
                        database.REGISTRY.put_attachment(database.REGISTRY[community_id],
                               self.request.files["arquivo_css"][0]["body"], "arquivo_css.css", "text/css")
                    except Exception as detail:
                        self.render("home.html", MSG=u"Erro: %s" % detail, \
                            NOMEPAG="comunidades")
                        return                    
                
            
            log.model.log(user, u'alterou o perfil da comunidade', objeto=community_id, tipo="community")    
            self.redirect("/profile/%s" % community_id)
            
        else:
            self.render("home.html", MSG=u"Você não tem permissão para alterar o perfil desta comunidade.", REGISTRY_ID=community_id, \
                        NOMEPAG="comunidades")

class ProfileHandler(BaseHandler):
    ''' Lista o perfil de um usuário ou comunidade '''
    @tornado.web.authenticated
    @model.allowedToAccess
    def get(self, registry_id):
        hora_inicio = datetime.now()
        #print "inicio=", hora_inicio
           
        user = self.get_current_user()
        cod_msg = self.get_argument("msg", "")
        list_itens = lambda lista, qtde: lista[:qtde] if lista!=None else None
        num_itens = lambda lista: str(len(lista)) if lista!=None else "0"

        mensagens = {
                     "100": u'Convite para usuário enviado com sucesso!',
                     "101": u'Você não participa mais desta comunidade!',
                     "102": u'Você não tem permissão para convidar usuários para esta comunidade!',
                     "103": u'Usuário já convidado! Aguardando resposta...',
                     "104": u'Usuário já está nesta comunidade!',
                     "105": u'Usuário Inexistente!',
                     "106": u'Não foi possível excluir esta comunidade, pois já existe conteúdo publicado na mesma.',
                     "121": u'Usuário não encontrado.',
                     "122": u'Comunidade não encontrada.',                  
                     "123": u'Tipo de busca incorreto.',
                     "124": u'Termos de busca não preenchidos.',
                     "130": u'Sua Sessão no Google foi encerrada.'
                     }
        msg = ""
        if cod_msg in mensagens: msg = mensagens[cod_msg]
        
        # Instancia o registry_id. 
        # Não precisa testar se ele existe pois o decorator allowedToAccess já verifica isso, dando erro 404 se necessário.
        self._registry = model.Registry().retrieve(registry_id)
        filter = not self._registry.isUserOrMember(user)
        
        if self._registry.isAUser():
            # ---------- usuário
            
            friends = self._registry.getFriendsList(page=1, page_size=QTD_AMIGOS_PAINEL_CONTROLE, user=user)[1]
            communities = self._registry.getCommunitiesList(page=1, page_size=QTD_COMUNIDADES_PAINEL_CONTROLE)
            mblogs = mblog.model.Mblog.listPosts(user, registry_id, 1, QTD_MBLOG_PAINEL_CONTROLE, myself=(user==registry_id)) if "mblog" in self._registry.getServices else None
            news = get_news_list(user) if user == registry_id else get_log_list(registry_id, limit=3, news=True)
            eventos = agenda.model.getNextEvents(registry_id, QTD_EVENTOS_PAINEL_CONTROLE) if "agenda" in self._registry.getServices else None
            tagcloud = cloudTag(registry_id)
            apps = self._registry.getMyApplications() if user==registry_id else []
            skills_to_validate = 0
            skill_type = "other" #valores possíveis: "self", "friend" e "other"
            habilidades = skills.model.Skill.calculaNivelHabilidade(registry_id) #Informações para o widget de gráfico de habilidade
            habilidades.sort(key=lambda x: x['nivel_geral'], reverse=True)
            from skills.control import MIN_HABILIDADES_GRAFICO

            self._scrap = scrapbook.model.Scrapbook().retrieve(registry_id)
            scraps = []
            if self._scrap:
                scraps = self._scrap.getScrapbookList(user, page=1, page_size=QTD_RECADOS_PAINEL_CONTROLE, \
                                                      filter=filter)              
            # obtem lista de noticias do Priv_Global_Admin para saber se precisa exibir moldura vermelha.
            lista_noticias = []
            if user==registry_id:
                noticias = Noticias("Priv_Global_Admin")
                lista_noticias = noticias.get_dict_lista_noticias(popup="S")
                
            links = []
            links.append((u"Página inicial", "fa-home", "/wiki/"+registry_id+"/home"))
            #links.append((u"Gráfico de habilidades", "glyphicon-home", "/profile/skills/chart/user/"+registry_id))
            if user==registry_id:
                skills_to_validate = skills.model.Skill.getSkill(user, "pending")
                skill_type = "self"
                
                links.append(("Chat", "fa-comments", "/chat/"+registry_id+"/messages"))
                num_convites = str(len(self._registry.amigos_pendentes) + len(self._registry.comunidades_pendentes))
                links.append(("Convites", "fa-envelope", "/invites", "", num_convites))
                links.append(("Alterar perfil", "fa-cog", "/profile/edit"))
                links.append((u"Dúvidas e Sugestões", "fa-question-circle", "/mblog/support"))
            elif user in self._registry.amigos:
                skills_to_validate = skills.model.Skill.getSkillsToValidate(user, registry_id)
                skill_type = "friend"
            elif user in self._registry.amigos_pendentes:
                links.append((u"Já convidado", "fa-check", ""))
            elif user in self._registry.amigos_convidados:
                links.append(("Aceitar amizade", "fa-check", "/invites"))
            else:
                links.append(("Adicionar amigo", "fa-user-plus", "/newfriend?friend="+registry_id))

            log.model.log(user, u'acessou o perfil de', objeto=registry_id, tipo="profile", news=False)
            self.render("modules/member/control-panel.html", NOMEPAG="perfil", \
                        REGISTRY_ID=registry_id, MSG=msg, \
                        FRIENDS=friends, \
                        COMMUNITIES=communities, \
                        NEWS=news[:QTD_NOVIDADES_PAINEL_CONTROLE], \
                        MBLOGS=mblogs, \
                        EVENTOS=eventos, \
                        APPS=apps, \
                        SCRAPS=scraps, \
                        LINKS=links, \
                        TAGCLOUD=tagcloud, \
                        SKILLS=habilidades, \
                        MIN_HABILIDADES_GRAFICO=MIN_HABILIDADES_GRAFICO, \
                        SKILLS_TO_VALIDATE=skills_to_validate, \
                        SKILL_TYPE=skill_type, \
                        AUTOCOMPLETE_ALL_SKILLS = model.getAutocompleteAllSkills(), \
                        LISTA_NOTICIAS=lista_noticias)
                       
            
        else:
            # ---------- comunidade
            
            members = self._registry.getMembersList(page=1, page_size=QTD_MEMBROS_PAINEL_CONTROLE, return_is_owner=True)[1]
            mblogs = mblog.model.Mblog.listPosts(user, registry_id, 1, QTD_MBLOG_PAINEL_CONTROLE) if "mblog" in self._registry.getServices else None
            blogs = blog.model.Blog.listBlogPosts(registry_id, 1, QTD_BLOG_PAINEL_CONTROLE, control_panel=True) if "blog" in self._registry.getServices else None
            eventos = agenda.model.getNextEvents(registry_id, QTD_EVENTOS_PAINEL_CONTROLE) if "agenda" in self._registry.getServices else None
            paginas = wiki.model.Wiki.listPortfolio(user, registry_id, 1, page_size=QTD_PAGINAS_PAINEL_CONTROLE) if "wiki" in self._registry.getServices else None
            forums = forum.model.Topic.get_forum_list(registry_id) if "forum" in self._registry.getServices else None
            news = get_news_list(registry_id)
            self._scrap = scrapbook.model.Scrapbook().retrieve(registry_id)
            scraps = []
            if self._scrap!=None and not filter:
                scraps = self._scrap.getScrapbookList(user, page=1, page_size=QTD_RECADOS_PAINEL_CONTROLE, \
                                                      filter=filter)

            # obtem lista de noticias de registry_id para exibi-las na moldura vermelha.
            noticias = Noticias(registry_id)
            lista_noticias = noticias.get_dict_lista_noticias(popup="S")

            links = []
            links.append((u"Página inicial", "fa-home", "/wiki/"+registry_id+"/home"))
            if self._registry.isOwner(user):
                links.append(("Alterar perfil", "fa-cog", "/profile/"+registry_id+"/edit"))
                links.append(("Gerenciar participantes", "fa-cogs", "/community/owners/"+registry_id))
                links.append((u"Estatísticas", "fa-bar-chart", "/stats/"+registry_id)) 
                links.append(("Excluir comunidade", "fa-trash", "/community/delete/"+registry_id, \
                              "return confirm('Deseja realmente excluir esta comunidade?');"))
            if user in self._registry.participantes:
                if not self._registry.isObrigatoria() and not self._registry.isOwner(user):
                    links.append(("Sair da comunidade", "glyphicon-question-sign", "/community/leave/"+registry_id, \
                                  "return confirm('Deseja realmente deixar de participar desta comunidade?');"))
            else:
                if self._registry.isVoluntaria():
                    links.append(("Entrar na comunidade", "glyphicon-question-sign", "/community/join/"+registry_id))

            log.model.log(user, u'acessou o perfil de', objeto=registry_id, tipo="profile", news=False)
            self.render("modules/community/control-panel.html", NOMEPAG="comunidades", \
                        COMMUNITYDATA=self._registry, REGISTRY_ID=registry_id, MSG=msg, \
                        MEMBERS=members, \
                        MBLOGS=mblogs, \
                        FORUM=list_itens(forums,QTD_FORUM_PAINEL_CONTROLE), \
                        NEWS=news[:QTD_NOVIDADES_PAINEL_CONTROLE], \
                        PAGINAS=paginas, \
                        BLOGS=blogs, \
                        EVENTOS=eventos, \
                        SCRAPS=scraps, \
                        LINKS=links, \
                        USUARIOS_NO_CHAT=chat.model.getUsuariosNoChat(registry_id), \
                        TAGCLOUD=cloudTag(registry_id), \
                        LISTA_NOTICIAS=lista_noticias)

        #hora_fim = datetime.now()
        #print "%s... %s -> %s = %s\n" % (registry_id, str(hora_inicio), str(hora_fim), str(hora_fim-hora_inicio))
    

class PhotoHandler(BaseHandler):
    ''' Exibe foto do usuário/comunidade '''
    
    #não exige que o usuário esteja autenticado pois deve aparecer caso o usuário possua documentos públicos 
    #@tornado.web.authenticated
    def get(self, registry_id):
        user = self.get_current_user()
        size = self.get_argument("size", "G")
        if size not in ["P", "M", "G"]: size="G"
        
        _registry = model.Registry().retrieve(registry_id)
        if _registry:
            if _registry.isSuspended():
                # usuário suspenso
                self.redirect("/static/imagens/usuario-default-%s.png"%size)
                return
                
            filename = "thumb"+size+".png"
            if '_attachments' in _registry and filename in _registry["_attachments"]:
                
                # usuário ou comunidade com foto
                self.set_header("Content-Disposition", "inline; filename=%s" % filename)
                self.set_header("Content-Type", _registry["_attachments"][filename]['content_type'])
                self.set_header("Content-Length", _registry["_attachments"][filename]['length'])
                if database.DB_VERSAO_010:
                    self.write(database.REGISTRY.get_attachment(registry_id, filename, default="Object not found!"))
                else:
                    self.write(database.REGISTRY.get_attachment(registry_id, filename, default="Object not found!").read())
                    
            elif _registry.isAUser():
                # usuário sem foto
                self.redirect("/static/imagens/usuario-default-%s.png"%size)
                
            elif _registry.isACommunity():
                #if "apps" in database.REGISTRY[registry_id]:
                if _registry.subtype=="privilege":
                    # privilégio sem foto
                    self.redirect("/static/imagens/privilegio-default-%s.png"%size)
                else:
                    # comunidade sem foto
                    self.redirect("/static/imagens/comunidade-default-%s.png"%size)
        else:
            raise HTTPError(404)


class CSSHandler(BaseHandler):
    ''' Exibe arquivo CSS utilizado pela wiki do usuário/comunidade '''
    
    def get(self, registry_id):
        user = self.get_current_user()
        
        #if self.isAllowedToAccess(user, registry_id, display_error=False):
        if registry_id in database.REGISTRY:
            #filename = database.REGISTRY[registry_id]['photo']
            filename = "arquivo_css.css"
            if '_attachments' in database.REGISTRY[registry_id] and \
               filename in database.REGISTRY[registry_id]['_attachments']:
                self.set_header("Content-Disposition", "inline; filename=%s" % filename)
                self.set_header("Content-Type", database.REGISTRY[registry_id]['_attachments'][filename]['content_type'])
                self.set_header("Content-Length", database.REGISTRY[registry_id]['_attachments'][filename]['length'])
                if database.DB_VERSAO_010:
                    self.write(database.REGISTRY.get_attachment(registry_id, filename, default="Object not found!"))
                else:
                    self.write(database.REGISTRY.get_attachment(registry_id, filename, default="Object not found!").read())
                    
            else:
                self.redirect("/static/arquivo_css_default.css")

        else:
            raise HTTPError(404)



class RemoveUserHandler(BaseHandler):
    ''' Desativação de usuário no Activ '''
    
    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        self.render("modules/member/suspend_user.html", REGISTRY_ID=user, MSG="", \
                    NOMEPAG="cadastro")

    @tornado.web.authenticated
    def post(self):
        user = self.get_current_user()
        passwd = self.get_argument("passwd", "")

        self._user = model.Member().retrieve(user)
        
        if passwd != "":
            hash = hashlib.md5()
            hash.update(user.encode('utf-8') + passwd.encode('utf-8'))             
            passwd = hash.hexdigest()
            
            if self._user.passwd == passwd:
                
                # desativa usuário
                self._user.suspended_passwd = self._user.passwd
                self._user.suspended_email = self._user.email
                self._user.suspended_cpf = self._user.cpf
                self._user.suspended_date = str(datetime.now())
                
                self._user.subtype = "suspended"
                self._user.passwd = PASSWD_USER_SUSPENDED
                self._user.email = PASSWD_USER_SUSPENDED
                self._user.cpf = PASSWD_USER_SUSPENDED
                
                self._user.save()

                # e remove todas as suas tags
                removeUserTags(user)
                
                log.model.log(user, u'encerrou sua conta no '+PLATAFORMA, news=False)
                self.redirect("/logout")
                
            else:
                self.render("modules/member/suspend_user.html", NEXT=next, MSG=u"Senha incorreta.", \
                        NOMEPAG="cadastro")
                
        else:
            self.render("modules/member/suspend_user.html", NEXT=next, MSG=u"Senha não especificada.", \
                        NOMEPAG="cadastro")
            
  
class ReactivateUserHandler(BaseHandler):
    ''' Reativação de usuário no Activ '''
    
    @tornado.web.authenticated
    @model.userIsCommunityMember (PRIV_GLOBAL_ADMIN)
    def get(self):
        self.render("modules/member/reactivate_user.html", REGISTRY_ID=PRIV_GLOBAL_ADMIN, MSG="", \
                    NOMEPAG="cadastro")

    @tornado.web.authenticated
    @model.userIsCommunityMember (PRIV_GLOBAL_ADMIN)
    def post(self):
        user = self.get_current_user()
        suspended_user = self.get_argument("user", "")

        self._user = model.Member().retrieve(suspended_user)
        
        msg = ""
        if self._user:
            if self._user.isSuspended():
                
                if not model.usersByCPF(self._user.suspended_cpf) and not model.emailExists(self._user.suspended_email):
                    
                    # reativa usuário
                    self._user.subtype = ""
                    self._user.passwd = self._user.suspended_passwd
                    self._user.email = self._user.suspended_email
                    self._user.cpf = self._user.suspended_cpf

                    self._user.suspended_passwd = ""
                    self._user.suspended_email = ""
                    self._user.suspended_cpf = ""
                    self._user.reactivated_date = str(datetime.now())
                    self._user.reactivated_by = user
                                        
                    self._user.save()
                     
                    log.model.log(suspended_user, u'reativou sua conta no '+PLATAFORMA, news=False)
                    
                    msg = u"O usuário %s foi reativado com sucesso e sua senha anterior foi restaurada. <br/>Favor executar o dbclean assim que possível para reativar as tags deste usuário." % suspended_user
                
                else:
                    msg = u"Usuário %s não pode ser reativado pois seu cpf e/ou email já foram reutilizados." % suspended_user
                    
            else:
                msg = u"Usuário %s não encontra-se desativado e portanto não pode ser reativado." % suspended_user
                
        else:
            msg = u"Usuário %s não encontrado." % suspended_user           
            
        self.render("modules/member/reactivate_user.html", MSG=msg, \
                    NOMEPAG="cadastro")  



"""
class ControlPanelDeleteHandler(BaseHandler):
    ''' Exclusão de uma Widget do painel de controle do usuário '''
    
    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        type = self.get_argument("type", "")
        if type:
            _user = model.Member().retrieve(user)
            if type in _user.widgets:
                _user.widgets.remove(type)
                _user.save()
                
        self.redirect("/profile/%s"%user)
"""        


class TestIntranetHandler(BaseHandler):
    ''' Teste para autenticação de usuários através da Intranet da UFRJ redirecionando 
    para o painel de controle do usuário. Usar no banco de teste'''
    

    def get(self):
        idUFRJ   = "11111011110" #colocar um cpf do banco de teste
        idSessao = "012345678901234567890"  
        if idUFRJ=="" or idSessao=="":
            self.render(self.searchEntryPoint(), NEXT="", MSG=u"Chamada inválida.", \
                        NOMEPAG="cadastro")
            return
            
        # Cria uma sessao valida
        """  
        cur = conn.cursor()
        cur.execute('''SELECT P.nome, P.email FROM UsuariosLogados U
                       JOIN Intranet_Pessoa P ON U.identificacaoUFRJ = P.identificacaoUFRJ
                       WHERE U.identificacaoUFRJ=%s AND U.SessionID=%s''', (idUFRJ, idSessao))
        """
        #Simula a row da query acima
        # Tem uma conexao valida
        row = ['\xc1rea de Sistemas de Informa\xe7\xe3o/NCE', "email@fulano.com"]
        
        # Nao tem conexao valida
        #row=[]
        
        if not row:
            self.render(self.searchEntryPoint(), NEXT="", MSG=u"Autenticação da intranet não reconhecida.", \
                        NOMEPAG="cadastro")
            return

        # obtém nome e email do usuário
        
        # estava dando erro 500 quando o nome na intranet tem acento.
        nomeIntranet = row[0].decode('iso-8859-1')
        
        email = row[1]
        
        #conn.close()        
        
        
        # verifica se o CPF autenticado existe no registry
        userlist = model.usersByCPF(idUFRJ)
        
        if userlist:
            user = userlist[0]    # Pega o primeiro. E se existir mais de um ???????
            
            # usuário autenticado
            self.set_secure_cookie("user", user, None)
            self.set_secure_cookie("nome", database.REGISTRY[user]["name"].encode('utf-8'), None) # 
            
            log.model.log(user, u'entrou no '+PLATAFORMA+' pela IntranetUFRJ', news=False)
            self.redirect("/user/%s" % user)

        else:
            if not email:
                msg = u"Não é possível acessar o ActivUFRJ pois você não tem email cadastrado na Intranet. " + \
                      u"Para cadastrar um email agora, <a href='https://intranet.ufrj.br/utilidades2006/aEmailF.asp'>clique aqui</a>."
                self.render("home.html", MSG=msg, \
                            NOMEPAG="cadastro")  
                return                  
                
                
            # verifica se o email existe no registry
            userlist = model.usersByEmail(email)
            if userlist:
                user = userlist[0]  # Pega o primeiro. E se existir mais de um ???????

                # usuário autenticado
                self.set_secure_cookie("user", user, None)
                self.set_secure_cookie("nome", database.REGISTRY[user]["name"].encode('utf-8'), None)
                
                # armazena o cpf no registry
                user_data = model.Registry().retrieve(user)
                user_data.cpf = idUFRJ
                user_data.save()

                log.model.log(user, u'entrou no '+PLATAFORMA+' pela IntranetUFRJ', news=False)
                self.redirect("/user/%s" % user)
    
            else:
                # 1o acesso: cpf e email do usuário autenticado na intranet não existem no registry
                # exibe um formulário de cadastro no Activ
                
                registry_data = model.Member()
                nomes = nomeIntranet.split()
                registry_data.name = nomes[0]
                registry_data.lastname = ' '.join(nomes[1:])
                
                #registry_data.name = ""
                #registry_data.lastname = ""
                registry_data.cpf = idUFRJ
                registry_data.email = email
                registry_data.user = ""
                registry_data.passwd = ""
                registry_data.vinculos = []

                # verifica se é professor ou tec_adm para atribuir o privilégio de criar comunidades
                # busca as informacoes para prencher a lista de vinculos - agora temos que testar todos os vinculos
                row=[]
                criar_comunidades = "N"
                
                # É professor ?
                """
                cur = conn.cursor()
                cur.execute('''SELECT IdentificacaoUFRJ, MatriculaSiape, Ativo, DescricaoLocal, Email FROM View_eh_professor
                               WHERE IdentificacaoUFRJ=%s''', idUFRJ)
                row = cur.fetchone()
                """
                #Simulando Row para a query acima:
                #Eh_professor
                #row = [idUFRJ,"0333333", "0", "Instituto Tercio Pacitti", email]
                #print row[0], row[2], row[3], row[4], row[1]
                if row:
                    criar_comunidades = "S"
                
                # registry_data.vinculos.append({"vinculo":"P", "instituicao":"UFRJ", "cpfufrj":row[0], "emailufrj": row[4], "ativo": row[2], "siape": row[1], "localizacao": row[3].strip()})
                
                row=[]
                  
                # É (tambem) funcionario ?
                """
                cur = conn.cursor()
                cur.execute('''SELECT IdentificacaoUFRJ, MatriculaSiape, Ativo, DescricaoLocal, Email FROM View_eh_tec_adm 
                               WHERE IdentificacaoUFRJ=%s''', idUFRJ)
                row = cur.fetchone()
                """
                #Simulando Row para a query acima:
                #Eh_funcionario
                row = [idUFRJ,"0333333", "0", "Instituto Tercio Pacitti", email]
                
                if row:
                    criar_comunidades = "S"
                  
                s = '\xc1rea de Sistemas de Informa\xe7\xe3o/NCE'
                registry_data.vinculos.append({"vinculo":"F", 
                                               "instituicao":"UFRJ", 
                                               'cpfufrj': '11122233300', 
                                               'emailufrj': 'xxxx@nce.ufrj.br', 
                                               "ativo": 1, 
                                               "siape": '0361111', 
                                               "localizacao": s.decode('iso-8859-1')})                
                            
                # registry_data.vinculos.append({"vinculo":"F", "instituicao":"UFRJ", "cpfufrj":row[0], "emailufrj": row[4], "siape": row[1], "ativo": row[2], "localizacao": row[3].strip()})
                    
                row=[]
                # É (tambem) aluno de graduação ?
                """
                cur = conn.cursor()
                cur.execute('''SELECT IdentificacaoUFRJ, registroSIRA, ativo, nome, Email FROM view_eh_aluno_grad
                               WHERE IdentificacaoUFRJ=%s''', idUFRJ)
                """             
                #Simulando Row para a query acima:
                #Eh_aluno_grad
                #row = [idUFRJ,"012345680", "0", "Informatica na Educacao", email]
                
                # registry_data.vinculos.append({"vinculo":"A", "instituicao":"UFRJ", "tipo": "Grad", "cpfufrj":row[0], "emailufrj": row[4], "dre": row[1], "ativo": row[2], "curso": row[3]})
                       
                
                row=[]
                # É (tambem) aluno de pós-graduação ?
                """
                cur = conn.cursor()
                cur.execute('''SELECT IdentificacaoUFRJ, registroSIRA, ativo, nome, Email FROM view_eh_aluno_pos
                               WHERE IdentificacaoUFRJ=%s''', idUFRJ)
                """
                #Eh_aluno_grad
                #row = [idUFRJ,"112345680", "0", "Mestrado em Informatica", email]
               
                # registry_data["vinculos"].append({"vinculo":"A", "instituicao":"UFRJ", "tipo": "Pos", "cpfufrj":row[0], "emailufrj": row[4], "dre": row[1], "ativo": row[2], "curso": row[3]})
                    
                row=[]
                                          
                self.render("modules/member/intranet-form.html", REGISTRYDATA=registry_data, MSG="", \
                            NOMEPAG="cadastro", CRIARCOMUNIDADES=criar_comunidades)                    
#Fim do teste intranet        
        
                                    
URL_TO_PAGETITLE = {
        "login":              "Login", 
        "loginintranet":      "Login", 
        "shutdown":           "Administração", 
        "new":                "Cadastro",
        "removeuser":         "Cadastro",
        "reactivateuser":     "Cadastro",
        "about":              "Sobre o ActivUFRJ",
        "user":               "Perfil",
        "profile":            "Perfil",
        "forgotpasswd":       "Perfil",
        "changeforgotpasswd": "Perfil",
        "photo":              "Perfil",
        "communities":        "Comunidades"
    }
            
HANDLERS = [
                (r"/",                                 MainHandler),
                (r"/homepage",                         HomePageHandler),
                (r"/login",                            LoginHandler),
                (r"/loginintranet",                    LoginIntranetHandler),
                (r"/logout",                           LogoutHandler),
                (r"/shutdown",                         ShutdownHandler),
                (r"/user/%s" % NOMEUSERS,              UserHandler),
                (r"/new/user" ,                        RegistryUserHandler),
                (r"/communities/new",                  RegistryCommunityHandler),
                (r"/profile/edit",                     EditProfileHandler),
                (r"/profile/%s/edit" % NOMEUSERS,      EditCommunityProfileHandler),
                (r"/profile/changepasswd",             ChangePasswdHandler),
                (r"/about",                            AboutHandler),
                (r"/forgotpasswd",                     ForgotPasswdHandler),
                (r"/changeforgotpasswd",               ChangeForgotPasswdHandler),
                (r"/profile/%s" % NOMEUSERS,           ProfileHandler),
                (r"/photo/%s" % NOMEUSERS,             PhotoHandler),
                (r"/css/%s" % NOMEUSERS,               CSSHandler),
                (r"/removeuser",                       RemoveUserHandler),               
                (r"/reactivateuser",                   ReactivateUserHandler),           
                #(r"/controlpanel/delete",              ControlPanelDeleteHandler)
                #(r"/testeintranet",                    TestIntranetHandler),             
            ]