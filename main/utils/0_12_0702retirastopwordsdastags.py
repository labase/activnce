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
             'wiki',
             'file']

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
FILE = __ACTIV.file

# Palavras ignoradas na lista de tags
STOPWORDS = ['de', 'a', 'o', 'que', 'e', 'do', 'da', 'em', 'um', 'para', 'com', u'não', 'uma', 'os', 'no', 'se', 'na', 'por', 'mais', 'as',
             'dos', 'como', 'mas', 'ao', 'ele', 'das', u'à', 'seu', 'sua', 'ou', 'quando', 'muito', 'nos', u'já', 'eu', 
             u'também', u'só', 'pelo', 'pela', u'até', 'isso', 'ela', 'entre', 'depois', 'sem', 'mesmo', 'aos', 'seus', 'quem', 
             'nas', 'me', 'esse', 'eles', u'você', 'essa', 'num', 'nem', 'suas', 'meu', u'às', 'minha', 'numa', 'pelos', 
             'elas', 'qual', u'nós', 'lhe', 'deles', 'essas', 'esses', 'pelas', 'este', 'dele', 'tu', 'te', u'vocês', 'vos', 
             'lhes', 'meus', 'minhas', 'teu', 'tua', 'teus', 'tuas', 'nosso', 'nossa', 'nossos', 'nossas', 'dela', 'delas', 'esta', 'estes',
             'estas', 'aquele', 'aquela', 'aqueles', 'aquelas', 'isto', 'aquilo',
             'estou', u'está', 'estamos', u'estão', 'estive', 'esteve', 'estivemos', 'estiveram', 'estava', u'estávamos', 
             'estavam', 'estivera', u'estivéramos', 'esteja', 'estejamos', 'estejam', 'estivesse', u'estivéssemos', 'estivessem', 
             'estiver', 'estivermos', 'estiverem', 'hei', u'há', 'havemos', u'hão', 'houve', 'houvemos', 'houveram', 'houvera', 
             u'houvéramos', 'haja', 'hajamos', 'hajam', 'houvesse', u'houvéssemos', 'houvessem', 'houver', 'houvermos', 'houverem', 
             'houverei', u'houverá', 'houveremos', u'houverão', 'houveria', u'houveríamos', 'houveriam', 'sou', u'é', 'somos', 
             u'são', 'era', u'éramos', 'eram', 'fui', 'foi', 'fomos', 'foram', 'fora', u'fôramos', 'seja', 'sejamos', 'sejam', 
             'fosse', u'fôssemos', 'fossem', 'for', 'formos', 'forem', 'serei', u'será', 'seremos', u'serão', 'seria', 
             u'seríamos', 'seriam', 'tenho', 'tem', 'temos', u'têm', 'tinha', u'tínhamos', 'tinham', 'tive', 'teve', 'tivemos', 
             'tiveram', 'tivera', u'tivéramos', 'tenha', 'tenhamos', 'tenham', 'tivesse', u'tivéssemos', 'tivessem', 'tiver', 'tivermos', 
             'tiverem', 'terei', u'terá', 'teremos', u'terão', 'teria', u'teríamos', 'teriam']

def convert_tags (oldTags):
    oldTags = [ x.lower() for x in oldTags ]
    oldTags = list(set(oldTags))

    newTags=[]
    for word in oldTags:
        if word not in STOPWORDS:
            newTags.append(word)
    return newTags

def main():

    print "processando registry..."
    for registry_id in REGISTRY:
        if "_design/" in registry_id:
            continue
        
        registry_data = REGISTRY[registry_id]
        if registry_data["tags"]: print "tags antes=", registry_data["tags"]
        registry_data["tags"] = convert_tags(registry_data["tags"])
        if registry_data["tags"]: print "tags depois=", registry_data["tags"]
        REGISTRY[registry_id] = registry_data

    print "processando wiki ..."
    for doc_id in WIKI:
        if "_design/" in doc_id:
            continue
        
        wiki_data = WIKI[doc_id]
        if wiki_data["tags"]: print "tags antes=", wiki_data["tags"]
        wiki_data["tags"] = convert_tags(wiki_data["tags"])
        if wiki_data["tags"]: print "tags depois=", wiki_data["tags"]
        WIKI[doc_id] = wiki_data

    print "processando files ..."
    for doc_id in FILE:
        if "_design/" in doc_id:
            continue
        
        file_data = FILE[doc_id]
        if file_data["tags"]: print "tags antes=", file_data["tags"]
        file_data["tags"] = convert_tags(file_data["tags"])
        if file_data["tags"]: print "tags depois=", file_data["tags"]
        FILE[doc_id] = file_data

    print "processando blog ..."
    # recria tags dos posts do blog
    for post_id in BLOG:
        if "_design/" in post_id:
            continue
        
        blog_data = BLOG[post_id]
        if blog_data["tags"]: print "tags antes=", blog_data["tags"]
        blog_data["tags"] = convert_tags(blog_data["tags"])

        if blog_data["tags"]: print "tags depois=", blog_data["tags"]
        BLOG[post_id] = blog_data

    print "fim do processamento ..."
    print u"É necessário executar o dbclean para regerar a tabela de tags."

if __name__ == "__main__":
    main()