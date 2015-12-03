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

from uuid import uuid4
from urllib import quote,unquote
import time
from datetime import datetime
import re
import operator
from operator import itemgetter
from datetime import datetime

import tornado.web
from tornado.web import HTTPError
import tornado.template

import model
import database
import core.model
from core.model import isUserOrOwner, isUserOrMember, isFriendOrMember, isACommunity,\
                       isAUser, isOwner, getType
import core.database
from core.database import DB_VERSAO_010
import bookmarks.model
from config import PLATAFORMA_URL
import wiki.database
import log.model
from search.model import addTag, removeTag, splitTags
import permission.model
from core.dispatcher import BaseHandler, HANDLERS, URL_TO_PAGETITLE, \
                            NOMEUSERS, \
                            FILENAMECHARS, PAGENAMECHARS
from libs.notify import Notify
from libs.dateformat import short_datetime, short_date, human_date
from libs.strformat import remove_diacritics, remove_special_chars, mem_size_format
import libs.permissions
from libs.permissions import isAllowedToDeleteObject, isAllowedToComment, isAllowedToDeleteComment, \
                             isAllowedToReadObject, isAllowedToWriteObject, objectOwnerFromService

''' importa definição do tutorial deste módulo, se existir _tutorial.py '''
from config import TUTORIAL
try:
    import _tutorial
except ImportError:
    pass


MAX_NUMBER_OF_UPLOADED_FILES = 100

# Limite de arquivos listados por página
NUM_MAX_FILES = 10

def prepareFolderFiles(user, files, registry_type, privacidade):
    
    def _strListSize(values_list, str):
        plural = lambda x: 's' if x!=1 else ''
        if values_list:
            return u"%d %s%s" % (len(values_list), str, plural(len(values_list)))
        else:
            return u"nenhum %s" % str

    # se houver pelo menos um checkbox, ativa seleção múltipla
    sel_multipla = False
    for file in files:
        file["apagar"]  = isAllowedToDeleteObject(user, file["owner"], file["file_id"])
        file["alterar"] = isAllowedToWriteObject(user, "file", file["registry_id"], nomeobj=file["filename_id"])
        file["ler"]     = isAllowedToReadObject(user, "file", file["registry_id"], nomeobj=file["filename_id"])
        
        file["data_nofmt"] = file["data_alt"]
        file["data_alt"] = short_datetime(file["data_alt"])
        file["num_comments"] = _strListSize (file["comentarios"], u"comentário")
        parent_id = file["registry_id"]+"/"+file["parent_folder"]
        parent = model.Files().retrieve(parent_id)
        
        # Vc só pode mover um item para uma pasta se:
        # vc pode apagar o item e o dono da pasta permite que vc crie items nela.
        file["mover"] = file["apagar"]
        if parent:
            file["mover"] = file["mover"] and isAllowedToWriteObject(user, "file", parent.registry_id, file["parent_folder"])

        if  file["alterar"] and file["mover"]:
            sel_multipla = True

        _perm = permission.model.Permission().retrieve("file/"+file["file_id"])
        if _perm:
            file["escrita"] = _perm.escrita
            file["leitura"] = _perm.leitura
        else:
            file["escrita"] = permission.model.default_permission("W", "file", registry_type, privacidade)
            file["leitura"] = permission.model.default_permission("R", "file", registry_type, privacidade)   
                    
                    
                    
                             
    #files = sorted(files, key=itemgetter("data_nofmt"), reverse = True)
    return (sel_multipla, files)


def prepareFile(user, file_data):
    filename_id = file_data["_id"].split("/")[1]
    file_data["apagar"] = isAllowedToDeleteObject(user, file_data["owner"], file_data["_id"])
    file_data["alterar"] = isAllowedToWriteObject(user, "file", file_data["registry_id"], filename_id)
    file_data["ler"]     = isAllowedToReadObject(user, "file", file_data["registry_id"], nomeobj=filename_id)
    file_data["data_upload"] = short_datetime(file_data["data_upload"])
    file_data["data_alt"] = short_datetime(file_data["data_alt"])
    file_data["comentar"] = isAllowedToComment(user, file_data["_id"], file_data["owner"])
    file_data["length"] = mem_size_format(file_data["length"])
    for comentario in file_data["comentarios"]:
        comentario["comment"] = comentario["comment"].replace("\r\n", "<br/>")
        comentario["apagar"] = isAllowedToDeleteComment(user, file_data["registry_id"], comentario["owner"])
        comentario["data_fmt"] = short_datetime(comentario["data_cri"])
    return file_data

    
class FileListHandler(BaseHandler):
    ''' Exibe lista de arquivos e pastas do registry_id '''
     
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('file')
    def get(self, registry_id):
        user = self.get_current_user()
        folder = self.get_argument("folder","")
        page = int(self.get_argument("page","1"))
        (registry_type, privacidade) = getType(registry_id)
        
        files = []
        # se não estou vendo a pasta raiz...
        if folder:
            folder_id = registry_id+"/"+folder
            self._file = model.Files().retrieve(folder_id)
            if self._file and self._file.is_folder=="S":
                path =  self._file.getFilePath()
                file_count = self._file.countFolderFiles()

                # inclui referência .. para subir na árvore
                files.append(self._file)
                nomefolder = files[0]["filename"]
                files[0]["filename"]      = ".."
                # files[0]["owner"]        = self._file.owner
                # se for usuário, self._file.owner
                # se folder possui owner, folder_owner
                # se for comunidade e folder não possui owner = files[0]["owner"] = owner da comunidade
                if not isACommunity(registry_id):
                    files[0]["owner"] = self._file.owner
                elif files[0]["parent_folder"] == ".." or files[0]["parent_folder"] == "":
                    files[0]["owner"] = core.model.Community().retrieve(registry_id).communityOwner
                #Estava assim.
                #files[0]["owner"]        = ""
                files[0]["file_id"]   = registry_id+"/"+files[0]["parent_folder"]
                files[0]["filename_id"]   = files[0]["parent_folder"]
                files[0]["description"]  = ""
                files[0]["apagar"]       = False
                files[0]["alterar"]      = False
                files[0]["data_alt"]     = ""
                files[0]["data_nofmt"]   = ""
                files[0]["alterado_por"] = ""
                files[0]["registry_id"]  = registry_id
                files[0]["mover"]        = False
                files[0]["num_comments"] = 0
                
                if not isAllowedToReadObject(user, "file", registry_id, folder):
                    raise HTTPError(403)
                    return
                                
            else:
                raise HTTPError(404)
                return
        else:
            path = "/"+registry_id+"/"
            file_count = model.Files.countRootFolderFiles(registry_id)

        (sel_multipla, files) = prepareFolderFiles(user, model.Files.listFolderFiles(user, registry_id, folder, page, NUM_MAX_FILES), registry_type, privacidade)

        # instancia registry para obter quota e espaço alocado
        self._reg = core.model.Registry().retrieve(registry_id)

        links = []
        if isUserOrMember(user, registry_id):
            links.append((u"Criar nova pasta", "/static/imagens/icones/add_folder32.png", "/file/newfolder/"+registry_id+"?folder="+folder))
            links.append((u"Upload de Múltiplos Arquivos", "/static/imagens/icones/upload32.png", "/file/upload2/"+registry_id+"?folder="+folder))
        if folder and (isUserOrOwner(user, registry_id) or user == objectOwnerFromService("file", registry_id, folder)):
            links.append((u"Alterar permissões desta pasta", "/static/imagens/icones/permissions32.png", "/permission/file/"+folder_id, "", "", True))
    
        log.model.log(user, u'listou os arquivos de', objeto=registry_id, tipo="file", news=False)
        self.render("modules/files/files-list.html", NOMEPAG='arquivos', \
                    REGISTRY_ID=registry_id, CRIAR=isUserOrMember(user,registry_id), \
                    FOLDER= folder, PATH=path, \
                    LINKS=links, \
                    UPLOAD_QUOTA=mem_size_format(self._reg.upload_quota), UPLOAD_SIZE=mem_size_format(self._reg.upload_size),\
                    SEL_MULTIPLA=sel_multipla, \
                    FILES=files, FILE_COUNT=file_count,\
                    DEFAULT_PERM = permission.model.default_all_permissions("file", registry_type, privacidade), \
                    PAGE=page, PAGESIZE=NUM_MAX_FILES, \
                    MSG="")


class FileListJsonHandler(BaseHandler):
    ''' Retorna lista de arquivos e pastas de uma pasta de um registry_id '''
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('file')
    def get(self, registry_id):
        
        special_types = { 
                         "video": ["mp4", "ogg", "ogv", "webm"],
                         "image": ["gif", "jpg", "jpeg", "png"]
        }
        user = self.get_current_user()
        folder = self.get_argument("folder","")
        type = self.get_argument("type","")
        
        files = model.Files.listFolderFiles(user, registry_id, folder, 1, 1000, return_all_data=False, include_folders=False)
        if type in special_types:
            self.write({"files": [ file for file in files if file.split(".")[-1].lower() in special_types[type] ]})
            
        else:
            self.write({"files": files})


class FileUploadHandler(BaseHandler):
    ''' Recebimento de arquivos do usuário '''
    
    @tornado.web.authenticated
    @core.model.userOrMember
    @core.model.serviceEnabled('file')
    def get(self, registry_id):
        user = self.get_current_user()
        rows = database.FILES.view('files/partial_data',startkey=[registry_id],endkey=[registry_id, {}])
        if len(rows) >= MAX_NUMBER_OF_UPLOADED_FILES:
            self.render("home.html", NOMEPAG='arquivos', MSG=u"Número máximo de arquivos excedido.")
            return

        self.render("modules/files/upload-form.html", \
                    NOMEPAG='arquivos', REGISTRY_ID=registry_id, MSG="")

    @tornado.web.authenticated
    @core.model.userOrMember
    @core.model.serviceEnabled('file')
    def post(self, registry_id):
        user = self.get_current_user()

        if self.request.files:
            
            # este split é para resolver o problema do IE, que manda o caminho completo.
            filename = self.request.files["arquivo"][0]["filename"].split("\\")[-1]
            #filename = remove_diacritics(filename)
            #filename = filename.replace(" ", "_")
            filename = remove_special_chars(remove_diacritics(filename.replace(" ","_")))
            
            if filename=="":
                msg = u"Nome do arquivo inválido.<br/>"
                self.render("home.html", MSG=msg, \
                            NOMEPAG='arquivos', REGISTRY_ID=registry_id)
                return

            if filename[0]=="_":
                msg = u"Nome do arquivo não pode iniciar com sublinhado (_).<br/>"
                self.render("home.html", MSG=msg, \
                            NOMEPAG='arquivos', REGISTRY_ID=registry_id)
                return

                                
            if registry_id in core.database.REGISTRY:
                if len(self.request.files["arquivo"][0]["body"]) + core.database.REGISTRY[registry_id]["upload_size"] > core.database.REGISTRY[registry_id]["upload_quota"]:
                    self.render("home.html", MSG=u"Espaço para armazenamento de arquivos excedido.", \
                                NOMEPAG='arquivos', REGISTRY_ID=registry_id)
                    return

                # A chave _id do documento no couchdb é nome/arquivo
                file_id = '/'.join([registry_id,filename])

                self._file = model.Files().retrieve(file_id)
                if self._file:
                    self.render("home.html", MSG=u"Já existe um arquivo com este mesmo nome (%s). Remova-o antes de subir com uma nova versão." % file_id, \
                                NOMEPAG='arquivos', REGISTRY_ID=registry_id)
                    return
                else: 
                    self._file = model.Files(file_id=file_id)
                
                self._file.parent_folder = self.get_argument("folder","")
                if self._file.parent_folder!="":
                    parent_id = '/'.join([registry_id,self._file.parent_folder])
                    test_parent_folder = model.Files().retrieve(parent_id)
                    if not test_parent_folder:
                        msg = u"Impossível criar arquivo dentro de uma pasta inexistente (%s)<br/>" % parent_id
                        self.render("home.html", MSG=msg, \
                                    NOMEPAG='arquivos', REGISTRY_ID=registry_id)
                        return
                        
                    elif not isAllowedToWriteObject(user, "file", registry_id, self._file.parent_folder):
                        msg = u"Você não tem permissão para criar arquivos nesta pasta."
                        self.render("home.html", MSG=msg, \
                                    NOMEPAG='arquivos', REGISTRY_ID=registry_id)
                        return

                self._file.description = self.get_argument("description","")
                self._file.tags = splitTags(self.get_argument("tags",""))
                
                self._file.owner = self._file.alterado_por = user
                self._file.registry_id = registry_id
                self._file.data_upload = self._file.data_alt = str(datetime.now())
                self._file.filename = filename
                self._file.saveFile(file_id, self.request.files)

                # inclui o arquivo recem criado na lista de filhos do parent_folder
                if self._file.parent_folder:
                    parent = model.Files().retrieve(registry_id+"/"+self._file.parent_folder)
                    parent.addItemToParent(user, filename)
                
                log.model.log(user, u'criou o arquivo', objeto=file_id, tipo="file")

                self.redirect("/file/%s?folder=%s" % (registry_id, self._file.parent_folder))

            else:
               self.render("home.html", MSG=u"Usuário ou comunidade inexistentes.", \
                           NOMEPAG='arquivos', REGISTRY_ID=user)

        else:
            self.render("home.html", MSG=u"Erro: Arquivo inexistente!", \
                        NOMEPAG='arquivos', REGISTRY_ID=registry_id)


class MultipleFileUploadHandler(BaseHandler):
    ''' Recebimento de múltiplos arquivos do usuário '''
    
    @tornado.web.authenticated
    @core.model.userOrMember
    @core.model.serviceEnabled('file')
    def get(self, registry_id):
        user = self.get_current_user()
        folder = self.get_argument("folder","")
        if folder:
            folder_id = registry_id+"/"+folder
            self._file = model.Files().retrieve(folder_id)
            if self._file and self._file.is_folder=="S":
                path =  self._file.getFilePath()
            else:
                raise HTTPError(404)
                return
        else:
            path = "/"+registry_id+"/"        

        rows = database.FILES.view('files/partial_data',startkey=[registry_id],endkey=[registry_id, {}])
        if len(rows) >= MAX_NUMBER_OF_UPLOADED_FILES:
            self.render("home.html", NOMEPAG='arquivos', MSG=u"Número máximo de arquivos excedido.")
            return
        
        links = []
        links.append(("Lista de Arquivos", "/static/imagens/icones/file32.png", "/file/"+registry_id+"?folder="+folder))
        
        self.render("modules/files/upload-form2.html", \
                    LINKS=links, PATH=path, FOLDER=folder, \
                    NOMEPAG='arquivos', REGISTRY_ID=registry_id, MSG="")

    @tornado.web.authenticated
    @core.model.userOrMember
    @core.model.serviceEnabled('file')
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

                                
            if registry_id in core.database.REGISTRY:
                if len(self.request.files["arquivo"][0]["body"]) + core.database.REGISTRY[registry_id]["upload_size"] > core.database.REGISTRY[registry_id]["upload_quota"]:
                    self.write (dict(status=1, msg=u"Espaço para armazenamento de arquivos excedido."))
                    return

                # A chave _id do documento no couchdb é nome/arquivo
                file_id = '/'.join([registry_id,filename])

                self._file = model.Files().retrieve(file_id)
                if self._file:
                    self.write (dict(status=1, msg=u"Já existe um arquivo com este mesmo nome (%s). Remova-o antes de subir com uma nova versão." % file_id))
                    return
                
                else: 
                    self._file = model.Files(file_id=file_id)
                
                self._file.parent_folder = self.get_argument("folder","")
                print "self._file.parent_folder=", self._file.parent_folder
                
                if self._file.parent_folder!="":
                    parent_id = '/'.join([registry_id,self._file.parent_folder])
                    test_parent_folder = model.Files().retrieve(parent_id)
                    if not test_parent_folder:
                        self.write (dict(status=1, msg=u"Impossível criar arquivo dentro de uma pasta inexistente (%s)" % parent_id))
                        return
                        
                    elif not isAllowedToWriteObject(user, "file", registry_id, self._file.parent_folder):
                        self.write (dict(status=1, msg=u"Você não tem permissão para criar arquivos nesta pasta"))
                        return

                self._file.description = self.get_argument("description","")
                self._file.tags = splitTags(self.get_argument("tags",""))
                
                self._file.owner = self._file.alterado_por = user
                self._file.registry_id = registry_id
                self._file.data_upload = self._file.data_alt = str(datetime.now())
                self._file.filename = filename
                self._file.saveFile(file_id, self.request.files)

                # inclui o arquivo recem criado na lista de filhos do parent_folder
                if self._file.parent_folder:
                    parent = model.Files().retrieve(registry_id+"/"+self._file.parent_folder)
                    parent.addItemToParent(user, filename)
                
                log.model.log(user, u'criou o arquivo', objeto=file_id, tipo="file")

                self.write (dict(status=0, redirect="/file/%s?folder=%s" % (registry_id, self._file.parent_folder)))

            else:
               self.write (dict(status=1, msg=u"Usuário ou comunidade inexistentes."))
                
        else:
            self.write (dict(status=1, msg=u"Erro: Arquivo inexistente!"))


class FileInfoHandler(BaseHandler):
    ''' Exibe informações de um arquivo do usuário '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('file')
    @libs.permissions.hasReadPermission ('file')    
    def get(self, registry_id, filename):
        user = self.get_current_user()
        filename = unquote(filename)
        file_data = dict()
        file_id = '/'.join([registry_id,filename])
        self._file = model.Files().retrieve(file_id)
        if self._file and self._file.is_folder!="S": 
            file_data = prepareFile(user, self._file.getFileInfo(user, filename))

            links = []
            reg = core.model.Registry().retrieve(user)
            if reg and "bookmarks"  in reg.getServices:                              
                links.append(bookmarks.model.Bookmarks.createBookmarkLink(user, "http://"+PLATAFORMA_URL+self.request.path))            
            links.append(("Ver", "/static/imagens/icones/view32.png", "/file/"+file_id+"?disp=inline"))
            links.append(("Baixar", "/static/imagens/icones/down32.png", "/file/"+file_id+"?disp=attachment"))
            if isAllowedToWriteObject(user, "file", registry_id, filename):
                links.append(("Alterar este arquivo", "/static/imagens/icones/edit32.png", "/file/edit/"+file_id))
            if isUserOrOwner(user, registry_id) or user == objectOwnerFromService("file", registry_id, filename):
                links.append((u"Alterar permissões deste arquivo", "/static/imagens/icones/permissions32.png", "/permission/file/"+file_id, "", "", True))     
            if isAllowedToDeleteObject(user, file_data["owner"], file_id):
                links.append(("Remover este arquivo", "/static/imagens/icones/delete32.png", "/file/delete/"+file_id,
                              "return confirm('Deseja realmente remover este Arquivo?');"))
                
            log.model.log(user, u'acessou informações do arquivo', objeto=file_id, tipo="file", news=False)                
            self.render("modules/files/file-info.html", NOMEPAG='arquivos', \
                        REGISTRY_ID=registry_id, \
                        PATH = self._file.getFilePath(), \
                        LINKS=links, \
                        FILE=file_data, MSG="")
        else:
            raise HTTPError(404)


class FileEditHandler(BaseHandler):
    ''' Alteração de arquivos: só permite alterar descrição e tags '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('file')
    @libs.permissions.hasWritePermission ('file')    
    def get(self, registry_id, filename):
        user = self.get_current_user()
        file_id = '/'.join([registry_id,unquote(filename)])
        self._file = model.Files().retrieve(file_id)
        if self._file and self._file.is_folder!="S":
            if isAllowedToWriteObject(user, "file", registry_id, filename):
                links = []
                if isUserOrOwner(user, registry_id) or user == objectOwnerFromService("file", registry_id, filename):
                    links.append((u"Alterar permissões deste arquivo", "/static/imagens/icones/permissions32.png", "/permission/file/"+file_id, "", "", True))     

                self.render("modules/files/file-edit.html", \
                            NOMEPAG='arquivos', REGISTRY_ID=registry_id, \
                            PATH = self._file.getFilePath(), \
                            LINKS=links, \
                            FILE=self._file, MSG="")
        else:
            self.render("home.html", MSG=u"Erro: Arquivo inexistente!", \
                        NOMEPAG='arquivos', REGISTRY_ID=registry_id)

    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('file')
    @libs.permissions.hasWritePermission ('file')    
    def post(self, registry_id, filename):
        user = self.get_current_user()
        file_id = '/'.join([registry_id,unquote(filename)])
        self._file = model.Files().retrieve(file_id)
        if self._file and self._file.is_folder!="S":
            self._file.editFile(user, self.get_argument("description",""), 
                                splitTags(self.get_argument("tags","")))

            log.model.log(user, u'alterou o arquivo', objeto=file_id, tipo="file")
            self.redirect("/file/info/%s" % file_id)
                
        else:
            self.render("home.html", MSG=u"Erro: Arquivo inexistente!", \
                        NOMEPAG='arquivos', REGISTRY_ID=registry_id)


class FileBrowserHandler(BaseHandler):
    ''' Browse de arquivos do usuário: Opção 'localizar no servidor' do CKEditor '''
    
    @core.model.allowedToAccess
    @core.model.serviceEnabled('file')
    def get(self, registry_id):
        user = self.get_current_user()
        filter = self.get_argument('filter','')
        image_exts = ('.jpg','.jpeg','.png','.bmp','.gif','.tif')
        
        # retorna apenas arquivos flash        
        if filter=='flash':
            #tipo = "Flash"
            titulo = "Arquivos Flash"
            exts = ('.swf')
        # retorna apenas imagens
        elif filter=='' or filter=='image':
            #tipo = "Imagem"
            titulo = "Imagens"
            exts = image_exts
            
        # retorna todos os arquivos e páginas            
        elif filter=='wiki':  
            titulo = u"Todos os arquivos e páginas"
            exts = []            
        
        # retorna todos os arquivos
        else:       # filter == 'all' ou qq outro valor
            #tipo = "All"
            titulo = "Todos os arquivos"
            exts = []            

        files = []
        for row in database.FILES.view('files/all_data',startkey=[registry_id],endkey=[registry_id, {}]):
            (registry_id, file_id) = row.key
            if row.value["is_folder"] != "S":
                if not exts or file_id.lower().endswith(exts):
                    files.append(dict(
                                     registry_id = registry_id,
                                     file_id = file_id,
                                     owner = row.value["owner"],
                                     icon = "/file/icon/%s" % file_id,
                                     service = "file"
                    ))
                    if file_id.lower().endswith(image_exts):
                        files[-1]["icon"] = "/file/%s?no_log=1" % file_id
        
        if filter=="wiki":
            for row in wiki.database.WIKI.view('wiki/partial_data',startkey=[registry_id],endkey=[registry_id, {}]):
                (registry_id, file_id) = row.key
                if row.value["is_folder"] != "S":
                    if not exts or file_id.lower().endswith(exts):
                        files.append(dict(
                                         registry_id = registry_id,
                                         file_id = file_id,
                                         owner = row.value["owner"],
                                         icon = "/static/imagens/icones/filetypes/32px/_blank.png",
                                         service = "wiki"
                        ))
                                
        files = sorted(files, key=itemgetter("owner"))
        
        self.render("modules/files/browser-list.html", \
                    REGISTRY_ID=registry_id, \
                    FILES=files, MSG="", TITULO=titulo)



class IconViewHandler(BaseHandler):
    ''' Exibe arquivos do usuário '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('file')
    def get(self, registry_id, filename):
        user = self.get_current_user()
        filename = unquote(filename).lower()
        url = "/static/imagens/icones/filetypes/32px/_blank.png"
        ext = filename.split(".")[-1]
        if ext in ["aac", "ai", "aiff", "avi", "bmp", "c", "cpp", "css", "dat", "dmg", "doc", "docx", "dotx", "dwg", "dxf",\
                   "eps", "exe", "flv", "gif", "h", "hpp", "htm", "html", "ics", "iso", "java", "jpg", "key", "mid", "mp3", "mp4", "mpg",\
                   "odf", "ods", "odt", "otp", "ots", "ott", "pdf", "php", "png", "ppt", "pptx", "psd", "py", "qt", "rar", "rb", "rtf",\
                   "sql", "tga", "tgz", "tiff", "txt", "wav", "xls", "xlsx", "xml", "yml", "zip"]:
            url = "/static/imagens/icones/filetypes/32px/%s.png" % ext
        self.redirect (url)




class FileCommentHandler(BaseHandler):
    ''' Inclusão de um comentário de um arquivo '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('file')
    def post(self, registry_id, filename):
        user = self.get_current_user()
        comentario = self.get_argument("comment","")
        file_id = "/".join([registry_id, unquote(filename)])
        
        self._file = model.Files().retrieve(file_id)
        if self._file:
            if isAllowedToComment(user, file_id, self._file.owner):
                if comentario:
                    self._file.newFileComment(user, comentario)
                    
                    #notifica o dono do post comentado
                    email_msg = "Arquivo: "+file_id+"\n"+\
                                self._file.comentarios[-1]["comment"]+"\n"+\
                                Notify.assinatura(user, registry_id, self._file.comentarios[-1]["data_cri"])+"\n\n"
                    Notify.email_notify(self._file.owner, user, "comentou seu arquivo", \
                                   message=email_msg, \
                                   link="file/info/"+file_id)
                    
                    log.model.log(user, u'comentou o arquivo', objeto=file_id, tipo="file")
                    self.redirect("/file/info/%s" % file_id)
                    
                else:
                    self.render("home.html", MSG=u"O comentário não pode ser vazio.", REGISTRY_ID=registry_id, NOMEPAG='arquivos')
            else:
                raise HTTPError(403)
        else:
            raise HTTPError(404)


class FileDeleteCommentHandler(BaseHandler):
    ''' Apaga um comentário de um Arquivo '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('file')
    def get(self, registry_id, filename):
        user = self.get_current_user()
        owner = self.get_argument("owner","")
        data_cri = self.get_argument("data","")
        
        if isAllowedToDeleteComment(user, registry_id, owner):
            file_id = "/".join([registry_id, unquote(filename)])
            self._file = model.Files().retrieve(file_id)
            if self._file:
                if self._file.deleteFileComment(owner, data_cri):
                    log.model.log(user, u'removeu um comentário do arquivo', objeto=file_id, tipo="file")
                    self.redirect("/file/info/%s#comment" % file_id)
                else:
                    raise HTTPError(404)
            else:
                raise HTTPError(404)
        else:
            raise HTTPError(403)


class FileNewFolderHandler(BaseHandler):
    ''' Criação de uma nova pasta '''

    @tornado.web.authenticated
    @core.model.userOrMember
    @core.model.serviceEnabled('file')
    def get (self, registry_id):
        user = self.get_current_user()
        parent_folder = self.get_argument("folder","")
        if parent_folder:
            parent_id = registry_id+"/"+parent_folder
            self._pai = model.Files().retrieve(parent_id)
            parent_name = self._pai.filename
            
            if not isAllowedToWriteObject(user, "file", registry_id, parent_folder):
                 self.render("home.html", MSG=u"Você não tem permissão para criar arquivos nesta pasta.", \
                        NOMEPAG='arquivos', REGISTRY_ID=registry_id)
                 return
        else:
            parent_name = registry_id+"/"
        
        self._file = model.Files(filename="Nova Pasta", parent_folder=parent_folder, description="")
        self.render("modules/files/newfolder-form.html", NOMEPAG='arquivos', \
                    PARENT_NAME=parent_name, \
                    FILEDATA=self._file, REGISTRY_ID=registry_id, MSG="")
        
    @tornado.web.authenticated
    @core.model.userOrMember
    @core.model.serviceEnabled('file')
    def post(self, registry_id):
        msg = ""
        user = self.get_current_user()

        filename = self.get_argument("filename","")
        if filename=="":
            msg += u"Nome de pasta não preenchido<br/>"
            
        elif "/" in filename:
            msg += u"Nome de pasta não pode conter o caractere '/'<br/>"
            
        elif model.Files.filenameExists(registry_id, filename):
            msg += u"Já existe um arquivo ou pasta com este nome<br/>"
            
        self._file = model.Files(filename=filename)
        self._file.is_folder = "S"
        parent_folder = self.get_argument("parent_folder","")
        if parent_folder != "":
            parent_id = '/'.join([registry_id,parent_folder])
            test_parent_folder = model.Files().retrieve(parent_id)
            if not test_parent_folder:
                msg += u"Impossível criar pasta em baixo de uma pasta inexistente (%s)<br/>" % parent_id
            elif not isAllowedToWriteObject(user, "file", registry_id, parent_folder):
                msg += u"Você não tem permissão para criar arquivos nesta pasta."

        self._file.parent_folder = parent_folder

        #self._file.tags = splitTags(self.get_argument("tags",""))
        
        if msg:
            if parent_folder:
                self._pai = model.Files().retrieve(registry_id+"/"+parent_folder)
                parent_name = self._pai.filename
            else:
                parent_name = registry_id+"/"

            self.render("modules/files/newfolder-form.html", NOMEPAG='arquivos', \
                    PARENT_NAME=parent_name, \
                    REGISTRY_ID=registry_id, FILEDATA=self._file, MSG=msg)
            
        else:
            filename_id = uuid4().hex
            file_id = '/'.join([registry_id,filename_id])
            self._file.filename = filename
            self._file.user = user
            self._file.owner = user
            self._file.registry_id = registry_id
            self._file.data_upload = str(datetime.now())
            self._file.alterado_por = user
            self._file.data_alt = self._file.data_upload
            
            self._file.saveFile(id=file_id, files=[], attachment=False)

            # inclui a pasta recem criada na lista de filhos do pai
            if parent_folder:
                parent = model.Files().retrieve(registry_id+"/"+parent_folder)
                parent.addItemToParent(user, filename_id)
            
            log.model.log(user, u'criou a pasta', objeto=registry_id+"/"+self._file.filename, link="/file/%s?folder=%s"%(registry_id,filename_id), tipo="file")
            self.redirect("/file/%s?folder=%s" % (registry_id, parent_folder))


class FileDeleteHandler(BaseHandler):
    ''' Apaga arquivos/pastas do usuário '''
    
    @tornado.web.authenticated
    @core.model.userOrMember
    @core.model.serviceEnabled('file')
    def get(self, registry_id, filename):
        user = self.get_current_user()
        
        file_id = '/'.join([registry_id,unquote(filename)])
        self._file = model.Files().retrieve(file_id)
        
        if self._file != None:
            if registry_id in core.database.REGISTRY:
                # salva variáveis para poder ter acesso a elas depois de remover do banco
                filename = self._file.filename
                file_owner = self._file.owner
                is_folder = self._file.is_folder

                legenda = "pasta" if self._file.is_folder=="S" else u"arquivo"
                
                if not isAllowedToDeleteObject(user, file_owner, file_id):
                    self.render("home.html", MSG=u"Você não tem permissão para remover este arquivo.", \
                                NOMEPAG='arquivos', REGISTRY_ID=registry_id)
                    return
                
                if self._file.is_folder=="S" and self._file.folder_items!=[]:
                    self.render("home.html", MSG=u"Você não pode apagar uma pasta que não esteja vazia.", \
                                NOMEPAG='arquivos', REGISTRY_ID=registry_id)
                    return
                
                parent_folder = self._file.parent_folder 
                (error, detail) = self._file.deleteFile(user)
                if error:
                    self.render("home.html", MSG=u"Erro: %s" % detail, \
                                NOMEPAG='arquivos', REGISTRY_ID=registry_id)
                    return

                # notifica o dono do arquivo excluído
                email_msg = legenda + " removido(a): "+file_id+"\n"+\
                            Notify.assinatura(user, registry_id, str(datetime.now()))+"\n\n"
                Notify.email_notify(file_owner, user, u"removeu %s"%legenda, \
                               message=email_msg, \
                               link="file/"+registry_id)
                                
                #log.model.log(user, u'removeu '+legenda, objeto=file_id, tipo="none")
                if is_folder=="S":
                    log.model.log(user, u'removeu a pasta', objeto=registry_id+"/"+filename, tipo="none")
                else:
                    log.model.log(user, u'removeu o arquivo', objeto=file_id, tipo="none")
                        
                self.redirect("/file/%s" % registry_id)
                return
            else:
                raise HTTPError(404)      
        else:
            raise HTTPError(404)


class FileDeleteAllHandler(BaseHandler):
    ''' Apaga vários arquivos/pastas em files '''

    @tornado.web.authenticated
    @core.model.userOrMember
    @core.model.serviceEnabled('file')
    def post(self, registry_id):
        user = self.get_current_user()
        if "items" not in self.request.arguments:
            msg = u"Arquivo a ser excluído não foi selecionado.<br/>"
            self.render("popup_msg.html", MSG=msg, REGISTRY_ID=registry_id)
            return
        
        items = self.request.arguments["items"] # items é uma lista
        folder = self.get_argument("folder", "")
        
        for item in items:
        
            file_id = '/'.join([registry_id,unquote(item)])
            self._file = model.Files().retrieve(file_id)
            
            if self._file != None:
                # salva variáveis para poder ter acesso a elas depois de remover do banco
                filename = self._file.filename
                file_owner = self._file.owner
                is_folder = self._file.is_folder
                
                legenda = "pasta" if self._file.is_folder=="S" else u"arquivo"
                if isAllowedToDeleteObject(user, file_owner, file_id):
                    
                    if self._file.is_folder=="S" and self._file.folder_items!=[]:
                        # Você não pode apagar uma pasta que não esteja vazia.
                        continue
                    parent_folder = self._file.parent_folder 
                    (error, detail) = self._file.deleteFile(user)

                    # notifica o dono do arquivo excluído
                    email_msg = legenda + u" removido(a): "+file_id+"\n"+\
                                Notify.assinatura(user, registry_id, str(datetime.now()))+"\n\n"
                    Notify.email_notify(file_owner, user, u"removeu %s "%legenda, \
                                   message=email_msg, \
                                   link="file/"+registry_id)

                    #log.model.log(user, u'removeu '+legenda, objeto=file_id, tipo="none")
                    if is_folder=="S":
                        log.model.log(user, u'removeu a pasta', objeto=registry_id+"/"+filename, tipo="none")
                    else:
                        log.model.log(user, u'removeu o arquivo', objeto=file_id, tipo="none")
        self.redirect("/file/%s?folder=%s" % (registry_id, folder) )

class FileMoveHandler(BaseHandler):
    ''' Move arquivo ou pasta entre pastas de files '''

    @tornado.web.authenticated
    @core.model.userOrMember
    @core.model.serviceEnabled('file')
    def get (self, registry_id, filename_id):
        user = self.get_current_user()
        file_id = '/'.join([registry_id, filename_id])
        self._file = model.Files().retrieve(file_id)
        
        if self._file: 
            if isAllowedToWriteObject(user, "file", registry_id, filename_id):
                
                self.render("modules/files/file-move.html", NOMEPAG='arquivos', \
                            PATH = self._file.getFilePath(links=False), \
                            FOLDERS = model.Files.listFolders(user, registry_id, "files/all_data"), \
                            REGISTRY_ID=registry_id, FILEDATA=self._file, \
                            MSG="")
            else:
                raise HTTPError(403)
        else:
            raise HTTPError(404)

   
    @tornado.web.authenticated
    @core.model.userOrMember
    @core.model.serviceEnabled('file')
    def post(self, registry_id, filename_id):
        user = self.get_current_user()
        file_id = '/'.join([registry_id, filename_id])
        self._file = model.Files().retrieve(file_id)
        
        if self._file: 
            old_parent = self._file.parent_folder
            new_parent = self.get_argument("destino","")
            
            if new_parent!="":
                parent_id = '/'.join([registry_id,new_parent])
                test_parent_folder = model.Files().retrieve(parent_id)
                if not test_parent_folder:
                    msg = u"Impossível mover objetos para pasta inexistente (%s)<br/>" % test_parent_folder.filename
                    self.render("popup_msg.html", MSG=msg, REGISTRY_ID=registry_id)
                    return

                elif not isAllowedToWriteObject(user, "file", registry_id, new_parent):
                    msg = u"Você não tem permissão para mover objetos para esta pasta."
                    self.render("popup_msg.html", MSG=msg, REGISTRY_ID=registry_id)
                    return
            
            old_path = self._file.getFilePath(links=False, includefolder=False)
            self._file.moveFile (registry_id, user, old_parent, new_parent)
            new_path = self._file.getFilePath(links=False, includefolder=False)
            
            # notifica o dono do arquivo movido
            legenda = "pasta" if self._file.is_folder=="S" else u"arquivo"
            email_msg = legenda+u" movido(a): "+self._file.filename+"\n"+\
                        u"De: " + old_path + " Para: " + new_path + "\n" +\
                        Notify.assinatura(user, registry_id, self._file.data_alt)+"\n\n"
            Notify.email_notify(self._file.owner, user, u"moveu um(a) " + legenda + u" criado(a) por você", \
                           message=email_msg, \
                           link="/file/%s?folder=%s"%(registry_id, filename_id) if legenda=="pasta" else "file/"+file_id)
            
            #log.model.log(user, u'moveu o arquivo', objeto=file_id, tipo="file")
            if self._file.is_folder=="S":
                log.model.log(user, u'moveu a pasta', objeto=registry_id+"/"+self._file.filename, link="/file/%s?folder=%s"%(registry_id, filename_id), tipo="file")
            else:
                log.model.log(user, u'moveu o arquivo', objeto=file_id, tipo="file")
            
            self.render("popup_msg.html", MSG=u"Arquivo/Pasta movido(a) com sucesso.", REGISTRY_ID=registry_id)
        else:
            self.render("popup_msg.html", MSG=u"Documento não encontrado: provavelmente o mesmo foi removido.", \
                        REGISTRY_ID=registry_id)

class FileMoveAllHandler(BaseHandler):
    ''' Move vários arquivos ou pastas entre pastas de files '''

    @tornado.web.authenticated
    @core.model.userOrMember
    @core.model.serviceEnabled('file')
    def get (self, registry_id):
        user = self.get_current_user()
        folder = self.get_argument("folder","")
        if "items" not in self.request.arguments:
            msg = u"Arquivo a ser movido não foi selecionado.<br/>"
            self.render("popup_msg.html", MSG=msg, REGISTRY_ID=registry_id)
            return
        items = self.request.arguments["items"]
                    
        desc_list = []
        for item in items:
            file_id = '/'.join([registry_id, item])
            self._file = model.Files().retrieve(file_id)
            desc = self._file.getDescendentsList()
            if desc: 
                desc_list.extend(desc)
        select_folders = [ f for f in model.Files.listFolders(user, registry_id, "files/all_data") if f not in desc_list]
        
        if folder:
            file_id = '/'.join([registry_id, folder])
            self._folder = model.Files().retrieve(file_id)
            if self._folder: 
                self.render("modules/files/file-move-all.html", NOMEPAG='arquivos', \
                            PATH=self._folder.getFilePath(links=False), \
                            ITEMS=items, \
                            FOLDER=folder, \
                            FOLDERS=select_folders, \
                            REGISTRY_ID=registry_id, \
                            MSG="")
        else:
            self.render("modules/files/file-move-all.html", NOMEPAG='arquivos', \
                        PATH="/%s/"%registry_id, \
                        ITEMS=items, \
                        FOLDER=folder, \
                        FOLDERS=select_folders, \
                        REGISTRY_ID=registry_id, \
                        MSG="")

   
    @tornado.web.authenticated
    @core.model.userOrMember
    @core.model.serviceEnabled('file')
    def post(self, registry_id):
        user = self.get_current_user()
        old_parent = self.get_argument("folder","")
        if "items" not in self.request.arguments:
            msg = u"Arquivo a ser movido não foi selecionado.<br/>"
            self.render("popup_msg.html", MSG=msg, REGISTRY_ID=registry_id)
            return
        items = self.request.arguments["items"]
        new_parent = self.get_argument("destino","")
            
        if new_parent!="":
            parent_id = '/'.join([registry_id,new_parent])
            test_parent_folder = model.Files().retrieve(parent_id)
            if not test_parent_folder:
                msg = u"Impossível mover objetos para pasta inexistente (%s)<br/>" % test_parent_folder.filename
                self.render("popup_msg.html", MSG=msg, REGISTRY_ID=registry_id)
                return

            elif not isAllowedToWriteObject(user, "file", registry_id, new_parent):
                msg = u"Você não tem permissão para mover objetos para esta pasta."
                self.render("popup_msg.html", MSG=msg, REGISTRY_ID=registry_id)
                return
        
        for item in items:
            file_id = registry_id+"/"+item
            self._file = model.Files().retrieve(file_id)
            
            old_path = self._file.getFilePath(links=False, includefolder=False)
            self._file.moveFile (registry_id, user, old_parent, new_parent)
            new_path = self._file.getFilePath(links=False, includefolder=False)
            
            legenda = "pasta" if self._file.is_folder=="S" else u"arquivo"
            # notifica o dono do arquivo movido
            email_msg = legenda+u" movido(a): "+self._file.filename+"\n"+\
                        u"De: " + old_path + " Para: " + new_path + "\n" +\
                        Notify.assinatura(user, registry_id, self._file.data_alt)+"\n\n"
            Notify.email_notify(self._file.owner, user, u"moveu o(a) " + legenda + u" criado(a) por você", \
                           message=email_msg, \
                           link="/file/%s?folder=%s"%(registry_id, item) if legenda=="pasta" else "file/"+file_id)
            
            
            #log.model.log(user, u'moveu a '+legenda, objeto=file_id, tipo="file")
            if self._file.is_folder=="S":
                log.model.log(user, u'moveu a pasta', objeto=registry_id+"/"+self._file.filename, link="/file/%s?folder=%s"%(registry_id, item), tipo="file")
            else:
                log.model.log(user, u'moveu o arquivo', objeto=file_id, tipo="file")
            
            
        self.render("popup_msg.html", MSG=u"Arquivos/Pastas movidos(as) com sucesso.", REGISTRY_ID=registry_id)


class FolderRenameHandler(BaseHandler):
    ''' Renomeia pasta da Files '''

    @tornado.web.authenticated
    @core.model.userOrMember
    @core.model.serviceEnabled('file')
    def get (self, registry_id, filename_id):
        user = self.get_current_user()
        file_id = '/'.join([registry_id, filename_id])
        self._file = model.Files().retrieve(file_id)
        if self._file: 
            if isAllowedToWriteObject(user, "file", registry_id, filename_id):
                self.render("modules/files/file-rename.html", NOMEPAG='arquivos', \
                            PATH = self._file.getFilePath(links=False), \
                            NEWNAME = "", \
                            REGISTRY_ID=registry_id, FILEDATA=self._file, \
                            MSG="")
            else:
                raise HTTPError(403)
        else:
            raise HTTPError(404)
            
            
    @tornado.web.authenticated
    @core.model.userOrMember
    @core.model.serviceEnabled('file')
    def post(self, registry_id, filename_id):
        user = self.get_current_user()
        file_id = '/'.join([registry_id, filename_id])
        self._file = model.Files().retrieve(file_id)
        if self._file: 
            old_name = self._file.filename
            new_name = self.get_argument("nomepag_novo","")
            if new_name:
                if "/" in new_name:
                    msg = u"* Nome de pasta não pode conter o caractere '/'<br/>"
                    self.render("modules/files/file-rename.html", NOMEPAG='arquivos', \
                                PATH = self._file.getFilePath(links=False), \
                                NEWNAME=new_name, \
                                REGISTRY_ID=registry_id, FILEDATA=self._file, \
                                MSG=msg)
                    
                elif model.Files.filenameExists(registry_id, new_name):
                    msg = u"Já existe um arquivo ou pasta com este nome<br/>"
                    self.render("modules/files/file-rename.html", NOMEPAG='arquivos', \
                                PATH = self._file.getFilePath(links=False), \
                                NEWNAME=new_name, \
                                REGISTRY_ID=registry_id, FILEDATA=self._file, \
                                MSG=msg)

                else:
                    # atualiza nome da pasta
                    self._file.filename = new_name
                    self._file.data_alt = str(datetime.now())
                    self._file.alterado_por = user
                    self._file.save()
                    
                    # notifica o dono do arquivo movida
                    email_msg = u"Pasta renomeada: "+file_id+"\n"+\
                                u"De: " + old_name + " Para: " + new_name + "\n" +\
                                Notify.assinatura(user, registry_id, self._file.data_alt)+"\n\n"
                    Notify.email_notify(self._file.owner, user, u"renomeou uma pasta criada por você", \
                                   message=email_msg, \
                                   link="/file/%s?folder=%s"%(registry_id, filename_id))
                    
                    log.model.log(user, u'renomeou a pasta', objeto=registry_id+"/"+self._file.filename, link="/file/%s?folder=%s"%(registry_id, filename_id), tipo="file")
                    self.render("popup_msg.html", MSG=u"Pasta renomeada com sucesso.", REGISTRY_ID=registry_id)
            else:
                msg = u"Nome da pasta não preenchido."
                self.render("modules/files/file-rename.html", NOMEPAG='arquivos', \
                            PATH = self._file.getFilePath(links=False), \
                            NEWNAME=new_name, \
                            REGISTRY_ID=registry_id, FILEDATA=self._file, \
                            MSG=msg)
                
        else:
            self.render("popup_msg.html", MSG=u"Documento não encontrado: provavelmente o mesmo foi removido.", \
                        REGISTRY_ID=registry_id)
            
            


class FileViewHandler(BaseHandler):
    ''' Exibe um arquivo do usuário '''
    
    @core.model.allowedToAccess
    @core.model.serviceEnabled('file')
    @libs.permissions.hasReadPermission ('file')    
    def get(self, registry_id, filename):
        user = self.get_current_user()
        filename = unquote(filename).split("/")[-1]
        no_log = self.get_argument("no_log","")

        file_id = '/'.join([registry_id,filename])
        self._file = model.Files().retrieve(file_id)
        if self._file and self._file.is_folder!="S":

            # Header content-disposition deve ser inline ou attachment
            disposition = self.get_argument("disp", "inline")

            if '_attachments' not in self._file:
                self.redirect("/file/info/%s/%s" % (registry_id, filename))
                
            self.set_header("Content-Disposition", "%s; filename=%s" % (disposition, filename))
            self.set_header("Content-Type", self._file["_attachments"][filename]['content_type'])
            self.set_header("Content-Length", self._file["_attachments"][filename]['length'])
            if DB_VERSAO_010:
                self.write(database.FILES.get_attachment(file_id, filename, default="Object not found!"))
            else:
                self.write(database.FILES.get_attachment(file_id, filename, default="Object not found!").read())
            
            # não gera log quando o arquivo é exibido no popup "localizar no servidor"
            if no_log=="":
                log.model.log(user, u'acessou o arquivo', objeto=file_id, tipo="file", news=False)                
            
        else:
            raise HTTPError(404)



URL_TO_PAGETITLE.update ({
        "file":   "Arquivos"
    })

HANDLERS.extend([
            (r"/file/%s" % (NOMEUSERS),                                  FileListHandler),
            (r"/file/json/%s" % NOMEUSERS,                               FileListJsonHandler),
            (r"/file/upload2/%s" % (NOMEUSERS),                          MultipleFileUploadHandler),
            (r"/file/upload/%s" % (NOMEUSERS),                           FileUploadHandler),
            (r"/file/info/%s/%s" % (NOMEUSERS, FILENAMECHARS),           FileInfoHandler),
            (r"/file/edit/%s/%s" % (NOMEUSERS, FILENAMECHARS),           FileEditHandler),
            (r"/file/browser/%s" % (NOMEUSERS),                          FileBrowserHandler),
            (r"/file/icon/%s/%s" % (NOMEUSERS, FILENAMECHARS),           IconViewHandler),
            (r"/file/comment/%s/%s" % (NOMEUSERS, FILENAMECHARS),        FileCommentHandler),
            (r"/file/comment/delete/%s/%s" % (NOMEUSERS, FILENAMECHARS), FileDeleteCommentHandler),
            (r"/file/newfolder/%s" % (NOMEUSERS),                        FileNewFolderHandler),
            (r"/file/delete/%s/%s" % (NOMEUSERS, FILENAMECHARS),         FileDeleteHandler),
            (r"/file/delete/%s" % NOMEUSERS,                             FileDeleteAllHandler),
            (r"/file/move/%s/%s" % (NOMEUSERS, FILENAMECHARS),           FileMoveHandler),
            (r"/file/move/%s" % NOMEUSERS,                                          FileMoveAllHandler),
            (r"/file/rename/%s/%s" % (NOMEUSERS, FILENAMECHARS),                    FolderRenameHandler),
            (r"/file/%s/%s" % (NOMEUSERS, FILENAMECHARS),                           FileViewHandler),
            # ignora folder antes do nome do arquivo
            (r"/file/%s/%s/%s" % (NOMEUSERS, FILENAMECHARS[1:-1], FILENAMECHARS),   FileViewHandler)
    ])
