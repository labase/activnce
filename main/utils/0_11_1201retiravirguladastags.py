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

_DOCBASES = ['registry', \
             'blog', \
             'wiki']

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
BLOG = __ACTIV.blog
WIKI = __ACTIV.wiki


def main():

    print "processando registry..."
    for registry_id in REGISTRY:
        if "_design/" in registry_id:
            continue
        
        registry_data = REGISTRY[registry_id]
        for i in range(len(registry_data["tags"])):
            registry_data["tags"][i] = registry_data["tags"][i].replace(",","")
            # remove se a tag ficar vazia
            if not registry_data["tags"][i]:
                del registry_data["tags"][i]
        REGISTRY[registry_id] = registry_data

    print "processando wiki ..."
    for doc_id in WIKI:
        if "_design/" in doc_id:
            continue
        
        wiki_data = WIKI[doc_id]
        print "tags antes=", wiki_data["tags"]
        
        if doc_id.split("/")[1] == "home" and "inicial" in wiki_data["tags"]:
            wiki_data["tags"].remove("inicial")
            print "tag 'inicial' removida:", doc_id

        for i in range(len(wiki_data["tags"])):
            wiki_data["tags"][i] = wiki_data["tags"][i].replace(",","")
            # remove se a tag ficar vazia
            if not wiki_data["tags"][i]:
                del wiki_data["tags"][i]

        print "tags depois=", wiki_data["tags"]
        WIKI[doc_id] = wiki_data

    print "processando blog ..."
    # recria tags dos posts do blog
    for post_id in BLOG:
        if "_design/" in post_id:
            continue
        
        blog_data = BLOG[post_id]
        print "tags antes=", blog_data["tags"]
        for i in range(len(blog_data["tags"])):
            blog_data["tags"][i] = blog_data["tags"][i].replace(",","")
            # remove se a tag ficar vazia
            if not blog_data["tags"][i]:
                del blog_data["tags"][i]
        print "tags depois=", blog_data["tags"]
        BLOG[post_id] = blog_data

    print "fim do processamento ..."
    print u"É necessário executar o dbclean para regerar a tabela de tags."

if __name__ == "__main__":
    main()