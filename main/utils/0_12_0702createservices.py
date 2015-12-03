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
        , services = []
        , upload_quota = 10 * 1024 * 1024    # max 10 Mb
        , upload_size = 0  
        , notify = "2"  # notificações de e-mail
                        # 0 = não receber
                        # 1 = receber apenas um boletim semanal
                        # 2 = receber sempre
        , cpf = ""      # incluido para futura integração a intranet da UFRJ
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
        , apps = {}
        , services = []
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

# Usuários criados automaticamente
USER_ADMIN       = "activ_admin"

# Privilégios
PRIV_SUPORTE_ACTIV = "Priv_Suporte_Activ"
PRIV_CONVIDAR_USUARIOS = "Priv_Convidar_Usuarios"
PRIV_GLOBAL_ADMIN = "Priv_Global_Admin"
PRIV_CRIAR_COMUNIDADES = "Priv_Criar_Comunidades"


excecoes = [USER_ADMIN, PRIV_SUPORTE_ACTIV, PRIV_CONVIDAR_USUARIOS, PRIV_GLOBAL_ADMIN, PRIV_CRIAR_COMUNIDADES]

def main():
    for item in REGISTRY:
        if "_design/" in item or item in ['_id', '_rev']:
            continue
        if "passwd" in REGISTRY[item]:
            print "[%s] user: %s" % (item, REGISTRY[item]["user"])
            user_data = _EMPTYMEMBER()
            user_data.update(REGISTRY[item])
            if item not in excecoes:
                user_data["services"] = ["blog","mblog","wiki","file","agenda"]

        else:
            print "[%s] community: %s" % (item, REGISTRY[item]["name"])
            user_data = _EMPTYCOMMUNITY()
            user_data.update(REGISTRY[item])
            if item not in excecoes:
                user_data["services"] = ["forum","blog","mblog","wiki","file","agenda","evaluation","noticia"]
        REGISTRY[item] = user_data



if __name__ == "__main__":
    main()