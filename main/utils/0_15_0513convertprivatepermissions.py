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

_DOCBASES = ['registry', 'permission']

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
PERMISSION = __ACTIV.permission

def main():
    """
    Converte as permissões maiores que acesso_comunidade de usuários/comunidades privadas.
    """

    print "\nIniciando conversao das permissoes \n"
    for id in PERMISSION:
        alterado = False
        if "_design" not in id:
            perm_data = dict()
            perm_data.update(PERMISSION[id])
            registry_id = perm_data["registry_id"]
            
            #print id, registry_id
            
            if registry_id in REGISTRY:
                registry_data = dict()
                registry_data.update(REGISTRY[perm_data["registry_id"]])
                
                if registry_data["privacidade"] == "Privada":
                
                    if perm_data["leitura"]["escopo"] == "acesso_activ" or perm_data["leitura"]["escopo"] == "acesso_publico":
                        perm_data["leitura"]["escopo"] = "acesso_comunidade"
                        alterado = True
                        
                    if perm_data["escrita"]["escopo"] == "acesso_activ" or perm_data["escrita"]["escopo"] == "acesso_publico":
                        perm_data["escrita"]["escopo"] = "acesso_comunidade"
                        alterado = True
                            
                    if alterado:
                        perm_data["data_alt"] = str(datetime.now())
                        PERMISSION[id] = perm_data

                        print "Permissao alterada: ", id
                        
            else:
                print "Permissao removida. Registry_id nao encontrado (%s)" % registry_id
                del PERMISSION[id]
                    


    print "Conversao finalizada."
if __name__ == "__main__":
    main()
