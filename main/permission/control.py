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

import operator
from operator import itemgetter
from uuid import uuid4
from urllib import quote,unquote
import time
from datetime import datetime
import re

import tornado.web
import tornado.template

import model
from model import TXT_PERM
import database
import core.model
from core.model import isOwner, isUserOrMember, isUserOrOwner, isAUser, isACommunity, getType, _EMPTYCOMMUNITY, _EMPTYMEMBER
import wiki.model
import files.model
from core.database import DB_VERSAO_010
import log.model
from search.model import addTag, removeTag
from core.dispatcher import BaseHandler, HANDLERS, URL_TO_PAGETITLE, \
                            NOMEUSERS, \
                            FILENAMECHARS, PAGENAMECHARS, \
                            VALID_LOGIN
from config import SERVICES
                 
import libs.permissions
from libs.permissions import objectOwnerFromService, perm_type, has_editable_permission
from libs.dateformat import short_datetime
from libs.strformat import remove_diacritics, remove_special_chars
from libs.notify import Notify

''' importa definição do tutorial deste módulo, se existir _tutorial.py '''
from config import TUTORIAL
try:
    import _tutorial
except ImportError:
    pass



"""

_NOMEPAGS[service][0] => SERVICES[type][service]["description"]
_NOMEPAGS[service][1] => SERVICES[type][service]["cor"]

_NOMEPAGS = {
                 "wiki": (u"páginas", "Azul"),
                 "file": ("arquivos", "Verde"),
                 "blog": ("blog", "Laranja"),
                 "evaluation": (u"avaliação", "Azul"),
                 "bookmarks": ("favoritos", "Verde"),
                 "glossary": (u"glossário", "Cinza"),
                 "agenda": ("agenda", "Laranja"),
                 "noticia": (u"notícia", "Verde"),
                 "question": (u"questões", "Cinza"),
                 "quiz": (u"quiz", "Laranja"),
                 "videoaula": (u"videoaula", "Azul")
}
"""

        
def get_object_path(service, registry_id, obj_name):
    ''' Constrói o caminho (PATH) de retorno de obj_name que será 
        apresentado na tela de Edição de Permissions.
    '''
    
    obj_id = "%s/%s" % (registry_id, obj_name)
            
    if service == "wiki":
        return u"Permissões do objeto " + wiki.model.Wiki().retrieve(obj_id).getPagePath(links=False, includepage=True)
        
    elif service == "file":
        return u"Permissões do objeto " + files.model.Files().retrieve(obj_id).getFilePath(links=False, includefile=True)
       
    elif perm_type(service)=="service":
        #permissão sobre o serviço como um todo
        return u"Permissões do servico /%s/%s" % (service, registry_id)
        
    elif perm_type(service)=="object":
        #permissão sobre o objeto
        return u"Permissões do objeto /%s/%s/%s" % (service, registry_id, obj_name)
    
    else: 
        return None   
    
    
class EditPermissionsHandler(BaseHandler):
    ''' Alteração de permissões de um objeto: (página Wiki, arquivo, avaliação, quiz, etc) 
        ou de um serviço (blog, bookmarks, etc) 
    '''

    @tornado.web.authenticated
    @libs.permissions.userOrOwnerOrObjectOwner
    def get (self, service, registry_id, objeto=""):
        user = self.get_current_user()
        (registry_type, privacidade) = getType(registry_id)
        if not has_editable_permission(service):
            self.render("home.html", MSG=u"Serviço inválido.", REGISTRY_ID=registry_id, \
                        NOMEPAG='comunidades')
            return     
               
        if service == "wiki" and objeto in ["home", "indice"]:
            service_perm = ( [(item, TXT_PERM[registry_type][item]) for item in ["acesso_activ","acesso_publico"]],
                             [(item, TXT_PERM[registry_type][item]) for item in SERVICES[registry_type][service]["perm_w"]] )
        elif privacidade == "Privada":
            service_perm = ( [(item, TXT_PERM[registry_type][item]) for item in ["acesso_privado", "acesso_grupos", "acesso_comunidade"]],
                             [(item, TXT_PERM[registry_type][item]) for item in SERVICES[registry_type][service]["perm_w"]] )
        else:
            service_perm = model.service_permissions (service, registry_type)
        
        
        groups = core.model.Registry().retrieve(registry_id).groups.keys()
        perm_id = '/'.join([service, registry_id, objeto])
        self._perm = model.Permission().retrieve(perm_id)
        if not self._perm: 
            self._perm = model.Permission(id=perm_id, \
                                          leitura=model.default_permission("R", service, registry_type, privacidade), \
                                          escrita=model.default_permission("W", service, registry_type, privacidade))
        self.render("modules/permission/perm-edit.html", \
                    NOMEPAG=SERVICES[registry_type][service]["description"], \
                    REGISTRY_ID=registry_id, PERM_ID=perm_id, PERMDATA=self._perm, \
                    PATH=get_object_path(service, registry_id, objeto), \
                    SERVICE=service, GROUPS=groups, \
                    LEGENDA_R=SERVICES[registry_type][service]["legenda_perm_r"], \
                    LEGENDA_W=SERVICES[registry_type][service]["legenda_perm_w"], \
                    SERVICE_PERM=service_perm, \
                    MSG="")

   
    @tornado.web.authenticated
    @libs.permissions.userOrOwnerOrObjectOwner
    def post(self, service, registry_id, objeto=""):
        user = self.get_current_user()
        registry_type = getType(registry_id)[0]
        
        user_data = _EMPTYCOMMUNITY()
        user_data.update(core.database.REGISTRY[registry_id])
        groups = user_data["groups"].keys()
        grupos_r = []
        grupos_w = []
        for g in groups:
            if self.get_argument("escopo_R","")=="acesso_grupos" and self.get_argument("R_"+g, "") == "S":
                grupos_r.append(g)
            if self.get_argument("escopo_W","")=="acesso_grupos" and self.get_argument("W_"+g, "") == "S":
                grupos_w.append(g)
                
        leitura={"escopo":self.get_argument("escopo_R",""), "grupos":grupos_r}
        escrita={"escopo":self.get_argument("escopo_W",""), "grupos":grupos_w}
        data_agora = str(datetime.now())
                    
        perm_id = '/'.join([service, registry_id, objeto])
        self._perm = model.Permission().retrieve(perm_id)
        if not self._perm: 
            
            # Permissão não existe. Busco o owner do objeto.
            owner = objectOwnerFromService (service, registry_id, objeto)
            if owner==None:
                self.render("home.html", MSG=u"Serviço inválido.", REGISTRY_ID=registry_id, \
                            NOMEPAG='comunidades')
                return  
             
            # crio a permissão deste objeto.       
            self._perm = model.Permission(id=perm_id, \
                                          owner=owner, \
                                          service=service, registry_id=registry_id, nomeobj=objeto, \
                                          data_cri = data_agora, \
                                          leitura=leitura, escrita=escrita)
        else:
            self._perm.leitura = leitura
            self._perm.escrita = escrita

        self._perm.data_alt = data_agora
        self._perm.alterado_por = user

        self._perm.save()
            
        """
        # notifica o dono da página alterada
        email_msg = u"Página alterada: "+doc_id+"\n"+\
                    Notify.assinatura(user, registry_id, self._wiki.historico[-1]["data_alt"])+"\n\n"
        Notify.email_notify(self._wiki.owner, user, u"alterou uma página criada por você", \
                       message=email_msg, \
                       link="wiki/"+doc_id)
        
        log.model.log(user, u'alterou a página', objeto=doc_id, tipo="wiki")
        self.redirect("/wiki/%s" % doc_id)
        """

        self.render("modules/permission/perm-edit.html", \
                    NOMEPAG=SERVICES[registry_type][service]["description"], \
                    REGISTRY_ID=registry_id, PERM_ID=perm_id, PERMDATA=self._perm, \
                    MSG=u"Permissões alteradas", \
                    PATH=get_object_path(service, registry_id, objeto), \
                    SERVICE=service, GROUPS=groups, \
                    LEGENDA_R=SERVICES[registry_type][service]["legenda_perm_r"], \
                    LEGENDA_W=SERVICES[registry_type][service]["legenda_perm_w"], \
                    SERVICE_PERM=model.service_permissions (service, registry_type))


class UpdateGroupsHandler(BaseHandler):
    ''' com parâmetro ?part= Altera grupos de um participante 
        com parâmetro ?group= Altera participantes de um grupo '''
    
    @tornado.web.authenticated
    def get(self, registry_id):               
        user = self.get_current_user()
        if isACommunity(registry_id):
            if isUserOrOwner(user, registry_id):
                part = self.get_argument("part","")
                group = self.get_argument("group","")
    
                user_data = _EMPTYCOMMUNITY()
                user_data.update(core.database.REGISTRY[registry_id])
                if part:
                    groups = [(group, part in user_data["groups"][group]) for group in user_data["groups"].keys()]
                    
                    self.render("modules/community/update-groups.html", NOMEPAG='comunidades', \
                                PART=part, GROUPS=groups, \
                                REGISTRY_ID=registry_id, MSG="")   
                elif group:
                    parts = [(part, part in user_data["groups"][group]) for part in user_data["participantes"] if isAUser(part)]
                    self.render("modules/community/update-parts.html", NOMEPAG='comunidades', \
                                PARTS=parts, GROUP=group, \
                                REGISTRY_ID=registry_id, MSG="")                   
                else:
                    self.render("home.html", MSG=u"Chamada inválida.", NOMEPAG='comunidades')                    
            else:
                    self.render("home.html", MSG=u"Somente administradores da comunidade podem agrupar participantes.", NOMEPAG='comunidades')  

        else:
            if isUserOrOwner(user, registry_id):
                part = self.get_argument("part","")
                group = self.get_argument("group","")
    
                user_data = _EMPTYMEMBER()
                user_data.update(core.database.REGISTRY[registry_id])
                if part:
                    groups = [(group, part in user_data["groups"][group]) for group in user_data["groups"].keys()]
                    
                    self.render("modules/community/update-groups.html", NOMEPAG='amigos', \
                                PART=part, GROUPS=groups, \
                                REGISTRY_ID=registry_id, MSG="")   
                elif group:
                    parts = [(part, part in user_data["groups"][group]) for part in user_data["amigos"]]
                    self.render("modules/community/update-parts.html", NOMEPAG='amigos', \
                                PARTS=parts, GROUP=group, \
                                REGISTRY_ID=registry_id, MSG="")                   
                else:
                    self.render("home.html", MSG=u"Chamada inválida.", NOMEPAG='amigos')                    
            else:
                    self.render("home.html", MSG=u"Somente o próprio usuário pode agrupar seus amigos.", NOMEPAG='amigos')                              
                            
    @tornado.web.authenticated
    def post(self, registry_id):               
        user = self.get_current_user()
        if isUserOrOwner(user, registry_id):
            part = self.get_argument("part","")
            group = self.get_argument("group","")

            if isACommunity(registry_id):
                user_data = _EMPTYCOMMUNITY()
            else:
                user_data = _EMPTYMEMBER()
            user_data.update(core.database.REGISTRY[registry_id])
            
            if part:
                for group in user_data["groups"].keys():
                    checkbox_value = self.get_argument(group,"")
                    if checkbox_value=="S" and part not in user_data["groups"][group]:
                        user_data["groups"][group].append(part)
                    elif checkbox_value<>"S" and part in user_data["groups"][group]:
                        while part in user_data["groups"][group]:
                            user_data["groups"][group].remove(part)
                core.database.REGISTRY[registry_id] = user_data
                     
                self.render("popup_msg.html", MSG=u"Grupos alterados com sucesso.", REGISTRY_ID=registry_id)
                
            elif group:
                pessoas = user_data["participantes"] if isACommunity(registry_id) else user_data["amigos"]
                for part in pessoas:
                    checkbox_value = self.get_argument(part,"")
                    if checkbox_value=="S" and part not in user_data["groups"][group]:
                        user_data["groups"][group].append(part)
                    elif checkbox_value<>"S" and part in user_data["groups"][group]:
                        while part in user_data["groups"][group]:
                            user_data["groups"][group].remove(part)
                core.database.REGISTRY[registry_id] = user_data
                     
                self.render("popup_msg.html", MSG=u"Participantes alterados com sucesso.", REGISTRY_ID=registry_id)               

            else:
                self.render("popup_msg.html", MSG=u"Chamada inválida.")                    
             
        else:
            if isACommunity(registry_id):
                self.render("popup_msg.html", MSG=u"Somente administradores da comunidade podem agrupar participantes.", REGISTRY_ID=registry_id)  
            else:                
                self.render("popup_msg.html", MSG=u"Somente o próprio usuário pode agrupar seus amigos.", REGISTRY_ID=registry_id)                    
            

class CreateGroupHandler(BaseHandler):
    ''' Cria um grupo numa comunidade/usuário '''
    @tornado.web.authenticated
    def get(self, registry_id):               
        user = self.get_current_user()
        if isUserOrOwner(user, registry_id):
            user_data = _EMPTYCOMMUNITY()
            user_data.update(core.database.REGISTRY[registry_id])
            groups = user_data["groups"].keys()
            
            self.render("modules/community/create-group.html", NOMEPAG='comunidades', \
                        GROUPS=groups, \
                        REGISTRY_ID=registry_id, MSG="")   
        elif isACommunity(registry_id):
            self.render("home.html", MSG=u"Somente administradores da comunidade podem criar grupos.", NOMEPAG='comunidades')  
        else:
            self.render("home.html", MSG=u"Somente o próprio usuário pode criar grupos.", NOMEPAG='amigos')  

    @tornado.web.authenticated
    def post(self, registry_id):               
        user = self.get_current_user()
        msg = ""
        if isUserOrOwner(user, registry_id):
            grupo = self.get_argument("grupo","")
            p = re.compile(VALID_LOGIN)
            if not grupo:
                msg = u"Grupo não preenchido."    
            elif not p.match(grupo):
                msg = u"Nome inválido. Deve ter no mínimo 3 caracteres, começando e terminando com letras ou números e utilizando apenas letras, números, '_' e '.' em sua composição. Não utilize acentuação!<br/>"                    
            else:
                user_data = _EMPTYCOMMUNITY()
                user_data.update(core.database.REGISTRY[registry_id])
                if grupo not in user_data["groups"]:
                    user_data["groups"][grupo] = []
                    core.database.REGISTRY[registry_id] = user_data     
                    msg = u"Grupo criado com sucesso."
                else:
                    msg = u"Grupo já existente."                    
   
        elif isACommunity(registry_id):
            msg=u"Somente administradores da comunidade podem criar grupos."  
        else:
            msg=u"Somente o próprio usuário pode criar grupos."
            
        self.render("popup_msg.html", MSG=msg, REGISTRY_ID=registry_id)                    
            
class DeleteGroupHandler(BaseHandler):
    ''' Remove um grupo numa comunidade/usuário '''
    @tornado.web.authenticated
    def get(self, registry_id):               
        user = self.get_current_user()
        grupo = self.get_argument("group","")
        if isUserOrOwner(user, registry_id):
            user_data = _EMPTYCOMMUNITY()
            user_data.update(core.database.REGISTRY[registry_id])
            if grupo in user_data["groups"]:
                del user_data["groups"][grupo]
                core.database.REGISTRY[registry_id] = user_data     
                if isACommunity(registry_id):
                    self.redirect ("/members/"+registry_id)
                else:
                    self.redirect ("/friends/"+registry_id)
                return
                    
            else:
                msg = u"Grupo não existente."   
        elif isACommunity(registry_id):
            msg = u"Somente administradores da comunidade podem excluir grupos."
        else:
            msg = u"Somente o próprio usuário pode excluir grupos."

        self.render("popup_msg.html", MSG=msg, REGISTRY_ID=registry_id)  
         

class UpdateCommunityGroupsHandler(BaseHandler):
    ''' Altera comunidades pertencentes a um grupo.
        com parâmetro ?part= Altera grupos de uma comunidade 
        com parâmetro ?group= Altera comunidades de um grupo 
    '''
    
    @tornado.web.authenticated
    def get(self, registry_id):               
        user = self.get_current_user()
        if user == registry_id:
            part = self.get_argument("part","")
            group = self.get_argument("group","")

            user_data = _EMPTYMEMBER()
            user_data.update(core.database.REGISTRY[registry_id])
            if part:
                groups = [(group, part in user_data["community_groups"][group]) for group in user_data["community_groups"].keys()]
                
                self.render("modules/community/update-groups.html", NOMEPAG='comunidades', \
                            PART=part, GROUPS=groups, \
                            REGISTRY_ID=registry_id, MSG="")   
            elif group:
                parts = [(part, part in user_data["community_groups"][group]) for part in user_data["comunidades"]]
                self.render("modules/community/update-parts.html", NOMEPAG='comunidades', \
                            PARTS=parts, GROUP=group, \
                            REGISTRY_ID=registry_id, MSG="")                   
            else:
                self.render("home.html", MSG=u"Chamada inválida.", NOMEPAG='comunidades')                    
        else:
                self.render("home.html", MSG=u"Somente o próprio usuário pode agrupar suas comunidades.", NOMEPAG='comunidades')                              
                            
    @tornado.web.authenticated
    def post(self, registry_id):               
        user = self.get_current_user()
        if user == registry_id:
            part = self.get_argument("part","")
            group = self.get_argument("group","")

            user_data = _EMPTYMEMBER()
            user_data.update(core.database.REGISTRY[registry_id])
            
            if part:
                for group in user_data["community_groups"].keys():
                    checkbox_value = self.get_argument(group,"")
                    if checkbox_value=="S" and part not in user_data["community_groups"][group]:
                        user_data["community_groups"][group].append(part)
                    elif checkbox_value<>"S" and part in user_data["community_groups"][group]:
                        while part in user_data["community_groups"][group]:
                            user_data["community_groups"][group].remove(part)
                core.database.REGISTRY[registry_id] = user_data
                     
                self.render("popup_msg.html", MSG=u"Grupos alterados com sucesso.", REGISTRY_ID=registry_id)
                
            elif group:
                for part in user_data["comunidades"]:
                    checkbox_value = self.get_argument(part,"")
                    if checkbox_value=="S" and part not in user_data["community_groups"][group]:
                        user_data["community_groups"][group].append(part)
                    elif checkbox_value<>"S" and part in user_data["community_groups"][group]:
                        while part in user_data["community_groups"][group]:
                            user_data["community_groups"][group].remove(part)
                core.database.REGISTRY[registry_id] = user_data
                     
                self.render("popup_msg.html", MSG=u"Grupo alterado com sucesso.", REGISTRY_ID=registry_id)               

            else:
                self.render("popup_msg.html", MSG=u"Chamada inválida.")                    
             
        else:
            self.render("popup_msg.html", MSG=u"Somente o próprio usuário pode agrupar suas comunidades.", REGISTRY_ID=registry_id)                    
            
class CreateCommunityGroupHandler(BaseHandler):
    ''' Cria um grupo de comunidades para um usuário '''
    @tornado.web.authenticated
    def get(self, registry_id):               
        user = self.get_current_user()
        if user == registry_id:
            self._member = core.model.Member().retrieve(registry_id)
            self.render("modules/community/create-group.html", NOMEPAG='comunidades', \
                        GROUPS=self._member.community_groups.keys(), \
                        REGISTRY_ID=registry_id, MSG="")   
        else:
            self.render("home.html", MSG=u"Somente o próprio usuário pode criar grupos.", NOMEPAG='comunidades')  

    @tornado.web.authenticated
    def post(self, registry_id):               
        user = self.get_current_user()
        msg = ""
        if user == registry_id:
            grupo = self.get_argument("grupo","")
            p = re.compile(VALID_LOGIN)
            if not grupo:
                msg = u"Grupo não preenchido."    
            elif not p.match(grupo):
                msg = u"Nome inválido. Deve ter no mínimo 3 caracteres, começando e terminando com letras ou números e utilizando apenas letras, números, '_' e '.' em sua composição. Não utilize acentuação!<br/>"                    
            else:
                self._member = core.model.Member().retrieve(registry_id)    
                 
                if grupo not in self._member.community_groups:
                    self._member.addCommunityGroup(grupo)
                    msg = u"Grupo criado com sucesso."
                else:
                    msg = u"Grupo já existente."                    
   
        else:
            msg=u"Somente o próprio usuário pode criar grupos."
            
        self.render("popup_msg.html", MSG=msg, REGISTRY_ID=registry_id)                    
 
class DeleteCommunityGroupHandler(BaseHandler):
    ''' Remove um grupo de comunidades de um usuário '''
    @tornado.web.authenticated
    def get(self, registry_id):               
        user = self.get_current_user()
        grupo = self.get_argument("group","")
        if user == registry_id:
            self._member = core.model.Member().retrieve(registry_id)

            if self._member.delCommunityGroup(grupo):
                self.redirect ("/communities/"+registry_id)
                return
                    
            else:
                msg = u"Grupo não existente."   
        else:
            msg = u"Somente o próprio usuário pode excluir grupos."

        self.render("popup_msg.html", MSG=msg, REGISTRY_ID=registry_id)  
                                           
URL_TO_PAGETITLE.update ({
        "permission":   u"Permissões",
        "groups":       u"Grupos"
    })

HANDLERS.extend([
            (r"/permission/%s/%s"    % (NOMEUSERS, PAGENAMECHARS),              EditPermissionsHandler), # blog, bookmarks, glossary, agenda, noticia, question
            (r"/permission/%s/%s/%s" % (NOMEUSERS, NOMEUSERS, PAGENAMECHARS),   EditPermissionsHandler),  # wiki, file, evaluation
            (r"/groups/%s" % NOMEUSERS,                                         UpdateGroupsHandler),
            (r"/groups/new/%s" % NOMEUSERS,                                     CreateGroupHandler),
            (r"/groups/delete/%s" % NOMEUSERS,                                  DeleteGroupHandler),
            (r"/communitygroups/%s" % NOMEUSERS,                                UpdateCommunityGroupsHandler),
            (r"/communitygroups/new/%s" % NOMEUSERS,                            CreateCommunityGroupHandler),
            (r"/communitygroups/delete/%s" % NOMEUSERS,                         DeleteCommunityGroupHandler)
])
