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
        , owner = ""           # quem criou a avaliação.
        , data_inicio = ""
        , data_encerramento = ""
        , pontuacao = []
        , data_cri = ""
        # <user>: {
        #   votos_dados: [<user1>, <user2>, ...],
        #   votos_recebidos: <num de pontos>
        # }
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
EVALUATION = __ACTIV.evaluation

NOVA_DATA_ENCERRAMENTO = "2010-05-14 23:59:00.000000"
DONO_DAS_AVALIACOES = "fabianaz"

def main():
    print "Processando avaliações criadas por ", DONO_DAS_AVALIACOES
    print "Nova data de encerramento=", NOVA_DATA_ENCERRAMENTO
    for item in EVALUATION:
        if item[0:2] == "GT" and EVALUATION[item]["owner"] == DONO_DAS_AVALIACOES:
            eval_data = _EMPTYEVALUATION()
            eval_data.update(EVALUATION[item])
            print "avaliação: %s (%s)" % (item, eval_data["data_encerramento"])
            eval_data["data_encerramento"] = NOVA_DATA_ENCERRAMENTO
            EVALUATION[item] = eval_data            
    
if __name__ == "__main__":
    main()