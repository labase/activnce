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
"""
convertquizpermission.py - a partir da versão X_XX_XXXX
Agora a permissão do quiz deixa de ser global para ser individual para cada quiz/pesquisa criado
"""

from couchdb import Server
from datetime import datetime

_DOCBASES = ['permission', 'activdb']

_EMPTYPERMISSION = lambda:dict(
# _id = "quiz/registry_id/quiz_id    " 

     service        = ""    # nome do serviço: quiz, etc
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

_EMPTYACTIVDB = lambda:dict()

class Activ(Server):
    "Active database"
   
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

ACTIVDB = __ACTIV.activdb
PERMISSION = __ACTIV.permission

def main():
    """
    Modifica permissions tipo quiz para ser individual
    """
    lista_id_permission = []
    print "\nConversao do quiz\n"
    for id in ACTIVDB:
        if "_design" not in id:
            activdb_data = dict()
            activdb_data.update(ACTIVDB[id])
            
            # verifica se o tipo é quiz 
            if "type" in activdb_data and activdb_data["type"]=="quiz":
                print "Dados do activdb: ", activdb_data
                # pesquisa se existe quiz/registry_id no permission
                # se existir, guarda registry_id, cria novo registro com o novo id
                if "quiz/"+activdb_data["registry_id"]+"/" in PERMISSION:
                    perm_data = _EMPTYPERMISSION()
                    perm_data.update(PERMISSION["quiz/"+activdb_data["registry_id"]+"/"])
                    perm_data["nomeobj"] = id
                    perm_data["owner"] = activdb_data["owner"]
                    
                    print "permission= ", perm_data
                    new_id =  "quiz/"+activdb_data["registry_id"]+"/"+id
                    print "novo id = ", new_id
                    #create new id com a permissão antiga
                    PERMISSION[new_id] = perm_data    
                    
                    # guarda o id do perm antigo em uma lista
                    if "quiz/"+activdb_data["registry_id"]+"/" not in lista_id_permission:
                        lista_id_permission.append("quiz/"+activdb_data["registry_id"]+"/") 
    
    # Agora remove os ids antigos do permission
    
    for old_id in lista_id_permission:
        del PERMISSION[old_id]
        print "Vou remover: ", old_id


    print "Conversao finalizada."
if __name__ == "__main__":
    main()
