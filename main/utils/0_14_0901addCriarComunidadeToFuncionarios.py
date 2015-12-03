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

import pymssql

from couchdb import Server

_DOCBASES = ['registry', 'dbintranet']

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
DBINTRANET = __ACTIV.dbintranet

def atribui_privilegio(user, priv):
    community_data = _EMPTYCOMMUNITY()
    community_data.update(REGISTRY[priv])
    if user not in community_data["participantes"]:
        community_data["participantes"].append(user)
        REGISTRY[priv] = community_data
    
    user_data = _EMPTYMEMBER()
    user_data.update(REGISTRY[user])
    if priv not in user_data["comunidades"]:
        user_data["comunidades"].append(priv)
        REGISTRY[user] = user_data


def main():

    dbinfo = _EMPTYDBINTRANET()
    dbinfo.update(DBINTRANET["intranet"])
    
    try:
        conn = pymssql.connect(host=dbinfo["host"], user=dbinfo["user"], password=dbinfo["passwd"], database=dbinfo["database"])
    except Exception as e:
        print u"--- Erro na conexão com o BD"
        exit()

    for usuario in REGISTRY:
        if "_design" not in usuario:
            registry_data = dict()
            registry_data.update(REGISTRY[usuario])

            if registry_data["type"]=="member" and registry_data["cpf"]!="":
                
                cur = conn.cursor()
                cur.execute('''SELECT MatriculaSiape, Ativo FROM View_eh_professor
                               WHERE IdentificacaoUFRJ=%s''', registry_data["cpf"])
                row = cur.fetchone()
                if row:
                    #matricula_siape = row[0]
                    #ativo = row[1]
                    print "professor: %s cpf: %s" % (usuario, registry_data["cpf"])
                    atribui_privilegio(usuario, "Priv_Criar_Comunidades")                   
                else:
                    cur = conn.cursor()
                    cur.execute('''SELECT MatriculaSiape, Ativo FROM View_eh_tec_adm 
                                   WHERE IdentificacaoUFRJ=%s''', registry_data["cpf"])
                    row = cur.fetchone()
                    if row:
                        #matricula_siape = row[0]
                        #ativo = row[1]
                        print "tec_adm: %s cpf: %s" % (usuario, registry_data["cpf"])
                        atribui_privilegio(usuario, "Priv_Criar_Comunidades")
                    
    conn.close()                      

if __name__ == "__main__":
    main()