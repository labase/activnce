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


_DOCBASES = ['task']



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
TASK = __ACTIV.task


def main():

    for item in TASK:
        if item.startswith("_design/"):
            continue

        task_data = {}
        task_data.update(TASK[item])
        
        if "recurso" not in task_data:
            task_data["recurso"] = ""
        if "labvad" not in task_data:
            task_data["labvad"] = "N"
        if not task_data["data_alt"]:
            print "alterando %s: %s por %s" % (item, task_data["data_alt"], task_data["data_cri"])
            task_data["data_alt"] = task_data["data_cri"]
        else:
            print "ignorando %s: %s" % (item, task_data["data_alt"])

        TASK[item] = task_data
                
    print "fim do processamento."


if __name__ == "__main__":
    main()