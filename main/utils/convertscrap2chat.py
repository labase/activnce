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



============= Desistimos de utilizar este script ================

"""

import time

from couchdb import Server

_DOCBASES = ['scrapbook', 'registry']

_EMPTYSCRAP = lambda:dict(
# _id = "registry_id"
    user_to = "",
    recados = []
)    
    
"""
ListField(DictField(Schema.build(
                        user_from = TextField(),
                        recado = TextField(),
                        data = TextField()
          )))
"""
    
    
    
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
SCRAPBOOK = __ACTIV.scrapbook
REGISTRY = __ACTIV.registry

def channel_name(user, registry_id):
    if registry_id in REGISTRY:
        registry_data = dict()
        registry_data.update(REGISTRY[registry_id])
        if "passwd" not in registry_data:
            return registry_id
                
        else:
            channel = [user, registry_id]   
            channel.sort()
            return ":".join(channel)
    else:
        return None
 
def short_datetime(date_str, include_year=True, include_separator=u" às "):
    try:
        date = time.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")
        #return time.strftime("%d/%m/%Y %H:%M:%S", date)
        if include_year:
            return time.strftime((u"%d/%m/%Y" + include_separator + u"%H:%M").encode('utf-8'), date).decode('utf-8')
        else:
            return time.strftime((u"%d/%m" + include_separator + u"%H:%M").encode('utf-8'), date).decode('utf-8')
    except ValueError:
        return u'Data inválida!'
            
def main():
    msg_chat = lambda user, msg, data: "<b>%s</b>: %s<div class='date'>%s</div>" % (user, msg, short_datetime(data, include_year=True))

    print u"iniciando conversão"
    for id in SCRAPBOOK:
        if "_design" not in id:
            print id
            agenda_data = _EMPTYSCRAP()
            agenda_data.update(SCRAPBOOK[id])        
            
            for recado in agenda_data["recados"]:
                if recado["user_from"]!="activ_admin":
                    channel_chat = channel_name(recado["user_from"], id)
                    if channel_chat:
                        msg = msg_chat(recado["user_from"], recado["recado"], recado["data"])
                        print "rpush...", channel_chat, msg
                        # model.REDIS.rpush(channel_chat, msg)
                    else:
                        print ">>>erro: ", recado["user_from"], id
                
    print u"conversão finalizada."
if __name__ == "__main__":
    main()
