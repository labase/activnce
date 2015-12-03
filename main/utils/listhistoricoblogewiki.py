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

_DOCBASES = ['wiki', 'blog']

_EMPTYWIKI = lambda:dict()
_EMPTYBLOG = lambda:dict()


class Activ(Server):
    "Active database"
    wiki = {}

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


__ACTIV = Activ('http://127.0.0.1:5984/')
WIKI = __ACTIV.wiki
BLOG = __ACTIV.blog

def main():

    print u"páginas com mais de uma versão no histórico"
    for id in WIKI:
        if "_design" not in id:
            wiki_data = _EMPTYWIKI()
            wiki_data.update(WIKI[id])   
            #registry_id = id.split("/")[0]
            if wiki_data["is_folder"] != "S":
                history_size = len(wiki_data["historico"])
                if history_size > 1:
                    print "%s - %d" % (id, history_size)
    
    print
    print u"posts com mais de uma versão no histórico"
    for id in BLOG:
        if "_design" not in id:
            blog_data = _EMPTYBLOG()
            blog_data.update(BLOG[id])   
            history_size = len(blog_data["historico"])
            if history_size > 1:
                print "%s - %d" % (id, history_size)
    
    print
    print u"fim"

if __name__ == "__main__":
    main()
