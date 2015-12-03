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

_DOCBASES = ['blog']

_EMPTYBLOG = lambda:dict()


# Nome das comunidades de e  para onde o blog sera migrado/copiado

COMU_SOURCE = "DevTnM"
#COMU_SOURCE = "Dev_AtivUFRJ"    #Comunidade no banco em producao

COMU_DESTINY = "Bem_Vindo"

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

BLOG = __ACTIV.blog

def main():

 
    print u"Processando os posts"
    print
    for id in BLOG:
        if "_design" not in id and COMU_SOURCE in id:
            
            print "id = ", id
            (registry_id, post ) = id.split("/")
            
            blog_data = _EMPTYBLOG()
            blog_data.update(BLOG[id])
            
            novo_id =  "%s/%s" % (COMU_DESTINY, post)
            
            print "Novo id", novo_id 
            
            #Criando novo registro de post no blog
            #BLOG[novo_id] = blog_data
            
            #Se for remover o antigo
            #del BLOG[id]
    
    print
    print u"fim"

if __name__ == "__main__":
    main()
