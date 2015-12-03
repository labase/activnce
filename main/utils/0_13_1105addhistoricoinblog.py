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

_DOCBASES = ['blog']

_EMPTYBLOG = lambda:dict(
# _id = "registry_id/nome_pagina"
          registry_id = ""    #  usuário ou comunidade (registry_id).
        , owner = ""          # quem criou.
                              # caso blog seja de uma comunidade, owner!=registry_id
        , titulo = "Novo Post"
        , post_id     = ""
        , conteudo = u"Entre aqui com o conteúdo do seu post. <br/>"
        , tags = []
        , data_cri = ""
        , data_alt       = ""
        , alterado_por   = ""
        , historico = []
)


class Activ(Server):
    "Active database"
    blog = {}

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
BLOG = __ACTIV.blog

def main():

    print u"iniciando conversão"
    for id in BLOG:
        if "_design" not in id:
            print id
            blog_data = _EMPTYBLOG()
            blog_data.update(BLOG[id])
            
            historico = dict (
                    conteudo = blog_data["conteudo"],
                    data_alt = blog_data["data_alt"],
                    #alterado_por = blog_data["alterado_por"]
                    alterado_por = blog_data["owner"]
            )
            blog_data["historico"] = [historico]
            
            
            """
            # remove os campos obsoletos
            del blog_data["conteudo"]
            blog_data["data_alt"] = ""
            blog_data["alterado_por"] = ""
            """
            
            BLOG[id] = blog_data
    print u"conversão finalizada."
if __name__ == "__main__":
    main()