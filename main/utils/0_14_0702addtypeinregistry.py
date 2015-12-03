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

PASSWD_USER_SUSPENDED = "***USER SUSPENDED***"
USER_ADMIN            = "activ_admin"

def main():

    for item in REGISTRY:
        if "_design" not in item:
            registry_data = dict()
            registry_data.update(REGISTRY[item])
            registry_data["type"] = ""
            registry_data["subtype"] = ""

            if "passwd" in registry_data:
                print "user: %s" % item
                registry_data["type"] = "member"
                if registry_data["passwd"] == PASSWD_USER_SUSPENDED:
                    registry_data["subtype"] = "suspended"
                    
            else:
                print "community: %s" % item
                registry_data["type"] = "community"
                if registry_data["owner"] == USER_ADMIN:
                    registry_data["subtype"] = "privilege"
    
            REGISTRY[item] = registry_data


if __name__ == "__main__":
    main()