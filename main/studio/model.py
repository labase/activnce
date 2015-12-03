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
from libs.strformat import remove_diacritics
from libs.images import resizeImage, thumbnail
from libs.permissions import isAllowedToDeleteObject, isAllowedToEditObject
from libs.dateformat import short_datetime


from datetime import datetime
from urllib import quote,unquote
import operator
from operator import itemgetter


class Studio(Document):
    user           = TextField() # usuário que fez o upload do arquivo,
                                 # esta chave era do bd antigo = owner novo (???)
    registry_id    = TextField() # dono do arquivo: usuário ou comunidade
    owner          = TextField() # quem fez upload.
                                 # caso file seja de uma comunidade, owner!=registry_id
    filename       = TextField() # (???)
    description    = TextField()
    type           = IntegerField() # 1 => Personagens/Objetos
                                    # 2 => Cenários
                                    # 3 => Storyboard
                                    # 4 => Games
    url            = TextField()
    tags           = ListField(TextField())
    data_upload    = TextField()
    data_alt       = TextField()
    alterado_por   = TextField()
    comentarios    = ListField(DictField(Schema.build(
                            owner    = TextField(),
                            comment  = TextField(),
                            data_cri = TextField()
                     )))
    acesso_publico = TextField(default="S") # "S" ou "N": indica se o arquivo pode ser acessado
                                            # de fora da plataforma


    @classmethod
    def listStudioFiles(self, user, registry_id, type):
        def _strListSize(values_list, str):
            plural = lambda x: 's' if x!=1 else ''
            if values_list:
                return u"%d %s%s" % (len(values_list), str, plural(len(values_list)))
            else:
                return u"nenhum %s" % str
                
        files = []
        i = 0
        for row in database.STUDIO.view('studio/all_data',startkey=[registry_id],endkey=[registry_id, {}]):
            if row.value["type"] == type:
                (registry_id, file_id) = row.key
                file_data = dict()
                file_data["registry_id"] = registry_id
                file_data["owner"] = row.value["owner"]
                file_data["acesso_publico"] = row.value["acesso_publico"]
                file_data["description"] = row.value["description"]
                file_data["url"] = row.value["url"]
                #file_data["tags"] = row.value["tags"]
                file_data["file_id"] = file_id
                
                # _file = Studio().retrieve(file_id)
                file_data["apagar"] = isAllowedToDeleteObject(user, row.value["owner"], file_id)
                file_data["alterar"] = isAllowedToEditObject(user, row.value["owner"], file_id)
                file_data["data_nofmt"] = row.value["data_alt"]
                file_data["data_alt"] = short_datetime(row.value["data_alt"])
                file_data["alterado_por"] = row.value["alterado_por"]
                file_data["num_comments"] = _strListSize (row.value["comentarios"], u"comentário")
                file_data["i"] = i
                i = i + 1
                
                files.append(file_data)
            
        files = sorted(files, key=itemgetter("data_nofmt"), reverse = True)
        return files
    
    @classmethod
    def listStudioFileNames(self, user, registry_id, type):
        files = []
        for row in database.STUDIO.view('studio/all_data',startkey=[registry_id],endkey=[registry_id, {}]):
            if row.value["type"] == type:
                (registry_id, file_id) = row.key
                files.append(file_id)
        return files

    
    def filesize(self, filename):
        if '_attachments' in self:
            return self['_attachments'][filename]['length']
        else:
            return 0
            
    def getFileInfo(self, user, filename):
        # cria cópia do objeto files preparando-o para envio ao template que lista info de um arquivo
        file_data = self
        if '_attachments' in self:
            file_data["content_type"] = self['_attachments']["imgG.png"]['content_type']
            file_data["length"] = self['_attachments']["imgG.png"]['length']
        else:
            file_data["content_type"] = "Arquivo corrompido."
            file_data["length"] = 0
        return file_data

    def saveFile(self, id, files):
        self.save(id=id)
        
        # cria versões da imagem
        # ícone N -> thumbnail P (imagem recortada) 30X40
        imagem_n = thumbnail(files["arquivo"][0]["body"], "P") 
        if not imagem_n:
            return False

        # ícone P -> thumbnail G (imagem recortada) 120X160
        imagem_p = thumbnail(files["arquivo"][0]["body"], "G")  
        if not imagem_p:
            return False

        # ícone M -> resizeImage P (imagem reduzida) 240X180 preservando aspect ratio original
        imagem_m = resizeImage(files["arquivo"][0]["body"], "P")  
        if not imagem_m:
            return False
        
        # ícone G -> resizeImage G (imagem reduzida) 1024X768 preservando aspect ratio original
        imagem_g = resizeImage(files["arquivo"][0]["body"], "G") 
        if not imagem_g:
            return False
        
        database.STUDIO.put_attachment(database.STUDIO[id],
                                    imagem_n,
                                    "imgN.png",
                                    "image/png")
        database.STUDIO.put_attachment(database.STUDIO[id],
                                    imagem_p,
                                    "imgP.png",
                                    "image/png")
        database.STUDIO.put_attachment(database.STUDIO[id],
                                    imagem_m,
                                    "imgM.png",
                                    "image/png")
        database.STUDIO.put_attachment(database.STUDIO[id],
                                    imagem_g,
                                    "imgG.png",
                                    "image/png")
    
        # atualiza o espaço ocupado por arquivos deste usuário/comunidade
        #_reg = core.model.Registry().retrieve(self.registry_id)
        #_reg.updateUploadSize(len(files["arquivo"][0]["body"]))
        
        # atualiza tabela de tags
        # vai para o tags.model
        data_tag = str(datetime.now())
        for tag in self.tags:
            nome = self.description if self.description else self.filename
            addTag(tag, self.registry_id, self.owner, "studio", id, nome, data_tag)
        return True
    
    def deleteFile(self):
        #filename = self.filename
        #filename = filename.replace("%20"," ")  #Corrigindo problema de upload de arquivo com espaço em branco
        #filesize = self.filesize(unquote(filename))
        registry_id = self.registry_id

        try:
            tags = self.tags
            self.delete()
        
            # vai para o tags.model
            for tag in tags:
                removeTag(remove_diacritics(tag.lower()), "studio", self.id)
        
        except Exception as detail:
            return (True, detail)
        
        # atualiza o espaço ocupado por arquivos deste usuário/comunidade
        #_reg = core.model.Registry().retrieve(self.registry_id)
        #_reg.updateUploadSize(-filesize)
        return (False, None)
        
    def editFile(self, user, newdesc, newtags, newaccess, newurl):
        # preserva tags anteriores
        old_tags = self.tags
    
        self.description = newdesc
        self.tags = newtags
        self.acesso_publico = newaccess
        self.url = newurl
        self.alterado_por = user
        self.data_alt = str(datetime.now())
        self.save()
    
        # compara as tags anteriores com as modificadas, atualizando a lista de tags no BD
        data_tag = str(datetime.now())
        nome = self.description if self.description else self.filename
        for tag in self.tags:
            if tag not in old_tags:
                addTag(tag, self.registry_id, user, "studio", self.id, nome, data_tag)
    
        for tag in old_tags:
            if tag not in self.tags:
                removeTag(remove_diacritics(tag.lower()), "studio", self.id)
    
    def newFileComment(self, owner, comment):
        self.comentarios.append(dict(
                                  owner = owner,
                                  comment = comment,
                                  data_cri = str(datetime.now())
                                ))
        self.save()
    
    def deleteFileComment(self, comment):
        self.comentarios.remove(comment)
        self.save()
    
    def save(self, id=None, db=database.STUDIO):
        if not self.id and id: self.id = id
        self.store(db)
        
    def retrieve(self, id, db=database.STUDIO):
        return Studio.load(db, id)
    
    def delete(self, db=database.STUDIO):
        #db.delete(self)
        del db[self.id]
        
        