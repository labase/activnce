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
import core.model
import log.model
import wiki.model

#import mocker
#from mocker import Mocker

import unittest

#class TestUpload(mocker.MockerTestCase):
class TestUpload(unittest.TestCase):
  """Testes unitários para o cadastro"""
  def setUp(self):
    #self.mock = Mocker()
    #MEMBER = self.mock.mock()

    core.model.REGISTRY = {}
    core.model.MAGKEYS = MAGKEYS_DEFAULT()    # recria chave mágica para que possa fazer outro cadastro    
    core.model.INVITES = {}
    core.model.MAGKEYTYPES = {}
    core.model.USERSCHOOL = {}
    log.model.NOTIFICATIONERROR = {}
    log.model.NOTIFICATION = {}
    
    log.model.LOG = {}    
    log.model.NEWS = {}
    wiki.model.WIKI = {}
    wiki.model.WIKIMEMBER = {}
    wiki.model.WIKICOMMUNITY = {}
    
    self.app = TestApp(WsgiApp())
    registry.update(REGISTRY_FORM)
    login.update(LOGIN_FORM)
    self.app.post('/new/user', registry)
    self.app.post('/login', login)

  def tearDown(self):
    #self.mock.restore()
    #self.mock.verify()
    #self.mock,MEMBER =None,None
    pass

  def test_returns_upload_form(self):
    "Return the Upload Form"
    response = self.app.get('/upload/teste')
    assert u'<form name="upload" action="/upload/teste" method="post" enctype="multipart/form-data">' in response, "Erro: Não exibiu formulário para upload de arquivos!"

  def test_returns_empty_list_of_files(self):
    "Return the user's list of files"
    response = self.app.get('/file/teste')
    assert 'Novo arquivo:' in response, "Erro: Não exibiu a lista de arquivos do usuário teste!"
    #assert u'Arquivos não encontrados' in response, "Erro: Não exibiu a lista de arquivos do usuário teste!"

  '''
  TODO: Simular uma lista de arquivos.
  def test_returns_list_of_files(self):
    "Return the user's list of files"
    response = self.app.get('/file/teste')
    assert u'<p>Arquivos de teste:</p>' in response, "Erro: Não exibiu a lista de arquivos do usuário teste!"
  '''   

  def test_upload_file(self):
    ''' TODO: simular upload de arquivo! Incrementar dicionário com o método de upload de attachment do CouchDB... '''
    "Upload File"
    response = self.app.post('/upload/teste', {'arquivo': ''})
    #response.mustcontain("Meus Arquivos:", "NOME_DO_ARQUIVO")

  def test_delete_file(self):
    ''' TODO: simular remoção de arquivo! Apagar documento com o id passado... '''
    "Delete File"
    response = self.app.get('/file/delete/teste/arq')
#    response.mustcontain("Meus Arquivos:", "NOME_DO_ARQUIVO")
