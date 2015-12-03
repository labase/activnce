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
import invites.model
import wiki.model

import unittest

from datetime import datetime

WIKI_FORM = lambda: dict ({ "nomepag": "",
             "conteudo": "<b> Meu texto novinho </b>",
             "tags": "riodejaneiro carnaval2010"
           })
pagina = {}

CREATE_COMMUNITY_FORM = lambda: dict ( name= "dev_comu_teste",
                          description= "Comunidade Teste",
                          participacao= u"Obrigatória",
                          privacidade= u"Pública" )
community = {}

class TestCarga(unittest.TestCase):
  """Testes de carga"""
  
  NUM_REQUESTED_FORMS = 0
  NUM_CREATED_USERS = 0
  NUM_REQUESTED_PAGES = 0
  NUM_CREATED_PAGES = 0
 
  f = open('./testfile', 'w+')
 
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

    
    self.app = TestApp(WsgiApp())
    registry.update(REGISTRY_FORM)
    
    #login.update(LOGIN_FORM)
    pagina = WIKI_FORM()
    community = CREATE_COMMUNITY_FORM()
    
    "Faz login como admin para criar uma comunidade"
    login.update(LOGIN_FORM)
    login["user"] =   'activ_admin'
    login["passwd"] = '123456'
    response = self.app.post('/login', login).follow().follow()
            
    "Cria uma comunidade teste onde os usuários serão inseridos por default"
    response = self.app.post('/new/community', community) 
    #assert u'<div class="tnmMSG">Cadastro criado com sucesso.</div>' in response, response
    
    
  def tearDown(self):
      # remove a comunidade teste eseus arquivos na wiki
      comu_teste = "dev_comu_teste"
      doc_id = "%s/home" % comu_teste
      if doc_id in wiki.database.WIKI:
          del wiki.database.WIKI[doc_id]
      if doc_id in wiki.database.WIKI:
          del wiki.database.WIKI[doc_id]
      if comu_teste in core.database.REGISTRY:
          del core.database.REGISTRY[comu_teste]
  
      for i in range(self.NUM_CREATED_USERS):
          user = 'dev_usu_teste%04d'%i
          
          # remove pagina inicial (home e indice)
          doc_id = "%s/home" % user
          if doc_id in wiki.database.WIKI:
              del wiki.database.WIKI[doc_id]

          doc_id = "%s/indice" % user
          if doc_id in wiki.database.WIKI:
              del wiki.database.WIKI[doc_id]
    
          # remove o usuário
          if user in core.database.REGISTRY:
              del core.database.REGISTRY[user]
              
          # remove invite
          if user in invites.model.INVITES:
              del invites.model.INVITES[user]
              
          # remove user da lista de usuarios convidados de mauricio
          invite_data = invites.model.INVITES["mauricio"]
          if user in invite_data["usuarios_convidados"]:
             invite_data["usuarios_convidados"].remove(user)
             invites.model.INVITES["mauricio"] = invite_data
             
          self.f.write('deleted: %s %s\n' % (str(datetime.now()), user))        

    # remove as páginas do usuário
#    user = 'usuario0000'
#    for i in range(self.NUM_CREATED_PAGES):
#          nomepagina = 'pagina%04d'%i
#          doc_id = "%s/%s" % (user,nomepagina)
#          if doc_id in wiki.model.WIKI:
#              del wiki.model.WIKI[doc_id]
#              wikimember_data = _EMPTYWIKIMEMBERORCOMMUNITY()
#              wikimember_data.update(wiki.model.WIKIMEMBER[user])
#              wikimember_data["paginas"].remove(doc_id)
#              wiki.model.WIKIMEMBER[user] = wikimember_data


  def test_create_multiple_users(self):
    "Cadastro de muitos usuários"


    
    for i in range(self.NUM_CREATED_USERS):
        registry['user'] = 'dev_usu_teste%04d'%i
        registry['email'] = 'dev_usu_teste%04d@nce.ufrj.br'%i

        invite_data = MAGKEYS_DEFAULT()  # recria chave mágica para que possa fazer outro cadastro
        mkey = invite_data["_id"]
        if mkey not in invites.model.MAGKEYS:
            invite_data['email'] = 'dev_usu_teste%04d@nce.ufrj.br'%i
            invites.model.MAGKEYS[mkey] = invite_data
        
        response = self.app.post('/new/user', registry)
        assert registry['user'] in core.database.REGISTRY, u"Erro: Não conseguiu cadastrar usuário"
        assert u'<div class="tnmMSG">Cadastro criado com sucesso.</div>' in response, u"Erro: Não exibiu mensagem após cadastrar usuário com sucesso!"
        #print "usuario criado="+registry['user']
        self.f.write('create: %s %s\n' % (str(datetime.now()), registry['user']))
          
    "Login de muitos usuários"
    for i in range(self.NUM_CREATED_USERS):
        login.update(LOGIN_FORM)
        login["user"] =   'dev_usu_teste%04d'%i 
        response = self.app.post('/login', login).follow().follow()
        assert u'<a href="/user/%s">%s</a>' % (login['user'],login['user']) in response, u"Erro: Não exibiu mensagem após fazer login do usuário!"
        #print "usuario logado="+login["user"]
        self.f.write('login: %s %s\n' % (str(datetime.now()), login['user']))

    "Requisita pagina home de todos os usuários"
    for i in range(self.NUM_CREATED_USERS):
        usuario = 'dev_usu_teste%04d'%i         
        response = self.app.get('/wiki/%s/home' % usuario)
        assert u'<!-- identificação da userpage utilizado para os testes. -->' in response, u"Erro: Não exibiu a página do usuário %s!" % usuario
        assert "(%s)</h1>" % usuario in response, u"Erro: Não exibiu a página do usuário %s!" % usuario
        self.f.write('home: %s %s\n' % (str(datetime.now()), usuario))
        

    "Requisita form de edição da pagina home da comunidade"
    for i in range(self.NUM_CREATED_USERS):
        usuario = 'dev_usu_teste%04d'%i         
        response = self.app.get('/wiki/edit/dev_comu_teste/home')
        assert u'<h2>Conteúdo:</h2>' in response, u"Erro: Não exibiu a página de edição do home da comunidade!"
        self.f.write('edit home: %s %s\n' % (str(datetime.now()), usuario))
        
    "Salva pagina editada da comunidade"
    #edit_data = 
    for i in range(self.NUM_CREATED_USERS):
        usuario = 'dev_usu_teste%04d'%i         
        response = self.app.post('/wiki/edit/dev_comu_teste/home', edit_data)
        assert u'<h2>Conteúdo:</h2>' in response, u"Erro: Não exibiu a página de edição do home da comunidade!"
        self.f.write('edit home: %s %s\n' % (str(datetime.now()), usuario))       
                       
  """
  def test_request_multiple_registry_forms(self):
    "Acessos ao formulário de cadastro (não vai ao BD)"
    for i in range(self.NUM_REQUESTED_FORMS):
          response = self.app.get('/new/user')
          assert 'input name="user" id="user" value="" type="text"' in response, "Erro: Não exibiu formulário de cadastro!"
            
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
  """
  