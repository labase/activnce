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

import re
import agenda.model as model
import core.model
import log.model
import unittest

COMMUNITY_FORM = { "name":"comunidade1",
                   "description": "Primeira Comunidade",
                   "participacao": "Mediante Convite",
                   "privacidade": "Pública",
                   "tags": ""
}

community = {}

AGENDA_FORM1 = {
                "dia": 25,
                "mes": 12,
                "ano": 2010,
                "msg": "Festa de Natal!"
}
AGENDA_ALTERADA1 = {
                "dia": 25,
                "mes": 12,
                "ano": 2010,
                "msg": "msg alterada"
}
AGENDA_FORM2 = {
                "dia": 31,
                "mes": 12,
                "ano": 2010,
                "msg": "Festa de Ano Novo!"
}
agenda1 = {}
agenda_alterada = {}

class TestAgenda(unittest.TestCase):
   """Testes unitários para a wiki"""
   def setUp(self):
      
      log.model.LOG = {}            
      log.model.NEWS = {}
      model.AGENDA = {}
      core.model.REGISTRY = {}
      core.model.MAGKEYS = MAGKEYS_DEFAULT()    # recria chave mágica para que possa fazer outro cadastro  
      core.model.INVITES = {}
      core.model.USERSCHOOL = {}    
      log.model.NOTIFICATIONERROR = {}
      log.model.NOTIFICATION = {}      
      #core.model.MAGKEYTYPES = {}
      
      self.app = TestApp(WsgiApp())
      registry.update(REGISTRY_FORM)
      self.app.post('/new/user', registry)
      login.update(LOGIN_FORM)
      self.app.post('/login', login)
      registry['user'] = 'amigo1'
      core.model.MAGKEYS = MAGKEYS_DEFAULT()    # recria chave mágica para que possa fazer outro cadastro  
      self.app.post('/new/user', registry)
      community.update(COMMUNITY_FORM)
      core.model.MAGKEYS = MAGKEYS_DEFAULT()    # recria chave mágica para que possa fazer outro cadastro
      core.model.REGISTRY['teste']['papeis'].append('docente')
      
      self.app.post('/new/community', community)
      #assert False, core.model.REGISTRY['comunidade1']
      agenda1.update(AGENDA_FORM1)
      agenda_alterada.update(AGENDA_ALTERADA1)
      
   def tearDown(self):
      #self.mock.restore()
      #self.mock.verify()criou um evento na agenda
      #self.mock,MEMBER =None,None
      pass

 # -------------------------------------------------------------
  # Exibição da Agenda sem eventos
  
   def test_new_event_form_to_user(self):
      "Testa a exibição de agenda vazia para um usuário:"      
      response = self.app.get('/agenda/teste')
      assert 'Criar novo evento' in response, "Erro: Não exibiu link para criar um novo evento"
      assert 'Nenhum evento encontrado.' in response, "Erro: Não exibiu msg 'Nenhum evento encontrado.'"

   def test_new_event_form_to_community(self):
      "Testa a exibição de agenda vazia para uma comunidade:"      
      response = self.app.get('/agenda/comunidade1')
      assert 'Criar novo evento' in response, "Erro: Não exibiu link para criar um novo evento"
      assert 'Nenhum evento encontrado.' in response, "Erro: Não exibiu msg 'Nenhum evento encontrado.'"
  

  # -------------------------------------------------------------
  # Criação e exibição de evento na agenda e exibição de eventos 
  
   def test_new_event_form_to_user(self):
      "Testa a exibição do formulário para criação de um evento para um usuário:"      
      response = self.app.get('/agenda/new/teste')
      assert 'Data:' in response, "Erro: Não exibiu formulário para criação de um novo evento para usuario"
      
   def test_new_event_form_to_user_whitout_permission(self):
      "Testa a exibição de mensagem 'Você não tem permissão para criar eventos nesta agenda.' para usuario sem permissão"
      login["user"] = "amigo1"
      self.app.post('/login', login)
      response = self.app.get('/agenda/new/teste')
      assert 'Você não tem permissão para criar eventos nesta agenda.' in response, "Erro: Não exibiu 'Você não tem permissão para criar eventos nesta agenda.'"
      
   def test_new_event_form_to_community(self):
      "Testa a exibição do formulário para criação de um evento para uma comunidade:"      
      response = self.app.get('/agenda/new/comunidade1')
      assert 'Data:' in response, "Erro: Não exibiu formulário para criação de um novo evento para comunidade"
      
   def test_new_event_form_to_community_fail(self):
      "Testa a exibição da mensagem 'Você não tem permissão para criar eventos nesta agenda.' para usuario que não está na comunidade"      
      login["user"] = "amigo1"
      self.app.post('/login', login)
      response = self.app.get('/agenda/new/comunidade1')
      assert 'Você não tem permissão para criar eventos nesta agenda.' in response, "Erro: Não exibiu 'Você não tem permissão para criar eventos nesta agenda.'"
            
   def test_create_event_to_user_ok(self):
      "Testa a criacao de um evento na agenda para usuario"      
      response = self.app.post('/agenda/new/teste', agenda1).follow()
      assert 'Festa de Natal!' in response, "Erro: Não exibiu evento criado"
      assert '201012' in model.AGENDA["teste"]["events"], "Erro: Não salvou evento no banco"
            
   def test_create_event_to_user_whitout_permission(self):
      "Testa a exibição de mensagem de não permissão para um usuário que tenta criar evento na agenda de outro usuário"
      login["user"] = "amigo1"
      self.app.post('/login', login)
      response = self.app.post('/agenda/new/teste', agenda1)
      assert 'Você não tem permissão para criar eventos nesta agenda.' in response, "Erro: Não exibiu Você não tem permissão para criar eventos nesta agenda."
      assert "teste" not in model.AGENDA, "Erro: Salvou evento no banco"
      
   def test_create_event_to_community_fail(self):
      "Testa a exibição de mensagem de não permissão para um usuário que tenta criar evento na agenda de comunidade onde ele não é participante"
      login["user"] = "amigo1"
      self.app.post('/login', login)
      response = self.app.post('/agenda/new/comunidade1', agenda1)
      assert 'Você não tem permissão para criar eventos nesta agenda.' in response, "Erro: Não exibiu Você não tem permissão para criar eventos nesta agenda."
      assert "comunidade1" not in model.AGENDA, "Erro: Salvou evento no banco"
      
   def test_create_event_whitout_day(self):
      "Testa a exibição da mensagem 'O Dia não pode ser vazio.' para tentativa de criar evento sem preencher o campo dia"      
      agenda1["dia"] = ""
      response = self.app.post('/agenda/new/teste', agenda1)
      assert 'O Dia não pode ser vazio.<br>' in response, "Erro: Não exibiu 'O Dia não pode ser vazio.<br>'"
      assert "teste" not in model.AGENDA, "Erro: Salvou evento no banco"
      
   def test_create_event_whitout_month(self):
      "Testa a exibição da mensagem 'O Mês não pode ser vazio.' para tentativa de criar evento sem preencher o campo mês"      
      agenda1["mes"] = ""
      response = self.app.post('/agenda/new/teste', agenda1)
      assert 'O Mês não pode ser vazio.<br>' in response, "Erro: Não exibiu 'O Mês não pode ser vazio.<br>'"
      assert "teste" not in model.AGENDA, "Erro: Salvou evento no banco"
      
   def test_create_event_whitout_year(self):
      "Testa a exibição da mensagem 'O Ano não pode ser vazio.' para tentativa de criar evento sem preencher o campo ano"      
      agenda1["ano"] = ""
      response = self.app.post('/agenda/new/teste', agenda1)
      assert 'O Ano não pode ser vazio.<br>' in response, "Erro: Não exibiu 'O Ano não pode ser vazio.<br>'"
      assert "teste" not in model.AGENDA, "Erro: Salvou evento no banco"
      
   def test_create_event_whitout_message(self):
      "Testa a exibição da mensagem 'O conteúdo da Mensagem não pode ser vazio.' para tentativa de criar evento sem preencher o campo mensagem"      
      agenda1["msg"] = ""
      response = self.app.post('/agenda/new/teste', agenda1)
      assert 'O conteúdo da Mensagem não pode ser vazio.<br>' in response, "Erro: Não exibiu 'O conteúdo da Mensagem não pode ser vazio.<br>'"
      assert "teste" not in model.AGENDA, "Erro: Salvou evento no banco"
      
   def test_create_event_whith_invalid_date(self):
      "Testa a exibição da mensagem 'Data inválida.' para tentativa de criar evento preenchendo com data inválida"      
      agenda1["dia"] = "di"
      response = self.app.post('/agenda/new/teste', agenda1)
      assert 'Data inválida.<br/>' in response, "Erro: Não exibiu 'Data inválida.<br>'"
      assert "teste" not in model.AGENDA, "Erro: Salvou evento no banco"
      
 # -------------------------------------------------------------
  # Alteração de evento na agenda  

   def test_edit_event_form_user(self):
      "Testa a exibição da tela de edição de um evento na agenda para usuario"      
      self.app.post('/agenda/new/teste', agenda1)
      response = self.app.get('/agenda/edit/teste?data=20101225')
      assert '<h2>Data:</h2> 25 / 12 / 2010' in response, "Erro: Não exibiu página de alteração de evento para usuario"
      
   def test_edit_event_form_community(self):
      "Testa a exibição da tela de edição de um evento na agenda para usuario"      
      self.app.post('/agenda/new/comunidade1', agenda1)
      response = self.app.get('/agenda/edit/comunidade1?data=20101225')
      assert '<h2>Data:</h2> 25 / 12 / 2010' in response, "Erro: Não exibiu página de alteração de evento para comunidade"
      
   def test_edit_event(self):
      "Testa a alteração de um evento na agenda para usuario"      
      self.app.post('/agenda/new/teste', agenda1)
      response = self.app.post('/agenda/edit/teste?data=20101225', agenda_alterada).follow()
      assert 'msg alterada' in response, "Erro: Não alterou o evento"
      assert 'msg alterada' in model.AGENDA["teste"]["events"]['201012']['25'][0]['msg'], "Erro: Não salvou evento no banco"
      
   def test_edit_event_to_user_whitout_permission(self):
      "Testa a exibição de mensagem de não permissão para um usuário que tenta alterar evento na agenda de outro usuário"
      self.app.post('/agenda/new/teste', agenda1)
      login["user"] = "amigo1"
      self.app.post('/login', login)
      response = self.app.post('/agenda/edit/teste?data=20101225', agenda_alterada)
      assert 'Você não tem permissão para criar eventos nesta agenda.' in response, "Erro: Não exibiu Você não tem permissão para criar eventos nesta agenda."
      assert 'msg alterada' not in model.AGENDA["teste"]["events"]['201012']['25'][0]['msg'], "Erro: Salvou evento no banco"
      
   def test_edit_event_whitout_message(self):
      "Testa a exibição da mensagem 'O conteúdo da Mensagem não pode ser vazio.' para tentativa de alterar evento sem preencher o campo mensagem"
      self.app.post('/agenda/new/teste', agenda1)
      agenda1["msg"] = ""
      response = self.app.post('/agenda/edit/teste?data=20101225', agenda1)
      assert 'O conteúdo da Mensagem não pode ser vazio.<br>' in response, "Erro: Não exibiu 'O conteúdo da Mensagem não pode ser vazio.<br>'"
      
   def test_edit_event_to_community_fail(self):
      "Testa a exibição de mensagem de não permissão para um usuário que tenta editar evento na agenda de comunidade onde ele não é participante"
      self.app.post('/agenda/new/comunidade1', agenda1)
      login["user"] = "amigo1"
      self.app.post('/login', login)
      response = self.app.post('/agenda/edit/comunidade1?data=20101225', agenda_alterada)
      assert 'Você não tem permissão para criar eventos nesta agenda.' in response, "Erro: Não exibiu Você não tem permissão para criar eventos nesta agenda."
      assert 'msg alterada' not in model.AGENDA["comunidade1"]["events"]['201012']['25'][0]['msg'], "Erro: Salvou evento no banco"

# -------------------------------------------------------------
  # Exclusão de eventos na Agenda
  
   def test_delete_event(self):
      "Testa a remoção de um evento na agenda para usuario"      
      self.app.post('/agenda/new/teste', agenda1)
      response = self.app.get('/agenda/delete/teste?data=20101225', agenda1)
      assert '201012' not in model.AGENDA["teste"]["events"], "Erro: Não excluiu evento do banco"
      
   def test_delete_event_fail(self):
      "Testa a exibição de mensagem de não permissão para um usuário que tenta excluir evento da agenda de outro usuário"
      self.app.post('/agenda/new/teste', agenda1)
      login["user"] = "amigo1"
      self.app.post('/login', login)
      response = self.app.get('/agenda/delete/teste?data=20101225', agenda1)
      assert 'Você não tem permissão para criar eventos nesta agenda.' in response, "Erro: Não exibiu Você não tem permissão para criar eventos nesta agenda."
      assert '201012' in model.AGENDA["teste"]["events"], "Erro: Excluiu evento do banco"
      
   def test_delete_event_community(self):
      "Testa a remoção de um evento na agenda para uma comunidade"      
      self.app.post('/agenda/new/comunidade1', agenda1)
      response = self.app.get('/agenda/delete/comunidade1?data=20101225', agenda1)
      assert '201012' not in model.AGENDA["comunidade1"]["events"], "Erro: Não excluiu evento do banco"
      
   def test_delete_event_fail_community(self):
      "Testa a exibição de mensagem de não permissão para um usuário que tenta excluir evento da agenda de uma comunidade na qual ele não é participante"
      self.app.post('/agenda/new/comunidade1', agenda1)
      login["user"] = "amigo1"
      self.app.post('/login', login)
      response = self.app.get('/agenda/delete/comunidade1?data=20101225', agenda1)
      assert 'Você não tem permissão para criar eventos nesta agenda.' in response, "Erro: Não exibiu Você não tem permissão para criar eventos nesta agenda."
      assert '201012' in model.AGENDA["comunidade1"]["events"], "Erro: Excluiu evento do banco"
      
   def test_delete_event_invalid_date(self):
      "Testa a exibição de mensagem de erro para usuario que tentar remover evento entrando com data inválida"      
      self.app.post('/agenda/new/teste', agenda1)
      response = self.app.get('/agenda/delete/teste?data=201012253', agenda1)
      assert u"data inválida.", "Erro: Não exibiu mensagem de data invalida"