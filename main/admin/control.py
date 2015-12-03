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

import time
from datetime import datetime, date
import string
from string import upper
from random import choice
import smtplib
import operator
from operator import itemgetter
import re

import tornado.web
from tornado.web import HTTPError
import tornado.template

from core.dispatcher import BaseHandler, HANDLERS, URL_TO_PAGETITLE, \
                            NOMEUSERS, \
                            FILENAMECHARS, PAGENAMECHARS, \
                            sortedKeys_ignorecase
import core.model
from core.model import _EMPTYMEMBER, _EMPTYCOMMUNITY
from core.model import isOnline
from libs.dateformat import short_datetime

import core.database
from config import PRIV_SUPORTE_ACTIV, PRIV_GLOBAL_ADMIN

import skills.model
import skills.database
from _abcoll import ItemsView
''' importa definição do tutorial deste módulo, se existir _tutorial.py '''
from config import TUTORIAL
try:
    import _tutorial
except ImportError:
    pass

_NUMERO_FMT = "([\d]+$)"

class ListUsersHandler(BaseHandler):
    ''' Busca de usuários Tonomundo '''
    
    @tornado.web.authenticated
    @core.model.userIsCommunityMember (PRIV_SUPORTE_ACTIV)
    def get (self):
        user = self.get_current_user()
        self.render("modules/admin/list-users-form.html", REGISTRY_ID=PRIV_SUPORTE_ACTIV, \
                    MSG="",\
                    NOMEPAG="cadastro")
        
    @tornado.web.authenticated
    @core.model.userIsCommunityMember (PRIV_SUPORTE_ACTIV)
    def post(self):
        user = self.get_current_user()
        tipo_busca = self.get_argument("tipo_busca","")
        editar = True
        users_dict = dict()
        msg = ""
        
        if tipo_busca=="simples":
            login = self.get_argument("login","")

            if not login:
                msg = u"Campo login não preenchido."
            else:
                user_data = _EMPTYMEMBER()
                if login in core.database.REGISTRY:
                    user_data.update(core.database.REGISTRY[login])
                    
                    fullname = user_data["name"]+ " " + user_data["lastname"]
                    #strPapeis = ' ' + ' '.join(user_data["papeis"]) + ' '
                    #users_dict[login] = [fullname, user_data["email"], strPapeis]
                    users_dict[login] = [fullname, user_data["email"]]

        if tipo_busca=="avancada":
            email = self.get_argument("email","")
            nome = self.get_argument("nome","")
            
            if (not email) and (not nome):
                msg = "Campos nome e email não preenchidos." 
            else:
                map_fun = """
                        function(doc) {
                            var fullname = doc.name+' '+doc.lastname;
                            var achou;
                            if (doc.passwd){
                                // Busca pelo email
                                if ('%s'!="")
                                    achou = (doc.email=='%s')
                                else
                                    achou = true
                                if (!achou) return;
                                
                                // Busca pelo nome
                                if ('%s'!="")
                                    achou = fullname.toLowerCase().indexOf('%s'.toLowerCase())>=0;
                                else
                                    achou = true
                                if (!achou) return;
                                import skills.model
                                    
                                emit(doc.user, [fullname, doc.email]); 
                            }
                        }"""   % (email, email, nome, nome)
    
                resultado = core.database.REGISTRY.query(map_funmedia_niveis_habilidades = "oi")
                for row in resultado:
                    users_dict[row.key] = row.value

        self.render("modules/admin/list-user.html", REGISTRY_ID=PRIV_SUPORTE_ACTIV, USERS=users_dict, \
                    EDITAR=editar, MSG=msg,\
                    NOMEPAG="cadastro")


class OnlineUsersHandler(BaseHandler):
    ''' Listagem de usuários online '''
    
    @tornado.web.authenticated
    @core.model.userIsCommunityMember (PRIV_SUPORTE_ACTIV)
    def get (self):
        user = self.get_current_user()
        
        logados = []
        for logado in core.model.USUARIOS_LOGADOS:
            # usuários que acessaram nos últimos 15 minutoa
            if isOnline(logado):
                logados.append((logado, \
                                short_datetime(core.model.USUARIOS_LOGADOS[logado]), "green"))

            # usuários que acessaram nos últimos 60 minutoa
            if isOnline(logado, time_since_last_request=60*60) and not [item for item in logados if item[0] == logado]:
                logados.append((logado, \
                                short_datetime(core.model.USUARIOS_LOGADOS[logado]), "yellow"))
                
            
        #logados = [(logado, short_datetime(core.model.USUARIOS_LOGADOS[logado])) for logado in core.model.USUARIOS_LOGADOS if isOnline(logado, time_since_last_request=60*60)]
        logados.sort(key=itemgetter(1), reverse=True)
        self.render("modules/admin/online-users.html", REGISTRY_ID=PRIV_SUPORTE_ACTIV, MSG="",\
                    NOMEPAG="cadastro", LOGADOS=logados)


class ListCommunitiesActHandler(BaseHandler):
    ''' Lista Das Comunidades do Activ '''
    @tornado.web.authenticated
    @core.model.userIsCommunityMember (PRIV_SUPORTE_ACTIV)
    def get (self):
        user = self.get_current_user()
        communities_dict = dict()
        for row in core.database.REGISTRY.view('communities/partial_data_of_all', None):
            communities_dict[row.key] = [row.value["description"], row.value["owner"], row.value["privacidade"], row.value["participacao"]]

        self.render("modules/admin/list-communities.html", REGISTRY_ID=PRIV_SUPORTE_ACTIV, COMMUNITIES=communities_dict, \
                    SORTEDKEYS=sortedKeys_ignorecase, MSG="",\
                    NOMEPAG="cadastro")


class FileQuotaHandler(BaseHandler):
    ''' Altera quota de arquivos de um usuário/comunidade '''
    
    @tornado.web.authenticated
    @core.model.userIsCommunityMember (PRIV_SUPORTE_ACTIV)
    def get (self, registry_id):
        user = self.get_current_user()
        
        _registry = core.model.Registry().retrieve(registry_id)
        if not _registry:
            raise HTTPError (404)
            return
        
        self.render("modules/admin/upload-quota.html", \
                    REGISTRY_ID=PRIV_SUPORTE_ACTIV, MSG="",\
                    REGISTRY_DATA=_registry, \
                    NOMEPAG="cadastro")

    @tornado.web.authenticated
    @core.model.userIsCommunityMember (PRIV_SUPORTE_ACTIV)
    def post(self, registry_id):
        user = self.get_current_user()
        
        _registry = core.model.Registry().retrieve(registry_id)
        if not _registry:
            raise HTTPError (404)
            return
        
        nova_quota = self.get_argument("nova_quota","")
        if nova_quota == "":
            msg = u"Nova quota de upload não preenchida."
        elif re.match(_NUMERO_FMT, nova_quota) == None:
            msg = u"Utilize um número inteiro de MB na nova quota."
        elif int(nova_quota)*1024*1024 < int(_registry.upload_size):
            msg = u"Nova quota deve ser maior ou igual ao espaço já utilizado."
        else:
            _registry.upload_quota = int(nova_quota)*1024*1024
            _registry.save()
            msg = u"Quota de upload de arquivos alterada com sucesso."
            
        self.render("modules/admin/upload-quota.html", \
                    REGISTRY_ID=PRIV_SUPORTE_ACTIV, MSG=msg,\
                    REGISTRY_DATA=_registry, \
                    NOMEPAG="cadastro")

class TotalUsersHandler(BaseHandler):
    ''' Lista Total de usuários do Activ '''
    @tornado.web.authenticated
    @core.model.userIsCommunityMember (PRIV_GLOBAL_ADMIN)
    def get (self):
        user = self.get_current_user()
        
        total_dict = dict()
        
        for row in core.database.REGISTRY.view('users/by_origin', group="true"):
            total_dict[row.key] = row.value
            
        
        self.render("modules/admin/list-totalusers.html", REGISTRY_ID=PRIV_GLOBAL_ADMIN, TOTAL=total_dict, \
                    MSG="",\
                    NOMEPAG="cadastro")
      
        
class MyAppsHandler(BaseHandler):
    ''' Lista todos os privilégios do usuário logado '''
    @tornado.web.authenticated
    
    def get (self):
        user = self.get_current_user()
        
        self._member = core.model.Member().retrieve(user)
        apps = self._member.getMyApplications()
          
        self.render("modules/admin/list-apps.html", REGISTRY_ID=user, \
                    APPS=apps, \
                    MSG="",\
                    NOMEPAG="cadastro")   
     
                        
class AppsHandler(BaseHandler):
    ''' Lista todos os privilégios da comunidade registry_id '''
    @tornado.web.authenticated
    @core.model.userOrMember
        
    def get (self, registry_id):
        if core.model.isACommunity(registry_id):
            self.render("modules/admin/list-apps.html", REGISTRY_ID=registry_id, \
                        MSG="",\
                        NOMEPAG="cadastro")           
        else:
            raise HTTPError(404)      
              
class SkillStatsHandler(BaseHandler):
    ''' Lista algumas estatísticas das habilidades dos usuários do Activ '''
    @tornado.web.authenticated
    @core.model.userIsCommunityMember (PRIV_GLOBAL_ADMIN)
    def get (self):
        num_usuarios = 0
        num_habilidades_distintas = 0
        total_habilidades = 0
        num_confirmacoes = 0
        habils_por_usuario = []
        num_usuarios_formacao = 0
        num_usuarios_experiencias = 0
        num_usuarios_lattes = 0
        num_producoes = 0
        for row in skills.database.SKILL.view('skill/by_user'):
            if row.value["habilidades"] or row.value["habilidades_pendentes"] or row.value["habilidades_recusadas"] or row.value["habilidades_invalidas"]: #Esconder usuários antigos, que não possuem habilidades em nenhuma das listas, mas possuem formações/experiências
                num_usuarios += 1
                if len(row.value["formacao"]) > 0:
                    num_usuarios_formacao += 1
                if len(row.value["experiencias"]) > 0:
                    num_usuarios_experiencias += 1
                if len(row.value["producoes"]) > 0:
                    num_usuarios_lattes += 1
                    num_producoes += len(row.value["producoes"])
                for habil in row.value["habilidades"]:
                    total_habilidades += 1
                    for user in habil["usuarios_referencia"]:
                        num_confirmacoes += 1
                for pend in row.value["habilidades_pendentes"]:
                    total_habilidades += 1
                    for user in pend["usuarios_referencia"]:
                        num_confirmacoes += 1
                for recusada in row.value["habilidades_recusadas"]:
                    total_habilidades += 1
                    for user in recusada["usuarios_referencia"]:
                        num_confirmacoes += 1
                habils_por_usuario.append((row.value["owner"], len(row.value["habilidades"]), len(row.value["habilidades_pendentes"]), len(row.value["habilidades_recusadas"]), len(row.value["habilidades_invalidas"]) ))
        
        num_habilidades_distintas = len(core.model.getAutocompleteAllSkills())
        
        self.render("modules/admin/list-skillstats.html", REGISTRY_ID=PRIV_GLOBAL_ADMIN, \
                    MSG="", NUM_USUARIOS=num_usuarios, NUM_HABILIDADES=num_habilidades_distintas, \
                    NUM_CONFIRMACOES=num_confirmacoes, HABILS_POR_USUARIO=habils_por_usuario, \
                    TOTAL_HABILIDADES=total_habilidades, NUM_USUARIOS_FORMACAO=num_usuarios_formacao,\
                    NUM_USUARIOS_EXPERIENCIAS=num_usuarios_experiencias, NUM_USUARIOS_LATTES=num_usuarios_lattes, \
                    NUM_PRODUCOES=num_producoes, \
                    NOMEPAG="cadastro")

class UserSkillsHandler(BaseHandler):
    ''' Lista habilidades e estatísticas de um usuário do Activ '''
    @tornado.web.authenticated
    @core.model.userIsCommunityMember (PRIV_GLOBAL_ADMIN)
    def get (self, user):
        habilidades = [] #Lista de dicionários com as informações do campo habilidades do banco de dados skill
        niveis_habilidades = [] #Lista apenas com os níveis das habilidades, para cálculo de média
        habilidades_pendentes = [] #Lista de dicionários com as informações do campo habilidades_pendentes do banco de dados skill
        habilidades_recusadas = [] #Lista de dicionários com as informações do campo habilidades_recusadas do banco de dados skill
        habilidades_invalidas = [] #Lista de dicionários com as informações do campo habilidades_invalidas do banco de dados skill
        for row in skills.database.SKILL.view('skill/by_user', key=[user]): #Olhando o banco e populando as listas
            for item in row.value["habilidades"]:
                habilidades.append(item)
                niveis_habilidades.append(item["nivel_habilidade"])
            for item in row.value["habilidades_pendentes"]:
                habilidades_pendentes.append(item)
            for item in row.value["habilidades_recusadas"]:
                habilidades_recusadas.append(item)
            for item in row.value["habilidades_invalidas"]:
                habilidades_invalidas.append(item)
                
        lista_sugeridas = [] #Lista apenas com os nomes das habilidades sugeridas 
        dict_sugeridas = dict() #Dict com os campos a serem adicionados na lista habilidades_sugeridas
        niveis_sugeridas = [] #Lista com níveis de habilidades sugeridas para posterior cálculo de média
        habilidades_sugeridas = [] #Lista de dicionários com todos os campos de habilidades sugeridas
        for row in skills.database.SKILL.view('skill/user_suggested', key=user): #Checa o banco por habilidades sugeridas pelo usuário user. Rows descritas abaixo:
            #row.key é o usuário que fez a sugestão das habilidades
            #row.id contém o usuário alvo das sugestões
            #row.value["nome_habilidade"] conta com o nome da habilidade sugerida
            #row.value["nivel_habilidade"] conta com o nível sugerido para a habilidade
            #row.value["tipo"] diz se em qual lista a habilidade está no usuário alvo. Ou seja, se é habilidade, habilidade_pendente, recusada ou inválida
            #É necessário condensar essas informações para serem enviadas corretamente ao template, conforme abaixo:
            if row.value["nome_habilidade"] not in lista_sugeridas: #Checa se a habilidade já foi sugerida a outro usuário ou é a primeira vez que essa sugestão é encontrada
                #Primeira vez desta sugestão
                lista_sugeridas.append(row.value["nome_habilidade"]) #Adiciona à lista de sugestões já feitas
                dict_sugeridas["nome_habilidade"] = row.value["nome_habilidade"]
                dict_sugeridas["sugestoes"] = [] #Prepara lista que receberá todas as sugestões feitas por user dessa habilidade em específico
                dict_temp = dict()
                dict_temp["usuario"] = row.id
                dict_temp["nivel"] = row.value["nivel_habilidade"]
                niveis_sugeridas.append(row.value["nivel_habilidade"])
                dict_temp["tipo"] = row.value["tipo"]
                dict_sugeridas["sugestoes"].append(dict_temp)
                habilidades_sugeridas.append(dict_sugeridas)
                dict_temp = {}
                dict_sugeridas = {}
            else:
                #Habilidade já sugerida anteriormente
                for item in habilidades_sugeridas: 
                    if item["nome_habilidade"] == row.value["nome_habilidade"]: #Procurando habilidade para alterar o campo sugestões...
                        dict_sugeridas = item
                        if (len(habilidades_sugeridas) == 1):
                            habilidades_sugeridas = []
                        else:
                            habilidades_sugeridas.remove(item)
                        dict_temp = dict()
                        dict_temp["usuario"] = row.id
                        dict_temp["nivel"] = row.value["nivel_habilidade"]
                        niveis_sugeridas.append(row.value["nivel_habilidade"])
                        dict_temp["tipo"] = row.value["tipo"]
                        dict_sugeridas["sugestoes"].append(dict_temp)
                        habilidades_sugeridas.append(dict_sugeridas)
                        dict_temp = {}
                        dict_sugeridas = {}
                        break
        
        #Cálculo das médias de níveis de habilidades
        media_habilidades = skills.model.Skill.CalculaMediaNiveis(niveis_habilidades)
        media_sugeridas = skills.model.Skill.CalculaMediaNiveis(niveis_sugeridas)
            
        self.render("modules/admin/list-user-skills.html", REGISTRY_ID=PRIV_GLOBAL_ADMIN, \
                    MSG="", USER=user, HABILIDADES=habilidades, \
                    HABILIDADES_PENDENTES=habilidades_pendentes, HABILIDADES_RECUSADAS=habilidades_recusadas, \
                    HABILIDADES_INVALIDAS=habilidades_invalidas, HABILIDADES_SUGERIDAS=habilidades_sugeridas,\
                    MEDIA_HABILIDADES=media_habilidades, MEDIA_SUGERIDAS=media_sugeridas, \
                    NOMEPAG="cadastro")        

class SkillUsersHandler(BaseHandler):
    ''' Lista habilidades e estatísticas de um usuário do Activ '''
    @tornado.web.authenticated
    @core.model.userIsCommunityMember (PRIV_GLOBAL_ADMIN)
    def get (self):
        
        lista_habilidades = []
        dict_habilidades = dict()
        habilidades_mapeadas = []
        for row in skills.database.SKILL.view('skill/users_by_skill'):
            if row.key not in lista_habilidades:
                lista_habilidades.append(row.key)
                dict_habilidades["nome_habilidade"] = row.key
                dict_habilidades["usuarios"] = []
                dict_habilidades["usuarios"].append(row.id)
                habilidades_mapeadas.append(dict_habilidades)
                dict_habilidades = {}
            else:
                for item in habilidades_mapeadas:
                    if item["nome_habilidade"] == row.key:
                        dict_habilidades = item
                        if len(habilidades_mapeadas) > 0:
                            habilidades_mapeadas.remove(item)
                        else:
                            habilidades_mapeadas = []
                        dict_habilidades["usuarios"].append(row.id)
                        habilidades_mapeadas.append(dict_habilidades)
                        dict_habilidades = {}
        
        habilidades_mapeadas.sort(key=lambda x: (len(x["usuarios"])), reverse=True)
  
        self.render("modules/admin/list-skills.html", REGISTRY_ID=PRIV_GLOBAL_ADMIN, \
                    MSG="", HABILIDADES=habilidades_mapeadas,\
                    NOMEPAG="cadastro")        
        
            
            
URL_TO_PAGETITLE.update ({
        "admin": u"Administração"
    })

HANDLERS.extend([
            (r"/admin/listusers",                           ListUsersHandler),
            (r"/admin/onlineusers",                         OnlineUsersHandler),
            (r"/admin/listcommunities",                     ListCommunitiesActHandler),
            (r"/admin/uploadquota/%s" % NOMEUSERS,          FileQuotaHandler),
            (r"/admin/totalusers",                          TotalUsersHandler),
            (r"/admin/apps/%s" % NOMEUSERS,                 AppsHandler),
            (r"/admin/myapps",                              MyAppsHandler),
            (r"/admin/skillstats",                          SkillStatsHandler),
            (r"/admin/skillstats/user/%s"% NOMEUSERS,       UserSkillsHandler),
            (r"/admin/skillstats/skills",                   SkillUsersHandler)
    ])