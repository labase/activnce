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
from urllib import quote,unquote
from operator import itemgetter

import tornado.web
import tornado.template
from tornado.web import HTTPError

import model
import database
import core.model
from core.model import isOwner, isMember, isUserOrMember
from core.model import ifExists

import core.database
from core.database import DB_VERSAO_010

import log.model
import wiki.model
from core.dispatcher import BaseHandler, HANDLERS, URL_TO_PAGETITLE, \
                            NOMEUSERS, \
                            FILENAMECHARS, PAGENAMECHARS
                            
from libs.dateformat import short_datetime, verificaIntervaloDMY, maiorData
from libs.strformat import remove_diacritics, remove_special_chars, mem_size_format
from libs.notify import Notify

import libs.permissions
from libs.permissions import usersAllowedToRead, isAllowedToDeleteObject, isAllowedToComment, isAllowedToDeleteComment, \
                             isAllowedToReadObject, isAllowedToWriteObject, objectOwnerFromService



''' importa definição do tutorial deste módulo, se existir _tutorial.py '''
from config import TUTORIAL, LABVAD_URL, LABVAD_LOGIN_URL
try:
    import _tutorial
except ImportError:
    pass

def prepareTasks(tasks, user):
    task_data = []
    
    for task in tasks:
        
        dentroDoPeriodo = verificaIntervaloDMY(task["data_inicio"], task["data_encerramento"])
        (comunidade_id, tarefa_id) = task["_id"].split("/")
        tem_grupo = False
        
        group_name = model.TaskFiles().getGroupName(comunidade_id,tarefa_id,user)
        if (group_name):
            tem_grupo = True         

        task_data.append((task["_id"], \
                                  task["descricao"], \
                                  task["data_inicio"], \
                                  task["data_encerramento"], \
                                  dentroDoPeriodo, \
                                  int(task["num_participantes"]), \
                                  tem_grupo, \
                                  task["data_alt"] \
                                  ))
    # retorna a lista ordenada por data_alt decrescente
    return sorted(task_data, key=itemgetter(7), reverse=True)
                    
class NewTaskHandler(BaseHandler):
    ''' Inclusão de uma nova tarefa numa comunidade '''

    @tornado.web.authenticated
    @core.model.serviceEnabled('task')
    def get(self, registry_id):
        user = self.get_current_user()
        
        if isOwner(user, registry_id):
            self._task = model.Task()
            
            # Tentando pegar os nomes do Grupos...
            self._comu = core.model.Community().retrieve(registry_id)
            #print self._comu.groups.keys()
            
            self.render("modules/task/newtask-form.html", MSG="", TASKDATA=self._task, \
                                REGISTRY_ID=registry_id, \
                                GROUPSDATA =self._comu.groups.keys(), \
                                NOMEPAG="Tarefas")
        else:
            raise HTTPError(403)  
            
              
    @tornado.web.authenticated
    @core.model.serviceEnabled('task')
    def post(self, registry_id):
        user = self.get_current_user()
        
        msg = ""
        if isOwner(user, registry_id):
            self._task = model.Task()
            self._task.nome = self.get_argument("nome","")
            if not self._task.nome:
                msg += u"Nome da tarefa não informado.<br/>"
            else:
                self._task.nome = remove_special_chars(remove_diacritics(self._task.nome.replace(" ","_")))
                if self._task.nome == "":
                    msg += u"Nome da tarefa inválido.<br/>"
            
            self._task.descricao = self.get_argument("descricao", "")            
            self._task.num_arquivos = self.get_argument("num_arquivos","")
                            
            self._task.valor = self.get_argument("valor","").strip()
            if not self._task.valor:
                msg += u"O campo 'Valor' não foi preenchido.<br/>"
            else:
                if ((int(self._task.valor) > 100) or (int(self._task.valor) < 0)):
                    msg += u"Valor preenchido incorretamente. Favor escolher um valor entre 0 e 100.<br/>"
                 
            self._task.owner = user
            self._task.data_cri = str(datetime.now())
            self._task.data_alt = self._task.data_cri
            
            self._task.data_inicio = self.get_argument("data_start","")
            if not self._task.data_inicio:
                msg += u"O campo 'Data/hora de início' não foi preenchido.<br/>"
            
            self._task.data_encerramento = self.get_argument("data_end","")
            if not self._task.data_encerramento:
                msg += u"O campo 'Data/hora de encerramento' não foi preenchido.<br/>"
                
            if not msg and not maiorData(self._task.data_encerramento, self._task.data_inicio, short=True):
                msg += u"A Data/hora de encerramento não pode ser anterior à Data/hora de início.<br/>"
            
            #under construction
            self._task.grupo = self.get_argument("select_groups","")


            if self.get_argument("forma_realizacao","") == "individual":
                self._task.num_participantes = 1
            elif self.get_argument("forma_realizacao","") == "em_grupos_de":
                self._task.num_participantes = self.get_argument("num_participantes","")
                if not self._task.num_participantes:
                    msg += u"O campo 'Número de Participantes' não foi preenchido.<br/>"

            self._task.recurso = self.get_argument("recurso","")
            self._task.labvad = self.get_argument("labvad","N")

            comu = core.model.Community().retrieve(registry_id)
            if msg:
                
                self.render("modules/task/newtask-form.html", MSG=msg, TASKDATA=self._task, \
                                    REGISTRY_ID=registry_id, GROUPSDATA =comu.groups.keys(), \
                                    NOMEPAG="Tarefas")                
            else:
                task_id = "%s/%s" % (registry_id, self._task.nome)
                try:
                    self._task.save(id=task_id)
                    
                except Exception as detail:
                    self.render("modules/task/newtask-form.html", MSG=u"Já existe uma tarefa com este nome", TASKDATA=self._task, \
                                    REGISTRY_ID=registry_id, GROUPSDATA =comu.groups.keys(), \
                                    NOMEPAG="Tarefas")
                    return
                
                #notifica usuários de uma comunidade quando uma tarefa é criada. Rever p/ grupos dentro da comunidade. 
                email_msg = user+" criou a tarefa "+ self._task.nome + " na comunidade " + registry_id +".\n" +\
                            Notify.assinatura(user, registry_id, self._task.data_cri)+"\n\n"
                            
                
                members = comu.getMembersList(return_is_owner=False)[1]
                            
                for member in members:
                    Notify.email_notify(member[0], user, "criou uma nova tarefa", \
                                   message=email_msg, \
                                   link="task/"+registry_id)
                
                                    
                log.model.log(user, u'criou a tarefa', objeto=task_id, tipo="task")
                self.redirect("/task/%s" % registry_id)               
        else:
            raise HTTPError(403)  



class TaskEditHandler(BaseHandler):
    ''' Alteração de uma tarefa numa comunidade '''

    @tornado.web.authenticated
    @core.model.serviceEnabled('task')
    def get(self, registry_id, task):
        user = self.get_current_user()

        if isOwner(user, registry_id):
            task_id = '/'.join([registry_id,unquote(task).decode("UTF-8")])
            self._task = model.Task().retrieve(task_id)
            if self._task:     
                
                self.render("modules/task/task-edit.html", MSG="", TASKDATA=self._task, \
                                    REGISTRY_ID=registry_id, NOMEPAG="Tarefas")
            else:
                raise HTTPError(404)  
        else:
            raise HTTPError(403)  
    
            
    @tornado.web.authenticated
    @core.model.serviceEnabled('task')
    def post(self, registry_id, task):
        user = self.get_current_user()
        
        if isOwner(user, registry_id):
            task_id = '/'.join([registry_id,unquote(task).decode("UTF-8")])
            self._task = model.Task().retrieve(task_id)
            if self._task:            
                msg = ''
                self._task.data_inicio = self.get_argument("data_start","")
                if self._task.data_inicio == "":
                    msg += u"O campo 'Data/hora de início' não foi preenchido.<br/>"
                self._task.data_encerramento = self.get_argument("data_end","")
                if self._task.data_encerramento == "":
                    msg += u"O campo 'Data/hora de encerramento' não foi preenchido.<br/>"
                    
                if not maiorData(self._task.data_encerramento, self._task.data_inicio, short=True):
                    msg += u"A Data/hora de encerramento não pode ser anterior à Data/hora de início.<br/>"
                
                self._task.descricao = self.get_argument("descricao", "")
                self._task.data_alt = str(datetime.now())
                self._task.valor = self.get_argument("valor","")              
                self._task.num_arquivos = self.get_argument("num_arquivos","")
                self._task.recurso = self.get_argument("recurso","")
                self._task.labvad = self.get_argument("labvad","N")
                                
                if msg:
                    self.render("modules/task/task-edit.html", MSG=msg, TASKDATA=self._task, \
                                        REGISTRY_ID=registry_id, NOMEPAG="Tarefas")
                    return

                self._task.save()
                log.model.log(user, u'alterou a tarefa', objeto=task_id, tipo="task")
                self.redirect("/task/%s" % registry_id)

            else:
                raise HTTPError(404)  
        else:
            raise HTTPError(403)  
       
            
class ListTasksHandler(BaseHandler):
    ''' Lista tarefas de uma comunidade '''

    @tornado.web.authenticated
    @core.model.serviceEnabled('task')
    def get(self, registry_id):
        user = self.get_current_user()
        
        if isMember(user, registry_id):
            
            if isOwner(user, registry_id):
                            
                task_data = prepareTasks(model.Task.listTasks(user, registry_id, True), user)
            else:
                task_data = prepareTasks(model.Task.listTasks(user, registry_id), user)
                                       
            links = []
            
            if isOwner(user, registry_id):
                links.append((u"Nova tarefa", "/static/imagens/icones/add32.png", "/task/new/"+registry_id))

            log.model.log(user, u'acessou a lista de tarefas de', objeto=registry_id, tipo="task", news=False)
            self.render("modules/task/task-list.html", TASKDATA=task_data, \
                        MSG="", \
                        REGISTRY_ID=registry_id, PERMISSION=isOwner(user,registry_id), \
                        LINKS=links, \
                        NOMEPAG="Tarefas")
        else:
            raise HTTPError(403)           

            
class TaskViewFilesHandler(BaseHandler):
    ''' Apresenta resolução da tarefa de um usuário específico '''

    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('task')
    @libs.permissions.hasReadPermission ('task')
    def get(self, registry_id, task, student):
        user = self.get_current_user()
        
        if isOwner(user, registry_id):
            file_id = '/'.join([registry_id,unquote(task).decode("UTF-8"),student])
            task_id = '/'.join([registry_id,unquote(task).decode("UTF-8")])                
            self._task = model.Task().retrieve(task_id)
            self._taskfiles = model.TaskFiles().retrieve(file_id)
            fileslist = []
            participanteslist = []
            meu_grupo = "" 
                        
            if self._taskfiles:
                fileslist = self._taskfiles.filenames
                i = 0
                for arq in fileslist:
                    fileslist[i][1] = short_datetime(fileslist[i][1], include_year=True)
                    fileslist[i][2] = mem_size_format(self._taskfiles["_attachments"][arq[0]]['length'])
                    i = i+1
                    
                participanteslist = self._taskfiles.participantes
                if int(self._task.num_participantes) > 1:
                    meu_grupo = model.TaskFiles().getGroupName(registry_id, task, user)

                log.model.log(user, u'acessou a tarefa', objeto=task_id, tipo="task", news=False)
                    
                self.render("modules/task/taskviewuser-form.html", \
                        TASKDATA=self._task, \
                        STUDENT=student,\
                        TASKFILES= fileslist, \
                        PARTICIPANTES = participanteslist, \
                        NOME_GRUPO = meu_grupo, \
                        NOMEPAG='tarefa', REGISTRY_ID=registry_id,TASK =task,NUMARQUIVOS = self._task.num_arquivos, MSG="", TASKDOC=self._taskfiles)
            else:
                self.render("home.html", MSG=u"Este aluno ainda não enviou esta tarefa.", REGISTRY_ID=ifExists(registry_id, user), \
                                NOMEPAG="Tarefas")            
        else:
            raise HTTPError(403)            
 
            
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('task')
    @libs.permissions.hasReadPermission ('task')
    def post(self, registry_id, task, student):
        user = self.get_current_user()
        
        if isOwner(user, registry_id):            
            task_id = '/'.join([registry_id,unquote(task).decode("UTF-8")])
            file_id = '/'.join([registry_id,unquote(task).decode("UTF-8"),student])        
            self._taskfiles = model.TaskFiles().retrieve(file_id)            
            nota = self.get_argument("nota","")
            self._taskfiles.nota = nota
            self._taskfiles.save()
             
            email_msg = "Administrador(a): " + user + "\n" +\
                        "Comunidade: "+ registry_id +"\n" +\
                        "Tarefa: "+ task +"\n" +\
                        "Nota: " + nota +"\n"+\
                        Notify.assinatura(user, registry_id, str(datetime.now()))+"\n\n"
            
            for member in self._taskfiles.participantes:            
                Notify.email_notify(member, user, "alterou sua nota em uma tarefa", \
                               message=email_msg, \
                               link="task/"+task_id)
            
            log.model.log(user, u'alterou uma nota na tarefa', objeto=task_id, tipo="task")
            
            self.redirect("/task/view/%s/%s" % (task_id,  student))
        else:
            raise HTTPError(403)  

        
class TaskViewHandler(BaseHandler):
    ''' Permite que o dono de uma comunidade veja a lista de usuários que já responderam à tarefa '''

    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('task')
    @libs.permissions.hasReadPermission ('task')
    def get(self, registry_id, task):
        user = self.get_current_user()
        
        if isOwner(user, registry_id):
            task_id = '/'.join([registry_id,unquote(task).decode("UTF-8")])            
            self._task = model.Task().retrieve(task_id)
            link = ""
            
            if self._task:
                if (int(self._task.num_participantes) <= 1):
                    comu = core.model.Community().retrieve(registry_id)
                    members = comu.getMembersList(return_is_owner=False)[1]
                    grupo = False
                    participantes = []
                                    
                    for member in members:
                        link = "/task/view/"+task_id+"/"
                        file_id = '/'.join([registry_id,unquote(task).decode("UTF-8"),member[0]])
                        taskfiles = model.TaskFiles().retrieve(file_id)
                        fileslist = []
                        if taskfiles:    
                            fileslist = taskfiles.filenames
                            participantes.append((member[0], member[1], len(fileslist), short_datetime(taskfiles.data_alt, include_year=True), link, taskfiles.nota))
                        else:
                            participantes.append((member[0], member[1], len(fileslist), "", link, ""))
            
                    log.model.log(user, u'acessou lista de usuarios que já responderam a tarefa', objeto=task_id, tipo="task", news=False)                      
                    self.render("modules/task/taskview-form.html", MSG="", \
                                    TASKNAME=unquote(task), \
                                    PARTICIPANTES=participantes, \
                                    LINK=link, \
                                    GRUPO = grupo, \
                                    REGISTRY_ID=registry_id, NOMEPAG="Tarefas")
                                        
                else:
                    grupo = True
                    participantes_por_grupos = dict()
                    participantes_por_grupos = model.TaskFiles().getGroupsAndParticipants(registry_id, task)
                    gruposlist = []
                    for nome_grupo in participantes_por_grupos:
                        
                        groupId = model.TaskFiles().getGroupId(registry_id, task, nome_grupo)
                       
                        link = "/task/view/"+task_id+"/"
                        file_id = '/'.join([registry_id,unquote(task).decode("UTF-8"),groupId["owner"]])
                        taskfiles = model.TaskFiles().retrieve(file_id)
                        fileslist = []
                        participanteslist = []
                        
                        if taskfiles:    
                            fileslist = taskfiles.filenames
                            participanteslist = taskfiles.participantes
                            
                            gruposlist.append((groupId["owner"], nome_grupo, len(fileslist), short_datetime(taskfiles.data_alt, include_year=True), link, taskfiles.nota, participanteslist))
                        else:
                            gruposlist.append((groupId["owner"], nome_grupo, len(fileslist), "", link, "", participanteslist))
                                              
                    log.model.log(user, u'acessou lista de grupos que já responderam a tarefa', objeto=task_id, tipo="task", news=False)                      
                    self.render("modules/task/taskview-form.html", MSG="", \
                                    TASKNAME=unquote(task), \
                                    PARTICIPANTES=gruposlist, \
                                    LINK=link, \
                                    GRUPO = grupo, \
                                    REGISTRY_ID=registry_id, NOMEPAG="Tarefas")                                        
            else:
                raise HTTPError(404)        
        else:
            raise HTTPError(403)  


class TaskDeleteHandler(BaseHandler):
    ''' Exclusão de uma tarefa numa comunidade '''

    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('task')
    def get(self, registry_id, task):
        user = self.get_current_user()
        
        if isOwner(user, registry_id):
            
            task_id = '/'.join([registry_id,unquote(task).decode("UTF-8")])       
            if database.TASKFILES.view('taskfiles/by_task',startkey=[registry_id, task],endkey=[registry_id, task, {}]):
                self.render("home.html", MSG=u"Você não pode remover uma tarefa com arquivos enviados ou grupos criados.", REGISTRY_ID=ifExists(registry_id, user), \
                            NOMEPAG="Tarefa")
            else:
                self._task = model.Task().retrieve(task_id)
                if self._task:                    
                    self._task.delete()
                    log.model.log(user, u'removeu a tarefa', objeto=task_id, tipo="none")
                    
                self.redirect("/task/%s" % registry_id)            
        else:
            raise HTTPError(403)  


class TaskFileUploadHandler(BaseHandler):
    ''' Recebimento de arquivos do usuário '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('task')
    @core.model.userOrMember
    def get(self, registry_id, task):
        
        user = self.get_current_user()
        owner = model.TaskFiles().getOwnerByParticipant(registry_id, task, user)
        if not(owner):
            owner = user
        file_id = '/'.join([registry_id,unquote(task).decode("UTF-8"),owner])
        task_id = '/'.join([registry_id,unquote(task).decode("UTF-8")])   
        self._task = model.Task().retrieve(task_id)
        self._taskfiles = model.TaskFiles().retrieve(file_id)
        nomeslist = []
        fileslist = []
        dentroDoPeriodo = 0
        
        if (model.Task().TaskConfirm(registry_id, task) == False):
            self.render("home.html", MSG=u"Esta tarefa não existe.", \
                        NOMEPAG='tarefa', REGISTRY_ID=registry_id)
            return
        
        if (verificaIntervaloDMY(self._task["data_inicio"], self._task["data_encerramento"]) == -1):
            mensagem = "Esta tarefa ainda não pode ser realizada. Tente novamente entre "+\
                        self._task["data_inicio"].split(" ")[0] + " às " + self._task["data_inicio"].split(" ")[1] +\
                        " e " + self._task["data_encerramento"].split(" ")[0] + " às " + self._task["data_encerramento"].split(" ")[1] + "."
            self.render("home.html", MSG=mensagem, \
                        NOMEPAG='tarefa', REGISTRY_ID=registry_id)
            return
        
        if ((int(self._task.num_participantes) > 1) and (verificaIntervaloDMY(self._task["data_inicio"], self._task["data_encerramento"]) == 1) and not (model.TaskFiles().getGroupName(registry_id, task, user))):
            self.render("home.html", MSG=u"Esta tarefa está fora do prazo, e era necessário um grupo para realizá-la.", \
                        NOMEPAG='tarefa', REGISTRY_ID=registry_id)
            return
    
        if ((int(self._task.num_participantes) > 1) and not (model.TaskFiles().getGroupName(registry_id, task, user))):
            self.render("home.html", MSG=u"Você precisa de um grupo para esta tarefa.", \
                                NOMEPAG='arquivos', REGISTRY_ID=registry_id)
            return
            
        if self._taskfiles:  
            
            fileslist = self._taskfiles.filenames
            nomeslist = self._taskfiles.participantes
            nome_grupo = self._taskfiles.nome_grupo
            participantes_pendentes = self._taskfiles.participantes_pendentes
            dentroDoPeriodo = verificaIntervaloDMY(self._task["data_inicio"], self._task["data_encerramento"])
            
            i = 0
            for arq in fileslist:
                fileslist[i][1] = short_datetime(fileslist[i][1], include_year=True)
                fileslist[i][2] = mem_size_format(self._taskfiles["_attachments"][arq[0]]['length'])
                i = i+1
        else:
            nome_grupo = ""
            participantes_pendentes = []
        
        if int(self._task.num_arquivos) <= int(len(fileslist)):
            criar = False
        else:
            criar=isUserOrMember(owner,registry_id)
        
        group_owner = False    
        if (user == owner):
            group_owner = True
        
        self.render("modules/task/taskupload-form.html", \
                    CRIAR= criar, \
                    TASKDATA=self._task, \
                    LABVAD_URL=LABVAD_URL, \
                    OWNER=owner, \
                    GROUP_OWNER=group_owner, \
                    NOME_GRUPO=nome_grupo, \
                    NOMES_LIST=nomeslist, \
                    TASKFILES=fileslist, \
                    PARTICIPANTES_PENDENTES=participantes_pendentes, \
                    PERIODO=dentroDoPeriodo, \
                    NOMEPAG="Tarefas", REGISTRY_ID=registry_id,TASK =task,NUMARQUIVOS = self._task.num_arquivos, MSG="", TASKDOC=self._taskfiles)


    @tornado.web.authenticated
    @core.model.serviceEnabled('task')
    @core.model.userOrMember
    def post(self, registry_id, task):
        user = self.get_current_user()
        meu_id = 0
        msg = ""
        
        owner = model.TaskFiles().getOwnerByParticipant(registry_id, task, user)
        if not(owner):
            owner = user
        task_id = '/'.join([registry_id,unquote(task).decode("UTF-8")])
        file_id = '/'.join([registry_id,unquote(task).decode("UTF-8"),owner])

        if self.request.files:
            
            filename = self.request.files["arquivo"][0]["filename"].split("\\")[-1]
            filename = remove_special_chars(remove_diacritics(filename.replace(" ","_")))
            
            if filename=="":
                msg += u"* Nome do arquivo inválido.<br/>"
            
            if model.TaskFiles().filenameExists(registry_id, file_id, filename):
                self.render("home.html", MSG="Já existe um arquivo com este nome.", \
                                NOMEPAG='tarefa', REGISTRY_ID=registry_id)
                return
                            
            self._task = model.Task().retrieve(task_id)
            self._file = model.TaskFiles().retrieve(file_id)
            if self._file:
                if len(self._file.filenames) >= self._task.num_arquivos:
                    self.render("home.html", MSG=u"Você já enviou o número de arquivos solicitado pelo professor. Remova algum arquivo caso deseje subir uma nova versão.", \
                                NOMEPAG='arquivos', REGISTRY_ID=registry_id)
                    return
            else: 
                self._file = model.TaskFiles(file_id=file_id)
                self._file.participantes.append(user)
    
            self._file.owner = owner
            self._file.alterado_por = user
            self._file.registry_id = registry_id
            self._file.task = task
            self._file.data_upload = self._file.data_alt = str(datetime.now())
            self._file.filenames.append((filename, self._file.data_upload, ""))
            self._file.saveFile(file_id, self.request.files)
            
            log.model.log(user, u'enviou um arquivo na tarefa', objeto=task_id, tipo="task")
            
            self.redirect("/task/%s" % task_id)
        else:
            self.render("home.html", MSG=u"Erro: Arquivo inexistente!", \
                        NOMEPAG='arquivos', REGISTRY_ID=registry_id)


class FileDeleteHandler(BaseHandler):
    ''' Apaga arquivos/pastas do usuário '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('task')
    @core.model.userOrMember
    def get(self, registry_id, filename, task):
        user = self.get_current_user()
        owner = self.get_argument("owner","")
        task_id = '/'.join([registry_id,unquote(task).decode("UTF-8")])        
        file_id = '/'.join([registry_id,unquote(task).decode("UTF-8"),owner])
        log_id = '/'.join([unquote(task).decode("UTF-8"),filename])
        self._file = model.TaskFiles().retrieve(file_id)        
        
        if self._file != None:           
            # salva variáveis para poder ter acesso a elas depois de remover do banco
            file_owner = self._file.owner
            
            if user in self._file.participantes:
                if owner == file_owner:
                    self._file.deleteAttachment(filename)
                    log.model.log(user, u'removeu um arquivo da tarefa', objeto=task_id, tipo="task")
                    
                    self.redirect("/task/%s/%s" % (registry_id, task))
                    return
                else:
                    raise HTTPError(403)  
            else:
                raise HTTPError(403)  
        else:
            raise HTTPError(404)  
            

class CommentTaskHandler(BaseHandler):
    ''' Inclusão de um comentário de uma tarefa '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('task')
    @core.model.userOrMember
    def post(self, registry_id, task):
        user = self.get_current_user()
        nome_usuario = self.get_argument("nome_usuario","")
        owner = self.get_argument("owner","")
        task_id = '/'.join([registry_id,unquote(task).decode("UTF-8")])
                
        if nome_usuario != "":
            file_id = '/'.join([registry_id,unquote(task).decode("UTF-8"),nome_usuario])
        else:
            file_id = '/'.join([registry_id,unquote(task).decode("UTF-8"),owner])
        
        self._taskfiles = model.TaskFiles().retrieve(file_id)
        if self._taskfiles:
            comentario = dict()
            comentario["comment"] = self.get_argument("comment","")
            comentario["owner"] = user
            comentario["data_cri"] = short_datetime(str(datetime.now()), include_year=True)
            
            if comentario["comment"]:
                self._taskfiles.comentarios.append(comentario)
                log.model.log(user, u'comentou a tarefa', objeto=task_id, tipo="task")
                
                self._taskfiles.save()
                
                if nome_usuario != "":
                    self.redirect("/task/view/%s/%s/%s" % (registry_id, task, nome_usuario))
                else:
                    self.redirect("/task/%s/%s" % (registry_id, task))               
            else:
                self.render("home.html", MSG=u"O comentário não pode ser vazio.", REGISTRY_ID=registry_id, NOMEPAG='tarefa',)
        else:
            raise HTTPError(404)  


class DeleteCommentHandler(BaseHandler):
    ''' Apaga um comentário de uma Tarefa '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('task')
    def get(self, registry_id, task):
        user = self.get_current_user()
        owner = self.get_argument("owner","")
        data_cri = self.get_argument("data","")
        
        if isAllowedToDeleteComment(user, registry_id, owner):
            task_id = '/'.join([registry_id,unquote(task).decode("UTF-8")])
            file_id = '/'.join([registry_id,unquote(task).decode("UTF-8"),owner])
        
            self._taskfiles = model.TaskFiles().retrieve(file_id)
            if self._taskfiles:
                if self._taskfiles.deleteTaskComment(user, data_cri):
                    
                    log.model.log(user, u'removeu um comentário da tarefa', objeto=task_id, tipo="task")
                    
                    self.redirect("/task/%s/%s" % (registry_id, task))
                else:
                    # Comentário não encontrado
                    raise HTTPError(404)  
            else:
                raise HTTPError(404)  
        else:
            raise HTTPError(403)  


class FileViewHandler(BaseHandler):
    ''' Exibe os arquivos entregues em uma tarefa por um grupo ou usuário '''
    
    @core.model.allowedToAccess
    @core.model.serviceEnabled('task')
    @libs.permissions.hasReadPermission('task')
    @core.model.userOrMember
    def get(self, registry_id, filename, task):
        
        user = self.get_current_user()
        meu_grupo = ""
        grupo_do_owner = ""
        meu_grupo = model.TaskFiles().getGroupName(registry_id,task,user)
        owner = self.get_argument("groupld","")
        grupo_do_owner = model.TaskFiles().getGroupName(registry_id,task,owner)

        if (meu_grupo and grupo_do_owner) or (user == owner) or isOwner(user,registry_id):            
            if (meu_grupo == grupo_do_owner) or isOwner(user, registry_id) or (user == owner):
                
                if not(user == owner):
                    user = owner

                task_id = '/'.join([registry_id,unquote(task).decode("UTF-8")])                
                file_id = '/'.join([registry_id,unquote(task).decode("UTF-8"),user])
                self._file = model.TaskFiles().retrieve(file_id)                            
                if self._file:
                   # Header content-disposition deve ser inline ou attachment
                    disposition = self.get_argument("disp", "inline")
                    self.set_header("Content-Disposition", "%s; filename=%s" % (disposition, filename))
                    self.set_header("Content-Type", self._file["_attachments"][filename]['content_type'])
                    self.set_header("Content-Length", self._file["_attachments"][filename]['length'])
                    
                    log.model.log(user, u'acessou um arquivo da tarefa', objeto=task_id, tipo="task", news=False)
                                        
                    if DB_VERSAO_010:
                        self.write(database.TASKFILES.get_attachment(file_id, filename, default="Object not found!"))
                    else:
                        self.write(database.TASKFILES.get_attachment(file_id, filename, default="Object not found!").read())
                    
                else:
                    # Arquivo não encontrado
                    raise HTTPError(404)                      
            else:
                #Você não tem permissão para baixar este arquivo
                raise HTTPError(403)                      
        else:
            #Você não tem permissão para visualizar esta tarefa.
            raise HTTPError(403)                      
                    

class TaskGroupListHandler(BaseHandler):
    ''' Lista de Grupos de Uma Tarefa '''

    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('task')
    @core.model.userOrMember
    def get(self, registry_id, task):
        
        user = self.get_current_user()
        task_id = '/'.join([registry_id,unquote(task).decode("UTF-8")])
        self._task = model.Task().retrieve(task_id)
        meu_grupo = ""        
        meu_grupo = model.TaskFiles().getGroupName(registry_id,task,user)
        tem_grupo = False
        if (meu_grupo):
            tem_grupo = True
        if (model.Task().TaskConfirm(registry_id, task) == False):
            self.render("home.html", MSG=u"Esta tarefa não existe.", \
                        NOMEPAG='tarefa', REGISTRY_ID=registry_id)
            return   
        
        dentroDoPeriodo = verificaIntervaloDMY(self._task["data_inicio"], self._task["data_encerramento"])
        
        grupos_pendente = model.TaskFiles().getGroupsByPending(registry_id, task, user)
        
        links = []
        if ((isMember(user, registry_id)) and (not tem_grupo)):
            links.append((u"Criar novo grupo", "/static/imagens/icones/add32.png", "/task/group/new/"+registry_id+"/"+task, "","",True))
                          
        participantes_por_grupos = dict()
        participantes_por_grupos = model.TaskFiles().getGroupsAndParticipants(registry_id,task)          

        log.model.log(user, u'acessou a lista de grupos da tarefa', objeto=task_id, tipo="task", news=False)

        self.render("modules/task/taskgroup-list.html", MSG="", \
                PARTICIPANTES_POR_GRUPOS=participantes_por_grupos, \
                TEM_GRUPO = tem_grupo, \
                MEU_GRUPO = meu_grupo, \
                GRUPOS_PENDENTE = grupos_pendente, \
                PERIODO = dentroDoPeriodo, \
                TASKNAME = task, \
                LINKS = links, \
                REGISTRY_ID=registry_id, NOMEPAG="Tarefas")

            
class TaskNewGroupHandler(BaseHandler):
    ''' Criação de Grupos de Uma Tarefa '''

    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('task')
    def get(self, registry_id, task):
        
        user = self.get_current_user()
        task_id = '/'.join([registry_id,unquote(task).decode("UTF-8")])
        self._task = model.Task().retrieve(task_id)
        
        if not isUserOrMember(user, registry_id):
            self.render("home.html", MSG=u"Você não tem permissão para criar grupos aqui.", \
                        NOMEPAG='tarefas', REGISTRY_ID=registry_id)
            return
        
        if verificaIntervaloDMY(self._task["data_inicio"], self._task["data_encerramento"]) == 1:
            self.render("home.html", MSG=u"Tarefa fora do prazo.", \
                        NOMEPAG='tarefas', REGISTRY_ID=registry_id)
            return
        
        if (model.Task.TaskConfirm(registry_id, task) == False):
            self.render("home.html", MSG=u"Esta tarefa não existe.", \
                        NOMEPAG='tarefa', REGISTRY_ID=registry_id)
            return
        
        self.render("modules/task/newtaskgrouppopup-form.html", \
                 NOMEPAG='tarefas', REGISTRY_ID=registry_id, MSG="")     
    
        
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('task')
    @core.model.userOrMember
    def post(self, registry_id, task):
        
        user = self.get_current_user()
        task_id = '/'.join([registry_id,unquote(task).decode("UTF-8")])
        file_id = '/'.join([registry_id,unquote(task).decode("UTF-8"),user])
        self._task = model.Task().retrieve(task_id)
        self._file = model.TaskFiles(file_id=file_id)
        
        if verificaIntervaloDMY(self._task["data_inicio"], self._task["data_encerramento"]) == 1:
            self.render("home.html", MSG=u"Tarefa fora do prazo.", \
                        NOMEPAG='tarefas', REGISTRY_ID=registry_id)
            return
        
        if model.TaskFiles().getGroupName(registry_id, task, user):
                self.render("home.html", MSG=u"Você não tem permissão para operar aqui.", \
                        NOMEPAG='tarefa', REGISTRY_ID=registry_id)
                return

        nome_grupo = self.get_argument("nome_grupo","")
        if not nome_grupo:
                self.render("popup_msg.html", MSG=u"Nome do grupo não foi preenchido.", REGISTRY_ID=registry_id)
                return
        
        ja_existe = False
        file_id = model.TaskFiles().getGroupFileId(registry_id, task, nome_grupo)
        if not(file_id == "-1"):
            ja_existe = True
        
        file_id = '/'.join([registry_id,unquote(task).decode("UTF-8"),user])
        
        if ja_existe:
            self.render("popup_msg.html", MSG=u"Nome do grupo ja existe.", REGISTRY_ID=registry_id)
            return
        
        self._file.owner = self._file.alterado_por = user
        self._file.registry_id = registry_id
        self._file.task = task
        self._file.data_upload = self._file.data_alt = str(datetime.now())
        self._file.participantes.append(user)
        self._file.nome_grupo = nome_grupo
        self._file.save(id=file_id)

        log.model.log(user, u'criou um grupo na tarefa', objeto=task_id, tipo="task", news=False)

        self.render("popup_msg.html", MSG=u"Grupo criado com sucesso!", REGISTRY_ID=registry_id)

class TaskGroupJoinHandler(BaseHandler):
    ''' Requisição de Entrada nos Grupos de Uma Tarefa '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('task')
    def get(self, registry_id, task):
        
        user = self.get_current_user()
        if not isUserOrMember(user, registry_id):
            self.render("home.html", MSG=u"Você não tem permissão para se juntar a um grupo aqui.", \
                        NOMEPAG='tarefas', REGISTRY_ID=registry_id)
            return
    
        nome_grupo = self.get_argument("grupo","")
        
        if ( not nome_grupo or (model.TaskFiles().getGroupFileId(registry_id, task, nome_grupo) == "-1")):
              self.render("home.html", MSG=u"Grupo inexistente.", \
                        NOMEPAG='tarefas', REGISTRY_ID=registry_id)
              return
        groupId = model.TaskFiles().getGroupId(registry_id, task, nome_grupo)            
        task_id = '/'.join([registry_id,unquote(task).decode("UTF-8")])
        file_id = '/'.join([registry_id,unquote(task).decode("UTF-8"),groupId["owner"]])
        self._task = model.Task().retrieve(task_id)
        self._file = model.TaskFiles().retrieve(file_id)
        
        grupo_user = model.TaskFiles().getGroupName(registry_id, task, user)
        
        if(int(self._task.num_participantes) > len(self._file.participantes)):
            if(grupo_user):
                self.render("home.html", MSG=u"Você já faz parte de um grupo para esta tarefa.", \
                        NOMEPAG='tarefas', REGISTRY_ID=registry_id)
                return
            
            if(user in self._file.participantes_pendentes):
                self.render("home.html", MSG=u"Você já requisitou entrada neste grupo.", \
                        NOMEPAG='tarefas', REGISTRY_ID=registry_id)
                return
            
            self._file.data_alt = str(datetime.now())
            self._file.participantes_pendentes.append(user)
            self._file.save(id=file_id)
            
            #notifica o dono do grupo sobre a requisição de entrada de um novo usuário     
            email_msg = "Usuário: " + user + "\n" +\
                        "Comunidade: "+ registry_id +"\n" +\
                        "Tarefa: "+ task +"\n" +\
                        "Grupo: "+ nome_grupo +"\n\n" +\
                        Notify.assinatura(user, registry_id, self._file.data_alt)+"\n\n"
                        
            Notify.email_notify(groupId["owner"], user, "requisitou entrada em seu grupo de tarefa", \
                           message=email_msg, \
                           link="task/"+task_id)

            log.model.log(user, u'requisitou entrada num grupo da tarefa', objeto=task_id, tipo="task", news=False)
            
            self.redirect("/task/%s" % registry_id)
        else:
            self.render("home.html", MSG=u"Este grupo está cheio.", \
                        NOMEPAG='tarefas', REGISTRY_ID=registry_id)
            
class TaskGroupAcceptHandler(BaseHandler):
    ''' Aceitação nos Grupos de Uma Tarefa '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('task')
    def get(self, registry_id, task):
        
        user = self.get_current_user()
        
        if not isUserOrMember(user, registry_id):
            self.render("home.html", MSG=u"Você não tem permissão para se juntar a um grupo aqui.", \
                        NOMEPAG='tarefas', REGISTRY_ID=registry_id)
            return
        
        meu_grupo = model.TaskFiles().getGroupName(registry_id, task, user)
        file_id = model.TaskFiles().getGroupFileId(registry_id, task, meu_grupo)
        task_id = '/'.join([registry_id,unquote(task).decode("UTF-8")])
        self._task = model.Task().retrieve(task_id)
        self._file = model.TaskFiles().retrieve(file_id)
        
        if verificaIntervaloDMY(self._task["data_inicio"], self._task["data_encerramento"]) != 0:
            self.render("home.html", MSG=u"Tarefa fora do prazo.", \
                        NOMEPAG='tarefas', REGISTRY_ID=registry_id)
            return
        
        if not self._file:
            self.render("home.html", MSG=u"Você não tem permissão para operar aqui.", \
                        NOMEPAG='tarefas', REGISTRY_ID=registry_id)
            return
        
        if not (self._file.owner == user):
            self.render("home.html", MSG=u"Você não tem permissão para adicionar pessoas neste grupo.", \
                        NOMEPAG='tarefas', REGISTRY_ID=registry_id)
            return

        add_user = self.get_argument("add_user","")     
        grupo_user = model.TaskFiles().getGroupName(registry_id, task, add_user)
        
        if not add_user in self._file.participantes_pendentes:
            self.render("home.html", MSG=u"Este usuário não requisitou entrada neste grupo.", \
                        NOMEPAG='tarefas', REGISTRY_ID=registry_id)
            return
        
        if grupo_user == meu_grupo:
            self.render("home.html", MSG=u"Este usuário já faz parte deste grupo.", \
                        NOMEPAG='tarefas', REGISTRY_ID=registry_id)
            return
            
        if(len(self._file.participantes) < int(self._task.num_participantes)):
            if(grupo_user):
                self._file.participantes_pendentes.remove(add_user)
                self._file.save(id=file_id)
                self.render("home.html", MSG=u"Este usuário já está em um grupo.", \
                        NOMEPAG='tarefas', REGISTRY_ID=registry_id)
                return
            
            self._file.data_alt = str(datetime.now())
            self._file.participantes.append(add_user)
            self._file.participantes_pendentes.remove(add_user)
            self._file.save(id=file_id)
            
            #notifica o usuario que ele foi aceito num grupo
            email_msg = "Usuário: " + user + "\n" +\
                        "Comunidade: "+ registry_id +"\n" +\
                        "Tarefa: "+ task +"\n" +\
                        "Grupo: "+ meu_grupo +"\n\n" +\
                        Notify.assinatura(user, registry_id, self._file.data_alt)+"\n\n"
                        
            Notify.email_notify(add_user, user, "aceitou sua entrada em um grupo de tarefa", \
                           message=email_msg, \
                           link="task/"+task_id)
            
            log.model.log(user, u'aceitou entrada num grupo da tarefa', objeto=task_id, tipo="task", news=False)
            
            self.redirect("/task/%s" % task_id)
        else:
            self.render("home.html", MSG=u"Este grupo está cheio.", \
                        NOMEPAG='tarefas', REGISTRY_ID=registry_id)
            return
        
class TaskGroupRejectHandler(BaseHandler):
    ''' Rejeição nos Grupos de Uma Tarefa '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('task')
    def get(self, registry_id, task):
        
        user = self.get_current_user()
        if not isUserOrMember(user, registry_id):
            
            self.render("home.html", MSG=u"Você não tem permissão para se juntar a um grupo aqui.", \
                        NOMEPAG='tarefas', REGISTRY_ID=registry_id)
            return
         
        meu_grupo = model.TaskFiles().getGroupName(registry_id, task, user)
        file_id = model.TaskFiles().getGroupFileId(registry_id, task, meu_grupo)
        task_id = '/'.join([registry_id,unquote(task).decode("UTF-8")])
        self._task = model.Task().retrieve(task_id)
        self._file = model.TaskFiles().retrieve(file_id)
        
        if not (self._file.owner == user):
            self.render("home.html", MSG=u"Você não tem permissão para rejeitar pessoas neste grupo.", \
                        NOMEPAG='tarefas', REGISTRY_ID=registry_id)
            return

        remove_user = self.get_argument("remove_user","")
        
        if not (remove_user in self._file.participantes_pendentes):
            self.render("home.html", MSG=u"Este usuário não requisitou entrada neste grupo.", \
                        NOMEPAG='tarefas', REGISTRY_ID=registry_id)
            return
              
        self._file.data_upload = self._file.data_alt = str(datetime.now())
        self._file.participantes_pendentes.remove(remove_user)
        self._file.save(id=file_id)
        
        #notifica o usuario que ele foi rejeitado num grupo
        email_msg = "Usuário: " + user + "\n" +\
                    "Comunidade: "+ registry_id +"\n" +\
                    "Tarefa: "+ task +"\n" +\
                    "Grupo: "+ meu_grupo +"\n\n" +\
                    Notify.assinatura(user, registry_id, self._file.data_alt)+"\n\n"
                    
        Notify.email_notify(remove_user, user, "rejeitou sua entrada em um grupo de tarefa", \
                       message=email_msg, \
                       link="task/group/list"+task_id)

        log.model.log(user, u'recusou entrada num grupo da tarefa', objeto=task_id, tipo="task", news=False)
        
        self.redirect("/task/%s" % task_id)
            
                       
class TaskGroupLeaveHandler(BaseHandler):
    ''' Saída nos Grupos de Uma Tarefa '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('task')
    def get(self, registry_id, task):
        
        user = self.get_current_user()
        nome_remover = self.get_argument("nome_remover","")
        nome_grupo = self.get_argument("grupo","")
        groupId = model.TaskFiles().getGroupId(registry_id, task, nome_grupo)
        task_id = '/'.join([registry_id,unquote(task).decode("UTF-8")])
        file_id = '/'.join([registry_id,unquote(task).decode("UTF-8"),groupId["owner"]])
        self._task = model.Task().retrieve(task_id)
        self._file = model.TaskFiles().retrieve(file_id)
        controle = False
        
        if verificaIntervaloDMY(self._task["data_inicio"], self._task["data_encerramento"]) != 0:
            self.render("home.html", MSG=u"Tarefa fora do prazo.", \
                        NOMEPAG='tarefas', REGISTRY_ID=registry_id)
            return
        
        #if para checar se usuário está saindo do grupo ou removendo alguém
        if user == self._file.owner:
            controle = "removendo"
        else:
             controle = "saindo"
            
        if nome_remover:
            user = nome_remover
                
        if not isUserOrMember(user, registry_id):
            self.render("home.html", MSG=u"Você não tem permissão para operar aqui.", \
                        NOMEPAG='tarefas', REGISTRY_ID=registry_id)
            return
        
        email_msg = "Usuário: " + user + "\n" +\
                    "Comunidade: "+ registry_id +"\n" +\
                    "Tarefa: "+ task +"\n" +\
                    "Grupo: "+ nome_grupo +"\n\n" +\
                    Notify.assinatura(user, registry_id, self._file.data_alt)+"\n\n"
        
        if self._file.owner == user:
            self._file.delete()
            
            for member in self._file.participantes:
                Notify.email_notify(member, user, "desfez um grupo de tarefa", \
                                   message=email_msg, \
                                   link="task/group/list"+task_id)            
        else:
            self._file.data_alt = str(datetime.now())
            if not (model.TaskFiles().getGroupName(registry_id, task, user) == nome_grupo):
                self.render("home.html", MSG=u"Você não tem permissão para operar aqui.", \
                        NOMEPAG='tarefas', REGISTRY_ID=registry_id)
                return
            self._file.participantes.remove(user)
            self._file.save(id=file_id)
            
            if(controle == "removendo"):
                #notifica o usuario que ele foi removido de um grupp                            
                Notify.email_notify(user, self.get_current_user(), "removeu você de um grupo de tarefa", \
                               message=email_msg, \
                               link="task/group/list"+task_id)
                
            elif(controle == "saindo"):
                #notifica os usuarios de um grupo que alguém o deixou                            
                for member in self._file.participantes:
                    Notify.email_notify(member, user, "deixou o seu grupo de tarefa", \
                                   message=email_msg, \
                                   link="task/group/list"+task_id)

        log.model.log(user, u'saiu de um grupo da tarefa', objeto=task_id, tipo="task", news=False)
               
        self.redirect("/task/%s" % registry_id)
      
      
"""        
class TaskLabVadHandler(BaseHandler):
    ''' Faz login no labvad '''
    
    @tornado.web.authenticated
    # @core.model.allowedToAccess
    # @core.model.serviceEnabled('task')
    def get(self):
        
        user = self.get_current_user()
        self._user = core.model.Member().retrieve(user)

        self.render("modules/task/labvad-login.html", \
                    LABVAD_LOGIN_URL=LABVAD_LOGIN_URL, \
                    LABVAD_URL=LABVAD_URL, \
                    EMAIL=self._user.email, PASSWD=self._user.labvad_passwd if self._user.labvad_passwd else "", \
                    MSG="")
        
        
        '''       
        if self._user.labvad_passwd:     
            import urllib
            import json
            
            # post 
            params = {"txtEmail": self._user.email, 
                      "txtSenha": self._user.labvad_passwd,
                      "acao": "activufrj"}
            f = urllib.urlopen(LABVAD_LOGIN_URL, urllib.urlencode(params))
            json_str = f.read()
            f.close()
            print json_str
            json_data = json.loads(json_str)
            print json_data
            if json_data["erro"]>0:
                self.render("modules/task/labvad-login.html", \
                            LABVAD_LOGIN_URL=LABVAD_LOGIN_URL, \
                            LABVAD_URL=LABVAD_URL, \
                            EMAIL=self._user.email, PASSWD=self._user.labvad_passwd, \
                            MSG=json_data["msg"])
    
                
            else:
                self.redirect(LABVAD_URL)
        
        else:
            self.render("modules/task/labvad-login.html", \
                        LABVAD_LOGIN_URL=LABVAD_LOGIN_URL, \
                        LABVAD_URL=LABVAD_URL, \
                        EMAIL=self._user.email, PASSWD="", \
                        MSG="")
        '''
            
       
    @tornado.web.authenticated
    # @core.model.allowedToAccess
    # @core.model.serviceEnabled('task')
    def post(self):
        
        user = self.get_current_user()
        email = self.get_argument("txtEmail","")
        passwd = self.get_argument("txtSenha","")
        
        self._user = core.model.Member().retrieve(user)
        
        if passwd:
            import md5
            import urllib
            import json
            
            self._user.labvad_passwd = md5.new(passwd).hexdigest();
            self._user.save()
        
            
            self.render("modules/task/labvad-login.html", \
                        LABVAD_LOGIN_URL=LABVAD_LOGIN_URL, \
                        LABVAD_URL=LABVAD_URL, \
                        EMAIL=self._user.email, PASSWD=self._user.labvad_passwd, \
                        MSG="")
        
            '''
            # post 
            params = {"txtEmail": email, 
                      "txtSenha": self._user.labvad_passwd,
                      "acao": "activufrj"}
            f = urllib.urlopen(LABVAD_LOGIN_URL, urllib.urlencode(params))
            json_str = f.read()
            f.close()
            print json_str
            json_data = json.loads(json_str)
            print json_data
            if json_data["erro"]>0:
                self.render("modules/task/labvad-login.html", EMAIL=self._user.email, PASSWD="", \
                            LABVAD_LOGIN_URL=LABVAD_LOGIN_URL, \
                            LABVAD_URL=LABVAD_URL, \
                            MSG=json_data["msg"])
            else:
                self.redirect(LABVAD_URL)
            '''
        else:
            self.render("modules/task/labvad-login.html", \
                        LABVAD_LOGIN_URL=LABVAD_LOGIN_URL, \
                        LABVAD_URL=LABVAD_URL, \
                        EMAIL=self._user.email, PASSWD="", \
                        MSG="Senha não preenchida.")


class OldTaskLabVadHandler(BaseHandler):
    ''' Faz login no labvad '''
    
    @tornado.web.authenticated
    # @core.model.allowedToAccess
    # @core.model.serviceEnabled('task')
    def get(self):
        
        user = self.get_current_user()
        self._user = core.model.Member().retrieve(user)

        self.render("modules/task/labvad-login.html", \
                    LABVAD_LOGIN_URL=LABVAD_LOGIN_URL, \
                    LABVAD_URL=LABVAD_URL, \
                    EMAIL=self._user.email, PASSWD=self._user.labvad_passwd if self._user.labvad_passwd else "", \
                    MSG="")
        
        
        '''       
        if self._user.labvad_passwd:     
            import urllib
            import json
            
            # post 
            params = {"txtEmail": self._user.email, 
                      "txtSenha": self._user.labvad_passwd,
                      "acao": "activufrj"}
            f = urllib.urlopen(LABVAD_LOGIN_URL, urllib.urlencode(params))
            json_str = f.read()
            f.close()
            print json_str
            json_data = json.loads(json_str)
            print json_data
            if json_data["erro"]>0:
                self.render("modules/task/labvad-login.html", \
                            LABVAD_LOGIN_URL=LABVAD_LOGIN_URL, \
                            LABVAD_URL=LABVAD_URL, \
                            EMAIL=self._user.email, PASSWD=self._user.labvad_passwd, \
                            MSG=json_data["msg"])
    
                
            else:
                self.redirect(LABVAD_URL)
        
        else:
            self.render("modules/task/labvad-login.html", \
                        LABVAD_LOGIN_URL=LABVAD_LOGIN_URL, \
                        LABVAD_URL=LABVAD_URL, \
                        EMAIL=self._user.email, PASSWD="", \
                        MSG="")
        '''
            
       
    @tornado.web.authenticated
    # @core.model.allowedToAccess
    # @core.model.serviceEnabled('task')
    def post(self):
        
        user = self.get_current_user()
        email = self.get_argument("txtEmail","")
        passwd = self.get_argument("txtSenha","")
        
        self._user = core.model.Member().retrieve(user)
        
        if passwd:
            import md5
            import urllib
            import json
            
            self._user.labvad_passwd = md5.new(passwd).hexdigest();
            self._user.save()
        
            
            self.render("modules/task/labvad-login.html", \
                        LABVAD_LOGIN_URL=LABVAD_LOGIN_URL, \
                        LABVAD_URL=LABVAD_URL, \
                        EMAIL=self._user.email, PASSWD=self._user.labvad_passwd, \
                        MSG="")
        
            '''
            # post 
            params = {"txtEmail": email, 
                      "txtSenha": self._user.labvad_passwd,
                      "acao": "activufrj"}
            f = urllib.urlopen(LABVAD_LOGIN_URL, urllib.urlencode(params))
            json_str = f.read()
            f.close()
            print json_str
            json_data = json.loads(json_str)
            print json_data
            if json_data["erro"]>0:
                self.render("modules/task/labvad-login.html", EMAIL=self._user.email, PASSWD="", \
                            LABVAD_LOGIN_URL=LABVAD_LOGIN_URL, \
                            LABVAD_URL=LABVAD_URL, \
                            MSG=json_data["msg"])
            else:
                self.redirect(LABVAD_URL)
            '''
        else:
            self.render("modules/task/labvad-login.html", \
                        LABVAD_LOGIN_URL=LABVAD_LOGIN_URL, \
                        LABVAD_URL=LABVAD_URL, \
                        EMAIL=self._user.email, PASSWD="", \
                        MSG="Senha não preenchida.")
                        
        
class TaskLabVadT0(BaseHandler):
    ''' Faz login no labvad '''
    
    @tornado.web.authenticated
    # @core.model.allowedToAccess
    # @core.model.serviceEnabled('task')
    def get(self):
        import urllib
        import json
        
        user = self.get_current_user()
        self._user = core.model.Member().retrieve(user)

        # post 
        params = {"txtEmail": self._user.email, 
                  "txtSenha": self._user.labvad_passwd,
                  "acao": "activufrj"}
        f = urllib.urlopen("http://localhost/labvad2/t1.php", urllib.urlencode(params))
        json_str = f.read()
        f.close()
        print "t0: "+json_str

        self.redirect ("http://localhost/labvad2/t2.php")
"""

URL_TO_PAGETITLE.update ({
        "task":  u"Tarefa"
    })
        
HANDLERS.extend([
            (r"/task/new/%s"               % (NOMEUSERS),                                    NewTaskHandler),
            # (r"/task/labvad",                                                                TaskLabVadHandler),
            # (r"/task/labvad/t0",                                                             TaskLabVadT0),
            (r"/task/%s"                   % (NOMEUSERS),                                    ListTasksHandler),
            (r"/task/view/%s/%s/%s"        % (NOMEUSERS,PAGENAMECHARS,PAGENAMECHARS),        TaskViewFilesHandler),
            (r"/task/view/%s/%s"           % (NOMEUSERS,PAGENAMECHARS),                      TaskViewHandler),
            (r"/task/%s/%s"                % (NOMEUSERS,PAGENAMECHARS),                      TaskFileUploadHandler), # antigo TaskHandler
            (r"/task/delete/%s/%s"         % (NOMEUSERS,PAGENAMECHARS),                      TaskDeleteHandler),
            (r"/task/edit/%s/%s"           % (NOMEUSERS,PAGENAMECHARS),                      TaskEditHandler),
            (r"/task/comment/%s/%s"        % (NOMEUSERS, PAGENAMECHARS),                     CommentTaskHandler),
            (r"/task/comment/delete/%s/%s" % (NOMEUSERS, PAGENAMECHARS),                     DeleteCommentHandler),
            (r"/task/upload/%s/%s"         % (NOMEUSERS,PAGENAMECHARS),                      TaskFileUploadHandler),
            (r"/task/fileview/%s/%s/%s"    % (NOMEUSERS,PAGENAMECHARS,PAGENAMECHARS),        FileViewHandler),
	        (r"/task/filedelete/%s/%s/%s"  % (NOMEUSERS,PAGENAMECHARS,PAGENAMECHARS),        FileDeleteHandler),
            (r"/task/group/list/%s/%s"     % (NOMEUSERS, PAGENAMECHARS),                     TaskGroupListHandler),
            (r"/task/groupjoin/%s/%s"      % (NOMEUSERS, PAGENAMECHARS),                     TaskGroupJoinHandler),
            (r"/task/groupaccept/%s/%s"    % (NOMEUSERS, PAGENAMECHARS),                     TaskGroupAcceptHandler),
            (r"/task/groupreject/%s/%s"    % (NOMEUSERS, PAGENAMECHARS),                     TaskGroupRejectHandler),
            (r"/task/groupleave/%s/%s"     % (NOMEUSERS, PAGENAMECHARS),                     TaskGroupLeaveHandler),
            (r"/task/group/new/%s/%s"      % (NOMEUSERS, PAGENAMECHARS),                     TaskNewGroupHandler)
    ])
