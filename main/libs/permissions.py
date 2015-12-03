# -*- coding: utf-8 -*-
"""
################################################
Oi Tonomundo - NCE/UFRJ
################################################

:Author: Eduardo Paz
:Contact: edupaz@nce.ufrj.br
:Date: $Date: 2010/08/02  $
:Status: This is a "work in progress"
:Revision: $Revision: 0.01 $
:Home: ``
:Copyright:  
"""

import urllib
import urlparse

from tornado.web import HTTPError 

import core.model
from core.model import isUserOrOwner, isUserOrMember, isFriendOrMember, isMember, isAUser
import wiki.model
import files.model
import blog.model
import evaluation.model 
import videoaula.model
import permission.model
from config import SERVICES

"""
esse método deixa de existir.
todas as chamadas a ele tem que passar a chamar
libs.permissions_base.isAllowedToWriteObject

somente o studio ainda está usando esta função
"""    

def isAllowedToEditObject(user, owner, doc_id, edicao_publica="S"):
    # só o dono da comunidade ou dono do objeto ou
    # (qq membro se o objeto for de edição pública)
    (registry_id, nomeobj) = doc_id.split("/")
    return (user == owner or \
            isUserOrOwner(user, registry_id) or \
            (isMember(user, registry_id) and edicao_publica=="S") )


"""
essas 3 não mudam
"""

def isAllowedToDeleteObject(user, owner, doc_id, wiki="N"):
    # só o dono de um objeto ou o dono da comunidade podem apagá-lo
    (registry_id, nomeobj) = doc_id.split("/")
    return ((wiki=="N" or nomeobj not in ["home", "indice"]) and \
            ((user == owner) or \
            isUserOrOwner(user, registry_id)))

def isAllowedToComment(user, doc_id, owner):
    # todos os participantes da comunidade ou amigos do usuário podem comentar o objeto
    (registry_id, post_id) = doc_id.split("/")
    return ((owner == user) or isFriendOrMember(user, registry_id))

def isAllowedToDeleteComment(user, registry_id, owner):
    # user: usuário que está tentando o acesso
    # registry_id: usuário/comunidade onde está o objeto
    # owner: dono do comentário
    # só o dono de um comentário ou o dono da comunidade podem apagá-lo
    return ((owner == user) or isUserOrOwner(user, registry_id))


"""
=======================================================================================
"""
 

def perm_type(service):
    if service in SERVICES["member"]:
        return SERVICES["member"][service]["perm_type"]
    elif service in SERVICES["community"]:
        return SERVICES["community"][service]["perm_type"]
    else:
        return ""

def has_editable_permission(service):
    if service in SERVICES["member"]:
        return SERVICES["member"][service]["editable_perm"]
    elif service in SERVICES["community"]:
        return SERVICES["community"][service]["editable_perm"]
    else:
        return False
           
            
def objectOwnerFromService(service, registry_id, obj_name):
    """
    """
    obj_id = "%s/%s" % (registry_id, obj_name)
            
    if service == "wiki":
        return wiki.model.Wiki().retrieve(obj_id).owner
        
    elif service == "file":
        return files.model.Files().retrieve(obj_id).owner
        
    elif service == "evaluation":
        return evaluation.model.Evaluation().retrieve(obj_id).owner
    
    elif service == "videoaula":
        return videoaula.model.Videoaula().retrieve_by_name_id(registry_id, obj_name).owner

    elif perm_type(service) == "service":
        return core.model.Registry().retrieve(registry_id).getOwner()
        
    else:
        return ""

     
def usersAllowedToRead(servico, registry_id, nomeobj=""):
    """ retorna lista de usuário autorizados a ler um serviço/objeto dentre os amigos/participantes de registry_id,
        mesmo que a permissão seja acesso_activ ou acesso_externo.
    """ 
    usuarios = []
    if isAUser(registry_id):
         for u in core.database.REGISTRY[registry_id]["amigos"]:
            if isAllowedToReadObject(u, servico, registry_id, nomeobj):
                usuarios.append(u)       
    else:
        for u in core.database.REGISTRY[registry_id]["participantes"]:
            if isAllowedToReadObject(u, servico, registry_id, nomeobj):
                usuarios.append(u)
    return usuarios

def isAllowedToReadObject(user, servico, registry_id, nomeobj=""):
    perm_id = "%s/%s/%s" % (servico, registry_id, nomeobj)
    
    _perm = permission.model.Permission().retrieve(perm_id)
    if not _perm: 
        if servico in ["evaluation", "quiz"]:
            # "acesso_comunidade"  
            return (isUserOrMember(user, registry_id))
        elif servico in ["question"]:
            # "acesso_privado"  
            return (isUserOrOwner(user, registry_id))
        else:
            # "acesso_activ"            
            return (user!="" and user!=None)
            
    if _perm.escopo_R == "acesso_privado":
        return (user == _perm.owner or isUserOrOwner(user, registry_id))  
          
    if _perm.escopo_R == "acesso_grupos":
        # permite acesso ao dono do objeto e ao dono/admin da comunidade
        if (user == _perm.owner or isUserOrOwner(user, registry_id)):
            return True
        
        # permite acesso aos participantes dos grupos selecionados
        _reg = core.model.Registry().retrieve(registry_id)
        if not _reg:
            return False
        for group in _perm.grupos_R:
            if user in _reg.getGroups[group]:
                return True
        return False
     
    if _perm.escopo_R == "acesso_comunidade":
        #return (isUserOrMember(user, registry_id))
        return (isFriendOrMember(user, registry_id))
                 
    if _perm.escopo_R == "acesso_activ":
        return (user!="" and user!=None)
    
    if _perm.escopo_R == "acesso_publico":
        return True
    
    return False

        
def isAllowedToWriteObject(user, servico, registry_id, nomeobj=""):
    perm_id = "%s/%s/%s" % (servico, registry_id, nomeobj)
    
    _perm = permission.model.Permission().retrieve(perm_id)
         
    if not _perm: 
        if servico in ["evaluation", "videoaula", "quiz", "question"]:
            # "acesso_privado"  
            return (isUserOrOwner(user, registry_id))       
        else:
            # "acesso_comunidade"            
            return (isUserOrMember(user, registry_id))
                    
    if _perm.escopo_W == "acesso_privado":
        return (user == _perm.owner or isUserOrOwner(user, registry_id))  
          
    if _perm.escopo_W == "acesso_grupos":
        # permite acesso ao dono do objeto e ao dono/admin da comunidade
        if (user == _perm.owner or isUserOrOwner(user, registry_id)):
            return True
        
        # permite acesso aos participantes dos grupos selecionados
        _reg = core.model.Registry().retrieve(registry_id)
        if not _reg:
            return False
        for group in _perm.grupos_W:
            if user in _reg.getGroups[group]:
                return True
        return False
     
    if _perm.escopo_W == "acesso_comunidade":
        # aqui pode ser isUserorMember pois não deixamos amigos escreverem em objetos de amigos
        return (isUserOrMember(user, registry_id))
    
    return False
        

"""
decorators
"""
class hasReadPermission(object):
    """ Exemplo de Uso: @libs.permissions.hasReadPermission ("blog")
        Verifica se o usuário logado tem permissão de leitura sobre o objeto "service_name/registry_id/obj_name".
    """
    def __init__(self, service_name):
        self.service_name = service_name
        
    def __call__(self, f):
        def wrapped_f(*args):
            user = args[0].get_current_user()
            registry_id = args[1]
            obj_name = args[2]
            if not isAllowedToReadObject(user, self.service_name, registry_id, obj_name):
                
                if not user and args[0].request.method in ("GET", "HEAD"):
                    url = args[0].get_login_url()
                    if "?" not in url:
                        if urlparse.urlsplit(url).scheme:
                            # if login url is absolute, make next absolute too
                            next_url = args[0].request.full_url()
                        else:
                            next_url = args[0].request.uri
                        url += "?" + urllib.urlencode(dict(next=next_url))
                        
                    # se não há usuário logado e o objeto não é acessível para fora do activ,
                    # redireciona para tela de login
                    args[0].redirect(url)
                    return

                # se há usuário logado e o objeto não pode ser acessado por ele, dá forbidden
                raise HTTPError(403)
                    
            f(*args)
        return wrapped_f



class canReadService(object):
    """ Exemplo de Uso: @libs.permissions.canReadService ("blog")
        Verifica se o usuário logado tem permissão de leitura sobre o serviço "service_name/registry_id".
    """
    def __init__(self, service_name):
        self.service_name = service_name
        
    def __call__(self, f):
        def wrapped_f(*args):
            user = args[0].get_current_user()
            registry_id = args[1]
            if not isAllowedToReadObject(user, self.service_name, registry_id):
                
                if not user and args[0].request.method in ("GET", "HEAD"):
                    url = args[0].get_login_url()
                    if "?" not in url:
                        if urlparse.urlsplit(url).scheme:
                            # if login url is absolute, make next absolute too
                            next_url = args[0].request.full_url()
                        else:
                            next_url = args[0].request.uri
                        url += "?" + urllib.urlencode(dict(next=next_url))
                        
                    # se não há usuário logado e o objeto não é acessível para fora do activ,
                    # redireciona para tela de login
                    args[0].redirect(url)
                    return

                # se há usuário logado e o objeto não pode ser acessado por ele, dá forbidden
                raise HTTPError(403)

            f(*args)
        return wrapped_f


class hasWritePermission(object):
    """ Exemplo de Uso: @libs.permissions.hasWritePermission ("wiki")
        Verifica se o usuário logado tem permissão de escrita sobre o objeto "service_name/registry_id/obj_name".
    """
    def __init__(self, service_name):
        self.service_name = service_name
        
    def __call__(self, f):
        def wrapped_f(*args):
            user = args[0].get_current_user()
            registry_id = args[1]
            obj_name = args[2]
            if not isAllowedToWriteObject(user, self.service_name, registry_id, obj_name):
                raise HTTPError(403)
            f(*args)
        return wrapped_f
    
class canWriteService(object):
    """ Exemplo de Uso: @libs.permissions.canWriteService ("blog")
        Verifica se o usuário logado tem permissão de escrita sobre o serviço "service_name/registry_id".
    """
    def __init__(self, service_name):
        self.service_name = service_name
        
    def __call__(self, f):
        def wrapped_f(*args):
            user = args[0].get_current_user()
            registry_id = args[1]
            if not isAllowedToWriteObject(user, self.service_name, registry_id):
                raise HTTPError(403)
            f(*args)
        return wrapped_f

        
def userOrOwnerOrObjectOwner(method):
    """ Exemplo de Uso: @libs.permissions.userOrOwnerOrObjectOwner
        Bloqueia acesso se (usuário logado não é o próprio registry_id ou se não é dono/administrador de registry_id) e
              não é dono do objeto. 
        Pega: service em args[0], registry_id em args[1] e obj_name em args[2]
    """
    #@functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        user = self.get_current_user()
        service = args[0]
        registry_id = args[1]
        if registry_id not in core.database.REGISTRY:
            raise HTTPError(404)
        
        if len(args)>2:
            obj_name = args[2]
            if not isUserOrOwner(user, registry_id) and user != objectOwnerFromService(service, registry_id, obj_name):
                raise HTTPError(403)
        else:
            if not isUserOrOwner(user, registry_id):
                raise HTTPError(403)
            
        return method(self, *args, **kwargs)
    
    return wrapper
