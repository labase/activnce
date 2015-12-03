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
from couchdb import Database
from couchdb.design import ViewDefinition

from config import COUCHDB_URL

_DOCBASES = ['news', 'log2', \
             'notification', \
             'notification_error']

      
# ---------------------------------------------------------------------------------------------------------------------------------
#                              Core
#                               |  Wiki
#                               |   |  Blog 
#                               |   |   |  File
#                               |   |   |   |  Mblog
#                               |   |   |   |   |  Recados
#                               |   |   |   |   |   |  Log
#                               |   |   |   |   |   |   |  Chat
#                               |   |   |   |   |   |   |   |  Favoritos
#                               |   |   |   |   |   |   |   |   |  Glossário
#                               |   |   |   |   |   |   |   |   |   |  Community
#                               |   |   |   |   |   |   |   |   |   |   |  Friends
#                               |   |   |   |   |   |   |   |   |   |   |   |  Invites
#                               |   |   |   |   |   |   |   |   |   |   |   |   |  Forum
#                               |   |   |   |   |   |   |   |   |   |   |   |   |   |  Avaliação
#                               |   |   |   |   |   |   |   |   |   |   |   |   |   |   |  Tarefas
#                               |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |  Rating
#                               |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |  Agenda
#                               |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |  Noticia
#                               |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |  Permission (*)
#                               |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |  Search (*)
#                               |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |  Studio (*)  
#                               |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |                                                                        
#                               |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |                                                                           
#                               v   v   v   v   v   v   v   v   v   v   v   v   v   v   v   v   v   v   v   v   v   v   v
# ---------------------------------------------------------------------------------------------------------------------------------
VERBOS_ESCRITA = [
          "aceitou",                                                                        # entrada num grupo da tarefa
          
          "alterou",                
                                # o seu perfil
                                # o perfil da comunidade
                                    # a página
                                        # o blog
                                            # o arquivo
                                                                # um link em favoritos de
                                                                    # um termo no glossário de
                                                                                        # a avaliação
                                                                                            # a tarefa
                                                                                            # uma nota na tarefa
                                                                                                    # um evento na agenda de
                                                                                            
          "avaliou",                                                                            # -
          
          "comentou",               # a página
                                        # no blog
                                            # o arquivo
                                                                # um link de favoritos de
                                                                                            # a tarefa
                                                
          "compartilhou",                       # no mblog de
          
          "convidou",                                                   # um participante para a comunidade
          
          "criou",                  
                                # a comunidade
                                    # a página
                                    # a pasta
                                            # o arquivo
                                            # a pasta
                                                                # um link em favoritos de
                                                                    # um termo no glossário de
                                                                                    # um tópico no forum
                                                                                        # a avaliação
                                                                                            # a tarefa
                                                                                            # um grupo na tarefa
                                                                                                    # um evento na agenda de
                                                                                                        # uma notícia em
                                                                
          "entrou",                                                     # na comunidade
                                                
          "enviou",                                 # recado para
                                                    # recado para todos os usuários do activufrj
                                                                                            # um arquivo na tarefa
          
          "escreveu",                   # no blog
                                                # no mblog de
                                                            # no chat de
                                                        
          "realizou",                                                                   # a avaliação

          "recusou",                                                                        # entrada num grupo da tarefa

          "removeu",                # um comentário da página
                                    # a pasta
                                    # a página
                                    # da lixeira a página
                                        # o post
                                        # um comentário do blog
                                        # da lixeira o post
                                            # um comentário do arquivo
                                            # a pasta
                                            # o arquivo
                                                # uma mensagem do mblog de
                                                    # o recado de
                                                                # um link de favoritos de
                                                                # um comentário do link favorito de
                                                                    # um termo do glossário de
                                                                                    # um tópico do forum
                                                                                    # uma resposta de um tópico do forum
                                                                                        # a avaliação
                                                                                            # a tarefa
                                                                                            # um arquivo da tarefa
                                                                                            # um comentário da tarefa
                                                                                                    # um evento da agenda de
              
          "requisitou",                                                                     # entrada num grupo da tarefa
          
          "respondeu",                                                              # um tópico do forum
          
          "restaurou",              # a página
                                        # o post

          "saiu",                                                       # da comunidade
                                                                                            # saiu de um grupo da tarefa


          #"moveu"                  # a pasta
                                    # a página
                                            # a pasta
                                            # o arquivo
                                                
          #"renomeou"               # a pasta
                                            # a pasta
                                                
          #"cadastrou-se"       # no activufrj
                                # no activufrj pela IntranetUFRJ
                                
                                                                 
          # "trocou"            # sua senha no activufrj
          
          # "solicitou"         # alteração de sua senha no activufrj
         
          # "confirmou"         # a alteração de sua senha no activufrj
]



          #"começou"                                                        # uma amizade com (*)
          #"convidou"                                                       # um usuário para amigo (*)
          #"acessou",                                                       # a lista de amigos de
# -----------------------------------------------------------------------------------
VERBOS_LEITURA = [
          "acessou"                 
                                # o perfil de
                                    # o portfolio de
                                    # o histórico da página
                                    # a lixeira das páginas de
                                    # a página
                                        # o blog de
                                        # o post
                                        # o histórico do post    
                                        # a lixeira do blog de     
                                            # informações do arquivo
                                            # o arquivo
                                                # mblogs de
                                                # menções ao mblog de
                                                        # as novidades de 
                                                        # as suas próprias novidades
                                                                # os favoritos de
                                                                    # o glossário de
                                                                        # a lista de participantes da comunidade
                                                                                    # o forum
                                                                                    # um tópico do forum
                                                                                        # a lista de avaliações
                                                                                        # os resultados das avaliações de
                                                                                        # o resultado da avaliação
                                                                                            # a lista de tarefas de
                                                                                            # a tarefa
                                                                                            # lista de usuarios que já responderam a tarefa
                                                                                            # lista de grupos que já responderam a tarefa
                                                                                            # um arquivo da tarefa
                                                                                            # a lista de grupos da tarefa
                                                                                                    # a agenda de
                                                                                                        # as notícias de
                                                                                                        # uma noticia em
                                                                               
          # "listou"                # as páginas de
                                            # os arquivos de 
                                                
          # "entrou"            # no activufrj
                                # no activufrj pela IntranetUFRJ
          # "saiu"              # do activufrj
          
]        
# -----------------------------------------------------------------------------------






# ------ Novidades ----------------------------------------------

_EMPTYNEWS = lambda: dict(
         avisos = []
     )
# _id = usuário que deve receber a novidade
#avisos = [ {
#               sujeito: "",
#               verbo: "",
#               objeto: "",
#               tipo: "",
#               data_inclusao: ""
#            }
#          ]


_EMPTYLOG = lambda: dict(
                         sujeito = "",
                         verbo = "",
                         objeto = "",
                         tipo = "",
                         link = "",
                         news = "",
                         data_inclusao = ""
)



# ------ Notificação por email ----------------------------------

_EMPTYNOTIFICATION = lambda: dict(
          registros = []
     )
# _id = usuário que deve ser notificado
#registros = [ {
#                  sujeito: "",
#                  subject: "",
#                  message: "",
#                  data_inclusao: "",
#              }
#            ]


_EMPTYNOTIFICATIONERROR = lambda: dict(
          registros = []
     )
# _id = usuário que deve ser notificado
#registros = [ {
#                  sujeito: "",
#                  subject: "",
#                  message: "",
#                  data_inclusao: "",
#              }
#            ]


class Activ(Server):
    "Active database"
    news = {}
    log = {}

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
NEWS = __ACTIV.news
LOG = __ACTIV.log2
NOTIFICATION = __ACTIV.notification
NOTIFICATIONERROR = __ACTIV.notification_error

# Variáveis temporárias onde LOG e NEWS são armazenados até que a thread faça a persistência no DB
#TEMP_LOG = {}
TEMP_LOG = []
TEMP_NEWS = {}




################################################
# CouchDB Permanent Views
################################################


# Permite obter a totalização de acessos ao activ por dia e por hora, num dado intervalo de datas
# Utilizado para gerar estatísticas de acesso para o administrador do activ
#
#
# Uso: LOG.view('log/total_by_day',startkey=[data_inicial], endkey=[data_final, {}], group="true", group_level=1)

total_by_day = ViewDefinition('log','total_by_day', \
                               '''function(doc) { 
                                       data_hora = doc.data_inclusao.split(" ");
                                       emit([data_hora[0], data_hora[1].substr(0,2), data_hora[1].substr(3)],  1);
                                   }
                                ''',
                                '''
                                function(keys, values) {
                                   return sum(values);
                                }
                                ''')

total_by_user = ViewDefinition('log','total_by_user', \
                               '''function(doc) { 
                                       data_hora = doc.data_inclusao.split(" ");
                                       emit([data_hora[0], doc.sujeito, data_hora[1].substr(0,2), data_hora[1].substr(3)],  1);
                                   }
                                ''',
                                '''
                                function(keys, values) {
                                   return sum(values);
                                }
                                ''')

# Uso: LOG.view('log/total_by_hour',startkey=[0,data_inicial], endkey=[23,data_final, {}], group="true", group_level=1)
"""
total_by_hour = ViewDefinition('log','total_by_hour', \
                               '''function(doc) { 
                                       data_hora = doc.data_inclusao.split(" ");
                                       emit([data_hora[1].substr(0,2), data_hora[0], data_hora[1].substr(3)],  1);
                                   }
                                ''',
                                '''
                                function(keys, values) {
                                   return sum(values);
                                }
                                ''')
"""
# Permite obter a data de última operação realizada num registry_id
# Utilizado para ordenação das comunidades 
#
#
# Uso: LOG.view('log/log_by_object',startkey=["turma1"], endkey=["turma1", {}])

log_by_object = ViewDefinition('log','log_by_object', \
                               '''function(doc) { 
                                       if (doc.objeto) {
                                           emit([doc.objeto.split("/")[0], doc.data_inclusao],  null);
                                       }
                                   }
                                ''')

# Permite obter todas as ações realizadas por um usuário
#
#
# Uso: LOG.view('log/log_list',startkey=["user1"], endkey=["user1", {}])

log_list = ViewDefinition('log','log_list', \
                                '''function(doc) { 
                                      emit([doc.sujeito, doc.data_inclusao, doc._id],  doc);
                                   }
                                ''')

# Permite obter todas as ações realizadas por um usuário que foram para news de seus amigos 
#
#
# Uso: LOG.view('log/log_list',startkey=["user1"], endkey=["user1", {}])

log_list_news = ViewDefinition('log','log_list_news', \
                                '''function(doc) { 
                                      if (doc.news=="True")
                                          emit([doc.sujeito, doc.data_inclusao, doc._id],  doc);
                                   }
                                ''')

#
# Estatísticas...
#
#
# Uso: LOG.view('log/stats_by_user',startkey=["turma1", "wiki"], endkey=["turma1", "wiki", {}, {}], group="true")

log_stats_by_user = ViewDefinition('log','stats_by_user', \
                               '''function(doc) { 
                                       if (doc.objeto) { 
                                           emit([doc.objeto.split("/")[0], doc.tipo, doc.data_inclusao.split(" ")[0], doc.sujeito, doc.verbo.split(" ")[0]], 1);
                                       }
                                   }
                                ''',
                                '''
                                function(keys, values) {
                                   return sum(values);
                                }
                                ''')


log_stats_by_all_users = ViewDefinition('log','stats_by_all_users', \
                               '''function(doc) { 
                                       if (doc.objeto) {
                                           emit([doc.objeto.split("/")[0], doc.data_inclusao.split(" ")[0], doc.sujeito, doc.verbo.split(" ")[0]],  1);
                                       }
                                   }
                                ''',
                                '''
                                function(keys, values) {
                                   return sum(values);
                                }
                                ''')

log_stats_by_object = ViewDefinition('log','stats_by_object', \
                               '''function(doc) { 
                                       if (doc.objeto) { 
                                           if(doc.objeto.split("/")[1]){
                                               emit([doc.objeto.split("/")[0], doc.tipo, doc.data_inclusao.split(" ")[0], doc.objeto.split("/")[1], doc.verbo.split(" ")[0]], 1);
                                           }
                                       }
                                   }
                                ''',
                                '''
                                function(keys, values) {
                                   return sum(values);
                                }
                                ''')

log_stats_by_all_objects = ViewDefinition('log','stats_by_all_objects', \
                               '''function(doc) { 
                                       if (doc.objeto) {
                                           if(doc.objeto.split("/")[1]){
                                                emit([doc.objeto.split("/")[0], doc.data_inclusao.split(" ")[0], doc.objeto.split("/")[1], doc.verbo.split(" ")[0], doc.tipo],  1);
                                           }
                                       }
                                   }
                                ''',
                                '''
                                function(keys, values) {
                                   return sum(values);
                                }
                                ''')

log_users_by_all_types_bar_chart = ViewDefinition('log','users_by_all_types_bar_chart', \
                               '''function(doc) { 
                                       var VERBOS_LEITURA = %s;
                                       var VERBOS_ESCRITA = %s;
                                       if (doc.objeto) {
                                        
                                           if(VERBOS_LEITURA.indexOf(doc.verbo.split(" ")[0]) != -1){
                                                emit([doc.objeto.split("/")[0], doc.data_inclusao.split(" ")[0], doc.sujeito, "leitura", doc.tipo],  1);
                                            }
                                            else if(VERBOS_ESCRITA.indexOf(doc.verbo.split(" ")[0]) != -1){
                                                emit([doc.objeto.split("/")[0], doc.data_inclusao.split(" ")[0], doc.sujeito, "escrita", doc.tipo],  1);
                                            }                                      
                                       }
                                   }
                                '''%(VERBOS_LEITURA, VERBOS_ESCRITA),
                                '''
                                function(keys, values) {
                                    return sum(values);
                                }
                                ''')


log_objects_by_all_types_bar_chart = ViewDefinition('log','objects_by_all_types_bar_chart', \
                               '''function(doc) { 
                                       var VERBOS_LEITURA = %s;
                                       var VERBOS_ESCRITA = %s;
                                       if (doc.objeto) {
                                           if(doc.objeto.split("/")[1]){
                                               if(VERBOS_LEITURA.indexOf(doc.verbo.split(" ")[0]) != -1){
                                                    emit([doc.objeto.split("/")[0], doc.data_inclusao.split(" ")[0], doc.objeto.split("/")[1], "leitura", doc.tipo],  1);
                                                }
                                                else if(VERBOS_ESCRITA.indexOf(doc.verbo.split(" ")[0]) != -1){
                                                    emit([doc.objeto.split("/")[0], doc.data_inclusao.split(" ")[0], doc.objeto.split("/")[1], "escrita", doc.tipo],  1);
                                                }
                                           }
                                       }
                                   }
                                '''%(VERBOS_LEITURA, VERBOS_ESCRITA),
                                '''
                                function(keys, values) {
                                    return sum(values);
                                }
                                ''')


log_users_by_types_bar_chart = ViewDefinition('log','users_by_types_bar_chart', \
                               '''function(doc) { 
                                       var VERBOS_LEITURA = %s;
                                       var VERBOS_ESCRITA = %s;
                                       if (doc.objeto) {
                                           if(VERBOS_LEITURA.indexOf(doc.verbo.split(" ")[0]) != -1){
                                                emit([doc.objeto.split("/")[0], doc.tipo, doc.data_inclusao.split(" ")[0], doc.sujeito, "leitura"],  1);
                                            }
                                            else if(VERBOS_ESCRITA.indexOf(doc.verbo.split(" ")[0]) != -1){
                                                emit([doc.objeto.split("/")[0], doc.tipo, doc.data_inclusao.split(" ")[0], doc.sujeito, "escrita"],  1);
                                            }
                                       }                                  
                                   }
                                '''%(VERBOS_LEITURA, VERBOS_ESCRITA),
                                '''
                                function(keys, values) {
                                    return sum(values);
                                }
                                ''')

log_objects_by_types_bar_chart = ViewDefinition('log','objects_by_types_bar_chart', \
                               '''function(doc) { 
                                       var VERBOS_LEITURA = %s;
                                       var VERBOS_ESCRITA = %s;
                                       if (doc.objeto) {
                                           if(doc.objeto.split("/")[1]){
                                               if(VERBOS_LEITURA.indexOf(doc.verbo.split(" ")[0]) != -1){
                                                    emit([doc.objeto.split("/")[0], doc.tipo, doc.data_inclusao.split(" ")[0], doc.objeto.split("/")[1], "leitura"],  1);
                                                }
                                                else if(VERBOS_ESCRITA.indexOf(doc.verbo.split(" ")[0]) != -1){
                                                    emit([doc.objeto.split("/")[0], doc.tipo, doc.data_inclusao.split(" ")[0], doc.objeto.split("/")[1], "escrita"],  1);
                                                }
                                           }
                                       }
                                   }
                                '''%(VERBOS_LEITURA, VERBOS_ESCRITA),
                                '''
                                function(keys, values) {
                                    return sum(values);
                                }
                                ''')

ViewDefinition.sync_many(LOG, [total_by_day, total_by_user, \
                               log_by_object, log_list, log_list_news, \
                               log_stats_by_user, log_stats_by_all_users, \
                               log_stats_by_object, log_stats_by_all_objects, \
                               log_objects_by_all_types_bar_chart, log_users_by_all_types_bar_chart,\
                               log_users_by_types_bar_chart,log_objects_by_types_bar_chart])

