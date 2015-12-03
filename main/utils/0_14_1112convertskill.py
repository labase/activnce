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
            habil_temp = []
            for habil in skill_data["habilidades"]:
                print u"Convertendo habilidade..."
                if habil["nome_habilidade"][0] == "/":
                    if len(skill_data["habilidades"]) > 1:
                        skill_data["habilidades"].remove(habil)
                    else:
                        skill_data["habilidades"] = []
                else:
                    if habil["nome_habilidade"][0] == " ":
                        habil["nome_habilidade"] = habil["nome_habilidade"][1:]
                    habil["nome_habilidade"] = habil["nome_habilidade"].lower()
                    habil_temp.append(habil["nome_habilidade"])
                    habil["usuarios_referencia"] = []
                    habil["producoes_referencia"] = []
                    habil["academico_referencia"] = []
                    habil["profissional_referencia"] = []
                print u"Habilidade convertida."
                
            for form in skill_data["formacao"]:
                print u"Convertendo formação..."
                if form["nivel"] == "nao_informado":
                    form["nivel"] = u"Não Informado"
                elif form["nivel"] == "graduacao":
                    form["nivel"] = u"Graduação"
                elif form["nivel"] == "pos_graduacao":
                    form["nivel"] = u"Pós-Graduação"
                elif form["nivel"] == "doutorado":
                    form["nivel"] = "Doutorado"
                elif form["nivel"] == "ensino_fundamental":
                    form["nivel"] = "Ensino Fundamental"
                elif form["nivel"] == "ensino_medio":
                    form["nivel"] = u"Ensino Médio"
                elif form["nivel"] == "mestrado":
                    form["nivel"] = u"Mestrado"
                
                if id == "Tartaruga":
                    print u"Atenção: ID de usuário que preencheu habilidades com espaço na frente do nome detectado. Executando processo de correção específico."
                    for habil in form["habilidades"]:
                        if habil[0] == " ":
                            form["habilidades"].append(habil[1:])
                            form["habilidades"].remove(habil)
                    
                for habil in form["habilidades"]:
                    if habil[0] != "/" and habil not in habil_temp:
                        dict_habil = dict()
                        dict_habil["nome_habilidade"] = habil
                        habil_temp.append(dict_habil["nome_habilidade"])
                        if (len(skill_data["habilidades"]) > 0):
                            dict_habil["id_habilidade"] = str(int(skill_data["habilidades"][-1]["id_habilidade"]) + 1)
                        else:
                            dict_habil["id_habilidade"] = "0"
                        
                        dict_habil["nivel_habilidade"] = ""
                        dict_habil["usuarios_referencia"] = []
                        dict_habil["producoes_referencia"] = []
                        dict_habil["academico_referencia"] = []
                        dict_habil["academico_referencia"].append(form["id_formacao"])
                        dict_habil["profissional_referencia"] = []

                        skill_data["habilidades"].append(dict_habil)
                        dict_habil = {}
                    elif habil[0] != "/" and habil in habil_temp:
                        for item in skill_data["habilidades"]:
                            if habil == item["nome_habilidade"]:
                                item["academico_referencia"].append(form["id_formacao"])
                    elif habil[0] == "/":
                        if len(form["habilidades"]) > 1:
                            form["habilidades"].remove(habil)
                        else:
                            form["habilidades"] = []
                
                if id == "Ericksson":
                    print u"Atenção: ID de usuário que preencheu incorretamente data_ini ou data_fim encontrado. Iniciando procedimento de correção específico para este usuário."
                    form["data_fim"] = "01/"+form["data_fim"]
                    form["data_ini"] = "01/"+form["data_ini"]
                elif id == "MiltonFilho":
                    print u"Atenção: ID de usuário que preencheu incorretamente data_ini ou data_fim encontrado. Iniciando procedimento de correção específico para este usuário."
                    form["data_fim"] = form["data_fim"][3:]
                    form["data_ini"] = form["data_ini"][2:]
                else:
                    form["data_fim"] = form["data_fim"][3:]
                    form["data_ini"] = form["data_ini"][3:]
                
                form["curso"] = ""
                form["habilidades"].sort()
                print u"Formação convertida."

            for exp in skill_data["experiencias"]:
                print u"Convertendo experiência..."
                exp["habilidades"].sort()
                for habil in exp["habilidades"]:
                    if habil[0] != "/" and habil not in habil_temp:
                        dict_habil = dict()
                        dict_habil["nome_habilidade"] = habil
                        habil_temp.append(dict_habil["nome_habilidade"])
                        if (len(skill_data["habilidades"]) > 0):
                            dict_habil["id_habilidade"] = str(int(skill_data["habilidades"][-1]["id_habilidade"]) + 1)
                        else:
                            dict_habil["id_habilidade"] = "0"
                        dict_habil["nivel_habilidade"] = ""
                        dict_habil["usuarios_referencia"] = []
                        dict_habil["producoes_referencia"] = []
                        dict_habil["academico_referencia"] = []
                        dict_habil["profissional_referencia"] = []
                        dict_habil["profissional_referencia"].append(exp["id_experiencias"])

                        skill_data["habilidades"].append(dict_habil)
                        dict_habil = {}
                    elif habil[0] != "/" and habil in habil_temp:
                        for item in skill_data["habilidades"]:
                            if habil == item["nome_habilidade"]:
                                item["profissional_referencia"].append(exp["id_experiencias"])
                    elif habil[0] == "/":
                        if len(exp["habilidades"]) > 1:
                            exp["habilidades"].remove(habil)
                        else:
                            exp["habilidades"] = []
                
                if id == "Ericksson":
                    print u"Atenção: ID de usuário que preencheu incorretamente data_ini ou data_fim encontrado. Iniciando procedimento de correção específico para este usuário."
                    exp["data_fim"] = exp["data_fim"][3:]
                    exp["data_ini"] = "01/"+exp["data_ini"]
                elif id == "Nelson":
                    print u"Atenção: ID de usuário que preencheu incorretamente data_ini ou data_fim encontrado. Iniciando procedimento de correção específico para este usuário."
                    exp["data_fim"] = exp["data_fim"][3:]
                    exp["data_ini"] = exp["data_ini"][3:5] + "/" + exp["data_ini"][5:]
                else:
                    exp["data_fim"] = exp["data_fim"][3:]
                    exp["data_ini"] = exp["data_ini"][3:]
                print u"Experiência convertida."         
        
            SKILL[id] = skill_data
    print u"conversão finalizada."
if __name__ == "__main__":
    main()
