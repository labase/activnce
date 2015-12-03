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

import sys

from utils.notify import notify

def print_usage():
    print "Uso: python utilrun.py <nome_util> <pars_adicionais>"
    print "<nome_util>: notify | ..."
    print "<pars_adicionais>: par1 | par2 | ..."


def main(argv):
    if len(argv) >= 1:
        util = argv[0]
        
        if util == "notify":
            print "processando utilitário..."
            notify()
            print "fim do processamento..."
        #elif util == "***"
        else:
            print_usage()
    else:
        print_usage()
    
if __name__ == "__main__":
    main(sys.argv[1:])