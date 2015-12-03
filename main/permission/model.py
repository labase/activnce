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
from config import PLATAFORMA, SERVICES

TXT_PERM = { "community":
               { "acesso_privado": "Somente o dono e os administradores da comunidade",
                 "acesso_grupos": "Somente os grupos especificados por mim",
                 "acesso_comunidade": "Somente os participantes desta comunidade",
                 "acesso_activ": u"Todos os usuários logados no %s"%PLATAFORMA,
                 "acesso_publico": "Todo o mundo"
               },
             "member":
               { "acesso_privado": "Somente eu",
                 "acesso_grupos": "Somente os grupos especificados por mim",
                 "acesso_comunidade": "Somente eu e meus amigos",
                 "acesso_activ": u"Todos os usuários logados no %s"%PLATAFORMA,
                 "acesso_publico": "Todo o mundo"
               }
            }   

def default_permission (mode, service, registry_type, privacidade):
    if mode=="R":
        return {"escopo":SERVICES[registry_type][service]["default_r"][privacidade], "grupos":[]}
    elif mode=="W":
        return {"escopo":SERVICES[registry_type][service]["default_w"][privacidade], "grupos":[]}
    else:
         return {} 
    
"""   
def default_permission (mode, service, registry_id="", user=""):
    if mode=="R":
        if service in ["evaluation", "quiz"]:
            return {"escopo":"acesso_comunidade", "grupos":[]}
        elif service in ["question"]:
            return {"escopo":"acesso_privado", "grupos":[]}
        else:
            return {"escopo":"acesso_activ", "grupos":[]}
        
    elif mode=="W":
        if registry_id != user and service not in ["evaluation", "question", "quiz", "videoaula"]:
            return {"escopo":"acesso_comunidade", "grupos":[]}
        else:
            return {"escopo":"acesso_privado", "grupos":[]}
    else:
         return {} 
"""

def default_all_permissions (service, registry_type, privacidade):

    default_R = default_permission ("R", service, registry_type, privacidade)
    default_W = default_permission ("W", service, registry_type, privacidade)
    
    return ((TXT_PERM[registry_type][default_R["escopo"]], TXT_PERM[registry_type][default_W["escopo"]]))

'''
<!-- ************ Permissões de LEITURA ******************* -->

user
----
"acesso_privado": "Somente eu"
"acesso_grupos": "Somente os grupos especificados por mim" (*) só se tiver GROUPS
"acesso_comunidade": "Somente eu e meus amigos"
"acesso_activ": "Todos os usuários logados no ActivUFRJ"
"acesso_publico": Todo o mundo


community
---------
"acesso_privado": "Somente o dono e os administradores da comunidade"
"acesso_grupos": "Somente os grupos especificados por mim" (*) só se tiver GROUPS
"acesso_comunidade": "Somente os participantes desta comunidade"
"acesso_activ": "Todos os usuários logados no ActivUFRJ"
"acesso_publico": Todo o mundo


        
<!-- ************ Permissões de ESCRITA ******************* -->

user
----
"acesso_privado": "Somente eu"

community
---------
"acesso_privado": "Somente o dono e os administradores da comunidade"
"acesso_grupos": "Somente os grupos especificados por mim" (*) só se tiver GROUPS
"acesso_comunidade": "Somente os participantes desta comunidade"
'''
    
    
    
     
def service_permissions (service, registry_type):
    ''' Retorna uma tupla ([R],[W]) - com as permissões por serviço 
        
        registry_type: "member" ou "community"
        
        Definição:
        acesso_privado: acesso para mim somente ou para os administradores (se comunidade);
        acesso_grupos: acesso para os grupos por mim especificados (dentre os grupos previamente criados);
        acesso_comunidade: acesso para meus amigos (se usuário) ou para os participantes da comunidade;
        acesso_activ: acesso para qualquer usuário logado no activ;
        acesso_publico: pessoas não cadastradas/logadas no activ podem acessar.
    '''
    return ( [(item, TXT_PERM[registry_type][item]) for item in SERVICES[registry_type][service]["perm_r"]],
             [(item, TXT_PERM[registry_type][item]) for item in SERVICES[registry_type][service]["perm_w"]] )
    

    
    
    
    
            
"""                 
def service_permissions (service, is_a_user):
    ''' Retorna uma tupla ([R],[W]) - com as permissões por serviço 
        
        Definição:
        acesso_privado: acesso para mim somente ou para os administradores (se comunidade);
        acesso_grupos: acesso para os grupos por mim especificados (dentre os grupos previamente criados);
        acesso_comunidade: acesso para meus amigos (se usuário) ou para os participantes da comunidade;
        acesso_activ: acesso para qualquer usuário logado no activ;
        acesso_publico: pessoas não cadastradas/logadas no activ podem acessar.
    '''
    
    if is_a_user:
        if service in ["agenda", "videoaula", "bookmarks", "glossary"]:
            return ([ ("acesso_privado", "Somente eu"), # acesso para leitura
                      ("acesso_grupos", "Somente os grupos especificados por mim"),
                      ("acesso_comunidade", "Somente eu e meus amigos"),
                      ("acesso_activ", "Todos os usuários logados no ActivUFRJ")
                    ],
                    [ ("acesso_privado", "Somente eu") # acesso para escrita
                    ])
        else:
            return ([ ("acesso_privado", "Somente eu"), # acesso para leitura
                      ("acesso_grupos", "Somente os grupos especificados por mim"),
                      ("acesso_comunidade", "Somente eu e meus amigos"),
                      ("acesso_activ", "Todos os usuários logados no ActivUFRJ"),
                      ("acesso_publico", "Todo o mundo") 
                    ],
                    [ ("acesso_privado", "Somente eu") # acesso para escrita
                    ])
      
    # comunidades  
    elif service in [ "wiki", "file", "blog"]:
        return ([ ("acesso_privado", "Somente o dono e os administradores da comunidade"), # acesso para leitura
                  ("acesso_grupos", "Somente os grupos especificados por mim"),
                  ("acesso_comunidade", "Somente os participantes desta comunidade"),
                  ("acesso_activ", "Todos os usuários logados no ActivUFRJ"),
                  ("acesso_publico", "Todo o mundo") 
                ],
                [ ("acesso_privado", "Somente o dono e os administradores da comunidade"), # acesso para escrita
                  ("acesso_grupos", "Somente os grupos especificados por mim"),
                  ("acesso_comunidade", "Somente os participantes desta comunidade")
                ])
    elif service in ["agenda", "videoaula", "bookmarks", "glossary"]:
        return ([ ("acesso_privado", "Somente o dono e os administradores da comunidade"), # acesso para leitura
                  ("acesso_grupos", "Somente os grupos especificados por mim"),
                  ("acesso_comunidade", "Somente os participantes desta comunidade"),
                  ("acesso_activ", "Todos os usuários logados no ActivUFRJ")
                ],
                [ ("acesso_privado", "Somente o dono e os administradores da comunidade"), # acesso para escrita
                  ("acesso_grupos", "Somente os grupos especificados por mim"),
                  ("acesso_comunidade", "Somente os participantes desta comunidade")
                ])
    elif service in ["evaluation", "quiz"]:
        return ([ ("acesso_privado", "Somente o dono e os administradores da comunidade"), # acesso para leitura
                  ("acesso_grupos", "Somente os grupos especificados por mim"),
                  ("acesso_comunidade", "Somente os participantes desta comunidade")
                ],
                [ ("acesso_privado", "Somente o dono e os administradores da comunidade")  # acesso para escrita
                ])
    elif service == "question":
        return ([ ("acesso_privado", "Somente o dono e os administradores da comunidade"), # acesso para leitura
                  ("acesso_grupos", "Somente os grupos especificados por mim"),
                  ("acesso_comunidade", "Somente os participantes desta comunidade")
                ],
                [ ("acesso_privado", "Somente o dono e os administradores da comunidade"), # acesso para escrita
                  ("acesso_grupos", "Somente os grupos especificados por mim"),
                  ("acesso_comunidade", "Somente os participantes desta comunidade")
                ])
    else:
         return ([], [])                                            
"""
                                                  
class Permission(Document):
    service        = TextField()    # nome do serviço: wiki, file, blog, etc
    registry_id    = TextField()    # usuário ou comunidade a que o objeto está associado
    nomeobj        = TextField()    # nome do objeto
    owner          = TextField()    # dono do objeto (quem criou o objeto)
    data_cri       = TextField()
    data_alt       = TextField()   
    alterado_por   = TextField()    
    leitura        = DictField()    
                    # { 
                    #   escopo: ("acesso_privado", "acesso_grupos", "acesso_comunidade", "acesso_activ" ou "acesso_publico"),
                    #   grupos: [se escopo=="acesso_grupos" <lista dos nomes dos grupos autorizados> senão vazia] 
                    # }
    escrita        = DictField()    # acesso_comunidade ou <nome_grupo>
                    # { 
                    #   escopo: ("acesso_privado", "acesso_grupos" ou "acesso_comunidade"),
                    #   grupos: [se escopo=="acesso_grupos" <lista dos nomes dos grupos autorizados> senão vazia] 
                    # }
    @property            
    def escopo_R (self):
        return self.leitura["escopo"]
 
    @property            
    def grupos_R (self):
        return self.leitura["grupos"]

    @property            
    def escopo_W (self):
        return self.escrita["escopo"]
 
    @property            
    def grupos_W (self):
        return self.escrita["grupos"]
                        
    def save(self, id=None, db=database.PERMISSION):
        if not self.id and id: self.id = id
        self.store(db)
        
    def retrieve(self, id, db=database.PERMISSION):
        return Permission.load(db, id)
        
    def delete(self, db=database.PERMISSION):
        #db.delete(self)
        del db[self.id]
        
        
        
