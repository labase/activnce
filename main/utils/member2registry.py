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


_DOCBASES = ['registry', 'member', 'community']

_EMPTYMEMBER = lambda: dict(
          user = ""
        , passwd = ""
        , name = ""
        , lastname = ""
        , email = ""
        , photo = ""
        , amigos = []
        , amigos_pendentes = []
        , amigos_convidados = []
        , comunidades = []
        , comunidades_pendentes = []
    )

_EMPTYCOMMUNITY = lambda: dict(
          name = ""
        , description = ""
        , owner = ""
        , photo = ""
        , participantes_pendentes = []
        , participantes = []
    )


class Activ(Server):
    "Active database"
    
    def __init__(self, url):
        print "iniciando o servidor..."
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
MEMBER = __ACTIV.member
COMMUNITY = __ACTIV.community

def main():
    user_data = _EMPTYMEMBER
    for item in MEMBER:
        user_data = MEMBER[item]
        REGISTRY[item] = user_data
     
    community_data = _EMPTYCOMMUNITY
    for item in COMMUNITY:
        community_data = COMMUNITY[item]
        REGISTRY[item] = community_data
    
if __name__ == "__main__":
    main()