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
import unittest
import log.model

LOGIN_FORM_AMIGO = { "user":"amigo1", "passwd": "teste" }

#class TestAmigo(mocker.MockerTestCase):
class TestAmigo(unittest.TestCase):
  """Testes unitários para o gerenciamento de amigos"""
  def setUp(self):
    #self.mock = Mocker()
    #MEMBER = self.mock.mock()
    
    core.model.REGISTRY = {}
    wiki.model.WIKI = {}
    wiki.model.WIKIMEMBER = {}
    wiki.model.WIKICOMMUNITY = {}    
    wiki.model.FILES = {}
    core.model.MAGKEYS = MAGKEYS_DEFAULT()    # recria chave mágica para que possa fazer outro cadastro  
    core.model.INVITES = {}
    core.model.MAGKEYTYPES = {}
    core.model.USERSCHOOL = {}
    log.model.NOTIFICATIONERROR = {}
    log.model.NOTIFICATION = {}
    
    log.model.LOG = {}
    log.model.NEWS = {}
    
    self.app = TestApp(WsgiApp())
    registry.update(REGISTRY_FORM)
    self.app.post('/new/user', registry)
    registry['user'] = 'amigo1'
    core.model.MAGKEYS = MAGKEYS_DEFAULT()    # recria chave mágica para que possa fazer outro cadastro  
    self.app.post('/new/user', registry)
    registry['user'] = 'amigo2'
    core.model.MAGKEYS = MAGKEYS_DEFAULT()    # recria chave mágica para que possa fazer outro cadastro  
    self.app.post('/new/user', registry)
    registry['user'] = 'amigo3'
    #self.app.post('/new/user', registry)
    core.model.MAGKEYS = MAGKEYS_DEFAULT()    # recria chave mágica para que possa fazer outro cadastro  
    login.update(LOGIN_FORM)
    self.app.post('/login', login)

  def tearDown(self):
    #self.mock.restore()
    #self.mock.verify()
    #self.mock,MEMBER =None,None
    pass

  def test_returns_friend_form(self):
    "Retorna formulário para cadastrar amigo"
    response = self.app.get('/searchfriends')
    assert u'Digite aqui o login, e-mail ou nome do usuário a ser convidado' in response, response #"Erro: Não exibiu formulário para convidar amigo!"

  def test_search_friends_fail(self):
    "Testa falha no envio de convite: Caracteres insuficientes"
    response = self.app.post('/searchfriends', {'friend': 'a'})
    assert u'Digite pelo menos 3 caracteres para procurar amigos.' in response, "Erro: Não exibiu mensagem de caracteres insuficientes!"

  '''
  #não estão passando pois utilizam queries em views do couchdb
  
  def test_search_friend_not_found(self):
    "Testa falha no envio de convite: Usuário inexistente"
    response = self.app.post('/searchfriends', {'friend': 'inexistente'})
    assert u'Nenhum usuário encontrado.' in response, "Erro: Não exibiu mensagem de usuário inexistente!"
  
  def test_search_friends(self):
    "Testa busca de usuários"
    response = self.app.post('/searchfriends', {'friend': 'amigo1'})
    assert u'<a href="/newfriend?friend=amigo1">convidar</a>' in response,"Erro: Não exibiu mensagem de caracteres insuficientes!"
  '''
  
  def test_invite_friend_fail(self):
    "Testa falha no envio de convite: Usuário inexistente"
    response = self.app.get('/newfriend?friend=amigo')
    assert u'Usuário Inexistente.' in response, "Erro: Não exibiu mensagem de usuário inexistente!"
    assert 'amigo' not in core.model.REGISTRY['teste']['amigos_convidados'], "Erro: Adicionou usuário inexistente!"
    response = self.app.get('/newfriend?friend=')
    assert u'Usuário Inexistente.' in response, "Erro: Não exibiu mensagem de usuário inexistente!"

  def test_invite_self_friend_fail(self):
    "Testa falha no envio de convite: não pode convidar seu próprio usuário para amigo"
    response = self.app.get('/newfriend?friend=teste')
    assert u'Você não pode convidar a si mesmo como amigo.' in response, "Erro: Não exibiu mensagem 'Você não pode convidar seu próprio usuário como amigo!'"
    assert 'teste' not in core.model.REGISTRY['teste']['amigos_convidados'], "Erro: Adicionou prório usuário como amigo!"

  def test_invite_duplicate_friend_fail(self):
    "Testa falha no envio de convite: não pode convidar amigo já convidado anteriormente"
    self.app.get('/newfriend?friend=amigo2')
    response = self.app.get('/newfriend?friend=amigo2')
    assert u'Você já convidou amigo2 anteriormente. Aguardando resposta.' in response, "Erro: Não exibiu mensagem 'Amigo já convidado! Aguardando resposta...'"
    assert 'amigo2' in core.model.REGISTRY['teste']['amigos_convidados'], "Erro: Não adicionou usuário na lista de amigos convidados!"
    assert 'teste' in core.model.REGISTRY['amigo2']['amigos_pendentes'], "Erro: Não adicionou usuário que convidou na lista de amigos pendentes!"

  def test_invite_pendent_friend_fail(self):
    "Testa falha no envio de convite: não pode convidar amigo que está na sua lista de amigos pendentes"
    self.app.get('/newfriend?friend=amigo1')
    login.update(LOGIN_FORM_AMIGO)
    self.app.post('/login', login)
    response = self.app.get('/newfriend?friend=teste')
    assert u'teste já te convidou anteriormente. Aguardando sua resposta.' in response, "Erro: Não exibiu mensagem 'Amigo está na sua lista de aprovação aguardando sua resposta!'"
    assert 'amigo1' in core.model.REGISTRY['teste']['amigos_convidados'], "Erro: Não adicionou usuário na lista de amigos convidados!"
    assert 'teste' in core.model.REGISTRY['amigo1']['amigos_pendentes'], "Erro: Não adicionou usuário que convidou na lista de amigos pendentes!"

  def test_invite_friend_success(self):
    "Testa sucesso no envio de convite"
    response = self.app.get('/newfriend?friend=amigo1')
    assert u'Convite para amigo1 enviado com sucesso.' in response, "Erro: Não exibiu mensagem de envio de convite!"
    assert 'amigo1' in core.model.REGISTRY['teste']['amigos_convidados'], "Erro: Não adicionou usuário na lista de amigos convidados!"
    assert 'teste' in core.model.REGISTRY['amigo1']['amigos_pendentes'], "Erro: Não adicionou usuário que convidou na lista de amigos pendentes!"

  def test_accept_friend_success(self):
    "Testa sucesso na aceitação do convite para amigo"
    self.app.get('/newfriend?friend=amigo1')
    login.update(LOGIN_FORM_AMIGO)
    self.app.post('/login', login)
    response = self.app.get('/acceptfriend/teste').follow()
    assert u'Solicitações de amizade' in response, "Erro: Não exibiu mensagem de aceitação de convite!"
    assert 'amigo1' in core.model.REGISTRY['teste']['amigos'], "Erro: Não adicionou usuário na lista de amigos de quem foi convidado!"
    assert 'teste' in core.model.REGISTRY['amigo1']['amigos'], "Erro: Não adicionou usuário na lista de amigos de quem convidou!"
    assert 'amigo1' not in core.model.REGISTRY['teste']['amigos_convidados'], "Erro: Não removeu usuário da lista de amigos pendentes!"
    assert 'teste' not in core.model.REGISTRY['amigo1']['amigos_pendentes'], "Erro: O usuário não foi removido da lista de amigos convidados!"

  def test_reject_friend_success(self):
    "Testa sucesso na recusa do convite para amigo"
    core.model.REGISTRY['teste']['amigos_pendentes'] = ['amigo1']
    core.model.REGISTRY['amigo1']['amigos_convidados'] = ['teste'] 
    response = self.app.get('/rejectfriend/amigo1').follow()
    assert 'amigo1' not in response, "Erro: Continua exibindo amigo1 na página de convites!"
    assert 'amigo1' not in core.model.REGISTRY['teste']['amigos_pendentes'], "Erro: Não removeu usuário da lista de amigos pendentes!"
    assert 'amigo1' not in core.model.REGISTRY['teste']['amigos'], "Erro: Adicionou usuário da lista de amigos!"
    assert 'teste' not in core.model.REGISTRY['amigo1']['amigos_convidados'], "Erro: O usuário não foi removido da lista de amigos convidados!"
    assert 'teste' not in core.model.REGISTRY['amigo1']['amigos'], "Erro: Adicionou usuário da lista de amigos!"

  def test_returns_list_of_pendent_friend_success(self):
    "Retorna lista de usuários pendentes no perfil do usuário"
    core.model.REGISTRY['teste']['amigos_pendentes'] = ['amigo1', 'amigo2', 'amigo3'] 
    response = self.app.get('/invites')
    response.mustcontain("amigo1", "amigo2", "amigo3")

  def test_returns_empty_list_of_friends(self):
    "Retorna mensagem se o usuário não tiver amigos"
    response = self.app.get('/friends/teste')
    assert u'teste ainda não possui nenhum amigo.' in response, "Erro: Não exibiu lista de amigos!"

  def test_returns_list_of_friends(self):
    "Retorna lista de amigos do usuário logado"
    core.model.REGISTRY['teste']['amigos'] = ['amigo1', 'amigo2']
    response = self.app.get('/friends/teste')
    response.mustcontain("amigo1", "amigo2")
