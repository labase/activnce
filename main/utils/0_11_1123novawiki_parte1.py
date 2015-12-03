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


_DOCBASES = ['wiki', \
             'blog', 'comment']
 
#Verificar conteúdo de wiki, blog, comments.             

_EMPTYWIKI = lambda:dict(
# _id = "registry_id/nome_pagina"
          user = ""           # usuário ou comunidade (registry_id).
        , registry_id = ""    #  usuário ou comunidade (registry_id).
        , owner = ""          # quem criou.
                              # caso wiki seja de uma comunidade, owner!=registry_id
        , nomepag = ""
        , nomepag_id = ""
        , conteudo = ""
        , edicao_publica = ""  # Se "S" qq participante pode editar, se "N" só o dono da página e os admins da comunidade.
        , tags = []
        , data_cri = ""         # data de criação da página
        , data_alt = ""         # data da última alteração
        , alterado_por = ""     # quem alterou a pag pela última vez
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



class Activ(Server):
    "Active database"
    
    def __init__(self, url):
        print "iniciando a conversão..."
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
WIKI = __ACTIV.wiki
BLOG = __ACTIV.blog
COMMENT = __ACTIV.comment


def main():
    def remove_diacritics(str):
        special_chars = [u'à', u'á', u'ã', u'â', u'À', u'Á', u'Ã', u'Â',\
                         u'é', u'ê', u'É', u'Ê',\
                         u'í', u'Í', \
                         u'ó', u'õ', u'ô', u'Ó',u'Õ', u'Ô', \
                         u'ú', u'ü', u'Ú', u'Ü', \
                         u'ç', u'Ç' ]
        chars = ['a', 'a', 'a', 'a', 'A', 'A', 'A', 'A',\
                 'e', 'e', 'E', 'E',\
                 'i',  'I', \
                 'o', 'o', 'o', 'O', 'O', 'O', \
                 'u', 'u', 'U', 'U', \
                 'c', 'C' ]

        for i in range(len(special_chars)):
            str=str.replace(special_chars[i], chars[i])
               
        return str
   
    def remove_special_chars(str):
        strnew = ""
        for i in range(len(str)):
            if (str[i]>="A" and str[i]<="Z") or\
               (str[i]>="a" and str[i]<="z") or\
               (str[i]>="0" and str[i]<="9") or\
               (str[i]=="_"):
                strnew += str[i]
                
        return strnew
    
#    Pega cada página wiki (wiki_id) e cria um novo wiki_id (wiki_id_novo) sem acentos os caracteres especiais
#    Para cada wiki_id, varre o conteúdo de blogs, mblogs, comments, news, para ver se há aguma referência
#
    for pagina in WIKI:
        if "_design" not in pagina:
            (registry_id, wiki_id) = pagina.split("/")

            novawiki_id = remove_special_chars(remove_diacritics(wiki_id.replace(" ","_")))
            novapagina = '/'.join([registry_id, novawiki_id])
            str2find = "wiki/%s" % pagina
            str2subs = "wiki/%s" % novapagina
            print "STR2FIND=",str2find.encode("utf-8")
            
            if str2find != str2subs:
                #
                # Procura no blog a existência de str2find
                #
                print "procurando no BLOG..."
                for blog_id in BLOG:
                    if "_design" not in blog_id:
                        blog_data = _EMPTYBLOG()
                        blog_data.update(BLOG[blog_id])
                        if str2find in blog_data["conteudo"]:
                            print "*** Achei = ", blog_id, blog_data["conteudo"].encode("utf-8")
                            blog_data["conteudo"] = blog_data["conteudo"].replace(str2find,str2subs)
                            print "Conteudo novo: ", blog_data["conteudo"].encode("utf-8")
                            BLOG[blog_id] = blog_data
                        #else:
                        #    print "não achei = ", blog_id
                    
                # Procura nos comentários do blog a existência de str2find
                #
                print "procurando no COMMENT..."
                for comment_id in COMMENT:
                    if "_design" not in comment_id:
                        comment_data = _EMPTYCOMMENT()
                        comment_data.update(COMMENT[comment_id])
                        if str2find in comment_data["comment"]:
                            print "*** Achei = ", comment_id, comment_data["comment"].encode("utf-8")
                            comment_data["comment"] = comment_data["comment"].replace(str2find,str2subs)
                            print "Conteudo novo: ", comment_data["comment"].encode("utf-8")
                            COMMENT[comment_id] = comment_data
                            
                        #else:
                        #    print "não achei = ", comment_id

                # Procura no blog a existência de str2find
                #
                print "procurando no WIKI..."
                for wiki_id in WIKI:
                    if "_design" not in wiki_id and pagina != wiki_id:
                        wiki_data = _EMPTYWIKI()
                        wiki_data.update(WIKI[wiki_id])
                        if str2find in wiki_data["conteudo"]:
                            print "*** Achei = ", wiki_id, wiki_data["conteudo"].encode("utf-8")
                            wiki_data["conteudo"] = wiki_data["conteudo"].replace(str2find,str2subs)
                            print "Conteudo novo: ", wiki_data["conteudo"].encode("utf-8")
                            WIKI[wiki_id] = wiki_data
                        #else:
                        #    print "não achei = ", wiki_id


if __name__ == "__main__":
    main()