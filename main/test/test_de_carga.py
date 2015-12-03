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

import core.model
import wiki.model
from wiki.model import _EMPTYWIKIMEMBERORCOMMUNITY

import unittest

WIKI_FORM = lambda: dict ({ "nomepag": "",
             "conteudo": "<b> Meu texto novinho </b>",
             "tags": "riodejaneiro carnaval2010"
           })
pagina = {}

class TestCarga(unittest.TestCase):
  """Testes de carga"""
  
  NUM_REQUESTED_FORMS = 0
  NUM_CREATED_USERS = 0
  NUM_REQUESTED_PAGES = 0
  NUM_CREATED_PAGES = 0
  
  def setUp(self):
    #core.model.REGISTRY = {}
    #core.model.PROFESSOR = {}
    #core.model.MAGKEYS = {}
    #core.model.REGISTRY = {}
    #core.model.USERSCHOOL = {}    
    #wiki.model.WIKI = {}
    #wiki.model.WIKIMEMBER = {}
    #wiki.model.WIKICOMMUNITY = {}  
    #wiki.model.FILES = {}
    #log.model.LOG = {}
    #log.model.NEWS = {}
    core.model.MAGKEYS = MAGKEYS_DEFAULT()  # recria chave mágica para que possa fazer outro cadastro
    
    self.app = TestApp(WsgiApp())
    registry.update(REGISTRY_FORM)
    login.update(LOGIN_FORM)
    pagina = WIKI_FORM()

  def tearDown(self):
    # remove pagina inicial dos usuários
    for i in range(self.NUM_CREATED_USERS):
          user = 'usuario%04d'%i
          doc_id = "%s/home" % user
          if doc_id in wiki.model.WIKI:
              del wiki.model.WIKI[doc_id]
              wikimember_data = _EMPTYWIKIMEMBERORCOMMUNITY()
              wikimember_data.update(wiki.model.WIKIMEMBER[user])
              wikimember_data["paginas"].remove(doc_id)
              wiki.model.WIKIMEMBER[user] = wikimember_data
    
    # remove os usuários criados
    for i in range(self.NUM_CREATED_USERS):
          user = 'usuario%04d'%i
          if user in core.model.REGISTRY:
              user_data = core.model.REGISTRY[user] 
              for key in user_data["mykeys"]:
                  del core.model.MAGKEYS[key]                    
              del core.model.REGISTRY[user]

    # remove as páginas do usuário
    user = 'usuario0000'
    for i in range(self.NUM_CREATED_PAGES):
          nomepagina = 'pagina%04d'%i
          doc_id = "%s/%s" % (user,nomepagina)
          if doc_id in wiki.model.WIKI:
              del wiki.model.WIKI[doc_id]
              wikimember_data = _EMPTYWIKIMEMBERORCOMMUNITY()
              wikimember_data.update(wiki.model.WIKIMEMBER[user])
              wikimember_data["paginas"].remove(doc_id)
              wiki.model.WIKIMEMBER[user] = wikimember_data


  def test_request_multiple_registry_forms(self):
    "Acessos ao formulário de cadastro (não vai ao BD)"
    for i in range(self.NUM_REQUESTED_FORMS):
          response = self.app.get('/new/user')
          assert 'input name="user" id="user" value="" type="text"' in response, "Erro: Não exibiu formulário de cadastro!"

  def test_create_multiple_users(self):
    "Cadastro de muitos usuários"
    for i in range(self.NUM_CREATED_USERS):
          registry['user'] = 'usuario%04d'%i
          response = self.app.post('/new/user', registry)
          assert registry['user'] in core.model.REGISTRY, "Erro: Não conseguiu cadastrar usuário"
          assert u'Cadastro criado com sucesso. Identifique-se para entrar na plataforma.' in response, response #"Erro: Não exibiu mensagem após cadastrar usuário com sucesso!"

  def test_request_multiple_user_pages(self):
    "Acessos à página inicial de um usuário"
    # cria um novo usuário
    # não está sendo removido, nem os registros criados em log e news.
    registry['user'] = 'usuario0000'
    response = self.app.post('/new/user', registry)
    # simula a existência de 4 amigos para que o news seja gerado.
    reg = core.model.REGISTRY['usuario0000']
    reg['amigos'] = ["livia", "mauricio", "julianne", "marcia"]
    core.model.REGISTRY['usuario0000'] = reg
    
    login['user'] = "usuario0000"
    self.app.post('/login', login)
    for i in range(self.NUM_REQUESTED_PAGES):
          response = self.app.get('/wiki/usuario0000/home')
          assert u'<!-- identificação da userpage utilizado para os testes. -->' in response, "Erro: Não exibiu a página do usuário!"
          assert '%s/home' % login["user"] in wiki.model.WIKI, "Erro: Não criou página inicial do usuário!"
    
  def test_create_multiple_wiki_pages(self):
    "Testa inclusão de muitas páginas de um usuário"
    pagina = WIKI_FORM()
    core.model.MAGKEYS = MAGKEYS_DEFAULT()  # recria chave mágica para que possa fazer outro cadastro
    
    registry['user'] = 'usuario0000'
    response = self.app.post('/new/user', registry)
    login['user'] = "usuario0000"
    self.app.post('/login', login)
    for i in range(self.NUM_CREATED_PAGES):
          pagina['nomepag'] = 'pagina%04d'%i
          #print pagina
          response = self.app.post('/wiki/newpage/usuario0000', pagina)
          assert u'302 Found' in response.status, response #"Erro: Não redirecionou!"
          #assert pagina['nomepag'] in response, "Erro: Não exibiu título da página incluída!"
          assert 'usuario0000/%s' % pagina['nomepag'] in wiki.model.WIKI, "Erro: Não incluiu a página!"
          assert 'usuario0000/%s' % pagina['nomepag'] in wiki.model.WIKIMEMBER["usuario0000"]["paginas"], "Erro: Não incluiu a página no WIKIMEMBER!"

  