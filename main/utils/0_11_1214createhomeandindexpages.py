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

from datetime import datetime

_DOCBASES = ['registry', \
             'wiki']

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
REGISTRY = __ACTIV.registry
WIKI = __ACTIV.wiki

_CONTEUDO_DEFAULT = { 
    "home": u"<br/><br/><br/>Esta é a página de apresentação de %s no ActivUFRJ." +\
            u"<br/><br/><br/><br/><br/>",
    "indice":  u"Este texto é apresentado em todas as suas páginas. " +\
               u"Altere-o incluindo links que permitam facilitar a navegação.<br/>" +\
               u"Exemplo:<br/>" +\
               u"<a href='/wiki/%s/home'>Página Inicial</a><br/>"
}

_NOMEPAG_DEFAULT = { 
    "home": u"Página inicial",
    "indice":  u"Índice"
}
def cria_pagina (nome_pag, registry_id, user):
    doc_id = registry_id+"/"+nome_pag
    wiki_data = _EMPTYWIKI()
    if doc_id in WIKI:
        wiki_data.update (WIKI[doc_id])
        
    wiki_data["user"] = registry_id
    wiki_data["owner"] = user
    wiki_data["edicao_publica"] = "N" if user==registry_id else "S"
    wiki_data["registry_id"] = registry_id
    wiki_data["nomepag_id"] = nome_pag
    wiki_data["nomepag"] = _NOMEPAG_DEFAULT[nome_pag]
    wiki_data["conteudo"] = _CONTEUDO_DEFAULT[nome_pag] % registry_id
    wiki_data["tags"] = []
    wiki_data["data_cri"] = str(datetime.now())
    wiki_data["data_alt"] = wiki_data["data_cri"]
    wiki_data["alterado_por"] = wiki_data["owner"]
    WIKI[doc_id] = wiki_data


def main():

    print "processando registry..."
    for registry_id in REGISTRY:
        if "_design/" in registry_id:
            continue
        
        owner = registry_id if "passwd" in REGISTRY[registry_id] else REGISTRY[registry_id]["owner"]

        if registry_id+"/home" not in WIKI:
            cria_pagina("home", registry_id, owner)
            print "pag. criada: ", registry_id+"/home"

        if registry_id+"/indice" not in WIKI:
            cria_pagina("indice", registry_id, owner)
            print "pag. criada: ", registry_id+"/indice"
          
          
    print "fim do processamento ..."

if __name__ == "__main__":
    main()