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


_DOCBASES = ['files']


# Acrescenta os campos: description, tags, alterado_por, data_alt

_EMPTYFILES = lambda:dict(
# _id = "registry_id/nome_arquivo"
# _attachments = <conteúdo do arquivo armazenado>
          user = ""           # usuário que fez o upload do arquivo,
                              # esta chave era do bd antigo = owner novo
        , registry_id = ""    # dono do arquivo: usuário ou comunidade
        , owner = ""          # quem fez upload.
                              # caso file seja de uma comunidade, owner!=registry_id
        , filename = ""
        , description = ""
        , tags = []
        , data_upload = ""
        , data_alt = ""
        , alterado_por = "")

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

def main():

    for file_id in FILES:
        if "_design/" in file_id:
            continue
        
        files_data = _EMPTYFILES()
        files_data.update(FILES[file_id])
        print "item:", file_id

        if not files_data["data_alt"]:
            files_data["data_alt"] = files_data["data_upload"]
        if not files_data["alterado_por"]:
            files_data["alterado_por"] = files_data["owner"]
        
        FILES[file_id] = files_data


if __name__ == "__main__":
    main()