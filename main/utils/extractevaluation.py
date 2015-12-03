#-*- coding: utf-8 -*-
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

_DOCBASES = ['registry', 'evaluation', 'evaluationcommunity']


_EMPTYMEMBER = lambda: dict(
          user = ""
        , passwd = ""
        , name = ""
        , lastname = ""
        , email = ""
        , photo = ""
        , amigos = []
        , amigos_pendentes = []
        , amigos_convidados = []
        , comunidades = []
        , comunidades_pendentes = []
    )

_EMPTYCOMMUNITY = lambda: dict(
          name = ""
        , description = ""
        , owner = ""
        , photo = ""
        , participantes_pendentes = []
        , participantes = []
    )


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

_EMPTYEVALUATIONCOMMUNITY = lambda: dict(
# _id = "registry_id" da comunidade
#
# Permite obter a lista de avaliações de uma determinada comunidade.
        avaliacoes = []
        # avaliacoes = [<aval_id1>, <aval_id2>, ...]         
)


class Activ(Server):
    "Active database"
    evaluation = {}
    evaluationcommunity = {}
    
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
EVALUATIONCOMMUNITY = __ACTIV.evaluationcommunity
REGISTRY = __ACTIV.registry

def main():
          
    #dicionario
    #
    arquivo = open ( "avaliacao.txt", "w" )
    avalusu = {}
    chaves = {}
    usudict = {}
    linha = ""
    criterios = [u'Como_voc\xea_classifica_seus_pares_quanto_a_pesquisa_de_objetos_virtuais_de_aprendizagem',
                 u'Roteiro_grupos_especialista',
                 u'Roteiro_conte\xfados_curriculares',
                 u'Identificou_falhas_e_colaborou',
                 u'PESQUISA_OBJETO_DIA_16',
                 u'ROTEIRO_GRUPOS_ESPECIALISTAS_DIA_16',
                 u'ROTEIRO_CONTEUDOS_CURRICULARES_DIA_16',
                 u'IDENTIFICOU_FALHAS_E_COLABOROU_DIA_16']

    for aval in EVALUATION:
	    chaves[aval.split("/")[-1]] = 0
	    #chaves.append(aval.encode('utf8'))
	    for usuario in EVALUATION[aval]:
		if 'votos_dados' in EVALUATION[aval.encode('utf8')][usuario]:
		    if not usuario in avalusu:
			avalusu[usuario] = {}
		    usuaval = avalusu[usuario] 
		    usuaval[aval.encode('utf8')] = EVALUATION[aval.encode('utf8')][usuario]['votos_dados']
	            avalusu[usuario]=usuaval
	
               #print avalusu

    #print "***** ", chaves.keys(), "*****"
    #print  [ 'lidiane_silva', [(gt, avalusu['lidiane_silva'][gt]) for gt in avalusu['lidiane_silva']  ]]
    #print avalusu["franciane_motta"]
    linha = "    ,"

    #print "fazendo o for "
    for criterio in criterios:
        linha = linha + ", " + criterio
    arquivo.write("%s\n" %linha.encode('utf8'))
    #print linha
    linha = ""
    for usuario in avalusu:
          #print usuario
          #if usuario  != 'franciane_motta':
	  #	continue
          linha = str(usuario)
          #print linha
          primeira = True
          for criterio in criterios:   
              #print criterio
              imprimiu = False
              
              for item in avalusu[usuario].items():
                  if criterio.encode('utf8') in item[0]:
                      if primeira:
                         linha = linha + ", "+ item[0].split("/")[0]
                         primeira = False
                      linha = linha + ", "+ str(item[1])
                      #print item[1] , ", " ;
                      imprimiu = True
              if not imprimiu:
                 if primeira:
                    linha = linha + ", "+ item[0].split("/")[0]
                    primeira = False
                 linha = linha + ", "+ "[ ]"     
                 #print [] , " , " ;
          arquivo.write("%s\n"% linha)
          print linha
          #print  [ 'lidiane_silva', [(gt, avalusu['lidiane_silva'][gt]) for chave in chaves gt in avalusu['lidiane_silva']  ]]

if __name__ == "__main__":
    main()
