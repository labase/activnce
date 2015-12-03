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

_DOCBASES = ['files', 'filemember', 'filecommunity', 'registryfile']


_EMPTYFILES = lambda:dict(
# _id = "registry_id/nome_arquivo"
# _attachments = <conteúdo do arquivo armazenado>
          user = ""           # usuário que fez o upload do arquivo,
                              # mesmo que numa comunidade (owner).
        , filename = ""
        , data_upload = ""
)

_EMPTYNEWFILES = lambda:dict(
# _id = "registry_id/nome_arquivo"
# _attachments = <conteúdo do arquivo armazenado>
          user = ""           # usuário que fez o upload do arquivo,
                              # esta chave era do bd antigo = owner novo
        , registry_id = ""    # dono do arquivo: usuário ou comunidade
        , owner = ""          # quem fez upload.
                              # caso file seja de uma comunidade, owner!=registry_id
        , filename = ""
        , data_upload = ""
)


_EMPTYFILEREGISTRY = lambda:dict(
# _id = "registry_id"
# permite obter a lista de posts de um determinado blog.
          files = []          # lista de "registry_id/nomedofile"
)


_SPECIALCHARS = {
          "'": "\u0027"
        , "\n": ""
        , "\r": ""
        , "\\": "\u005c"
}


class Activ(Server):
    "Active database"
    files = {}
    filemember = {}
    filecommunity = {}
    registryfile = {}

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

FILES = __ACTIV.files
FILEMEMBER = __ACTIV.filemember
FILECOMMUNITY = __ACTIV.filecommunity
REGISTRYFILE = __ACTIV.registryfile

def main():
    def remove_diacritics(str):
            special_chars = [u'à', u'á', u'ã', u'À', u'Á', u'Ã',\
                         u'é', u'ê', u'É', u'Ê',\
                         u'í', u'Í', \
                         u'ó', u'õ', u'ô', u'Ó',u'Õ', u'Ô', \
                         u'ú', u'ü', u'Ú', u'Ü', \
                         u'ç', u'Ç' ]
            chars = ['a', 'a', 'a', 'A', 'A', 'A',\
                 'e', 'e', 'E', 'E',\
                 'i',  'I', \
                 'o', 'o', 'o', 'O', 'O', 'O', \
                 'u', 'u', 'U', 'U', \
                 'c', 'C' ]

            for i in range(len(special_chars)):
                str=str.replace(special_chars[i], chars[i])
               
            return str
      
    file_data = _EMPTYFILES()
    files = []
    fileregistry_data = _EMPTYFILEREGISTRY()
    
    for file_id in FILES:
        (registry_id, filename) = file_id.split("/")
        #filename = remove_diacritics(filename)
        #filename = filename.replace("%20"," ")
                
        file_data = _EMPTYFILES()
        #wikistemp = { user : [ ]}
        file_data = FILES[file_id]
        filenew_data = _EMPTYFILES()
        filenew_data.update(file_data)
        filenew_data["filename"] = filename
        
        if registry_id in FILEMEMBER:
          filenew_data["registry_id"] = registry_id
          filenew_data["owner"] = registry_id
        elif registry_id in FILECOMMUNITY:
          filenew_data["registry_id"] = registry_id
          
          for lista in FILECOMMUNITY[registry_id]["files"]:  
              if lista["file_id"] == file_id:
                 filenew_data["owner"] = lista["owner"]
                 continue

        if registry_id in REGISTRYFILE:
           if file_id not in REGISTRYFILE[registry_id]["files"]:
              fileregistry_data = _EMPTYFILEREGISTRY()
              fileregistry_data.update(REGISTRYFILE[registry_id])
              fileregistry_data["files"].append(file_id)
              print "registro existe no fileregistry:", fileregistry_data
              REGISTRYFILE[registry_id] = fileregistry_data
        else:
              fileregistry_data = _EMPTYFILEREGISTRY()
              fileregistry_data["files"] = [file_id]
              print "registro  no fileregistry:", registry_id, fileregistry_data
              REGISTRYFILE[registry_id] = fileregistry_data

        FILES[file_id] = filenew_data
        print "antes: ", file_data
        print " ----------------------------------"
        print "depois: ", filenew_data       
    
if __name__ == "__main__":
    main()
