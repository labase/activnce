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

import re
import time
from datetime import datetime
from urllib import quote,unquote

import tornado.web
import tornado.template
from tornado.web import HTTPError

import model
from model import _EMPTYEVALUATION
import core.model
from core.model import isOwner, isMember, isUserOrMember
from core.model import ifExists

import core.database

import log.model
import wiki.model
from core.dispatcher import BaseHandler, HANDLERS, URL_TO_PAGETITLE, \
                            NOMEUSERS, \
                            FILENAMECHARS, PAGENAMECHARS
                            
from libs.dateformat import short_datetime, verificaIntervaloDMY
from libs.strformat import remove_diacritics, remove_special_chars
import libs.permissions
from libs.permissions import usersAllowedToRead, isAllowedToReadObject

''' importa definição do tutorial deste módulo, se existir _tutorial.py '''
from config import TUTORIAL
try:
    import _tutorial
except ImportError:
    pass

def prepareEvaluations(user, avals):
    aval_data = []
    for aval in avals:
        dentroDoPeriodo = verificaIntervaloDMY(aval["data_inicio"], aval["data_encerramento"]) == 0
        (registry_id, obj_name) = aval["_id"].split("/")
        aval_data.append((aval["_id"], \
                                  aval["descricao"], \
                                  aval["tipo"], \
                                  aval["data_inicio"], \
                                  aval["data_encerramento"], \
                                  aval["jaAvaliou"] or not dentroDoPeriodo or not isAllowedToReadObject(user, "evaluation", registry_id, obj_name)\
                                  ))
    return aval_data

def prepareResults(aval_data):

    (registry_id, nomeobj) = aval_data["_id"].split("/")

    n_avaliacoes = 0
    for item in aval_data["avaliacoes"]:
        if "votos_dados" in aval_data["avaliacoes"][item] and aval_data["avaliacoes"][item]["votos_dados"]:
            n_avaliacoes +=1
            
    aval_data["n_avaliacoes"] = str(n_avaliacoes)
    aval_data["n_avaliadores"] = str(len(usersAllowedToRead("evaluation", registry_id, nomeobj)))
    aval_data["data_cri"] = short_datetime(aval_data["data_cri"])
    return aval_data
                    
class NewEvaluationHandler(BaseHandler):
    ''' Inclusão de uma nova avaliação numa comunidade '''

    @tornado.web.authenticated
    @core.model.serviceEnabled('evaluation')
    def get(self, registry_id, tipo):
        user = self.get_current_user()
        
        if isOwner(user, registry_id):
            self._aval = model.Evaluation()
            if tipo=="member":
                self._aval.tipo = "participantes"
                self._comu = core.model.Community().retrieve(registry_id)
                avaliados = self._comu.getMembersList(return_is_owner=False)[1]
                grupos = {}
                for item in self._comu.groups:
                    grupos[item.encode('iso-8859-1')] = [x.encode('iso-8859-1') for x in self._comu.groups[item]]
                groupnames = {}
                for grupo in grupos:  
                    groupnames[grupo.encode('iso-8859-1')] = grupo.encode('iso-8859-1') 
                
            else:       # tipo =="wiki"
                self._aval.tipo = u"páginas"
                avaliados = [row.key[1].split("/")[1] for row in wiki.database.WIKI.view('wiki/partial_data',startkey=[registry_id],endkey=[registry_id, {}]) if row.value["is_folder"]!="S" and not row.value["removido"]]
                (grupos, groupnames) = wiki.model.Wiki.listWikiFolderItens(registry_id, encoding='iso-8859-1')
                
            self.render("modules/evaluation/newevaluation-form.html", MSG="", EVALUATIONDATA=self._aval, \
                                AVALIADOS=avaliados, REGISTRY_ID=registry_id, \
                                GROUPS=grupos, \
                                GROUPNAMES=groupnames, \
                                NOMEPAG=u"Avaliações")

        else:
            self.render("home.html", MSG=u"Você não pode criar avaliação nesta comunidade.", REGISTRY_ID=ifExists(registry_id, user), \
                            NOMEPAG="comunidades")
        """
        for row in TAGS.view('search/tagcloud', group="true"):
            try:
                tag = row.key[1].encode('iso-8859-1')
                resultado[tag] = row.value 
            except Exception as detail:
                # ignora tag com erro (caracteres inválidos)
                #print "tag com erro:", row.key[1]
                pass
        """
                        
            
    @tornado.web.authenticated
    @core.model.serviceEnabled('evaluation')
    def post(self, registry_id, tipo):
        user = self.get_current_user()
        
        msg = ""
        if isOwner(user, registry_id):
            self._aval = model.Evaluation()
            self._aval.nome = self.get_argument("nome","")
            if not self._aval.nome:
                msg += u"Nome da avaliação não informado.<br/>"
            else:
                self._aval.nome = remove_special_chars(remove_diacritics(self._aval.nome.replace(" ","_")))
                if self._aval.nome == "":
                    msg += u"Nome da avaliação inválido.<br/>"
            
            self._aval.descricao = self.get_argument("descricao", "")
            
            if tipo=="member":
                self._aval.tipo = "participantes"
                self._comu = core.model.Community().retrieve(registry_id)
                avaliados = self._comu.participantes
                grupos = self._comu.groups
                groupnames = {}
                for grupo in grupos:  
                    groupnames[grupo] = grupo  
                
            else:       # tipo =="wiki"
                self._aval.tipo = u"páginas"
                avaliados = [row.key[1].split("/")[1] for row in wiki.database.WIKI.view('wiki/partial_data',startkey=[registry_id],endkey=[registry_id, {}]) if row.value["is_folder"]!="S" and not row.value["removido"]]
                (grupos, groupnames) = wiki.model.Wiki.listWikiFolderItens(registry_id)



                
            # qdo colocamos as views passou a dar erro de encoding
            # avaliados = [x.encode("UTF-8") for x in avaliados]
            for item in avaliados:
                if self.get_argument(item,"") == "S":
                    self._aval.avaliados.append(item)
                    
            if not self._aval.avaliados:
                msg += u"Selecione pelo menos um item para ser avaliado.<br/>"
                
            pontuacao = self.get_argument("pontuacao","").strip()
            if pontuacao:
                self._aval.pontuacao = pontuacao.split(",")
            else:
                msg += u"O campo 'Pontuação' não foi preenchido.<br/>"
            self._aval.owner = user
            self._aval.data_cri = str(datetime.now())
            
            self._aval.data_inicio = self.get_argument("data_start","")
            if not self._aval.data_inicio:
                msg += u"O campo 'Data/hora de início' não foi preenchido.<br/>"
            
            self._aval.data_encerramento = self.get_argument("data_end","")
            if not self._aval.data_encerramento:
                msg += u"O campo 'Data/hora de encerramento' não foi preenchido.<br/>"

            if msg:
                self.render("modules/evaluation/newevaluation-form.html", MSG=msg, EVALUATIONDATA=self._aval, \
                                    AVALIADOS=avaliados, REGISTRY_ID=registry_id, \
                                    GROUPS=grupos, \
                                    GROUPNAMES=groupnames, \
                                    NOMEPAG=u"Avaliações")                
            else:
                aval_id = "%s/%s" % (registry_id, self._aval.nome)
                try:
                    self._aval.save(id=aval_id)
                except Exception as detail:
                    self.render("modules/evaluation/newevaluation-form.html", MSG=u"Já existe uma avaliação com este nome", EVALUATIONDATA=self._aval, \
                                    AVALIADOS=avaliados, REGISTRY_ID=registry_id, \
                                    GROUPS=grupos, \
                                    GROUPNAMES=groupnames, \
                                    NOMEPAG=u"Avaliações")
                    return
                    
                log.model.log(user, u'criou a avaliação', objeto=aval_id, tipo="evaluation")
                self.redirect("/evaluation/%s" % registry_id)
                
        else:
            self.render("home.html", MSG=u"Você não pode criar avaliação nesta comunidade.", REGISTRY_ID=ifExists(registry_id, user), \
                            NOMEPAG="comunidades")

class EvaluationEditHandler(BaseHandler):
    ''' Alteração de uma avaliação numa comunidade '''

    @tornado.web.authenticated
    @core.model.serviceEnabled('evaluation')
    def get(self, registry_id, aval):
        user = self.get_current_user()

        if isOwner(user, registry_id):
            aval_id = '/'.join([registry_id,unquote(aval).decode("UTF-8")])
            self._aval = model.Evaluation().retrieve(aval_id)
            if self._aval:            
                links = []
                links.append((u"Alterar permissões desta avaliação", "/static/imagens/icones/permissions32.png", "/permission/evaluation/"+aval_id, "", "", True))     
                
                self.render("modules/evaluation/evaluation-edit.html", MSG="", EVALUATIONDATA=self._aval, \
                                    REGISTRY_ID=registry_id, NOMEPAG=u"Avaliações", LINKS=links)
            else:
                self.render("home.html", MSG=u"Avaliação inexistente.", REGISTRY_ID=registry_id, \
                                NOMEPAG=u"Avaliações")
        else:
            self.render("home.html", MSG=u"Você não pode alterar avaliações nesta comunidade.", REGISTRY_ID=ifExists(registry_id, user), \
                            NOMEPAG="comunidades")
            
    @tornado.web.authenticated
    @core.model.serviceEnabled('evaluation')
    def post(self, registry_id, aval):
        user = self.get_current_user()
        
        if isOwner(user, registry_id):
            aval_id = '/'.join([registry_id,unquote(aval).decode("UTF-8")])
            self._aval = model.Evaluation().retrieve(aval_id)
            if self._aval:            
                msg = ''
                self._aval.data_inicio = self.get_argument("data_inicio","")
                if self._aval.data_inicio == "":
                    msg += u"O campo 'Data/hora de início' não foi preenchido.<br/>"
                self._aval.data_encerramento = self.get_argument("data_encerramento","")
                if self._aval.data_encerramento == "":
                    msg += u"O campo 'Data/hora de encerramento' não foi preenchido.<br/>"
                
                self._aval.descricao = self.get_argument("descricao", "")
                self._aval.data_alt = str(datetime.now())
                if msg:
                    self.render("modules/evaluation/evaluation-edit.html", MSG=msg, EVALUATIONDATA=self._aval, \
                                        REGISTRY_ID=registry_id, NOMEPAG=u"Avaliações")
                    return

                self._aval.save()
                
                log.model.log(user, u'alterou a avaliação', objeto=aval_id, tipo="evaluation")
                self.redirect("/evaluation/%s" % registry_id)

            else:
                self.render("home.html", MSG=u"Avaliação inexistente.", REGISTRY_ID=registry_id, \
                                NOMEPAG=u"Avaliações")
        else:
            self.render("home.html", MSG=u"Você não pode alterar avaliações nesta comunidade.", REGISTRY_ID=ifExists(registry_id, user), \
                            NOMEPAG="comunidades")

            
class ListEvaluationHandler(BaseHandler):
    ''' Lista avaliações de uma comunidade '''

    @tornado.web.authenticated
    @core.model.serviceEnabled('evaluation')
    def get(self, registry_id):
        user = self.get_current_user()
        if isMember(user, registry_id):
            
            aval_data = prepareEvaluations(user, model.Evaluation.listEvaluations(user, registry_id))
            
            links = []
            if isOwner(user, registry_id):
                links.append((u"Nova avaliação de páginas", "/static/imagens/icones/wiki32.png", "/evaluation/new/"+registry_id+"/wiki"))
                links.append((u"Nova avaliação de participantes", "/static/imagens/icones/members32.png", "/evaluation/new/"+registry_id+"/member"))
                links.append(("Votos dos participantes", "/static/imagens/icones/vote32.png", "/evaluation/result/"+registry_id))

            log.model.log(user, u'acessou a lista de avaliações de', objeto=registry_id, tipo="evaluation", news=False)
            self.render("modules/evaluation/evaluation-list.html", EVALUATIONDATA=aval_data, \
                        MSG="", \
                        REGISTRY_ID=registry_id, PERMISSION=isOwner(user,registry_id), \
                        LINKS=links, \
                        NOMEPAG=u"Avaliações")

        else:
            self.render("home.html", MSG=u"Você não é membro desta comunidade.", REGISTRY_ID=ifExists(registry_id, user), \
                            NOMEPAG="comunidades")
            
            
class CommunityResultsHandler(BaseHandler):
    ''' Lista resultados das avaliações de uma comunidade '''

    @tornado.web.authenticated
    @core.model.serviceEnabled('evaluation')
    def get(self, registry_id):
        user = self.get_current_user()        
        if isOwner(user, registry_id):
            avaliacoes = model.Evaluation.listEvaluationsByUser(registry_id)
            
            log.model.log(user, u'acessou os resultados das avaliações de', objeto=registry_id, tipo="evaluation", news=False)
            
            self.render("modules/evaluation/evaluation-votes.html", EVALUATIONRESULTS=avaliacoes, REGISTRY_ID=registry_id, \
                                NOMEPAG=u"Avaliações")

        else:
            self.render("home.html", MSG=u"Você tem autorização para entrar nesta página.", REGISTRY_ID=ifExists(registry_id, user), \
                            NOMEPAG="comunidades")
            

        
class EvaluationResultHandler(BaseHandler):
    ''' Permite que o dono de uma comunidade veja resultados parciais de uma avaliação '''

    @tornado.web.authenticated
    @core.model.serviceEnabled('evaluation')
    def get(self, registry_id, aval):
        user = self.get_current_user()
        if isOwner(user, registry_id):
            aval_id = '/'.join([registry_id,unquote(aval).decode("UTF-8")])
            self._aval = model.Evaluation().retrieve(aval_id)
            if self._aval:            
                aval_data = prepareResults(self._aval.calcResultAvaliacao())
                log.model.log(user, u'acessou o resultado da avaliação', objeto=aval_id, tipo="evaluation", news=False)

                self.render("modules/evaluation/evaluation-result.html", AVALDATA=aval_data, \
                                REGISTRY_ID=registry_id, NOMEPAG=u"Avaliações") 
            else:
                self.render("home.html", MSG=u"Avaliação inexistente.", REGISTRY_ID=registry_id, \
                                NOMEPAG=u"Avaliações")         
        else:
            self.render("home.html", MSG=u"Você não tem permissão para acessar eta página.", REGISTRY_ID=ifExists(registry_id, user), \
                                NOMEPAG=u"Avaliações")         


class EvaluationHandler(BaseHandler):
    ''' Permite que um usuário faça uma avaliação numa comunidade '''

    @tornado.web.authenticated
    @core.model.serviceEnabled('evaluation')
    @libs.permissions.hasReadPermission ('evaluation')     
    def get(self, registry_id, aval):
        user = self.get_current_user()
        aval_id = '/'.join([registry_id,unquote(aval).decode("UTF-8")])
        self._aval = model.Evaluation().retrieve(aval_id)
        if self._aval:            
            #if verificaPeriodo(aval_data["data_inicio"], aval_data["data_encerramento"]):
            if verificaIntervaloDMY(self._aval.data_inicio, self._aval.data_encerramento) == 0:

                if self._aval.alreadyHasEvaluated(user):
                    self.render("home.html", MSG=u"Você já realizou esta avaliação.", REGISTRY_ID=registry_id, \
                                NOMEPAG=u"Avaliações")                    
                else:
                    self._aval.data_inicio = self._aval.data_inicio
                    self._aval.data_encerramento = self._aval.data_encerramento
                    self.render("modules/evaluation/evaluation-form.html", MSG="", \
                                AVALDATA=self._aval, AVAL_ID=aval_id, \
                                REGISTRY_ID=registry_id, \
                                NOMEPAG=u"Avaliações")
            else:
                self.render("home.html", MSG=u"Fora do período de avaliação.", REGISTRY_ID=registry_id, \
                        NOMEPAG=u"Avaliações")
        else:
            self.render("home.html", MSG=u"Avaliação inexistente.", REGISTRY_ID=registry_id, \
                            NOMEPAG=u"Avaliações")         

    @tornado.web.authenticated
    @core.model.serviceEnabled('evaluation')
    @libs.permissions.hasReadPermission ('evaluation')     
    def post(self, registry_id, aval):
        user = self.get_current_user()
        
        aval_id = '/'.join([registry_id,unquote(aval).decode("UTF-8")])
        self._aval = model.Evaluation().retrieve(aval_id)
        if self._aval:            
            #if verificaPeriodo(aval_data["data_inicio"], aval_data["data_encerramento"]):
            if verificaIntervaloDMY(self._aval.data_inicio, self._aval.data_encerramento) == 0:

                if self._aval.alreadyHasEvaluated(user):
                    self.render("home.html", MSG=u"Você já realizou esta avaliação.", REGISTRY_ID=registry_id, \
                                NOMEPAG=u"Avaliações")                    
                else:   
                    # processa a avaliação realizada
                    participantes = core.database.REGISTRY[registry_id]["participantes"]
    
                    opcoes = []
                    for i in range(len(self._aval.pontuacao)):
                        opcao = self.get_argument("opcao%d"%(i+1),"")
                        if not opcao:
                            self.render("modules/evaluation/evaluation-form.html", MSG=u"Alguma opção não foi selecionada.", \
                                AVALDATA=self._aval, PARTICIPANTES=participantes, AVAL_ID=aval_id, REGISTRY_ID=registry_id, \
                                NOMEPAG=u"Avaliações")
                            return
                        else:  
                            opcoes.append(opcao)
                    if len(opcoes) != len(list(set(opcoes))):
                        self.render("modules/evaluation/evaluation-form.html", MSG=u"Alguma opção foi selecionada mais de uma vez.",
                                AVALDATA=self._aval, PARTICIPANTES=participantes, AVAL_ID=aval_id, REGISTRY_ID=registry_id, \
                                NOMEPAG=u"Avaliações")
                        return

                    # atualiza a lista de votos dados pelo usuário
                    if user in self._aval.avaliacoes:
                        self._aval.avaliacoes[user]["votos_dados"] = opcoes
                    else:
                        self._aval.avaliacoes[user] = {
                            "votos_dados": opcoes,
                            "votos_recebidos": 0
                        }
                        
                    # incrementa a pontuação de cada usuário votado
                    pos=0
                    for op in opcoes:
                        if op not in self._aval.avaliacoes:
                            self._aval.avaliacoes[op] = {
                                "votos_dados": [],
                                "votos_recebidos": 0
                            }
                        self._aval.avaliacoes[op]["votos_recebidos"] += int(self._aval.pontuacao[pos])
                        pos += 1
                        
                    self._aval.save()   
                    log.model.log(user, u'realizou a avaliação', objeto=aval_id, tipo="evaluation")
                    
                    aval_data = prepareEvaluations(user, model.Evaluation.listEvaluations(user, registry_id))
                    
                    links = []
                    if isOwner(user, registry_id):
                        links.append((u"Nova avaliação de páginas", "/static/imagens/icones/wiki32.png", "/evaluation/new/"+registry_id+"/wiki"))
                        links.append((u"Nova avaliação de participantes", "/static/imagens/icones/members32.png", "/evaluation/new/"+registry_id+"/member"))
                        links.append(("Votos dos participantes", "/static/imagens/icones/vote32.png", "/evaluation/result/"+registry_id))
        
                    self.render("modules/evaluation/evaluation-list.html", EVALUATIONDATA=aval_data, \
                                MSG=u"Avaliação realizada com sucesso.", \
                                REGISTRY_ID=registry_id, PERMISSION=isOwner(user,registry_id), \
                                LINKS=links, \
                                NOMEPAG=u"Avaliações")
            
            else:
                self.render("home.html", MSG=u"Fora do período de avaliação.", REGISTRY_ID=registry_id, \
                        NOMEPAG=u"Avaliações")

        else:
            self.render("home.html", MSG=u"Avaliação inexistente.", REGISTRY_ID=registry_id, \
                            NOMEPAG=u"Avaliações")         


class EvaluationDeleteHandler(BaseHandler):
    ''' Exclusão de uma avaliação numa comunidade '''

    @tornado.web.authenticated
    @core.model.serviceEnabled('evaluation')
    def get(self, registry_id, aval):
        user = self.get_current_user()
        
        if isOwner(user, registry_id):
            
            aval_id = '/'.join([registry_id,unquote(aval).decode("UTF-8")])
            
            self._aval = model.Evaluation().retrieve(aval_id)
            if self._aval:                    
                self._aval.delete()
                log.model.log(user, u'removeu a avaliação', objeto=aval_id, tipo="none")

            self.redirect("/evaluation/%s" % registry_id)
            
        else:
            self.render("home.html", MSG=u"Você não tem permissão para remover esta avaliação.", REGISTRY_ID=ifExists(registry_id, user), \
                            NOMEPAG="comunidades")
"""
class NewMultipleEvaluationHandler(BaseHandler):
    ''' Inclusão de avaliações em várias comunidades '''

    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        
        aval_data = _EMPTYEVALUATION()
        aval_data["comunidades"] = ""
        self.render("modules/evaluation/multiple-newevaluation-form.html", MSG="", EVALUATIONDATA=aval_data, REGISTRY_ID=user, \
                            NOMEPAG=u"Avaliações")

    @tornado.web.authenticated
    def post(self):
        aval_data = _EMPTYEVALUATION()
        user = self.get_current_user()
        
        msg = ""
           
        aval_data["comunidades"] = self.get_argument("comunidades","")
        nchars = len(aval_data["comunidades"])
        comunidades = []        
        if nchars<2:
            msg+= u"* Digite pelo menos dois caracteres que definam o nome das comunidades.<br/>"
        else:    
            for community_id in core.database.REGISTRY:
                if "passwd" not in core.database.REGISTRY[community_id]:
                    if aval_data["comunidades"] == core.database.REGISTRY[community_id]["name"][:nchars] and \
                       isOwner(user, community_id):
                        comunidades.append(core.database.REGISTRY[community_id]["name"])
        
        if not comunidades:
            msg+= u"* Não existe nenhuma comunidade criada por você com estes nomes.<br/>"
            
        aval_data["nome"] = self.get_argument("nome","")
        if aval_data["nome"] =="":
            msg += u"* Nome da avaliação não preenchido<br/>"
        aval_data["nome"] = remove_special_chars(remove_diacritics(aval_data["nome"].replace(" ","_")))
        if aval_data["nome"]=="":
            msg += u"Nome da avaliação inválido.<br/>"
                
        aval_data["pontuacao"] = self.get_argument("pontuacao","").strip()
        if aval_data["pontuacao"]:
            aval_data["pontuacao"] = aval_data["pontuacao"].split(",")
        else:
            msg += u"* O campo 'Pontuação' não foi preenchido.<br/>"
        aval_data["owner"] = user
        aval_data["data_cri"] = str(datetime.now())
        try:        
            aval_data["data_inicio"] = "%04d-%02d-%02d %02d:%02d:00.000000" % \
                                        (int(self.get_argument("ano1","")), \
                                         int(self.get_argument("mes1","")), \
                                         int(self.get_argument("dia1","")), \
                                         int(self.get_argument("hora1","")),\
                                         int(self.get_argument("min1","")))
            data = time.strptime(aval_data["data_inicio"],"%Y-%m-%d %H:%M:%S.%f")
        except Exception as detail:
            msg += u"* Data de início inválida.<br/>"

        try:        
            aval_data["data_encerramento"] = "%04d-%02d-%02d %02d:%02d:00.000000" % \
                                        (int(self.get_argument("ano2","")), \
                                         int(self.get_argument("mes2","")), \
                                         int(self.get_argument("dia2","")), \
                                         int(self.get_argument("hora2","")),\
                                         int(self.get_argument("min2","")))
            data = time.strptime(aval_data["data_encerramento"],"%Y-%m-%d %H:%M:%S.%f")
        except Exception as detail:
            msg += u"* Data de encerramento inválida.<br/>"
        
        if msg:
            self.render("modules/evaluation/multiple-newevaluation-form.html", MSG=msg, REGISTRY_ID=user, EVALUATIONDATA=aval_data, \
                            NOMEPAG=u"Avaliações")
            return
        
        for community_id in comunidades:
            aval_id = "%s/%s" % (community_id, aval_data["nome"])
            if aval_id not in model.EVALUATION:
                model.EVALUATION[aval_id] = aval_data
                
                log.model.log(user, u'criou a avaliação', objeto=aval_id, tipo="evaluation")
                msg += u"* Criada avaliação %s.<br/>" % aval_id
            else:
                msg += u"* Já existe uma avaliação %s.<br/>" % aval_id

        self.render("home.html", MSG=msg, REGISTRY_ID=user, \
                            NOMEPAG=u"Avaliações")
"""

URL_TO_PAGETITLE.update ({
        "evaluation":  u"Avaliação"
    })
        
HANDLERS.extend([
            #(r"/evaluation/new",                                             NewMultipleEvaluationHandler),
            (r"/evaluation/new/%s/(wiki|member)"    % (NOMEUSERS),           NewEvaluationHandler),
            (r"/evaluation/%s"           % (NOMEUSERS),                      ListEvaluationHandler),
            (r"/evaluation/result/%s"    % (NOMEUSERS),                      CommunityResultsHandler),
            (r"/evaluation/result/%s/%s" % (NOMEUSERS,PAGENAMECHARS),        EvaluationResultHandler),
            (r"/evaluation/%s/%s"        % (NOMEUSERS,PAGENAMECHARS),        EvaluationHandler),
            (r"/evaluation/delete/%s/%s" % (NOMEUSERS,PAGENAMECHARS),        EvaluationDeleteHandler),
            (r"/evaluation/edit/%s/%s" % (NOMEUSERS,PAGENAMECHARS),          EvaluationEditHandler),
    ])
