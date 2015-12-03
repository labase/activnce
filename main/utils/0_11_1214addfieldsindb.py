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

_DOCBASES = ['files', \
             'wiki', 
             'registry']


_EMPTYWIKI = lambda:dict(
# _id = "registry_id/nome_pagina"
          user = ""           # usuário ou comunidade (registry_id).
        , registry_id = ""    # usuário ou comunidade (registry_id).
        , owner = ""          # quem criou.
                              # caso wiki seja de uma comunidade, owner!=registry_id
        , nomepag = u"Nova Página"
        , nomepag_id = "NovaPagina"
        , conteudo = u"Entre aqui com o conteúdo da sua página. <br/>"
        , edicao_publica = ""   # Se "S" qq participante pode editar, 
                                # se "N" só o dono da página e os admins da comunidade.
        , tags = []
        , data_cri = ""         # data de criação da página
        , data_alt = ""         # data da última alteração
        , alterado_por = ""     # quem alterou a pag pela última vez
        , comentarios = []
        , acesso_publico = "N"  # "S" ou "N": indica se a página pode ser acessada
                                # de fora da plataforma
)

_EMPTYFILES = lambda:dict(
# _id = "registry_id/nome_arquivo"
# _attachments = <conteúdo do arquivo armazenado>
          user = ""           # usuário que fez o upload do arquivo,
                              # esta chave era do bd antigo = owner novo
        , registry_id = ""    # dono do arquivo: usuário ou comunidade
        , owner = ""          # quem fez upload.
                              # caso file seja de uma comunidade, owner!=registry_id
        , filename = ""
        , description = ""
        , tags = []
        , data_upload = ""
        , data_alt = ""
        , alterado_por = ""
        , comentarios = []
        , acesso_publico = "N"  # "S" ou "N": indica se a página pode ser acessada
                                # de fora da plataforma
)


_EMPTYMEMBER = lambda: dict(
          user = ""
        , passwd = ""
        , name = ""
        , lastname = ""
        , email = ""
        , tags = [] 
        , description = ""
        , photo = ""
        , cod_institute = ""
        , institute = ""
        , amigos = []
        , amigos_pendentes = []
        , amigos_convidados = []
        , comunidades = []
        , comunidades_pendentes = []
        , papeis = []
        , mykeys = []
        , privacidade = u"Pública"           # Pode ser: Pública ou Privada
        , blog_aberto = "N"                  # Indica se o blog deste usuário 
                                             # pode ser acessado de fora da plataforma
        , upload_quota = 10 * 1024 * 1024    # max 10 Mb
        , upload_size = 0  
        , notify = "2"  # notificações de e-mail
                        # 0 = não receber
                        # 1 = receber apenas um boletim semanal
                        # 2 = receber sempre
        , data_cri = ""
        , data_alt = ""
    )

_EMPTYCOMMUNITY = lambda: dict(
          name = ""
        , description = ""
        , tags = []
        , owner = ""
        , photo = ""
        , participantes_pendentes = []
        , participantes = []
        , comunidades = []                   # comunidades em que esta comunidade está incluída
        , upload_quota = 60 * 1024 * 1024    # max 60 Mb
        , upload_size = 0
        , papeis = []
        , admins = []
        , cod_institute = ""
        , institute = ""
        , privacidade = ""    # Pública ou Privada
        , blog_aberto = "N"   # Indica se o blog deste usuário 
                              # pode ser acessado de fora da plataforma
        , participacao = ""   # Mediante Convite, Voluntária ou Obrigatória
        , data_cri = ""
        , data_alt = ""
    )

class Activ(Server):
    "Active database"
    
    def __init__(self, url):
        print "conectando com o banco..."
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


__ACTIV = Activ('http://127.0.0.1:5984/')
FILES = __ACTIV.files
WIKI = __ACTIV.wiki
REGISTRY = __ACTIV.registry


def main():

    print "processando wiki..."
    for doc_id in WIKI:
        if "_design/" in doc_id:
            continue
        
        wiki_data = _EMPTYWIKI()
        wiki_data.update(WIKI[doc_id])
        WIKI[doc_id] = wiki_data
        
    print "processando files..."
    for file_id in FILES:
        if "_design/" in file_id:
            continue
        
        file_data = _EMPTYFILES()
        file_data.update(FILES[file_id])
        FILES[file_id] = file_data

    print "processando registry..."
    for registry_id in REGISTRY:
        if "_design/" in file_id:
            continue
        
        if "passwd" in REGISTRY[registry_id]:
            registry_data = _EMPTYMEMBER()

        else:
            registry_data = _EMPTYCOMMUNITY()
        
        registry_data.update(REGISTRY[registry_id])

        # remove papeis tnm e educo do registry
        if "tnm" in registry_data["papeis"]:
            registry_data["papeis"].remove("tnm")
            print "papel tnm removido de", registry_id 
        
        if "educo" in registry_data["papeis"]:
            registry_data["papeis"].remove("educo")
            print "papel educo removido de", registry_id 

        REGISTRY[registry_id] = registry_data

    print "fim do processamento ..."

if __name__ == "__main__":
    main()