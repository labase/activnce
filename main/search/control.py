# -*- coding: utf-8 -*-
"""
################################################
Plataforma ActivUFRJ
################################################

:Author: *Fernando de Mesentier Silva*
:Contact: fms2005@gmail.com
:Date: $Date: 2010/09/14  $
:Status: This is a "work in progress"
:Revision: $Revision: 0.01 $
:Home: `LABASE `__
:Copyright: ©2009, `GPL 
"""

import tornado.web
import tornado.template

import model
from model import findTag, userTag, cloudTag
import core.model
from core.model import isAUser, isACommunity
import log.model
from core.dispatcher import BaseHandler, HANDLERS,  URL_TO_PAGETITLE, \
                            NOMEUSERS
from libs.strformat import remove_diacritics

from datetime import datetime
import operator
from operator import itemgetter


_MAX_RESULTADOS_POR_ITEM = 12
        
        
class SearchTagHandler(BaseHandler):
    ''' Busca de conteudo por tags, usuários e comunidades '''
    
    @tornado.web.authenticated
    def post(self):
        user = self.get_current_user()
        tipo = self.get_argument("tipo","")
        str_busca = self.get_argument("str_busca","")
        
        if str_busca:
            if tipo == "T": # busca por tags
                tags = remove_diacritics(str_busca.lower())
                if tags:
                    resultados_busca = {}
                    for tag in list(set(tags.split(","))):
                        temp_busca = findTag(tag.strip())
                        for item in temp_busca:
                            for tupla in temp_busca[item]:
                                registry_id = tupla[2]
                                # se este item ainda não foi encontrado e ele
                                # não faz parte de uma comunidade privada...
                                #if self.isAllowedToAccess(user, registry_id, display_error=False) and \
                                if core.model.isAllowedToAccess(user, registry_id)==0:
                                    if item not in resultados_busca:
                                        resultados_busca[item] = [tupla]
                                    elif tupla not in resultados_busca[item]:
                                        resultados_busca[item].append(tupla)
        
                    for item in resultados_busca:
                        # ordena pela data não formatada
                        resultados_busca[item].sort(key=itemgetter(4), reverse=True)
                        # limita o número de itens exibidos
                        resultados_busca[item] = resultados_busca[item][:_MAX_RESULTADOS_POR_ITEM]
        
                    totais = [len(resultados_busca[key]) for key in resultados_busca]
                    
                    self.render("modules/search/search-results.html", REGISTRY_ID=user, \
                                           NOMEPAG='busca', \
                                           RESULTADOS=resultados_busca, LEGENDA=URL_TO_PAGETITLE, \
                                           NUM_RESULT=sum(totais), \
                                           TAGS_PROCURADAS=str_busca)
                    return
                
            elif tipo == "P": # busca por usuários
                #registry_id = self.get_argument("registry_id","")
                registry_id = str_busca.split(":")[0]
                
                if isAUser(registry_id):
                    self.redirect ("/user/%s"%registry_id)
                    return
                else:
                    #msg = u'Usuário não encontrado.'   
                    msg = 121
                       
            elif tipo == "C": # busca por comunidades
                #registry_id = self.get_argument("registry_id","")
                registry_id = str_busca.split(":")[0]
                
                if isACommunity(registry_id):
                    self.redirect ("/community/%s"%registry_id)
                    return
                else:
                    #msg = u'Comunidade não encontrada.'    
                    msg = 122                   
            else:
                #msg = u'Tipo de busca incorreto.'
                msg = 123

        else:
            #msg = u'Termos de busca não preenchidos.'
            msg = 124
 
        #self.render("popup_msg.html", MSG=msg)
        self.redirect ("/profile/%s?msg=%s" % (user,msg))


class SearchUserTagHandler(BaseHandler):
    ''' Busca de conteudo de um usuário ou comunidade por tags '''
    
    @tornado.web.authenticated
    def get(self, registry_id):
        user = self.get_current_user()
        tags_procuradas = self.get_argument("tags","")
        tags = remove_diacritics(tags_procuradas.lower())

        resultados_busca = {}
        for tag in list(set(tags.split(","))):
            temp_busca = userTag(registry_id, tag)
            
            for item in temp_busca:
                for tupla in temp_busca[item]:
                    #if self.isAllowedToAccess(user, tupla[2], display_error=False) and \
                    if core.model.isAllowedToAccess(user, tupla[2])==0:
                        if item not in resultados_busca:
                            resultados_busca[item] = [tupla]
                        elif tupla not in resultados_busca[item]:
                            resultados_busca[item].append(tupla)

        for item in resultados_busca:
            # ordena pela data não formatada
            resultados_busca[item].sort(key=itemgetter(4), reverse=True)
            # limita o número de itens exibidos
            resultados_busca[item] = resultados_busca[item][:_MAX_RESULTADOS_POR_ITEM]

        totais = [len(resultados_busca[key]) for key in resultados_busca]
        
        self.render("modules/search/user-results.html", REGISTRY_ID=registry_id, \
                               NOMEPAG='busca', \
                               RESULTADOS=resultados_busca, LEGENDA=URL_TO_PAGETITLE, \
                               NUM_RESULT=sum(totais), \
                               TAGS_PROCURADAS=tags_procuradas)


class TagCloudHandler(BaseHandler):
    ''' Exibe tagcloud de um usuário ou comunidade '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    def get(self, registry_id):
        self.render("modules/search/tagcloud.html", NOMEPAG="perfil", \
                    REGISTRY_ID = registry_id, MSG=u"", \
                    TAGCLOUD = cloudTag(registry_id))


URL_TO_PAGETITLE.update ({
        "search": "Busca"
    })

HANDLERS.extend([
            (r"/search",                 SearchTagHandler),
            (r"/search/%s"%NOMEUSERS,    SearchUserTagHandler),
            (r"/tagcloud/%s"%NOMEUSERS,  TagCloudHandler)
        ])
