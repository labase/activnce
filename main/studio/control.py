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
import time
from datetime import datetime
import re
from datetime import datetime

import tornado.web
import tornado.template

import model
import database
import core.model
from core.database import DB_VERSAO_010
from core.model import isUserOrOwner, isUserOrMember, isFriendOrMember
import core.database

import log.model
from search.model import addTag, removeTag, splitTags

from core.dispatcher import BaseHandler, HANDLERS, URL_TO_PAGETITLE, \
                            NOMEUSERS, \
                            FILENAMECHARS, PAGENAMECHARS

from libs.notify import Notify
from libs.dateformat import short_datetime, short_date, human_date
from libs.strformat import remove_diacritics, remove_special_chars
from libs.images import resizeImage, thumbnail
from libs.permissions import isAllowedToDeleteObject, isAllowedToEditObject, isAllowedToComment, isAllowedToDeleteComment


''' importa definição do tutorial deste módulo, se existir _tutorial.py '''
from config import TUTORIAL
try:
    import _tutorial
except ImportError:
    pass



MAX_NUMBER_OF_UPLOADED_FILES = 100
_revision = ""


class StudioListHandler(BaseHandler):
    ''' Exibe lista de arquivos do registry_id '''
     
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('studio')
    def get(self, registry_id):
        
        user = self.get_current_user()
        links=[]
        type = self.get_argument("type","1")

        files = model.Studio.listStudioFiles(user, registry_id, int(type))
        if isUserOrMember(user, registry_id):
            links.append((u"Upload de Múltiplos Arquivos", "/static/imagens/icones/upload32.png", "/studio/upload2/"+registry_id+"?type="+type))

        tabs = []
        tabs.append(("Personagens/Objetos", "" if type=="1" else "/studio/%s?type=1"%registry_id))
        tabs.append((u"Cenários",           "" if type=="2" else "/studio/%s?type=2"%registry_id))
        tabs.append(("Storyboard",          "" if type=="3" else "/studio/%s?type=3"%registry_id))
        tabs.append(("Games",               "" if type=="4" else "/studio/%s?type=4"%registry_id))
                
        self.render("modules/studio/files-list.html", NOMEPAG=u'Estúdio', \
                    LINKS=links, REGISTRY_ID=registry_id, CRIAR=isUserOrMember(user,registry_id), \
                    TYPE=type, \
                    TABS=tabs, \
                    FILES=files, MSG="")


class StudioViewHandler(BaseHandler):
    ''' Exibe um arquivo do usuário '''
    
    @core.model.allowedToAccess
    @core.model.serviceEnabled('studio')
    def get(self, registry_id, filename):
        user = self.get_current_user()
        size = self.get_argument("size","M")
        if size not in ["N", "P", "M", "G"]: size="M"

        filename = unquote(filename)
        file_id = '/'.join([registry_id,filename])
        self._file = model.Studio().retrieve(file_id)
        if self._file != None:
            if not user and self._file.acesso_publico!="S":
                self.redirect ("/?next=/studio/"+file_id)
                return

            # Header content-disposition deve ser inline ou attachment
            disposition = self.get_argument("disp", "inline")

            attachname = "img%s.png" % size
            if '_attachments' not in self._file or attachname not in self._file["_attachments"]:
                self.redirect("/studio/info/%s/%s" % (registry_id, filename))
            
            self.set_header("Content-Disposition", "%s; filename=%s" % (disposition, filename))
            self.set_header("Content-Type", self._file["_attachments"][attachname]['content_type'])
            self.set_header("Content-Length", self._file["_attachments"][attachname]['length'])
            if DB_VERSAO_010:
                self.write(database.STUDIO.get_attachment(file_id, attachname, default="Object not found!"))
            else:
                self.write(database.STUDIO.get_attachment(file_id, attachname, default="Object not found!").read())
            
            #log.model.log(user, u'acessou o arquivo', objeto=file_id, tipo="file")    
            
        else:
            self.render("home.html", MSG=u"Arquivo não encontrado.", \
                        NOMEPAG=u'Estúdio', REGISTRY_ID=registry_id)


class StudioInfoHandler(BaseHandler):
    ''' Exibe informações de um arquivo do usuário '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('studio')
    def get(self, registry_id, filename):
        user = self.get_current_user()
        filename = unquote(filename)
        file_data = dict()
        file_id = '/'.join([registry_id,filename])
        self._file = model.Studio().retrieve(file_id)
        
        if self._file != None:
            file_data = self._file.getFileInfo(user, filename)

            file_data["apagar"] = isAllowedToDeleteObject(user, file_data["owner"], file_id)
            file_data["alterar"] = isAllowedToEditObject(user, file_data["owner"], file_id)
            file_data["data_upload"] = short_datetime(file_data["data_upload"])
            file_data["data_alt"] = short_datetime(file_data["data_alt"])
            file_data["comentar"] = isAllowedToComment(user, file_id, file_data["owner"])
            for comentario in file_data["comentarios"]:
                comentario["comment"] = comentario["comment"].replace("\r\n", "<br/>")
                comentario["apagar"] = isAllowedToDeleteComment(user, registry_id, comentario["owner"])
                comentario["data_fmt"] = short_datetime(comentario["data_cri"])
            
            links = []
            links.append(("Ver", "/static/imagens/icones/view32.png", "/studio/"+file_id+"?disp=inline&size=G"))
            links.append(("Baixar", "/static/imagens/icones/down32.png", "/studio/"+file_id+"?disp=attachment&size=G"))
            if isAllowedToEditObject(user, file_data["owner"], file_id):
                links.append(("Alterar este arquivo", "/static/imagens/icones/edit32.png", "/studio/edit/"+file_id))
            if isAllowedToDeleteObject(user, file_data["owner"], file_id):
                links.append(("Remover este arquivo", "/static/imagens/icones/delete32.png", "/studio/delete/"+file_id,
                              "return confirm('Deseja realmente remover este Arquivo?');"))
            self.render("modules/studio/file-info.html", NOMEPAG=u'Estúdio', \
                        REGISTRY_ID=registry_id, \
                        LINKS=links, \
                        FILE=file_data, MSG="")
        else:
            self.render("home.html", MSG=u"Arquivo não encontrado.", \
                        NOMEPAG=u'Estúdio', REGISTRY_ID=registry_id)


class StudioDeleteHandler(BaseHandler):
    ''' Apaga arquivos do usuário '''
    
    @tornado.web.authenticated
    @core.model.serviceEnabled('studio')
    def get(self, registry_id, filename):
        user = self.get_current_user()
        
        file_id = '/'.join([registry_id,unquote(filename)])
        self._file = model.Studio().retrieve(file_id)
        
        if self._file != None:
            if registry_id in core.database.REGISTRY:
                file_owner = self._file.owner
                if not isAllowedToDeleteObject(user, file_owner, file_id):
                    self.render("home.html", MSG=u"Você não tem permissão para remover este arquivo.", \
                                NOMEPAG=u'Estúdio', REGISTRY_ID=registry_id)
                    return

                (error, detail) = self._file.deleteFile()
                if error:
                    self.render("home.html", MSG=u"Erro: %s" % detail, \
                                NOMEPAG=u'Estúdio', REGISTRY_ID=registry_id)
                    return

                # notifica o dono do arquivo excluído
                email_msg = "Arquivo removido: "+file_id+"\n"+\
                            Notify.assinatura(user, registry_id, str(datetime.now()))+"\n\n"
                Notify.email_notify(file_owner, user, u"removeu uma imagem na studio de games", \
                               message=email_msg, \
                               link="studio/"+registry_id)
                                
                log.model.log(user, u'removeu a imagem no studio de games', objeto=file_id, tipo="none")
                
                self.redirect("/studio/%s" % registry_id)
                return
            else:
               msg = u"Usuário ou comunidade inexistentes."
               self.render("home.html", MSG=msg, \
                           NOMEPAG=u'Estúdio', REGISTRY_ID=user)         
        else:
            self.render("home.html", MSG=u"Arquivo não encontrado.", \
                        NOMEPAG=u'Estúdio', REGISTRY_ID=registry_id)


class MultipleStudioUploadHandler(BaseHandler):
    ''' Recebimento de múltiplos arquivos do usuário '''
    
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('studio')
    def get(self, registry_id):
        #rows = database.STUDIO.view('studio/partial_data',startkey=[registry_id],endkey=[registry_id, {}])
        #if len(rows) >= MAX_NUMBER_OF_UPLOADED_FILES:
        #    self.render("home.html", NOMEPAG='paginas', MSG=u"Número máximo de arquivos excedido.")
        #    return
        type = self.get_argument("type","")
        
        tabs = []
        tabs.append(("Personagens/Objetos", "" if type=="1" else "/studio/upload2/%s?type=1"%registry_id))
        tabs.append((u"Cenários",           "" if type=="2" else "/studio/upload2/%s?type=2"%registry_id))
        tabs.append(("Storyboard",          "" if type=="3" else "/studio/upload2/%s?type=3"%registry_id))
        tabs.append(("Games",               "" if type=="4" else "/studio/upload2/%s?type=4"%registry_id))
                
        links = []
        links.append(("Lista de Arquivos", "/static/imagens/icones/file32.png", "/studio/"+registry_id+"?type="+type))
                       
        self.render("modules/studio/upload-form2.html", \
                    LINKS=links, TYPE=type,  \
                    TABS = tabs, \
                    NOMEPAG=u'Estúdio', REGISTRY_ID=registry_id, MSG="")

    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('studio')
    def post(self, registry_id):
        user = self.get_current_user()
        
        if self.request.files:
            
            # este split é para resolver o problema do IE, que manda o caminho completo.
            filename = self.request.files["arquivo"][0]["filename"].split("\\")[-1]
            #filename = remove_diacritics(filename)
            #filename = filename.replace(" ", "_")
            filename = remove_special_chars(remove_diacritics(filename.replace(" ","_")))
            
            if filename=="":
                self.write (dict(status=1, msg=u"Nome do arquivo inválido."))
                return

            if filename[0]=="_":
                self.write (dict(status=1, msg=u"Nome do arquivo não pode iniciar com sublinhado (_)."))
                return

            if "." not in filename or filename.split(".")[-1].lower() not in ["gif", "jpg", "jpeg", "png"]:
                self.write (dict(status=1, msg=u"Utilize somente arquivos com extensão: gif, jpg, jpeg ou png."))
                return
                                
           
            if registry_id in core.database.REGISTRY:
                if not isUserOrMember(user, registry_id):
                     self.write (dict(status=1, MSG=u"Você não tem permissão para carregar arquivos aqui."))
                     return

                # A chave _id do documento no couchdb é nome/arquivo
                file_id = '/'.join([registry_id,filename])

                self._file = model.Studio().retrieve(file_id)
                if self._file:
                    self.write (dict(status=1, MSG=u"Já existe um arquivo com este mesmo nome (%s). Remova-o antes de subir com uma nova versão." % file_id))
                    return
                else: 
                    self._file = model.Studio(file_id=file_id)

                
                if self.get_argument("type","")=="":
                    self.write (dict(status=1, MSG=u"Escolha a fase onde a imagem deve ser armazenada."))
                    return
                 
                self._file.type = int(self.get_argument("type",""))
                self._file.description = self.get_argument("description","")
                self._file.url = self.get_argument("url","")
                self._file.tags = splitTags(self.get_argument("tags",""))
                self._file.owner = self._file.alterado_por = user
                self._file.registry_id = registry_id
                self._file.data_upload = self._file.data_alt = str(datetime.now())
                self._file.filename = filename
                if not self._file.saveFile(file_id, self.request.files):
                    self.write (dict(status=1, MSG=u"Erro na leitura do arquivo de imagem. (%s)" %file_id))
                    return
                
                log.model.log(user, u'criou o arquivo', objeto=file_id, tipo="file")

                self.write (dict(status=0, redirect="/studio/%s" % (registry_id)))

            else:
               self.write (dict(status=1, msg=u"Usuário ou comunidade inexistentes."))
                
        else:
            self.write (dict(status=1, msg=u"Erro: Arquivo inexistente!"))


class StudioUploadHandler(BaseHandler):
    ''' Recebimento de arquivos do usuário '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('studio')
    def get(self, registry_id):
        #rows = database.STUDIO.view('studio/partial_data',startkey=[registry_id],endkey=[registry_id, {}])
        #if len(rows) >= MAX_NUMBER_OF_UPLOADED_FILES:
        #    self.render("home.html", NOMEPAG='paginas', MSG=u"Número máximo de arquivos excedido.")
        #    return

        self.render("modules/studio/upload-form.html", \
                    NOMEPAG=u'Estúdio', REGISTRY_ID=registry_id, MSG="")

    @tornado.web.authenticated
    @core.model.serviceEnabled('studio')
    def post(self, registry_id):
        user = self.get_current_user()

        if self.request.files:
            
            # este split é para resolver o problema do IE, que manda o caminho completo.
            filename = self.request.files["arquivo"][0]["filename"].split("\\")[-1]
            filename = remove_diacritics(filename)
            filename = filename.replace(" ", "_")
            if "." not in filename or filename.split(".")[-1].lower() not in ["gif", "jpg", "jpeg", "png"]:
                self.render("home.html", MSG=u"Utilize somente arquivos com extensão: gif, jpg, jpeg ou png.", \
                            NOMEPAG=u'Estúdio', REGISTRY_ID=registry_id)
                return

            tipo = ""
            if registry_id in core.database.REGISTRY:
                if not isUserOrMember(user, registry_id):
                    self.render("home.html", MSG=u"Você não tem permissão para carregar arquivos aqui.", \
                                NOMEPAG=u'Estúdio', REGISTRY_ID=registry_id)
                    return
                    
                #if len(self.request.files["arquivo"][0]["body"]) + core.database.REGISTRY[registry_id]["upload_size"] > core.database.REGISTRY[registry_id]["upload_quota"]:
                #    self.render("home.html", MSG=u"Espaço para armazenamento de arquivos excedido.", \
                #                NOMEPAG=u'Estúdio', REGISTRY_ID=registry_id)
                #    return

                # A chave _id do documento no couchdb é nome/arquivo
                file_id = '/'.join([registry_id,filename])

                self._file = model.Studio().retrieve(file_id)
                if self._file:
                    self.render("home.html", MSG=u"Já existe um arquivo com este mesmo nome. Remova-o antes de subir com uma nova versão.", \
                                NOMEPAG=u'Estúdio', REGISTRY_ID=registry_id)
                    return
                else: 
                    self._file = model.Studio(file_id=file_id)
                
                if self.get_argument("type","")=="":
                    self.render("home.html", MSG=u"Escolha a fase onde a imagem deve ser armazenada.", \
                                NOMEPAG=u'Estúdio', REGISTRY_ID=registry_id)
                    return
                
                self._file.type = int(self.get_argument("type",""))
                self._file.description = self.get_argument("description","")
                self._file.url = self.get_argument("url","")
                self._file.tags = splitTags(self.get_argument("tags",""))
                self._file.owner = self._file.alterado_por = user
                self._file.registry_id = registry_id
                self._file.data_upload = self._file.data_alt = str(datetime.now())
                self._file.filename = filename
                if not self._file.saveFile(file_id, self.request.files):
                    self.render("home.html", MSG=u"Erro na leitura do arquivo de imagem.", \
                                NOMEPAG=u'Estúdio', REGISTRY_ID=registry_id)
                    return
                    
                log.model.log(user, u'criou imagem no studio de games', objeto=file_id, tipo="studio")

                self.redirect("/studio/%s" % registry_id)

            else:
               self.render("home.html", MSG=u"Usuário ou comunidade inexistentes.", \
                           NOMEPAG=u'Estúdio', REGISTRY_ID=user)

        else:
            self.render("home.html", MSG=u"Erro: Arquivo inexistente!", \
                        NOMEPAG=u'Estúdio', REGISTRY_ID=registry_id)


class StudioEditHandler(BaseHandler):
    ''' Alteração de arquivos: só permite alterar descrição e tags '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('studio')
    def get(self, registry_id, filename):
        user = self.get_current_user()
        file_id = '/'.join([registry_id,unquote(filename)])
        self._file = model.Studio().retrieve(file_id)
        if self._file:
            if isAllowedToEditObject(user, self._file.owner, file_id):
                self.render("modules/studio/file-edit.html", \
                            NOMEPAG=u'Estúdio', REGISTRY_ID=registry_id, \
                            FILE=self._file, MSG="")
        else:
            self.render("home.html", MSG=u"Erro: Arquivo inexistente!", \
                        NOMEPAG=u'Estúdio', REGISTRY_ID=registry_id)

    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('studio')
    def post(self, registry_id, filename):
        
        user = self.get_current_user()
        
        file_id = '/'.join([registry_id,unquote(filename)])

        self._file = model.Studio().retrieve(file_id)
        if self._file:
            if isAllowedToEditObject(user, self._file.owner, file_id):
                
                self._file.editFile(user, self.get_argument("description",""), 
                                    splitTags(self.get_argument("tags","")),
                                    self.get_argument("acesso_publico","S"),
                                    self.get_argument("url",""))

                log.model.log(user, u'alterou imagem do studio de games', objeto=file_id, tipo="studio")
                self.redirect("/studio/info/%s" % file_id)
                
            else:
               self.render("home.html", MSG=u"Você não tem permissão para alterar este arquivo.", \
                           NOMEPAG=u'Estúdio', REGISTRY_ID=user)

        else:
                self.render("home.html", MSG=u"Erro: Arquivo inexistente!", \
                            NOMEPAG=u'Estúdio', REGISTRY_ID=registry_id)


class StudioCommentHandler(BaseHandler):
    ''' Inclusão de um comentário de um arquivo '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('studio')
    def post(self, registry_id, filename):
        user = self.get_current_user()
        comentario = self.get_argument("comment","")
        file_id = "/".join([registry_id, unquote(filename)])
        
        self._file = model.Studio().retrieve(file_id)
        if self._file:
            if isAllowedToComment(user, file_id, self._file.owner):
                if comentario:
                    self._file.newFileComment(user, comentario)
                    
                    # notifica o dono do post comentado
                    email_msg = "Arquivo: "+file_id+"\n"+\
                                self._file.comentarios[-1]["comment"]+"\n"+\
                                Notify.assinatura(user, registry_id, self._file.comentarios[-1]["data_cri"])+"\n\n"
                    Notify.email_notify(self._file.owner, user, "comentou a imagem no studio de games", \
                                   message=email_msg, \
                                   link="studio/info/"+file_id)
                    
                    log.model.log(user, u'comentou a imagem no studio de games', objeto=file_id, tipo="studio")
                    self.redirect("/studio/info/%s" % file_id)
                    
                else:
                    self.render("home.html", MSG=u"O comentário não pode ser vazio.", REGISTRY_ID=registry_id, NOMEPAG=u'Estúdio')
            else:
                self.render("home.html", MSG=u"Você não tem permissão para comentar este arquivo.", REGISTRY_ID=registry_id, NOMEPAG=u'Estúdio')
        else:
            self.render("home.html", MSG=u"Arquivo não encontrado.", REGISTRY_ID=registry_id, NOMEPAG=u'Estúdio')


class StudioDeleteCommentHandler(BaseHandler):
    ''' Apaga um comentário de um Arquivo '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('studio')
    def get(self, registry_id, filename):
        user = self.get_current_user()
        comentario = dict()
        comentario["owner"] = self.get_argument("owner","")
        comentario["data_cri"] = self.get_argument("data","")
        file_id = "/".join([registry_id, unquote(filename)])
        if isAllowedToDeleteComment(user, registry_id, comentario["owner"]):
            
            for row in database.STUDIO.view('studio/comment',key=[file_id, comentario["owner"], comentario["data_cri"]]):
                comentario["comment"] = row.value

                self._file = model.Studio().retrieve(file_id)
                if self._file:
                    self._file.deleteFileComment(comentario)

                    log.model.log(user, u'removeu um comentário da imagem no studio de games', objeto=file_id, tipo="studio")
                    self.redirect("/studio/info/%s#comment" % file_id)
                else:
                    msg = u"Arquivo não encontrado."
                    self.render("home.html", MSG=msg, REGISTRY_ID=registry_id, NOMEPAG=u'Estúdio')
        else:
            msg = u"Você não tem permissão para apagar este comentário."
            self.render("home.html", MSG=msg, REGISTRY_ID=registry_id, NOMEPAG=u'Estúdio')


URL_TO_PAGETITLE.update ({
        "studio":   u"Estúdio"
    })

HANDLERS.extend([
            (r"/studio/upload2/%s" % (NOMEUSERS),                          MultipleStudioUploadHandler),
            (r"/studio/upload/%s" % (NOMEUSERS),                           StudioUploadHandler),
            (r"/studio/info/%s/%s" % (NOMEUSERS, FILENAMECHARS),           StudioInfoHandler),
            (r"/studio/comment/%s/%s" % (NOMEUSERS, FILENAMECHARS),        StudioCommentHandler),
            (r"/studio/comment/delete/%s/%s" % (NOMEUSERS, FILENAMECHARS), StudioDeleteCommentHandler),
            (r"/studio/delete/%s/%s" % (NOMEUSERS, FILENAMECHARS),         StudioDeleteHandler),
            (r"/studio/%s" % (NOMEUSERS),                                  StudioListHandler),
            (r"/studio/%s/%s" % (NOMEUSERS, FILENAMECHARS),                StudioViewHandler),
            (r"/studio/edit/%s/%s" % (NOMEUSERS, FILENAMECHARS),           StudioEditHandler)
    ])
