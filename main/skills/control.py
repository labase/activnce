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

import tornado.web
import tornado.template
import model
import database

from datetime import datetime
import core.model
from core.model import isACommunity, isAUser
from core.dispatcher import BaseHandler, HANDLERS, URL_TO_PAGETITLE, \
                            NOMEUSERS, PAGENAMECHARS
from search.model import splitTags
from config import PRIV_GLOBAL_ADMIN, PLATAFORMA                        
from libs.notify import Notify
import log.model

''' importa definição do tutorial deste módulo, se existir _tutorial.py '''
from config import TUTORIAL
try:
    import _tutorial
except ImportError:
    pass

# Número máximo de habilidades a serem exibidas no gráfico de radar
MAX_HABILIDADES_GRAFICO = 8
# Número mínimo de habilidades a serem exibidas no gráfico de radar
MIN_HABILIDADES_GRAFICO = 4 
# Número máximo de habilidades a serem exibidas no widget de habilidades pendentes
MAX_HABILIDADES_PENDENTES_WIDGET = 3

class ExperienceHandler(BaseHandler):
    ''' Visualização das experiências profissionais e formação acadêmica do usuário '''
    
    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        
        tabs = []
        tabs.append(("Editar Perfil", "/profile/edit"))
        tabs.append(("Alterar Senha", "/profile/changepasswd"))
        tabs.append(("Formação e Experiências", ""))
        tabs.append(("Produção Acadêmica - Lattes", "/profile/skills/productions"))
        tabs.append(("Habilidades", "/profile/skills/"+user))
        
        (formacao, experiencias, habilidades_sem_nivel) = model.Skill.getSkill(user, "experience")
        
        self.render("modules/skills/profile-edit-experience.html", REGISTRY_ID=user, MSG="", \
                        FORMACAO=formacao, EXPERIENCIAS=experiencias, HABILIDADES_SEM_NIVEL=habilidades_sem_nivel, TABS=tabs, NOMEPAG="perfil")
        
class AddAcademicExperienceHandler(BaseHandler):
    ''' Gerenciamento da Formação Acadêmica de um usuário '''   

    @tornado.web.authenticated
    def post(self):
        user = self.get_current_user()
        msg = ""
        
        (ja_existente, id_formacao, id_habilidade) = model.Skill.checkUserSkill(user, "academic")

        if(ja_existente): #Checa se o usuário já informou alguma experiência
            self._skill = model.Skill().retrieve(user)
        else:   
            self._skill = model.Skill()
            self._skill.owner = user
        
        formacao = dict()
        formacao["id_formacao"] = id_formacao
        formacao["instituicao"] = self.get_argument("formacao_instituicao","")
        if formacao["instituicao"] == "":
            msg += u"O campo Instituição deve ser preenchido.<br/>"
        formacao["curso"] = self.get_argument("formacao_curso","")
        formacao["nivel"] = self.get_argument("formacao_nivel","")
        data_ini =  self.get_argument("formacao_data_ini_ano","")+self.get_argument("formacao_data_ini_mes","")
        formacao["data_ini"] = data_ini[4:6]+"/"+data_ini[0:4]
        formacao_concluida = self.get_argument("formacao_check_andamento", "")
        if formacao_concluida == "on":
            data_fim =  self.get_argument("formacao_data_fim_ano","")+self.get_argument("formacao_data_fim_mes","")
        else:
            data_fim =  ""
        if data_fim:
            formacao["data_fim"] = data_fim[4:6]+"/"+data_fim[0:4]
        else:
            formacao["data_fim"] = ""
        if data_ini > data_fim and formacao_concluida == "on":
            msg += u"A data de início não pode ser posterior à data de término.<br/>"   
        formacao["descricao"] = self.get_argument("formacao_descricao","")
        if formacao["descricao"] == "":
            msg += u"O campo Descrição deve ser preenchido.<br/>"
        lista_habilidades_temp = []
        lista_habilidades_temp = splitTags(self.get_argument("formacao_habilidades",""))
        if len(lista_habilidades_temp) == 0:
            msg += u"O campo Habilidades deve ser preenchido.<br/>"
        lista_habilidades = []
        for item in lista_habilidades_temp:
            lista_habilidades.append(model.strip_tags(item))
        lista_habilidades.sort()
        formacao["habilidades"] = lista_habilidades 
        habilidade_existente = False #Booleano para identificar se a habilidade já existe no banco deste usuário
        dict_habil = dict() #Dicionário para servir de base caso a habilidade não seja encontrada no banco deste usuário
        for habil in lista_habilidades: #Para cada habilidade fornecida pelo usuário
            for item in self._skill.habilidades: #Verificar se já está na lista de habilidades do usuário
                if item["nome_habilidade"] == habil:
                    habilidade_existente = True
                    item["academico_referencia"].append(id_formacao)
                    break
            if not habilidade_existente: #Se ainda não achou, continue procurando
                for item in self._skill.habilidades_pendentes: #Verificar se já está na lista de habilidades_pendentes do usuário
                    if item["nome_habilidade"] == habil:
                        habilidade_existente = True
                        item["academico_referencia"].append(id_formacao)
                        break
                if not habilidade_existente: #Se ainda não achou, continue procurando
                    for item in self._skill.habilidades_recusadas: #Verificar se já está na lista de habilidades_recusadas do usuário
                        if item["nome_habilidade"] == habil:
                            habilidade_existente = True
                            item["academico_referencia"].append(id_formacao)
                            break
                    if not habilidade_existente: #Se ainda não achou, continue procurando
                        for item in self._skill.habilidades_invalidas: #Verificar se já está na lista de habilidades_invalidas do usuário
                            if item["nome_habilidade"] == habil:
                                habilidade_existente = True
                                item["academico_referencia"].append(id_formacao)
                                break
            if not habilidade_existente: #Se não achou em nenhuma lista, é uma nova habilidade_pendente
                dict_habil["nome_habilidade"] = habil
                dict_habil["usuarios_referencia"] = []
                dict_habil["producoes_referencia"] = []
                dict_habil["academico_referencia"] = [id_formacao]
                dict_habil["profissional_referencia"] = []
                dict_habil["nivel_habilidade"] = ""
                dict_habil["id_habilidade"] = id_habilidade
                
                self._skill.habilidades.append(dict_habil)
                id_habilidade = str(int(id_habilidade) + 1)
                dict_habil = {}
            habilidade_existente = False
        
        self._skill.formacao.append(formacao)
        
        if msg:
            self.render("home.html", MSG=msg, REGISTRY_ID=user, NOMEPAG="perfil")
            return
        
        self._skill.save(id=user)

        self.redirect("/profile/skills/new/experience")
            
        
        
class AddProfessionalExperienceHandler(BaseHandler):
    ''' Gerenciamento de Experiências Profissionais de um usuário '''
        
    @tornado.web.authenticated
    def post(self):
        user = self.get_current_user()
        msg = ""
        
        (ja_existente, id_experiencias, id_habilidade) = model.Skill.checkUserSkill(user, "professional")

        if(ja_existente): #Checa se o usuário já informou alguma experiência
            self._skill = model.Skill().retrieve(user)
        else:   
            self._skill = model.Skill()
            self._skill.owner = user
        
        experiencias = dict()
        experiencias["id_experiencias"] = id_experiencias
        experiencias["empresa"] = self.get_argument("experiencias_empresa","")
        if experiencias["empresa"] == "":
            msg += u"O campo Empresa/Projeto deve ser preenchido.<br/>"
        experiencias["cargo"] = self.get_argument("experiencias_cargo","")
        data_ini =  self.get_argument("experiencias_data_ini_ano","")+self.get_argument("experiencias_data_ini_mes","")
        experiencias["data_ini"] = data_ini[4:6]+"/"+data_ini[0:4]
        experiencia_concluida = self.get_argument("experiencias_check_andamento", "")
        if experiencia_concluida != "on":
            data_fim =  self.get_argument("experiencias_data_fim_ano","")+self.get_argument("experiencias_data_fim_mes","")
        else:
            data_fim =  ""
        if data_fim:
            experiencias["data_fim"] = data_fim[4:6]+"/"+data_fim[0:4]
        else:
            experiencias["data_fim"] = ""
        if data_ini > data_fim and experiencia_concluida != "on":
            msg += u"A data de início não pode ser posterior à data de término.<br/>"  
        experiencias["descricao"] = self.get_argument("experiencias_descricao","")
        if experiencias["descricao"] == "":
            msg += u"O campo Descrição deve ser preenchido.<br/>" 
        
        lista_habilidades_temp = []
        lista_habilidades_temp = splitTags(self.get_argument("experiencias_habilidades",""))
        if lista_habilidades_temp == "":
            msg += u"O campo Habilidades deve ser preenchido.<br/>" 
        lista_habilidades = []
        for item in lista_habilidades_temp:
            lista_habilidades.append(model.strip_tags(item))   
        lista_habilidades.sort()
        experiencias["habilidades"] = lista_habilidades 
        habilidade_existente = False #Booleano para identificar se a habilidade já existe no banco deste usuário
        dict_habil = dict() #Dicionário para servir de base caso a habilidade não seja encontrada no banco deste usuário
        for habil in lista_habilidades: #Para cada habilidade fornecida pelo usuário
            for item in self._skill.habilidades: #Verificar se já está na lista de habilidades do usuário
                if item["nome_habilidade"] == habil:
                    habilidade_existente = True
                    item["profissional_referencia"].append(id_experiencias)
                    break
            if not habilidade_existente: #Se ainda não achou, continue procurando
                for item in self._skill.habilidades_pendentes: #Verificar se já está na lista de habilidades_pendentes do usuário
                    if item["nome_habilidade"] == habil:
                        habilidade_existente = True
                        item["profissional_referencia"].append(id_experiencias)
                        break
                if not habilidade_existente: #Se ainda não achou, continue procurando
                    for item in self._skill.habilidades_recusadas: #Verificar se já está na lista de habilidades_recusadas do usuário
                        if item["nome_habilidade"] == habil:
                            habilidade_existente = True
                            item["profissional_referencia"].append(id_experiencias)
                            break
                    if not habilidade_existente: #Se ainda não achou, continue procurando
                        for item in self._skill.habilidades_invalidas: #Verificar se já está na lista de habilidades_invalidas do usuário
                            if item["nome_habilidade"] == habil:
                                habilidade_existente = True
                                item["profissional_referencia"].append(id_experiencias)
                                break
            if not habilidade_existente: #Se não achou em nenhuma lista, é uma nova habilidade_pendente
                dict_habil["nome_habilidade"] = habil
                dict_habil["usuarios_referencia"] = []
                dict_habil["producoes_referencia"] = []
                dict_habil["academico_referencia"] = []
                dict_habil["profissional_referencia"] = [id_experiencias]
                dict_habil["nivel_habilidade"] = ""
                dict_habil["id_habilidade"] = id_habilidade
                
                self._skill.habilidades.append(dict_habil)
                dict_habil = {}
                id_habilidade = str(int(id_habilidade) + 1)
            habilidade_existente = False
        
        self._skill.experiencias.append(experiencias)
        
        if msg:
            self.render("home.html", MSG=msg, REGISTRY_ID=user, NOMEPAG="perfil")
            return
        
        self._skill.save(id=user)

        self.redirect("/profile/skills/new/experience")

class EditSkillHandler(BaseHandler):
    ''' Edição de uma experiencia ou habilidade'''

    @tornado.web.authenticated
    def get(self, tipo, skill_id):
        user = self.get_current_user()
        
        skill_to_edit = model.Skill().get_skillToEdit(user, tipo, skill_id)

        self.render("modules/skills/profile-popup-edit-experience.html", NOMEPAG="perfil", \
                        SKILLDATA=skill_to_edit, TIPO=tipo, REGISTRY_ID=user, MSG="")
        
    @tornado.web.authenticated
    def post(self, tipo, skill_id):
        user = self.get_current_user()
        msg = ""
        self._skill = model.Skill().retrieve(user)
        
        if tipo == "academic":
            skill_to_edit = model.Skill().get_skillToEdit(user, tipo, skill_id)
            self._skill.formacao.remove(skill_to_edit)

            skill_to_edit["instituicao"] = self.get_argument("formacao_instituicao","")
            if skill_to_edit["instituicao"] == "":
                msg += u"O campo Instituição deve ser preenchido.<br/>"
            skill_to_edit["curso"] = self.get_argument("formacao_curso","")
            skill_to_edit["nivel"] = self.get_argument("formacao_nivel","")                
                
            data_ini =  self.get_argument("formacao_data_ini_ano","")+self.get_argument("formacao_data_ini_mes","")
            skill_to_edit["data_ini"] = data_ini[4:6]+"/"+data_ini[0:4]
            formacao_concluida = self.get_argument("formacao_check_andamento", "")
            if formacao_concluida == "on":
                data_fim =  self.get_argument("formacao_data_fim_ano","")+self.get_argument("formacao_data_fim_mes","")
            else:
                data_fim =  ""
            if data_fim:
                skill_to_edit["data_fim"] = data_fim[4:6]+"/"+data_fim[0:4]
            else:
                skill_to_edit["data_fim"] = ""
            if data_ini > data_fim and formacao_concluida == "on":
                msg += u"A data de início não pode ser posterior à data de término.<br/>"        
                
            skill_to_edit["descricao"] = self.get_argument("formacao_descricao","")
            if skill_to_edit["descricao"] == "":
                msg += u"O campo Descrição deve ser preenchido.<br/>" 
                
            lista_habilidades = []
            lista_habilidades = splitTags(self.get_argument("formacao_habilidades",""))
            if len(lista_habilidades) == 0:
                msg += u"O campo Habilidades deve ser preenchido.<br/>" 
            else:
                ###Se o usuário removeu uma habilidade da lista de habilidades###
                for item in skill_to_edit["habilidades"]:
                    if item not in lista_habilidades: #Se o usuario removeu uma habilidade desta formação
                        habilidade_existente = False #Booleano para identificar se a habilidade já existe no banco deste usuário
                        for habil in self._skill.habilidades: #Verifica se a habilidade removida está na lista habilidades
                            if habil["nome_habilidade"] == item:
                                if len(habil["academico_referencia"]) == 1:
                                    habil["academico_referencia"] = []
                                else:
                                    habil["academico_referencia"].remove(skill_id)
                                habilidade_existente = True
                                break
                        if not habilidade_existente: #Se não encontrou em habilidades, procurar em habilidades_pendentes
                            for habil in self._skill.habilidades_pendentes:
                                if habil["nome_habilidade"] == item:
                                    if len(habil["academico_referencia"]) == 1:
                                        habil["academico_referencia"] = []
                                    else:
                                        habil["academico_referencia"].remove(skill_id)
                                    habilidade_existente = True
                                    break
                        if not habilidade_existente: #Se não encontrou em habilidades_pendentes, procurar em habilidades_recusadas
                            for habil in self._skill.habilidades_recusadas:
                                if habil["nome_habilidade"] == item:
                                    if len(habil["academico_referencia"]) == 1:
                                        habil["academico_referencia"] = []
                                    else:
                                        habil["academico_referencia"].remove(skill_id)
                                    habilidade_existente = True
                                    break
                        if not habilidade_existente: #Se não encontrou em habilidades_recusadas, procurar em habilidades_invalidas
                            for habil in self._skill.habilidades_invalidas:
                                if habil["nome_habilidade"] == item:
                                    if len(habil["academico_referencia"]) == 1:
                                        habil["academico_referencia"] = []
                                    else:
                                        habil["academico_referencia"].remove(skill_id)
                                    habilidade_existente = True
                                    break
                                
                        if len(skill_to_edit["habilidades"]) == 1:
                            skill_to_edit["habilidades"] = []
                        else:        
                            skill_to_edit["habilidades"].remove(item)
                
                ###Se usuário adicionou uma nova habilidade à lista de habilidades###
                dict_habil = dict() #Dicionário para servir de base caso a habilidade não seja encontrada no banco deste usuário
                for habil in lista_habilidades: #Para cada habilidade fornecida pelo usuário
                    if habil not in skill_to_edit["habilidades"]: #Se habil não está na lista ORIGINAL de habilidades fornecidas pelo usuário, é uma nova habilidade
                        habilidade_existente = False #Booleano para identificar se a habilidade já existe no banco deste usuário
                        for item in self._skill.habilidades: #Verificar se já está na lista de habilidades do usuário
                            if item["nome_habilidade"] == habil:
                                habilidade_existente = True
                                item["academico_referencia"].append(skill_id)
                                break
                        if not habilidade_existente: #Se ainda não achou, continue procurando
                            for item in self._skill.habilidades_pendentes: #Verificar se já está na lista de habilidades_pendentes do usuário
                                if item["nome_habilidade"] == habil:
                                    habilidade_existente = True
                                    item["academico_referencia"].append(skill_id)
                                    break
                        if not habilidade_existente: #Se ainda não achou, continue procurando
                            for item in self._skill.habilidades_recusadas: #Verificar se já está na lista de habilidades_recusadas do usuário
                                if item["nome_habilidade"] == habil:
                                    habilidade_existente = True
                                    item["academico_referencia"].append(skill_id)
                                    break
                        if not habilidade_existente: #Se ainda não achou, continue procurando
                            for item in self._skill.habilidades_invalidas: #Verificar se já está na lista de habilidades_invalidas do usuário
                                if item["nome_habilidade"] == habil:
                                    habilidade_existente = True
                                    item["academico_referencia"].append(skill_id)
                                    break
                        if not habilidade_existente: #Se não achou em nenhuma lista, é uma nova habilidade_pendente
                            dict_habil["nome_habilidade"] = habil
                            dict_habil["usuarios_referencia"] = []
                            dict_habil["producoes_referencia"] = []
                            dict_habil["academico_referencia"] = [skill_id]
                            dict_habil["profissional_referencia"] = []
                            dict_habil["nivel_habilidade"] = ""
                            (temp, id_habilidade) = model.Skill.checkUserSkill(user, "skills")
                            dict_habil["id_habilidade"] = id_habilidade
                            
                            self._skill.habilidades.append(dict_habil)
                            dict_habil = {}
                        skill_to_edit["habilidades"].append(habil)
    
                     
            skill_to_edit["habilidades"].sort()
            self._skill.formacao.append(skill_to_edit)
            self._skill.formacao = sorted(self._skill.formacao, key=lambda k: int(k['id_formacao'])) 
        
        elif tipo == "professional":
            skill_to_edit = model.Skill().get_skillToEdit(user, tipo, skill_id)
            self._skill.experiencias.remove(skill_to_edit)
            
            skill_to_edit["empresa"] = self.get_argument("experiencias_empresa","")
            if skill_to_edit["empresa"] == "":
                msg += u"O campo Empresa/Projeto deve ser preenchido.<br/>"
            skill_to_edit["cargo"] = self.get_argument("experiencias_cargo","")
            data_ini =  self.get_argument("experiencias_data_ini_ano","")+self.get_argument("experiencias_data_ini_mes","")
            skill_to_edit["data_ini"] = data_ini[4:6]+"/"+data_ini[0:4]
            experiencia_concluida = self.get_argument("experiencias_check_andamento", "")
            if experiencia_concluida != "on":
                data_fim =  self.get_argument("experiencias_data_fim_ano","")+self.get_argument("experiencias_data_fim_mes","")
            else:
                data_fim =  ""
            if data_fim:
                skill_to_edit["data_fim"] = data_fim[4:6]+"/"+data_fim[0:4]
            else:
                skill_to_edit["data_fim"] = ""
            if data_ini > data_fim and experiencia_concluida != "on":
                msg += u"A data de início não pode ser posterior à data de término.<br/>" 
            skill_to_edit["descricao"] = self.get_argument("experiencias_descricao","")
            if skill_to_edit["descricao"] == "":
                msg += u"O campo Descrição deve ser preenchido.<br/>" 
           
            lista_habilidades = []
            lista_habilidades = splitTags(self.get_argument("experiencias_habilidades",""))
            if len(lista_habilidades) == 0:
                msg += u"O campo Habilidades deve ser preenchido.<br/>" 
            else:
                ###Se o usuário removeu uma habilidade da lista de habilidades###
                for item in skill_to_edit["habilidades"]:
                    if item not in lista_habilidades: #Se o usuario removeu uma habilidade desta experiência profissional
                        habilidade_existente = False #Booleano para identificar se a habilidade já existe no banco deste usuário
                        for habil in self._skill.habilidades: #Verifica se a habilidade removida está na lista habilidades
                            if habil["nome_habilidade"] == item:
                                if len(habil["profissional_referencia"]) == 1:
                                    habil["profissional_referencia"] = []
                                else:
                                    habil["profissional_referencia"].remove(skill_id)
                                habilidade_existente = True
                                break
                        if not habilidade_existente: #Se não encontrou em habilidades, procurar em habilidades_pendentes
                            for habil in self._skill.habilidades_pendentes:
                                if habil["nome_habilidade"] == item:
                                    if len(habil["profissional_referencia"]) == 1:
                                        habil["profissional_referencia"] = []
                                    else:
                                        habil["profissional_referencia"].remove(skill_id)
                                    habilidade_existente = True
                                    break
                        if not habilidade_existente: #Se não encontrou em habilidades_pendentes, procurar em habilidades_recusadas
                            for habil in self._skill.habilidades_recusadas:
                                if habil["nome_habilidade"] == item:
                                    if len(habil["profissional_referencia"]) == 1:
                                        habil["profissional_referencia"] = []
                                    else:
                                        habil["profissional_referencia"].remove(skill_id)
                                    habilidade_existente = True
                                    break
                        if not habilidade_existente: #Se não encontrou em habilidades_recusadas, procurar em habilidades_invalidas
                            for habil in self._skill.habilidades_invalidas:
                                if habil["nome_habilidade"] == item:
                                    if len(habil["profissional_referencia"]) == 1:
                                        habil["profissional_referencia"] = []
                                    else:
                                        habil["profissional_referencia"].remove(skill_id)
                                    habilidade_existente = True
                                    break
                                
                        if len(skill_to_edit["habilidades"]) == 1:
                            skill_to_edit["habilidades"] = []
                        else:        
                            skill_to_edit["habilidades"].remove(item)
                
                ###Se usuário adicionou uma nova habilidade à lista de habilidades###
                dict_habil = dict() #Dicionário para servir de base caso a habilidade não seja encontrada no banco deste usuário
                for habil in lista_habilidades: #Para cada habilidade fornecida pelo usuário
                    if habil not in skill_to_edit["habilidades"]: #Se habil não está na lista ORIGINAL de habilidades fornecidas pelo usuário, é uma nova habilidade
                        habilidade_existente = False #Booleano para identificar se a habilidade já existe no banco deste usuário
                        for item in self._skill.habilidades: #Verificar se já está na lista de habilidades do usuário
                            if item["nome_habilidade"] == habil:
                                habilidade_existente = True
                                item["profissional_referencia"].append(skill_id)
                                break
                        if not habilidade_existente: #Se ainda não achou, continue procurando
                            for item in self._skill.habilidades_pendentes: #Verificar se já está na lista de habilidades_pendentes do usuário
                                if item["nome_habilidade"] == habil:
                                    habilidade_existente = True
                                    item["profissional_referencia"].append(skill_id)
                                    break
                        if not habilidade_existente: #Se ainda não achou, continue procurando
                            for item in self._skill.habilidades_recusadas: #Verificar se já está na lista de habilidades_recusadas do usuário
                                if item["nome_habilidade"] == habil:
                                    habilidade_existente = True
                                    item["profissional_referencia"].append(skill_id)
                                    break
                        if not habilidade_existente: #Se ainda não achou, continue procurando
                            for item in self._skill.habilidades_invalidas: #Verificar se já está na lista de habilidades_invalidas do usuário
                                if item["nome_habilidade"] == habil:
                                    habilidade_existente = True
                                    item["profissional_referencia"].append(skill_id)
                                    break
                        if not habilidade_existente: #Se não achou em nenhuma lista, é uma nova habilidade_pendente
                            dict_habil["nome_habilidade"] = habil
                            dict_habil["usuarios_referencia"] = []
                            dict_habil["producoes_referencia"] = []
                            dict_habil["academico_referencia"] = []
                            dict_habil["profissional_referencia"] = [skill_id]
                            dict_habil["nivel_habilidade"] = ""
                            (temp, id_habilidade) = model.Skill.checkUserSkill(user, "skills")
                            dict_habil["id_habilidade"] = id_habilidade
                            
                            self._skill.habilidades.append(dict_habil)
                            dict_habil = {}
                        skill_to_edit["habilidades"].append(habil)
    
                     
            skill_to_edit["habilidades"].sort()
            self._skill.experiencias.append(skill_to_edit)
            self._skill.experiencias = sorted(self._skill.experiencias, key=lambda k: int(k['id_experiencias']))
            
        elif tipo == "skills":
            erro = 0
            nivel = self.get_argument("nivel","")
            #nome = self.get_argument("nome","")
            nome = unicode(self.request.body.split("&nome=")[1],'utf-8')
            #OBS: Foi utilizada a forma de pegar o argumento nome acima para contornar o problema causado se o usuário digitar um argumento com um +
            #Este problema acarretava no descarte dos caracteres a partir do +
            if nome != "" and nivel != "":
                for habil in self._skill.habilidades:
                    if nome == habil["nome_habilidade"]:
                        habil["nivel_habilidade"] = nivel
            else:
                erro = 1
        
        if msg:
            self.render("popup_msg.html", MSG=msg, REGISTRY_ID=user)
            return
        
        self._skill.save(id=user)
        
        if tipo == "academic":
            self.render("popup_msg.html", MSG="Formação editada com sucesso!", REGISTRY_ID=user)
            return
        elif tipo == "professional":
            self.render("popup_msg.html", MSG="Experiência profissional editada com sucesso!", REGISTRY_ID=user)
            return
        elif tipo == "skills":
            if erro == 0:
                self.write("success")
                self.finish()


class DeleteSkillHandler(BaseHandler):
    ''' Exclusão de uma experiencia ou habilidade'''

    @tornado.web.authenticated
    def get(self, tipo, skill_id):
        user = self.get_current_user()

        self._skill = model.Skill().retrieve(user)
        if self._skill:                    
            #tratar usuario mexendo na url
            (item_to_remove, remove_document) = model.Skill.removeSkill(user, skill_id, tipo)
            
            if remove_document:
                self._skill.delete()
            else:
                if tipo == "academic":
                    self._skill.formacao.remove(item_to_remove)
                    for habil in self._skill.habilidades:
                        for item in habil["academico_referencia"]:
                            if item == skill_id:
                                if len(habil["academico_referencia"]) == 1:
                                    habil["academico_referencia"] = []
                                else:
                                    habil["academico_referencia"].remove(item)
                                break
                                
                elif tipo == "professional":
                    self._skill.experiencias.remove(item_to_remove)
                    for habil in self._skill.habilidades:
                        for item in habil["profissional_referencia"]:
                            if item == skill_id:
                                if len(habil["profissional_referencia"]) == 1:
                                    habil["profissional_referencia"] = []
                                else:
                                    habil["profissional_referencia"].remove(item)
                                break
                elif tipo == "skills":
                    self._skill.habilidades.remove(item_to_remove)
                    for form in self._skill.formacao:
                        for item in form["habilidades"]:
                            if item == item_to_remove["nome_habilidade"]:
                                if len(form["habilidades"]) == 1:
                                    form["habilidades"] = []
                                else:
                                    form["habilidades"].remove(item)
                                break
                    for exp in self._skill.experiencias:
                        for item in exp["habilidades"]:
                            if item == item_to_remove["nome_habilidade"]:
                                if len(exp["habilidades"]) == 1:
                                    exp["habilidades"] = []
                                else:
                                    exp["habilidades"].remove(item)
                                break
                        
                self._skill.save(id=user)
            
            if tipo != "skills":    
                self.redirect("/profile/skills/new/experience")
            else:
                self.redirect("/profile/skills/"+user)

class SkillHandler(BaseHandler):
    ''' Lista habilidades e habilidades pendentes do usuário '''
    
    @tornado.web.authenticated
    def get(self, registry_id):
        user = self.get_current_user()
        if user != registry_id:
            self.render("home.html", MSG=u"Você não tem permissão para ver esta página.", REGISTRY_ID=user, \
                                NOMEPAG="Tarefas")     
        else:
            tabs = []
            tabs.append(("Editar Perfil", "/profile/edit"))
            tabs.append(("Alterar Senha", "/profile/changepasswd"))
            tabs.append(("Formação e Experiências", "/profile/skills/new/experience"))
            tabs.append(("Produção Acadêmica - Lattes", "/profile/skills/productions"))
            tabs.append(("Habilidades", ""))
            
            (habilidades, habilidades_pendentes, habilidades_recusadas, habilidades_sem_nivel) = model.Skill.getSkill(user, "skills_pending_refused")

            self.render("modules/skills/profile-edit-skill.html", REGISTRY_ID=user, MSG="", \
                            HABILIDADES=habilidades, HABILIDADES_PENDENTES=habilidades_pendentes, HABILIDADES_RECUSADAS=habilidades_recusadas, \
                            HABILIDADES_SEM_NIVEL=habilidades_sem_nivel, TABS=tabs, NOMEPAG="perfil", \
                            AUTOCOMPLETE_ALL_SKILLS=core.model.getAutocompleteAllSkills())
        

class AddSkillHandler(BaseHandler):
    ''' Adicionar habilidade de um usuário '''
        
    @tornado.web.authenticated
    def post(self):
        user = self.get_current_user()
        producoes_referencia = []
        usuarios_referencia = []
        academico_referencia = []
        profissional_referencia = []
        encontrado = False

        msg = ""
        
        (ja_existente, skill_id) = model.Skill.checkUserSkill(user, "skills")

        if(ja_existente): #Checa se o usuário já informou alguma experiência
            self._skill = model.Skill().retrieve(user)
            
        else:   
            self._skill = model.Skill()
            self._skill.owner = user
        
        habilidades = dict()
        habilidades["id_habilidade"] = skill_id
        habilidades["nome_habilidade"] = model.strip_tags(self.get_argument("nome_habilidade_nova","").lower())
        if habilidades["nome_habilidade"] == "":
            msg += u"O campo Habilidade deve ser preenchido.<br/>"
            
        for item in self._skill.habilidades: #Procurando se a habilidade entrada já está presente na lista de habilidades do usuário.
            if item["nome_habilidade"] == habilidades["nome_habilidade"]:
                msg += u"A habilidade escolhida já consta em sua lista de habilidades."
                break
                encontrado = True
        
        habilidades["producoes_referencia"] = []
        habilidades["usuarios_referencia"] = []
        habilidades["academico_referencia"] = []
        habilidades["profissional_referencia"] = []
        
        if not encontrado and ja_existente:#Se não está nas habilidades, procura na lista de habilidades pendentes também.
            for item in self._skill.habilidades_pendentes:
                if item["nome_habilidade"] == habilidades["nome_habilidade"]:
                    producoes_referencia = item["producoes_referencia"]
                    usuarios_referencia = item["usuarios_referencia"]
                    academico_referencia = item["academico_referencia"]
                    profissional_referencia = item["profissional_referencia"]
                    if len(self._skill.habilidades_pendentes) == 1:
                        self._skill.habilidades_pendentes = []
                    else:
                        self._skill.habilidades_pendentes.remove(item)
                    habilidades["producoes_referencia"] = producoes_referencia
                    habilidades["usuarios_referencia"] = usuarios_referencia
                    habilidades["academico_referencia"] = academico_referencia
                    habilidades["profissional_referencia"] = profissional_referencia
                    encontrado = True
                    break

        
        if not encontrado and ja_existente:#Se não está nas habilidades nem nas habilidades_pendentes, procura na lista de habilidades recusadas também.
            for item in self._skill.habilidades_recusadas:
                if item["nome_habilidade"] == habilidades["nome_habilidade"]:
                    producoes_referencia = item["producoes_referencia"]
                    usuarios_referencia = item["usuarios_referencia"]
                    academico_referencia = item["academico_referencia"]
                    profissional_referencia = item["profissional_referencia"]
                    if len(self._skill.habilidades_recusadas) == 1:
                        self._skill.habilidades_recusadas = []
                    else:
                        self._skill.habilidades_recusadas.remove(item)
                    habilidades["producoes_referencia"] = producoes_referencia
                    habilidades["usuarios_referencia"] = usuarios_referencia
                    habilidades["academico_referencia"] = academico_referencia
                    habilidades["profissional_referencia"] = profissional_referencia
                    encontrado = True
                    break
    
        if not encontrado and ja_existente:#Se ainda sim não foi encontrado, testa também nas habilidades_inválidas
            for item in self._skill.habilidades_invalidas:
                if item["nome_habilidade"] == habilidades["nome_habilidade"]:
                    producoes_referencia = item["producoes_referencia"]
                    usuarios_referencia = item["usuarios_referencia"]
                    academico_referencia = item["academico_referencia"]
                    profissional_referencia = item["profissional_referencia"]
                    if len(self._skill.habilidades_invalidas) == 1:
                        self._skill.habilidades_invalidas = []
                    else:
                        self._skill.habilidades_invalidas.remove(item)
                    habilidades["producoes_referencia"] = producoes_referencia
                    habilidades["usuarios_referencia"] = usuarios_referencia
                    habilidades["academico_referencia"] = academico_referencia
                    habilidades["profissional_referencia"] = profissional_referencia
                    encontrado = True
                    break
                
        habilidades["nivel_habilidade"] = self.get_argument("nivel_habilidade_nova","")
        
        self._skill.habilidades.append(habilidades)
        
        if msg:
            self.render("home.html", MSG=msg, REGISTRY_ID=user, NOMEPAG="perfil")
            return
        
        self._skill.save(id=user)

        self.redirect("/profile/skills/"+user)
        
class SkillLevelPopupHandler(BaseHandler):
    ''' Exibe o Popup de seleção de nível para as habilidades oriundas dos formulários de Formação e Experiências '''

    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        
        habilidades_sem_nivel = model.Skill().getSkill(user, "skills_sem_nivel")
        
        self.render("modules/skills/profile-popup-select-skill-level.html", NOMEPAG="perfil", \
                    SKILLDATA=habilidades_sem_nivel, REGISTRY_ID=user, MSG="")
        
        
class RefusedSkillHandler(BaseHandler):
    ''' Lista produções e Upload do XML do Lattes de um usuário '''
    
    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        
        habilidades_recusadas = model.Skill.getSkill(user, "refused")
        
        self.render("modules/skills/profile-popup-rejected-skills.html", REGISTRY_ID=user, MSG="", \
                        HABILIDADES_RECUSADAS=habilidades_recusadas, NOMEPAG="perfil")
        
    @tornado.web.authenticated
    def post(self):
        user = self.get_current_user()
        producoes_old = []
        habilidades = []
        habilidades_pendentes = []
        habilidades_recusadas = []
        msg = ""
        
        try:
            file = self.request.files["arquivo"][0]
        except:
            msg = "Por favor escolha o arquivo correto."
            self.render("home.html", MSG=msg, REGISTRY_ID=user, NOMEPAG="perfil")
            return
        if (file["content_type"] != "text/xml"):
            msg = "Arquivo inválido. Por favor escolha o arquivo correto."
        
        #Temp é apenas usada para que o retorno da função seja atendido
        (ja_existente, temp) = model.Skill.checkUserSkill(user, "productions")
        
        if(ja_existente): #Checa se o usuário já informou alguma experiência
            self._skill = model.Skill().retrieve(user)
            if "_attachments" in self._skill:
                if not (model.Skill.checkLastLattesUpdate(user, file["body"])):
                    msg = u"O arquivo XML que você escolheu é mais antigo que o presente no banco de dados do ActivUFRJ.</br>"\
                        +"Se realmente desejar substituir o arquivo, por favor remova o antigo, e então envie o novo."
            (producoes_old, habilidades, habilidades_pendentes, habilidades_recusadas) = model.Skill.getProductionDataAll(user)
        else:   
            self._skill = model.Skill()
            self._skill.owner = user
        
        if msg:
            self.render("home.html", MSG=msg, REGISTRY_ID=user, NOMEPAG="perfil")
            return
        
        (producoes, habilidades, habilidades_pendentes, header, erro) = model.Skill.getProductionsFromXML(user, file["body"], \
                                                                                        producoes_old, habilidades, habilidades_pendentes, habilidades_recusadas)
        
        
        self._skill.cabecalho_lattes = header
        self._skill.producoes = producoes
        self._skill.habilidades = habilidades
        self._skill.habilidades_pendentes = habilidades_pendentes
        
        self._skill.save(id=user)
        self._skill.saveFile(user, file)

        if erro == 1:
            msg = "Arquivo inválido. Por favor escolha o arquivo curriculo.xml correto."
        
        self.redirect("/profile/skills/productions")
               
class ProductionHandler(BaseHandler):
    ''' Lista produções e Upload do XML do Lattes de um usuário '''
    
    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        
        tabs = []
        tabs.append(("Editar Perfil", "/profile/edit"))
        tabs.append(("Alterar Senha", "/profile/changepasswd"))
        tabs.append(("Formação e Experiências", "/profile/skills/new/experience"))
        tabs.append(("Produção Acadêmica - Lattes", ""))
        tabs.append(("Habilidades", "/profile/skills/"+user))
        
        (producoes, habilidades_pendentes, file_data) = model.Skill.getProductionData(user, includeFileData=True)
        habilidades_no_xml = model.Skill.checkProductionSkills(producoes, file_data)
        
        self.render("modules/skills/profile-edit-productions.html", REGISTRY_ID=user, MSG="", \
                        PRODUCOES=producoes, HABILIDADES_PENDENTES=habilidades_pendentes, FILE_DATA=file_data, \
                        HABILIDADES_NO_XML=habilidades_no_xml, TABS=tabs, NOMEPAG="perfil", \
                            AUTOCOMPLETE_ALL_SKILLS=core.model.getAutocompleteAllSkills())
        
    @tornado.web.authenticated
    def post(self):
        user = self.get_current_user()
        producoes_old = []
        habilidades = []
        habilidades_pendentes = []
        habilidades_recusadas = []
        msg = ""
        
        try:
            file = self.request.files["arquivo"][0]
        except:
            msg = "Por favor escolha o arquivo correto."
            self.render("home.html", MSG=msg, REGISTRY_ID=user, NOMEPAG="perfil")
            return
        if (file["content_type"] != "text/xml"):
            msg = "Arquivo inválido. Por favor escolha o arquivo correto."
        
        #Temp é apenas usada para que o retorno da função seja atendido
        (ja_existente, temp) = model.Skill.checkUserSkill(user, "productions")
        
        if(ja_existente): #Checa se o usuário já informou alguma experiência
            self._skill = model.Skill().retrieve(user)
            if "_attachments" in self._skill:
                if not (model.Skill.checkLastLattesUpdate(user, file["body"])):
                    msg = u"O arquivo XML que você escolheu é mais antigo que o presente no banco de dados do ActivUFRJ.</br>"\
                        +"Se realmente desejar substituir o arquivo, por favor remova o antigo, e então envie o novo."
            (producoes_old, habilidades, habilidades_pendentes, habilidades_recusadas) = model.Skill.getProductionDataAll(user)
        else:   
            self._skill = model.Skill()
            self._skill.owner = user
        
        if msg:
            self.render("home.html", MSG=msg, REGISTRY_ID=user, NOMEPAG="perfil")
            return
        
        (producoes, habilidades, habilidades_pendentes, header, erro) = model.Skill.getProductionsFromXML(user, file["body"], \
                                                                                        producoes_old, habilidades, habilidades_pendentes, habilidades_recusadas)
        
        
        self._skill.cabecalho_lattes = header
        self._skill.producoes = producoes
        self._skill.habilidades = habilidades
        self._skill.habilidades_pendentes = habilidades_pendentes
        
        self._skill.save(id=user)
        self._skill.saveFile(user, file)

        if erro == 1:
            msg = "Arquivo inválido. Por favor escolha o arquivo curriculo.xml correto."
        else:
            log.model.log(user, u'enviou seu curriculo Lattes', objeto="", tipo="skills")
        self.redirect("/profile/skills/productions")

class EditProductionHandler(BaseHandler):
    ''' Mais detalhes e adição de referências à uma produção'''

    @tornado.web.authenticated
    def get(self, production_id):
        user = self.get_current_user()

        producao = model.Skill().getProduction(user, production_id)

        self.render("modules/skills/profile-popup-edit-productions.html", NOMEPAG="perfil", \
                        PRODUCAO=producao, REGISTRY_ID=user, MSG="")
        


class PointUserHandler(BaseHandler):
    ''' Gerencia um usuário apontando outro como co-autor de sua produção. '''
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self, production_id, autor_id):
        user = self.get_current_user()
        
        username = self.get_argument("username","")
        
        if username == "":
            return
    
        if not isAUser(username):
            self.write("usuario invalido")
            self.finish()
            return
        
        #Temp é usada apenas para atender ao retorno da função
        (producoes, temp) = model.Skill.getProductionData(user)
        
        for item in producoes:
            if item["SEQUENCIA-PRODUCAO"] == production_id:
                item["AUTORES"][int(autor_id)]["USERNAME-ACTIV"] = username
                
        self._skill = model.Skill().retrieve(user)
        self._skill.producoes = producoes
        self._skill.save(id=user)
        
        self.write(username)
        self.finish()
 
class DeleteXmlHandler(BaseHandler):
    ''' Remove do banco o arquivo XML do usuário'''

    @tornado.web.authenticated
    def get(self, filename):
        user = self.get_current_user()

        self._skill = model.Skill().retrieve(user)
        if self._skill:  
            self._skill.deleteAttachment(filename)
               
        self.redirect("/profile/skills/productions")
        
class ReferencesPopupHandler(BaseHandler):
    ''' Lista de referências de uma habilidade pendente'''

    @tornado.web.authenticated
    def get(self, tipo, user, skill_id):
        (nome_habilidade, producoes_referencia, numero_usuarios, academico_referencia, profissional_referencia) = model.Skill().getSkillReferences(user, tipo, skill_id)
        
        self.render("modules/skills/profile-popup-production-references.html", NOMEPAG="perfil", \
                    PRODUCOES_REFERENCIA=producoes_referencia, NUM_USUARIOS=numero_usuarios, ACADEMICO_REFERENCIA=academico_referencia, \
                    PROFISSIONAL_REFERENCIA=profissional_referencia, NOME_HABILIDADE=nome_habilidade, USER=user,\
                    REGISTRY_ID=user, MSG="")
            
             
class ValidateUserPendingSkills(BaseHandler):
    ''' Gerencia lista de habilidades_pendentes, distribuindo itens entre habilidades, habilidades_recusadas e habilidades_invalidas. '''
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        user = self.get_current_user()
        nome_habilidade = model.strip_tags(self.get_argument("nome","").lower())
        nivel_habilidade = self.get_argument("nivel","")
        tipo = self.get_argument("tipo","")
        producoes_referencia = []
        usuarios_referencia = []
        academico_referencia = []
        profissional_referencia = []
        
        if nome_habilidade == "":
            return
        
        (habilidades, habilidades_pendentes, habilidades_recusadas, habilidades_invalidas) = model.Skill.getSkill(user, "skills_pending_refused_invalid")
        
        for item in habilidades_pendentes:
            if item["nome_habilidade"] == nome_habilidade:
                producoes_referencia = item["producoes_referencia"]
                usuarios_referencia = item["usuarios_referencia"]
                academico_referencia = item["academico_referencia"]
                profissional_referencia = item["profissional_referencia"]
                if (tipo == "recusar") and (item not in habilidades_recusadas):
                    habilidades_recusadas.append(item)
                if (tipo == "invalidar") and (item not in habilidades_invalidas):
                    habilidades_invalidas.append(item)
                if len(habilidades_pendentes) == 1:
                    habilidades_pendentes = []
                else:
                    habilidades_pendentes.remove(item)
                break
        
        if tipo == "confirmar":
            dict_habilidades = dict()
            dict_habilidades["nome_habilidade"] = nome_habilidade
            dict_habilidades["nivel_habilidade"] = nivel_habilidade
            dict_habilidades["producoes_referencia"] = producoes_referencia
            dict_habilidades["usuarios_referencia"] = usuarios_referencia
            dict_habilidades["academico_referencia"] = academico_referencia
            dict_habilidades["profissional_referencia"] = profissional_referencia
            
            if habilidades:
                dict_habilidades["id_habilidade"] = str(int(habilidades[-1]["id_habilidade"])+1)
            else:
                dict_habilidades["id_habilidade"] = "0"
            
            habilidades.append(dict_habilidades)
                    
            
        self._skill = model.Skill().retrieve(user)
        self._skill.habilidades = habilidades
        self._skill.habilidades_pendentes = habilidades_pendentes
        self._skill.habilidades_recusadas = habilidades_recusadas
        self._skill.habilidades_invalidas = habilidades_invalidas
        self._skill.save(id=user)
        
        if len(habilidades_pendentes) == 0:
            self.write("final success")
        else:
            self.write("success")
        self.finish()
        
class ValidateUserRefusedSkills(BaseHandler):
    ''' Gerencia lista de habilidades_recusadas, distribuindo itens entre habilidades e habilidades_invalidas. '''
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self, user, skill_id):
        tipo = "refused"
        referencias = "Habilidade detectada nas seguintes produções:"
        (nome_habilidade, producoes_referencia, numero_usuarios, academico_referencia, profissional_referencia) = model.Skill().getSkillReferences(user, tipo, skill_id)
        dict_resposta = dict()
        dict_resposta["producoes_referencia"] = producoes_referencia
        dict_resposta["num_usuarios"] = numero_usuarios
        dict_resposta["academico_referencia"] = academico_referencia
        dict_resposta["profissional_referencia"] = profissional_referencia
        
        self.write(dict_resposta)
        self.finish()
        
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        user = self.get_current_user()
        nome_habilidade = model.strip_tags(self.get_argument("nome","").lower())
        nivel_habilidade = self.get_argument("nivel","")
        tipo = self.get_argument("tipo","")
        producoes_referencia = []
        usuarios_referencia = []
        academico_referencia = []
        profissional_referencia = []
        
        if nome_habilidade == "":
            return
        
        (habilidades, habilidades_recusadas, habilidades_invalidas) = model.Skill.getSkill(user, "skills_refused_invalid")
        
        for item in habilidades_recusadas:
            if item["nome_habilidade"] == nome_habilidade:
                producoes_referencia = item["producoes_referencia"]
                usuarios_referencia = item["usuarios_referencia"]
                academico_referencia = item["academico_referencia"]
                profissional_referencia = item["profissional_referencia"]
                if (tipo == "invalidar") and (item not in habilidades_invalidas):
                    habilidades_invalidas.append(item)
                if len(habilidades_recusadas) == 1:
                    habilidades_recusadas = []
                else:
                    habilidades_recusadas.remove(item)
                break
        
        if tipo == "confirmar":
            dict_habilidades = dict()
            dict_habilidades["nome_habilidade"] = nome_habilidade
            dict_habilidades["nivel_habilidade"] = nivel_habilidade
            dict_habilidades["producoes_referencia"] = producoes_referencia
            dict_habilidades["usuarios_referencia"] = usuarios_referencia
            dict_habilidades["academico_referencia"] = academico_referencia
            dict_habilidades["profissional_referencia"] = profissional_referencia
            
            if habilidades:
                dict_habilidades["id_habilidade"] = str(int(habilidades[-1]["id_habilidade"])+1)
            else:
                dict_habilidades["id_habilidade"] = "0"
            
            habilidades.append(dict_habilidades)
                    
            
        self._skill = model.Skill().retrieve(user)
        self._skill.habilidades = habilidades
        self._skill.habilidades_recusadas = habilidades_recusadas
        self._skill.habilidades_invalidas = habilidades_invalidas
        self._skill.save(id=user)

        if len(habilidades_recusadas) == 0:
            self.write("final success")
        else:
            self.write("success")
        self.finish()
        
class ValidateUserSkills(BaseHandler):
    ''' Trata a validação social das skills no perfil do usuário '''
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        user = self.get_current_user() #Usuário que faz a validação
        nome_habilidade = model.strip_tags(self.get_argument("nome_habilidade","").lower())
        nivel_habilidade = self.get_argument("nivel","")
        target = self.get_argument("target","") #Usuário alvo validação
        erro = 0 
        encontrado = False #Marca se a habilidade a ser inserida já foi encontrada em alguma das listas de habilidades. Ver abaixo.
        ja_validou = False #Marca se o usuário já validou a habilidade em questão para este target 
        dict_habil = dict()
        dict_habil["nome"] = user
        dict_habil["nivel"] = nivel_habilidade
        
        (habilidades, habilidades_pendentes, habilidades_recusadas, habilidades_invalidas) = model.Skill.getSkill(target, "skills_pending_refused_invalid")
        
        if nome_habilidade == "":
            erro = 1
        
        nome_habilidade = model.strip_tags(nome_habilidade)         
        
        for habil in habilidades:#Procurando habilidade sugerida na lista de habilidades já existentes do target
            if habil["nome_habilidade"] == nome_habilidade:
                for usuario in habil["usuarios_referencia"]:#Verificando se user já validou esta habilidade antes
                    if user == usuario["nome"]:#Se sim, muda apenas o nível da habilidade na lista usuarios_referencia
                        ja_validou = True
                        usuario["nivel"] = nivel_habilidade
                        break
                if not ja_validou:#Se não, adiciona o user e o nível na lista usuarios_referencia
                    habil["usuarios_referencia"].append(dict_habil)
                encontrado = True
                break
            
        if not encontrado:
            for pend in habilidades_pendentes: #Se não encontrou na lista de habilidades, procura nas pendentes
                if pend["nome_habilidade"] == nome_habilidade:
                    for usuario in pend["usuarios_referencia"]:#Verificando se user já validou esta habilidade antes
                        if user == usuario["nome"]:#Se sim, muda apenas o nível da habilidade na lista usuarios_referencia
                            ja_validou = True
                            usuario["nivel"] = nivel_habilidade
                            break
                    if not ja_validou:#Se não, adiciona o user e o nível na lista usuarios_referencia
                        pend["usuarios_referencia"].append(dict_habil)
                    encontrado = True
                    break

        if not encontrado:
            for recusada in habilidades_recusadas: #Se não encontrou na lista de pendentes, procura nas recusadas
                if recusada["nome_habilidade"] == nome_habilidade:
                    for usuario in recusada["usuarios_referencia"]:#Verificando se user já validou esta habilidade antes
                        if user == usuario["nome"]:#Se sim, muda apenas o nível da habilidade na lista usuarios_referencia
                            ja_validou = True
                            usuario["nivel"] = nivel_habilidade
                            break
                    if not ja_validou:#Se não, adiciona o user e o nível na lista usuarios_referencia
                        recusada["usuarios_referencia"].append(dict_habil)
                    encontrado = True
                    break

        if not encontrado:
            for invalida in habilidades_invalidas: #Se não encontrou na lista de recusadas, procura nas invalidas
                if invalida["nome_habilidade"] == nome_habilidade:
                    for usuario in invalida["usuarios_referencia"]:#Verificando se user já validou esta habilidade antes
                        if user == usuario["nome"]:#Se sim, muda apenas o nível da habilidade na lista usuarios_referencia
                            ja_validou = True
                            usuario["nivel"] = nivel_habilidade
                            break
                    if not ja_validou:#Se não, adiciona o user e o nível na lista usuarios_referencia
                        invalida["usuarios_referencia"].append(dict_habil)
                    encontrado = True
                    break
                    
        if not encontrado: #Se ainda não encontrou, deve criar uma nova
            dict_pend = dict()
            dict_pend["usuarios_referencia"] = []
            dict_pend["usuarios_referencia"].append(dict_habil)
            dict_pend["producoes_referencia"] = []
            dict_pend["academico_referencia"] = []
            dict_pend["profissional_referencia"] = []
            dict_pend["nome_habilidade"] = nome_habilidade
            habilidades_pendentes.append(dict_pend)
            encontrado = True
            
            #notifica usuário que um amigo recomendou uma nova habilidade. 
            email_msg = u"Um de seus amigos recomendou a habilidade "+ nome_habilidade + \
            u" no seu perfil. Veja se você aceita esta recomendação!\n" + \
            Notify.assinatura(target, target, str(datetime.now()))+"\n\n"
                        
            Notify.email_notify(target, target, "Uma nova habilidade lhe foi recomendada!", \
                           message=email_msg, \
                           link="skills/new/skill",sendToMyself=True)
            
        if erro == 0:    
            ja_existente = model.Skill.checkUserSkill(target, "skills", False)
            
            if ja_existente:
                self._skill = model.Skill().retrieve(target)
                self._skill.habilidades = habilidades
                self._skill.habilidades_pendentes = habilidades_pendentes
                self._skill.habilidades_recusadas = habilidades_recusadas
                self._skill.habilidades_invalidas = habilidades_invalidas
                self._skill.save(id=target)
            else:
                self._skill = model.Skill()
                self._skill.owner = target
                self._skill.habilidades_pendentes = habilidades_pendentes
                self._skill.save(id=target)
            
            self.write("success")
            self.finish()
            
        elif erro == 1:
            self.write("error")
            self.finish()
            
class ReviewValidatedSkills(BaseHandler):
    ''' Dá ao usuário a opção de rever as sugestões de habilidades já feitas à outro usuário'''

    @tornado.web.authenticated
    def get(self, target):
        user = self.get_current_user()
        skills_to_review = model.Skill().getSkillsToReview(user, target)
        
        self.render("modules/skills/profile-popup-review-skills.html", NOMEPAG="perfil", \
                    REVIEWDATA=skills_to_review, TARGET=target, REGISTRY_ID=user, MSG="")

class SkillUserChartHandler(BaseHandler):
    ''' Gera o gráfico de habilidades de usuário(s)'''

    @tornado.web.authenticated
    def get(self, target):
        user = self.get_current_user()
        skilldata_user = []
        skilldata_target = []

        #Pegando lista de habilidades com seus respectivos níveis do usuário logado
        skilldata_user = model.Skill().calculaNivelHabilidade(user)
        skilldata_user.sort(key=lambda x: x['nivel_geral'], reverse=True)
        if user != target:#Se o usuário está visualizando o gráfico de outro
            #Pegando a lista de habilidades do outro usuário
            skilldata_target = model.Skill().calculaNivelHabilidade(target)
            skilldata_target.sort(key=lambda x: x['nivel_geral'], reverse=True)
            temp = []
            habils_em_comum = []
            #Montando uma lista apenas com os nomes das habilidades do alvo
            for item in skilldata_target:
                temp.append(item["nome_habilidade"])
            #Verificando habilidades em comum e salvando em habils_em_comum    
            for item in skilldata_user:
                if item["nome_habilidade"] in temp:
                    habils_em_comum.append(item)
            #Salvando as habilidades em comum em skilldata_user para envio ao template
            skilldata_user = habils_em_comum
        self.render("modules/skills/profile-skill-user-chart.html", NOMEPAG="perfil", \
                    SKILLDATA_USER=skilldata_user, SKILLDATA_TARGET=skilldata_target, \
                    MAX_HABILIDADES_GRAFICO=MAX_HABILIDADES_GRAFICO, MIN_HABILIDADES_GRAFICO=MIN_HABILIDADES_GRAFICO, REGISTRY_ID=target, MSG="")

class SkillCommunityChartHandler(BaseHandler):
    ''' Gera o gráfico de habilidades de usuário(s)'''

    @tornado.web.authenticated
    def get(self, registry_id):
        comu = core.model.Community().retrieve(registry_id)
        members = comu.getMembersList()[1]
        
        self.render("modules/skills/profile-skill-community-chart.html", NOMEPAG="perfil", \
                    MEMBERS=members, \
                    MAX_HABILIDADES_GRAFICO=MAX_HABILIDADES_GRAFICO, MIN_HABILIDADES_GRAFICO=MIN_HABILIDADES_GRAFICO, REGISTRY_ID=registry_id, MSG="")     
        
class SkillSearchHandler(BaseHandler):
    ''' Busca de usuários por habilidades '''
    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        str_busca = ""
        resultado_busca = []
        self.render("modules/skills/skill-search.html", NOMEPAG="Busca", \
                    STR_BUSCA=str_busca, RESULTADO_BUSCA = resultado_busca, REGISTRY_ID=user, MSG="")   
    @tornado.web.authenticated
    def post(self):
        user = self.get_current_user()
        str_busca = self.get_argument("campo_busca","")
        if not str_busca:
            str_busca = self.get_argument("str_busca","")
        resultado_busca = []
        filtros = []

        if str_busca != "":
            resultado_busca = model.Skill().buscaSkill(str_busca, filtros)
            
        self.render("modules/skills/skill-search.html", NOMEPAG="Busca", \
                    STR_BUSCA=str_busca, RESULTADO_BUSCA = resultado_busca, REGISTRY_ID=user, MSG="")    
            
URL_TO_PAGETITLE.update ({
        "skills": u"Habilidades"
        })

HANDLERS.extend([
                (r"/profile/skills/new/experience",                                                                 ExperienceHandler),
                (r"/profile/skills/new/experience/academic",                                                        AddAcademicExperienceHandler),
                (r"/profile/skills/delete/%s/%s"                   % (PAGENAMECHARS, PAGENAMECHARS),                DeleteSkillHandler),
                (r"/profile/skills/new/experience/professional",                                                    AddProfessionalExperienceHandler),
                (r"/profile/skills/edit/%s/%s"                     % (PAGENAMECHARS, PAGENAMECHARS),                EditSkillHandler),
                (r"/profile/skills/new/skill/add",                                                                  AddSkillHandler),
                (r"/profile/skills/new/skill/level",                                                                SkillLevelPopupHandler),
                (r"/profile/skills/new/skill/rejected",                                                             RefusedSkillHandler),
                (r"/profile/skills/productions",                                                                    ProductionHandler),
                (r"/profile/skills/productions/edit/%s"            % (PAGENAMECHARS),                               EditProductionHandler),
                (r"/profile/skills/productions/edit/%s/%s"         % (PAGENAMECHARS, PAGENAMECHARS),                PointUserHandler),
                (r"/profile/skills/productions/delete/%s"          % (PAGENAMECHARS),                               DeleteXmlHandler),
                (r"/profile/skills/productions/references/%s/%s/%s"% (PAGENAMECHARS, PAGENAMECHARS,PAGENAMECHARS),  ReferencesPopupHandler),
                (r"/profile/skills/validate/pending",                                                               ValidateUserPendingSkills),
                (r"/profile/skills/validate/refused",                                                               ValidateUserRefusedSkills),
                (r"/profile/skills/validate/refused/%s/%s"         % (PAGENAMECHARS,PAGENAMECHARS),                 ValidateUserRefusedSkills),
                (r"/profile/skills/validate/social",                                                                ValidateUserSkills),
                (r"/profile/skills/review/%s"                      % (PAGENAMECHARS),                               ReviewValidatedSkills),
                (r"/profile/skills/chart/user/%s"                  % (PAGENAMECHARS),                               SkillUserChartHandler),
                (r"/profile/skills/%s"                             % (NOMEUSERS),                                   SkillHandler),
                (r"/skills/search",                                                                                 SkillSearchHandler)
        ])