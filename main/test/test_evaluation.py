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
:Home: `LABASE <http://labase.nce.ufrj.br/>`__
:Copyright: ©2009, `GPL <http://is.gd/3Udt>__. 
"""

from main import WsgiApp
from webtest import TestApp
from webob import Request, Response
from test_core import REGISTRY_FORM, LOGIN_FORM, registry, login, \
                      MAGKEYS_DEFAULT

#import mocker
#from mocker import Mocker
from datetime import datetime
import evaluation.model
import core.model
import wiki.model
import log.model
import unittest

CREATE_COMMUNITY_FORM = { "name":"comunidade5",
                        "description": "Primeira Comunidade",
                        "participacao": "Mediante Convite",
                        "privacidade": "Pública" }                        

EVALUATION_DEFAULT = lambda: dict( {
                        "comunidade5/av1":
                        {
                        "_id":"comunidade5/av1",
                        "nome":"av1",
                        "descricao":"primeira avaliação",
                        "tipo":"participantes",
                        "avaliados":['teste'],
                        "owner": "teste",
                        "data_inicio": "2010-05-05 14:45:40.631966",
                        "data_encerramento": "2020-05-07 14:45:40.631966",
                        "pontuacao": [3,1],
                        "data_cri": "2010-05-05 14:45:40.631966"
                        }
})

EVALUATION_COMMUNITY_DEFAULT = lambda: dict( {
                        "comunidade5":
                          {
                            "avaliacoes":["comunidade5/av1"]
                          }
})

CREATE_EVALUATION_FORM = lambda: dict(
          nome = "av2",
          descricao = "descrição",
          dia1 = "30",
          mes1 = "04",
          ano1 = "2010",
          hora1 = "08",
          min1 = "00",
          dia2 = "30",
          mes2 = "05",
          ano2 = "2020",
          hora2 = "08",
          min2 = "00",
          pontuacao = "2,1",
          teste = "S"
)

PERFORM_EVALUATION_FORM = lambda: dict(
          opcao1 = "teste", 
          opcao2 = "teste2",
)

create_evaluation = {}
create_community = {}
perform_evaluation = {}

class TestEvaluation(unittest.TestCase):
  """Testes unitários para o gerenciamento de avaliações"""
  def setUp(self):
    #self.mock = Mocker()
    #MEMBER = self.mock.mock()
    
    log.model.LOG = {}            
    log.model.NEWS = {}
    evaluation.model.EVALUATION = EVALUATION_DEFAULT()
    evaluation.model.EVALUATIONCOMMUNITY = EVALUATION_COMMUNITY_DEFAULT()
    core.model.REGISTRY = {}
    core.model.MAGKEYS = MAGKEYS_DEFAULT()    # recria chave mágica para que possa fazer outro cadastro  
    core.model.INVITES = {}
    core.model.USERSCHOOL = {}    
    #core.model.MAGKEYTYPES = {}
    log.model.NOTIFICATIONERROR = {}
    log.model.NOTIFICATION = {}
    
    self.app = TestApp(WsgiApp())
    login.update(LOGIN_FORM)
    #core.model.REGISTRY['teste']['papeis'].append('docente')
    registry.update(REGISTRY_FORM)
    
    self.app.post('/new/user', registry)
    registry['user'] = 'teste2'
    core.model.MAGKEYS = MAGKEYS_DEFAULT()    # recria chave mágica para que possa fazer outro cadastro  
    self.app.post('/new/user', registry)      
    registry['user'] = 'outrousuario'
    core.model.MAGKEYS = MAGKEYS_DEFAULT()    # recria chave mágica para que possa fazer outro cadastro  
    self.app.post('/new/user', registry)      
    self.app.post('/login', login)
    create_community.update(CREATE_COMMUNITY_FORM)
    core.model.REGISTRY['teste']['papeis'].append('docente')
    self.app.post('/new/community', create_community)
    create_evaluation.update(CREATE_EVALUATION_FORM())
    perform_evaluation.update(PERFORM_EVALUATION_FORM())

  def tearDown(self):
    #self.mock.restore()
    #self.mock.verify()
    #self.mock,MEMBER =None,None
    pass

  # -------------------------------------------------------------
  # Create new evaluation form
  
  def test_returns_newevaluation_form(self):
    "Retorna formulário para criação de nova avaliação para a comunidade5"
    response = self.app.get('/evaluation/member/new/comunidade5', headers={'Accept-Language':'pt-br'})
    assert u'Primeira Comunidade (comunidade5)' in response, "Erro: Não exibiu formulário para criar avaliação!"

  def test_reject_newevaluation_form_invalid_community(self):
    "Return error message: Comunidade inexistente."
    response = self.app.get('/evaluation/member/new/inexistente', headers={'Accept-Language':'pt-br'})
    assert u'Você não pode criar avaliação nesta comunidade.' in response, "Erro: Não exibiu mensagem informando que o usuário não é membro!"

  def test_reject_newevaluation_form_user_as_community(self):
    "Return error message: Comunidade inexistente."
    response = self.app.get('/evaluation/member/new/teste', headers={'Accept-Language':'pt-br'})
    assert u'Você não pode criar avaliação nesta comunidade.' in response, "Erro: Não exibiu mensagem informando que o usuário não é membro!"

  def test_reject_newevaluation_form_user_not_member(self):
    "Return error message: Você não é membro desta comunidade."
    login["user"] = "outrousuario"
    self.app.post('/login', login)
    response = self.app.get('/evaluation/member/new/comunidade5', headers={'Accept-Language':'pt-br'})
    assert u'Você não pode criar avaliação nesta comunidade.' in response, "Erro: Não exibiu mensagem informando que o usuário não é membro!"

  # -------------------------------------------------------------
  # Create new evaluation

  def test_accept_newevaluation_ok(self):
    "Check evaluation in database after evaluation ok"
    response = self.app.post('/evaluation/member/new/comunidade5', create_evaluation).follow()
    assert "comunidade5/av2" in evaluation.model.EVALUATION, "Erro: Não incluiu a avaliação na comunidade."
    assert "comunidade5/av2" in evaluation.model.EVALUATIONCOMMUNITY["comunidade5"]["avaliacoes"], "Erro: Não incluiu a avaliação em EVALUATIONCOMMUNITY."
    assert "comunidade5/av2" in response, "Erro: Não exibiu a página das avaliações da comunidade."
    
  def test_reject_newcommunity_double_evaluation_name(self):
    "Return error message: Já existe uma avaliação com este nome"
    self.app.post('/evaluation/member/new/comunidade5', create_evaluation).follow()
    #print evaluation.model.EVALUATION
    response = self.app.post('/evaluation/member/new/comunidade5', create_evaluation)
    assert u'Já existe uma avaliação com este nome' in response, "Erro: Não exibiu a mensagem 'Já existe uma avaliação com este nome'"
      
  def test_reject_evaluation_without_name(self):
    "Return error message: Nome de avaliação inválido"
    create_evaluation["nome"]=""
    response = self.app.post('/evaluation/member/new/comunidade5', create_evaluation)
    assert u"Nome da avaliação não informado.<br/>" in response, "Erro: Não exibiu a mensagem de nome inválido."

  def test_accept_evaluation_with_special_chars(self):
    "Criação e aceitação de avaliação cujo nome contem caracteres especiais e espaço em branco."
    create_evaluation["nome"]="Avaliação %$#@!"
    response = self.app.post('/evaluation/member/new/comunidade5', create_evaluation).follow()
    assert u"Avaliacao_" in response, "Erro: Não exibiu a mensagem de nome inválido."

  def test_reject_evaluation_without_pontuation(self):
    "Return error message: O campo 'Pontuação' não foi preenchido"
    create_evaluation["pontuacao"]=""
    response = self.app.post('/evaluation/member/new/comunidade5', create_evaluation)
    assert u"O campo 'Pontuação' não foi preenchido" in response, "Erro: Não exibiu a mensagem de pontuação não preenchida."

  def test_reject_evaluation_without_first_date(self):
    "Return error message: Data de início inválida."
    create_evaluation["dia1"]=""
    response = self.app.post('/evaluation/member/new/comunidade5', create_evaluation)
    assert u"Data de início inválida." in response, "Erro: Não exibiu a mensagem de data de início inválida."

  def test_reject_evaluation_without_second_date(self):
    "Return error message: Data de encerramento inválida."
    create_evaluation["dia2"]=""
    response = self.app.post('/evaluation/member/new/comunidade5', create_evaluation)
    assert u"Data de encerramento inválida." in response, "Erro: Não exibiu a mensagem de data de encerramento inválida."

  # -------------------------------------------------------------
  # List of Evaluations
  
  def test_list_of_evaluations(self):
    "Return list of evaluations"
    response = self.app.get('/evaluation/comunidade5')
    assert u'<a href="/evaluation/comunidade5/av1">av1</a>' in response, "Erro: Não exibiu tela com a comunidade criada!"
     
  # -------------------------------------------------------------
  # Perform the evaluation

  def test_returns_evaluation_form(self):
    "Retorna formulário para realização da avaliação"
    response = self.app.get('/evaluation/comunidade5/av1', headers={'Accept-Language':'pt-br'})
    assert u'<i>Avaliação de participantes<br/>' in response, "Erro: Não exibiu formulário para criar avaliação!"
    assert u'<select name="opcao1">' in response, "Erro: Não exibiu formulário para criar avaliação!"

  def test_evaluation_form_before_beginning(self):
    "Retorna mensagem de avaliação não iniciada"
    evaluation.model.EVALUATION["comunidade5/av1"]["data_inicio"] = "2019-05-05 14:45:40.631966"
    response = self.app.get('/evaluation/comunidade5/av1', headers={'Accept-Language':'pt-br'})
    assert u'<div class="tnmMSG">Fora do período de avaliação.</div>' in response, "Erro: Não exibiu mensagem de que a avaliação está fora do período de avaliação!"

  def test_accept_evaluation_ok(self):
    "Check evaluation in database after evaluation ok"
    # inclui mais um participante na comunidade para que a avaliação possa ser feita
    core.model.REGISTRY["comunidade5"]["participantes"].append("teste2")
    core.model.REGISTRY["teste2"]["comunidades"].append("comunidade5")
    # recupera o numero de pontos de cada um antes da avaliação
    votos_em_teste = votos_em_teste2 = 0
    if "teste" in evaluation.model.EVALUATION["comunidade5/av1"]:
      votos_em_teste = int(evaluation.model.EVALUATION["comunidade5/av1"]["teste"]["votos_recebidos"])
    if "teste2" in evaluation.model.EVALUATION["comunidade5/av1"]:
      votos_em_teste2 = int(evaluation.model.EVALUATION["comunidade5/av1"]["teste2"]["votos_recebidos"])
    # realiza a avaliação
    response = self.app.post('/evaluation/comunidade5/av1', perform_evaluation)
    # verifica se existem os registros dos usuários teste e teste2
    assert "teste" in evaluation.model.EVALUATION["comunidade5/av1"], "Erro: Não incluiu teste no EVALUATION."
    assert "teste2" in evaluation.model.EVALUATION["comunidade5/av1"], "Erro: Não incluiu teste2 no EVALUATION."
    # verifica se as informações do avaliador foram armazenadas
    assert evaluation.model.EVALUATION["comunidade5/av1"]["teste"]["votos_dados"]==["teste","teste2"], "Erro: Não incluiu a informação dos votos dados pelo avaliador no BD."
    # verfica se os pontos dos avaliados foram incrementados corretamente
    assert int(evaluation.model.EVALUATION["comunidade5/av1"]["teste"]["votos_recebidos"]) == votos_em_teste + 3, \
            "Erro: Não incrementou o número de pontos do avaliado teste no BD."
    assert int(evaluation.model.EVALUATION["comunidade5/av1"]["teste2"]["votos_recebidos"]) == votos_em_teste2 + 1, \
            "Erro: Não incrementou o número de pontos do avaliado teste2 no BD."
    # verifica se a mensagem final foi exibida
    assert "Avaliação realizada com sucesso." in response, "Erro: Não exibiu mensagem de avaliação realizada com sucesso."
    
  def test_reject_user_selected_twice(self):
    "Verifica se um usuário foi selecionado mais de uma vez"
    perform_evaluation["opcao2"]="teste"
    response = self.app.post('/evaluation/comunidade5/av1', perform_evaluation)
    assert "Alguma opção foi selecionada mais de uma vez." in response, "Erro: Não exibiu mensagem de usuário selecionado mais de uma vez."

  def test_reject_no_user_selected(self):
    "Verifica se alguma opção deixou de ser selecionada"
    perform_evaluation["opcao2"]=""
    response = self.app.post('/evaluation/comunidade5/av1', perform_evaluation)
    assert "Alguma opção não foi selecionada." in response, "Erro: Não exibiu mensagem de opção não selecionada."

  def test_reject_double_evaluation(self):
    "Verifica se um usuário pode avaliar mais de uma vez"
    # inclui mais um participante na comunidade para que a avaliação possa ser feita
    core.model.REGISTRY["comunidade5"]["participantes"].append("teste2")
    core.model.REGISTRY["teste2"]["comunidades"].append("comunidade5")
    self.app.post('/evaluation/comunidade5/av1', perform_evaluation)
    response = self.app.post('/evaluation/comunidade5/av1', perform_evaluation)
    assert "Você já realizou esta avaliação." in response, "Erro: Não exibiu mensagem de avaliação duplicada."
    
  # -------------------------------------------------------------
  # Show final results
  def test_show_results_of_evaluation(self):
    "Check evaluation in database after evaluation ok"
    # inclui mais um participante na comunidade para que a avaliação possa ser feita
    core.model.REGISTRY["comunidade5"]["participantes"].append("teste2")
    core.model.REGISTRY["teste2"]["comunidades"].append("comunidade5")
    # realiza duas avaliações como teste e como teste2
    self.app.post('/evaluation/comunidade5/av1', perform_evaluation)
    self.app.post('/login', login)    
    self.app.post('/evaluation/comunidade5/av1', perform_evaluation)
    # altero a data de encerramento
    evaluation.model.EVALUATION["comunidade5/av1"]["data_encerramento"] = "2010-05-06 14:45:40.631966"
    # entro na avaliação mais uma vez para ver o resultado
    response = self.app.get('/evaluation/comunidade5/av1', headers={'Accept-Language':'pt-br'})
    # verifica se a mensagem final foi exibida
    assert "Resultado da avaliação comunidade5/av1:" in response, "Erro: Não exibiu resultado da avaliação."
    assert "teste - 6 pontos <br/>" in response, "Erro: Não exibiu resultado da avaliação."
    assert "teste2 - 2 pontos <br/>" in response, "Erro: Não exibiu resultado da avaliação."
    
  def test_show_results_of_evaluation(self):
    "Check evaluation in database after evaluation ok"
    # inclui mais um participante na comunidade para que a avaliação possa ser feita
    core.model.REGISTRY["comunidade5"]["participantes"].append("teste2")
    core.model.REGISTRY["teste2"]["comunidades"].append("comunidade5")
    # realiza duas avaliações como teste e como teste2
    self.app.post('/evaluation/comunidade5/av1', perform_evaluation)
    login["user"] = "teste2"
    self.app.post('/login', login)    
    self.app.post('/evaluation/comunidade5/av1', perform_evaluation)
    # altero a data de encerramento
    evaluation.model.EVALUATION["comunidade5/av1"]["data_encerramento"] = "2010-05-06 14:45:40.631966"
    # entro na avaliação mais uma vez para ver o resultado
    response = self.app.get('/evaluation/comunidade5/av1', headers={'Accept-Language':'pt-br'})
    # verifica se a mensagem final foi exibida
    assert "Fora do período de avaliação." in response, "Erro: Não exibiu mensagem de que está fora do período de avaliação."    

