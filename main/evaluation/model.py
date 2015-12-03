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
try:
  from couchdb.schema import Document, TextField, IntegerField, LongField, DateTimeField, DictField, ListField, Schema, FloatField
except ImportError:
  from couchdb.mapping import Document, TextField, IntegerField, LongField, DateTimeField, DictField, ListField, FloatField
  from couchdb.mapping import Mapping as Schema

#from libs.permissions import usersAllowedToRead
import libs.permissions

import database
#import core.database

from operator import itemgetter

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

class Evaluation(Document):
    # _id = "registry_id/nome_avaliacao"
    nome              = TextField(default="") 
    tipo              = TextField() # "participantes" ou "páginas"
    descricao         = TextField(default="") 
    avaliados         = ListField(TextField()) # lista de itens a serem avaliados
    owner             = TextField() # quem criou a avaliação.
    data_inicio       = TextField() 
    data_encerramento = TextField() 
    pontuacao         = ListField(TextField()) 
    data_cri          = TextField() 
    data_alt          = TextField() 
    avaliacoes        = DictField()
    # {
    #    <user>: {
    #        votos_dados: [<user1>, <user2>, ...],
    #        votos_recebidos: <num de pontos>
    #    }
    #    ...
    # }


    @classmethod    
    def listEvaluations(self, user, registry_id):
        lista_aval = []
        for row in database.EVALUATION.view('evaluation/all_data',startkey=[registry_id],endkey=[registry_id, {}]):
            aval = dict()
            aval.update(row.value)
            aval["_id"] = row.value["_id"]
            aval["jaAvaliou"] = "avaliacoes" in row.value and user in row.value["avaliacoes"] and row.value["avaliacoes"][user]["votos_dados"]
            lista_aval.append(aval)
       
        return lista_aval

    @classmethod    
    def listEvaluationsByUser(self, registry_id):
        avaliacoes = {}
        for row in database.EVALUATION.view('evaluation/all_data',startkey=[registry_id],endkey=[registry_id, {}]):
            avaliacoes[row.key[1]] = {}
            nomeobj = row.value["_id"].split("/")[1]            
            for usuario in libs.permissions.usersAllowedToRead("evaluation", registry_id, nomeobj):
                if usuario in row.value["avaliacoes"]:
                    avaliacoes[row.key[1]][usuario] = row.value["avaliacoes"][usuario]["votos_dados"]
                else:
                    avaliacoes[row.key[1]][usuario] = []
                
        return avaliacoes
                        
    def alreadyHasEvaluated(self, user):
        return  user in self.avaliacoes and self.avaliacoes[user]["votos_dados"]


    def calcResultAvaliacao(self):

        """ retorna dicionário com uma avaliacao e compilação dos resultados. """
        
        resultado_avaliacao = {}
        for item in self.avaliados:
            if item in self.avaliacoes:
                resultado_avaliacao[item] = self.avaliacoes[item]["votos_recebidos"]
            else:
                resultado_avaliacao[item] = 0
                
        resultado_avaliacao = resultado_avaliacao.items()
        resultado_avaliacao.sort(key = itemgetter(1), reverse=True) #ordena os participantes pelos votos recebidos
        
        aval_data = dict(
                _id            = self.id,
                nome              = self.nome,
                tipo              = self.tipo, 
                descricao         = self.descricao, 
                avaliados         = self.avaliados, 
                owner             = self.owner, 
                data_inicio       = self.data_inicio, 
                data_encerramento = self.data_encerramento, 
                pontuacao         = self.pontuacao, 
                data_cri          = self.data_cri, 
                data_alt          = self.data_alt,  
                avaliacoes        = self.avaliacoes,
                result_aval       = resultado_avaliacao,
        )
        
        return aval_data
            
    def save(self, id=None, db=database.EVALUATION):
        if not self.id and id: self.id = id
        self.store(db)
        
    def retrieve(self, id, db=database.EVALUATION):
        return Evaluation.load(db, id)
    
    def delete(self, db=database.EVALUATION):
        #db.delete(self)
        del db[self.id]



