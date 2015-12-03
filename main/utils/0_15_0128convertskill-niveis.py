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

    print u"iniciando conversão..."
    for id in SKILL:
        if "_design" not in id:
            skill_data = _EMPTYSKILL()
            skill_data.update(SKILL[id])
            print u"Iniciando conversão de: " + skill_data["owner"]
            for habil in skill_data["habilidades"]:
                print u"Convertendo habilidade..."
                if habil["nivel_habilidade"] == "competente":
                    habil["nivel_habilidade"] = "apto"
                if habil["nivel_habilidade"] == "profissional":
                    habil["nivel_habilidade"] = "proficiente"
                if habil["nivel_habilidade"] == "expert":
                    habil["nivel_habilidade"] = "especialista"
                
                for user in habil["usuarios_referencia"]:
                    if user["nivel"] == "competente":
                        user["nivel"] = "apto"
                    if user["nivel"] == "profissional":
                        user["nivel"] = "proficiente"
                    if user["nivel"] == "expert":
                        user["nivel"] = "especialista"  
                print u"Habilidade convertida."
            
            for pend in skill_data["habilidades_pendentes"]:
                print u"Convertendo habilidade_pendente..."
                for user in pend["usuarios_referencia"]:
                    if user["nivel"] == "competente":
                        user["nivel"] = "apto"
                    if user["nivel"] == "profissional":
                        user["nivel"] = "proficiente"
                    if user["nivel"] == "expert":
                        user["nivel"] = "especialista"  
                print u"Habilidade_pendente convertida."
                
            for recusada in skill_data["habilidades_recusadas"]:
                print u"Convertendo habilidade_recusada..."
                for user in recusada["usuarios_referencia"]:
                    if user["nivel"] == "competente":
                        user["nivel"] = "apto"
                    if user["nivel"] == "profissional":
                        user["nivel"] = "proficiente"
                    if user["nivel"] == "expert":
                        user["nivel"] = "especialista"  
                print u"Habilidade_recusada convertida."
                
            for invalida in skill_data["habilidades_invalidas"]:
                print u"Convertendo habilidade_invalida..."
                for user in invalida["usuarios_referencia"]:
                    if user["nivel"] == "competente":
                        user["nivel"] = "apto"
                    if user["nivel"] == "profissional":
                        user["nivel"] = "proficiente"
                    if user["nivel"] == "expert":
                        user["nivel"] = "especialista"  
                print u"Habilidade_invalida convertida."
                
            SKILL[id] = skill_data
    print u"conversão finalizada."
if __name__ == "__main__":
    main()
