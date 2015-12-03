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
import core.database

from operator import itemgetter

_DOCBASES = ['task']

class Task(Document):
    # _id = "registry_id/nome_avaliacao"
    nome              = TextField(default="") #Título da avaliação
    #tipo              = TextField() # "participantes" ou "páginas"
    descricao         = TextField(default="") 
    recurso           = TextField(default="") # url do recurso para realização da tarefa
    labvad            = TextField(default="N") # indica se a tarefa deve ser realizada no LabVad
    owner             = TextField() # quem criou a avaliação.
    data_inicio       = TextField() 
    data_encerramento = TextField() 
    valor             = TextField()
    num_arquivos      = TextField()
    data_cri          = TextField() 
    data_alt          = TextField() 
    avaliacoes        = DictField()
    num_participantes = TextField()
    grupo             = TextField()
    # {
    #    <user>: <nota>,
    #    ...
    # }


    @classmethod    
    def listTasks(self, user, registry_id, owner=False):
        lista_tasks = []
        self._comu = core.model.Community().retrieve(registry_id)
        for row in database.TASK.view('task/all_data',startkey=[registry_id],endkey=[registry_id, {}]):
            task = dict()
            task.update(row.value)
            task["_id"] = row.value["_id"]
            grupo = row.value["grupo"]
            if not owner:
                if (grupo != "Todos"):
                    members = self._comu.getMembersList(grupo)[1]
                    for part in members:
                        if user in part[0]:
                            lista_tasks.append(task)
                else:
                    lista_tasks.append(task)
            else:
                lista_tasks.append(task)
        return lista_tasks
    
    @classmethod    
    def TaskConfirm(self, registry_id, task_name):
        existe = False
        for row in database.TASK.view('task/by_id',startkey=[registry_id, task_name],endkey=[registry_id, task_name, {}]):
            existe = True
       
        return existe
                 
    def save(self, id=None, db=database.TASK):
        if not self.id and id: self.id = id
        self.store(db)
        
    def retrieve(self, id, db=database.TASK):
        return Task.load(db, id)
    
    def delete(self, db=database.TASK):
        del db[self.id]

class TaskFiles(Document):
    # chave = registry_id/task_id/user
    registry_id    = TextField() # dono do arquivo: usuário ou comunidade
    owner          = TextField() # quem fez upload.
    filenames      = ListField(ListField(TextField())) # lista de tuplas com (nomes do arquivo, data upload, comentario)
    #filename       = TextField()
    data_upload    = TextField()
    data_alt       = TextField()
    alterado_por   = TextField()
    nota           = TextField()
    task           = TextField()
    nome_grupo     = TextField()
    participantes  = ListField(TextField())
    participantes_pendentes  = ListField(TextField())
    comentarios    = ListField(DictField(Schema.build(
                            owner    = TextField(),
                            comment  = TextField(),
                            data_cri = TextField()
                     )))

    
    @classmethod
    def getGroupId(self, registry_id, task, nome_grupo):
        
        for group in database.TASKFILES.view('taskfiles/by_group',startkey=[registry_id, task, nome_grupo],endkey=[registry_id, task, nome_grupo, {}]):
            (comunidade_id, tarefa_id, owner) = group.id.split("/") 
            file_data = dict()             
            file_data["comunidade_id"] = comunidade_id
            file_data["tarefa_id"] =  tarefa_id #este file_id é o id
            file_data["owner"] = owner
        return file_data
    
    @classmethod
    def getGroupName(self, registry_id, task, user): 
        meu_grupo=""
        for part in database.TASKFILES.view('taskfiles/by_participante',startkey=[registry_id, task, user],endkey=[registry_id, task, user, {}]):
            meu_grupo = part.value["group"]
        return meu_grupo
    
    
    @classmethod
    def getGroupFileId(self, registry_id, task, meu_grupo):
        file_id = "-1"
        for group in database.TASKFILES.view('taskfiles/by_group',startkey=[registry_id, task, meu_grupo],endkey=[registry_id, task, meu_grupo, {}]):
            file_id = group.value["id"]
        return file_id
    
    
    @classmethod
    def getOwnerByParticipant(self, registry_id, task, user):
        owner = ""
        meu_id =""
        for part in database.TASKFILES.view('taskfiles/by_participante',startkey=[registry_id, task, user],endkey=[registry_id, task, user, {}]):
            meu_id    = part.value["id"]
        
        if(meu_id):
            (comunidade_id, tarefa_id, owner) = meu_id.split("/")
        return owner
    
       
    @classmethod
    def getGroupsAndParticipants(self, registry_id, task):
        participantes_por_grupos = dict()
        for row in database.TASKFILES.view('taskfiles/by_task',startkey=[registry_id, task],endkey=[registry_id, task, {}]):
            participantes_por_grupos[row.value["nome_grupo"]] = row.value["participantes"]
        return participantes_por_grupos
    
    @classmethod
    def getGroupsByPending(self, registry_id, task, user):
        group_names = []
        for row in database.TASKFILES.view('taskfiles/by_participantes_pendentes',startkey=[registry_id, task, user],endkey=[registry_id, task, user, {}]):
            group_names.append(row.value["group"])
        return group_names
    
    @classmethod
    def listUserTaskFiles(self, user, registry_id, task_id):
        
        def _strListSize(values_list, str):
            plural = lambda x: 's' if x!=1 else ''
            if values_list:
                return u"%d %s%s" % (len(values_list), str, plural(len(values_list)))
            else:
                return u"nenhum %s" % str
    
        files = []
        for row in database.TASKFILES.view('files/folder_data',startkey=[registry_id, folder],endkey=[registry_id, folder, {}]):
            (registry_id, folder, file_id) = row.key
            file_data = dict()
            file_data.update(row.value)
            file_data["registry_id"] = registry_id
            file_data["file_id"] = file_id   #este file_id é o id
            file_data["filename_id"] = file_id.split("/")[1] #= ao nomepag_id da wiki
            files.append(file_data)            
        return files
    
    
    @classmethod
    def listFolders(self, user, registry_id, view_name):
        folders = [("", "/")]
        for row in database.TASKFILES.view(view_name,startkey=[registry_id],endkey=[registry_id, {}]):
              (registry_id, doc_id) = row.key
              if row.value["is_folder"]=="S":
                  folders.append((doc_id.split("/")[1], str_limit(row.value["filename"], 50)))        
        #folders = sorted(folders, key=itemgetter("data_nofmt"), reverse = True)
        return folders


    @classmethod
    def filenameExists(self, registry_id, file_id, filename):
        # Verifica se já existe algum item (página ou pasta) cadastrado com um determinado nome
    
        return database.TASKFILES.view('taskfiles/filename_exists',startkey=[registry_id,file_id,filename],endkey=[registry_id,file_id,filename, {}])

    def filesize(self, filename):
        if '_attachments' in self:
            return self['_attachments'][filename]['length']
        else:
            return 0
            

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
            database.TASKFILES.put_attachment(database.TASKFILES[id],
                                          files["arquivo"][0]["body"],
                                          self.filenames[-1][0],
                                          files["arquivo"][0]["content_type"])
    def newFileComment(self, owner, comment):
        self.comentarios.append(dict(
                                  owner = owner,
                                  comment = comment,
                                  data_cri = str(datetime.now())
                                ))
        self.save()

    
    def deleteFileComment(self, owner, data_cri):
        for row in database.TASKFILES.view('files/comment',key=[self.id, owner, data_cri]):
            comentario = dict()
            comentario["comment"] = row.value
            comentario["data_cri"] = data_cri
            comentario["owner"] = owner            
            self.comentarios.remove(comentario)
            self.save()
            return True
        return False
   

    def save(self, id=None, db=database.TASKFILES):
        if not self.id and id: self.id = id
        self.store(db)
        
    def retrieve(self, id, db=database.TASKFILES):
        return TaskFiles.load(db, id)
    
    def delete(self, db=database.TASKFILES):
        #db.delete(self)
        del db[self.id]

    def deleteAttachment(self, filename, db=database.TASKFILES):
        for index, item in enumerate(self.filenames):
            if item[0] == filename:
                self.filenames.pop(index)
                self.save()
                db.delete_attachment(self, filename)
                return

    def deleteTaskComment(self, owner, data_cri):
        for row in database.TASKFILES.view('taskfiles/comment',key=[self.id, owner, data_cri]):
            comentario = dict()
            comentario["comment"] = row.value
            comentario["data_cri"] = data_cri
            comentario["owner"] = owner            
            self.comentarios.remove(comentario)
            self.save()
            return True
        return False