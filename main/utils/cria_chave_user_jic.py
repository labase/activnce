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
'''
import urllib

import errno
import os.path
import locale
import time
from datetime import datetime
'''
# Utilitário para criar a chave dos integrantes da JIC 2011
from couchdb import Server
import sys
import time
import string
from random import choice

# Bancos que serão alterados
# registry - > chave do usuário tnm_admin
# magkeys -> entrada das chaves máqicas

_DOCBASES = ['magkeys', 'registry']


""" Lista de futuros usuários. JIC """

_EMPTYGENERIC = lambda: dict()

_EMPTYREGISTRY = lambda: dict()

_MAGKEYTYPES = dict(
      super_usuario = dict(
                       papeis = [ "super_usuario", "docente", "docente_externo", "funcionario", "aluno", "aluno_externo", "estagiario", "comunidade", "usuario_externo"],
                       codigo="su"
                       ),
      docente = dict(
                       papeis = ["comunidade"],
                       codigo="do"
                       ),
      docente_externo = dict(
                       papeis = [],
                       codigo="de"
                       ),
      funcionario = dict(
                       papeis = ["comunidade"],
                       codigo="fu"
                       ),
      estagiario = dict(
                        papeis = [],
                        codigo="es"
                        ),
      aluno = dict(
                 papeis = [],
                 codigo="al"
                 ),
      aluno_externo = dict(
                        papeis = [],
                        codigo="ae"
                        ),
      usuario_externo = dict(
                        papeis = [],
                        codigo="ue"
                        ),
      comunidade = dict(
                        papeis = [],
                        codigo="co"
                        )
)
def msgUse ():
    print "Uso: python cria_chave_user_jic.py arquivo_csv papel [separador]"
    print "Papel = aluno "
    print "Separador padrao = ;"
    print "Primeira linha do arquivo csv = chaves que irão para o banco"
    print "Considerar utilizar um arquivo separado com associacao de cabeçalho."

def genDictKey(linha_csv, separador):
    lista_chaves = (((linha_csv.replace("\n","")).strip()).strip("")).split(separador)
    if lista_chaves[0] == "":
        lista_chaves = []
    return lista_chaves

def mkeyCode (tipo):
    cod = ""
    if tipo in _MAGKEYTYPES:
        cod = _MAGKEYTYPES[tipo]["codigo"]
    return cod

def GenMagicKey(tipo, instituicao, length=24, chars=string.letters + string.digits):
    return mkeyCode(tipo) + instituicao + ''.join([choice(chars) for i in range(length)])

def invited_email(email):
    """ Busca uma chave pelo email """
    map_fun = "function(doc) { if (doc.email == '%s') emit(doc.email, doc.magic); }" % email
    resultado = MAGKEYS.query(map_fun)
        
    if resultado:
        return True
    else:
        return False

class Activ(Server):
    "Active database"
    
    def __init__(self, url):
        print "iniciando o servidor..."
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
REGISTRY = __ACTIV.registry
def main(argv):
    msg = ""   
    try:
        if len(argv) >= 2:
            arquivo_csv = argv[0]
            papel = argv[1]

            #separador = '\t'  , ",", ";"          
            separador = ';'            
            if len(argv) >= 3:
                if argv[2]:
                   separador = argv[2]

            magic_keys = {}
            chaves = []
            arquivo = open ( arquivo_csv, "r" )
            unidade = ""
            processados = 0
            total = 0
            registry_data = _EMPTYREGISTRY()
            registry_data = REGISTRY["tnm_admin"]
            # Primeira linha para ver as chaves
            chaves = genDictKey(arquivo.readline(),separador)
            for registro in arquivo:
                table_data = _EMPTYGENERIC()
                id_registro = ""
                registro = genDictKey(registro, separador)
                if registro:
                   for i in range(0,len(registro)):
                       #Extraindo a chave
                       chave = chaves[i]
                       chave = chave.strip()
                       #Processando o campo                   
                       campo = registro[i].replace('"', "")
                       campo = campo.strip()
                       campo = campo.decode("utf-8")
                       # Processamento dos campos específicos
                       # Considerar colocar estas associações em um arquivo
                       if papel == "aluno":
                          if chave == "curso_codigo_SIGA":
                             unidade = campo[0:4]
                          if chave == "Email_Bolsista":
                             chave="email" 
                          if chave == "Bolsista":
                             chave = "nome"
                          if chave == "CPF_Bolsista":
                             chave = "CPF"
                       if papel == "docente":
                          if chave == "Orientador":
                             chave = "nome"
                          if chave == "Email_Orientador":
                             chave = "email" 
                          if chave == "codigo_unidade":
                             unidade = campo[0:4]
                       # Guardando os dados processados
                       table_data[chave] = campo
                       # acrescenta quem envia o convite
                   table_data["user"] = "tnm_admin"
                   # acrescenta a chave individual 
                   table_data["magic"] = GenMagicKey(papel, unidade)
                   # acrescenta um campo comunidades para ser levado para o registry do cadastro do usuario
                   #Esta seria as comunidades_default
                   table_data["comunidades"] = ['jicac2011']
                   id_registro = table_data["magic"]
                   if id_registro:
                      if invited_email(table_data["email"]):
                          print "Email já existente = ", table_data["email"]
                      else:
                          MAGKEYS[id_registro] = table_data
                          print id_registro, " : ", table_data["nome"], " : ", processados
                          registry_data["mykeys"].append(id_registro)
                          processados = processados + 1
                   else:
                      print "Chave mágica não foi criada. ", table_data["email"], ":", total
                else:
                   print "linha em branco encontrada. ", total
                   total = total + 1
                REGISTRY["tnm_admin"] = registry_data   
        else:
            msgUse()
            exit()
    except ValueError:
        print "Parâmetro inválido."
        msgUse()
        exit()
    
if __name__ == "__main__":
    main(sys.argv[1:])

