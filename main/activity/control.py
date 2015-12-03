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

from datetime import datetime
from uuid import uuid4
from operator import itemgetter

import tornado.web
from tornado.web import HTTPError
import tornado.template

import model
from core.dispatcher import BaseHandler, HANDLERS, URL_TO_PAGETITLE, \
                            NOMEUSERS, FILENAMECHARS, PAGENAMECHARS
                            
import core.model
from core.model import isUserOrOwner, isACommunity
from config import PLATAFORMA_URL
import log.model
import question.model
from libs.notify import Notify
from libs.dateformat import short_datetime, verificaIntervaloDMY, maiorData
from libs.strformat import remove_diacritics, remove_special_chars, remove_html_tags, str_limit
import libs.permissions
from libs.permissions import isAllowedToDeleteObject, \
                             isAllowedToReadObject, isAllowedToWriteObject


def prepareActivities(user, activities):
    for a in activities:
        a["value"]["titulo"] = str_limit(remove_html_tags(a["value"]["titulo"]), 120)
        
        # somente o dono do tópico ou o dono/admins da comunidade podem apagar um tópico
        a["value"]["apagar"] = isAllowedToDeleteObject(user, a["value"]["owner"], a["value"]["registry_id"]+"/"+a["value"]["_id"])
        
        # somente o dono do objeto pode alterar
        a["value"]["alterar"] = isAllowedToWriteObject(user, "activity", a["value"]["registry_id"])

    return activities


class NewGroupHandler(BaseHandler):
    ''' Inclusão de um grupo '''

    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('activity')
    @libs.permissions.canWriteService ('activity')
    def get (self, registry_id):
        user = self.get_current_user()
        
        self.render("modules/activity/newgroup-form.html",  NOMEPAG=u"atividades", \
                    GRUPO=model.Group(), \
                    REGISTRY_ID=registry_id, MSG="")

    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('activity')
    @libs.permissions.canWriteService ('activity')
    def post(self, registry_id):
        user = self.get_current_user()
        type = self.get_argument("type","")

        _group = model.Group()
        msg = ""
        _group.titulo = self.get_argument("titulo","")
        if _group.titulo == "":
            msg += u"O nome do grupo não pode ser vazio.<br/>"
        else:
            _group.name_id = remove_special_chars(remove_diacritics(_group.titulo.replace(" ","_")))
            if _group.name_id == "":
                msg += u"Nome do grupo inválido<br/>"

        if msg:
            self.render("modules/activity/newgroup-form.html",  NOMEPAG=u"atividades", \
                        GRUPO=_group, \
                        REGISTRY_ID=registry_id, MSG=msg)
            return       
        
        doc_id = uuid4().hex
        _group.data_cri = str(datetime.now())
        _group.service="activity"
        _group.type="group"
        _group.registry_id = registry_id
        _group.owner = user
        
        _group.save(id=doc_id)
        
        log.model.log(user, u'criou um grupo de atividades em', objeto=registry_id, tipo="activity", link="/activity/%s"%registry_id)
        self.render("modules/activity/newgroup-form.html",  NOMEPAG=u"atividades", \
                    GRUPO=model.Group(), \
                    REGISTRY_ID=registry_id, MSG="O grupo foi criado com sucesso")  
            
        
        
class NewActivityHandler(BaseHandler):
    ''' Inclusão de uma atividade '''

    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('activity')
    @libs.permissions.canWriteService ('activity')
    def get (self, registry_id):
        user = self.get_current_user()
        group_id = self.get_argument("id","")
        
        self.render("modules/activity/activity-form.html",  NOMEPAG=u"atividades", \
                    ATIVIDADE=model.Activity(), \
                    GROUP=group_id, \
                    REGISTRY_ID=registry_id, MSG="")

    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('activity')
    @libs.permissions.canWriteService ('activity')
    def post(self, registry_id):
        user = self.get_current_user()

        _atividade = model.Activity()
        msg = ""
        _atividade.titulo = self.get_argument("titulo","")
        if _atividade.titulo == "":
            msg += u"O nome da atividade não pode ser vazio.<br/>"
        else:
            _atividade.name_id = remove_special_chars(remove_diacritics(_atividade.titulo.replace(" ","_")))
            if _atividade.name_id == "":
                msg += u"Título da atividade inválido<br/>"

        _atividade.group_id = self.get_argument("id","") 
        if _atividade.group_id == "":
            msg += u"O grupo da atividade não foi informado.<br/>"
            
        if msg:
            self.render("modules/activity/activity-form.html",  NOMEPAG=u"atividades", \
                        ATIVIDADE=_atividade, \
                        GROUP=_atividade.group_id, \
                        REGISTRY_ID=registry_id, MSG=msg)  
            return       
        
        #verifica se o registry é usuário ou comunidade  
        if registry_id == user: 
            _atividade.subtype="user"
        else:
            _atividade.subtype="comunity"
        
        doc_id = uuid4().hex
        #_atividade.observacao = self.get_argument("observacao",'')
        _atividade.data_cri = str(datetime.now())
        _atividade.data_start = short_datetime(_atividade.data_cri, include_separator=" ")
        _atividade.data_end = ""
        _atividade.encarregados.append(user)
        _atividade.prioritario = self.get_argument("prioritario",'N')
        _atividade.status = u"pendente"
        _atividade.service="activity"
        _atividade.type="activity"
        _atividade.registry_id = registry_id
        _atividade.owner = user
        
        log.model.log(user, u'criou uma atividade em', objeto=registry_id, tipo="activity",link="/activity/%s"%registry_id)
        _atividade.save(id=doc_id)
        
        self.render("modules/activity/activity-form.html",  NOMEPAG=u"atividades", \
                    ATIVIDADE=model.Activity(), \
                    GROUP=_atividade.group_id, \
                    REGISTRY_ID=registry_id, MSG="A atividade foi criada com sucesso")  
 
class ActivityShowHandler(BaseHandler):
    ''' Mostra uma atividade '''

    @tornado.web.authenticated
    #@core.model.allowedToAccess
    #@core.model.serviceEnabled('activity')
    #@libs.permissions.canWriteService ('activity')
    def get (self, registry_id, id):
        user = self.get_current_user()
       
        _atividade = model.Activity().retrieve(id)
        if _atividade:
            
            self.render("modules/activity/activity-show.html",  NOMEPAG=u"atividades", ATIVIDADE=_atividade, REGISTRY_ID=registry_id, MSG="")
       
        else:        
            
              raise HTTPError(404)
        
        
class ActivityEditHandler(BaseHandler):
    ''' Edição de uma atividade '''

    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('activity')
    @libs.permissions.canWriteService ('activity')
    def get (self, registry_id, id):
        user = self.get_current_user()
        _atividade = model.Activity().retrieve(id)
        
        members = []
        if isACommunity(registry_id):
            _community = core.model.Registry().retrieve(registry_id)
            (num_members, members) = _community.getMembersList()
        
        if _atividade:
            self.render("modules/activity/activity-edit.html",  NOMEPAG=u"atividades",  MEMBERS=members, \
                        ATIVIDADE=_atividade, REGISTRY_ID=registry_id, MSG="")
        else:        
              raise HTTPError(404)
          
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('activity')
    @libs.permissions.canWriteService ('activity')
    def post(self, registry_id, id):
        user = self.get_current_user()
        _atividade = model.Activity().retrieve(id)
        
        members = []
        if isACommunity(registry_id):
            _community = core.model.Registry().retrieve(registry_id)
            (num_members, members) = _community.getMembersList()
        
        msg = ""
        titulo = self.get_argument("titulo","")
        if not titulo:
            msg = u"A atividade precisa ter um titulo.<br/>"
            
        if _atividade.subtype== "comunity":
            _atividade.encarregados = self.get_arguments("encarregados")
        
        _atividade.titulo = titulo
        _atividade.observacao = self.get_argument("observacao",'')
        _atividade.data_start = self.get_argument("data_start",'')
        _atividade.data_end = self.get_argument("data_end",'')
        _atividade.data_conclusion = self.get_argument("data_conclusion",'')
        _atividade.prioritario = self.get_argument("prioritario",'N')
        _atividade.status = self.get_argument("status","")

        if _atividade.data_end and _atividade.data_start and not maiorData(_atividade.data_end, _atividade.data_start, short=True):
            msg += u"A Data de encerramento não pode ser anterior à Data de início.<br/>"
        
        if msg: 
            self.render("modules/activity/activity-edit.html",  NOMEPAG=u"atividades", ATIVIDADE=_atividade, MEMBERS=members, \
                                                                REGISTRY_ID=registry_id, MSG=msg)  
            return       
        
        doc_id = id
        _atividade.data_alt = str(datetime.now())
        _atividade.type="activity"
        _atividade.registry_id = registry_id
        _atividade.alterado_por = user
        _atividade.save(id=doc_id)
        
        log.model.log(user, u'alterou uma atividade em', objeto=registry_id, tipo="activity", link="/activity/%s"%registry_id)
        self.render("modules/activity/activity-edit.html",  NOMEPAG=u"atividades", MEMBERS=members, ATIVIDADE=_atividade, \
                    REGISTRY_ID=registry_id, MSG=u"Alteração realizada com sucesso")  

                
class ActivityListHandler(BaseHandler):
    ''' Lista de atividades '''
                
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('activity')
    @libs.permissions.canReadService ('activity')
    def get (self, registry_id):
        #hora_inicio = datetime.now()
        #print "inicio=", hora_inicio

        user = self.get_current_user()
        _atividades = prepareActivities(user, model.Activity().listActivities(registry_id))
        #print "prepareActivities=", datetime.now()
        
        groupIsfilled = model.Group().GroupIsFilled(registry_id)
        #print "GroupIsFilled=", datetime.now()

        links = []            
        if isUserOrOwner(user, registry_id):
            links.append((u"Alterar permissões", "/static/imagens/icones/permissions32.png", "/permission/activity/"+registry_id, "", "", True))   
        if user == registry_id:
            links.append((u"Atividades pendentes de "+registry_id, "/static/imagens/icones/pendent_activity32.png", "/activity/pendent/"+registry_id, "", "", False))
            
        log.model.log(user, u'acessou as atividades de', objeto=registry_id, tipo="activity", link="/activity/%s"%registry_id, news=False)

        #print "links=", datetime.now()
        self.render("modules/activity/activity-list.html",  NOMEPAG=u"atividades", \
                                     GROUPISFILLED = groupIsfilled, \
                                     ADMIN = isAllowedToWriteObject(user, "activity", registry_id) , \
                                     LINKS=links, \
                                     ATIVIDADES=_atividades, REGISTRY_ID=registry_id, MSG="")
            
        #hora_fim = datetime.now()
        #print "%s... %s -> %s = %s\n" % (registry_id, str(hora_inicio), str(hora_fim), str(hora_fim-hora_inicio))

            
class FinalizedActivityHandler(BaseHandler):
    ''' lista de atividades finalizadas '''

    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('activity')
    @libs.permissions.canReadService ('activity')
    def get (self, registry_id):
      
        user = self.get_current_user()
        _atividades = prepareActivities(user, model.Activity().listfinalizedByRegistry_id(registry_id))
        groupIsfilled = model.Group().GroupIsFilled(registry_id, True)
        
        if _atividades:
            log.model.log(user, u'acessou as atividades finalizadas de', objeto=registry_id, tipo="activity", link="/activity/%s"%registry_id, news=False)

            self.render("modules/activity/activity-finalized.html",  NOMEPAG=u"atividades", \
                                     ADMIN = isAllowedToWriteObject(user, "activity", registry_id) , \
                                     GROUPISFILLED = groupIsfilled, \
                                     ATIVIDADES=_atividades, REGISTRY_ID=registry_id, MSG="")
        else:
            
            raise HTTPError(404)
                
          
class ActivityDeleteHandler(BaseHandler):
    ''' Apaga atividade ou grupo '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('activity')
    @libs.permissions.canWriteService ("activity")
    def get(self, registry_id, id):
        user = self.get_current_user() 
        _object = model.Activity().retrieve(id)
        
        if _object :
            _object_owner = _object.owner
  
            if not isAllowedToDeleteObject(user, _object_owner, registry_id+"/"+id):
                raise HTTPError(403)
               
            elif _object.type == "activity" :
                _object.delete()
                log.model.log(user, u'removeu uma atividade de', objeto=registry_id, tipo="activity", link="/activity/%s"%registry_id)
                self.redirect("/activity/%s" % registry_id)
                return
            elif _object.type == "group" and not model.Group().countObjectsByGroup(id):
                _object.delete()
                log.model.log(user, u'removeu um grupo de atividades de', objeto=registry_id, tipo="activity", link="/activity/%s"%registry_id)
                self.redirect("/activity/%s" % registry_id)
            
        else:
            raise HTTPError(404)
           
  
class PendingActivityHandler(BaseHandler):
    ''' lista todas atividades nas quais o registry_id é encarregado'''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('activity')
    @libs.permissions.canReadService ('activity')
    def get (self, registry_id):
        user = self.get_current_user() 
        _atividades = model.Activity().listPendentActivities(registry_id)

        links = []            
        links.append((u"Atividades de "+registry_id, "/static/imagens/icones/pendent_activity32.png", "/activity/"+registry_id, "", "", False))
                  
        log.model.log(user, u'acessou as atividades pendentes de', objeto=registry_id, tipo="activity", link="/activity/%s"%registry_id, news=False)
        
        self.render("modules/activity/activity-pendent.html", NOMEPAG=u"Atividades", \
                                     ATIVIDADES=_atividades, LINKS=links, REGISTRY_ID=registry_id, MSG="")  
        
        
URL_TO_PAGETITLE.update ({
        "activity": u"Atividades"
    })


HANDLERS.extend([
            (r"/activity/newgroup/%s"            % (NOMEUSERS),                     NewGroupHandler),        
            (r"/activity/new/%s"                 % (NOMEUSERS),                     NewActivityHandler),
            (r"/activity/finalized/%s"           % (NOMEUSERS),                     FinalizedActivityHandler), 
            (r"/activity/pendent/%s"             % (NOMEUSERS),                     PendingActivityHandler),       
            (r"/activity/%s"                     % (NOMEUSERS),                     ActivityListHandler),
            (r"/activity/%s/%s"                  % (NOMEUSERS, NOMEUSERS),          ActivityShowHandler),
            (r"/activity/edit/%s/%s"             % (NOMEUSERS, NOMEUSERS),          ActivityEditHandler),
            (r"/activity/delete/%s/%s"           % (NOMEUSERS, NOMEUSERS),          ActivityDeleteHandler)
            
    ])
