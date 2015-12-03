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
from uuid import uuid4
import re
import sys

_DOCBASES = ['registry', 'magkeys', \
             'activdb', \
             'blog', \
             'comment',\
             'mblog',\
             'wiki',\
             'files',\
             'bookmarks',\
             'glossary',\
             'studio',\
             'tags']

# Tabelas a serem removidas para depois serem recriadas
#
_DOCBASES_TO_REMOVE = ['tags']


# dicionários com as estruturas de acesso ao couchdb
"""
_EMPTYMEMBER = lambda: dict(
          user = ""
        , passwd = ""
        , name = ""
        , lastname = ""
        , email = ""
        , conta_google = ""
        , tags = [] 
        , description = ""
        , amigos = []
        , amigos_pendentes = []
        , amigos_convidados = []
        , comunidades = []
        , comunidades_pendentes = []
        , mykeys = []
        , origin = ""                        # Pode ser: "convidado" ou "intranet"
        , privacidade = u"Pública"           # Pode ser: Pública ou Privada
        #, blog_aberto = "N"                 # Indica se o blog deste usuário 
                                             # pode ser acessado de fora da plataforma
        , services = []
        , groups = {}                        # se usuário, guarda os grupos de amigos.
                                             # se comunidade, guarda os grupos de participantes.
                                             # { "nome_grupo1": ["usuario1", "usuario2", ...],
                                             #   "nome_grupo2": ["usuario1", "usuario2", ...]
                                             # }
        , community_groups = {}              # grupos de comunidades que o usuário participa
                                             # não é utilizado nas permissões.
        , upload_quota = 10 * 1024 * 1024    # max 10 Mb
        , upload_size = 0  
        , notify = "2"  # notificações de e-mail
                        # 0 = não receber
                        # 1 = receber apenas um boletim semanal
                        # 2 = receber sempre
        , cpf = ""      # incluido para futura integração a intranet da UFRJ
        , data_cri = ""
        , data_alt = ""
        
        , suspended_passwd = ""     # copia de passwd, cpf e email se usuário for suspenso.
        , suspended_cpf = ""
        , suspended_email = ""
        , suspended_date = ""
        , reactivated_date = ""
        , reactivated_by = ""
    )

_EMPTYCOMMUNITY = lambda: dict(
          name = ""
        , description = ""
        , conta_google = ""
        , tags = []
        , owner = ""
        , participantes_pendentes = []
        , participantes = []
        , comunidades = []                   # comunidades em que esta comunidade está incluída
        , upload_quota = 60 * 1024 * 1024    # max 60 Mb
        , upload_size = 0
        , admins = []
        , apps = {}
        , services = []
        , groups = {}                        # se comunidade, guarda os grupos de participantes.
                                             # { "nome_grupo1": ["usuario1", "usuario2", ...],
                                             #   "nome_grupo2": ["usuario1", "usuario2", ...]
                                             # }
        , privacidade = ""    # Pública ou Privada
        #, blog_aberto = "N"   # Indica se o blog deste usuário 
                              # pode ser acessado de fora da plataforma
        , participacao = ""   # Mediante Convite, Voluntária ou Obrigatória
        , data_cri = ""
        , data_alt = ""
    )
"""
# Nova estrutura do Registry para members e communities

_EMPTYMEMBER = lambda: dict(
          user = ""
        , passwd = ""
        , name = ""
        , lastname = ""
        , email = ""
        , conta_google = ""
        , tags = [] 
        , description = ""
        , amigos = []
        , amigos_pendentes = []
        , amigos_convidados = []
        , comunidades = []
        , comunidades_pendentes = []
        , mykeys = []
        , origin = ""                        # Pode ser: "convidado" ou "intranet"
        , privacidade = u"Pública"           # Pode ser: Pública ou Privada
        #, blog_aberto = "N"                 # Indica se o blog deste usuário 
                                             # pode ser acessado de fora da plataforma
        , services = []
        , groups = {}                        # se usuário, guarda os grupos de amigos.
                                             # se comunidade, guarda os grupos de participantes.
                                             # { "nome_grupo1": ["usuario1", "usuario2", ...],
                                             #   "nome_grupo2": ["usuario1", "usuario2", ...]
                                             # }
        , community_groups = {}              # grupos de comunidades que o usuário participa
                                             # não é utilizado nas permissões.
        , upload_quota = 10 * 1024 * 1024    # max 10 Mb
        , upload_size = 0  
        , notify = "2"  # notificações de e-mail
                        # 0 = não receber
                        # 1 = receber apenas um boletim semanal
                        # 2 = receber sempre
        , cpf = ""      # incluido para futura integração a intranet da UFRJ
        , data_cri = ""
        , data_alt = ""
        
        , suspended_passwd = ""     # copia de passwd, cpf e email se usuário for suspenso.
        , suspended_cpf = ""
        , suspended_email = ""
        , suspended_date = ""
        , reactivated_date = ""
        , reactivated_by = ""
        , type = "member"
        , subtype = ""
    )

_EMPTYCOMMUNITY = lambda: dict(
          name = ""
        , description = ""
        , conta_google = ""
        , tags = []
        , owner = ""
        , participantes_pendentes = []
        , participantes_chamados = []
        , participantes = []
        , comunidades = []                   # comunidades em que esta comunidade está incluída
        , upload_quota = 60 * 1024 * 1024    # max 60 Mb
        , upload_size = 0
        , admins = []
        , apps = {}
        , services = []
        , groups = {}                        # se comunidade, guarda os grupos de participantes.
                                             # { "nome_grupo1": ["usuario1", "usuario2", ...],
                                             #   "nome_grupo2": ["usuario1", "usuario2", ...]
                                             # }
        , privacidade = ""    # Pública ou Privada
        , participacao = ""   # Mediante Convite, Voluntária ou Obrigatória
        , data_cri = ""
        , data_alt = ""
        , type = "community"
        , subtype = ""
    )


_EMPTYTAG = lambda:dict(
    # _id = <couchdb_id>
    tag = "",
    registry_id = "",
    owner = "",
    tipo = "",        # community/wiki/blog/user/mblog/file
    objeto = "",
    data_cri = ""
)


# Marca de conteúdo removido na wiki e no blog
_CONTEUDO_REMOVIDO = "##@@$$%% REMOVED %%$$@@##"

# Marca de usuário suspenso
PASSWD_USER_SUSPENDED = "***USER SUSPENDED***"

def remove_html_tags(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)


class Activ(Server):
    "Active database"
    
    def __init__(self, url):
        print "conectando com o banco..."
        Server.__init__(self, url)
        
        self.erase_tables(_DOCBASES_TO_REMOVE) 
        
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

    def erase_tables(self, tables):
        'erase a list of tables'
        for table in tables:
            try:
                del self[table]
            except:
                pass

__ACTIV = Activ('http://127.0.0.1:5984/')
REGISTRY = __ACTIV.registry
ACTIVDB = __ACTIV.activdb
MAGKEYS = __ACTIV.magkeys
BLOG = __ACTIV.blog
MBLOG = __ACTIV.mblog
COMMENT = __ACTIV.comment
WIKI = __ACTIV.wiki
FILES = __ACTIV.files
TAGS = __ACTIV.tags
BOOKMARKS = __ACTIV.bookmarks
GLOSSARY = __ACTIV.glossary
STUDIO = __ACTIV.studio

def addTag(tag, registry_id, owner, tipo, objeto, texto, data_alt=""):
    tag_data = _EMPTYTAG()
    tag_data["tag"] = tag
    tag_data["registry_id"] = registry_id
    tag_data["owner"] = owner
    tag_data["tipo"] = tipo
    tag_data["objeto"] = objeto
    tag_data["texto"] = texto
    tag_data["data_cri"] = str(datetime.now()) if data_alt=="" else data_alt
    
    tag_id = uuid4().hex
    tag_data["_id"] = tag_id
    
    TAGS[tag_id] = tag_data

def procRegistry():
    suspended_users = []
    for registry_id in REGISTRY:
        if registry_id.startswith("_design/"):
            continue
        
        if "passwd" in REGISTRY[registry_id]:
            
            #member
            print "  user: %s" % registry_id
            user_data = _EMPTYMEMBER()
            user_data.update(REGISTRY[registry_id])

            # se o usuário está suspenso, ignora-o
            if user_data["passwd"] == PASSWD_USER_SUSPENDED:
                suspended_users.append(registry_id)
                continue
                      
            # recria searchtags do perfil do usuário
            username = user_data["name"]+' '+user_data["lastname"]
            for tag in user_data["tags"]:
                addTag(tag, registry_id, registry_id, "user", \
                       registry_id, username, data_alt=user_data["data_alt"])

            # limpa lista das mkeys do usuário
            user_data["mykeys"] = []
          
            # elimina duplicação nas listas de amigos e comunidades
            user_data["amigos"] = list(set(user_data["amigos"]))
            user_data["amigos_pendentes"] = list(set(user_data["amigos_pendentes"]))
            user_data["amigos_convidados"] = list(set(user_data["amigos_convidados"]))
            user_data["comunidades"] = list(set(user_data["comunidades"]))
            user_data["comunidades_pendentes"] = list(set(user_data["comunidades_pendentes"]))

            # corrige lista de amigos do usuário
            #print "   amigos."
            for amigo in user_data["amigos"]:
                if amigo == registry_id:
                    # remove o proprio usuário da lista de amigos                    
                    print "      %s removido da lista amigos" % registry_id
                    user_data["amigos"].remove(amigo)
                elif amigo not in REGISTRY or "passwd" not in REGISTRY[amigo]:
                    # remove usuário inexistente da lista de amigos
                    print u"    amigo removido: %s" % amigo
                    user_data["amigos"].remove(amigo)
                elif "passwd" in REGISTRY[amigo] and registry_id not in REGISTRY[amigo]["amigos"]:
                    # se A é amigo de B, então B é amigo de A
                    print u"    registrado na lista do amigo: %s" % amigo
                    amigo_data =  _EMPTYMEMBER()
                    amigo_data.update(REGISTRY[amigo])
                    amigo_data["amigos"].append(registry_id)
                    REGISTRY[amigo] = amigo_data
                #else:
                #    print u"    %s ok." % amigo
          
            # um amigo não pode ser amigo_pendente nem amigo_convidado
            for amigo in user_data["amigos"]:
                if amigo in user_data["amigos_pendentes"]:
                    print u"    amigo pendente removido: %s já é amigo." % amigo
                    user_data["amigos_pendentes"].remove(amigo)
                if amigo in user_data["amigos_convidados"]:
                    print u"    amigo convidado removido: %s já é amigo." % amigo
                    user_data["amigos_convidados"].remove(amigo)
                
            # corrige lista de amigos_pendentes
            #print "   amigos pendentes."
            for pendente in user_data["amigos_pendentes"]:
                if pendente == registry_id:
                    # remove o proprio usuário da lista de amigos pendentes                    
                    print "      %s removido da lista amigos_pendentes" % registry_id
                    user_data["amigos_pendentes"].remove(pendente)       
                elif pendente not in REGISTRY or "passwd" not in REGISTRY[pendente]:
                    # remove usuário inexistente da lista de amigos pendentes
                    print "    amigo pendente removido: %s" % pendente
                    user_data["amigos_pendentes"].remove(pendente)
                elif "passwd" in REGISTRY[pendente] and registry_id not in REGISTRY[pendente]["amigos_convidados"]:
                    # se A é amigo pendente de B, então B é amigo convidado de A
                    print "    registrado na lista do amigo: %s" % amigo
                    amigo_data =  _EMPTYMEMBER()
                    amigo_data.update(REGISTRY[pendente])
                    amigo_data["amigos_convidados"].append(registry_id)
                    REGISTRY[pendente] = amigo_data
                #else:
                #    print u"    %s ok." % pendente

          
            # corrige lista de amigos_convidados
            #print "   amigos convidados."
            for convidado in user_data["amigos_convidados"]:
                if convidado == registry_id:
                    # remove o proprio usuário da lista de amigos convidados
                    print "      %s removido da lista amigos_convidados" % registry_id
                    user_data["amigos_convidados"].remove(convidado)
                elif convidado not in REGISTRY or "passwd" not in REGISTRY[convidado]:
                    # remove usuário inexistente da lista de amigos convidados
                    print "    amigo convidado removido: %s" % convidado
                    user_data["amigos_convidados"].remove(convidado)
                elif "passwd" in REGISTRY[convidado] and registry_id not in REGISTRY[convidado]["amigos_pendentes"]:
                    # se A é amigo convidado de B, então B é amigo convidado de A
                    print "    registrado na lista do amigo: %s" % amigo
                    amigo_data =  _EMPTYMEMBER()
                    amigo_data.update(REGISTRY[convidado])
                    amigo_data["amigos_pendentes"].append(registry_id)
                    REGISTRY[convidado] = amigo_data
                #else:
                #    print u"    %s ok." % convidado


            # corrige lista de comunidades
            #print "   comunidades."
            for comunidade in user_data["comunidades"]:
                if comunidade not in REGISTRY or "passwd" in REGISTRY[comunidade]:
                    # remove comunidade inexistente da lista de comunidades
                    print "    comunidade removida: %s" % comunidade
                    user_data["comunidades"].remove(comunidade)
                elif "passwd" not in REGISTRY[comunidade] and registry_id not in REGISTRY[comunidade]["participantes"]:
                    # se a comunidade B está na lista de comunidades do usuário A,
                    # então A tem que estar na lista de participantes de B
                    print "    registrado na lista de participantes de %s" % comunidade
                    community_data =  _EMPTYCOMMUNITY()
                    community_data.update(REGISTRY[comunidade])
                    community_data["participantes"].append(registry_id)
                    REGISTRY[comunidade] = community_data
                #else:
                #    print u"    %s ok." % comunidade

            # corrige lista de grupos removendo comunidades das quais eu não faço mais parte.
            for grupo in user_data["community_groups"]:
                communities_in_group = []
                communities_in_group.extend(user_data["community_groups"][grupo])
                
                for comu in communities_in_group:
                    if comu not in user_data["comunidades"]:
                        print "removendo %s de %s" % (comu, grupo)
                        user_data["community_groups"][grupo].remove(comu)
                        
                        
                        
            # um comunidade não pode ser comunidade_pendente
            for comunidade in user_data["comunidades"]:
                if comunidade in user_data["comunidades_pendentes"]:
                    print "    comunidade pendente removida: %s já é comunidade." % comunidade
                    user_data["comunidades_pendentes"].remove(comunidade)


            # corrige lista de comunidades pendentes
            #print "   comunidades pendentes."
            for comunidade in user_data["comunidades_pendentes"]:
                if comunidade not in REGISTRY or "passwd" in REGISTRY[comunidade]:
                    # remove comunidade inexistente da lista de comunidades pendentes
                    print "    comunidade removida: %s" % comunidade
                    user_data["comunidades_pendentes"].remove(comunidade)
                elif "passwd" not in REGISTRY[comunidade] and registry_id not in REGISTRY[comunidade]["participantes_pendentes"]:
                    # se a comunidade B está na lista de comunidades pendentes do usuário A,
                    # então A tem que estar na lista de participantes pendentes de B
                    print "    registrado na lista de participantes pendentes de %s" % comunidade
                    community_data =  _EMPTYCOMMUNITY()
                    community_data.update(REGISTRY[comunidade])
                    community_data["participantes_pendentes"].append(registry_id)
                    REGISTRY[comunidade] = community_data
                #else:
                #    print u"    %s ok." % comunidade

                
            REGISTRY[registry_id] = user_data
          
        else:
            # comunidades

            print "  community: %s" % REGISTRY[registry_id]["name"]
            community_data = _EMPTYCOMMUNITY()
            community_data.update(REGISTRY[registry_id])

            # recria searchtags do perfil da comunidade
            for tag in community_data["tags"]:
                addTag(tag, registry_id, community_data["owner"], "community", \
                       registry_id, community_data["description"], community_data["data_alt"])

            # elimina duplicação nas listas de participantes
            community_data["participantes"] = list(set(community_data["participantes"]))
            community_data["participantes_pendentes"] = list(set(community_data["participantes_pendentes"]))

            # corrige lista de participantes da comunidade
            #print "   participantes."
            for participante in community_data["participantes"]:
                if participante not in REGISTRY or "passwd" not in REGISTRY[participante]:
                    # remove usuário inexistente da lista de participantes
                    print u"    participante removido: %s" % participante
                    community_data["participantes"].remove(participante)
                elif "passwd" in REGISTRY[participante] and registry_id not in REGISTRY[participante]["comunidades"]:
                    # se o usuário A é participante da comunidade B,
                    # então B tem que estar na lista de comunidades de A
                    print u"    registrada na lista de comunidades de %s" % participante
                    part_data =  _EMPTYMEMBER()
                    part_data.update(REGISTRY[participante])
                    part_data["comunidades"].append(registry_id)
                    REGISTRY[participante] = part_data
                #else:
                #    print u"    %s ok." % participante

            # um participante não pode ser participante_pendente
            for participante in community_data["participantes"]:
                if participante in community_data["participantes_pendentes"]:
                    print u"    participante pendente removido: %s ja eh participante." % participante
                    community_data["participantes_pendentes"].remove(participante)
                
            # corrige lista de participantes_pendentes
            #print "   participantes pendentes."
            for participante in community_data["participantes_pendentes"]:
                if participante not in REGISTRY or "passwd" not in REGISTRY[participante]:
                    # remove usuário inexistente da lista de participantes
                    print u"    participante removido: %s" % participante
                    community_data["participantes_pendentes"].remove(participante)
                elif "passwd" in REGISTRY[participante] and registry_id not in REGISTRY[participante]["comunidades_pendentes"]:
                    # se o usuário A é participante pendente da comunidade B,
                    # então B tem que estar na lista de comunidades pendentes de A
                    print u"    registrada na lista de comunidades pendentes de %s" % participante
                    part_data =  _EMPTYMEMBER()
                    part_data.update(REGISTRY[participante])
                    part_data["comunidades_pendentes"].append(registry_id)
                    REGISTRY[participante] = part_data
                #else:
                #    print u"    %s ok." % participante
           
            REGISTRY[registry_id] = community_data
    

    print "processando magic keys..."
    for key in MAGKEYS:
        user = MAGKEYS[key]['user']
        if user not in REGISTRY:
            print "  removendo. user inexistente: %s key: %s" % (user,key)

            # remove chave se usuário não existe mais no registry
            del MAGKEYS[key]
          
        else:
            # print "  ok. user: %s key: %s" % (user,key)

            # acrescenta chave na lista de chaves do usuário
            user_data = _EMPTYMEMBER()
            user_data.update(REGISTRY[user])
            user_data["mykeys"].append(key)
            REGISTRY[user] = user_data
    
    return suspended_users
    
    
    
    
def showProgress(count, totalSize):
  percent = int(count*100/totalSize)
  #sys.stdout.write("\r" + "...%d%%" % percent)
  #sys.stdout.flush()
  print "...%d%%" % percent + "\r",
"""    
wiki_size = len(WIKI)
i=0
for doc in WIKI:
    i=i+1
    showProgress(i,wiki_size) 
"""



def main(argv):
    opcao = ""
    if len(argv)>0:
        if argv[0] == "tags":
            opcao = "tags"
        else:
            print "uso: python dbclean.py -> para processar tudo ou "
            print "     python dbclean.py tags -> para somente regerar as tags."
            exit (1)
    
    if opcao!="tags":
        print "processando registry..."
        suspended_users = procRegistry()
    else:
        print "verificando usuarios suspensos..."
        suspended_users = []
        for registry_id in REGISTRY:
            if registry_id.startswith("_design/"):
                continue
            
            if "passwd" in REGISTRY[registry_id]:
                
                #member
                user_data = _EMPTYMEMBER()
                user_data.update(REGISTRY[registry_id])
    
                if user_data["passwd"] == PASSWD_USER_SUSPENDED:
                    suspended_users.append(registry_id)
    
    print "usuarios suspensos detectados..."
    print suspended_users
    
    print "processando tags da wiki ..."
    # recria tags das páginas wiki
    for doc_id in WIKI:
        if doc_id.startswith("_design/"):
            continue
          
        if doc_id.split("/")[0] in suspended_users:
            continue
          
        wiki_data = WIKI[doc_id]
        if wiki_data["is_folder"]!="S":
            # trata tags da página se a mesma não está na lixeira
            if wiki_data["historico"][-1]["conteudo"] != _CONTEUDO_REMOVIDO:            
                for tag in wiki_data["tags"]:
                    addTag(tag, wiki_data["registry_id"], wiki_data["owner"], "wiki", \
                           doc_id, wiki_data["nomepag"], data_alt=wiki_data["historico"][-1]["data_alt"])
        else:
            # esvazia lista de folder_items de todas as pastas para recriar depois
            wiki_data["folder_items"] = []
            WIKI[doc_id] = wiki_data

    print "processando folders da wiki ..."
    # recria lista de folder_items das pastas
    for doc_id in WIKI:
        if doc_id.startswith("_design/"):
            continue
            
        if doc_id.split("/")[0] in suspended_users:
            continue

        wiki_data = WIKI[doc_id]
        if wiki_data["is_folder"] == "S":
            print "  %s"%doc_id
        if wiki_data["parent_folder"] != "":
            # instancia o pai do doc_id
            parent_id = wiki_data["registry_id"]+"/"+wiki_data["parent_folder"]
            if parent_id in WIKI:
                parent_data = WIKI[parent_id]
                if parent_data["is_folder"] == "S":
                    # se o pai é um folder, acrescenta o doc_id na lista de filhos do pai
                    parent_data["folder_items"].append(wiki_data["nomepag_id"])
                    WIKI[parent_id] = parent_data
                else:
                    # se o pai não é um folder: erro, coloca o doc_id no folder raiz
                    wiki_data["parent_folder"] = ""
                    WIKI[doc_id] = wiki_data
            else:
                # se o pai não existe: erro, coloca o doc_id no folder raiz
                wiki_data["parent_folder"] = ""
                WIKI[doc_id] = wiki_data

    print "processando tags de arquivos ..."
    # recria tags dos arquivos
    for file_id in FILES:
        if file_id.startswith("_design/"):
            continue            

        if file_id.split("/")[0] in suspended_users:
            continue

        file_data = FILES[file_id]
        nome = file_data["description"] if file_data["description"] else file_data["_id"].split("/")[1]
        for tag in file_data["tags"]:
            addTag(tag, file_data["registry_id"], file_data["owner"], "file", \
                        file_id, nome, data_alt=file_data["data_alt"])

        # esvazia lista de folder_items de todas as pastas para recriar depois
        if file_data["is_folder"]=="S":
            file_data["folder_items"] = []
            FILES[file_id] = file_data

    print "processando folders de arquivos ..."
    # recria lista de folder_items das pastas
    for file_id in FILES:
        if file_id.startswith("_design/"):
            continue

        if file_id.split("/")[0] in suspended_users:
            continue
            
        files_data = FILES[file_id]
        if files_data["is_folder"] == "S":
            print "  %s"%file_id
        if files_data["parent_folder"] != "":
            # instancia o pai do file_id
            parent_id = files_data["registry_id"]+"/"+files_data["parent_folder"]
            if parent_id in FILES:
                parent_data = FILES[parent_id]
                if parent_data["is_folder"] == "S":
                    # se o pai é um folder, acrescenta o file_id na lista de filhos do pai
                    parent_data["folder_items"].append(file_id.split("/")[1])
                    FILES[parent_id] = parent_data
                else:
                    # se o pai não é um folder: erro, coloca o doc_id no folder raiz
                    files_data["parent_folder"] = ""
                    FILES[file_id] = files_data
            else:
                # se o pai não existe: erro, coloca o doc_id no folder raiz
                files_data["parent_folder"] = ""
                FILES[file_id] = files_data
                
    print "processando tags do blog ..."
    # recria tags dos posts do blog
    for post_id in BLOG:
        if post_id.startswith("_design/"):
            continue                
        if post_id.split("/")[0] in suspended_users:
            continue

        blog_data = BLOG[post_id]
        
        # trata tags do post se o mesmo não está na lixeira
        if blog_data["historico"][-1]["conteudo"] != _CONTEUDO_REMOVIDO:            
            for tag in blog_data["tags"]:
                addTag(tag, blog_data["registry_id"], blog_data["owner"], "blog", \
                       post_id, blog_data["titulo"], data_alt=blog_data["data_alt"])

    print "processando mblog ..."
    # recria tags dos posts do mblog
    for post_id in MBLOG:
        if post_id.startswith("_design/"):
            continue                
        mblog_data = MBLOG[post_id]

        if mblog_data["owner"] in suspended_users:
            continue
        
        for tag in mblog_data["tags"]:
            addTag(tag, mblog_data["registry_id"], mblog_data["owner"], "mblog", \
                   post_id, remove_html_tags(mblog_data["conteudo"]), data_alt=mblog_data["data_cri"])

    print "processando favoritos ..."
    # recria tags dos favoritos
    for mark in BOOKMARKS:
        if mark.startswith("_design/"):
            continue
                
        bookmark_data = BOOKMARKS[mark]
        if bookmark_data["owner"] in suspended_users:
            continue
        
        for tag in bookmark_data["tags"]:
            addTag(tag, bookmark_data["registry_id"], bookmark_data["owner"], "bookmarks", \
                   mark, bookmark_data["url"], data_alt=bookmark_data["data_alt"])
    
    print "processando glossarios ..."
    # recria tags dos glossários
    for item in GLOSSARY:
        if item.startswith("_design/"):
            continue
        if item.split("/")[0] in suspended_users:
            continue
                
        glossary_data = GLOSSARY[item]
        for tag in glossary_data["tags"]:
            addTag(tag, glossary_data["registry_id"], glossary_data["owner"], "glossary", \
                   item, glossary_data["term"], data_alt=glossary_data["data_alt"])
    
    print "processando studio ..."
    # recria tags do estúdio de games
    for file_id in STUDIO:
        if file_id.startswith("_design/"):
            continue
        if file_id.split("/")[0] in suspended_users:
            continue
                
        studio_data = STUDIO[file_id]
        nome = studio_data["description"] if studio_data["description"] else studio_data["_id"].split("/")[1]
        for tag in studio_data["tags"]:
            addTag(tag, studio_data["registry_id"], studio_data["owner"], "studio", \
                        file_id, nome, data_alt=studio_data["data_alt"])
               
    print "processando activdb"
    # recria tags do activdb (videoaula, quiz, question, forum, etc ...)
    for activ_id in ACTIVDB:
        if activ_id.startswith("_design/"):
            continue
                
        activ_data = ACTIVDB[activ_id]

        if activ_data["registry_id"] in suspended_users:
            continue
        
        # as questions, apesar de possuir tags, não entram na tabela de tags.
        #
        # até o momento, os únicos serviços que tem tags no activdb são forum e videoaula
        if activ_data["service"] != "question":
            for tag in activ_data["tags"]:
                addTag(tag, activ_data["registry_id"], activ_data["owner"], activ_data["service"], \
                            activ_data["registry_id"]+"/"+activ_data["name_id"], activ_data["titulo"], data_alt=activ_data["data_alt"])
                        




    print "fim do processamento ..."
    
if __name__ == "__main__":
    main(sys.argv[1:])
