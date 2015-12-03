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

# Lista de databases a serem compactados
#
_DOCBASES = ['registry']
_DOCBASES.extend(['magkeys', 'invites', 'requestinviteform', 'requestinvite'])
_DOCBASES.extend(['news', 'log', 'notification', 'notification_error'])
_DOCBASES.extend(['agenda'])
_DOCBASES.extend(['wiki'])
_DOCBASES.extend(['files'])
_DOCBASES.extend(['mblog'])
_DOCBASES.extend(['blog', 'comment'])
_DOCBASES.extend(['forum', 'forum_param'])
_DOCBASES.extend(['noticias'])
_DOCBASES.extend(['desenho'])
_DOCBASES.extend(['scrapbook'])
_DOCBASES.extend(['tags'])



class Activ(Server):
    "Active database"
    
    def __init__(self, url):
        print "iniciando a compactação..."
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


def main():
    for attribute in _DOCBASES:
        print "Compactando:", attribute
        getattr(__ACTIV, attribute).compact()
    
    
if __name__ == "__main__":
    main()