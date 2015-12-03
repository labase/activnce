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
from datetime import datetime
from uuid import uuid4
import re

_DOCBASES = ['magkeys']


VALIDADE_DA_CHAVE = 60   # numero de dias


def elapsed_time(data):
    # Verifica quanto tempo foi decorrido da data até agora
    # Retorna um objeto do tipo datetime.timedelta
    #
    hoje = datetime.now()

    inicio = time.strptime(data,"%Y-%m-%d %H:%M:%S.%f")
    inicio = datetime(inicio.tm_year, inicio.tm_mon, inicio.tm_mday,
              inicio.tm_hour, inicio.tm_min, inicio.tm_sec)
    return hoje - inicio


class Activ(Server):
    "Active database"
    
    def __init__(self, url):
        print "conectando com o banco..."
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
MAGKEYS = __ACTIV.magkeys



def main():

    print "Deseja remover magic keys com mais de %s dias?" % VALIDADE_DA_CHAVE
    resp = raw_input("Digite S para remover e N para cancelar: ")
    if resp=='S':
        for key in MAGKEYS:
            if 'data_convite' in MAGKEYS[key]:
                delta = str(elapsed_time(MAGKEYS[key]['data_convite']))
                
                if delta.find(',') > 0:
                    days, hours = delta.split(',')
                    days = int(days.split()[0].strip())
                else:
                    days = 0
                
                if days > VALIDADE_DA_CHAVE:
                    del MAGKEYS[key]
            else:
                del MAGKEYS[key]
    
        print "Fim do processamento. Favor rodar o dbclean para acertar a lista de chaves de cada usuário no registry ..."
        
    else:
        print "A execução foi cancelada. Nenhuma chave foi removida."

if __name__ == "__main__":
    main()