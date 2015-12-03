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
                      MAGKEYS_DEFAULT, PRIVILEGIOS_DEFAULT

import re
import agenda.model as model
import core.model
import log.model
import educo_core.model
import unittest

POR_LOGIN_FORM = { "tipo":"ativo",
                   "login": "teste"
}

ALLOWED_USERS_DEFAULT =  lambda: dict ({
   "professor@rioeduca.net": {
          "email": "professor@rioeduca.net",
          "nome": "Professor Fulano de Tal",   
          "papel": "professor",
          "comunidades": [],
          "mkey": "12345"
   },
   "digitador@rioeduca.net": {
          "email": "digitador@rioeduca.net",
          "nome": "Digitador Fulano de Tal",   
          "papel": "digitador",
          "comunidades": [],
          "mkey": "12345"
   },
   "aluno@rioeduca.net": {
          "email": "aluno@rioeduca.net",
          "nome": "Aluno Fulano de Tal",   
          "papel": "aluno",
          "comunidades": [],
          "mkey": "12345"
   }                
})

class TestAdmin(unittest.TestCase):
   """Testes unitários para o módulo admin"""
   def setUp(self):
      
      log.model.LOG = {}            
      log.model.NEWS = {}
      model.AGENDA = {}
      core.model.REGISTRY = PRIVILEGIOS_DEFAULT()
      core.model.MAGKEYS = MAGKEYS_DEFAULT()    # recria chave mágica para que possa fazer outro cadastro  
      core.model.INVITES = {}
      core.model.USERSCHOOL = {}    
      educo_core.model.ALLOWED_USERS = ALLOWED_USERS_DEFAULT()
      educo_core.model.CADERNOS      = {}
      educo_core.model.ATIVIDADES    = {}
      educo_core.model.ACESSOS       = {}
      educo_core.model.SLIDES        = {}
      log.model.NOTIFICATIONERROR = {}
      log.model.NOTIFICATION = {}
    
      self.app = TestApp(WsgiApp())
      
      # registra usuário "teste"
      registry.update(REGISTRY_FORM)
      self.app.post('/new/user', registry)
      core.model.REGISTRY["teste"]["comunidades"] = ["Priv_Suporte_Educopedia", "PRIV_SUPORTE_ACTIV"]
      # registra usuário "teste2"
      registry['user'] = 'teste2'
      core.model.MAGKEYS = MAGKEYS_DEFAULT()    # recria chave mágica para que possa fazer outro cadastro  
      self.app.post('/new/user', registry)
      
      # faz login como teste
      login.update(LOGIN_FORM)
      self.app.post('/login', login)
      
   def tearDown(self):
      #self.mock.restore()
      #self.mock.verify()criou um evento na agenda
      #self.mock,MEMBER =None,None
      pass

   # -------------------------------------------------------------
   # Exibição do formulário de procura de usuários Educopédia
  
   def test_show_list_users_educo_form(self):
      "Testa a exibição do formulário de procura de usuários Educopedia"      
      response = self.app.get('/admin/listusers_educo')
      assert 'form action="/admin/listusers_educo" method="post">' in response, "Erro: Não exibiu formulário de busca de usuários Educopédia."

   def test_deny_list_users_educo_form(self):
      "Exibe mensagem de erro a um usuário que não tem privilégio de acessar o formulário de procura de usuários Educopédia"
      login["user"] = "teste2"
      self.app.post('/login', login)      
      response = self.app.get('/admin/listusers_educo', status=403)
      assert '403 Forbidden' in response.status, "Erro: Exibiu o form para alguém que não tem permissão."   

   # -------------------------------------------------------------
   # Exibição do formulário de procura de usuários Tonomundo

   def test_show_list_users_tnm_form(self):
      "Testa a exibição do formulário de procura de usuários Tonomundo"      
      response = self.app.get('/admin/listusers_tnm')
      assert 'form action="/admin/listusers_tnm" method="post">' in response, "Erro: Não exibiu formulário de busca de usuários Tonomundo."

   def test_deny_list_users_tnm_form(self):
      "Exibe mensagem de erro a um usuário que não tem privilégio de acessar o formulário de procura de usuários Tonomundo"
      login["user"] = "teste2"
      self.app.post('/login', login)      
      response = self.app.get('/admin/listusers_tnm', status=403)
      assert '403 Forbidden' in response.status, "Erro: Exibiu o form para alguém que não tem permissão."

   # -------------------------------------------------------------
   # Resultado da busca simples de usuários Educopédia
  
   def test_cant_find_allowed_user_educo_by_login(self):
      "Testa a busca pelo login de um usuário Educopédia pendente inexistente"      
      response = self.app.post('/admin/listusers_educo', { "tipo":"pendente", "login": "teste", "tipo_busca": "simples"})
      assert 'Nenhum usuário encontrado com estes critérios de busca.' in response, "Erro: Não exibiu mensagem: Nenhum usuário encontrado com estes critérios de busca."

   def test_find_allowed_user_educo_by_login(self):
      "Testa a busca de um usuário Educopédia pendente existente pelo login"      
      response = self.app.post('/admin/listusers_educo', { "tipo_busca": "simples", "tipo":"pendente", "login": "professor@rioeduca.net"})
      assert 'professor@rioeduca.net' in response, "Erro: Não encontrou um usuário Educopédia pendente."
      
   def test_cant_find_registry_user_educo_by_login(self):
      "Testa a busca de um usuário Educopédia ativo inexistente pelo login"      
      response = self.app.post('/admin/listusers_educo', { "tipo":"ativo", "login": "professor@rioeduca.net", "tipo_busca":"simples"})
      assert 'Nenhum usuário encontrado com estes critérios de busca.' in response, "Erro: Não exibiu mensagem: Nenhum usuário encontrado com estes critérios de busca."
 
   def test_find_registry_user_educo_by_login(self):
      "Testa a busca de um usuário Educopédia ativo existente pelo login"
      core.model.REGISTRY['teste']['papeis'].append("educo")
      response = self.app.post('/admin/listusers_educo', { "tipo":"ativo", "login": "teste", "tipo_busca":"simples"})
      assert 'teste' in response, "Erro: Não encontrou um usuário Educopédia ativo."

   # -------------------------------------------------------------
   # Resultado da busca simples de usuários Tonomundo
  
   def test_cant_find_user_tnm_by_login(self):
      "Testa a busca de um usuário Tonomundo inexistente pelo login"      
      response = self.app.post('/admin/listusers_tnm', {"login": "aluno", "tipo_busca": "simples"})
      assert 'Nenhum usuário encontrado com estes critérios de busca.' in response, "Erro: Não exibiu mensagem: Nenhum usuário encontrado com estes critérios de busca."

   def test_find_user_tnm_by_login(self):
      "Testa a busca de um usuário Tonomundo existente pelo login"      
      response = self.app.post('/admin/listusers_tnm', { "tipo_busca": "simples", "login": "teste"})
      assert 'teste' in response, "Erro: Não encontrou um usuário Tonomundo."

   # -------------------------------------------------------------
   # Resultado da busca avançada de usuários Educopédia
      
   def test_cant_find_registry_user_educo_by_no_name_and_no_papel(self):
      "Exibe mensagem de erro ao procurar por um usuário Educopédia ativo sem informar nome e papel"
      response = self.app.post('/admin/listusers_educo', { "tipo_busca": "avancada","tipo":"ativo", "login": "", "papel": "todos"})
      assert u'<div class="tnmMSG">Campo nome não preenchido e campo papel não selecionado.</div>' in response, "Erro: Não exibiu mensagem de erro."

   def test_cant_find_allowed_user_educo_by_no_name_and_no_papel(self):
      "Exibe mensagem de erro ao procurar por um usuário Educopédia pendente sem informar nome e papel"
      response = self.app.post('/admin/listusers_educo', { "tipo_busca": "avancada","tipo":"pendente", "login": "", "papel": "todos"})
      assert u'<div class="tnmMSG">Campo nome não preenchido e campo papel não selecionado.</div>' in response, "Erro: Não exibiu mensagem de erro."

   # -------------------------------------------------------------
   # Resultado da busca avançada de usuários Tonomundo
      
   def test_cant_find_registry_user_tnm_by_no_field_filled(self):
      "Exibe mensagem de erro ao procurar por um usuário Tonomundo ativo sem informar email, nome, papel e escola"
      response = self.app.post('/admin/listusers_tnm', { "tipo_busca": "avancada", "email": "", "nome": "", "papel": "todos", "escola": "todas"})
      assert u'<div class="tnmMSG">Campos nome e email não preenchidos e campos papel e escola não selecionados.</div>' in response, "Erro: Não exibiu mensagem de erro."
