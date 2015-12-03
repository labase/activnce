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

_DOCBASES = ['files', 'registry']

_EMPTYFILES = lambda:dict(
# _id = "registry_id/nome_pagina"
          user = ""           # usuário ou comunidade (registry_id).
        , registry_id = ""    #  usuário ou comunidade (registry_id).
        , owner = ""          # quem fez upload.
                              # caso File seja de uma comunidade, owner!=registry_id
        , filename = ""
        , description = ""
        , tags = []
        , data_upload = ""
        , data_alt       = ""
        , alterado_por   = ""
        , comentarios    = []
        , acesso_publico = ""
        , edicao_publica = "S"
        # novos atributos para armazenar pastas para a File - addfieldinFILES
        , is_folder       = "N"
        , parent_folder   = ""
        , folder_items    = []
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
FILES = __ACTIV.files
REGISTRY = __ACTIV.registry

def main():

    print "- Inicio do processamento de add field in Files."
    for file_id in FILES:
        if "_design/" in file_id:
            continue

        files_data = _EMPTYFILES()
        files_data.update(FILES[file_id])
        print "file_id in FILES:", file_id
        (registry_id, filename_id) = file_id.split("/")
        #Resolvendo problema de filename em branco
        if files_data["filename"] == "":
            files_data["filename"] = filename_id
        if registry_id in REGISTRY and "passwd" in REGISTRY[registry_id]:
            files_data["edicao_publica"] = "N"
        FILES[file_id] = files_data
        
            
    print "- Fim do processamento de add field in FILES."

if __name__ == "__main__":
    main()