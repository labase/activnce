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

_DOCBASES = ['wiki']

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
        
        , nomepag_id     = ""
        , data_alt       = ""
        , alterado_por   = ""
        , comentarios    = []
        , acesso_publico = ""

        , historico = []
        
        # novos atributos para armazenar pastas para a Wiki.
        , is_folder       = "N"
        , parent_folder   = ""
        , folder_items    = []
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

def main():

    print u"iniciando conversão"
    for id in WIKI:
        if "_design" not in id:
            print id
            wiki_data = _EMPTYWIKI()
            wiki_data.update(WIKI[id])
            
            historico = dict (
                    conteudo = wiki_data["conteudo"],
                    data_alt = wiki_data["data_alt"],
                    alterado_por = wiki_data["alterado_por"]
            )
            wiki_data["historico"] = [historico]
            
            """
            del wiki_data["conteudo"]
            if wiki_data["is_folder"]!="S":
                wiki_data["data_alt"] = ""
                wiki_data["alterado_por"] = ""
            """
            
            WIKI[id] = wiki_data
    print u"conversão finalizada."
if __name__ == "__main__":
    main()
