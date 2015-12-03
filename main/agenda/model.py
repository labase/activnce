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


try:
  from couchdb.schema import Document, TextField, IntegerField, LongField, DateTimeField, DictField, ListField, Schema, FloatField
except ImportError:
  from couchdb.mapping import Document, TextField, IntegerField, LongField, DateTimeField, DictField, ListField, FloatField
  from couchdb.mapping import Mapping as Schema

import database

from datetime import datetime


_EMPTYAGENDA = lambda:dict(
# _id = "registry_id"
        events = {}
        #AAAAMM: {
        #    DD: [{ msg = "", owner = "", url = "", hora="", duracao="", data_cri = "" }, ...]
        #}
)

def getNextEvents(registry_id, num_events):
    """ pega os próximos "num_events" eventos a partir de agora na agenda de registry_id """
    events = []
    agora = datetime.now()
    
    for item in database.AGENDA.view('agenda/by_date', startkey=[registry_id, str(agora.year), "%02d"%agora.month, "%02d"%agora.day, str(agora.hour), str(agora.minute)], \
                                     endkey=[registry_id, "9999", {}], \
                                     limit=num_events):
        (registry_id, ano, mes, dia, hora, minuto) = item.key
        # acrescenta a data no dicionário retornado pela view
        events.append(dict(item.value.items() + [('data', dia+'/'+mes)]))
    return events
                                     