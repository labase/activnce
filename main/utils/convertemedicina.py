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


_DOCBASES = ['a_registry',\
             'a_wiki',\
             'a_files',\
             'a_blog', \
             'a_comment',\
             'a_mblog',\
             'a_evaluation',\
             'a_noticias',\
             'a_agenda',\
             'a_forum',\
             'a_scrapbook',\
             'm_registry',\
             'm_wiki',\
             'm_files',\
             'm_blog', \
             'm_comment',\
             'm_mblog',\
             'm_evaluation',\
             'm_noticias',\
             'm_agenda',\
             'm_forum',\
             'm_scrapbook']

_EMPTYMEMBER = lambda: dict(
          user = ""
        , passwd = ""
        , name = ""
        , lastname = ""
        , email = ""
        , tags = [] 
        , description = ""
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


_EMPTYBLOG = lambda:dict(
# _id = "registry_id/nome_post"
          registry_id = ""    # dono do blog: usuário ou comunidade.
        , owner = ""          # quem postou.
                              # caso blog seja de uma comunidade, owner!=registry_id
        , titulo = "Novo Post"
        , post_id = ""        # identificador do post.
                              # é obtido a partir do título, extraíndo caracteres especiais,
                              # letras acentuadas e subtituindo espaços por _.
        , conteudo = "Entre aqui com o conteúdo do seu post. <br/>"
        , tags = []
        , data_cri = ""
        , data_alt = ""         # data da última alteração
        , alterado_por = ""     # quem alterou o post pela última vez
     )


_EMPTYCOMMENT = lambda:dict(
# _id = "couchdb_id"
          registry_id = ""    # dono do blog  
        , owner = ""          # quem fez o comentário
        , post_id = ""        # post comentado
        , comment = "Entre aqui com o conteúdo do seu post. <br/>"
        , data_cri = ""
     )



_EMPTYMBLOG = lambda:dict(
# _id = "couchdb_id"
          registry_id = ""  # dono do mblog: usuário ou comunidade
        , owner = ""        # quem postou. caso mblog seja de uma comunidade, owner!=registry_id
        , conteudo = ""
        , conteudo_original = "" # conteúdo do post original, caso este post seja um compartilhamento
        , tags = []
        , reply_to = ""     # mblog_id do post respondido por este
        , interessados = [] # lista dos registry_ids dos interessados neste post.
                            # esta informação é necessária para facilitar a exclusão do mblog.
        , mencionados = []  # lista dos registry_ids mencionados nesse post.
        , data_cri = ""
                # caso este post seja o compartilhamento de outro:
                # registry_id, owner e data_cri guardam informações de quem compartilhou
                # registry_id_original, owner_original e data_original guardam informações do post original
        , registry_id_original = "" 
        , owner_original = ""
        , data_original = ""
        , mblog_id_original = ""
                # caso este post tenha sido compartilhado por outros: 
                # share_list é a lista de compartilhamentos (mblog_ids) que ele possui.
        , share_list = []
)


_EMPTYEVALUATION = lambda:dict(
# _id = "registry_id/nome_avaliacao"
          nome = ""
        , tipo = ""             # "participantes" ou "páginas"
        , descricao = ""
        , avaliados = []        # lista de itens a serem avaliados
        , owner = ""            # quem criou a avaliação.
        , data_inicio = ""
        , data_encerramento = ""
        , pontuacao = []
        , data_cri = ""
        , data_alt = ""
        # <user>: {
        #   votos_dados: [<user1>, <user2>, ...],
        #   votos_recebidos: <num de pontos>
        # }
)


_EMPTYNOTICIA = lambda:dict(
# _id = "registry_id/id"        # nome da comunidade/id da noticia
          id            = 0     # indice da noticia
        , titulo        = ""    # titulo
        , resumo        = ""    # resumo
        , texto         = ""    # corpo da noticia
        , url           = ""    # no lugar do corpo da noticia usar uma url
        , fonte         = ""    # fonte
        , dt_publicacao = ""    # data da publicação
        , dt_validade   = ""    # data limite de exibição da noticia
     )


_EMPTYAGENDA = lambda:dict(
# _id = "registry_id"
        events = {}
        #AAAAMM: {
        #    DD: [{ msg = "", owner = "", url = "", data_cri = "" }, ...]
        #}
)

_EMPTYSCRAPBOOK = lambda:dict(
          user_to = "",
          recados = []
     )

_EMPTYFORUM = lambda:dict(
# _id = "registry_id"            # dono do forum, mesmo nome da comunidade.
          topics = []            # lista de tópicos
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
REGISTRY = __ACTIV.a_registry
BLOG = __ACTIV.a_blog
MBLOG = __ACTIV.a_mblog
COMMENT = __ACTIV.a_comment
WIKI = __ACTIV.a_wiki
FILES = __ACTIV.a_files
EVALUATION = __ACTIV.a_evaluation
NOTICIAS = __ACTIV.a_noticias
AGENDA = __ACTIV.a_agenda
FORUM = __ACTIV.a_forum
SCRAP = __ACTIV.a_scrapbook

M_REGISTRY = __ACTIV.m_registry
M_BLOG = __ACTIV.m_blog
M_MBLOG = __ACTIV.m_mblog
M_COMMENT = __ACTIV.m_comment
M_WIKI = __ACTIV.m_wiki
M_FILES = __ACTIV.m_files
M_EVALUATION = __ACTIV.m_evaluation
M_NOTICIAS = __ACTIV.m_noticias
M_AGENDA = __ACTIV.m_agenda
M_FORUM = __ACTIV.m_forum
M_SCRAP = __ACTIV.m_scrapbook


def copy_table(table_name, mtable, table, empty_table):
    ''' copia mtable para table se não houver conflito de chave '''
    print "processando %s ..." % table_name
    for m_id in mtable:
        if "_design/" in m_id:
            continue
        
        achou = False
        for id in table:
            if "_design/" in id:
                continue
            if id == m_id:
                achou = True
                break
                
        table_data = empty_table
        table_data.update(mtable[m_id])
        if achou:
            # copia mtable para table com outro nome
            m_id = m_id.replace("/","/_")
            
        attachment = False
        del table_data["_id"]
        del table_data["_rev"]
        if "_attachments" in table_data:
            attachment = True
            filename = m_id.split("/")[1]
            tipo = table_data['_attachments'][filename]['content_type']
            del table_data["_attachments"]
                
        table[m_id] = table_data
        print u"copiando..."
        
        if attachment:
            print "filename=", filename
            print "tipo=", tipo
            # Lê attachment com a foto original
            arq = mtable.get_attachment(m_id, filename)

            #try:
            table.put_attachment(table[m_id],
                       arq, filename, tipo)
            #except Exception as detail:
            #    print "*** Erro ao salvar attachments no banco ", m_id
            #    continue
                
                

def extend_table(table_name, mtable, table, empty_table, atributo=""):
    ''' mescla dados da mtable para table se não houver conflito de chave '''
    print "processando %s ..." % table_name
    for m_id in mtable:
        if "_design/" in m_id:
            continue
        
        achou = False
        for id in table:
            if "_design/" in id:
                continue
            
            if id == m_id:
                achou = True
                break
            
        if achou:
            print "Conflito no %s: %s" % (table_name, id)
            if atributo:
                table_data = empty_table
                table_data.update(table[id])
                table_data[atributo].extend(mtable[m_id][atributo])
                table[id] = table_data
                print "copiando %s %s" % (m_id, atributo)
            
        else:
            # copia mtable para table
            #
            table_data = empty_table
            table_data.update(mtable[m_id])
            del table_data["_id"]
            del table_data["_rev"]
            table[m_id] = table_data
            print "copiando %s" % m_id
            
def main():

    print "processando registry..."
    for mregistry_id in M_REGISTRY:
        if "_design/" in mregistry_id:
            continue
        
        achou = False
        for registry_id in REGISTRY:
            if "_design/" in registry_id:
                continue
            if registry_id == mregistry_id:
                achou = True
                break
                
        print "copiando %s" % mregistry_id
        if achou:
            tipo = "user" if "passwd" in REGISTRY[registry_id] else "community"
            mtipo = "user" if "passwd" in M_REGISTRY[mregistry_id] else "community"
            print "Conflito no registry: %s (%s) X %s (%s)" % \
                          (registry_id, tipo, mregistry_id, mtipo)
            
            if tipo==mtipo and tipo=="user":
                user_data = _EMPTYMEMBER()
                user_data.update(REGISTRY[registry_id])
                
                user_data["amigos"].extend(M_REGISTRY[mregistry_id]["amigos"])
                user_data["amigos_convidados"].extend(M_REGISTRY[mregistry_id]["amigos_convidados"])
                user_data["amigos_pendentes"].extend(M_REGISTRY[mregistry_id]["amigos_pendentes"])

                user_data["comunidades"].extend(M_REGISTRY[mregistry_id]["comunidades"])
                user_data["comunidades_pendentes"].extend(M_REGISTRY[mregistry_id]["comunidades_pendentes"])
                REGISTRY[registry_id] = user_data
                
            elif tipo==mtipo and tipo=="community":
                community_data = _EMPTYCOMMUNITY()
                community_data.update(REGISTRY[registry_id])
                
                community_data["participantes"].extend(M_REGISTRY[mregistry_id]["participantes"])
                community_data["participantes_pendentes"].extend(M_REGISTRY[mregistry_id]["participantes_pendentes"])
                REGISTRY[registry_id] = community_data
                
        else:
            attachment = False
            if "passwd" in M_REGISTRY[mregistry_id]:
                registry_data = _EMPTYMEMBER()
            else:
                registry_data = _EMPTYCOMMUNITY()
                
            registry_data.update(M_REGISTRY[mregistry_id])
            registry_data["cod_institute"] = "3501"
            registry_data["institute"] = u"Faculdade de Medicina"
            del registry_data["_id"]
            del registry_data["_rev"]
            if "_attachments" in registry_data:
                attachment = True
                del registry_data["_attachments"]
            REGISTRY[mregistry_id] = registry_data
              
            if attachment:
                # Lê attachment com a foto original
                foto = M_REGISTRY.get_attachment(mregistry_id, registry_data["photo"])
    
                try:
                    REGISTRY.put_attachment(REGISTRY[mregistry_id],
                           foto, registry_data["photo"], "image/png")
                except Exception as detail:
                    print "*** Erro ao salvar attachments no banco ", mregistry_id
                    continue


    # só copiar os registros da medicina para o activ
    copy_table("wiki", M_WIKI, WIKI, _EMPTYWIKI())
    copy_table("files", M_FILES, FILES, _EMPTYFILES())
    copy_table("blog", M_BLOG, BLOG, _EMPTYBLOG())
    copy_table("comment", M_COMMENT, COMMENT, _EMPTYCOMMENT())
    copy_table("mblog", M_MBLOG, MBLOG, _EMPTYMBLOG())
    
    # para cada registry_id, acrescentar os registros da medicina no activ
    extend_table("evaluation", M_EVALUATION, EVALUATION, _EMPTYEVALUATION())
    extend_table("noticias", M_NOTICIAS, NOTICIAS, _EMPTYNOTICIA())
    extend_table("agenda", M_AGENDA, AGENDA, _EMPTYAGENDA())
    extend_table("forum", M_FORUM, FORUM, _EMPTYFORUM())

    extend_table("recados", M_SCRAP, SCRAP, _EMPTYSCRAPBOOK(), "recados")

    print "fim do processamento ..."

if __name__ == "__main__":
    main()