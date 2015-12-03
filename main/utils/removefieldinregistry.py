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


def main():
    for item in REGISTRY:
        print "name= %s, lastname= %s, user=%s" % (REGISTRY[item]["name"], REGISTRY[item]["lastname"], REGISTRY[item]["user"])
        if "passwd" in REGISTRY[item]:
            if REGISTRY[item]["passwd"] == "":
                # era uma comunidade
                print "  passwd vazio."
                user_data = REGISTRY[item]
                print "user_data antes=", user_data
                del user_data["user"]
                del user_data["passwd"]
                del user_data["lastname"]
                del user_data["email"]
                del user_data["amigos"]
                del user_data["amigos_pendentes"]
                del user_data["amigos_convidados"]
                del user_data["comunidades"]
                del user_data["comunidades_pendentes"]
                print "user_data depois=", user_data
                REGISTRY[item] = user_data
                
            else:
                # era um usuário
                print "  passwd=%s." % REGISTRY[item]["passwd"]
         
        else:
            print "  não tem passwd." 
    
if __name__ == "__main__":
    main()