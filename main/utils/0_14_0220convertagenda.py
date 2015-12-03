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

_DOCBASES = ['agenda']

_EMPTYAGENDA = lambda:dict(
# _id = "registry_id"
        events = {}
        #AAAAMM: {
        #    DD: [{ msg = "", owner = "", url = "", hora="", duracao="", data_cri = "" }, ...]
        #}
)

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
AGENDA = __ACTIV.agenda

def main():

    print u"iniciando conversão"
    for id in AGENDA:
        if "_design" not in id:
            print id
            agenda_data = _EMPTYAGENDA()
            agenda_data.update(AGENDA[id])            
            for anomes in agenda_data["events"]:
                for dia in agenda_data["events"][anomes]:
                    for evento in agenda_data["events"][anomes][dia]:
                        print "antigo=", anomes, dia, evento
                        if "hora" not in evento:
                            evento["hora"] = "08:00"
                        if "duracao" not in evento:
                            evento["duracao"] = "01:00"
                        print "alterado=", evento

            AGENDA[id] = agenda_data
    print u"conversão finalizada."
if __name__ == "__main__":
    main()
