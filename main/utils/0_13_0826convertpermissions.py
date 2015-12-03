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

_DOCBASES = ['registry', 'wiki', 'files', 'permission']

_EMPTYPERMISSION = lambda:dict(
# _id = "service/registry_id/nomeobj"

     service        = ""    # nome do serviço: wiki, file, blog, etc
    ,registry_id    = ""    # usuário ou comunidade a que o objeto está associado
    ,nomeobj        = ""    # nome do objeto
    ,owner          = ""    # dono do objeto (quem criou o objeto)
    ,data_cri       = ""
    ,data_alt       = ""   
    ,alterado_por   = ""    
    ,leitura        = {}    
                    # { 
                    #   escopo: ("acesso_privado", "acesso_grupos", "acesso_comunidade", "acesso_activ" ou "acesso_publico"),
                    #   grupos: [se escopo=="acesso_grupos" <lista dos nomes dos grupos autorizados> senão vazia] 
                    # }
    ,escrita        = {}    # acesso_comunidade ou <nome_grupo>
                    # { 
                    #   escopo: ("acesso_privado", "acesso_grupos" ou "acesso_comunidade"),
                    #   grupos: [se escopo=="acesso_grupos" <lista dos nomes dos grupos autorizados> senão vazia] 
                    # }
)


class Activ(Server):
    "Active database"
    evaluation = {}

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
REGISTRY = __ACTIV.registry
WIKI = __ACTIV.wiki
FILES = __ACTIV.files
PERMISSION = __ACTIV.permission

def main():
    """
    Cria as permissões para blog, wiki e files a partir dos atributos de registry, wiki e file.
    Atenção: O DB permission deve estar vazio.
    """

    print "\nConversao do blog \n"
    for id in REGISTRY:
        if "_design" not in id:
            registry_data = dict()
            registry_data.update(REGISTRY[id])
            
            if "blog_aberto" in registry_data:
                perm_data = _EMPTYPERMISSION()
    
                # montagem do documento de permissions
                perm_data["service"] = "blog"
                
                perm_data_id = "blog"+"/"+id+"/"
                perm_data["registry_id"] = id
                if "passwd" in registry_data:
                    perm_data["owner"] = id
                else:
                    perm_data["owner"] = registry_data["owner"]
                    
                if  registry_data["blog_aberto"] == "S":
                    perm_data["leitura"] = { "escopo" : "acesso_publico", "grupos" : [] }
                else:
                    perm_data["leitura"] = { "escopo" : "acesso_activ", "grupos" : [] }
    
                perm_data["escrita"] = { "escopo" : "acesso_comunidade", "grupos" : [] }
                perm_data["data_cri"] = registry_data["data_alt"]
                perm_data["data_alt"] = str(datetime.now())
                
                print "Blog do: " , id, "   registry_data[blog_aberto] =" , registry_data["blog_aberto"]
                print "perm_data = ", perm_data
                
                #update da permissão
                PERMISSION[perm_data_id] = perm_data
                
    # Conversao da WIKI
    print "\nConversao da wiki \n"
    for id in WIKI:
        if "_design" not in id:
            wiki_data = dict()
            wiki_data.update(WIKI[id])

            perm_data = _EMPTYPERMISSION()
            perm_data_id = "wiki"+"/"+id
            (perm_data["registry_id"], perm_data["nomeobj"]) = id.split("/")
            perm_data["owner"] = perm_data["registry_id"]
            perm_data["service"] = "wiki"            
            if wiki_data["acesso_publico"] == "S":
                # S = acesso_publico, N = acesso_activ
                perm_data["leitura"] = { "escopo" : "acesso_publico", "grupos" : [] }
            else:
                perm_data["leitura"] = { "escopo" : "acesso_activ", "grupos" : [] }

            if wiki_data["edicao_publica"] == "S": 
                # S = acesso_comunidade, N = "acesso_privado"
                perm_data["escrita"] = { "escopo" : "acesso_comunidade", "grupos" : [] }
            else: 
                # considerando edicao_publica="N"
                perm_data["escrita"] = { "escopo" : "acesso_privado", "grupos" : [] }                
                
            perm_data["data_cri"] = wiki_data["data_alt"]
            perm_data["data_alt"] = str(datetime.now())
            
            print "Wiki : " , id, "   wiki_data[acesso_publico] =" , wiki_data["acesso_publico"], "wiki_data[edicao_publica] =", wiki_data["edicao_publica"]
            print "perm_data = ", perm_data
                
            #update da permissão
            PERMISSION[perm_data_id] = perm_data

    # Conversao do Files
    print "\nConversao de files \n"
    for id in FILES:
        if "_design" not in id:
            file_data = dict()
            file_data.update(FILES[id])
            
            perm_data = _EMPTYPERMISSION()
            perm_data_id = "file"+"/"+id
            (perm_data["registry_id"], perm_data["nomeobj"]) = id.split("/")
            perm_data["owner"] = perm_data["registry_id"]
            perm_data["service"] = "file"            
            if file_data["acesso_publico"] == "S":
                # S = acesso_publico, N = acesso_activ
                perm_data["leitura"] = { "escopo" : "acesso_publico", "grupos" : [] }
            else:
                perm_data["leitura"] = { "escopo" : "acesso_activ", "grupos" : [] }

            if file_data["edicao_publica"] == "S": 
                # s = acesso_comunidade, N = "acesso_privado"
                perm_data["escrita"] = { "escopo" : "acesso_comunidade", "grupos" : [] }
            else: 
                # considerando edicao_publica="N"?
                perm_data["escrita"] = { "escopo" : "acesso_privado", "grupos" : [] }                
                
            perm_data["data_cri"] = file_data["data_alt"]
            perm_data["data_alt"] = str(datetime.now())
            
            print "file : " , id.encode('utf-8'), "   file_data[acesso_publico] =" , file_data["acesso_publico"], "file_data[edicao_publica] =", file_data["edicao_publica"]
            #print "perm_data = ", perm_data
                
            #update da permissão
            PERMISSION[perm_data_id] = perm_data


    print "Conversao finalizada."
if __name__ == "__main__":
    main()
