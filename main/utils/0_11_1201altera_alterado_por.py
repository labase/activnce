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
from uuid import uuid4


_DOCBASES = ['blog', \
             'wiki']

_EMPTYBLOG = lambda:dict(
# _id = "registry_id/nome_post"
          registry_id = ""    # dono do blog: usuário ou comunidade.
        , owner = ""          # quem postou.
                              # caso blog seja de uma comunidade, owner!=registry_id
        , titulo = "Novo Post"
        , post_id = ""        # identificador do post.
                              # é obtido a partir do título, extraíndo caracteres especiais,
                              # letras acentuadas e subtituindo espaços por _.
        , conteudo = "Entre aqui com o conteúdo do seu post. <br/>"
        , tags = []
        , data_cri = ""
        , data_alt = ""         # data da última alteração
        , alterado_por = ""     # quem alterou o post pela última vez
     )


_EMPTYWIKI = lambda:dict(
# _id = "registry_id/nome_pagina"
          user = ""           # usuário ou comunidade (registry_id).
        , registry_id = ""    #  usuário ou comunidade (registry_id).
        , owner = ""          # quem criou.
                              # caso wiki seja de uma comunidade, owner!=registry_id
        , nomepag = ""
        , nomepag_id = ""
        , conteudo = ""
        , edicao_publica = ""  # Se "S" qq participante pode editar, se "N" só o dono da página e os admins da comunidade.
        , tags = []
        , data_cri = ""         # data de criação da página
        , data_alt = ""         # data da última alteração
        , alterado_por = ""     # quem alterou a pag pela última vez
)


class Activ(Server):
    "Active database"
    
    def __init__(self, url):
        print "conectando com o banco..."
        Server.__init__(self, url)
        
        act = self
        test_and_create = lambda doc: doc in act and act[doc] or act.create(doc)
        for attribute in _DOCBASES:
            setattr(Activ, attribute, test_and_create(attribute))
            
    def erase_tables(self, tables):
        'erase a list of tables'
        for table in tables:
            try:
                del self[table]
            except:
                pass

__ACTIV = Activ('http://127.0.0.1:5984/')
BLOG = __ACTIV.blog
WIKI = __ACTIV.wiki

def main():
    
    print "processando wiki ..."
    # recria tags das páginas wiki
    for doc_id in WIKI:
        if "_design/" in doc_id:
            continue        
        wiki_data = _EMPTYWIKI()
        wiki_data.update(WIKI[doc_id])
        if not wiki_data["alterado_por"]:
            wiki_data["alterado_por"] = wiki_data["owner"]
        WIKI[doc_id] = wiki_data


    print "processando blog ..."
    # recria tags dos posts do blog
    for post_id in BLOG:
        if "_design/" in post_id:
            continue                
        blog_data = _EMPTYBLOG()
        blog_data.update(BLOG[post_id])
        if not blog_data["alterado_por"]:
            blog_data["alterado_por"] = blog_data["owner"]
        BLOG[post_id] = blog_data


    print "fim do processamento ..."

if __name__ == "__main__":
    main()