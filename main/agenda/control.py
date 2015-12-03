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

import time
from datetime import datetime, date
import re

import tornado.web
import tornado.template

from core.dispatcher import BaseHandler, HANDLERS, URL_TO_PAGETITLE, \
                            NOMEUSERS, \
                            FILENAMECHARS, PAGENAMECHARS, \
                            sortedKeys
import database
import model
from model import _EMPTYAGENDA
import core.model
from core.model import isUserOrMember
import core.database
import log.model
from libs.dateformat import maiorHora, _meses, calculaHoraFinal
import libs.permissions
from libs.permissions import isAllowedToWriteObject

''' importa definição do tutorial deste módulo, se existir _tutorial.py '''
from config import TUTORIAL
try:
    import _tutorial
except ImportError:
    pass

# Formatos de data e hora
_DATA_FMT = "(\d\d\/\d\d\/\d\d\d\d$)"
_HORA_FMT = "(\d\d\:\d\d$)"
   
    
class AgendaHandler(BaseHandler):
    ''' Apresenta a agenda de um usuário/comunidade '''
        
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('agenda')
    @libs.permissions.canReadService ('agenda')       
    def get (self, registry_id):
        user = self.get_current_user()
        mes = self.get_argument("mes","") 
        ano = self.get_argument("ano","")
        
        events_data = {}
        if registry_id in database.AGENDA:
            if mes:
                if not ano:
                    ano = date.today().year
                ano_mes = "%04d%02d" % (int(ano), int(mes))
                if ano_mes in database.AGENDA[registry_id]["events"]:
                    events_data[ano_mes] = database.AGENDA[registry_id]["events"][ano_mes]
            else:
                if ano:
                    for item in database.AGENDA[registry_id]["events"]:
                       if item[0:4] == ano:
                           events_data[item] = database.AGENDA[registry_id]["events"][item]
                else:
                    events_data = database.AGENDA[registry_id]["events"]

        links = []
        if core.model.isUserOrOwner(user, registry_id):
            links.append((u"Alterar permissões desta agenda", "/static/imagens/icones/permissions32.png", "/permission/agenda/"+registry_id, "", "", True))   
 
        log.model.log(user, u'acessou a agenda de', objeto=registry_id, tipo="agenda", news=False)
        self.render("modules/agenda/events.html", REGISTRY_ID=registry_id, EVENTS=events_data, MSG="", NOMEPAG='agenda', \
                            LINKS=links, \
                            ALTERAR=isAllowedToWriteObject(user, "agenda", registry_id))
        


class AgendaXMLHandler(BaseHandler):
    ''' Retorna XML com a agenda de um usuário/comunidade '''
        
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('agenda')
    @libs.permissions.canReadService ('agenda')       
    def get (self, registry_id):
        user = self.get_current_user()
        mes = self.get_argument("mes","") 
        ano = self.get_argument("ano","")

        events_data = {}
        if registry_id in core.database.REGISTRY:

            if registry_id in database.AGENDA:
                if mes:
                    if not ano:
                        ano = date.today().year
                    ano_mes = "%04d%02d" % (int(ano), int(mes))
                    if ano_mes in database.AGENDA[registry_id]["events"]:
                        events_data[ano_mes] = database.AGENDA[registry_id]["events"][ano_mes]
                else:
                    if ano:
                        for item in database.AGENDA[registry_id]["events"]:
                           if item[0:4] == ano:
                               events_data[item] = database.AGENDA[registry_id]["events"][item]
                    else:
                        events_data = database.AGENDA[registry_id]["events"]
                        
        self.set_header("Content-Type", "application/xml")        
        self.render("modules/agenda/events.xml", EVENTS=events_data, NOMEPAG='agenda',SORTEDKEYS=sortedKeys)


class AgendaJSONHandler(BaseHandler):
    ''' Retorna JSON com a agenda de um usuário/comunidade usado pela requisição assíncrona que monta a agenda '''
        
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('agenda')
    @libs.permissions.canReadService ('agenda')       
    def get (self, registry_id):
        
        def prox_mes(ano, mes):
            if mes==12:
                mes=1
                ano=ano+1
            else:
                mes=mes+1
            return "%04d%02d" % (ano, mes)
            
        def ant_mes(ano, mes):
            if mes==1:
                mes=12
                ano=ano-1
            else:
                mes=mes-1
            return "%04d%02d" % (ano, mes)
            
        user = self.get_current_user()
        mes = self.get_argument("mes","") 
        ano = self.get_argument("ano","")

        events_data = {}
        if registry_id in core.database.REGISTRY:

            if registry_id in database.AGENDA:
                if mes:
                    if not ano:
                        ano = date.today().year
                    ano_mes = "%04d%02d" % (int(ano), int(mes))
                    if ano_mes in database.AGENDA[registry_id]["events"]:
                        events_data[ano_mes] = database.AGENDA[registry_id]["events"][ano_mes]
                    '''
                    pmes = prox_mes(int(ano), int(mes))
                    if pmes in database.AGENDA[registry_id]["events"]:
                        events_data[pmes] = database.AGENDA[registry_id]["events"][pmes]
                    ames = ant_mes(int(ano), int(mes))
                    if ames in database.AGENDA[registry_id]["events"]:
                        events_data[ames] = database.AGENDA[registry_id]["events"][ames]
                    '''
                        
                else:
                    if ano:
                        for item in database.AGENDA[registry_id]["events"]:
                           if item[0:4] == ano:
                               events_data[item] = database.AGENDA[registry_id]["events"][item]
                    else:
                        events_data = database.AGENDA[registry_id]["events"]
                        
        #self.set_header("Content-Type", "application/xml")        
        self.write(events_data)


class NewEventHandler(BaseHandler):
    ''' Inclusão de um evento na agenda '''
    
    @tornado.web.authenticated
    @core.model.serviceEnabled('agenda')
    @libs.permissions.canWriteService ('agenda')    
    def get (self, registry_id):
        user = self.get_current_user()
        data = self.get_argument("date","")

        evento = dict(
                      hora = '',
                      duracao = '01:00',
                      msg = '',
                      url = 'http://',
                      dia = '',
                      mes = '',
                      ano = '',
                      data = data
                )            
        self.render("modules/agenda/event-form.html", REGISTRY_ID=registry_id,NOMEPAG='agenda', MSG="", EVENTO=evento)
        
    @tornado.web.authenticated
    @core.model.serviceEnabled('agenda')
    @libs.permissions.canWriteService ('agenda')    
    def post(self, registry_id):
        msg = ""
        user = self.get_current_user()
        data = self.get_argument("data","")
        hora = self.get_argument("hora","")
        duracao = self.get_argument("duracao","")
        
        if re.match(_HORA_FMT, hora) == None:
            msg += u"Hora inválida. Utilize o formato HH:MM<br>"
            
        if re.match(_HORA_FMT, duracao) == None:
            msg += u"Duração inválida. Utilize o formato HH:MM<br>"
             
        if re.match(_DATA_FMT, data) == None:
            msg += u"Data inválida. Utilize o formato DD/MM/AAAA<br>"
        else:
            (dia, mes, ano) = data.split("/")

        texto = self.get_argument("msg","")
        if texto == "":
            msg += u"A descrição não pode ser vazia.<br>"
    
        url = self.get_argument("url","")       # opcional
                    
        if msg:
            evento = dict(
                          hora = hora,
                          duracao = duracao,
                          msg = texto,
                          url = url,
                          dia = dia,
                          mes = mes,
                          ano = ano,
                          data = data
                    )
                        
            self.render("modules/agenda/event-form.html", REGISTRY_ID=registry_id,NOMEPAG='agenda', MSG=msg, EVENTO=evento)
            return
        
        else:
            ano_mes = ano+mes
            
            agenda_data = _EMPTYAGENDA()
            if registry_id in database.AGENDA:
                agenda_data.update(database.AGENDA[registry_id])
            
            if ano_mes not in agenda_data["events"]:
                agenda_data["events"][ano_mes] = {}

            event = dict(
                         msg = texto,
                         owner = user,
                         url = url,
                         duracao = duracao,
                         hora = hora,
                         data_cri = str(datetime.now())
            )

            if dia not in agenda_data["events"][ano_mes]:
                agenda_data["events"][ano_mes][dia] = [event]
            else:
                #agenda_data["events"][ano_mes][dia].append(event)
                sort = False
                
                for i in range(len(agenda_data["events"][ano_mes][dia])):
                    
                    if maiorHora(agenda_data["events"][ano_mes][dia][i]["hora"], event["hora"], True):
                        agenda_data["events"][ano_mes][dia].insert(i, event)
                        sort = True
                        break
                        
                if not sort:
                    agenda_data["events"][ano_mes][dia].append(event)
                                        
            database.AGENDA[registry_id] = agenda_data
            
            log.model.log(user, u'criou um evento na agenda de', objeto=registry_id, tipo="agenda", link="/agenda/%s?mes=%s&ano=%s"%(registry_id, mes, ano))
            self.render("popup_msg.html",MSG=u"Evento criado")

            
class EditEventHandler(BaseHandler):
    ''' Alteração de um evento na agenda '''

    @tornado.web.authenticated
    @core.model.serviceEnabled('agenda')
    @libs.permissions.canWriteService ('agenda')    
    def get (self, registry_id):
        user = self.get_current_user()

        data = self.get_argument("data","")
        pos = int (self.get_argument("pos","0"))
        if len(data) != 8:
            msg = u"data inválida."
            self.render("popup_msg.html", MSG=msg)
            return
        
        ano_mes = data[0:6]
        dia = data[6:]
        
        if ano_mes in database.AGENDA[registry_id]["events"] and \
           dia in database.AGENDA[registry_id]["events"][ano_mes] and \
           len(database.AGENDA[registry_id]["events"][ano_mes][dia]) > pos:
                evento = database.AGENDA[registry_id]["events"][ano_mes][dia][pos]
                evento['dia'] = dia
                evento['mes'] = ano_mes[4:]
                evento['ano'] = ano_mes[0:4]
                evento['pos'] = pos
                self.render("modules/agenda/event-edit.html", EVENTO=evento, NOMEPAG='agenda', \
                                    REGISTRY_ID=registry_id, MSG="")
        else:
            msg = u"Evento não encontrado."
            self.render("popup_msg.html", MSG=msg)
            
    @tornado.web.authenticated
    @core.model.serviceEnabled('agenda')
    @libs.permissions.canWriteService ('agenda')    
    def post(self, registry_id):
        msg = ""
        user = self.get_current_user()     
        dia = self.get_argument("dia","") 
        mes = self.get_argument("mes","") 
        ano = self.get_argument("ano","")
        hora = self.get_argument("hora","")
        duracao = self.get_argument("duracao","") 
        texto = self.get_argument("msg","")
        url = self.get_argument("url","")
        pos = int(self.get_argument("pos","0"))
                
        if texto == "":    
            msg += u"A descrição não pode ser vazia.<br>"

        if re.match(_HORA_FMT, hora) == None:
            msg += u"Hora inválida. Utilize o formato HH:MM<br>"
            
        if re.match(_HORA_FMT, duracao) == None:
            msg += u"Duração inválida. Utilize o formato HH:MM<br>"
                              
        if msg:
            evento = dict(
                          hora = hora,
                          duracao = duracao,
                          msg = texto,
                          url = url,
                          dia = dia,
                          mes = mes,
                          ano = ano,
                          pos = pos
                    )

            self.render("modules/agenda/event-edit.html", EVENTO=evento, NOMEPAG='agenda', \
                                REGISTRY_ID=registry_id, MSG=msg)            

        else:
            dia = "%02d" % int(dia)
            ano_mes = "%04d%02d" % (int(ano), int(mes))

            agenda_data = _EMPTYAGENDA()
            if registry_id in database.AGENDA:
                agenda_data.update(database.AGENDA[registry_id])
            
            if ano_mes not in agenda_data["events"]:
                agenda_data["events"][ano_mes] = {}
                
            
            event = agenda_data["events"][ano_mes][dia][pos]
            
            agenda_data["events"][ano_mes][dia].pop(pos)
            
            event["msg"] = texto
            event["hora"] = hora
            event["duracao"] = duracao
            event["owner"] = user
            event["url"] = url
            event["data_cri"] = str(datetime.now())
                   
            
            if dia not in agenda_data["events"][ano_mes]:
                agenda_data["events"][ano_mes][dia] = {}
            else:
                if len(agenda_data["events"][ano_mes][dia])==0:
                    agenda_data["events"][ano_mes][dia].append(event)
                else:
                    sort = False
                
                    for i in range(len(agenda_data["events"][ano_mes][dia])):
                        
                        if maiorHora(agenda_data["events"][ano_mes][dia][i]["hora"], event["hora"], True):
                            agenda_data["events"][ano_mes][dia].insert(i, event)
                            sort = True
                            break
                            
                    if not sort:
                            agenda_data["events"][ano_mes][dia].append(event)                    
            
            try:
                database.AGENDA[registry_id] = agenda_data
            except Exception as detail:
                self.render("home.html",NOMEPAG='agenda', MSG=u"Erro: %s" % detail)
                return
            
            log.model.log(user, u'alterou um evento na agenda de', objeto=registry_id, tipo="agenda", \
                          link="/agenda/%s?mes=%s&ano=%s"%(registry_id, mes, ano))
            self.render("popup_msg.html",MSG=u"Evento Alterado")


class DeleteEventHandler(BaseHandler):
    ''' Exclusão de um dia na agenda '''

    @tornado.web.authenticated
    @core.model.serviceEnabled('agenda')
    @libs.permissions.canWriteService ('agenda')    
    def get (self, registry_id):
        user = self.get_current_user()

        data = self.get_argument("data","")
        pos = int(self.get_argument("pos","0"))
        if len(data) != 8:
            msg = u"data inválida."
            self.render("popup_msg.html", MSG=msg)
            return
        
        ano_mes = data[0:6]
        dia = data[6:]
        
        if ano_mes in database.AGENDA[registry_id]["events"]:
            if dia in database.AGENDA[registry_id]["events"][ano_mes]:
                event_data = _EMPTYAGENDA()
                event_data.update(database.AGENDA[registry_id])
                if len(event_data["events"][ano_mes][dia]) <= pos:
                    msg = u"evento não encontrado."
                    self.render("popup_msg.html", MSG=msg)
                    return                        
                del event_data["events"][ano_mes][dia][pos]
                if not event_data["events"][ano_mes][dia]:
                    del event_data["events"][ano_mes][dia]
                if not event_data["events"][ano_mes]:
                    del event_data["events"][ano_mes]
                database.AGENDA[registry_id] = event_data
        log.model.log(user, u'removeu um evento da agenda de', objeto=registry_id, tipo="agenda")
        self.render("popup_msg.html",MSG=u"Evento Excluído")

       
class AgendaListDayHandler(BaseHandler):
    ''' Apresenta a agenda de um dia de um usuário/comunidade '''
        
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('agenda')
    @libs.permissions.canReadService ('agenda')       
    def get (self, registry_id):
        user = self.get_current_user()
        evento = self.get_argument("event","")
        (ano, mes, dia, num) = evento.split("-") 
        
        ano_mes = str(ano)+str(mes)

        events_data = []
        if registry_id in database.AGENDA:
            agenda_data = database.AGENDA[registry_id]
            if ano_mes in agenda_data["events"] and dia in agenda_data["events"][ano_mes]:
                events_data = agenda_data["events"][ano_mes][dia]
        for item in events_data:
            item["hora_fim"] = calculaHoraFinal(item["hora"], item["duracao"])

        log.model.log(user, u'acessou a agenda de', objeto=registry_id, tipo="agenda", news=False)
        self.render("modules/agenda/events-list.html", REGISTRY_ID=registry_id, EVENTS=events_data, MSG="", NOMEPAG='agenda', \
                            ANO=ano , MES=mes, DIA=dia, NUM=num, MESES=_meses, \
                            ALTERAR=core.model.isUserOrMember(user,registry_id))


URL_TO_PAGETITLE.update ({
        "agenda": "Agenda"
    })

HANDLERS.extend([
            (r"/agenda/new/%s" % NOMEUSERS,    NewEventHandler),
            (r"/agenda/edit/%s" % NOMEUSERS,   EditEventHandler),
            (r"/agenda/delete/%s" % NOMEUSERS, DeleteEventHandler),
            (r"/agenda/xml/%s" % NOMEUSERS,    AgendaXMLHandler),
            (r"/agenda/json/%s" % NOMEUSERS,   AgendaJSONHandler),
            (r"/agenda/day/%s" % NOMEUSERS,    AgendaListDayHandler),
            (r"/agenda/%s" % NOMEUSERS,        AgendaHandler)
    ])
