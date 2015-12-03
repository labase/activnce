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

    
class Activ(Server):
    "Active database"
    
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
    print u">>> iniciando a conversão..."
    print 
    
    registry_id_to_convert = "Priv_Global_Admin"
    tags_to_remove = ["erros", "erro400", "erro500", "erro503"]
     
    for blog_id in BLOG:
        if "_design" not in blog_id:
            
            if blog_id.split("/")[0] == registry_id_to_convert:
                blog_data = dict()
                blog_data.update(BLOG[blog_id])
                
                for tag in tags_to_remove:
                    if tag in blog_data["tags"]:
                        blog_data["tags"].remove(tag)
                print u"blog_id= %s (%s)" % (blog_id, blog_data["tags"])
                        
                #BLOG[blog_id] = blog_data
            
    print u">>> fim do processamento..."
    print u"Atencao: eh necessario rodar o dbclean agora."

if __name__ == "__main__":
    main()