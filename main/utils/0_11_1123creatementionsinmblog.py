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
from string import find, replace


_DOCBASES = ['mblog', 'registry']

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

def processa_arroba (conteudo):
    # Retorna duas listas com todas as menções feitas numa mensagem.
    # lista_original: inclui usuários e comunidades mencionadas;
    #                 não inclui @ seguido de usuario/comunidade inexistentes
    # lista_processada: Caso seja feita menção a uma comunidade, a lista inclui
    #                   todos os participantes da comunidade mencionada.
    
    found_list = [i.lstrip('@') for i in list(set(re.findall(r"@\w+", conteudo)))]
    ref_list = []
    proc_list = []
    
    for registry_id in found_list:
        if registry_id in REGISTRY:
            ref_list.append(registry_id)
            user_data = REGISTRY[registry_id]
            if "passwd" not in user_data:
                # referência a uma comunidade
                conteudo = replace(conteudo, "@%s"%registry_id, \
                                   '@<a title="%s" href="/mblog/%s">%s</a>'%(user_data["description"], registry_id, registry_id))
                proc_list.extend(user_data["participantes"])
            else:
                # referência a um usuário
                conteudo = replace(conteudo, "@%s"%registry_id, \
                                   '@<a title="%s" href="/mblog/%s">%s</a>'%(user_data["name"]+" "+user_data["lastname"], registry_id, registry_id))
                proc_list.append(registry_id)

    return dict( conteudo=conteudo,
                lista_original=ref_list,
                lista_processada=proc_list
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

def remove_html_tags(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

__ACTIV = Activ('http://127.0.0.1:5984/')
MBLOG = __ACTIV.mblog
REGISTRY = __ACTIV.registry

def main():

    for item in MBLOG:
        if "_design" not in item:
            mblog_data = _EMPTYMBLOG()
            mblog_data.update(MBLOG[item])
            print "item: %s %s - %s" % (mblog_data["registry_id"], mblog_data["owner"], mblog_data["conteudo"])
    
            str = remove_html_tags(mblog_data["conteudo"])
            ret = processa_arroba(str)
            print "ret=", ret
            mblog_data["mencionados"] = ret["lista_original"]
            MBLOG[item] = mblog_data


if __name__ == "__main__":
    main()