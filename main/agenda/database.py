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
from couchdb.design import ViewDefinition
from config import COUCHDB_URL

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


__ACTIV = Activ(COUCHDB_URL)
AGENDA = __ACTIV.agenda


# Retorna todas as entradas na agenda por registry_id e data/hora
#
# Retorno:
# todos os campos do documento
#
# Uso: database.AGENDA.view('agenda/by_date',startkey=[registry_id, ano, mes, dia, hora, min], endkey=[registry_id, ano, mes, dia, hora, min, {}], limit=3)
#
agenda_by_date = ViewDefinition('agenda','by_date', \
                               '''function(doc) { 
                                     for (var anomes in doc.events){
                                        ano = anomes.slice(0,4);
                                        mes = anomes.slice(4);
                                        for (var dia in doc.events[anomes]) {
                                           for (var event in doc.events[anomes][dia]) {
                                              hora = doc.events[anomes][dia][event]["hora"].slice(0,2);
                                              min = doc.events[anomes][dia][event]["hora"].slice(3);
                                              emit([doc._id, ano, mes, dia, hora, min], doc.events[anomes][dia][event]); 
                                           }
                                        }
                                     }
                                   }
                                ''')



ViewDefinition.sync_many(AGENDA, [agenda_by_date])
                                     