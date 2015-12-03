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

from uuid import uuid4
from datetime import datetime, timedelta
import os

try:
  from couchdb.schema import Document, TextField, IntegerField, LongField, DateTimeField, DictField, ListField, Schema, FloatField
except ImportError:
  from couchdb.mapping import Document, TextField, IntegerField, LongField, DateTimeField, DictField, ListField, FloatField
  from couchdb.mapping import Mapping as Schema
  
import database
import core.model
import core.database


def getAllSkills():

    autocomplete_all_skills = []
    autocomplete_confirmed_skills = []
    for row in database.SKILL.view('skill/all_skills'):#Key[0] = lista de habilidades; key[1] = habilidades_pendentes; key[2] = habilidades_recusadas
        for item0 in row.key[0]:
            if (item0.encode('iso-8859-1', 'ignore')) not in autocomplete_all_skills:
                autocomplete_all_skills.append(item0.encode('iso-8859-1', 'ignore'))
                autocomplete_confirmed_skills.append(item0.encode('iso-8859-1', 'ignore'))
        for item1 in row.key[1]:            
            if (item1.encode('iso-8859-1', 'ignore')) not in autocomplete_all_skills:
                autocomplete_all_skills.append(item1.encode('iso-8859-1', 'ignore'))
        for item2 in row.key[2]:
            if (item2.encode('iso-8859-1', 'ignore')) not in autocomplete_all_skills:
                autocomplete_all_skills.append(item2.encode('iso-8859-1', 'ignore'))
    return (autocomplete_all_skills, autocomplete_confirmed_skills)

from HTMLParser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


class Skill(Document):
    # Provavelmente sofrerá alterações devido à abstração de dificuldades em virtude de uma abordagem inicial básica

    owner                   = TextField()
    formacao                = ListField(DictField())
    experiencias            = ListField(DictField())
    habilidades             = ListField(DictField())
    habilidades_pendentes   = ListField(DictField())
    habilidades_recusadas   = ListField(DictField())
    habilidades_invalidas   = ListField(DictField())
    producoes               = ListField(DictField())
    cabecalho_lattes        = DictField()
    
    @classmethod    
    def checkUserSkill(self, user, tipo, includeId=True):
        #Retorna se o documento referente à user existe no banco. Se includeId for True, também retorna a id da próxima habilidade, formação ou experiência a ser incluída.
        ja_existente = False
        skill_id = "0"
        id_habilidade = "0"
        for row in database.SKILL.view('skill/by_user',startkey=[user],endkey=[user, {}]):
            ja_existente = True
            if(includeId):
                if tipo == "academic":
                    if row.value["formacao"]:
                        skill_id = str(int(row.value["formacao"][-1]["id_formacao"])+1) #indica qual o proximo id a ser atribuído
                    if row.value["habilidades"]:
                        id_habilidade = str(int(row.value["habilidades"][-1]["id_habilidade"])+1) #indica qual o proximo id a ser atribuído
                elif tipo == "professional":
                    if row.value["experiencias"]:
                        skill_id = str(int(row.value["experiencias"][-1]["id_experiencias"])+1) #indica qual o proximo id a ser atribuído
                    if row.value["habilidades"]:
                        id_habilidade = str(int(row.value["habilidades"][-1]["id_habilidade"])+1) #indica qual o proximo id a ser atribuído
                elif tipo == "skills":
                    if row.value["habilidades"]:
                        skill_id = str(int(row.value["habilidades"][-1]["id_habilidade"])+1) #indica qual o proximo id a ser atribuído
                elif tipo == "productions":
                    skill_id = "0"
        
        if includeId:
            if tipo == "academic" or tipo == "professional":
                return(ja_existente, skill_id, id_habilidade)
            else:
                return (ja_existente, skill_id)
        else:
            return ja_existente
    
    @classmethod    
    def getSkill(self, user, tipo):
        for row in database.SKILL.view('skill/by_user',startkey=[user],endkey=[user, {}]):
            if tipo == "experience":
                formacao = row.value["formacao"]
                experiencias = row.value["experiencias"]
                habilidades_sem_nivel = False #Booleano que indica se há habilidades sem o nível informado no banco
                for habil in row.value["habilidades"]:
                    if habil["nivel_habilidade"] == "":
                            habilidades_sem_nivel = True
                            break
                return (formacao, experiencias, habilidades_sem_nivel)
            elif tipo == "skills_sem_nivel":
                habilidades_sem_nivel = []
                for habil in row.value["habilidades"]:
                    if habil["nivel_habilidade"] == "":
                        habilidades_sem_nivel.append(habil) 
                return habilidades_sem_nivel
            elif tipo == "skills_pending_refused":
                habilidades_sem_nivel = False #Booleano que indica se há habilidades sem o nível informado no banco
                for habil in row.value["habilidades"]:
                    if habil["nivel_habilidade"] == "":
                            habilidades_sem_nivel = True
                            break
                return (row.value["habilidades"], row.value["habilidades_pendentes"], row.value["habilidades_recusadas"], habilidades_sem_nivel)
            elif tipo == "skills_pending_refused_invalid":
                return (row.value["habilidades"], row.value["habilidades_pendentes"], row.value["habilidades_recusadas"], row.value["habilidades_invalidas"])
            elif tipo == "skills_refused_invalid":
                return (row.value["habilidades"], row.value["habilidades_recusadas"], row.value["habilidades_invalidas"])
            elif tipo == "refused":
                return row.value["habilidades_recusadas"]
            elif tipo == "pending":
                return row.value["habilidades_pendentes"]
            elif tipo == "skills_and_pending":
                return (row.value["habilidades"], row.value["habilidades_pendentes"])
        #Retornar vazio caso não haja documento no banco
        if tipo == "refused" or tipo == "pending" or tipo == "skills_sem_nivel":
            return []
        elif tipo == "skills_and_pending":
            return ([], [])
        elif tipo == "skills_refused_invalid" or tipo == "experience":
            return ([], [], [])
        elif tipo == "skills_pending_refused" or tipo == "skills_pending_refused_invalid":
            return ([], [], [], [])
        
    @classmethod    
    def getSkillsToValidate(self, user, target):
        skills_to_validate = []
        ja_existente = False
        for row in database.SKILL.view('skill/by_user',startkey=[target],endkey=[target, {}]):
            for item in row.value["habilidades"]:
                ja_existente = False
                for ref in item["usuarios_referencia"]:
                    if user == ref["nome"]:
                        ja_existente = True
                        break
                if not ja_existente:
                    skills_to_validate.append(item["nome_habilidade"])
                    
            for item in row.value["habilidades_pendentes"]:
                ja_existente = False
                for ref in item["usuarios_referencia"]:
                    if user == ref["nome"]:
                        ja_existente = True
                        break
                if not ja_existente:
                    skills_to_validate.append(item["nome_habilidade"])
                 
        return skills_to_validate
    
    @classmethod    
    def getProduction(self, user, production_id):
        #Retorna os campos de uma produção em específico, oriunda da lista de produções do usuário
        for row in database.SKILL.view('skill/by_user',startkey=[user],endkey=[user, {}]):
            for item in row.value["producoes"]:
                if item["SEQUENCIA-PRODUCAO"] == production_id:
                    return item
                
    @classmethod    
    def getSkillReferences(self, user, tipo, skill_id):
        #Retorna a lista dos nomes de produções-referência e o número de usuários que validaram uma habilidade
        producoes_temp = []
        producoes_referencia = []
        academico_temp = []
        academico_referencia = []
        profissional_temp = []
        profissional_referencia = []
        numero_usuarios = 0
        dict_temp = dict()
        if tipo == "pending":
            for row in database.SKILL.view('skill/by_user',startkey=[user],endkey=[user, {}]):
                nome_habilidade = row.value["habilidades_pendentes"][int(skill_id)]["nome_habilidade"]            
                producoes_temp = row.value["habilidades_pendentes"][int(skill_id)]["producoes_referencia"]
                academico_temp = row.value["habilidades_pendentes"][int(skill_id)]["academico_referencia"]
                profissional_temp = row.value["habilidades_pendentes"][int(skill_id)]["profissional_referencia"]
                for usuario in row.value["habilidades_pendentes"][int(skill_id)]["usuarios_referencia"]:
                    if usuario["nivel"] != "skipped":
                        numero_usuarios = numero_usuarios + 1
                for item in producoes_temp:
                    for producao in row.value["producoes"]:
                        if producao["SEQUENCIA-PRODUCAO"] == item:
                            producoes_referencia.append(producao["TITULO-DO-ARTIGO"])
                            
                for item in academico_temp:
                    for form in row.value["formacao"]:
                        if form["id_formacao"] == item:
                            dict_temp["nivel"] = form["nivel"]
                            dict_temp["instituicao"] = form["instituicao"]
                            dict_temp["curso"] = form["curso"]
                            dict_temp["data_ini"] = form["data_ini"]
                            academico_referencia.append(dict_temp)
                            dict_temp = {}
                            
                for item in profissional_temp:
                    for exp in row.value["experiencias"]:
                        if exp["id_experiencias"] == item:
                            dict_temp["cargo"] = exp["cargo"]
                            dict_temp["empresa"] = exp["empresa"]
                            dict_temp["data_ini"] = exp["data_ini"]
                            profissional_referencia.append(dict_temp)
                            dict_temp = {}
        elif tipo == "refused":
            for row in database.SKILL.view('skill/by_user',startkey=[user],endkey=[user, {}]):
                nome_habilidade = row.value["habilidades_recusadas"][int(skill_id)]["nome_habilidade"]            
                producoes_temp = row.value["habilidades_recusadas"][int(skill_id)]["producoes_referencia"]
                academico_temp = row.value["habilidades_recusadas"][int(skill_id)]["academico_referencia"]
                profissional_temp = row.value["habilidades_recusadas"][int(skill_id)]["profissional_referencia"]
                for usuario in row.value["habilidades_recusadas"][int(skill_id)]["usuarios_referencia"]:
                    if usuario["nivel"] != "skipped":
                        numero_usuarios = numero_usuarios + 1
                for item in producoes_temp:
                    for producao in row.value["producoes"]:
                        if producao["SEQUENCIA-PRODUCAO"] == item:
                            producoes_referencia.append(producao["TITULO-DO-ARTIGO"])
                for item in academico_temp:
                    for form in row.value["formacao"]:
                        if form["id_formacao"] == item:
                            dict_temp["nivel"] = form["nivel"]
                            dict_temp["instituicao"] = form["instituicao"]
                            dict_temp["curso"] = form["curso"]
                            dict_temp["data_ini"] = form["data_ini"]
                            academico_referencia.append(dict_temp)
                            dict_temp = {}
                            
                for item in profissional_temp:
                    for exp in row.value["experiencias"]:
                        if exp["id_experiencias"] == item:
                            dict_temp["cargo"] = exp["cargo"]
                            dict_temp["empresa"] = exp["empresa"]
                            dict_temp["data_ini"] = exp["data_ini"]
                            profissional_referencia.append(dict_temp)
                            dict_temp = {}
        elif tipo == "confirmed":
            for row in database.SKILL.view('skill/by_user',startkey=[user],endkey=[user, {}]):            
                for habil in row.value["habilidades"]:
                    if habil["id_habilidade"] == skill_id:
                        nome_habilidade = habil["nome_habilidade"]
                        producoes_temp = habil["producoes_referencia"]
                        academico_temp = habil["academico_referencia"]
                        profissional_temp = habil["profissional_referencia"]
                        for usuario in habil["usuarios_referencia"]:
                            if usuario["nivel"] != "skipped":
                                numero_usuarios = numero_usuarios + 1
                        break
                for item in producoes_temp:
                    for producao in row.value["producoes"]:
                        if producao["SEQUENCIA-PRODUCAO"] == item:
                            producoes_referencia.append(producao["TITULO-DO-ARTIGO"])
                            
                for item in academico_temp:
                    for form in row.value["formacao"]:
                        if form["id_formacao"] == item:
                            dict_temp["nivel"] = form["nivel"]
                            dict_temp["instituicao"] = form["instituicao"]
                            dict_temp["curso"] = form["curso"]
                            dict_temp["data_ini"] = form["data_ini"]
                            academico_referencia.append(dict_temp)
                            dict_temp = {}
                            
                            
                for item in profissional_temp:
                    for exp in row.value["experiencias"]:
                        if exp["id_experiencias"] == item:
                            dict_temp["cargo"] = exp["cargo"]
                            dict_temp["empresa"] = exp["empresa"]
                            dict_temp["data_ini"] = exp["data_ini"]
                            profissional_referencia.append(dict_temp)
                            dict_temp = {}
        
        return (nome_habilidade, producoes_referencia, numero_usuarios, academico_referencia, profissional_referencia)

    @classmethod    
    def getSkillsToReview(self, user, target):
        skills_to_review = []
        temp_dict = dict()
        
        for row in database.SKILL.view('skill/by_user',startkey=[target],endkey=[target, {}]):
            for habil in row.value["habilidades"]:
                for usuario_referencia in habil["usuarios_referencia"]:
                    if user == usuario_referencia["nome"]:
                        temp_dict = habil
                        temp_dict["nivel"] = usuario_referencia["nivel"]
                        skills_to_review.append(temp_dict)
                        break
            for pend in row.value["habilidades_pendentes"]:
                for usuario_referencia in pend["usuarios_referencia"]:
                    if user == usuario_referencia["nome"]:
                        temp_dict = pend
                        temp_dict["nivel"] = usuario_referencia["nivel"]
                        skills_to_review.append(temp_dict)
                        break
            for recusada in row.value["habilidades_recusadas"]:
                for usuario_referencia in recusada["usuarios_referencia"]:
                    if user == usuario_referencia["nome"]:
                        temp_dict = recusada
                        temp_dict["nivel"] = usuario_referencia["nivel"]
                        skills_to_review.append(temp_dict)
                        break
            for invalida in row.value["habilidades_invalidas"]:
                for usuario_referencia in invalida["usuarios_referencia"]:
                    if user == usuario_referencia["nome"]:
                        temp_dict = invalida
                        temp_dict["nivel"] = usuario_referencia["nivel"]
                        skills_to_review.append(temp_dict)
                        break
            
        return skills_to_review
        
    @classmethod    
    def getProductionData(self, user, includeFileData=False):
        #Retorna uma tupla, com os seguitnes dados:
        ## Lista de produções do usuário (producoes, no banco)
        ## Lista de Habilidades Pendentes do usuário (habilidades_pendentes, no banco)
        ## OPCIONAL - Lista com dados do XML do banco, se este existir. Esta lista contém:
        #### [0] - Nome do Arquivo
        #### [1] - Hora e minuto da última atualização, no formato HH:MM
        #### [2] - Dia, mês e ano da última atualização, no formato DD/MM/AAAA
        producoes = []
        habilidades_pendentes = []
        file_data = []
        for row in database.SKILL.view('skill/by_user',startkey=[user],endkey=[user, {}]):
            producoes = row.value["producoes"]
            habilidades_pendentes = row.value["habilidades_pendentes"]
            
            if "_attachments" in row.value:
                    file_data.append(row.value["_attachments"].keys()[0])
                    #Hora e minuto da ultima atualizacao, no formato hh:mm
                    file_data.append(row.value["cabecalho_lattes"]["HORA-ATUALIZACAO"][0:2]+":"+row.value["cabecalho_lattes"]["HORA-ATUALIZACAO"][2:4])
                    #Dia, mês e ano da ultima atualizacao, no formato dd/mm/aaaa
                    file_data.append(row.value["cabecalho_lattes"]["DATA-ATUALIZACAO"][0:2]+"/"+row.value["cabecalho_lattes"]["DATA-ATUALIZACAO"][2:4]\
                                    +"/"+row.value["cabecalho_lattes"]["DATA-ATUALIZACAO"][4:8])
        if includeFileData:
            return (producoes, habilidades_pendentes, file_data)
        else:
            return (producoes, habilidades_pendentes)

    @classmethod
    def checkProductionSkills(self, producoes, file_data):
        ##Retorna um inteiro (0, 1 ou 2):
        #Retorna 0 se o usuário ainda não subiu um xml de currículo lattes
        #Retorna 1 se há habilidades oriundas do currículo do usuário
        #Retorna 2 se NÃO há habilidades oriundas do currículo do usuário
        if len(file_data) == 0:
            return 0 
        palavras_chave = 0
        for prod in producoes:
            for i in range(6):
                try:
                    if (prod["PALAVRA-CHAVE-"+str(i+1)]):
                        palavras_chave = palavras_chave + 1
                except:
                    palavras_chave = palavras_chave
        if palavras_chave > 0:
            return 1
        else:
            return 2
        

    @classmethod    
    def getProductionDataAll(self, user):
        #Retorna uma tupla, com os seguitnes dados:
        ## Lista de produções do usuário (producoes, no banco)
        ## Lista de Habilidades do usuário (habilidades, no banco)
        ## Lista de Habilidades Pendentes do usuário (habilidades_pendentes, no banco)
        ## Lista de Habilidades Recusadas pelo usuário (habilidades_recusadas, no banco)
        producoes = []
        habilidades_pendentes = []
        for row in database.SKILL.view('skill/by_user',startkey=[user],endkey=[user, {}]):
            producoes = row.value["producoes"]
            habilidades_pendentes = row.value["habilidades_pendentes"]
            habilidades_recusadas = row.value["habilidades_recusadas"]
            habilidades = row.value["habilidades"]
        
        return (producoes, habilidades, habilidades_pendentes, habilidades_recusadas)
                
    @classmethod    
    def get_skillToEdit(self, user, tipo, skill_id):
        skill_to_edit = dict()
        if tipo == "academic":
            for row in database.SKILL.view('skill/user_academic_experience',startkey=[user],endkey=[user, {}]):
                for item in row.value["formacao"]:
                    if item["id_formacao"] == skill_id:
                        skill_to_edit = item
                        break
        elif tipo == "professional":
            for row in database.SKILL.view('skill/user_professional_experience',startkey=[user],endkey=[user, {}]):
                for item in row.value["experiencias"]:
                    if item["id_experiencias"] == skill_id:
                        skill_to_edit = item
                        break    
        skill_to_edit["habilidades"].sort()
        return skill_to_edit
                
    
    @classmethod    
    def removeSkill(self, user, skill_id, tipo):
        remove_document = False
        
        if tipo == "academic":
            for row in database.SKILL.view('skill/by_user',startkey=[user],endkey=[user, {}]):
                for item in row.value["formacao"]:
                    if item["id_formacao"] == skill_id:
                        item_to_remove = item
                        
                #Testa se o item a ser removido é a única coisa no documento   
                if((len(row.value["experiencias"]) + len(row.value["formacao"]) + len(row.value["habilidades"]) + len(row.value["habilidades_pendentes"]) \
                     + len(row.value["habilidades_recusadas"]) + len(row.value["habilidades_invalidas"]) + len(row.value["producoes"]) == 1) and \
                     ("_attachments" not in row.value) and (row.value["cabecalho_lattes"] != {})):
                    remove_document = True
        elif tipo == "professional":
            for row in database.SKILL.view('skill/by_user',startkey=[user],endkey=[user, {}]):
                for item in row.value["experiencias"]:
                    if item["id_experiencias"] == skill_id:
                        item_to_remove = item
                #Testa se o item a ser removido é a única coisa no documento
                if((len(row.value["experiencias"]) + len(row.value["formacao"]) + len(row.value["habilidades"]) + len(row.value["habilidades_pendentes"]) \
                     + len(row.value["habilidades_recusadas"]) + len(row.value["habilidades_invalidas"]) + len(row.value["producoes"]) == 1) and \
                     ("_attachments" not in row.value) and (row.value["cabecalho_lattes"] != {})):
                    remove_document = True
                
        elif tipo == "skills":
            for row in database.SKILL.view('skill/by_user',startkey=[user],endkey=[user, {}]):
                for item in row.value["habilidades"]:
                    if item["id_habilidade"] == skill_id:
                        item_to_remove = item
                #Testa se o item a ser removido é a única coisa no documento        
                if((len(row.value["experiencias"]) + len(row.value["formacao"]) + len(row.value["habilidades"]) + len(row.value["habilidades_pendentes"]) \
                     + len(row.value["habilidades_recusadas"]) + len(row.value["habilidades_invalidas"]) + len(row.value["producoes"]) == 1) and \
                     ("_attachments" not in row.value) and (row.value["cabecalho_lattes"] != {})):
                    remove_document = True

        return (item_to_remove, remove_document)

    @classmethod    
    def checkLastLattesUpdate(self, user, content):
        #Retorna True se a data de criação do xml do banco é mais antiga que a do content, False caso contrário
        import elementtree.ElementTree as ET
        root = ET.fromstring(content)
        
        for row in database.SKILL.view('skill/by_user',startkey=[user],endkey=[user, {}]):
            #Colocando dados na forma AAAAMMDD para comparação aritmética
            data_banco = row.value["cabecalho_lattes"]["DATA-ATUALIZACAO"][4:8]+row.value["cabecalho_lattes"]["DATA-ATUALIZACAO"][2:4]+row.value["cabecalho_lattes"]["DATA-ATUALIZACAO"][0:2]
            data_submissao = root.get("DATA-ATUALIZACAO")[4:8]+root.get("DATA-ATUALIZACAO")[2:4]+root.get("DATA-ATUALIZACAO")[0:2]

            if (int(data_banco) <= int(data_submissao)) and \
                (int(row.value["cabecalho_lattes"]["HORA-ATUALIZACAO"]) < int(root.get("HORA-ATUALIZACAO"))):
                return True
            else:
                return False
            
    @classmethod    
    def CalculaMediaNiveis(self, niveis):
        #Recebe uma lista de niveis e calcula a média dos mesmos, retornando o nível médio tanto como número e classificação (novato, iniciante...)
        if len(niveis) == 0:
            return (0.0, u"sem sugestões")
        
        media_num = 0.0
        for s in niveis:
            if s == "novato":
                media_num += 1.0
                continue
            if s == "iniciante":
                media_num += 2.0
                continue
            if s == "apto":
                media_num += 3.0
                continue
            if s == "proficiente":
                media_num += 4.0
                continue
            if s == "especialista":
                media_num += 5.0
                continue
        media_num /= len(niveis)
        
        if media_num >= 0.0 and media_num <= 1.69:
            media_str = "novato"
        elif media_num >= 1.7 and media_num <= 2.69:
            media_str = "iniciante"
        elif media_num >= 2.7 and media_num <= 3.69:
            media_str = "apto"
        elif media_num >= 3.7 and media_num <= 4.69:
            media_str = "proficiente"
        elif media_num >= 4.7:
            media_str = "especialista"
            
        return (media_num, media_str)
            
    @classmethod    
    def calculaNivelHabilidade(self, user):
        #
        lista_habilidades = []
        dict_habilidades = dict()
        #dict_habilidades["nivel_geral"]
        #dict_habilidades["nome_habilidade"]
        ###Variáveis para a fórmula de cálculo do nível geral:
        ##nivel_pessoal: nível da habilidade que o próprio usuário informou
        ##nivel_social: soma dos níveis apontados pelos amigos do usuário
        ##num_validacoes: número de usuários que validaram a habilidade
        ##nivel_producoes: temporariamente definido como 5, nível máximo
        ##peso_pessoal: peso dado ao nivel_pessoal
        peso_pessoal = 1.0
        ##peso_social: peso dado ao nivel_social
        peso_social = 1.0
        ##peso_producoes: peso dado ao nivel_producoes
        peso_producoes = 1.0
        ##num_parcelas: número de parcelas para o cálculo da média. Por enquanto, 3: nivel_pessoal, nivel_social e nivel_producoes
        num_parcelas = 3.0
        
        for row in database.SKILL.view('skill/by_user',startkey=[user],endkey=[user, {}]):
            for habil in row.value["habilidades"]:
                dict_habilidades["nome_habilidade"] = habil["nome_habilidade"]
                dict_habilidades["id_habilidade"] = habil["id_habilidade"]
                #nivel_pessoal:
                nivel_pessoal = 0.0
                if habil["nivel_habilidade"] == "novato":
                    nivel_pessoal = 1.0
                elif habil["nivel_habilidade"] == "iniciante":
                    nivel_pessoal = 2.0
                elif habil["nivel_habilidade"] == "apto":
                    nivel_pessoal = 3.0
                elif habil["nivel_habilidade"] == "proficiente":
                    nivel_pessoal = 4.0
                elif habil["nivel_habilidade"] == "especialista":
                    nivel_pessoal = 5.0
                #nivel_social:
                nivel_social = 0.0
                num_validacoes = 0.0
                for item in habil["usuarios_referencia"]:
                    if item["nivel"] == "novato":
                        nivel_social = nivel_social + 1.0
                        num_validacoes = num_validacoes + 1.0
                    elif item["nivel"] == "iniciante":
                        nivel_social = nivel_social + 2.0
                        num_validacoes = num_validacoes + 1.0
                    elif item["nivel"] == "apto":
                        nivel_social = nivel_social + 3.0
                        num_validacoes = num_validacoes + 1.0
                    elif item["nivel"] == "proficiente":
                        nivel_social = nivel_social + 4.0
                        num_validacoes = num_validacoes + 1.0
                    elif item["nivel"] == "especialista":
                        nivel_social = nivel_social + 5.0
                        num_validacoes = num_validacoes + 1.0
                    else:
                        nivel_social = nivel_social + 0.0
                if num_validacoes == 0.0:
                    num_validacoes = 1.0
                #nivel_producoes
                if len(habil["producoes_referencia"]) > 0.0:
                    nivel_producoes = 5.0
                else:
                    nivel_producoes = 0.0
                
                #calculo do nível geral:                
                nivel_geral = (nivel_pessoal*peso_pessoal + \
                              (nivel_social/num_validacoes)*peso_social + \
                              nivel_producoes) \
                              / num_parcelas
                
                if nivel_geral >= 0.0 and nivel_geral <= 1.69:
                    nivel_geral = 1
                elif nivel_geral >= 1.7 and nivel_geral <= 2.69:
                    nivel_geral = 2
                elif nivel_geral >= 2.7 and nivel_geral <= 3.69:
                    nivel_geral = 3
                elif nivel_geral >= 3.7 and nivel_geral <= 4.69:
                    nivel_geral = 4
                elif nivel_geral >= 4.7:
                    nivel_geral = 5
                
                              
                dict_habilidades["nivel_geral"] = nivel_geral
                lista_habilidades.append(dict_habilidades)
                dict_habilidades = {}
        return lista_habilidades
                                
    @classmethod
    def buscaSkill(self, str_busca, filtros):
        from search.model import STOPWORDS
        #Palavras reservadas: AND
        lista_busca = []
        for word in str_busca.split(" "):
            if word.encode('iso-8859-1', 'ignore') not in STOPWORDS and len(lista_busca) <= 10 and (word == "AND" or (word != "AND" and word not in lista_busca)):
                lista_busca.append(word)

        lista_habilidades = []
        dict_habilidades = dict()
        lista_resposta = []
        dict_temp = dict()
        
        if "AND" not in lista_busca:
            for item in lista_busca:
                for row in database.SKILL.view('skill/users_by_confirmed', key=item):
                    if row.value["nome_habilidade"] not in lista_habilidades:
                        lista_habilidades.append(row.value["nome_habilidade"])
                        dict_habilidades["nome_habilidade"] = row.value["nome_habilidade"]
                        dict_habilidades["usuarios"] = []
                        dict_temp["nome_usuario"] = row.id
                        dict_temp["nivel"] = row.value["nivel"]
                        dict_habilidades["usuarios"].append(dict_temp)
                        dict_temp = {}
                        lista_resposta.append(dict_habilidades)
                        dict_habilidades = {}
                        
                    else:
                        for i in range(len(lista_resposta)):
                            lista_usuarios = []
                            for user in lista_resposta[i]["usuarios"]:
                                lista_usuarios.append(user["nome_usuario"])
                            if row.id not in lista_usuarios:
                                if lista_resposta[i]["nome_habilidade"] == row.value["nome_habilidade"]: 
                                    dict_temp["nome_usuario"] = row.id
                                    dict_temp["nivel"] = row.value["nivel"]
                                    lista_resposta[i]["usuarios"].append(dict_temp)
                                    dict_temp = {}
                                    break
        #else: #Se há AND na busca
            #TODO
                            
            
        for resp in lista_resposta:
            resp["usuarios"].sort(key=lambda x: x["nivel"], reverse=True)
            termo_temp = []
            for termo in resp["nome_habilidade"].split(" "):
                if termo not in STOPWORDS:
                    termo_temp.append(termo)
            
            if len(lista_busca) > 0:
                resp["grau_relevancia"] = float(len(termo_temp)) / float(len(lista_busca))
            else: #Não deve entrar nunca...
                resp["grau_relevancia"] = float(len(termo_temp)) / 1.0
            
        lista_resposta.sort(key=lambda x: x["grau_relevancia"], reverse=True)
        
        return lista_resposta
        
    @classmethod    
    def getProductionsFromXML(self, user, content, producoes_old, habilidades, habilidades_pendentes, habilidades_recusadas):
        #Essa função visa fazer o corte do conteúdo do XML enviado pelo usuário, para obter os dados de suas publicações no Lattes
        import elementtree.ElementTree as ET
        erro = 0 #variavel para marcar codigo de erro, caso haja um
        header = dict() #dados de controle: id do lattes, data e hora da ultima atualizacao
        producoes = [] #lista de artigos publicados pelo usuario
        dict_producoes = dict() #cada producao é um dicionario com os campos
        dict_autores = dict() #dicionario a ser usado para suporte à lista de autores de cada produção
        lista_autores = [] #lista de autores de cada produção, cada item contendo os dados do dicionário dict_autores
        dict_area = dict() #dicionario a ser usado para suporte à lista de áreas do conhecimento de cada produção
        lista_area = [] #lista de áreas de conhecimento de uma produção. Por definição do Lattes, cada produção tem até 3 áreas
        dict_habilidades = dict() #dicionario a ser utilizado para dar suporte às listas de habilidades 
        lista_temp = [] #lista temporária que guarda os nomes das habilidades_pendentes e habilidades_recusadas. Facilita o processo de busca.
        lista_temp_habilidades = [] #lista temporária que guarda os nomes das habilidades. Facilita o processo de busca.
        for habil in habilidades:
            lista_temp_habilidades.append(habil["nome_habilidade"])
        for habil in habilidades_pendentes:
            lista_temp.append(habil["nome_habilidade"])
        for habil in habilidades_recusadas:
            lista_temp.append(habil["nome_habilidade"])
        
        root = ET.fromstring(content)
        
        if root.tag != "CURRICULO-VITAE": #validacao do xml certo
            erro = 1 #xml inválido
        
        header["DATA-ATUALIZACAO"] = root.get("DATA-ATUALIZACAO")
        header["HORA-ATUALIZACAO"] = root.get("HORA-ATUALIZACAO")
        header["NUMERO-IDENTIFICADOR"] = root.get("NUMERO-IDENTIFICADOR")
        
        for node in root:
            if node.tag == "DADOS-GERAIS":
                header["NOME-COMPLETO"] = node.get("NOME-COMPLETO")
                header["NOME-EM-CITACOES-BIBLIOGRAFICAS"] = node.get("NOME-EM-CITACOES-BIBLIOGRAFICAS")
                
            if node.tag == "PRODUCAO-BIBLIOGRAFICA":
                for production in node:
                    if production.tag == "ARTIGOS-PUBLICADOS":
                        for paper in production:
                            if paper.tag == "ARTIGO-PUBLICADO": #Será sempre verdade, se o usuário tiver artigo publicado
                                dict_producoes["SEQUENCIA-PRODUCAO"] = paper.get("SEQUENCIA-PRODUCAO")
                                for item in paper:
                                    if item.tag == "DADOS-BASICOS-DO-ARTIGO":
                                        dict_producoes["TITULO-DO-ARTIGO"] = item.get("TITULO-DO-ARTIGO")
                                        dict_producoes["ANO-DO-ARTIGO"] = item.get("ANO-DO-ARTIGO")
                                        dict_producoes["IDIOMA"] = item.get("IDIOMA")
                                        dict_producoes["TITULO-DO-ARTIGO-INGLES"] = item.get("TITULO-DO-ARTIGO-INGLES")
                                        dict_producoes["NATUREZA"] = item.get("NATUREZA")
                                        dict_producoes["PAIS-DE-PUBLICACAO"] = item.get("PAIS-DE-PUBLICACAO")
                                        dict_producoes["MEIO-DE-DIVULGACAO"] = item.get("MEIO-DE-DIVULGACAO")
                                        dict_producoes["HOME-PAGE-DO-TRABALHO"] = item.get("HOME-PAGE-DO-TRABALHO")
                                        dict_producoes["DOI"] = item.get("DOI")
                                    if item.tag == "DETALHAMENTO-DO-ARTIGO":
                                        dict_producoes["TITULO-DO-PERIODICO-OU-REVISTA"] = item.get("TITULO-DO-PERIODICO-OU-REVISTA")
                                        dict_producoes["ISSN"] = item.get("ISSN")
                                        dict_producoes["VOLUME"] = item.get("VOLUME")
                                        dict_producoes["FASCICULO"] = item.get("FASCICULO")
                                        dict_producoes["SERIE"] = item.get("SERIE")
                                        dict_producoes["PAGINA-INICIAL"] = item.get("PAGINA-INICIAL")
                                        dict_producoes["PAGINA-FINAL"] = item.get("PAGINA-FINAL")
                                        dict_producoes["LOCAL-DE-PUBLICACAO"] = item.get("LOCAL-DE-PUBLICACAO")
                                    if item.tag == "AUTORES":    
                                        dict_autores["NOME-COMPLETO-DO-AUTOR"] = item.get("NOME-COMPLETO-DO-AUTOR")
                                        dict_autores["NOME-PARA-CITACAO"] = item.get("NOME-PARA-CITACAO")
                                        dict_autores["ORDEM-DE-AUTORIA"] = item.get("ORDEM-DE-AUTORIA")
                                        dict_autores["NRO-ID-CNPQ"] = item.get("NRO-ID-CNPQ")
                                        
                                        for object in producoes_old:#For para manutenção de usernames dos autores caso o usuário já tenha preenchido
                                            if object["SEQUENCIA-PRODUCAO"] == dict_producoes["SEQUENCIA-PRODUCAO"]:
                                                for autor in object["AUTORES"]:
                                                    if "USERNAME-ACTIV" in autor:
                                                        if dict_autores["NOME-COMPLETO-DO-AUTOR"] == autor["NOME-COMPLETO-DO-AUTOR"] and \
                                                        dict_autores["NOME-PARA-CITACAO"] == autor["NOME-PARA-CITACAO"] and \
                                                        dict_autores["ORDEM-DE-AUTORIA"] == autor["ORDEM-DE-AUTORIA"] and \
                                                        dict_autores["NRO-ID-CNPQ"] == autor["NRO-ID-CNPQ"]:
                                                            dict_autores["USERNAME-ACTIV"] = autor["USERNAME-ACTIV"]
                                                break
                                        
                                        lista_autores.append(dict_autores)
                                        dict_autores = {}
                                    if item.tag == "PALAVRAS-CHAVE":                                        
                                        #Segundo a documentação do Lattes, todas as publicações tem os campos PALAVRA-CHAVE-i, i de 1 a 6:
                                        for i in range(1,7):
                                            dict_producoes["PALAVRA-CHAVE-"+str(i)] = item.get("PALAVRA-CHAVE-"+str(i)).lower()
                                            #Pegando apenas as palavras não-vazias:
                                            if dict_producoes["PALAVRA-CHAVE-"+str(i)] != "":
                                                if dict_producoes["PALAVRA-CHAVE-"+str(i)] in lista_temp:
                                                    #Habilidade ja existe na lista habilidades_pendentes
                                                    for habil in habilidades_pendentes:
                                                        if dict_producoes["PALAVRA-CHAVE-"+str(i)] == habil["nome_habilidade"]:
                                                            if dict_producoes["SEQUENCIA-PRODUCAO"] not in habil["producoes_referencia"]:
                                                                habil["producoes_referencia"].append(dict_producoes["SEQUENCIA-PRODUCAO"])
                                                                break
                                                else:
                                                    if dict_producoes["PALAVRA-CHAVE-"+str(i)] in lista_temp_habilidades:
                                                    #Habilidade já existente na lista de habilidades; Basta adicionar produção
                                                        for habil in habilidades:
                                                            if dict_producoes["PALAVRA-CHAVE-"+str(i)] == habil["nome_habilidade"]:
                                                                if dict_producoes["SEQUENCIA-PRODUCAO"] not in habil["producoes_referencia"]:
                                                                    habil["producoes_referencia"].append(dict_producoes["SEQUENCIA-PRODUCAO"])
                                                                    break
                                                    else:
                                                    #Habilidade nova para a lista habilidades_pendentes
                                                        dict_habilidades["nome_habilidade"] = dict_producoes["PALAVRA-CHAVE-"+str(i)]
                                                        dict_habilidades["usuarios_referencia"] = []
                                                        dict_habilidades["producoes_referencia"] = []
                                                        dict_habilidades["academico_referencia"] = []
                                                        dict_habilidades["profissional_referencia"] = []
                                                        dict_habilidades["producoes_referencia"].append(dict_producoes["SEQUENCIA-PRODUCAO"])
                                                        habilidades_pendentes.append(dict_habilidades)
                                                        lista_temp.append(dict_producoes["PALAVRA-CHAVE-"+str(i)])
                                                        dict_habilidades = {}
                                                        
                                        
                                    if item.tag == "AREAS-DO-CONHECIMENTO": #segundo a documentação do lattes, cada artigo pode ter até 3 áreas
                                        for area in item:
                                            dict_area["NOME-GRANDE-AREA-DO-CONHECIMENTO"] = area.get("NOME-GRANDE-AREA-DO-CONHECIMENTO")
                                            dict_area["NOME-DA-AREA-DO-CONHECIMENTO"] = area.get("NOME-DA-AREA-DO-CONHECIMENTO")
                                            dict_area["NOME-DA-SUB-AREA-DO-CONHECIMENTO"] = area.get("NOME-DA-SUB-AREA-DO-CONHECIMENTO")
                                            dict_area["NOME-DA-ESPECIALIDADE"] = area.get("NOME-DA-ESPECIALIDADE")
                                            lista_area.append(dict_area)
                                            dict_area = {}
                                    if item.tag == "INFORMACOES-ADICIONAIS":
                                        dict_producoes["DESCRICAO-INFORMACOES-ADICIONAIS"] = item.get("DESCRICAO-INFORMACOES-ADICIONAIS")
                                        dict_producoes["DESCRICAO-INFORMACOES-ADICIONAIS-INGLES"] = item.get("DESCRICAO-INFORMACOES-ADICIONAIS-INGLES")
                                    
                                    dict_producoes["AUTORES"] = lista_autores
                                    dict_producoes["AREAS-DO-CONHECIMENTO"] = lista_area
                                    
                                producoes.append(dict_producoes)
                                dict_producoes = {}
                                lista_autores = []
                                lista_area = []
        
        return (producoes, habilidades, habilidades_pendentes, header, erro)
        
        
    def saveFile(self, id, files, attachment=True):
        self.save(id=id)
        if attachment:
            database.SKILL.put_attachment(database.SKILL[id],
                                          files["body"],
                                          files["filename"],
                                          files["content_type"])
            
    def deleteAttachment(self, filename, db=database.SKILL):        
        db.delete_attachment(self, filename)
        return
   
    def save(self, id=None, db=database.SKILL):
        if not self.id and id: self.id = id
        self.store(db)
        
    def delete(self, db=database.SKILL):
        #db.delete(self)
        del db[self.id]

    def retrieve(self, id, db=database.SKILL):
        return Skill.load(db, id)