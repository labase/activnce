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
import time

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
        # <user>: {
        #   votos_dados: [<user1>, <user2>, ...],
        #   votos_recebidos: <num de pontos>
        # }
)

def short_datetime(date_str, include_year=True, include_separator=u" às "):
    try:
        date = time.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")
        #return time.strftime("%d/%m/%Y %H:%M:%S", date)
        if include_year:
            return time.strftime((u"%d/%m/%Y" + include_separator + u"%H:%M").encode('utf-8'), date).decode('utf-8')
        else:
            return time.strftime((u"%d/%m" + include_separator + u"%H:%M").encode('utf-8'), date).decode('utf-8')
    except ValueError:
        return u'Data inválida!'
    
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


def main():
    print "Processando avaliações "
    print "Convertendo data_inicio e data_encerramento para o formato DD/MM/AAAA HH:SS"
    for item in EVALUATION:
        aval_data = _EMPTYEVALUATION()
        aval_data.update(EVALUATION[item])
        alterou = False
        if len(aval_data["data_inicio"]) == 26:
            aval_data["data_inicio"] = short_datetime(aval_data["data_inicio"], include_separator=" ")
            alterou = True
        if len(aval_data["data_encerramento"]) == 26:
            aval_data["data_encerramento"] = short_datetime(aval_data["data_encerramento"], include_separator=" ")
            alterou = True
        if alterou:
            print u"avaliação: %s (%s, %s)" % (item, aval_data["data_inicio"], aval_data["data_encerramento"])
            EVALUATION[item] = aval_data
        else:
            print u"avaliação: %s (ok)" % item
    
if __name__ == "__main__":
    main()