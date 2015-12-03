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


# Remove paint de services de registry

# ATENCAO: só utilize este utilitário se o módulo paint não estiver na lista de serviços 
#         definidos no config.py


from couchdb import Server

from datetime import datetime
from uuid import uuid4
import re

_DOCBASES = ['registry']
             
class Activ(Server):
    "Active database"
    
    def __init__(self, url):
        print "conectando com o banco..."
        Server.__init__(self, url)
        
        #self.erase_tables(_DOCBASES_TO_REMOVE) 
        
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

    def erase_tables(self, tables):
        'erase a list of tables'
        for table in tables:
            try:
                del self[table]
            except:
                pass

__ACTIV = Activ('http://127.0.0.1:5984/')
REGISTRY = __ACTIV.registry
#

def main():

    print "processando registry..."
    for registry_id in REGISTRY:
        if "_design/" in registry_id:
            continue
        
        if "passwd" in REGISTRY[registry_id]:
            
            #member
            print "  user: %s" % registry_id
            user_data = REGISTRY[registry_id]

            # remove paint de servicos , se houver
            if "paint" in user_data["services"]:
                user_data["services"].remove("paint")
            REGISTRY[registry_id] = user_data
            # fim do altera tag para users          
    print "fim do processamento ..."

if __name__ == "__main__":
    main()