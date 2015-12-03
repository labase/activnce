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

_DOCBASES = ['wiki', 'registry']

_EMPTYWIKI = lambda:dict(
# _id = "registry_id/nome_pagina"
          user = ""           # usuário ou comunidade (registry_id).
        , registry_id = ""    #  usuário ou comunidade (registry_id).
        , owner = ""          # quem criou.
                              # caso wiki seja de uma comunidade, owner!=registry_id
        , nomepag = "NovaPagina"
        , conteudo = "Entre aqui com o conteúdo da sua página. <br/>"
        , edicao_publica = "S"  # Se "S" qq participante pode editar, se "N" só o dono da página e os admins da comunidade.
        , tags = []
        , data_cri = ""
)


class Activ(Server):
    "Active database"
    wiki = {}

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
WIKI = __ACTIV.wiki
REGISTRY = __ACTIV.registry

def main():

    for id in WIKI:
        wiki_data = _EMPTYWIKI()
        wiki_data.update(WIKI[id])   
        registry_id = id.split("/")[0]
        if registry_id in REGISTRY and "passwd" in REGISTRY[registry_id]:
            wiki_data["edicao_publica"] = "N"
        WIKI[id] = wiki_data
        print "id=", id, wiki_data["edicao_publica"]

if __name__ == "__main__":
    main()
