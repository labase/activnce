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
from couchdb import Server
from couchdb.design import ViewDefinition

from config import COUCHDB_URL

_DOCBASES = ['task', 'taskfiles']

class Activ(Server):
    "Active database"
    task = {}
    taskfiles = {}
    
    def __init__(self, url):
        Server.__init__(self, url)
        act = self
        test_and_create = lambda doc: doc in act and act[doc] or act.create(doc)
        for attribute in _DOCBASES:
            setattr(Activ, attribute, test_and_create(attribute))

    def erase_database(self):
        'erase tables'
        for table in _DOCBASES:
            try:
                del self[table]
            except:
                pass


__ACTIV = Activ(COUCHDB_URL)
TASK = __ACTIV.task
TASKFILES = __ACTIV.taskfiles

################################################
# CouchDB Permanent Views
################################################
#
# Retorna todas as tarefas de uma comunidade incluindo registry_id como parte da chave
#
# Retorno:
# todos os campos de TASK
#
# Uso: model.TASK.view('task/all_data',startkey=["comunidade1"],endkey=["comunidade1", {}])
#

task_all_data = ViewDefinition('task','all_data', \
                               '''function(doc) { 
                                     emit([doc._id.split("/")[0], doc._id], doc); 
                                   }
                                ''')


#
# Retorna todas as tarefas de uma comunidade, com o nome da comunidade e o nome da tarefa como parte da chave
#
# Retorno:
# todas as tarefas de uma comunidade
#
# Uso: model.TASK.view('task/by_id',startkey=["comunidade1", "tarefa1"],endkey=["comunidade1", "tarefa1", {}])
#

task_by_id = ViewDefinition('task','by_id', \
                               '''function(doc) { 
                                     emit([doc._id.split("/")[0], doc._id.split("/")[1]], null);
                                   }
                                ''')

# Retorna se existe um arquivo chamado filename em uma tarefa de uma comunidade
#
# Retorno:
# 
#
# Uso: database.TASKFILES.view('taskfiles/filename_exists',startkey=[registry_id,file_id,filename],endkey=[registry_id,file_id,filename, {}])
#
taskfiles_filename_exists = ViewDefinition('taskfiles','filename_exists', \
                               '''function(doc) {
                                        for (file in doc.filenames)
                                            emit([doc.registry_id, doc._id, doc.filenames[file][0]], null); 
                                   }
                                ''')


# Permite encontrar um comentário de uma tarefa
#
# Retorno:
# Comentário
#
# Uso: 
# database.TASKFILES.view('taskfiles/comment',key=[doc_id, user, data_cri])

task_comment = ViewDefinition('taskfiles','comment', \
                          '''
                          function(doc) { 
                            for (c in doc.comentarios)
                               emit([doc._id, doc.comentarios[c]['owner'], doc.comentarios[c]['data_cri']], doc.comentarios[c]['comment']);
                          }
                           ''')

#
# Retorna todos os registros de TASKFILES pertencentes à task a qual se refere como chave
#
#
# Retorno:
# Taskfiles
#
# Uso: database.TASKFILES.view('taskfiles/by_task',startkey=[registry_id, task],endkey=[registry_id, task, {}]):
#
taskfiles_by_task = ViewDefinition('taskfiles','by_task', \
                               '''function(doc) { 
                                     emit([doc.registry_id, doc.task], doc); 
                                   }
                                ''')

#
# Retorna se um usuário é participante de um grupo de tarefa
# Permite obter o nome do grupo a qual o participante pertence, bem como o id da to taskfile assosciado
#
# Retorno:
# id do taskfile, nome do grupo
#
# Uso: database.TASKFILES.view('taskfiles/by_participante',startkey=[registry_id, task, participante],endkey=[registry_id, task, participante, {}]):
#
taskfiles_by_participante = ViewDefinition('taskfiles','by_participante', \
                               '''function(doc) { 
                                     for (part in doc.participantes)
                                         emit([doc.registry_id, doc.task, doc.participantes[part]], 
                                         { id : doc._id,
                                           group : doc.nome_grupo}); 
                                   }
                                ''')

#
# Retorna todos os grupos de uma determinada tarefa em uma comunidade
#
# Retorno:
# id do taskfile ao qual o grupo pertence
#
# Uso: database.TASKFILES.view('taskfiles/by_group',startkey=[registry_id, task, nome_grupo],endkey=[registry_id, task, nome_grupo, {}]):
#
taskfiles_by_group = ViewDefinition('taskfiles','by_group', \
                               '''function(doc) { 
                                     emit([doc.registry_id, doc.task, doc.nome_grupo],
                                     { id : doc._id}); 
                                   }
                                ''')

#
# Retorna se um usuario faz parte da lista de participantes de um grupo
# Permite obter o id do taskfile ao qual o usuário pertence
#
# Retorno:
# taskfile id
#
# Uso: database.TASKFILES.view('taskfiles/by_lista_participantes',startkey=[registry_id, task, usuario],endkey=[registry_id, task, usuario, {}]):
#
taskfiles_by_lista_participantes = ViewDefinition('taskfiles','by_lista_participantes', \
                               '''function(doc) { 
                                     emit([doc.registry_id, doc.task, doc.participantes], doc._id); 
                                   }
                                ''')

#
# Retorna se o usuario esta na lista de participantes pendentes de um grupo
# Permite obter o nome dos grupos e o id dos taskfiles aos quais o usuario pertence
#
# Retorno:
# nome do grupo e id do taskfile
#
# Uso: database.TASKFILES.view('taskfiles/by_participantes_pendentes',startkey=[registry_id, task, usuario],endkey=[registry_id, task, usuario, {}]):
#
taskfiles_by_participantes_pendentes = ViewDefinition('taskfiles','by_participantes_pendentes', \
                               '''function(doc) {
                                    for (part in doc.participantes_pendentes)
                                     emit([doc.registry_id, doc.task, doc.participantes_pendentes[part]],
                                         {id : doc._id,
                                           group : doc.nome_grupo});
                                   }
                                ''')

ViewDefinition.sync_many(TASK, [task_all_data, task_by_id])
ViewDefinition.sync_many(TASKFILES, [task_comment, taskfiles_by_task, taskfiles_by_participante, taskfiles_by_group, taskfiles_by_lista_participantes, \
                                     taskfiles_filename_exists, taskfiles_by_participantes_pendentes])
