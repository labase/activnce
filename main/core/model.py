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

import hashlib
import urllib
import functools
from datetime import datetime
import random

try:
  from couchdb.schema import Document, TextField, IntegerField, LongField, DateTimeField, DictField, ListField, Schema, FloatField
except ImportError:
  from couchdb.mapping import Document, TextField, IntegerField, LongField, DateTimeField, DictField, ListField, FloatField
  from couchdb.mapping import Mapping as Schema

#from tornado.httpclient import HTTPError
from tornado.web import HTTPError

import database
from database import PASSWD_USER_SUSPENDED
import log.model
from log.model import _EMPTYNEWS
import log.database
import search.model
import skills.model
import permission.model
from libs.dateformat import elapsed_time, date_now, str_to_date
from config import PRIVILEGIOS, PRIV_GLOBAL_ADMIN, LOG_THREADS, DIR_RAIZ_ACTIV, LOG_THREADS_FILE


# Controle de usuários logados
USUARIOS_LOGADOS = dict()

# listas em memória para autocomplete
AUTOCOMPLETE_TAGS = {}
AUTOCOMPLETE_USERS = {}
AUTOCOMPLETE_COMMUNITIES = {}
AUTOCOMPLETE_ALL_SKILLS = []
AUTOCOMPLETE_CONFIRMED_SKILLS = []

# dicionários com as estruturas de acesso ao couchdb
# Ainda é preciso atualizar pois os cadastros utilizam estes dicionarios
_EMPTYMEMBER = lambda: dict(
          user = ""
        , passwd = ""
        , labvad_passwd = ""
        , name = ""
        , lastname = ""
        , email = ""
        , conta_google = ""
        , vinculos = []                    # da intranetUFRJ : A, P, F, email, cpf, localização, curso, etc     
        , tags = [] 
        , description = ""
        , amigos = []
        , amigos_pendentes = []
        , amigos_convidados = []
        , comunidades = []
        , comunidades_pendentes = []
        , mykeys = []
        , origin = ""                        # Pode ser: "convidado" ou "intranet"
        , privacidade = u"Pública"           # Pode ser: Pública ou Privada
        #, blog_aberto = "N"                 # Indica se o blog deste usuário 
                                             # pode ser acessado de fora da plataforma
        , services = []
        , groups = {}                        # se usuário, guarda os grupos de amigos.
                                             # se comunidade, guarda os grupos de participantes.
                                             # { "nome_grupo1": ["usuario1", "usuario2", ...],
                                             #   "nome_grupo2": ["usuario1", "usuario2", ...]
                                             # }
        , community_groups = {}              # grupos de comunidades que o usuário participa
                                             # não é utilizado nas permissões.
        , upload_quota = 10 * 1024 * 1024    # max 10 Mb
        , upload_size = 0  
        , notify = "2"  # notificações de e-mail
                        # 0 = não receber
                        # 1 = receber apenas um boletim semanal
                        # 2 = receber sempre
        , cpf = ""      # incluido para futura integração a intranet da UFRJ
        , data_cri = ""
        , data_alt = ""
        
        , suspended_passwd = ""     # copia de passwd, cpf e email se usuário for suspenso.
        , suspended_cpf = ""
        , suspended_email = ""
        , suspended_date = ""
        , reactivated_date = ""
        , reactivated_by = ""
        , type = "member"
        , subtype = ""
    )

_EMPTYCOMMUNITY = lambda: dict(
          name = ""
        , description = ""
        , conta_google = ""
        , tags = []
        , owner = ""
        , participantes_pendentes = []
        , participantes_chamados = []
        , participantes = []
        , comunidades = []                   # comunidades em que esta comunidade está incluída
        , upload_quota = 60 * 1024 * 1024    # max 60 Mb
        , upload_size = 0
        , admins = []
        , apps = {}
        , services = []
        , groups = {}                        # se comunidade, guarda os grupos de participantes.
                                             # { "nome_grupo1": ["usuario1", "usuario2", ...],
                                             #   "nome_grupo2": ["usuario1", "usuario2", ...]
                                             # }
        , privacidade = ""    # Pública ou Privada
        #, blog_aberto = "N"   # Indica se o blog deste usuário 
                              # pode ser acessado de fora da plataforma
        , participacao = ""   # Mediante Convite, Voluntária ou Obrigatória
        , data_cri = ""
        , data_alt = ""
        , type = "community"
        , subtype = ""
    )


_EMPTYDBINTRANET = lambda: dict(
          host = ""
        , user = ""
        , passwd = ""
        , database = ""
    )

# decorators globais
def administrator(method):
    """ Decorate methods with this to require administrator privilege. """
    #@functools.wraps(method)
    def wrapper(self, *args, **kwargs):
      user = self.get_current_user()
      if isMember(user, PRIV_GLOBAL_ADMIN):
            raise HTTPError(403)
      return method(self, *args, **kwargs)
     
    return wrapper


def allowedToAccess(method):
    """ Exemplo de Uso: @core.model.allowedToAccess
        Bloqueia acesso aos usuários/comunidades privadas se o usuário logado não for amigo/participante.
    """
    #@functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        user = self.get_current_user()
        registry_id = args[0]              # o primeiro parâmetro da função decorada deve ser o registry_id
        
        allowed = isAllowedToAccess(user, registry_id)
        if allowed==1:
            raise HTTPError(403)
        elif allowed==2:
            raise HTTPError(404)
        else:
            return method(self, *args, **kwargs)
    
    return wrapper


def allowedToAccessPrivNoticias(method):
    """ Exemplo de Uso: @core.model.allowedToAccessPrivNoticias
        Bloqueia acesso aos usuários/comunidades privadas se o usuário logado não for amigo/participante.
        Exceto se a comunidade for Priv_Global_Admin. Usado para permitir acesso às noticias do sistema.
    """
    #@functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        user = self.get_current_user()
        registry_id = args[0]              # o primeiro parâmetro da função decorada deve ser o registry_id
        
        if registry_id == PRIV_GLOBAL_ADMIN:
            return method(self, *args, **kwargs)
            
        allowed = isAllowedToAccess(user, registry_id)
        
        if allowed==1:
            raise HTTPError(403)
        elif allowed==2:
            raise HTTPError(404)
        else:
            return method(self, *args, **kwargs)
    
    return wrapper
   
def userOrMember(method):
    """ Exemplo de Uso: @core.model.userOrMember
        Bloqueia acesso se usuário logado não é o próprio registry_id ou se não é participante de registry_id
    """
    #@functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        user = self.get_current_user()
        registry_id = args[0]              # o primeiro parâmetro da função decorada deve ser o registry_id
        if not isUserOrMember(user, registry_id):
            raise HTTPError(403)
        return method(self, *args, **kwargs)
    
    return wrapper


def userOrOwner(method):
    """ Exemplo de Uso: @core.model.userOrOwner
        Bloqueia acesso se usuário logado não é o próprio registry_id ou se não é dono/administrador de registry_id
    """
    #@functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        user = self.get_current_user()
        registry_id = args[0]              # o primeiro parâmetro da função decorada deve ser o registry_id
        if not isUserOrOwner(user, registry_id):
            raise HTTPError(403)
        return method(self, *args, **kwargs)
    
    return wrapper

def owner(method):
    """ Exemplo de Uso: @core.model.owner
        Bloqueia acesso se usuário logado não é dono/administrador de registry_id
    """
    #@functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        user = self.get_current_user()
        registry_id = args[0]              # o primeiro parâmetro da função decorada deve ser o registry_id
        if not isOwner(user, registry_id):
            raise HTTPError(403)
        return method(self, *args, **kwargs)
    
    return wrapper


def friendOrMember(method):
    """ Exemplo de Uso: @core.model.friendOrMember
        Bloqueia acesso se usuário logado não é amigo ou se não é participante de registry_id
    """
    #@functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        user = self.get_current_user()
        registry_id = args[0]              # o primeiro parâmetro da função decorada deve ser o registry_id
        if not isFriendOrMember(user, registry_id):
            raise HTTPError(403)
        return method(self, *args, **kwargs)
    
    return wrapper

'''
class requirePrivilege(object):
    """ Exemplo de Uso: @core.model.requirePrivilege ("digitador")
        Exige que o usuário logado possua um determinado papel.
    """
    def __init__(self, priv):
        self.priv = priv
        
    def __call__(self, f):
        def wrapped_f(*args):
            user = args[0].get_current_user()
            user_data = database.REGISTRY[user]
            if self.priv not in user_data["papeis"]:
                raise HTTPError(403)
            f(*args)
        return wrapped_f
'''

class serviceEnabled(object):
    """ Exemplo de Uso: @core.model.serviceEnabled ("blog")
        Exige que o registry_id possua um determinado serviço.
    """
    def __init__(self, service_name):
        self.service_name = service_name
        
    def __call__(self, f):
        def wrapped_f(*args):
            registry_id = args[1]
            _reg = Registry().retrieve(registry_id)
            if _reg:
                if self.service_name not in _reg.getServices:
                    raise HTTPError(404)
            else:
                raise HTTPError(404)
            f(*args)
        return wrapped_f

class serviceEnabledToCommunity(object):
    """ Exemplo de Uso: @core.model.serviceEnabled ("blog")
        Exige que o registry_id possua um determinado serviço somente se ele for uma comunidade.
    """
    def __init__(self, service_name):
        self.service_name = service_name
        
    def __call__(self, f):
        def wrapped_f(*args):
            registry_id = args[1]
            _reg = Registry().retrieve(registry_id)
            if _reg:
                if isACommunity(registry_id) and self.service_name not in _reg.getServices:
                    raise HTTPError(404)
            else:
                raise HTTPError(404)
            f(*args)
        return wrapped_f


class userIsCommunityMember(object):
    """ Exemplo de Uso: @core.model.userIsCommunityMember (NOME_COMUNIDADE)
        Para multiplas comunidades, separe pelo ;
        Exige que o usuário logado seja participante de uma determinada comunidade.
    """
    def __init__(self, priv):
        self.priv = priv

    def __call__(self, f):
 
         def wrapped_f(*args):
            user = args[0].get_current_user()
            user_data = database.REGISTRY[user]
            priv_list = list(set(self.priv.split(";")))
            EHUMA = False
            for i in range(len(priv_list)):
               if priv_list[i].lstrip(";") in user_data["comunidades"]:
                    EHUMA = True
                    #if self.priv not in user_data["comunidades"]:
            if not EHUMA:
               raise HTTPError(403)
            f(*args)
         return wrapped_f


def saveAutocompleteStrings():
    global AUTOCOMPLETE_TAGS
    global AUTOCOMPLETE_USERS
    global AUTOCOMPLETE_COMMUNITIES
    global AUTOCOMPLETE_ALL_SKILLS
    global AUTOCOMPLETE_CONFIRMED_SKILLS
    
    AUTOCOMPLETE_TAGS = search.model.cloudTag()
    (AUTOCOMPLETE_ALL_SKILLS, AUTOCOMPLETE_CONFIRMED_SKILLS) = skills.model.getAllSkills()

    AUTOCOMPLETE_USERS = dict()
    for row in database.REGISTRY.view('users/partial_data'):
        AUTOCOMPLETE_USERS[row.key.encode('iso-8859-1', 'ignore')] = row.value["nome_completo"].encode('iso-8859-1', 'ignore')
             
    AUTOCOMPLETE_COMMUNITIES = dict()
    for row in database.REGISTRY.view('communities/partial_data'):
        AUTOCOMPLETE_COMMUNITIES[row.key.encode('iso-8859-1', 'ignore')] = row.value["description"].encode('iso-8859-1', 'ignore')
        
    if LOG_THREADS:
        text_file = open(DIR_RAIZ_ACTIV+LOG_THREADS_FILE, "a+")
        text_file.write("[%s] AutocompleteLoader (tags:%s; users:%s; communities:%s)\n" % (str(datetime.now()), str(len(AUTOCOMPLETE_TAGS)), str(len(AUTOCOMPLETE_USERS)), str(len(AUTOCOMPLETE_COMMUNITIES))))
        text_file.close()
        
                    
def getAutocompleteTags():
    return AUTOCOMPLETE_TAGS
    
def getAutocompleteUsers():
    return AUTOCOMPLETE_USERS

def getAutocompleteCommunities():
    return AUTOCOMPLETE_COMMUNITIES

def getAutocompleteAllSkills():
    return AUTOCOMPLETE_ALL_SKILLS   
def getAutocompleteConfirmedSkills():
    return AUTOCOMPLETE_CONFIRMED_SKILLS   
   

class ActivDB(Document):
    #_id            = <couchdb_id>
    type           = TextField() # tipo do documento: member, community, wiki, etc
    subtype        = TextField()

    # service/registry_id/name_id deve ser único
    service        = TextField() # nome do serviço: wiki,file,blog,etc  (precisa existir ??? ou pode usar somente type/subtype ???)
    registry_id    = TextField() # usuário ou comunidade onde está localizado o objeto
    name_id        = TextField() # identificador do objeto (titulo do objeto sem caracteres especiais)

    titulo         = TextField(default='') # nome(titulo) do objeto
    owner          = TextField()           # usuário que criou o objeto
    tags           = ListField(TextField())
    
    
    # relacionamento 1..n entre documentos: 
    # exemplos: no forum, um reply pertence a um tópico
    #           no activity, uma atividade pertence a um grupo
    
    # id do documento que representa o grupo ao qual este objeto pertence 
    group_id       = TextField()
    
    data_cri       = TextField()
    data_alt       = TextField()
    alterado_por   = TextField()


    @classmethod
    def registry_id_has_objects(self, registry_id):
        if database.ACTIVDB.view('registry_id/has_objects', key=[registry_id, {}]):
            return True
        else:
            return False
        
    @classmethod
    def exists(self, service, type, registry_id, name_id):
        if database.ACTIVDB.view('object/exists', key=[service, type, registry_id, name_id]):
            return True
        else:
            return False
         
    def save(self, id=None, db=database.ACTIVDB):
        if not self.id and id: self.id = id
        self.store(db)
        
    def retrieve(self, id, db=database.ACTIVDB):
        # retorna um objeto da classe ActivDB
        # para converter para um objeto correspondente ao tipo armazenado no atributo type, sobreescreva essa método
        return ActivDB.load(db, id)
            
    def delete(self, db=database.ACTIVDB):
        #db.delete(self)
        del db[self.id]          

    @classmethod
    def retrieve_by_name_id(self, service, type, registry_id, name_id):
        for row in database.ACTIVDB.view('objects/by_registry_id', key=[service, type,registry_id,name_id]):
            return row.value
        return None

    @classmethod    
    def listObjects(self, service, type, registry_id, page=None, page_size=None, tag=None):
        """ Retorna uma lista de objetos de um service/tipo/registry_id provenientes do activDB.
            Filtros:
            Se page e pagesize forem omitidos é porque a chamada deve retornar todos os objetos.
            Se tag for omitida, retorna os objetos independente das suas tags.
        """
        
        lista = []
        
        if tag:
            if page != None and page_size != None:
                for row in database.ACTIVDB.view('objects/by_registry_id_and_tag', startkey=[service, type, registry_id, tag, {}], endkey=[service, type, registry_id, tag], 
                                              descending="true", skip=(page-1)*page_size , limit=page_size):
                    obj_data = dict()
                    obj_data.update(row.value)
                                
                    lista.append(obj_data)
            else:
                for row in database.ACTIVDB.view('objects/by_registry_id_and_tag', startkey=[service, type, registry_id, tag, {}], endkey=[service, type, registry_id, tag], 
                                              descending="true"):
                    obj_data = dict()
                    obj_data.update(row.value)
                                
                    lista.append(obj_data)
                    
        else:
            if page != None and page_size != None:
                for row in database.ACTIVDB.view('objects/by_registry_id', startkey=[service, type, registry_id, {}], endkey=[service, type, registry_id], 
                                              descending="true", skip=(page-1)*page_size , limit=page_size):
                    obj_data = dict()
                    obj_data.update(row.value)
                                
                    lista.append(obj_data)
            else:
                for row in database.ACTIVDB.view('objects/by_registry_id', startkey=[service, type, registry_id, {}], endkey=[service, type, registry_id], 
                                              descending="true"):
                    obj_data = dict()
                    obj_data.update(row.value)
                                
                    lista.append(obj_data)
                 
        return lista

    @classmethod    
    def listObjectByGroup(self, service, registry_id, group_id):
        lista = []
        for row in database.ACTIVDB.view('objects/by_group', startkey=[service, registry_id, group_id], endkey=[service, registry_id, group_id, {}]):
            obj_data = dict()
            obj_data.update(row.value)        
            lista.append(obj_data)
        return lista


    @classmethod    
    def countObjectsByGroup(self, activ_id):
        """ Retorna o número de itens pertencentes a um grupo
        """
        for row in database.ACTIVDB.view('groups/total_itens',key=activ_id, group="true"):
            return row.value
        return 0
    
    @classmethod    
    def listObjectsByGroup(self, service, registry_id, page=None, page_size=None, tag=None):
        """ Retorna uma lista de objetos de um tipo/registry_id provenientes do activDB.
            Filtros:
            Se page e pagesize forem omitidos é porque a chamada deve retornar todos os objetos.
            Se tag for omitida, retorna os objetos independente das suas tags.
        """
        
        lista = []
        
        if tag:
            if page != None and page_size != None:
                for row in database.ACTIVDB.view('objects/by_group_and_tag', startkey=[service, registry_id, tag], endkey=[service, registry_id, tag, {}], 
                                              skip=(page-1)*page_size , limit=page_size):
                    obj_data = dict()
                    obj_data.update(row)
                                
                    lista.append(obj_data)
            else:
                for row in database.ACTIVDB.view('objects/by_group_and_tag', startkey=[service, registry_id, tag], endkey=[service, registry_id, tag, {}]):
                    obj_data = dict()
                    obj_data.update(row)
                                
                    lista.append(obj_data)
                    
        else:
            if page != None and page_size != None:
                for row in database.ACTIVDB.view('objects/by_group', startkey=[service, registry_id], endkey=[service, registry_id, {}], 
                                              skip=(page-1)*page_size , limit=page_size):
                    obj_data = dict()
                    obj_data.update(row)
                                
                    lista.append(obj_data)
            else:
                for row in database.ACTIVDB.view('objects/by_group', startkey=[service, registry_id], endkey=[service, registry_id, {}]):
                    obj_data = dict()
                    obj_data.update(row)
                                
                    lista.append(obj_data)
            
        return lista
    
    
    
    @classmethod    
    def listObjectsBySubtype(self, service, type, subtype, registry_id, page=None, page_size=None, tag=None):
        """ Retorna uma lista de objetos de um tipo/registry_id provenientes do activDB.
            Filtros:
            Se page e pagesize forem omitidos é porque a chamada deve retornar todos os objetos.
            Se tag for omitida, retorna os objetos independente das suas tags.
        """
        
        lista = []
        
        if tag:
            if page != None and page_size != None:
                for row in database.ACTIVDB.view('objects/by_subtype_registry_id_and_tag', startkey=[service, type, subtype, registry_id, tag, {}], endkey=[service, type, subtype, registry_id, tag], 
                                              descending="true", skip=(page-1)*page_size , limit=page_size):
                    obj_data = dict()
                    obj_data.update(row.value)
                                
                    lista.append(obj_data)
            else:
                for row in database.ACTIVDB.view('objects/by_subtype_registry_id_and_tag', startkey=[service, type, subtype, registry_id, tag, {}], endkey=[service, type, subtype, registry_id, tag],
                                                 descending="true"):
                    obj_data = dict()
                    obj_data.update(row.value)
                                
                    lista.append(obj_data)
        else:
            
            if page != None and page_size != None:
                for row in database.ACTIVDB.view('objects/by_subtype_and_registry_id', startkey=[service, type, subtype, registry_id, {}], endkey=[service, type, subtype, registry_id], 
                                              descending="true", skip=(page-1)*page_size , limit=page_size):
                    obj_data = dict()
                    obj_data.update(row.value)
                                
                    lista.append(obj_data)
            else:
                for row in database.ACTIVDB.view('objects/by_subtype_and_registry_id', startkey=[service, type, subtype, registry_id, {}], endkey=[service, type, subtype, registry_id],
                                                 descending="true"):
                    obj_data = dict()
                    obj_data.update(row.value)
                                
                    lista.append(obj_data)
         
        return lista
        
    @classmethod    
    def countObjectsByRegistryId(self, service, type, registry_id):
        for row in database.ACTIVDB.view('objects/count',key=[service, type, registry_id], group="true"):
            return row.value
        return 0

    @classmethod    
    def countObjectsBySubtype(self, service, type, subtype, registry_id):
        for row in database.ACTIVDB.view('objects/count_by_subtype',key=[service, type, subtype, registry_id], group="true"):
            return row.value
        return 0
         
    @classmethod 
    def countObjectsByRegistryIdTags(self, service, type, registry_id, tag):
        for row in database.ACTIVDB.view('objects/count_by_registry_id_and_tag', \
                                           startkey=[service, type, registry_id, tag], endkey=[service, type, registry_id, tag, {}], \
                                           group_level=1, group="true"):        
            return row.value
        return 0
     
    @classmethod
    def listAllTags(self, service, type, registry_id, tag=None):
        tags_list = []
        for row in database.ACTIVDB.view('objects/by_registry_id_and_tag', startkey = [service, type, registry_id], endkey = [service, type, registry_id, {}, {}, {}]):
            tag_found = row.key[3]
            tags_list.append(tag_found)

        if tag and tag in tags_list:
            tags_list.remove(tag)
        tags_list = sorted(set(tags_list))    
        return tags_list    
    
    
class Registry(Document):
    tags                  = ListField(TextField())                  # tags do perfil do usuário ou da comunidade
    groups                = DictField()                             # { "nomegrupo": [user1, user2, ...] }
    privacidade           = TextField(default=u"Pública")           # Pode ser: Pública ou Privada
    services              = ListField(TextField())
    #widgets               = ListField(TextField())                  # lista de widgets do painel de controle do usuário
    
    conta_google          = TextField()
    upload_quota          = IntegerField(default=10 * 1024 * 1024)  # max 10 Mb ou 60 Mb
    upload_size           = IntegerField(default=0)  
    data_cri              = TextField()
    data_alt              = TextField()

    type                  = TextField()
    subtype               = TextField()
    
    @property
    def getServices(self):
        return self.services

    @property
    def getGroups(self):
        return self.groups

    def getType(self):
        if self.type=="member":
            if self.subtype=="suspended":
                return "suspended"
            else:
                return "member"
        else:
            return self.type
                                 
    def isAUser(self, active_user=True):
        if active_user:
            # verifica se self é um usuário ativo
            return self.getType() == "member"
        else:
            # verifica se self é usuário (ativo ou inativo)
            return self.getType() in ["member", "supended"]

    def isSuspended(self):
        return self.getType() == "suspended"
            
    def isACommunity(self):
        return self.getType() == "community"
           
    def isOwner(self, user):
        if isinstance(self, Member):
            return user == self.id
        elif isinstance(self, Community):
            return user == self.owner or user in self.admins
        else:
            return False

    def getOwner(self):
        # Se registry_id é usuário retorna registry_id (registry_id de member não tem owner).
        # Senão retorna a propriedade owner
        
        if isinstance(self, Member):
            return self.id
        elif isinstance(self, Community):
            return self.owner

    def isUserOrMember(self, user):
        # Verifica se user é o próprio registry_id ou se é participante de registry_id
        if isinstance(self, Member):
            return user == self.id
        elif isinstance(self, Community):
            return self.isMember(user)
        else:
            return False
              
    def updateUploadSize(self, size):
        self.upload_size += size
        self.save()
        
    def save(self, id=None, db=database.REGISTRY):
        if not self.id and id: self.id = id
        self.store(db)
        
    def delete(self, db=database.REGISTRY):
        #db.delete(self)
        del db[self.id]

    
    def retrieve(self, id, db=database.REGISTRY):
        # retorna um objeto da classe Member ou Community dependendo do que estiver armazenado no registry com esse id
        _tmp = Registry.load(db, id)
        if _tmp: 
            if _tmp.isAUser():
                _tmp.__class__ = Member 
            elif _tmp.isACommunity():
                _tmp.__class__ = Community 
            elif _tmp.isSuspended():
                _tmp = None 
                
        return _tmp
            
        
            

class Member(Registry):
    user                  = TextField() 
    passwd                = TextField()
    labvad_passwd         = TextField()
    name                  = TextField()
    lastname              = TextField()
    email                 = TextField(default="")
    description           = TextField(default="")
    amigos                = ListField(TextField())
    amigos_pendentes      = ListField(TextField())
    amigos_convidados     = ListField(TextField())
    comunidades           = ListField(TextField())
    comunidades_pendentes = ListField(TextField())
    community_groups      = DictField()
    vinculos              = ListField(DictField())  # lista de dicionario de vinculos com uam instituicao com seguintes as chaves:
                                                    # vinculo =  P, F, A - professor, aluno ou funcionario; dre, ou siape; instituicao (ex:ufrj);
                                                    # tipo (grad, pos), se A; emailufrj; cpfufrj; ativo (0 ou 1); localizacao ou curso;
    mykeys                = ListField(TextField())
    notify                = TextField(default="2")  # notificações de e-mail
                                                    # 0 = não receber
                                                    # 1 = receber apenas um boletim semanal
                                                    # 2 = receber sempre
    cpf                   = TextField(default="")   # incluido para futura integração a intranet da UFRJ
    origin                = TextField()             # origem do cadastro deste usuário: "convidado" ou "intranet"

    suspended_passwd      = TextField()
    suspended_cpf         = TextField()
    suspended_email       = TextField()
    suspended_date        = TextField()
    reactivated_date      = TextField()
    reactivated_by        = TextField()
    show_tutorial         = TextField(default="S")

    
    @classmethod
    def createUser(self, newuser, pwd, name, lastname, priv):
        """ Factory para criar usuário da plataforma """
        _usr = Member().retrieve(newuser)
        if not _usr:
            _usr = Member(user=newuser)
            hash = hashlib.md5()
            hash.update(newuser+pwd) 
            _usr.type = "member"
            _usr.passwd = hash.hexdigest()
            _usr.name = name
            _usr.lastname = lastname
            _usr.comunidades = []
            _usr.privacidade = priv
            _usr.save(id=newuser)
        return _usr
 

    def getFriendsList(self, group="", page=None, page_size=None, user=None):
        # retorna lista de (user_id, full_name, online, chat) dos amigos de self

        tem_amigos = False
        for row in database.REGISTRY.view('users/friends',startkey=[self.id],endkey=[self.id, {}]):
            (registry_id, type) = row.key
            if type == 0:
                tem_amigos = True
                amigos = row.value["friends"]
                dados_amigos = [None] * len(amigos)
            else:
                if tem_amigos and ((group and row.value["user"] in self.groups[group]) or group==""):
                    if row.value["user"] in amigos:
                        pos = amigos.index(row.value["user"])
                        online = isOnline(row.value["user"])
                        chat = "/chat/"+row.value["user"] if user and online and isFriend(user,row.value["user"]) else ""
                        dados_amigos[pos] = (row.value["user"], row.value["full_name"], online, chat)
       
        if tem_amigos:
            # remove da lista usuários excluídos da plataforma
            dados_amigos = [amigo for amigo in dados_amigos if amigo!=None] 
            num_amigos = len(dados_amigos)
            # e retorna somente a página solicitada
            inicio = (page-1)*page_size if page and page_size else 0
            fim = inicio + page_size if page and page_size else len(dados_amigos)
            return (num_amigos, dados_amigos[inicio:fim])
        
        else:
            # usuário não tem amigos ou é um usuário excluído
            return(0,[])
    
    
    def getCommunitiesList(self, group="", page=None, page_size=None):
        # retorna lista de (id_community, description, is_owner) das comunidades de self

        for row in database.REGISTRY.view('users/communities',startkey=[self.id],endkey=[self.id, {}]):
            (registry_id, type) = row.key
            if type == 0:
                comunidades = row.value["communities"]
                dados_comunidades = [None] * len(comunidades)
            else:
                if (group and row.value["community"] in self.community_groups[group]) or group=="":
                    if row.value["community"] in comunidades:
                        pos = comunidades.index(row.value["community"])
                        dados_comunidades[pos] = (row.value["community"], row.value["description"], self.id==row.value["owner"])
       
        # remove da lista comunidades posições não preenchidas porque não pertencem ao grupo
        dados_comunidades = [comu for comu in dados_comunidades if comu!=None] 
        inicio = (page-1)*page_size if page and page_size else 0
        fim = inicio + page_size if page and page_size else len(dados_comunidades)
        return dados_comunidades[inicio:fim]
                                
        
    def getMyApplications(self):  
        # retorna dicionário com todas as aplicações de privilégios que um usuário pode executar
        priv_dict = {}
        for priv in PRIVILEGIOS:
            if priv in self.comunidades:
                priv_dict.update(PRIVILEGIOS[priv]['apps'])
        return priv_dict
    
        
    """     
    def countFriends(self, group=""):
        
        # é preciso excluir os usuários suspensos dessa lista...
        # como fazer isso???        
        # idem para Community.countMembers()

        if group:
            return len(self.groups[group])
        else:
            return len(self.amigos)
    """
                 
    def countCommunities(self, group=""):
        if group:
            return len(self.community_groups[group])
        else:
            return len(self.comunidades)

    def addCommunity(self, community_id):
        if community_id not in self.comunidades:
            self.comunidades.append(community_id)
            self.save()
            
    def delCommunity(self, community_id):
        if community_id in self.comunidades:
            # remove a comunidade da lista de comunidades do usuário
            self.comunidades.remove(community_id)
            
            # remove a comunidade dos grupos de comunidades do usuário
            for grupo in self.community_groups:
                if community_id in self.community_groups[grupo]:
                    self.community_groups[grupo].remove(community_id)

            self.save()
            
    def addFriend(self, friend_id):
        pass

    def addCommunityGroup(self, grupo):
        if self.community_groups:
            self.community_groups[grupo] = []
        else:
            self.community_groups = {grupo: []}
        self.save()
        
    def delCommunityGroup(self, grupo):
        if self.community_groups and grupo in self.community_groups:
            del self.community_groups[grupo]
            self.save()
            return True
        else:
            return False

    def getFullName(self):
        return self.name+" "+self.lastname
    
    def getShowTutorial(self):
        if self.show_tutorial:
            return self.show_tutorial
        else:
            return "S"
            
    def retrieve(self, id, db=database.REGISTRY):
        return Member.load(db, id)
    

class Community(Registry):
    name                    = TextField() 
    description             = TextField() 
    owner                   = TextField() 
    participantes_pendentes = ListField(TextField())
    participantes_chamados  = ListField(TextField())   # lista de emails que ainda não são usuários da plataforma,
                                                       # que foram chamados pelo dono da comunidade
    participantes           = ListField(TextField())
    comunidades             = ListField(TextField())   # comunidades em que esta comunidade está incluída
    admins                  = ListField(TextField())
    #apps                    = ListField(ListField(TextField()))
    apps                    = DictField()
    participacao            = TextField()  # Mediante Convite, Voluntária ou Obrigatória

    @property
    def communityOwner(self):
        return self.owner
    
    @classmethod
    def createPrivilege(self, priv_nome, priv_desc, priv_apps, priv_services, owner):
        """ Factory para criar comunidade obrigatória associada a um privilégio """
        _prv = Community().retrieve(priv_nome)
        if not _prv:
            _prv = Community(name=priv_nome)
            _prv.type = "community"
            _prv.subtype = "privilege"
            
            _prv.description = priv_desc
            _prv.owner = owner.user
            _prv.participantes = [owner.user]
            _prv.privacidade = "Privada"
            _prv.participacao = u"Obrigatória"
            _prv.apps = priv_apps
            _prv.services = priv_services
            _prv.save(id=priv_nome)
            
        else:
            _prv.owner = owner.user
            _prv.apps = priv_apps
            _prv.services = priv_services
            if owner.user not in _prv.participantes:
                _prv.participantes.append(owner.user)
            _prv.save()
            
        # inclui este privilégio na lista de comunidades do priv_owner
        owner.addCommunity(priv_nome)
        return _prv

    @classmethod
    def getCalledCommunities(self, email):
        # retorna lista de (email, id_community, participacao) das comunidades pras quais o email foi chamado
        lista = []
        for row in database.REGISTRY.view('called/by_email',startkey=[email],endkey=[email, {}]):
            lista.append(row.key)
        return lista
            
    def retrieve(self, id, db=database.REGISTRY):
        return Community.load(db, id)
            
    def delMember(self, member_id):
        if member_id in self.participantes:
            self.participantes.remove(member_id)
            self.save()
            
    def getMembersList(self, group="", page=None, page_size=None, return_is_owner=True):
        # retorna lista de (user, nome_completo, is_admin) dos participantes de self
        _isOwner = lambda user: user==self.owner or user in self.admins

        dados_participantes = []
        for row in database.REGISTRY.view('communities/members',startkey=[self.id],endkey=[self.id, {}]):
            (registry_id, type) = row.key
            if type == 0:
                participantes = row.value["members"]
                dados_participantes = [None] * len(participantes)
            elif (group and row.value["user"] in self.groups[group]) or group=="":
                if row.value["user"] in participantes:
                    pos = participantes.index(row.value["user"])
                    if return_is_owner:
                        dados_participantes[pos] = (row.value["user"], row.value["full_name"], _isOwner(row.value["user"]))
                    else:
                        dados_participantes[pos] = (row.value["user"], row.value["full_name"])
       
        # remove da lista usuários excluídos da plataforma
        dados_participantes = [participante for participante in dados_participantes if participante!=None]
        num_participantes = len(dados_participantes) 
        inicio = (page-1)*page_size if page and page_size else 0
        fim = inicio + page_size if page and page_size else len(dados_participantes)
        
        return (num_participantes, dados_participantes[inicio:fim])

        
    """
    def countMembers(self, group=""):
        if group:
            return len(self.groups[group])
        else:
            return len(self.participantes)
    """

    def isMedianteConvite(self): 
        # verifica se community_id é mediante convite
        return self.participacao == u"Mediante Convite"
    
    def isObrigatoria(self):  
        # verifica se community_id é obrigatória
        return self.participacao == u"Obrigatória"
    
    def isVoluntaria(self):  
        # verifica se community_id é voluntária
        return self.participacao == u"Voluntária"
            
    def isMember(self, user):
        return user in self.participantes
    
    
class ForgottenPasswd(Document):
    
    user              = TextField() 
    data_pedido       = TextField() 
    data_execucao     = TextField(default="") 
    ip                = TextField(default="")
               
    def save(self, id=None, db=database.FORGOTTENPASSWD):
        if not self.id and id: self.id = id
        self.store(db)
        
    def retrieve(self, id, db=database.FORGOTTENPASSWD):
        return ForgottenPasswd.load(db, id)
    
    def delete(self, db=database.FORGOTTENPASSWD):
        del db[self.id]
        
   
   
def isAllowedToAccess(user, registry_id):
    # Verifica acesso a usuários/comunidades privadas se o usuário logado não for amigo/participante.
    _reg = Registry().retrieve(registry_id)
    if _reg:
        if _reg.isAUser():
            if _reg.privacidade=="Privada" and user != registry_id and user not in _reg.amigos:
                return 1 # acesso negado para usuário privado
            
        elif _reg.privacidade=="Privada" and user not in _reg.participantes:
                return 1 # acesso negado para comunidade privada
    else:
        return 2 # registry_id inexistente ou suspenso

    return 0 # acesso permitido

        
def isMember(user, community_id):
    # Verifica se um usuário é participante de uma comunidade
    if database.REGISTRY.view('users/ismemberof',key=[user, community_id]):
        return True
    else: 
        return False

def isUserOrMember(user, registry_id):
    # Verifica se user é o próprio registry_id ou se é participante de registry_id
    return (user == registry_id or isMember(user, registry_id))
    
def isFriend(user, registry_id):
    # Verifica se o user está na lista de amigos de registry_id
    if database.REGISTRY.view('users/isfriend',key=[user, registry_id]):
        return True
    else: 
        return False

def isFriendOrMember(user, registry_id):
    return (isFriend(user, registry_id) or \
            isUserOrMember(user, registry_id))

def isOwner(user, registry_id):
    # Verifica se o user é dono ou admin da comunidade registry_id
    if database.REGISTRY.view('users/isowner',key=[user, registry_id]):
        return True
    else:
        return False

def isUserOrOwner(user, registry_id):
    return (user == registry_id or isOwner(user, registry_id))

def ifExists(registry_id, user):
    # Retorna registry_id se existe em database.REGISTRY, 
    # caso contrário, retorna user.
    return registry_id if registry_id in database.REGISTRY else user

def emailExists(email):
    # Verifica se já existe algum usuário cadastrado com um determinado email
    if database.REGISTRY.view('users/by_email',key=email):
        return True
    else: 
        return False

def usersByEmail(email):
    # Retorna lista de registry_id's dos usuários encontrados no cadastro que tenham um determinado email
    # Obs: atualmente o cadastro não permite mais a entrada de um novo usuário com um email já cadastrado,
    # mas como antigamente isso era possível, existem alguns casos de usuários diferentes com um mesmo email
    # no registry.
    user_list = []
    for row in database.REGISTRY.view('users/by_email',key=email):
        user_list.append (row.value)
    return user_list

def usersByCPF(cpf):
    # Retorna lista de registry_id's dos usuários encontrados no cadastro que tenham um determinado CPF
    user_list = []
    for row in database.REGISTRY.view('users/by_cpf',key=cpf):
        user_list.append (row.value)
    return user_list

def registryIdExists (registry_id, caseInsensitive=True):
    if caseInsensitive:
        if database.REGISTRY.view('registry/exists', key=registry_id.lower()):
            return True
        else: 
            return False

    else:
        return registry_id in database.REGISTRY
    
def isACommunity(community_id):
    if database.REGISTRY.view('communities/exists', key=community_id):
        return True
    else: 
        return False

def isAUser(registry_id):
    if database.REGISTRY.view('users/exists', key=registry_id):
        return True
    else: 
        return False

def getType(registry_id):
    """ retorna tupla (type, privacidade) ou None se o registry_id não existir """
    
    for row in database.REGISTRY.view('registry/type', key=registry_id):
        if row.value["type"]=="member":
            if row.value["subtype"]=="suspended":
                return ("suspended", row.value["privacidade"])
            else:
                return ("member", row.value["privacidade"])
        else:
            return (row.value["type"], row.value["privacidade"]) 
    return None

def isOnline(user, time_since_last_request=60*15):
    # por defualt, a partir de 15 minutos de inatividade é considerado offline
    if user in USUARIOS_LOGADOS:
        tempo = elapsed_time(USUARIOS_LOGADOS[user])
        return not tempo.days and tempo.seconds <= time_since_last_request
    else:
        return False

def sortByLoginTime(list_users):
    # ordena pelo menor tempo desde o último acesso
    # Se o usuario nunca acessou, assume dia 01/01/1970.
    def data_login(member): 
        if member in USUARIOS_LOGADOS:
            return str_to_date(USUARIOS_LOGADOS[member])
        else:
            for row in log.database.LOG.view('log/log_list',startkey=[member, {}], endkey=[member], descending="true", limit=1):
                return str_to_date(row.key[1])
            return str_to_date("1970-01-01 00:00:00.000000")      
        
    my_list = [ (member, data_login(member)) for member in list_users ]
    
    #Ordenando pela menor data
    sorted_list = sorted(my_list, key =lambda  x: x[1], reverse=True )
    
    return [member[0] for member in sorted_list]
 
def sortCommunitiesByAccessTime(list_communities):
    # ordena pelo menor tempo desde o último acesso
    # Se a comunidade nunca foi acessada, assume dia 01/01/1970.
    def data_access(comu): 
        for row in log.database.LOG.view('log/log_by_object',startkey=[comu, {}], endkey=[comu], descending="true", limit=1):
            return str_to_date(row.key[1])
        return str_to_date("1970-01-01 00:00:00.000000")
        
    my_list = [ (comu, data_access(comu)) for comu in list_communities ]
    
    #Ordenando pela menor data
    sorted_list = sorted(my_list, key =lambda  x: x[1], reverse=True )
    
    return [comu[0] for comu in sorted_list]

    
def onlineUsers(community_id):                      # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    users = []
    if community_id in database.REGISTRY:
        for user in database.REGISTRY[community_id]["participantes"]:
            if user not in users and isOnline(user):
                users.append(user)
    return users

