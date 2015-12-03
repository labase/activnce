# -*- coding: utf-8 -*-
"""
################################################
Plataforma Oi Tonomundo - ActivUFRJ - Educopédia
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
from couchdb import Database
from couchdb.design import ViewDefinition

from config import COUCHDB_URL
from search.model import STOPWORDS

STOPWORDS_UNICODE = [item.encode('iso-8859-1', 'ignore') for item in STOPWORDS]

CALCULA_NIVEL_GERAL = u"""
    //#Variáveis para a fórmula de cálculo do nível geral:
    //nivel_pessoal: nível da habilidade que o próprio usuário informou
    //nivel_social: soma dos níveis apontados pelos amigos do usuário
    //num_validacoes: número de usuários que validaram a habilidade
    //nivel_producoes: temporariamente definido como 5, nível máximo
    //peso_pessoal: peso dado ao nivel_pessoal
    peso_pessoal = 1.0;
    //peso_social: peso dado ao nivel_social
    peso_social = 1.0;
    //peso_producoes: peso dado ao nivel_producoes
    peso_producoes = 1.0;
    //num_parcelas: número de parcelas para o cálculo da média. Por enquanto, 3: nivel_pessoal, nivel_social e nivel_producoes
    num_parcelas = 3.0;
    nivel_pessoal = 0.0;
    if (doc.habilidades[item]["nivel_habilidade"] == "novato"){
        nivel_pessoal = 1.0;
    }else if (doc.habilidades[item]["nivel_habilidade"] == "iniciante"){
        nivel_pessoal = 2.0;
    }else if (doc.habilidades[item]["nivel_habilidade"] == "apto"){
        nivel_pessoal = 3.0;
    }else if (doc.habilidades[item]["nivel_habilidade"] == "proficiente"){
        nivel_pessoal = 4.0;
    }else if (doc.habilidades[item]["nivel_habilidade"] == "especialista"){
        nivel_pessoal = 5.0;
    }

    nivel_social = 0.0;
    num_validacoes = 0.0;
    for (user in doc.habilidades[item]["usuarios_referencia"]){
        if (doc.habilidades[item]["usuarios_referencia"][user]["nivel"] == "novato"){
            nivel_social = nivel_social + 1.0;
            num_validacoes = num_validacoes + 1.0;
        }else if (doc.habilidades[item]["usuarios_referencia"][user]["nivel"] == "iniciante"){
            nivel_social = nivel_social + 2.0;
            num_validacoes = num_validacoes + 1.0;
        }else if (doc.habilidades[item]["usuarios_referencia"][user]["nivel"] == "apto"){
            nivel_social = nivel_social + 3.0;
            num_validacoes = num_validacoes + 1.0;
        }else if (doc.habilidades[item]["usuarios_referencia"][user]["nivel"] == "proficiente"){
            nivel_social = nivel_social + 4.0;
            num_validacoes = num_validacoes + 1.0;
        }else if (doc.habilidades[item]["usuarios_referencia"][user]["nivel"] == "especialista"){
            nivel_social = nivel_social + 5.0;
            num_validacoes = num_validacoes + 1.0;
        }else{
            nivel_social = nivel_social + 0.0;
        }
    }
    if (num_validacoes == 0.0){
        num_validacoes = 1.0;
    }

    if (doc.habilidades[item]["producoes_referencia"].length > 0.0){
        nivel_producoes = 5.0;
    }else{
        nivel_producoes = 0.0;
    }

    nivel_geral = (nivel_pessoal*peso_pessoal +
                  (nivel_social/num_validacoes)*peso_social +
                  nivel_producoes*peso_producoes)
                  / num_parcelas;
    
    if ((nivel_geral >= 0.0) && (nivel_geral <= 1.69)){
        nivel_geral = 1;
    }else if ((nivel_geral >= 1.7) && (nivel_geral <= 2.69)){
        nivel_geral = 2;
    }else if ((nivel_geral >= 2.7) && (nivel_geral <= 3.69)){
        nivel_geral = 3;
    }else if ((nivel_geral >= 3.7) && (nivel_geral <= 4.69)){
        nivel_geral = 4;
    }else if (nivel_geral >= 4.7){
        nivel_geral = 5;
    }
"""
_DOCBASES = ['skill']

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


__ACTIV = Activ(COUCHDB_URL)
SKILL = __ACTIV.skill


################################################
# CouchDB Permanent Views
################################################

#Permite obter todas as experiências profissionais e acadêmicas de um usuário, bem como suas habilidades cadastradas. 
skill_by_user = ViewDefinition('skill','by_user', \
                               '''function(doc) { 
                                       emit([doc._id],  doc);
                                   }
                                '''
                                )

#Permite obter os campos referentes às formações acadêmicas de um usuário 
skill_user_academic_experience = ViewDefinition('skill','user_academic_experience', \
                               '''function(doc) {
                                           emit([doc._id],  {formacao : doc.formacao, habilidades: doc.habilidades,
                                               habilidades_pendentes: doc.habilidades_pendentes,
                                               habilidades_recusadas: doc.habilidades_recusadas,
                                               habilidades_invalidas: doc.habilidades_invalidas});
                                   }
                                '''
                                )

#Permite obter os campos referentes às experiências profissionais de um usuário 
skill_user_professional_experience = ViewDefinition('skill','user_professional_experience', \
                               '''function(doc) {
                                           emit([doc._id],  {experiencias : doc.experiencias, habilidades: doc.habilidades,
                                               habilidades_pendentes: doc.habilidades_pendentes,
                                               habilidades_recusadas: doc.habilidades_recusadas,
                                               habilidades_invalidas: doc.habilidades_invalidas});
                                   }
                                '''
                                )


#Permite obter todos os nomes de habilidades, habilidades_pendentes e habilidades_recusadas no banco de dados 
skill_all_skills = ViewDefinition('skill','all_skills', \
                               '''function(doc) {
                                           habilidades = [];
                                           for (item in doc.habilidades){
                                               habilidades[habilidades.length] = doc.habilidades[item]["nome_habilidade"];
                                           }
                                           pendentes = [];
                                           for (item in doc.habilidades_pendentes){
                                               pendentes[pendentes.length] = doc.habilidades_pendentes[item]["nome_habilidade"];
                                           }
                                           recusadas = [];
                                           for (item in doc.habilidades_recusadas){
                                               recusadas[recusadas.length] = doc.habilidades_recusadas[item]["nome_habilidade"];
                                           }
                                           emit([habilidades, pendentes, recusadas],  null);
                                   }
                                '''
                                )

#Permite obter todas as habilidades sugeridas por um usuário
skill_user_suggested = ViewDefinition('skill','user_suggested', \
                               '''function(doc) {
                                    for (item in doc.habilidades){
                                        for (user in doc.habilidades[item]["usuarios_referencia"]){   
                                            emit(doc.habilidades[item]["usuarios_referencia"][user]["nome"], 
                                                {nome_habilidade: doc.habilidades[item]["nome_habilidade"],
                                                nivel_habilidade: doc.habilidades[item]["usuarios_referencia"][user]["nivel"],
                                                tipo: "habilidade"});
                                        }
                                     }
                                     for (item in doc.habilidades_pendentes){
                                        for (user in doc.habilidades_pendentes[item]["usuarios_referencia"]){   
                                            emit(doc.habilidades_pendentes[item]["usuarios_referencia"][user]["nome"], 
                                                {nome_habilidade: doc.habilidades_pendentes[item]["nome_habilidade"],
                                                nivel_habilidade: doc.habilidades_pendentes[item]["usuarios_referencia"][user]["nivel"],
                                                tipo: "habilidade_pendente"});
                                        }
                                     }
                                     for (item in doc.habilidades_recusadas){
                                        for (user in doc.habilidades_recusadas[item]["usuarios_referencia"]){   
                                            emit(doc.habilidades_recusadas[item]["usuarios_referencia"][user]["nome"], 
                                                {nome_habilidade: doc.habilidades_recusadas[item]["nome_habilidade"],
                                                nivel_habilidade: doc.habilidades_recusadas[item]["usuarios_referencia"][user]["nivel"],
                                                tipo: "habilidade_recusada"});
                                        }
                                     }
                                     for (item in doc.habilidades_invalidas){
                                        for (user in doc.habilidades_invalidas[item]["usuarios_referencia"]){   
                                            emit(doc.habilidades_invalidas[item]["usuarios_referencia"][user]["nome"], 
                                                {nome_habilidade: doc.habilidades_invalidas[item]["nome_habilidade"],
                                                nivel_habilidade: doc.habilidades_invalidas[item]["usuarios_referencia"][user]["nivel"],
                                                tipo: "habilidade_invalida"});
                                        }
                                     }
                                   }
                                '''
                                )

#Permite obter os usuários que possuem determinada habilidade em uma de suas listas
skill_users_by_skill = ViewDefinition('skill','users_by_skill', \
                               '''function(doc) {
                                    for (item in doc.habilidades){   
                                            emit(doc.habilidades[item]["nome_habilidade"], null);
                                     }
                                     for (item in doc.habilidades_pendentes){   
                                            emit(doc.habilidades_pendentes[item]["nome_habilidade"], null);
                                     }
                                     for (item in doc.habilidades_recusadas){   
                                            emit(doc.habilidades_recusadas[item]["nome_habilidade"], null);
                                     }                                     
                                     for (item in doc.habilidades_invalidas){   
                                            emit(doc.habilidades_invalidas[item]["nome_habilidade"], null);
                                     }
                                   }
                                '''
                                )

#Permite obter os usuários que possuem determinada habilidade confirmada
skill_users_by_confirmed = ViewDefinition('skill','users_by_confirmed', \
                               '''function(doc) {
                                       var STOPWORDS = %s;
                                    
                                       lista_split = [];
                                        for (item in doc.habilidades){
                                            lista_split = doc.habilidades[item]["nome_habilidade"].split(" ");
                                            for (i in lista_split){
                                                if (STOPWORDS.indexOf(lista_split[i]) == -1 && lista_split[i] != "AND"){
                                                
                                                    %s
                                                    
                                                    emit(lista_split[i], {"nome_habilidade" : doc.habilidades[item]["nome_habilidade"],
                                                                          "nivel" : nivel_geral});
                                                } 
                                            }
                                         }
                                    }
                                '''%(STOPWORDS_UNICODE, CALCULA_NIVEL_GERAL)
                                )

ViewDefinition.sync_many(SKILL, [skill_by_user, skill_user_academic_experience, skill_user_professional_experience, skill_all_skills, \
                                 skill_user_suggested, skill_users_by_skill, skill_users_by_confirmed])

