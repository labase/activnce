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
from uuid import uuid4
from urllib import quote,unquote
import operator
from operator import itemgetter

import tornado.web
from tornado.web import HTTPError
import tornado.template

from core.dispatcher import BaseHandler, HANDLERS, URL_TO_PAGETITLE, \
                            NOMEUSERS, \
                            FILENAMECHARS, PAGENAMECHARS, \
                            sortedKeys
import model
import core.model
from core.model import isUserOrOwner
import bookmarks.model
import core.database
import log.model
import files.model
from search.model import addTag, removeTag, splitTags
from libs.notify import Notify
from libs.dateformat import short_datetime
from libs.strformat import str_limit, remove_diacritics, remove_special_chars, remove_html_tags
import libs.permissions
from libs.permissions import isAllowedToDeleteObject, isAllowedToWriteObject, objectOwnerFromService

''' importa definição do tutorial deste módulo, se existir _tutorial.py '''
from config import TUTORIAL
try:
    import _tutorial
except ImportError:
    pass

# Número máximo de questões exibidas na página que lista questões
NUM_MAX_VIDEOAULAS = 20

# Formatos de vídeo suportados pelo HTML5 testados nos seguintes ambientes:
#                          | mp4 | ogv | webm |
# IE 11/Windows 7          |  X  |     |      |
# FF 30/Windows 7          |  X  |  X  |  X   |
# FF 30.0 /Ubuntu 12.04    |  X  |  X  |  X   |
# Chrome/Windows 7         |  X  |  X  |  X   |
# Chromium 34/Ubuntu 12.04 |     |  X  |  X   |
# FF/Android               |     |     |      |
# Safari/Ios               |     |     |      |
# Safari/MacOs             |     |     |      | 

mime_types = {
              "mp4": "video/mp4", 
              "ogg": "video/ogg", 
              "ogv": "video/ogg", 
              "3gp": "video/3gp", 
              "webm": "video/webm"
              }
            
def prepareVideoaulas(user, videoaulas):
    for va in videoaulas:
        va["titulo"] = str_limit(remove_html_tags(va["titulo"]), 200)
        
        # permissões para remover e alterar uma videoaula
        va["alterar"] = isAllowedToWriteObject(user, "videoaula", va["registry_id"], va["name_id"])
        va["apagar"] = isAllowedToDeleteObject(user, va["owner"], va["registry_id"]+"/"+va["name_id"])
        
        # datas formatadas
        va["data_fmt"] = short_datetime(va["data_cri"])
        if "data_alt" in va and va["data_alt"]:
            va["data_alt"] = short_datetime(va["data_alt"])
        
    #return sorted(videoaulas, key=itemgetter("data_cri"), reverse=True)
    return videoaulas
    
    
class VideoAulaListHandler(BaseHandler):
    ''' Lista as videoaulas de um usuario ou comunidade '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('videoaula')
    def get (self, registry_id):
        user = self.get_current_user()
        page = int(self.get_argument("page","1"))
        
        videoaulas_count = model.Videoaula.countObjectsByRegistryId(registry_id)
        lista_videoaulas = prepareVideoaulas(user, model.Videoaula.listObjects(registry_id, page, NUM_MAX_VIDEOAULAS))
        tags_list = model.Videoaula.listAllTags(registry_id)

        links = []    
        if isUserOrOwner(user, registry_id):
            links.append((u"Nova videoaula", "/static/imagens/icones/new32.png", "/videoaula/new/"+registry_id))
         
        log.model.log(user, u'acessou as videoaulas de', objeto=registry_id, tipo="videoaula", news=False)
                 
        self.render("modules/videoaula/videoaula-list.html", NOMEPAG="videoaulas", REGISTRY_ID=registry_id, \
                                              VIDEOAULAS=lista_videoaulas, VIDEOAULAS_COUNT=videoaulas_count, \
                                              PAGE=page, PAGESIZE=NUM_MAX_VIDEOAULAS, \
                                              TITLE=u"Videoaulas de %s" % registry_id, \
                                              TAGS = tags_list, \
                                              LINKS=links)


class VideoAulaTagHandler(BaseHandler):
    ''' Lista as videoaulas de um usuario ou comunidade por uma tag '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('videoaula')
    def get (self, registry_id, tag):
        user = self.get_current_user()
        page = int(self.get_argument("page","1"))
        
        videoaulas_count = model.Videoaula.countObjectsByRegistryIdTags(registry_id, tag)
        lista_videoaulas = prepareVideoaulas(user, model.Videoaula.listObjects(registry_id, page, NUM_MAX_VIDEOAULAS, tag))
        tags_list = model.Videoaula.listAllTags(registry_id)

        links = []    
        if isUserOrOwner(user, registry_id):
            links.append((u"Nova videoaula", "/static/imagens/icones/new32.png", "/videoaula/new/"+registry_id))
         
        log.model.log(user, u'acessou as videoaulas de', objeto=registry_id, tipo="videoaula", news=False)
                 
        self.render("modules/videoaula/videoaula-list.html", NOMEPAG="videoaulas", REGISTRY_ID=registry_id, \
                                              VIDEOAULAS=lista_videoaulas, VIDEOAULAS_COUNT=videoaulas_count, \
                                              PAGE=page, PAGESIZE=NUM_MAX_VIDEOAULAS, \
                                              TITLE=u"Videoaulas de %s com a tag %s" % (registry_id, tag), \
                                              TAGS = tags_list, \
                                              LINKS=links)
      
        
class NewVideoAulaHandler(BaseHandler):
    ''' Inclusão de uma videoaula '''

    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('videoaula')
    @core.model.userOrOwner
    def get (self, registry_id):
        user = self.get_current_user()
        self.render("modules/videoaula/videoaula-form.html",  NOMEPAG="videoaulas", VIDEODATA=model.Videoaula(), \
                    FOLDERS = files.model.Files.listFolders(user, registry_id, "files/all_data"), \
                    REGISTRY_ID=registry_id, MSG="")  

    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('videoaula')
    @core.model.userOrOwner
    def post(self, registry_id):
        user = self.get_current_user()
        _va = model.Videoaula()
        msg = ""
        
        _va.titulo = self.get_argument("name","")
        if _va.titulo == "":
            msg += u"Nome da videoaula não preenchido.<br/>"
                
        _va.arqvideo = self.get_argument("arqvideo","")
        if _va.arqvideo == "":
            msg += u"Arquivo de vídeo não preenchido.<br/>"

        _va.tags = splitTags(self.get_argument("tags",""))

        _va.service = "videoaula"
        _va.type = "videoaula"
        _va.registry_id = registry_id
        _va.name_id = remove_special_chars(remove_diacritics(_va.titulo.replace(" ","_")))

        if model.Videoaula.exists(_va.registry_id, _va.name_id):
            msg += u"Já existe uma videoaula com este nome"

        if msg:
            self.render("modules/videoaula/videoaula-form.html",  NOMEPAG="videoaulas", VIDEODATA=_va, \
                        FOLDERS = files.model.Files.listFolders(user, registry_id, "files/all_data"), \
                        REGISTRY_ID=registry_id, MSG=msg)  
            return
                
        else:
            doc_id = uuid4().hex
            _va.owner = user
            #_va.alterado_por = user

            _va.data_cri = str(datetime.now())
            _va.data_alt = _va.data_cri
            _va.save(id=doc_id)
            
            # Adiciona tags da videoaula ao banco de tags.
            data_tag = str(datetime.now())
            for tag in _va.tags:
                addTag(tag, registry_id, user, "videoaula", registry_id+"/"+_va.name_id, str_limit(remove_html_tags(_va.titulo), 50), data_tag)
            
            log.model.log(user, u'criou videoaula em', objeto=registry_id, tipo="videoaula",link="/videoaula/%s/%s"%(registry_id,_va.name_id))
            self.redirect("/videoaula/edit/%s/%s" % (registry_id,_va.name_id))
        

class EditVideoAulaHandler(BaseHandler):
    ''' Edição de uma videoaula '''

    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('videoaula')
    @libs.permissions.hasWritePermission ("videoaula")
    def get (self, registry_id, name_id):
        user = self.get_current_user()
        _va = model.Videoaula().retrieve_by_name_id(registry_id, name_id)
        if _va:
            ext = _va.arqvideo.split(".")[-1]

            links = []
            if isUserOrOwner(user, registry_id) or user == objectOwnerFromService("videoaula", registry_id, name_id):
                links.append((u"Alterar permissões desta videoaula", "/static/imagens/icones/permissions32.png", "/permission/videoaula/"+registry_id+"/"+name_id, "", "", True))     
            if isAllowedToDeleteObject(user, _va.owner, registry_id+"/"+name_id):
                links.append(("Remover esta videoaula", "/static/imagens/icones/delete32.png", "/videoaula/delete/"+registry_id+"/"+name_id,
                              "return confirm('Deseja realmente remover esta videoaula?');"))            
            self.render("modules/videoaula/videoaula-edit.html", NOMEPAG="videoaulas", VIDEODATA=_va, \
                        FOLDERS = files.model.Files.listFolders(user, registry_id, "files/all_data"), \
                        SORTEDKEYS=sortedKeys, MIME_TYPE=mime_types[ext],            
                        LINKS=links, \
                        REGISTRY_ID=registry_id, MSG="")
        else:
            raise HTTPError(404)
       

    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('videoaula')
    @libs.permissions.hasWritePermission ("videoaula")
    def post(self, registry_id, name_id):
        user = self.get_current_user()
        _va = model.Videoaula().retrieve_by_name_id(registry_id, name_id)
        if _va:
            old_tags = _va.tags
            _va.tags = splitTags(self.get_argument("tags",""))
         
            data_tag = str(datetime.now())
            for tag in _va.tags:
                if tag not in old_tags:
                    addTag(tag, registry_id, user, "videoaula", registry_id+"/"+name_id, str_limit(remove_html_tags(_va.titulo), 50), data_tag)

            for tag in old_tags:
                if tag not in _va.tags:
                    removeTag(remove_diacritics(tag.lower()), "videoaula", id)

            _va.data_alt = str(datetime.now())
            _va.alterado_por = user      
            _va.save()
            
            log.model.log(user, u'alterou uma videoaula de', objeto=registry_id, tipo="videoaula")    
            self.redirect(r"/videoaula/edit/%s/%s" % (registry_id, name_id))       
                         
        else:
            raise HTTPError(404)


class VideoAulaSyncHandler(BaseHandler):
    ''' Inclusão de um slide numa videoaula '''

    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('videoaula')
    @libs.permissions.hasWritePermission ("videoaula")
    def post(self, registry_id, name_id):
        user = self.get_current_user()
        
        # instancia objeto Videoaula a partir de registry_id e name_id
        _va = model.Videoaula.retrieve_by_name_id(registry_id, name_id)
        
        if _va:
            msg = ""
            tempo = self.get_argument("time","")
            slide = self.get_argument("slide","")
                
            if tempo == "":
                msg += u"Tempo não preenchido.<br/>"
                
            if slide == "":
                msg += u"Slide não selecionado.<br/>"
                
            if msg:
                self.write (dict(status=1, result=msg))
                """
                self.render("modules/videoaula/videoaula-edit.html", NOMEPAG="videoaulas", VIDEODATA=_va, \
                            FOLDERS = files.model.Files.listFolders(user, registry_id, "files/all_data"), \
                            SORTEDKEYS=sortedKeys, \
                            REGISTRY_ID=_va.registry_id, MSG=msg)
                """
                
                return

            _va.slides[tempo] = slide
            _va.data_alt = str(datetime.now())
            _va.alterado_por = user      
                        
            _va.save()
            
            log.model.log(user, u'incluiu um slide na videoaula', objeto=_va.registry_id, tipo="videoaula")   
            
            self.write (dict(status=0, result=u"Slide incluído."))
            #self.redirect(r"/videoaula/edit/%s/%s" % (_va.registry_id, _va.name_id))       
                         
        else:
            # videoaula não encontrada
            raise HTTPError(404)
 
 
class VideoAulaDelSyncHandler(BaseHandler):
    ''' Exclusão de um slide de uma videoaula '''

    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('videoaula')
    @libs.permissions.hasWritePermission ("videoaula")
    def get(self, registry_id, name_id):
        user = self.get_current_user()
        
        # instancia objeto Videoaula a partir de registry_id e name_id
        _va = model.Videoaula.retrieve_by_name_id(registry_id, name_id)
        if _va:
            tempo = self.get_argument("time","")
                
            if tempo == "":
                # Bad request
                raise HTTPError(400)  
                return
               
            if tempo in _va.slides:  
                del _va.slides[tempo]
                _va.data_alt = str(datetime.now())
                _va.alterado_por = user      
                            
                _va.save()
                
                log.model.log(user, u'excluiu um slide da videoaula', objeto=_va.registry_id, tipo="videoaula")   
                 
            #self.redirect(r"/videoaula/edit/%s/%s" % (_va.registry_id, _va.name_id))       
            self.write (dict(status=0, result=u"Slide excluído."))      
                  
        else:
            # videoaula não encontrada
            raise HTTPError(404)       
         
        
class VideoAulaDeleteHandler(BaseHandler):
    ''' Apaga uma videoaula '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('videoaula')
    @libs.permissions.hasWritePermission ("videoaula")
    def get(self, registry_id, name_id):
        user = self.get_current_user()
        
        _va = model.Videoaula.retrieve_by_name_id(registry_id, name_id)
        if _va:
            va_owner = _va.owner
            if not isAllowedToDeleteObject(user, va_owner, registry_id+"/"+name_id):
                raise HTTPError(403)
                return

            va_name = str_limit(remove_html_tags(_va.titulo), 200) 
            _va.delete()
            
            # notifica o dono da videoaula excluída
            email_msg = "Videoaula removida: "+va_name+"\n"+\
                        Notify.assinatura(user, registry_id, str(datetime.now()))+"\n\n"
            Notify.email_notify(va_owner, user, u"removeu uma videoaula criada por você", \
                           message=email_msg, \
                           link="videoaula/"+registry_id)
                            
            log.model.log(user, u'removeu uma videoaula de', objeto=registry_id, tipo="videoaula")
            
            self.redirect("/videoaula/%s" % registry_id)
       
        else:
            raise HTTPError(404)
            

class VideoAulaPlayHandler(BaseHandler):
    ''' Exibição de uma videoaula '''

    #@tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('videoaula')
    @libs.permissions.hasReadPermission ("videoaula")
    def get (self, registry_id, name_id):
        user = self.get_current_user()
        _va = model.Videoaula().retrieve_by_name_id(registry_id, name_id)
        if _va:
            ext = _va.arqvideo.split(".")[-1]
            self.render("modules/videoaula/videoaula-play.html", NOMEPAG="videoaulas", VIDEODATA=_va, \
                        SORTEDKEYS=sortedKeys, MIME_TYPE=mime_types[ext], \
                        REGISTRY_ID=registry_id, MSG="")
        else:
            raise HTTPError(404)
        
        
URL_TO_PAGETITLE.update ({
        "videoaula": "Videoaulas"
    })

HANDLERS.extend([
            (r"/videoaula/%s"               % (NOMEUSERS),                     VideoAulaListHandler),
            (r"/videoaula/tag/%s/%s"        % (NOMEUSERS, PAGENAMECHARS),      VideoAulaTagHandler),
            (r"/videoaula/new/%s"           % (NOMEUSERS),                     NewVideoAulaHandler),
            (r"/videoaula/edit/%s/%s"       % (NOMEUSERS, PAGENAMECHARS),      EditVideoAulaHandler),
            (r"/videoaula/sync/%s/%s"       % (NOMEUSERS, PAGENAMECHARS),      VideoAulaSyncHandler),
            (r"/videoaula/delsync/%s/%s"    % (NOMEUSERS, PAGENAMECHARS),      VideoAulaDelSyncHandler),           
            (r"/videoaula/delete/%s/%s"     % (NOMEUSERS, PAGENAMECHARS),      VideoAulaDeleteHandler),
            (r"/videoaula/%s/%s"            % (NOMEUSERS, PAGENAMECHARS),      VideoAulaPlayHandler)
    ])
