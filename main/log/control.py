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

import tornado.web
import tornado.template
import model
import database

from datetime import datetime
import core.model
from core.model import isACommunity, isOwner
from core.dispatcher import BaseHandler, HANDLERS, URL_TO_PAGETITLE, \
                            NOMEUSERS
from config import PRIV_GLOBAL_ADMIN, PLATAFORMA                        
from libs.dateformat import short_datetime, converteDataDMYToYMDStr
#converteDataDMYToMDYStrSemHora, calculaDiferencaDatas, converteDataDMYToYMDStrSemHora, converteDataYMDToMDYStrSemHora

''' importa definição do tutorial deste módulo, se existir _tutorial.py '''
from config import TUTORIAL
try:
    import _tutorial
except ImportError:
    pass


# Número máximo de itens exibidos na lista de novidades de um usuário
NUM_MAX_NOVIDADES = 40

           
            
class ListMyNewsHandler(BaseHandler):
    ''' Lista o que o usuário logado tem feito no Activ '''
    
    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        page = int(self.get_argument("page","1"))
        log_data = []
        log_data = model.get_log_list(user, date_time=True, news=False)
        log_count = len(log_data)
        
        # obtem apenas a página que será exibida
        skip = (page-1)*NUM_MAX_NOVIDADES
        log_data = log_data[skip:skip+NUM_MAX_NOVIDADES]

        tabs = []
        tabs.append(("O que meus amigos tem feito no "+PLATAFORMA, "/news/"+user))
        tabs.append(("O que eu tenho feito no "+PLATAFORMA, ""))
        
        model.log(user, u'acessou as suas novidades', tipo="news", news=False)        
        self.render("modules/log/news-list.html", NOMEPAG="novidades", REGISTRY_ID=user, \
                                                  NEWS=log_data, NEWS_COUNT=log_count, \
                                                  PAGE=page, PAGESIZE=NUM_MAX_NOVIDADES, \
                                                  TABS=tabs, \
                                                  MSG="")

class ListNewsHandler(BaseHandler):
    ''' Lista novidades para um usuário ou comunidade '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    def get(self, registry_id):
        user = self.get_current_user()
        page = int(self.get_argument("page","1"))
        log_data = []
        if isACommunity(registry_id) or user==registry_id:
            log_data = model.get_news_list(registry_id, date_time=True)
        else:
            log_data = model.get_log_list(registry_id, date_time=True, news=True)

        log_count = len(log_data)
        
        # obtem apenas a página que será exibida
        skip = (page-1)*NUM_MAX_NOVIDADES
        log_data = log_data[skip:skip+NUM_MAX_NOVIDADES]
        
        tabs = []
        if user==registry_id:
            tabs.append(("O que meus amigos tem feito no "+PLATAFORMA, ""))
            tabs.append(("O que eu tenho feito no "+PLATAFORMA, "/news"))
        
        model.log(user, u'acessou as novidades de', objeto=registry_id, tipo="news", news=False)        
        self.render("modules/log/news-list.html", NOMEPAG="novidades", REGISTRY_ID=registry_id, \
                                                  NEWS=log_data, NEWS_COUNT=log_count, \
                                                  PAGE=page, PAGESIZE=NUM_MAX_NOVIDADES, \
                                                  TABS=tabs, \
                                                  MSG="")
                
class PlotSystemStats(BaseHandler):       
    @tornado.web.authenticated
    @core.model.userIsCommunityMember (PRIV_GLOBAL_ADMIN)
    def get(self):
        tabs = []
        tabs.append(("N&#186; Total de Acessos", ""))
        tabs.append(("N&#186; de Acessos por Usuário", "/stats/users"))        
        self.render("modules/log/form-system-stats.html", NOMEPAG=u"estatísticas", \
                    REGISTRY_ID=PRIV_GLOBAL_ADMIN, \
                    TABS=tabs, MSG="")

    @tornado.web.authenticated
    @core.model.userIsCommunityMember (PRIV_GLOBAL_ADMIN)
    def post(self):      
        tipo = self.get_argument("tipo","") 
        data_inicial = converteDataDMYToYMDStr(self.get_argument("data_inicio",""))
        data_final = converteDataDMYToYMDStr(self.get_argument("data_encerramento",""))
        format = '%Y-%m-%d'
       
        msg = ""
        if tipo=="":
            msg = u"Tipo de gráfico não especificado. <br/>"            
        if (not data_inicial) or (not data_final):
            msg = u"Data final ou inicia _prv.apps = priv_appsl inválida. <br/>"
        elif ((datetime.strptime(data_final, format)) < (datetime.strptime(data_inicial, format))):
            msg = u"Data final anterior à data inicial. <br/>"

        if msg:
            self.render("modules/log/form-system-stats.html", NOMEPAG=u"estatísticas", \
                        REGISTRY_ID=PRIV_GLOBAL_ADMIN, \
                        MSG=msg)
        else:
            lista_dados = model.Log.get_system_stats(tipo, data_inicial, data_final) 
            self.render("modules/log/render-system-stats.html", NOMEPAG=u"estatísticas", \
                         REGISTRY_ID=PRIV_GLOBAL_ADMIN, \
                         ALTURA=(len(lista_dados)*45), \
                         INICIO=self.get_argument("data_inicio",""), FIM=self.get_argument("data_encerramento",""), \
                         TIPO=tipo, LISTADEDADOS=lista_dados)

class PlotSystemUserStats(BaseHandler):       
        
    @tornado.web.authenticated
    @core.model.userIsCommunityMember (PRIV_GLOBAL_ADMIN)
    def get(self):
        tabs = []
        tabs.append(("N&#186; Total de Acessos", "/stats"))
        tabs.append(("N&#186; de Acessos por Usuário", ""))             
        self.render("modules/log/form-system-user-stats.html", NOMEPAG=u"estatísticas", 
                    REGISTRY_ID=PRIV_GLOBAL_ADMIN, \
                    TABS=tabs, MSG="")

        
    @tornado.web.authenticated
    @core.model.userIsCommunityMember (PRIV_GLOBAL_ADMIN)    
    def post(self):      
        num_usuarios = self.get_argument("num_usuarios","")
        data_inicial = converteDataDMYToYMDStr(self.get_argument("data_inicio",""))
        data_final = converteDataDMYToYMDStr(self.get_argument("data_encerramento",""))
        format = '%Y-%m-%d'
  
        msg = ""
    
        if (not data_inicial) or (not data_final):
            msg = u"Data final ou inicia _prv.apps = priv_appsl inválida. <br/>"
        elif ((datetime.strptime(data_final, format)) < (datetime.strptime(data_inicial, format))):
            msg = u"Data final anterior à data inicial. <br/>"

        (listaDeDados, listaDeMembros) = model.Log.get_system_user_stats(num_usuarios, data_inicial, data_final)
    
        tamanho_eixo = model.get_maximum_axis_size(listaDeDados)
        
        if msg:
            self.render("modules/log/form-system-user-stats.html", NOMEPAG=u"estatísticas", 
                        REGISTRY_ID=PRIV_GLOBAL_ADMIN, \
                        MSG=msg)
        else:
            self.render("modules/log/render-system-user-stats.html", NOMEPAG=u"estatísticas", LISTADEDADOS = listaDeDados, LISTADEUSUARIOS = listaDeMembros, \
                        REGISTRY_ID=PRIV_GLOBAL_ADMIN, \
                        TAMANHO_EIXO=tamanho_eixo, TITLE=u"Ações de usuário(s) ao longo do tempo",ALTURA = (len(listaDeDados)*45))

class PlotStats(BaseHandler):       
        
    @tornado.web.authenticated
    @core.model.userOrOwner    
    def get(self, registry_id):
        comunidade = core.model.Community().retrieve(registry_id)
        listaMembrosDaComunidade = [ part[0] for part in comunidade.getMembersList(return_is_owner=False)[1] ]
        
        
        tabs = []
        tabs.append(("N&#186; de Acessos por Usuário", ""))
        tabs.append(("N&#186; de Acessos por Objeto", "/stats/object/"+registry_id))
                    
        self.render("modules/log/plot-stats-data.html", NOMEPAG=u"estatísticas", \
                    NOMECOMUNIDADE=registry_id, MEMBROSDACOMUNIDADE=listaMembrosDaComunidade, REGISTRY_ID=registry_id, \
                    TABS=tabs, MSG="")

        
    @tornado.web.authenticated
    @core.model.userOrOwner    
    def post(self,registry_id):      
        nome_comunidade = self.get_argument("nome_comunidade","")
        tipo = self.get_argument("tipo_servico","") 
        membro = self.get_argument("select_membros","")
        tipo_log = self.get_argument("group1","")
        periodo_estatistica = self.get_argument("periodo_estatistica","")
        
        data_inicial = converteDataDMYToYMDStr(self.get_argument("data_inicio",""))
        data_final = converteDataDMYToYMDStr(self.get_argument("data_encerramento",""))
        format = '%Y-%m-%d'
       
        msg = ""
        if (not data_inicial) or (not data_final):
            msg = u"Data final ou inicial inválida."
        elif ((datetime.strptime(data_final, format)) < (datetime.strptime(data_inicial, format))):
            msg = u"Data final anterior à data inicial."
        else:
            if periodo_estatistica == "diario": 
                (listaDeDados, listaDeMembros) = model.get_community_user_action_list(nome_comunidade, data_inicial, data_final, tipo, membro, tipo_log, format)
                if len(listaDeMembros) > 20:
                    msg = u"Não é possível gerar este gráfico com mais de 20 usuários. Por favor, restrinja mais a sua busca ou utilize a estatística de todo o período."
            elif periodo_estatistica == "total":
                (listaDeDados, listaDeMembros) = model.get_community_users_action_list_bar_chart(nome_comunidade, data_inicial, data_final, tipo, tipo_log, format)     
            if not listaDeDados:
                msg = u"Não há ações de um usuário no período solicitado."
            else:
                tamanho_eixo = model.get_maximum_axis_size(listaDeDados, periodo_estatistica)
        
        if msg:
            comunidade = core.model.Community().retrieve(registry_id)
            listaMembrosDaComunidade = [ part[0] for part in comunidade.getMembersList(return_is_owner=False)[1] ]
            tabs = []
            tabs.append(("N&#186; de Acessos por Usuário", ""))
            tabs.append(("N&#186; de Acessos por Objeto", "/stats/object/"+registry_id))
            self.render("modules/log/plot-stats-data.html", NOMEPAG=u"estatísticas", \
                        NOMECOMUNIDADE=registry_id, MEMBROSDACOMUNIDADE=listaMembrosDaComunidade, REGISTRY_ID=registry_id, \
                        TABS=tabs, MSG=msg)
        else:
            if periodo_estatistica == "diario":
                self.render("modules/log/stats-render.html", NOMEPAG=u"estatísticas", LISTADEDADOS = listaDeDados, LISTADEUSUARIOS = listaDeMembros, \
                             REGISTRY_ID=registry_id, TAMANHO_EIXO=tamanho_eixo, TITLE=u"Ações de usuário(s) ao longo do tempo")
            elif periodo_estatistica == "total":
                self.render("modules/log/stats-render-bar-chart.html", NOMEPAG=u"estatísticas", LISTADEDADOS = listaDeDados, LISTADEUSUARIOS = listaDeMembros, \
                             REGISTRY_ID=registry_id, TAMANHO_EIXO=tamanho_eixo, TITLE=u"Ações de usuário(s) ao longo do tempo",ALTURA = (len(listaDeDados)*45))

class PlotObjectStats(BaseHandler):       

    @tornado.web.authenticated
    @core.model.userOrOwner    
    def get(self, registry_id):
        tabs = []
        tabs.append(("N&#186; de Acessos por Usuário", "/stats/"+registry_id))
        tabs.append(("N&#186; de Acessos por Objeto", ""))        
        self.render("modules/log/plot-objects-data.html", NOMEPAG=u"estatísticas", \
                    NOMECOMUNIDADE=registry_id, REGISTRY_ID=registry_id, \
                    TABS=tabs, MSG="")
        
    @tornado.web.authenticated
    @core.model.userOrOwner    
    def post(self,registry_id):      
        nome_comunidade = self.get_argument("nome_comunidade","")
        tipo_servico = self.get_argument("tipo_servico","")
        periodo_estatistica = self.get_argument("periodo_estatistica","")
        tipo_log = self.get_argument("group1","")
        data_inicial = converteDataDMYToYMDStr(self.get_argument("data_inicio",""))
        data_final = converteDataDMYToYMDStr(self.get_argument("data_encerramento",""))
        format = '%Y-%m-%d'

        msg = ""
        if (not data_inicial) or (not data_final):
            msg = u"Data final ou inicial inválida."
        elif ((datetime.strptime(data_final, format)) < (datetime.strptime(data_inicial, format))):
            msg = u"Data final anterior à data inicial."
        else:
            if periodo_estatistica == "diario":
                (listaDeDados, listaDeObjetos) = model.get_community_object_action_list(nome_comunidade, data_inicial, data_final, tipo_servico, tipo_log, format)
                if len(listaDeObjetos) > 20:
                    msg = u"Não é possível gerar este gráfico com mais de 20 objetos. Por favor, restrinja mais a sua busca ou utilize a estatística de todo o período."
            elif periodo_estatistica == "total":
                (listaDeDados, listaDeObjetos) = model.get_community_object_action_list_bar_chart(nome_comunidade, data_inicial, data_final, tipo_servico, tipo_log, format)
            
            if not listaDeDados:
                msg = u"Não há ações em um objeto no período solicitado."
            else:
                tamanho_eixo = model.get_maximum_axis_size(listaDeDados, periodo_estatistica)
                
        if msg:
            tabs = []
            tabs.append(("N&#186; de Acessos por Usuário", "/stats/"+registry_id))
            tabs.append(("N&#186; de Acessos por Objeto", ""))              
            self.render("modules/log/plot-objects-data.html", NOMEPAG=u"estatísticas", \
                        NOMECOMUNIDADE=registry_id, REGISTRY_ID=registry_id, \
                        TABS=tabs, MSG=msg)
        else:
            
            if periodo_estatistica == "diario":
                self.render("modules/log/stats-render.html", NOMEPAG=u"estatísticas", LISTADEDADOS = listaDeDados, LISTADEUSUARIOS = listaDeObjetos, \
                             REGISTRY_ID=registry_id, TAMANHO_EIXO=tamanho_eixo, TITLE=u"Uso de objetos ao longo do tempo")
            elif periodo_estatistica == "total":
                self.render("modules/log/stats-render-bar-chart.html", NOMEPAG=u"estatísticas", LISTADEDADOS = listaDeDados, LISTADEUSUARIOS = listaDeObjetos, \
                             REGISTRY_ID=registry_id, TAMANHO_EIXO=tamanho_eixo, TITLE=u"Uso de objetos ao longo do tempo", ALTURA = (len(listaDeDados)*45))
                    

URL_TO_PAGETITLE.update ({
        "news": "Novidades",
        "stats": u"Estatísticas"
        })

HANDLERS.extend([
        (r"/news",                                      ListMyNewsHandler),
        (r"/news/%s"                % NOMEUSERS,        ListNewsHandler),
        (r"/stats",                                     PlotSystemStats),
        (r"/stats/users",                               PlotSystemUserStats),
        (r"/stats/%s"               % NOMEUSERS,        PlotStats),
        (r"/stats/object/%s"        % NOMEUSERS,        PlotObjectStats)
        ])
