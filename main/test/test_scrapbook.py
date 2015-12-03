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
import core.model
import log.model
import scrapbook.model
import wiki.model
import unittest

SCRAP = { "teste": {
             "user_to": "teste",
             "recados": [ { "recado": "teste", "data": "10/10/2010", "user_from": "amigo1" }
                        ]
             }
}

SEND_SCRAP_FORM = { "friend":"amigo1",
                    "scrap": "Primeira Mensagem" }

send_scrap = {}

LOGIN_FORM_AMIGO = { "user":"amigo1", "passwd": "teste" }

#class TestAmigo(mocker.MockerTestCase):
class TestScrap(unittest.TestCase):
  """Testes unitários para o gerenciamento de comunidades"""
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
    scrapbook.model.SCRAPBOOK = {}
    
    self.app = TestApp(WsgiApp())
    registry.update(REGISTRY_FORM)
    self.app.post('/new/user', registry)
    registry['user'] = 'amigo1'
    core.model.MAGKEYS = MAGKEYS_DEFAULT()    # recria chave mágica para que possa fazer outro cadastro  
    self.app.post('/new/user', registry)

    login.update(LOGIN_FORM)
    self.app.post('/login', login)
    send_scrap.update(SEND_SCRAP_FORM)

  def tearDown(self):
    #self.mock.restore()
    #self.mock.verify()
    #self.mock,MEMBER =None,None
    pass

  # -------------------------------------------------------------
  # Send new scrap
  
  def test_returns_send_scrap_form(self):
    "Retorna formulário para envio de recados"
    response = self.app.get('/new/scrap')
    assert u'Digite aqui o seu recado' in response, "Erro: Não exibiu formulário para envio de recados!"

  def test_accept_send_scrap_ok(self):
    "Return message after sending scrap"
    response = self.app.post('/new/scrap', send_scrap).follow()
    assert u'Primeira Mensagem' in response, "Erro: Não exibiu o recado!"
    assert "amigo1" in scrapbook.model.SCRAPBOOK, "Erro: Não incluiu o recado no banco."

  def test_reject_send_scrap_user_not_found(self):
    "Return message if user doesnt exist"
    send_scrap["friend"] = "amigo2"
    response = self.app.post('/new/scrap', send_scrap)
    assert u'Usuário Inexistente!' in response, "Erro: Não exibiu mensagem de Usuário Inexistente"
    assert "amigo2" not in scrapbook.model.SCRAPBOOK, "Erro: Incluiu um usuário inexistente no banco de recados."
  
  def test_reject_send_scrap_without_message(self):
    "Return message if there is no message"
    send_scrap["scrap"] = ""
    response = self.app.post('/new/scrap', send_scrap)
    assert u'Você não escreveu o seu recado.' in response, "Erro: Não exibiu mensagem de recado não preenchido!"
    assert "amigo1" not in scrapbook.model.SCRAPBOOK, "Erro: Incluiu recado sem mensagem no banco."

  # -------------------------------------------------------------
  # List Scrapbook
  
  def test_empty_list_of_scrap(self):
    "Return empty list of scraps"
    response = self.app.get('/scrap/teste')
    assert '<h1>fulano de tal (teste)</h1>' in response, "Erro: Não exibiu mensagem 'teste ainda não possui nenhum recado.'"
        
  def test_list_of_scrap(self):
    "Return list of scraps"

    self.app.post('/new/scrap', send_scrap)
    response = self.app.get('/scrap/amigo1')
    assert u'Primeira Mensagem' in response, "Erro: Não exibiu recado do usuario."
     
  # -------------------------------------------------------------
  # Delete Scrap
  def test_delete_nonexisting_user_scrap(self):
    "Return message if trying to delete a scrap from a nonexisting user"
    scrapbook.model.SCRAPBOOK.update(SCRAP)
    response = self.app.get('/delete/scrap?id=')
    print response
    assert u'Usuário inexistente.' in response, "Erro: Não exibiu mensagem 'Usuário inexistente.'"

  def test_delete_other_user_scrap(self):
    "Return message if trying to delete other user scraps"
    scrapbook.model.SCRAPBOOK.update(SCRAP)
    response = self.app.get('/delete/scrap?id=amigo1&&item=0')
    assert u'Você não tem permissão para apagar um recado de outro usuário.' in response, "Erro: Não exibiu mensagem 'Você não tem permissão para apagar um recado de outro usuário.'"
    
  def test_delete_empty_scrap(self):
    "Return 'scrap não encontrado' message scraps"
    scrapbook.model.SCRAPBOOK.update(SCRAP)
    response = self.app.get('/delete/scrap?id=teste')
    assert u'Scrap não encontrado.' in response, "Erro: Não exibiu mensagem 'Scrap não encontrado.'"

  def test_delete_nonexisting_scrap(self):
    "Return 'scrap não encontrado' message scraps"
    scrapbook.model.SCRAPBOOK.update(SCRAP)
    response = self.app.get('/delete/scrap?id=teste&&item=1')
    assert u'Scrap não encontrado.' in response, "Erro: Não exibiu mensagem 'Scrap não encontrado.'"

  def test_deleting_scrap(self):
    "Return list of empty scraps"
    scrapbook.model.SCRAPBOOK.update(SCRAP)
    response = self.app.get('/delete/scrap?id=teste&&item=0')
    assert scrapbook.model.SCRAPBOOK["teste"]["recados"] == [] , "Erro: Não apgou scrap."

