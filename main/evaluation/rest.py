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

from urllib import quote,unquote

import tornado.web

import model
import core.model
from core.model import isOwner

import core.database

import log.model
from core.dispatcher import BaseHandler, HANDLERS, \
                            NOMEUSERS, \
                            PAGENAMECHARS
                            
from libs.dateformat import short_datetime
import libs.permissions
from libs.permissions import usersAllowedToRead


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
                    
           
class CommunityResultsHandler(BaseHandler):
    ''' Lista resultados das avaliações de uma comunidade '''

    @tornado.web.authenticated
    @core.model.serviceEnabled('evaluation')
    def get(self, registry_id):
        user = self.get_current_user()        
        if isOwner(user, registry_id):
            avaliacoes = model.Evaluation.listEvaluationsByUser(registry_id)
            
            log.model.log(user, u'acessou os resultados das avaliações de', objeto=registry_id, tipo="evaluation", news=False)
            self.write (dict(status=0, result=avaliacoes))                

        else:
            self.write (dict(status=1, msg=u"Você não tem permissão para acessar esta página."))
            

        
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

                self.write (dict(status=0, result=aval_data))                
            else:
                self.write (dict(status=1, msg=u"Avaliação inexistente."))                  
        else:
            self.write (dict(status=1, msg=u"Você não tem permissão para acessar esta página."))



HANDLERS.extend([
            (r"/rest/evaluation/result/%s"    % (NOMEUSERS),                  CommunityResultsHandler),
            (r"/rest/evaluation/result/%s/%s" % (NOMEUSERS,PAGENAMECHARS),        EvaluationResultHandler)
    ])
