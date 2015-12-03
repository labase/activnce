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

try:
  from couchdb.schema import Document, TextField, IntegerField, LongField, DateTimeField, DictField, ListField, Schema, FloatField
except ImportError:
  from couchdb.mapping import Document, TextField, IntegerField, LongField, DateTimeField, DictField, ListField, FloatField
  from couchdb.mapping import Mapping as Schema

import database
import core.model
from search.model import addTag, removeTag
from libs.strformat import remove_diacritics, str_limit
from libs.dateformat import short_datetime

from datetime import datetime
from urllib import quote,unquote
import operator
from operator import itemgetter


class Files(Document):
    user           = TextField() # usuário que fez o upload do arquivo,
                                 # esta chave era do bd antigo = owner novo (???)
    registry_id    = TextField() # dono do arquivo: usuário ou comunidade
    owner          = TextField() # quem fez upload.
                                 # caso file seja de uma comunidade, owner!=registry_id
    filename       = TextField() # (???)
    description    = TextField()
    tags           = ListField(TextField())
    data_upload    = TextField()
    data_alt       = TextField()
    alterado_por   = TextField()
    comentarios    = ListField(DictField(Schema.build(
                            owner    = TextField(),
                            comment  = TextField(),
                            data_cri = TextField()
                     )))

    # novos atributos para armazenar pastas para Files.
    is_folder       = TextField(default="N") # "S" ou "N": indica se esta entrada corresponde a uma pasta ou arquivo
    parent_folder   = TextField(default="")  # "" indica que esta entrada está na raiz (não tem pasta pai)
    folder_items    = ListField(TextField())
    
    @classmethod
    def listFolderFiles(self, user, registry_id, folder, page, page_size, return_all_data=True, include_folders=True):
    
        files = []
        for row in database.FILES.view('files/folder_data',startkey=[registry_id, folder, {}],endkey=[registry_id, folder], descending="true", skip=(page-1)*page_size , limit=page_size):
            (registry_id, folder, data_upload, file_id) = row.key
            if row.value["is_folder"]!="S" or (row.value["is_folder"]=="S" and include_folders):
                if return_all_data:
                    file_data = dict()
                    file_data.update(row.value)
                    file_data["registry_id"] = registry_id
                    file_data["file_id"] = file_id   #este file_id é o id
                    file_data["filename_id"] = file_id.split("/")[1] #= ao nomepag_id da wiki
                    files.append(file_data)
                else:
                    files.append(file_id.split("/")[1])
        
        return files
    
    @classmethod 
    def countRootFolderFiles(self, registry_id):
        for row in database.FILES.view('files/count_rootfiles',key=registry_id, group="true"):
            return row.value
        return 0

    def countFolderFiles(self):
        return len(self.folder_items)
        
    @classmethod
    def listFolders(self, user, registry_id, view_name):
        folders = [("", "/")]
        for row in database.FILES.view(view_name,startkey=[registry_id],endkey=[registry_id, {}]):
              (registry_id, doc_id) = row.key
              if row.value["is_folder"]=="S":
                  folders.append((doc_id.split("/")[1], str_limit(row.value["filename"], 50)))
        
        #folders = sorted(folders, key=itemgetter("data_nofmt"), reverse = True)
        return folders

    @classmethod
    def filenameExists(self, registry_id, filename):
        # Verifica se já existe algum item (página ou pasta) cadastrado com um determinado nome
        return (database.FILES.view('files/filename_exists',startkey=[registry_id,filename],endkey=[registry_id,filename, {}]))
    

    def filesize(self, filename):
        if '_attachments' in self:
            return self['_attachments'][filename]['length']
        else:
            return 0
            
    def getFileInfo(self, user, filename):
        # cria cópia do objeto files preparando-o para envio ao template que lista info de um arquivo
        file_data = self
        if '_attachments' in self:
            file_data["content_type"] = self['_attachments'][filename]['content_type']
            file_data["length"] = self['_attachments'][filename]['length']
        else:
            file_data["content_type"] = "Arquivo corrompido."
            file_data["length"] = 0
        return file_data

    def getFilePath(self, links=True, includefolder=True, includefile=False):
        # links: indica se o path deve conter links html para cada item do path
        # includefolder: indica se, caso o item seja um folder, deve retornar o caminho até o item inclusive.
        
        path = ""
        
        no = self
        folder = None
        folder_id = None
        while no.parent_folder != "":
            if folder_id != None:
                if links:
                    path = "<a href='/file/%s?folder=%s'>%s</a>/" % (no.registry_id, folder_id, folder) + path
                else:
                    path = folder + "/" + path
            no = Files().retrieve(no.registry_id+"/"+no.parent_folder)
            folder_id = no.id.split("/")[1]
            folder = no.filename
        if folder_id != None:
            if links:
                path = "<a href='/file/%s?folder=%s'>%s</a>/" % (no.registry_id, folder_id, folder) + path
            else:
                path = folder + "/" + path
        if links:
            path = "/<a href='/file/%s'>%s</a>/"%(no.registry_id,no.registry_id) + path
        else:
            path = "/" + no.registry_id + "/" + path
            
        if includefolder and self.is_folder=="S":
            # se o item é um folder, retorna o caminho até o item (inclusive)
            if links:
                path = path + "<a href='/file/%s?folder=%s'>%s</a>" % (no.registry_id, self.id.split("/")[1], self.filename)
            else:
                path = path + self.filename
                
        if includefile and self.is_folder=="N":
            # se o item não é um folder, retorna o caminho até o arquivo (inclusive)
            if links:
                path = path + "<a href='/file/info/%s/%s'>%s</a>" % (no.registry_id, self.id.split("/")[1], self.filename)
            else:
                path = path + self.filename                
        return path


    def getDescendentsList(self):
        lista_desc = []
        no = self
        if no.is_folder=="S":
            lista_desc.append((no.id.split("/")[1], no.filename))
        
            for item in no.folder_items:
                no = Files().retrieve(no.registry_id+"/"+item)
                filhos = no.getDescendentsList()
                if filhos: lista_desc.extend(filhos)
        return lista_desc


    def removeItemFromParent(self, user, item):
        self.folder_items.remove(item)
        self.data_alt = str(datetime.now())
        self.alterado_por = user
        self.save()
    

    def addItemToParent(self, user, item):
        self.folder_items.append(item)
        self.data_alt = str(datetime.now())
        self.alterado_por = user
        self.save()
        

    def saveFile(self, id, files, attachment=True):
        self.save(id=id)
        if attachment:
            database.FILES.put_attachment(database.FILES[id],
                                          files["arquivo"][0]["body"],
                                          self.filename,
                                          files["arquivo"][0]["content_type"])
    
            # atualiza o espaço ocupado por arquivos deste usuário/comunidade
            _reg = core.model.Registry().retrieve(self.registry_id)
            _reg.updateUploadSize(len(files["arquivo"][0]["body"]))
        
        # folders não possuem tags
        if self.is_folder != "S":
            # atualiza tabela de tags
            data_tag = str(datetime.now())
            for tag in self.tags:
                nome = self.description if self.description else self.filename
                addTag(tag, self.registry_id, self.owner, "file", id, nome, data_tag)
        
    def deleteFile(self, user):
        #print "self.filename=", self.filename
        filename = self.filename
        filename = filename.replace("%20"," ")  #Corrigindo problema de upload de arquivo com espaço em branco
        filesize = self.filesize(unquote(filename))
        #print "self.filename=", self.filename
        #print "filesize=", filesize
        registry_id = self.registry_id
        parent = self.parent_folder
        filename_id = self.id.split("/")[1]
        
        try:
            tags = self.tags
            self.delete()
        
            # vai para o tags.model
            for tag in tags:
                removeTag(remove_diacritics(tag.lower()), "file", self.id)
        
        except Exception as detail:
            return (True, detail)
        
        # remove da lista de filhos do pai
        if parent:
            parent_obj = Files().retrieve(registry_id+"/"+parent)
            parent_obj.removeItemFromParent(user, filename_id)
                    
        # atualiza o espaço ocupado por arquivos deste usuário/comunidade
        _reg = core.model.Registry().retrieve(self.registry_id)
        _reg.updateUploadSize(-filesize)
        return (False, None)
        
    def editFile(self, user, newdesc, newtags):
        # preserva tags anteriores
        old_tags = self.tags
    
        self.description = newdesc
        self.tags = newtags
        self.alterado_por = user
        self.data_alt = str(datetime.now())
        self.save()
    
        # compara as tags anteriores com as modificadas, atualizando a lista de tags no BD
        data_tag = str(datetime.now())
        nome = self.description if self.description else self.filename
        for tag in self.tags:
            if tag not in old_tags:
                addTag(tag, self.registry_id, user, "file", self.id, nome, data_tag)
    
        for tag in old_tags:
            if tag not in self.tags:
                removeTag(remove_diacritics(tag.lower()), "file", self.id)
    
    def newFileComment(self, owner, comment):
        self.comentarios.append(dict(
                                  owner = owner,
                                  comment = comment,
                                  data_cri = str(datetime.now())
                                ))
        self.save()
    
    def deleteFileComment(self, owner, data_cri):
        for row in database.FILES.view('files/comment',key=[self.id, owner, data_cri]):
            comentario = dict()
            comentario["comment"] = row.value
            comentario["data_cri"] = data_cri
            comentario["owner"] = owner
            
            self.comentarios.remove(comentario)
            self.save()
            return True
        return False
    
    def moveFile (self, registry_id, user, old_parent, new_parent):
        self.parent_folder = new_parent
        filename_id = self.id.split("/")[1]
        self.save()
        
        if old_parent:
            old = Files().retrieve(registry_id+"/"+old_parent)
            old.removeItemFromParent(user, filename_id)
        
        if new_parent:
            new = Files().retrieve(registry_id+"/"+new_parent)
            new.addItemToParent(user, filename_id)
            
    def save(self, id=None, db=database.FILES):
        if not self.id and id: self.id = id
        self.store(db)
        
    def retrieve(self, id, db=database.FILES):
        return Files.load(db, id)
    
    def delete(self, db=database.FILES):
        #db.delete(self)
        del db[self.id]
        
        