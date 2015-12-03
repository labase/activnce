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

_DOCBASES = ['evaluation']

_EMPTYEVALUATION = lambda:dict(
# _id = "registry_id/nome_avaliacao"
          nome = ""
        , tipo = ""             # "participantes" ou "páginas"
        , descricao = ""
        , avaliados = []        # lista de itens a serem avaliados
        , owner = ""            # quem criou a avaliação.
        , data_inicio = ""
        , data_encerramento = ""
        , pontuacao = []
        , data_cri = ""
        , data_alt = ""
        , avaliacoes = {}
        # <user>: {
        #   votos_dados: [<user1>, <user2>, ...],
        #   votos_recebidos: <num de pontos>
        # }
)


class Activ(Server):
    "Active database"
    evaluation = {}

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
EVALUATION = __ACTIV.evaluation

def main():

    print u"iniciando conversão"
    for id in EVALUATION:
        if "_design" not in id:
            print id
            aval_data = _EMPTYEVALUATION()
            aval_data.update(EVALUATION[id])
            print "aval_data=", aval_data
            
            avaliacoes = {}
            for key in aval_data.keys():
                if not aval_data["avaliacoes"] and key not in _EMPTYEVALUATION().keys() and key not in ['_rev', '_id']:
                    avaliacoes[key] = aval_data[key]
                    del aval_data[key]
                
            if not aval_data["avaliacoes"]:
                aval_data["avaliacoes"] = avaliacoes
            
            print "aval_data=", aval_data

            
            EVALUATION[id] = aval_data
    print u"conversão finalizada."
if __name__ == "__main__":
    main()
