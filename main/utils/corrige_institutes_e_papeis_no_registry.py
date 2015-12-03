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
    )

_EMPTYCOMMUNITY = lambda: dict(
          name = ""
        , description = ""
        , tags = []
        , owner = ""
        , photo = ""
        , participantes_pendentes = []
        , participantes = []
        , comunidades = []                   # comunidades em que esta comunidade está incluída
        , upload_quota = 20 * 1024 * 1024    # max 20 Mb
        , upload_size = 0
        , papeis = []
        , admins = []
        , cod_institute = ""
        , institute = ""
        , privacidade = ""    # Pública ou Privada
        , participacao = ""   # Mediante Convite, Voluntária ou Obrigatória
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
        if "passwd" in REGISTRY[item]:
            print "user: %s" % REGISTRY[item]["user"]
            user_data = _EMPTYMEMBER()
            user_data.update(REGISTRY[item])
        else:            
            print "community: %s" % REGISTRY[item]["name"]
            user_data = _EMPTYCOMMUNITY()
            user_data.update(REGISTRY[item])            
          
        if user_data["cod_institute"] == "0002":
            user_data["cod_institute"] = "0056"
        
        if "gestor" in user_data["papeis"]:
            user_data["papeis"].remove("gestor")
            user_data["papeis"].append("funcionario")
           
        REGISTRY[item] = user_data
    
if __name__ == "__main__":
    main()