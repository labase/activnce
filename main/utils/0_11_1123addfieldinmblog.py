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


_DOCBASES = ['mblog']

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
MBLOG = __ACTIV.mblog

def main():

    for item in MBLOG:
        if "_design" not in item:
            mblog_data = _EMPTYMBLOG()
            mblog_data.update(MBLOG[item])
            print "item: %s %s - %s" % (mblog_data["registry_id"], mblog_data["owner"], mblog_data["conteudo"])
    
            MBLOG[item] = mblog_data


if __name__ == "__main__":
    main()