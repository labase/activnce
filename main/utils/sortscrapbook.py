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


_DOCBASES = ['scrapbook']


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



def main():
    __ACTIV = Activ('http://127.0.0.1:5984/')
    SCRAPBOOK = __ACTIV.scrapbook
    
    for item in SCRAPBOOK:
          print item


    for registry_id in SCRAPBOOK:
        scrap_data = SCRAPBOOK[registry_id]
        print registry_id, " antes: ", scrap_data["recados"]        
        scrap_data["recados"].reverse()
        print  registry_id, " depois: ", scrap_data["recados"]
        SCRAPBOOK[registry_id] = scrap_data
        
    
if __name__ == "__main__":
    main()