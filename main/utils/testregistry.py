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
import re

_DOCBASES = ['registry']


class Activ(Server):
    "Active database"
    
    def __init__(self, url):
        print "iniciando a verificação..."
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

VALID_LOGIN = "(^[a-zA-Z0-9][\w\.]+\w$)"

def has_diacritics(str):
    for i in range(len(str)):
        if ord(str[i]) >= 128:
            return True
    return False

def main():
    p = re.compile(VALID_LOGIN)
    for item in REGISTRY:
        if "_design" not in item:
            if "passwd" in REGISTRY[item]:
                if not p.match(item):
                    print "invalid user: %s" % item
                if has_diacritics(item):
                    print "user has diacritics: %s" % item
            else:
                if not p.match(item):
                    print "invalid community: %s" % item
                if has_diacritics(item):
                    print "community has diacritics: %s" % item
    print "Final da verificação..."

if __name__ == "__main__":
    main()