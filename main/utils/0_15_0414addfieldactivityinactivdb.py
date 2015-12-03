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

_DOCBASES = ['activdb']

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
ACTIVDB = __ACTIV.activdb


def main():

    for item in ACTIVDB:
        if item.startswith("_design/"):
            continue
        
        if ACTIVDB[item]["service"] == "activity" and ACTIVDB[item]["type"] == "activity":
            print "atividade: %s %s" % (ACTIVDB[item]["registry_id"], ACTIVDB[item]["titulo"])
            activity_data = {}
            activity_data.update(ACTIVDB[item])

            activity_data["data_conclusion"] = ""

            ACTIVDB[item] = activity_data
            
    print "fim do processamento."


if __name__ == "__main__":
    main()