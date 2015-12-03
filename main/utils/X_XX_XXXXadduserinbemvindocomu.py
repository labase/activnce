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

from couchdb import Server

from datetime import datetime
from uuid import uuid4
import re
import sys

_DOCBASES = ['registry']


# dicionários com as estruturas de acesso ao couchdb

_EMPTYMEMBER = lambda: dict(
          user = ""
        , passwd = ""
        , name = ""
        , lastname = ""
        , email = ""
        , conta_google = ""
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
        , participacao = ""   # Mediante Convite, Voluntária ou Obrigatória
        , data_cri = ""
        , data_alt = ""
        , type = "community"
        , subtype = ""
    )

#Nome da comunidade de boas vindas
COMUNIDADE_BEMVINDO = "Bem_Vindo"

# Marca de conteúdo removido na wiki e no blog
_CONTEUDO_REMOVIDO = "##@@$$%% REMOVED %%$$@@##"

# Marca de usuário suspenso
PASSWD_USER_SUSPENDED = "***USER SUSPENDED***"

class Activ(Server):
    "Active database"
    
    def __init__(self, url):
        print "iniciando a conversão..."
        Server.__init__(self, url)
        act = self
        test_and_create = lambda doc: doc in act and act[doc] or act.create(doc)
        for attribute in _DOCBASES:
            setattr(Activ, attribute, test_and_create(attribute))
            
    def erase_database(self):
        'erase tables'
        for table in _DOCBASES:
            try:
                del self[table]
            except:
                pass

__ACTIV = Activ('http://127.0.0.1:5984/')
REGISTRY = __ACTIV.registry

# Utilitario para incluir a comunidade Bem_vindo para todos os usuarios

def main():

    print "processando registry..."
    users_no_activ = []
    
    for registry_id in REGISTRY:
        if "_design/" in registry_id:
            continue
        
        if "passwd" in REGISTRY[registry_id]:
            
            #member
            print "  user: %s" % registry_id
            user_data = _EMPTYMEMBER()
            user_data.update(REGISTRY[registry_id])
            print " comunidades antes: ", user_data["comunidades"]
            if  COMUNIDADE_BEMVINDO not in user_data["comunidades"]:
                user_data["comunidades"].append(COMUNIDADE_BEMVINDO)
                #se agora colocou a comunidade, incluira na comunidade o nome do usuario
                users_no_activ.append(registry_id)
                
            print " comunidades depois: ", user_data["comunidades"]
            
            #Salvando o registro do usuario
            #REGISTRY[registry_id] = user_data
    
    # fim da varredura dos usuarios
    #Colocando a lista de usuarios na comundidade de boas vindas        
           
    community_data = _EMPTYCOMMUNITY()
    community_data.update(REGISTRY[COMUNIDADE_BEMVINDO])
    print "participantes antes:", community_data["participantes"]
    
    community_data["participantes"].extend(users_no_activ)   
 
    print "participantes depois:", community_data["participantes"]    
    
    #Salvando a comunidade    
    #REGISTRY[COMUNIDADE_BEMVINDO] = community_data
                
    print "fim do processamento ..."
    
if __name__ == "__main__":
    main()