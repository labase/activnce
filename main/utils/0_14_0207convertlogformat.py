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
from uuid import uuid4

_DOCBASES = ['log', 'log2']

_EMPTYLOG = lambda: dict(
                         sujeito = "",
                         verbo = "",
                         objeto = "",
                         tipo = "",
                         link = "",
                         news = "True",           # todos os documentos do log velho que não tiverem o campo news
                                                  # serão copiados para o log novo com news="True"
                                                  # este valor será armazenado sempre como string
                         data_inclusao = ""
)

class Activ(Server):
    "Active database"
    log = {}
    log2 = {}

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
LOG  = __ACTIV.log
LOG2 = __ACTIV.log2

def main():

    print u"iniciando conversão"
    for user_id in LOG:
        if "_design" not in user_id:
            #print "-------------------"
            print user_id
            log_data = dict()
            log_data.update(LOG[user_id])
            
            for item in log_data["registros"]:
                log_new = _EMPTYLOG()
                log_new.update(item)
                if log_new["news"] is True:
                    log_new["news"] = "True"
                if log_new["news"] is False:
                    log_new["news"] = "False"
                #print log_new
                
                id = uuid4().hex
                LOG2[id] = log_new
       
    print u"conversão finalizada."
    
if __name__ == "__main__":
    main()