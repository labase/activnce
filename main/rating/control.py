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
from tornado.web import HTTPError
import tornado.template

import model
import database
import core.model

from core.database import DB_VERSAO_010
import log.model

from core.dispatcher import BaseHandler, HANDLERS, URL_TO_PAGETITLE, \
                            NOMEUSERS, \
                            FILENAMECHARS, PAGENAMECHARS
                            
from libs.dateformat import short_datetime
from libs.strformat import remove_diacritics, remove_special_chars
from libs.notify import Notify
import operator
from operator import itemgetter

from urllib import quote,unquote
import time
from datetime import datetime
import re


class ListEvaluationsHandler(BaseHandler):
    ''' Lista todas as avaliações de um objeto  '''

    @tornado.web.authenticated
    @core.model.allowedToAccess
    def get(self, escopo, objeto):
        user = self.get_current_user()
        tipo = self.get_argument("tipo","")
        doc_id = "/".join([escopo, objeto])
        
        avaliacoes = model.Rating.listRatingsFromObject(tipo, escopo, objeto)
        self.render("modules/rating/eval-list.html", MSG="", AVALIACOES=avaliacoes, REGISTRY_ID=escopo, DOC_ID=doc_id, NOMEPAG='paginas')



class NewEvaluationHandler(BaseHandler):
    ''' Usuário avalia um objeto  '''

    @tornado.web.authenticated
    #@core.model.allowedToAccess
    def post(self, escopo, objeto):
        user = self.get_current_user()
        tipo = self.get_argument("tipo","")
        rating = self.get_argument("rating","")
        
        if tipo and rating:
            if not model.Rating.getUserRatingFromObject(user, tipo, escopo, objeto):
                self._rating = model.Rating()
                self._rating.user = user
                self._rating.tipo = tipo
                self._rating.escopo = escopo
                self._rating.objeto = objeto
                self._rating.rating = rating
                self._rating.data_cri = str(datetime.now())
                self._rating.save()
                
                if tipo=="question":
                    log.model.log(user, u'avaliou uma questão de', objeto=escopo, tipo=tipo, link="/question/%s?id=%s"%(escopo,objeto))
                else:
                    log.model.log(user, u'avaliou', objeto=escopo+"/"+objeto, tipo=tipo)
                
                (mean_rating, num_ratings) = model.Rating.getRatingsFromObject(tipo, escopo, objeto)
                self.write("%.1f %i" % (mean_rating, num_ratings))
            else:
                raise HTTPError(400)
        else:
            raise HTTPError(400)



URL_TO_PAGETITLE.update ({
        "rating":   u"Avaliação e Recomendação"
    })

HANDLERS.extend([
            (r"/rating/%s/%s" % (NOMEUSERS, PAGENAMECHARS),         ListEvaluationsHandler),
            (r"/rating/new/%s/%s" % (NOMEUSERS, PAGENAMECHARS),     NewEvaluationHandler)
    ])
