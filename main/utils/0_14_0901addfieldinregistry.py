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


_DOCBASES = ['registry']



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


def main():

    for item in REGISTRY:
        if "_design" not in item:
            if REGISTRY[item]["type"] == "community":
                print "community: %s" % REGISTRY[item]["name"]
                community_data = _EMPTYCOMMUNITY()
                community_data.update(REGISTRY[item])
    
                REGISTRY[item] = community_data
    print "fim do processamento."


if __name__ == "__main__":
    main()