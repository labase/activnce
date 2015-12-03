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
import urllib
import functools

import sys, errno
import os.path
import locale
import time
from datetime import datetime


def main(argv):
    msg = ""   
    try:
        if len(argv) >= 2:
            arquivo_csv = argv[0]
            include_tabela = argv[1]
            
            if len(argv) >= 3:
                if argv[2]:
                   if argv[2] == "TAB":
                      separador = "\t"
                   else:
                      separador = argv[2]
                else:
                   separador = ';'
                if len(argv) >= 4 and argv[3]:
                    papel = argv[3]

            exec("import " + include_tabela)
            exec("from " + include_tabela + " import  _EMPTYGENERIC")
            exec("from " + include_tabela + " import  GENERIC_DB")

            table_data = _EMPTYGENERIC()
            #table_data["papel"] = papel APENAS SE FOR PARA PESSOAS
            chaves = []
            arquivo = open ( arquivo_csv, "r" )
            
            # Primeira linha - chave __ID
            ID = []
            ID = (arquivo.readline().replace("\n", "")).split(separador)
            for i in ID:
                i = i.rstrip()
                i = i.lstrip()
                i = i.replace('"', "")
            print "ID: ",ID
            # Segunda linha para ver as chaves
            chaves = (arquivo.readline().replace("\n", "")).split(separador)
            print chaves
            
            for registro in arquivo:
                registro = (registro.replace("\n", "")).split(separador)
                print registro
                id_registro = ""
                for i in range(0,len(registro)):
                    chave = chaves[i].replace('"', "")
                    chave = chave.rstrip()
                    chave = chave.lstrip()
                    
                    campo = registro[i].replace('"', "")
                    campo = campo.rstrip()
                    campo = campo.lstrip()
                    campo = campo.decode("utf-8")
                    print "campo = ", campo
                    table_data[chave] = campo

                    for i in ID:
                        if chave == i:
                            id_registro += campo
                print "id_registro = ", id_registro
                print "salvando tabela: ", table_data
                GENERIC_DB[id_registro] = table_data
        else:
            print "Uso: python createdb_from_csv.py arquivo.csv tabela_banco [separador]"
            print "Separador padrao = ;  , papel padrao = em branco "
            print "Primeira linha do arquivo = chave de __ID "
            print "Segunda linha do arquivo csv = chaves do banco "
            exit()
    except ValueError:
        print "Parâmetro inválido."
        print "Uso: python createdb_from_csv.py arquivo_csv banco.py"
        exit()
    
if __name__ == "__main__":
    main(sys.argv[1:])
