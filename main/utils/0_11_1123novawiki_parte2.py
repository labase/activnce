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
WIKI = __ACTIV.wiki

def main():
    def remove_diacritics(str):
        special_chars = [u'à', u'á', u'ã', u'â', u'À', u'Á', u'Ã', u'Â',\
                         u'é', u'ê', u'É', u'Ê',\
                         u'í', u'Í', \
                         u'ó', u'õ', u'ô', u'Ó',u'Õ', u'Ô', \
                         u'ú', u'ü', u'Ú', u'Ü', \
                         u'ç', u'Ç' ]
        chars = ['a', 'a', 'a', 'a', 'A', 'A', 'A', 'A',\
                 'e', 'e', 'E', 'E',\
                 'i',  'I', \
                 'o', 'o', 'o', 'O', 'O', 'O', \
                 'u', 'u', 'U', 'U', \
                 'c', 'C' ]

        for i in range(len(special_chars)):
            str=str.replace(special_chars[i], chars[i])
               
        return str
   
    def remove_special_chars(str):
        strnew = ""
        for i in range(len(str)):
            if (str[i]>="A" and str[i]<="Z") or\
               (str[i]>="a" and str[i]<="z") or\
               (str[i]>="0" and str[i]<="9") or\
               (str[i]=="_"):
                strnew += str[i]
                
        return strnew
    
#    Primeira passada: colocando o nomepag_id

    for item in WIKI:
        if "_design" not in item:
            (registry_id, pagina) = item.split("/")
            wiki_data = _EMPTYWIKI()
            wiki_data.update(WIKI[item])
            wiki_data["nomepag_id"] = pagina.replace(" ","_")
            wiki_data["nomepag_id"] = remove_diacritics(wiki_data["nomepag_id"])
            wiki_data["nomepag_id"] = remove_special_chars(wiki_data["nomepag_id"])
            #criando o novo id da página
            WIKI[item] = wiki_data
            print "item: %s %s - %s" % (registry_id, wiki_data["nomepag"], wiki_data["nomepag_id"])


# Segunda passada: incluindo um id novo - não remove o anterior.
# Guarda o wiki_id antigo em um banco chamado tempwiki
    
    for item in WIKI:
        if "_design" not in item:
            (registry_id, pagina) = item.split("/")
            wiki_data = _EMPTYWIKI()
            wiki_data.update(WIKI[item])
            nova_wiki = _EMPTYWIKI()           
            if wiki_data["nomepag"] != wiki_data["nomepag_id"]:
                for i in wiki_data:
                    if i not in ["_id", "_rev"]:
                        nova_wiki[i] = wiki_data[i]

                #criando o novo id da página
                print "Novo nome: ", wiki_data["nomepag_id"]
                newdoc_id = '/'.join([registry_id,wiki_data["nomepag_id"]])
                if newdoc_id not in WIKI:
                   WIKI[newdoc_id] = nova_wiki
                   del WIKI[item]
                else:
                    print "ERRO: nomepag já existente - ", newdoc_id

if __name__ == "__main__":
    main()