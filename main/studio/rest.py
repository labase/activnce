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
import core.model
from core.database import DB_VERSAO_010
from core.model import isUserOrOwner, isUserOrMember, isFriendOrMember
import core.database

import log.model
from search.model import addTag, removeTag

from core.dispatcher import BaseHandler, HANDLERS, URL_TO_PAGETITLE, \
                            NOMEUSERS, \
                            FILENAMECHARS, PAGENAMECHARS

from libs.notify import Notify
from libs.dateformat import short_datetime, short_date, human_date
from libs.strformat import remove_diacritics, remove_special_chars
from libs.images import resizeImage, thumbnail
from libs.permissions import isAllowedToDeleteObject, isAllowedToEditObject, isAllowedToComment, isAllowedToDeleteComment

from urllib import quote,unquote
import time
from datetime import datetime
import re
from datetime import datetime

MAX_NUMBER_OF_UPLOADED_FILES = 100
_revision = ""

class StudioListHandler(BaseHandler):
    ''' Exibe lista de arquivos do registry_id '''
     
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('studio')
    def get(self, registry_id):
        user = self.get_current_user()
        type = int(self.get_argument("type","1"))
        files = model.Studio.listStudioFileNames(user, registry_id, type)
        self.write (dict(status=0, result=files))

class StudioViewHandler(BaseHandler):
    ''' Exibe um arquivo do usuário '''
    
    @core.model.allowedToAccess
    @core.model.serviceEnabled('studio')
    def get(self, registry_id, filename):
        user = self.get_current_user()
        size = self.get_argument("size","M")
        if size not in ["N", "P", "M", "G"]: size="N"

        filename = unquote(filename)
        file_id = '/'.join([registry_id,filename])
        self._file = model.Studio().retrieve(file_id)
        if self._file != None:
            if not user and self._file.acesso_publico!="S":
                self.redirect ("/?next=/file/"+file_id)
                return

            # Header content-disposition deve ser inline ou attachment
            disposition = self.get_argument("disp", "inline")

            attachname = "img%s.png" % size
            if '_attachments' not in self._file or attachname not in self._file["_attachments"]:
                self.redirect("/file/info/%s/%s" % (registry_id, filename))
            
            self.set_header("Content-Disposition", "%s; filename=%s" % (disposition, attachname))
            self.set_header("Content-Type", self._file["_attachments"][attachname]['content_type'])
            self.set_header("Content-Length", self._file["_attachments"][attachname]['length'])
            if DB_VERSAO_010:
                self.write(database.STUDIO.get_attachment(file_id, attachname, default="Object not found!"))
            else:
                self.write(database.STUDIO.get_attachment(file_id, attachname, default="Object not found!").read())
            
            #log.model.log(user, u'acessou o arquivo', objeto=file_id, tipo="file")    
            
        else:
            self.write (dict(status=1, msg=u"Arquivo não encontrado."))

HANDLERS.extend([
            (r"/rest/studio/%s" % (NOMEUSERS),                                  StudioListHandler),
            (r"/rest/studio/%s/%s" % (NOMEUSERS, FILENAMECHARS),                StudioViewHandler)
    ])