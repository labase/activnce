# -*- coding: utf-8 -*-

import csv
from couchdb import Server
import time
from datetime import datetime

_DOCBASES = ['escolas', 'magkeyinstitutes']

_MAGKEYINSTITUTES = {
      "0001": dict(
            nome = u"Instituto Oi Futuro"
          ),
      "0002": dict(
            nome = u"Núcleo de Computação Eletrônica"
          ),
      "0003": dict(
            nome = u"NAVE"
          ),
      "9999": dict(
            nome = u"-"
          )      
}

_EMPTYINSTITUTE = lambda: dict(
          nome = "",
          school_id = ""
)
_EMPTYSCHOOL = lambda: dict(
          nome_ultima_atualizacao = ""
	, data_ultima_atualizacao = ""
        , nome = ""
	, abreviado = ""
	, ativa = ""
	, situacao = ""
        , dependencia_administrativa = ""
	, secretaria = ""
        , codigo_inep = ""
	, cnpj = ""
        , endereco = ""
        , numero = ""
        , complemento = ""
        , bairro = ""
        , municipio = ""
        , distrito = ""
        , estado = ""
        , pais = ""
        , cep = ""
	, telefone1 = ""
	, telefone1_ramal = ""
	, telefone2 = ""
	, telefone2_ramal = ""
	, telefone_pub = ""
	, fax = ""
	, fax_ramal = ""
        , email = ""
        , site = ""
        , localizacao = ""
        , vertente = ""
        , regiao = ""
        , modalidade_ensino = []
	, turnos = []
        , qtd_gestor = ""
        , qtd_professor = ""
        , qtd_tec_adm = ""
        , qtd_aluno = ""
        , gestor1_funcao = ""
	, gestor1_nome = ""
	, gestor1_sexo = ""
	, gestor1_data_nascimento = ""
	, gestor1_email1 = ""
	, gestor1_email2 = ""
	, gestor1_telefone1 = ""
	, gestor1_telefone1_ramal = ""
	, gestor1_telefone2 = ""
	, gestor1_telefone2_ramal = ""
	, gestor2_funcao = ""
	, gestor2_outra_funcao = ""
	, gestor2_nome = ""
	, gestor2_sexo = ""
	, gestor2_data_nascimento = ""
	, gestor2_email1 = ""
	, gestor2_email2 = ""
	, gestor2_telefone1 = ""
	, gestor2_telefone1_ramal = ""
	, gestor2_telefone2 = ""
	, gestor2_telefone2_ramal = ""
	, gestor3_funcao = ""
	, gestor3_outra_funcao = ""
	, gestor3_nome = ""
	, gestor3_sexo = ""
	, gestor3_data_nascimento = ""
	, gestor3_email1 = ""
	, gestor3_email2 = ""
	, gestor3_telefone1 = ""
	, gestor3_telefone1_ramal = ""
	, gestor3_telefone2 = ""
	, gestor3_telefone2_ramal = ""
        , contato1_funcao = ""
	, contato1_outra_funcao = ""
	, contato1_nome = ""
	, contato1_sexo = ""
	, contato1_data_nascimento = ""
	, contato1_email1 = ""
	, contato1_email2 = ""
	, contato1_telefone1 = ""
	, contato1_telefone1_ramal = ""
	, contato1_telefone2 = ""
	, contato1_telefone2_ramal = ""
	, contato2_funcao = ""
	, contato2_outra_funcao = ""
	, contato2_nome = ""
	, contato2_sexo = ""
	, contato2_data_nascimento = ""
	, contato2_email1 = ""
	, contato2_email2 = ""
	, contato2_telefone1 = ""
	, contato2_telefone1_ramal = ""
	, contato2_telefone2 = ""
	, contato2_telefone2_ramal = ""
	, contato3_funcao = ""
	, contato3_outra_funcao = ""
	, contato3_nome = ""
	, contato3_sexo = ""
	, contato3_data_nascimento = ""
	, contato3_email1 = ""
	, contato3_email2 = ""
	, contato3_telefone1 = ""
	, contato3_telefone1_ramal = ""
	, contato3_telefone2 = ""
	, contato3_telefone2_ramal = ""
	, desktop = ""
	, mini_desktop = ""
	, impressora = ""
	, scanner = ""
	, webcam = ""
	, link = ""
	, idebs = {}
	, enems = {}
	, provas = {}
    )


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
ESCOLAS = __ACTIV.escolas
MAGKEYINSTITUTES = __ACTIV.magkeyinstitutes

def main():
    """ Para carregar as escolas no magkeyinstitute. Com o _id da mesma. """      

    #>>> db = server.create('python-tests')
    #>>> db['johndoe'] = dict(type='Person', name='John Doe')
    #>>> db['maryjane'] = dict(type='Person', name='Mary Jane')
    #>>> db['gotham'] = dict(type='City', name='Gotham City')
    #>>> map_fun = '''function(doc) {
    #...     if (doc.type == 'Person')
    #...         emit(doc.name, null);
    #... }'''
    #>>> for row in db.query(map_fun):
    #...     print row.key
    #
    
    map_fun = '''function(doc) {
                emit(doc.nome, null);
    }'''
    
    resultado = MAGKEYINSTITUTES.query(map_fun)
    #comecando de um determinado valor que ja existe no banco
    # oi, nce, nave e visitante
    mg_id = len(resultado)
    
    for row in ESCOLAS.query(map_fun):
        mg_id1= str(mg_id).zfill(4)
        print mg_id1  
        magkeyinstitute_data = _EMPTYINSTITUTE()
        magkeyinstitute_data["nome"] = row.key.encode('utf8')
        magkeyinstitute_data["school_id"] = row.id
        
        #print row.id, row.key
        #MAGKEYINSTITUTES[meg_id1] = magkeyinstitute_data
        mg_id += 1  
    

if __name__ == "__main__":
    main()
