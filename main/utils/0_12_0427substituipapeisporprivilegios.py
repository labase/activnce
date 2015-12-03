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
        , tags = [] 
        , description = ""
        , amigos = []
        , amigos_pendentes = []
        , amigos_convidados = []
        , comunidades = []
        , comunidades_pendentes = []
        , mykeys = []
        , privacidade = u"Pública"           # Pode ser: Pública ou Privada
        , blog_aberto = "N"                  # Indica se o blog deste usuário 
                                             # pode ser acessado de fora da plataforma
        , upload_quota = 10 * 1024 * 1024    # max 10 Mb
        , upload_size = 0  
        , notify = "2"  # notificações de e-mail
                        # 0 = não receber
                        # 1 = receber apenas um boletim semanal
                        # 2 = receber sempre
        , data_cri = ""
        , data_alt = ""
    )

_EMPTYCOMMUNITY = lambda: dict(
          name = ""
        , description = ""
        , tags = []
        , owner = ""
        , participantes_pendentes = []
        , participantes = []
        , comunidades = []                   # comunidades em que esta comunidade está incluída
        , upload_quota = 60 * 1024 * 1024    # max 60 Mb
        , upload_size = 0
        , admins = []
        , privacidade = ""    # Pública ou Privada
        , blog_aberto = "N"   # Indica se o blog deste usuário 
                              # pode ser acessado de fora da plataforma
        , participacao = ""   # Mediante Convite, Voluntária ou Obrigatória
        , data_cri = ""
        , data_alt = ""
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

# Privilégios
PRIV_SUPORTE_ACTIV = "Priv_Suporte_Activ"
PRIV_CONVIDAR_USUARIOS = "Priv_Convidar_Usuarios"
PRIV_GLOBAL_ADMIN = "Priv_Global_Admin"
PRIV_CRIAR_COMUNIDADES = "Priv_Criar_Comunidades"


def adiciona (user_id, user_data, community_id):
    print "  adicionado em: %s" % community_id
    if community_id not in user_data["comunidades"]:
        user_data["comunidades"].append(community_id)
    
    community_data = _EMPTYCOMMUNITY()
    community_data.update(REGISTRY[community_id])
    if user_id not in community_data["participantes"]:
        community_data["participantes"].append(user_id)
        REGISTRY[community_id] = community_data


def main():

    for item in REGISTRY:
        if "passwd" in REGISTRY[item]:
            print "user: %s" % REGISTRY[item]["user"]
            user_data = _EMPTYMEMBER()
            user_data.update(REGISTRY[item])

            if "papeis" in user_data:
                if "admin" in user_data["papeis"]:
                    adiciona(item, user_data, PRIV_GLOBAL_ADMIN)
                    adiciona(item, user_data, PRIV_SUPORTE_ACTIV)
                
                if "super_usuario" in user_data["papeis"]:
                    adiciona(item, user_data, PRIV_CONVIDAR_USUARIOS)
    
                if "super_usuario" in user_data["papeis"] or \
                   "docente" in user_data["papeis"] or \
                   "funcionario" in user_data["papeis"]:
                    adiciona(item, user_data, PRIV_CRIAR_COMUNIDADES)
                
            REGISTRY[item] = user_data


if __name__ == "__main__":
    main()