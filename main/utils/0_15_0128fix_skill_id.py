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

_DOCBASES = ['skill']

_EMPTYSKILL = lambda:dict(
    owner                   = "",
    formacao                = [],
    experiencias            = [],
    habilidades             = [],
    habilidades_pendentes   = [],
    habilidades_recusadas   = [],
    habilidades_invalidas   = [],
    producoes               = [],
    cabecalho_lattes        = {}
)


class Activ(Server):
    "Active database"
    skill = {}

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
SKILL = __ACTIV.skill

def main():

    print u"Iniciando correção..."
    num_erros = 0
    for id in SKILL:
        if "_design" not in id:
            skill_data = _EMPTYSKILL()
            skill_data.update(SKILL[id])
            lista_ids = []
    
            print u"Iniciando correção de: " + skill_data["owner"]
            for habil in skill_data["habilidades"]:
                if int(habil["id_habilidade"]) in lista_ids:
                    habil["id_habilidade"] = str(lista_ids[-1]+1)
                    lista_ids.append(int(habil["id_habilidade"]))
                    num_erros = num_erros + 1
                    print u"Erro encontrado e corrigido! Quantidade de erros até aqui: " + str(num_erros)
                else:
                    lista_ids.append(int(habil["id_habilidade"]))
                    lista_ids.sort()
                    
            SKILL[id] = skill_data
            lista_ids = []
    print u"Correção finalizada."
    print u"Foram corrigidos " + str(num_erros) + " registros."
if __name__ == "__main__":
    main()
