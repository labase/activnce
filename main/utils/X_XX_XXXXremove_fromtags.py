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


# Substitui _ por espaço nas tags (menos as do mblog)


#Funciona em conjunto com o dbclean para regerar as tags


from couchdb import Server

from datetime import datetime
from uuid import uuid4
import re

_DOCBASES = ['registry', \
             'blog', \
             'comment',\
             'wiki',\
             'files',\
             'bookmarks',\
             'glossary'
             ]
def remove_html_tags(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)


class Activ(Server):
    "Active database"
    
    def __init__(self, url):
        print "conectando com o banco..."
        Server.__init__(self, url)
        
        #self.erase_tables(_DOCBASES_TO_REMOVE) 
        
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

BLOG = __ACTIV.blog

COMMENT = __ACTIV.comment
WIKI = __ACTIV.wiki
FILES = __ACTIV.files

BOOKMARKS = __ACTIV.bookmarks
GLOSSARY = __ACTIV.glossary


def main():

    print "processando registry..."
    for registry_id in REGISTRY:
        if "_design/" in registry_id:
            continue
        
        if "passwd" in REGISTRY[registry_id]:
            
            #member
            print "  user: %s" % registry_id
            user_data = REGISTRY[registry_id]

            # passa tags para minusculas
            temp_tags = []            
            for tag in user_data["tags"]:
                if "_" in tag:
                    nova_tag = tag.replace("_", " ")
                    temp_tags.append(nova_tag)
                else:
                    temp_tags.append(tag)
                user_data["tags"] = temp_tags
                
            REGISTRY[registry_id] = user_data
            # fim do altera tag para users          
        else:
            # comunidades
            community_data = REGISTRY[registry_id]

            # tags em minusculas
            temp_tags = []
            for tag in community_data["tags"]:
               if "_" in tag:
                    nova_tag = tag.replace("_", " ")
                    temp_tags.append(nova_tag)
               else:
                    temp_tags.append(tag)
            community_data["tags"] = temp_tags
            
            REGISTRY[registry_id] = community_data
            
    print "processando tags da wiki ..."
    # recria tags das páginas wiki
    for doc_id in WIKI:
        if "_design/" in doc_id:
            continue
            
        wiki_data = WIKI[doc_id]
        if wiki_data["is_folder"]!="S":
            # trata tags das páginas

            temp_tags = []
            for tag in wiki_data["tags"]:
               if "_" in tag:
                    nova_tag = tag.replace("_", " ")
                    temp_tags.append(nova_tag)
               else:
                    temp_tags.append(tag)
            wiki_data["tags"] = temp_tags
            WIKI[doc_id] = wiki_data

    print "processando tags de arquivos ..."
    # recria tags dos arquivos
    for file_id in FILES:
        if "_design/" in file_id:
            continue            
        file_data = FILES[file_id]
        nome = file_data["description"] if file_data["description"] else file_data["_id"].split("/")[1]
        temp_tags = []
        for tag in file_data["tags"]:
               if "_" in tag:
                    nova_tag = tag.replace("_", " ")
                    temp_tags.append(nova_tag)
               else:
                    temp_tags.append(tag)
        file_data["tags"] = temp_tags

        FILES[file_id] = file_data

    print "processando blog ..."
    # recria tags dos posts do blog
    for post_id in BLOG:
        if "_design/" in post_id:
            continue                
        blog_data = BLOG[post_id]

        temp_tags = []
        for tag in blog_data["tags"]:
               if "_" in tag:
                    nova_tag = tag.replace("_", " ")
                    temp_tags.append(nova_tag)
               else:
                    temp_tags.append(tag)
        blog_data["tags"] = temp_tags
        BLOG[post_id] = blog_data
        
    
    print "processando favoritos ..."
    # recria tags dos favoritos
    for mark in BOOKMARKS:
        if "_design/" in mark:
            continue
        bookmark_data = BOOKMARKS[mark]
        temp_tags = []
        for tag in bookmark_data["tags"]:
               if "_" in tag:
                    nova_tag = tag.replace("_", " ")
                    temp_tags.append(nova_tag)
               else:
                    temp_tags.append(tag)
        bookmark_data["tags"] = temp_tags
        BOOKMARKS[mark] = bookmark_data
    
    print "processando glossarios ..."
    # recria tags dos glossários
    for item in GLOSSARY:
        if "_design/" in item:
            continue
        glossary_data = GLOSSARY[item]
        temp_tags = []
        for tag in glossary_data["tags"]:
               if "_" in tag:
                    nova_tag = tag.replace("_", " ")
                    temp_tags.append(nova_tag)
               else:
                    temp_tags.append(tag)
        glossary_data["tags"] = temp_tags
        GLOSSARY[item] = glossary_data
    
    print "fim do processamento ..."
    print "Favor executar o dbclean."

if __name__ == "__main__":
    main()