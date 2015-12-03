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
from config import COUCHDB_URL
from couchdb.design import ViewDefinition

_DOCBASES = ['magkeys', 'invites', 'requestinviteform', 'requestinvite']


_EMPTYKEYS = lambda: dict(
        # _id = magic
          user = ""         # quem convidou
        , magic = ""        # chave mágica
        , email = ""        # e-mail convidado
        , data_convite = "" # data do envio do convite
    )


_EMPTYINVITES = lambda: dict(
        # _id = "user"
        convidado_por = "",
        mkey = "", # mkey usada para se cadastrar
        convites_enviados= [],
            # { "email": "",
            #   "papel": "",
            #   "data_cri": "" }
        comunidades_autorizadas = [],
            # { "login": "",
            #   "numero": "",
            #   "data_cri": "" }
        usuarios_convidados = []    # user_ids
)


_EMPTYREQUESTINVITEFORM = lambda:dict(
# _id = "registry_id/nome_form"
          nome = ""               # Nome é o título sem caracteres especiais
        , titulo = ""             # Título do formulário
        , instrucoes = ""
        , campolivre = ""         # Título do campo livre
                                  # Resposta dada ao usuário após o envio do formulário
        , resposta = u"Sua solicitação de convite foi enviada com sucesso e está em processo de análise."
        , owner = ""              # quem criou o formulário.
        , data_inicio = ""
        , data_encerramento = ""
        , data_cri = ""
        , data_alt = ""
)

_REQUESTINVITEFORM = _EMPTYREQUESTINVITEFORM().keys()
_REQUESTINVITEFORM.remove("nome")
_REQUESTINVITEFORM.remove("owner")
_REQUESTINVITEFORM.remove("data_cri")
_REQUESTINVITEFORM.remove("data_alt")

_EDITREQUESTINVITEFORM = _EMPTYREQUESTINVITEFORM().keys()
_EDITREQUESTINVITEFORM.remove("titulo")
_EDITREQUESTINVITEFORM.remove("nome")
_EDITREQUESTINVITEFORM.remove("owner")
_EDITREQUESTINVITEFORM.remove("data_cri")
_EDITREQUESTINVITEFORM.remove("data_alt")


_EMPTYREQUESTINVITE = lambda:dict(
# _id = couchdb_id
          nome = ""               # Nome do usuário requisitante
        , email = ""              # Email do usuário requisitante
        , campolivre = ""         # Conteúdo do campo livre
        , owner = ""              # Quem criou o formulário 
        , nome_form = ""          # "registry_id/nome_form"
        , estado = ""             # "pendente", "recusado" ou "aprovado"
        , data_cri = ""
)


class Activ(Server):
    "Active database"
    magkeys = {}
    invites = {}
    requestinviteform = {}
    
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
MAGKEYS = __ACTIV.magkeys
INVITES = __ACTIV.invites
REQUESTINVITEFORM = __ACTIV.requestinviteform
REQUESTINVITE = __ACTIV.requestinvite

################################################
# CouchDB Permanent Views
################################################
#
# Retorna todos os formulários de requisição de convites criados por um usuário, incluindo registry_id como parte da chave
#
# Retorno:
# todos os campos de REQUESTINVITEFORM
#
# Uso: model.REQUESTINVITEFORM.view('requestinviteform/all_data',startkey=["usuario1"],endkey=["usuario1", {}])
#

requestinviteform_all_data = ViewDefinition('requestinviteform','all_data', \
                               '''function(doc) { 
                                     emit([doc._id.split("/")[0], doc._id], doc); 
                                   }
                                ''')

#
# Verifica se existem requisições de convites de um formulários criados por um usuário, incluindo registry_id como parte da chave
#
# Retorno:
# todos os campos de REQUESTINVITE
#
# Uso: model.REQUESTINVITE.view('requestinvites/exists',startkey=["usuario1"],endkey=["usuario1", {}])
#

requestinvites_exists = ViewDefinition('requestinvites','exists', \
                               '''function(doc) { 
                                     emit([doc.owner, doc.nome_form, doc._id], null); 
                                   }
                                ''')

#
# Retorna todas as requisições pendentes de convites de todos os formulários criados por um usuário, incluindo registry_id como parte da chave
#
# Retorno:
# todos os campos de REQUESTINVITE
#
# Uso: model.REQUESTINVITE.view('requestinvitespendentes/all_data',startkey=["usuario1"],endkey=["usuario1", {}])
#

requestinvitespendentes_all_data = ViewDefinition('requestinvitespendentes','all_data', \
                               '''function(doc) { 
                                     if (doc.estado=="pendente")
                                         emit([doc.owner, doc.nome_form, doc._id], doc); 
                                   }
                                ''')

#
# Retorna todas as requisições pendentes de convites de todos os formulários criados por um usuário, incluindo registry_id como parte da chave
#
# Retorno:
# todos os campos de REQUESTINVITE
#
# Uso: model.REQUESTINVITE.view('requestinvitespendentes/all_data',startkey=["usuario1"],endkey=["usuario1", {}])
#

requestinvitesrecusados_all_data = ViewDefinition('requestinvitesrecusados','all_data', \
                               '''function(doc) { 
                                     if (doc.estado=="recusado")
                                         emit([doc.owner, doc.nome_form, doc._id], doc); 
                                   }
                                ''')

#
# Retorna todas as requisições pendentes de convites de todos os formulários criados por um usuário, incluindo registry_id como parte da chave
#
# Retorno:
# todos os campos de REQUESTINVITE
#
# Uso: model.REQUESTINVITE.view('requestinvitespendentes/all_data',startkey=["usuario1"],endkey=["usuario1", {}])
#

requestinvitesaprovados_all_data = ViewDefinition('requestinvitesaprovados','all_data', \
                               '''function(doc) { 
                                     if (doc.estado=="aprovado")
                                         emit([doc.owner, doc.nome_form, doc._id], doc); 
                                   }
                                ''')

ViewDefinition.sync_many(REQUESTINVITEFORM, [requestinviteform_all_data])

ViewDefinition.sync_many(REQUESTINVITE, [requestinvitespendentes_all_data, 
                                         requestinvitesrecusados_all_data, 
                                         requestinvitesaprovados_all_data, 
                                         requestinvites_exists])

