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
        , photo = ""
        , cod_institute = ""
        , institute = ""
        , amigos = []
        , amigos_pendentes = []
        , amigos_convidados = []
        , comunidades = []
        , comunidades_pendentes = []
        , papeis = []   # serve tb para definir se o usuário é "tnm" ou "educo"
        , mykeys = []
        , privacidade = u"Pública"           # Pública ou Privada
        , upload_quota = 10 * 1024 * 1024    # max 10 Mb
        , upload_size = 0  
        , notify = "2"  # notificações de e-mail
                        # 0 = não receber
                        # 1 = receber apenas um boletim semanal
                        # 2 = receber sempre
    )

_EMPTYCOMMUNITY = lambda: dict(
          name = ""
        , description = ""
        , owner = ""
        , photo = ""
        , participantes_pendentes = []
        , participantes = []
        , comunidades = []                   # comunidades em que esta comunidade está incluída
        , upload_quota = 20 * 1024 * 1024    # max 20 Mb
        , upload_size = 0
        , papeis = []
        , cod_institute = ""
        , institute = ""
        , privacidade = ""    # Pública ou Privada
        , participacao = ""   # Mediante Convite, Voluntária ou Obrigatória
        , tags = []
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

# Usuários e Comunidades criados automaticamente
USER_ADMIN       = "tnm_admin"
EDUCO_OWNER     = "adm_educopedia"
EDUCO_CONVIDADO = "convidado"

TIPO_ESCOLA_TNM = "Tipo_Escola_TNM"
TIPO_TURMA_TNM  = "Tipo_Turma_TNM"     
TIPO_GRUPO_DE_ALUNOS_TNM     = "Tipo_Grupo_De_Alunos_TNM" 
PRIV_CONSULTAR_CADASTRO      = "Priv_Consultar_Cadastro"
PRIV_ALTERAR_CADASTRO        = "Priv_Alterar_Cadastro"
PRIV_SUPORTE_EDUCOPEDIA      = "Priv_Suporte_Educopedia"
COMUNIDADE_EDUCOPEDISTAS     = "educopedistas"
COMUNIDADE_EDUCOPEDISTAS_TNM = "educopedistas_tonomundo"

excecoes = [USER_ADMIN, EDUCO_OWNER, EDUCO_CONVIDADO, TIPO_ESCOLA_TNM, TIPO_TURMA_TNM, TIPO_GRUPO_DE_ALUNOS_TNM, \
            PRIV_CONSULTAR_CADASTRO, PRIV_ALTERAR_CADASTRO, PRIV_SUPORTE_EDUCOPEDIA, COMUNIDADE_EDUCOPEDISTAS, \
            COMUNIDADE_EDUCOPEDISTAS_TNM]

def main():
#    for item in REGISTRY:
#        if item not in excecoes:
#            if "passwd" in REGISTRY[item]:
#                print "user: %s" % REGISTRY[item]["user"]
#                user_data = _EMPTYMEMBER()
#                user_data.update(REGISTRY[item])
#            else:            
#                print "community: %s" % REGISTRY[item]["name"]
#                user_data = _EMPTYCOMMUNITY()
#                user_data.update(REGISTRY[item])            
#        REGISTRY[item] = user_data

    for item in REGISTRY:
        if "passwd" in REGISTRY[item]:
            print "user: %s" % REGISTRY[item]["user"]
            user_data = _EMPTYMEMBER()
            user_data.update(REGISTRY[item])

            user_data["notify"] = "2"

            REGISTRY[item] = user_data


if __name__ == "__main__":
    main()