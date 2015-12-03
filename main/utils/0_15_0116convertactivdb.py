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
    agenda = {}

    def __init__(self, url):
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

    print u"iniciando conversão"
    for id in ACTIVDB:
        if "_design" not in id:
            activ_data = dict()
            activ_data.update(ACTIVDB[id])    
            
            # inclui atributo group_id
            activ_data["group_id"] = ""    
            
            # se não existe título copia name
            if "titulo" not in activ_data or activ_data["titulo"]=="" or activ_data["titulo"]==None:
                activ_data["titulo"] = activ_data["name"]
            
            # remove name
            del activ_data["name"]
            
            if activ_data["subtype"] == "":
                activ_data["subtype"] = None
                
            # inclui atributo service de acordo com o type   
            if activ_data["type"] == "answer":
                activ_data["service"] = "quiz"
            elif activ_data["type"] == "question":
                activ_data["service"] = "question"
            elif activ_data["type"] == "quiz":
                activ_data["service"] = "quiz"
            elif activ_data["type"] == "videoaula":
                activ_data["service"] = "videoaula"

            print "%s/%s/%s" % (activ_data["service"], activ_data["type"], activ_data["subtype"])
            #ACTIVDB[id] = activ_data
    print u"conversão finalizada."
    
if __name__ == "__main__":
    main()
