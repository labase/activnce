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
from datetime import datetime
import time

_DOCBASES = ['forum','registry']

_EMPTYFORUM = lambda:dict(
# _id = "registry_id"            # dono do forum, mesmo nome da comunidade.
          topics = []            # lista de tópicos
     )

_EMPTYTOPIC = lambda:dict(
          owner = ""            # dono do tópico 
        , title = ""            # titulo do tópico
        , content = ""          # descrição do tópico
        , receber_email = False # decidir se o dono do tópico recebe ou não emails em cada post
        , posts = []            # lista de posts
        , num_posts = 0         # número de posts
        , dt_last_post = ""     # data do último post
        , dt_creation_post = "" # data de criação do post
     )

_EMPTYPOST = lambda:dict(
          owner = ""            # dono do post
        , title = ""            # título do post
        , message = ""          # mensagem postada
        , data = ""             # data hora do post
    )

_EMPTYUSER = lambda:dict(
    # dados básicos do usuário ou comunidade resgatados de registry
          registry_id = ""      # login
        , photo = ""            # foto
        , name = ""             # nome
        , email = ""            # email
     )

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
REGISTRY = __ACTIV.registry
FORUM = __ACTIV.forum

def main():

    for id in FORUM:
        forum_data = _EMPTYFORUM()
        forum_data.update(FORUM[id])
        
        for item in range(0,len(forum_data['topics'])):
            data_hora = datetime.now()
            forum_data['topics'][item]['dt_creation_post'] = str(data_hora)
        
        FORUM[id] = forum_data
        print "forum=", id, forum_data
    
if __name__ == "__main__":
    main()