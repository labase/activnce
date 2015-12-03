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

#from tornado.httpclient import HTTPError
import model

from config import PLATAFORMA, COUCHDB_URL, USER_ADMIN, PRIVILEGIOS


PASSWD_USER_SUSPENDED = "***USER SUSPENDED***"

_DOCBASES = ['registry', 'dbintranet', 'forgottenpasswd', 'activdb']


class Activ(Server):
    "Active database"
    #registry = {}

    def __init__(self, url):
        print "iniciando o servidor..."
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

    def version_couchdb_010(self):
        return isinstance(self.version, str) and \
               (self.version=="0.10.0" or self.version=="1.0.1")


__ACTIV = Activ(COUCHDB_URL)
REGISTRY = __ACTIV.registry
ACTIVDB = __ACTIV.activdb
DBINTRANET = __ACTIV.dbintranet
FORGOTTENPASSWD = __ACTIV.forgottenpasswd
DB_VERSAO_010 = __ACTIV.version_couchdb_010()



################################################
# CouchDB permanent views from registry database
################################################

# Permite verificar se um usuário existe no REGISTRY (case insensitive)
#
# Uso: 
# database.REGISTRY.view('registry/exists',key=registry_id.lower())

registry_exists = ViewDefinition('registry','exists', \
                          '''function(doc) { 
                                 emit(doc._id.toLowerCase(), null); 
                             }
                          ''')


# Permite verificar o tipo de um registry_id ("member", "suspended" ou "community")
#
# Uso: 
# database.REGISTRY.view('registry/type',key=registry_id)

registry_type = ViewDefinition('registry', 'type', \
                          '''function(doc) { 
                                emit(doc._id, {type: doc.type, subtype:doc.subtype, privacidade:doc.privacidade});
                             }
                          ''')




# Permite verificar se um usuário existe no REGISTRY
#
# Uso: 
# database.REGISTRY.view('users/exists',key=registry_id)

users_exists = ViewDefinition('users','exists', \
                          '''function(doc) { 
                                if (doc.type=="member" && doc.subtype!="suspended")
                                   emit(doc._id, null); 
                             }
                          ''')


# Permite verificar total de cadastrados no activ
#
# Uso: database.REGISTRY.view('users/by_origin', group="true")

users_origin = ViewDefinition('users','by_origin', \
                          '''function(doc) { 
                                if (doc.type=="member") 
                                    if (doc.origin)
                                        emit(doc.origin, 1) 
                                    else if (doc.subtype=="suspended")
                                        emit("usuario desativado", 1)
                                    else
                                        emit("convidado", 1); 
                             }
                          ''',
                          '''
                            function(keys, values) {
                               return sum(values);
                            }
                          ''')


# Busca id do usuário pelo email (exclui as comunidades e usuários suspensos)
#
# Uso: 
# database.REGISTRY.view('users_by_email/exists',key=email)

users_by_email = ViewDefinition('users','by_email', \
                               '''function(doc) { 
                                     if (doc.type=="member" && doc.subtype!="suspended")
                                        emit(doc.email, doc._id); 
                                  }
                               ''')



# Busca id do usuário pelo CPF (exclui as comunidades e usuários suspensos)
#
# Uso: 
# database.REGISTRY.view('users_by_cpf/exists',key=cpf)

users_by_cpf = ViewDefinition('users', 'by_cpf', \
                               '''function(doc) { 
                                     if (doc.type=="member" && doc.subtype!="suspended" && doc.cpf!="")
                                        emit(doc.cpf, doc._id); 
                                  }
                               ''')


# Permite verfificar se um usuário participa de uma comunidade
#
# Uso: 
# database.REGISTRY.view('users/ismemberof',key=[user, registry_id])

users_ismemberof = ViewDefinition('users','ismemberof', \
                          '''
                          function(doc) { 
                             if (doc.type=="community")
                                for (c in doc.participantes)
                                   emit([doc.participantes[c], doc._id], null); 
                           }
                           ''')


# Permite verfificar se um usuário é dono ou admin de uma comunidade
#
# Uso: 
# database.REGISTRY.view('users/isowner',key=[user, registry_id])

users_isowner = ViewDefinition('users','isowner', \
                          '''
                          function(doc) { 
                             if (doc.type=="community"){
                                emit([doc.owner, doc._id], null); 
                                for (c in doc.admins)
                                   emit([doc.admins[c], doc._id], null);
                             }
                          }
                           ''')


# Permite verificar se um usuário é amigo de outro
#
# Uso: 
# database.REGISTRY.view('users/isfriend',key=[user, registry_id])

users_isfriend = ViewDefinition('users','isfriend', \
                          '''
                          function(doc) { 
                             if (doc.type=="member" && doc.subtype!="suspended"){
                                for (c in doc.amigos)
                                   emit([doc.amigos[c], doc._id], null);
                             }
                          }
                           ''')


# Retorna lista de amigos de um usuário com todas as informações adicionais
# para exibir no painel de controle
#
# Uso: 
# database.REGISTRY.view('users/friends',key=[user, registry_id])


users_friends = ViewDefinition('users', 'friends', \
                          '''
                          function(doc) { 
                             if (doc.type=="member" && doc.subtype!="suspended"){
                                emit([doc._id, 0], {friends: doc.amigos});
                                for (a in doc.amigos)
                                   emit([doc.amigos[a], 1], {user: doc._id, full_name: doc.name+' '+doc.lastname});
                             }
                          }
                           ''')


# Retorna lista de comunidades das quais um usuário participa, com todas as informações adicionais
# para exibir no painel de controle

users_communities = ViewDefinition('users', 'communities', \
                          '''
                          function(doc) { 
                             if (doc.type=="member"){
                                 if (doc.subtype!="suspended"){
                                    emit([doc._id, 0], {communities: doc.comunidades});
                                }
                             }
                             else {
                                for (p in doc.participantes)
                                   emit([doc.participantes[p], 1], {community: doc._id, description: doc.description, owner: doc.owner});                             
                             }
                          }
                           ''')

# Todos os usuários do REGISTRY que não sejam Privados
# Retorna apenas nome_completo e email.
# user_id: {
#    nome_completo (name+lastname), 
#    email
# }

users_partial_data = ViewDefinition('users','partial_data', \
                                    '''function(doc) { 
                                          if (doc.type=="member" && doc.subtype!="suspended" && doc.privacidade!="Privada") 
                                             emit(doc._id, {nome_completo: doc.name+' '+doc.lastname, email: doc.email}); 
                                       }
                                    ''')




# Retorna lista de emails chamados para a plataforma para participar de uma comunidade
#
# Uso: 
# database.REGISTRY.view('called/by_email',startkey=[email], endkey=[email, {}])


called_by_email = ViewDefinition('called', 'by_email', \
                          '''
                          function(doc) { 
                             if (doc.type=="community"){
                                for (c in doc.participantes_chamados)
                                   emit([doc.participantes_chamados[c], doc._id, doc.participacao], null);
                             }
                          }
                           ''')


# Permite verificar se uma comunidade existe no REGISTRY
#
# Retorno:
# community_id: null
# True se existe, False se não existe
#
# Uso: 
# database.REGISTRY.view('communities/exists',key=registry_id)

communities_exists = ViewDefinition('communities','exists', \
                                  '''function(doc) { 
                                        if (doc.type=="community")
                                           emit(doc._id, null); 
                                     }
                                  ''')


# Retorna lista de participantes de uma comunidade, com todas as informações adicionais
# para exibir no painel de controle

communities_members = ViewDefinition('communities', 'members', \
                          '''
                          function(doc) { 
                             if (doc.type=="community"){
                                emit([doc._id, 0], {members: doc.participantes});
                             }
                             else if (doc.type=="member" && doc.subtype!="suspended") {
                                for (c in doc.comunidades) 
                                   emit([doc.comunidades[c], 1], {user: doc._id, full_name: doc.name+' '+doc.lastname});                             
                             }
                          }
                           ''')


# Todos as comunidades do REGISTRY que não sejam Privadas nem Obrigatórias
# Retorna apenas descricao e participacao.
# community_id: {
#     descricao:
#     participacao:
# }

communities_partial_data = ViewDefinition('communities','partial_data', \
                          u'''
                          function(doc) { 
                             if (doc.type=="community" && doc.privacidade!="Privada") 
                                 emit(doc._id, 
                                      {description: doc.description, participacao: doc.participacao}); 
                           }
                           ''')


# Todos as comunidades do REGISTRY
# Retorna apenas descricao e participacao.
# community_id: {
#     descricao:
#     participacao:
# }

communities_partial_data_of_all = ViewDefinition('communities','partial_data_of_all', \
                          u'''
                          function(doc) { 
                             if (doc.type=="community") 
                                 emit(doc._id, 
                                      {description: doc.description, owner: doc.owner, privacidade: doc.privacidade, participacao: doc.participacao}); 
                           }
                           ''')



ViewDefinition.sync_many(REGISTRY, [
                                    registry_exists, \
                                    registry_type \
                                    ])

ViewDefinition.sync_many(REGISTRY, [
                                    users_exists, \
                                    users_origin, \
                                    users_by_email, \
                                    users_by_cpf, \
                                    users_ismemberof, \

                                    users_isowner, \
                                    users_isfriend, \
                                    users_friends, \
                                    users_communities, \
                                    users_partial_data, \
                                    ])

ViewDefinition.sync_many(REGISTRY, [
                                    called_by_email, \
                                    communities_exists, \
                                    communities_members, \
                                    communities_partial_data, \
                                    communities_partial_data_of_all \
                                    ])



################################################
# CouchDB permanent views from activdb database
################################################
#
# Verifica se um objeto com type/registry_id/name_id já existe no activdb
#
#
# Uso: core.database.ACTIVDB.view('object/exists', key=["videoaula","videoaula","mauricio","name_id"])
#
registry_id_has_objects = ViewDefinition('registry_id','has_objects', \
                               '''function(doc) {
                                       emit([doc.registry_id, doc._id], null );
                                    }
                                ''')


#
# Verifica se um objeto com type/registry_id/name_id já existe no activdb
#
#
# Uso: core.database.ACTIVDB.view('object/exists', key=["videoaula","videoaula","mauricio","name_id"])
#
object_exists = ViewDefinition('object','exists', \
                               '''function(doc) {
                                       emit([doc.service, doc.type, doc.registry_id, doc.name_id], null );
                                    }
                                ''')

# Retorna todas os objetos incluindo registry_id como parte da chave
# Permite obter todos os objetos de um determinado registry_id·
#
#
# Uso: core.database.ACTIVDB.view('objects/by_registry_id', startkey=["videoaula","mauricio"], endkey=["videoaula","mauricio", {}])
#      core.database.ACTIVDB.view('objects/by_registry_id', key=[type,registry_id,name_id])
#
objects_by_registry_id = ViewDefinition('objects','by_registry_id', \
                               '''function(doc) {
                                       emit([doc.service, doc.type, doc.registry_id, doc.name_id], doc );
                                    }
                               ''')

objects_by_subtype_and_registry_id = ViewDefinition('objects','by_subtype_and_registry_id', \
                               '''function(doc) {
                                       emit([doc.service, doc.type, doc.subtype, doc.registry_id, doc.name_id], doc );
                                    }
                               ''')

# Conta número total de objetos de um determinado registry_id
#
#
# Uso: core.database.ACTIVDB.view('objects/count',key=["videoaula","mauricio"], group="true")
#
objects_count = ViewDefinition('objects','count', \
                               '''function(doc) { 
                                      emit([doc.service, doc.type, doc.registry_id], 1);
                                  }
                                ''',
                               u'''
                                function(keys, values) {
                                   return sum(values);
                                }
                                ''')

objects_count_by_subtype = ViewDefinition('objects','count_by_subtype', \
                               '''function(doc) { 
                                      emit([doc.service, doc.type, doc.subtype, doc.registry_id], 1);
                                  }
                                ''',
                               u'''
                                function(keys, values) {
                                   return sum(values);
                                }
                                ''')


# Retorna todos os objetos incluindo registry_id e tags como parte da chave
# Permite obter todos os objetos com a tag escolhida de um determinado registry_id·
#
#
# Uso: core.database.ACTIVDB.view('objects/by_registry_id_and_tag',startkey=["videoaula","mauricio"],endkey=["videoaula","mauricio", {}])
#
objects_by_registry_id_and_tag = ViewDefinition('objects','by_registry_id_and_tag', \
                                '''function(doc) { 
                                        for (t in doc.tags)
                                           emit([doc.service, doc.type, doc.registry_id, doc.tags[t], doc.data_alt, doc._id], doc);
                                   }
                                ''')

objects_by_subtype_registry_id_and_tag = ViewDefinition('objects','by_subtype_registry_id_and_tag', \
                                '''function(doc) { 
                                        for (t in doc.tags)
                                           emit([doc.service, doc.type, doc.subtype, doc.registry_id, doc.tags[t], doc.data_alt, doc._id], doc);
                                   }
                                ''')

# Conta número total de questões de um determinado registry_id·e de uma determinada tag
#
#
# Uso: core.database.ACTIVDB.view('objects/count_by_registry_id_and_tag',startkey=["mauricio","tag"],endkey=["mauricio", "tag", {}, group_level=1, group="true")
#
objects_count_by_registry_id_and_tag = ViewDefinition('objects','count_by_registry_id_and_tag', \
                               '''function(doc) { 
                                       for (t in doc.tags)
                                           emit([doc.service, doc.type, doc.registry_id, doc.tags[t], doc._id], 1);
                                   }
                                ''',
                                '''function(keys, values, rereduce) {
                                  if (rereduce) {
                                    return sum(values);
                                  } else {
                                    return values.length;
                                  }
                                }
                                ''')

              

# Retorna lista de objetos por grupo
# 
# Uso: database.ACTIVDB.view('objects/by_group',startkey=[service,registry_id],endkey=[{}])



objects_by_group = ViewDefinition('objects', 'by_group', \
                            '''
                              function(doc) {
                                     if (doc.group_id) {
                                        emit ([doc.service, doc.registry_id, doc.group_id, doc.data_cri, 1], doc);
                                     }
                                     else {
                                        emit ([doc.service, doc.registry_id, doc._id, doc.data_cri, 0], doc);
                                     }
                               }
                            ''')   


# Retorna lista de objetos por grupo
# 
# Uso: database.ACTIVDB.view('objects/by_group',startkey=[service,registry_id],endkey=[{}])

groups_total_itens = ViewDefinition('groups', 'total_itens', \
                            '''
                              function(doc) {
                                     if (doc.group_id) {
                                        emit (doc.group_id, 1);
                                     }
                               }
                            ''',
                            '''
                                function(keys, values) {
                                   return sum(values);
                                }
                            ''')  


# Retorna lista de objetos por grupo e por tag
# 
# Uso: database.ACTIVDB.view('objects/by_group_and_tag',startkey=[service,registry_id,tag],endkey=[{}])

objects_by_group_and_tag = ViewDefinition('objects', 'by_group_and_tag', \
                            '''
                              function(doc) {
                                     if (doc.group_id) {
                                        emit ([doc.service, doc.registry_id, "", doc.group_id, 1], doc);
                                     }
                                     else {
                                        for (t in doc.tags)
                                            emit ([doc.service, doc.registry_id, doc.tags[t], doc._id, 0], doc);
                                     }
                               }
                            ''')   


ViewDefinition.sync_many(ACTIVDB, [ registry_id_has_objects, \
                                    object_exists, \
                                    objects_by_registry_id, \
                                    objects_by_subtype_and_registry_id, \
                                    objects_count, \
                                    objects_count_by_subtype, \
                                    objects_by_registry_id_and_tag, \
                                    objects_by_subtype_registry_id_and_tag, \
                                    objects_count_by_registry_id_and_tag, \
                                    objects_by_group, \
                                    objects_by_group_and_tag, \
                                    groups_total_itens \
                                    ])



  




