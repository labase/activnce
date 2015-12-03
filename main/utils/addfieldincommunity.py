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
    #    for item in REGISTRY:
    #        if "passwd" not in REGISTRY[item] and item!="educopedistas":
    #            print "community: %s" % REGISTRY[item]["name"]
    #            user_data = _EMPTYCOMMUNITY()
    #            user_data.update(REGISTRY[item])
    #            user_data["participacao"] = "Mediante Convite"
    #            user_data["privacidade"] = u"Pública"
    #            REGISTRY[item] = user_data            
    for item in REGISTRY:
        if "passwd" not in REGISTRY[item]:
            print "community: %s" % REGISTRY[item]["name"]
            user_data = _EMPTYCOMMUNITY()
            user_data.update(REGISTRY[item])
            REGISTRY[item] = user_data
    
if __name__ == "__main__":
    main()