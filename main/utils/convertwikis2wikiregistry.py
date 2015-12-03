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

_DOCBASES = ['wiki', 'wikimember', 'wikicommunity', 'registrywiki']

_EMPTYWIKI = lambda:dict(
# _id = "registry_id/nome_pagina"
          user = ""           # dono da página: usuário (antigo que postou a página)

        , registry_id = ""    # dono da página: usuário ou comunidade (registry_id).
        , owner = ""          # quem postou.
                              # caso wiki seja de uma comunidade, owner!=registry_id
        , nomepag = "NovaPagina"
        , conteudo = "Entre aqui com o conteúdo da sua página. <br/>"
        , tags = []
        , data_cri = ""
)
_EMPTYWIKIANTES = lambda:dict(
# _id = "registry_id/nome_pagina"
          user = ""           # dono da página: usuário ou comunidade (registry_id).
        , nomepag = "NovaPagina"
        , conteudo = "Entre aqui com o conteúdo da sua página. <br/>"
        , tags = []
        , data_cri = ""
)

_EMPTYREGISTRYWIKI = lambda:dict(
# _id = "registry_id"
# permite obter a lista de wikis de um determinado comunidade ou usuário.
          paginas = []          # lista de "registry_id/nome_post"
)


_EMPTYWIKIMEMBERORCOMMUNITY = lambda: dict(
# _id = "registry_id"
#
# Permite obter a lista de páginas de um determinado usuário/comunidade.
# Este template se aplica aos dois documentos: WIKIMEMBER e WIKICOMMUNITY.
#
# Em WIKIMEMBER paginas é uma lista de doc_ids ["registry_id/nome_pagina", ...]
# Em WIKICOMMUNITY paginas é uma lista de dicionários:
# { owner: "registry_id de quem criou a página",
#   doc_id: "registry_id/nome_pagina"
# }
#

         paginas = []         
)

_SPECIALCHARS = {
          "'": "\u0027"
        , "\n": ""
        , "\r": ""
        , "\\": "\u005c"
}


class Activ(Server):
    "Active database"
    wiki = {}
    wikimember = {}
    wikicommunity = {}
    registrywiki = {}

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
WIKIMEMBER = __ACTIV.wikimember
WIKICOMMUNITY = __ACTIV.wikicommunity
REGISTRYWIKI = __ACTIV.registrywiki

def main():
    wiki_data_antes = _EMPTYWIKIANTES()
    wiki_data_depois = _EMPTYWIKI()
    wikis = []
    wikistemp = {}
    
    for id in WIKI:
        (registry_id, nomepag ) = id.split("/")
        #wikistemp = { user : [ ]}
        wiki_data_antes.update(WIKI[id])
#        registry_id = WIKI[id]["user"]
        if registry_id in wikistemp:
          wikistemp[registry_id].append(id)
        else:
          wikistemp[registry_id] = [id]
        if registry_id in WIKIMEMBER:
#          wiki_data_antes ["user"] = wiki_data_antes["user"]
          wiki_data_antes ["registry_id"] = registry_id
          wiki_data_antes ["owner"] = registry_id
#          wiki_data_depois["data_cri"] = wiki_data_antes["data_cri"]
#          wiki_data_depois["tags"] = wiki_data_antes["tags"]
#          wiki_data_depois["conteudo"] = wiki_data_antes["conteudo"]
#          wiki_data_depois["nomepag"] = wiki_data_antes["nomepag"]
        elif registry_id in WIKICOMMUNITY:
#          wiki_data_depois["user"] = wiki_data_antes["user"]
          wiki_data_antes["registry_id"] = registry_id
#          wiki_data_depois["data_cri"] = wiki_data_antes["data_cri"]
#          wiki_data_depois["tags"] = wiki_data_antes["tags"]
#          wiki_data_depois["conteudo"] = wiki_data_antes["conteudo"]
#          wiki_data_depois["nomepag"] = wiki_data_antes["nomepag"]

          for lista in WIKICOMMUNITY[registry_id]["paginas"]:
              if lista["doc_id"] == id:
                 wiki_data_antes["owner"] = lista["owner"]
                 continue
#        print "antes: ", wiki_data_antes          
        print "depois: ", wiki_data_antes
        print "----------------------------------"
        try:
           WIKI[id] = wiki_data_antes
        except Exception as detail:
           print "ERRor no id:", registry_id
           continue
        print "WikiRegistry [ ", registry_id , "] = ", wikistemp[registry_id]   

    for registry_id in wikistemp:    
        registrywiki_data = _EMPTYREGISTRYWIKI()
        lista = wikistemp[registry_id]
        registrywiki_data["paginas"] = lista
        print registry_id, "-----",  lista
        REGISTRYWIKI[registry_id] = registrywiki_data       

if __name__ == "__main__":
    main()