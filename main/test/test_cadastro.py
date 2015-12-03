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

import search.model
import core.model
import wiki.model
import log.model
import unittest


WIKI_DEFAULT = lambda: dict({
                "tnm/home" :
                { "user": "tnm", 
                  "nomepag": "home",
                  "conteudo": u"Página inicial do TNM",
                  "tags": [],
                  "data_cri": "2009-12-15 17:09:17.559390" }
})

WIKICOMMUNITY_DEFAULT = lambda: dict ({
                    "tnm": {
                       "paginas": [ {"owner": "teste",
                                     "doc_id": "tnm/home"}
                                ]
                    }
                 })



PROFILE_EDIT = {
                "name" : "novo nome",
                "lastname" : "novo sobrenome",
                "email" : "novoemail@email.com",
                "tags" : "novas tags",
                "description" : "nova descricao",
                "notify" : "0"
}

CHANGE_PASSWD_FORM = dict(
          oldpasswd = "teste",
          newpasswd = "novoteste",
          confpasswd = "novoteste"
)

MAGKEYS_FORM = dict(
          userid = "teste",
          numkeys = 1,
          tipo = "docente",
          instituicao = "NAVE"
)

INVITE_FORM = dict(
          email = "teste@email.com",
          tipo = "aluno",
          escola = u'3107'
)

INVITE_TEMPLATE = {
          u'al9999a54cxwpAbU0lZdEyYQn0XaIT': {
                'magic': u'al9999a54cxwpAbU0lZdEyYQn0XaIT',
                'email': u'teste@email.com',
                'user': 'teste'
                }
}
mkeys = {}
changepasswd = {}
profile_edit = {}
invite = {}

#class TestCadastro(mocker.MockerTestCase):
class TestCadastro(unittest.TestCase):
  """Testes unitários para o cadastro"""
  def setUp(self):
    #self.mock = Mocker()
    #REGISTRY = self.mock.mock()
    
    core.model.REGISTRY = {}
    core.model.MAGKEYS = MAGKEYS_DEFAULT()
    core.model.INVITES = {}
    core.model.MAGKEYTYPES = {}
    core.model.USERSCHOOL = {}
    search.model.SEARCHTAGS = {}
    wiki.model.WIKI = WIKI_DEFAULT()
    wiki.model.WIKIMEMBER = {}
    wiki.model.WIKICOMMUNITY = WIKICOMMUNITY_DEFAULT()
    wiki.model.FILES = {}
    log.model.LOG = {}
    log.model.NEWS = {}
    log.model.NOTIFICATIONERROR = {}
    log.model.NOTIFICATION = {}
    
    self.app = TestApp(WsgiApp())
    registry.update(REGISTRY_FORM)
    login.update(LOGIN_FORM)
    mkeys.update(MAGKEYS_FORM)
    changepasswd.update(CHANGE_PASSWD_FORM)
    profile_edit.update(PROFILE_EDIT)
    invite.update(INVITE_FORM)

  def tearDown(self):
    #self.mock.restore()
    #self.mock.verify()
    #self.mock,REGISTRY =None,None
    pass

  # -------------------------------------------------------------
  # Home Page

  def test_returns_home_on_root(self):
    "Return the home page on '/'"
    response = self.app.get('/')
    assert u'<td><input type="image" src="/static/imagens/activ/ok.png" border="0" class="form_enviar"/></td>' in response, "Erro: Não exibiu tela de Home!"

  # -------------------------------------------------------------
  # Convites
  def test_type_user_invites_super_usuario(self):
    "Return a form containing the types of user invites(super usuário)"
    self.app.post('/new/user', registry)
    self.app.post('/login', login)
    core.model.MAGKEYTYPES.update(core.model._MAGKEYTYPES)
    core.model.REGISTRY["teste"]["cod_institute"] = '3107'
    core.model.REGISTRY["teste"]["papeis"] = [ "tnm" , "super_usuario"]
    response = self.app.get('/invites')
    assert '<option value="super_usuario">' in response, "Erro: Mostrou convite para super_usuario"
    assert '<option value="funcionario">' in response, "Erro: Mostrou convite para funcionário"
    assert '<option value="docente">' in response, "Erro: Mostrou convite para docente"
    assert '<option value="aluno">' in response, "Erro: Não mostrou convite para aluno"
    assert '<option value="estagiario">' in response, "Erro: Não mostrou convite para estagiário"    
    assert '<option value="usuario_externo">' in response, "Erro: Não mostrou convite para usuario_externo"

  def test_type_user_invites_gestor(self):
    "Return a form containing the types of user invites(gestor)"
    self.app.post('/new/user', registry)
    self.app.post('/login', login)
    core.model.MAGKEYTYPES.update(core.model._MAGKEYTYPES)
    core.model.REGISTRY["teste"]["cod_institute"] = '3107'
    core.model.REGISTRY["teste"]["papeis"] = [ "tnm" , "funcionario"]
    response = self.app.get('/invites')
    assert '<option value="super_usuario">' not in response, "Erro: Mostrou convite para super_usuarios"
    assert '<option value="funcionario">' not in response, "Erro: Mostrou convite para funcionário"
    assert '<option value="professor">' not in response, "Erro: Mostrou convite para professor"
    assert '<option value="aluno">' not in response, "Erro: Não mostrou convite para aluno"
    assert '<option value="estagiario">' not in response, "Erro: Não mostrou convite para estagiário"    
    assert '<option value="usuario_convidado">' not in response, "Erro: Não mostrou convite para convidado"

  def test_type_invites_professor(self):
    "Return a form containing the types of user invites(professor)"
    self.app.post('/new/user', registry)
    self.app.post('/login', login)
    core.model.MAGKEYTYPES.update(core.model._MAGKEYTYPES)
    core.model.REGISTRY["teste"]["cod_institute"] = '3107'
    core.model.REGISTRY["teste"]["papeis"] = [ "tnm" , "professor"]
    response = self.app.get('/invites')
    assert '<option value="super_usuario">' not in response, "Erro: Mostrou convite para super_usuarios"
    assert '<option value="funcionario">' not in response, "Erro: Mostrou convite para funcionário"
    assert '<option value="professor">' not in response, "Erro: Mostrou convite para professor"
    assert '<option value="aluno">' not in response, "Erro: Não mostrou convite para aluno"
    assert '<option value="estagiario">' not in response, "Erro: Não mostrou convite para estagiário"    
    assert '<option value="usuario_convidado">' not in response, "Erro: Não mostrou convite para convidado"

  def test_type_invites_aluno(self):
    "Return a form containing the types of user invites(aluno)"
    self.app.post('/new/user', registry)
    self.app.post('/login', login)
    core.model.MAGKEYTYPES.update(core.model._MAGKEYTYPES)
    core.model.REGISTRY["teste"]["cod_institute"] = '3107'
    core.model.REGISTRY["teste"]["papeis"] = [ "tnm" , "aluno"]
    response = self.app.get('/invites')
    assert '<option value="super_usuario">' not in response, "Erro: Mostrou convite para super_usuarios"
    assert '<option value="funcionario">' not in response, "Erro: Mostrou convite para funcionário"
    assert '<option value="professor">' not in response, "Erro: Mostrou convite para professor"
    assert '<option value="aluno">' not in response, "Erro: Não mostrou convite para aluno"
    assert '<option value="estagiario">' not in response, "Erro: Não mostrou convite para estagiário"    
    assert '<option value="usuario_convidado">' not in response, "Erro: Não mostrou convite para convidado"

  def test_type_user_invites_estagiario(self):
    "Return a form containing the types of user invites(usuário convidado)"
    self.app.post('/new/user', registry)
    self.app.post('/login', login)
    core.model.MAGKEYTYPES.update(core.model._MAGKEYTYPES)
    core.model.REGISTRY["teste"]["cod_institute"] = '3107'
    core.model.REGISTRY["teste"]["papeis"] = [ "tnm" , "estagiario"]
    response = self.app.get('/invites')
    assert '<option value="super_usuario">' not in response, "Erro: Mostrou convite para super_usuarios"
    assert '<option value="funcionario">' not in response, "Erro: Mostrou convite para funcionário"
    assert '<option value="professor">' not in response, "Erro: Mostrou convite para professor"
    assert '<option value="aluno">' not in response, "Erro: Não mostrou convite para aluno"
    assert '<option value="estagiario">' not in response, "Erro: Não mostrou convite para estagiário"    
    assert '<option value="usuario_convidado">' not in response, "Erro: Não mostrou convite para convidado"

  def test_type_user_invites_convidado(self):
    "Return a form containing the types of user invites(usuário convidado)"
    self.app.post('/new/user', registry)
    self.app.post('/login', login)
    core.model.MAGKEYTYPES.update(core.model._MAGKEYTYPES)
    core.model.REGISTRY["teste"]["cod_institute"] = '3107'
    core.model.REGISTRY["teste"]["papeis"] = [ "tnm" , "convidado"]
    response = self.app.get('/invites')
    assert '<option value="super_usuario">' not in response, "Erro: Mostrou convite para super_usuarios"
    assert '<option value="funcionario">' not in response, "Erro: Mostrou convite para funcionário"
    assert '<option value="professor">' not in response, "Erro: Mostrou convite para professor"
    assert '<option value="aluno">' not in response, "Erro: Não mostrou convite para aluno"
    assert '<option value="estagiario">' not in response, "Erro: Não mostrou convite para estagiário"    
    assert '<option value="usuario_convidado">' not in response, "Erro: Não mostrou convite para convidado"
  """
  def test_inviting_user_without_email(self):
    "Return a message with the error: 'E-mail inválido' (sem email)"
    self.app.post('/new/user', registry)
    self.app.post('/login', login)
    core.model.MAGKEYTYPES.update(core.model._MAGKEYTYPES)
    core.model.REGISTRY["teste"]["cod_institute"] = '3107'
    core.model.REGISTRY["teste"]["papeis"] = [ "tnm" , "super_usuario"]
    invite["email"] = ""
    response = self.app.post('/invites', invite)
    assert "E-mail inválido" in response, "Erro: Não mostrou mensagem de email inválido"
  """
  
  def test_inviting_user_with_invalid_email(self):
    "Return a message with the error: 'E-mail inválido' (email inválido)"
    self.app.post('/new/user', registry)
    self.app.post('/login', login)
    core.model.MAGKEYTYPES.update(core.model._MAGKEYTYPES)
    core.model.REGISTRY["teste"]["cod_institute"] = '3107'
    core.model.REGISTRY["teste"]["papeis"] = [ "tnm" , "super_usuario"]
    invite["email"] = "dsjfhsdk"
    response = self.app.post('/invites', invite)
    assert "E-mail inválido" in response, "Erro: Não mostrou mensagem de email inválido"
    invite["email"] = "dsjfhsdk@asda"
    response = self.app.post('/invites', invite)
    assert "E-mail inválido" in response, "Erro: Não mostrou mensagem de email inválido"

  def test_inviting_user_without_tipo(self):
    "Return a message with the error: 'Papel não foi selecionado'"
    self.app.post('/new/user', registry)
    self.app.post('/login', login)
    core.model.MAGKEYTYPES.update(core.model._MAGKEYTYPES)
    core.model.REGISTRY["teste"]["cod_institute"] = '3107'
    core.model.REGISTRY["teste"]["papeis"] = [ "tnm" , "super_usuario"]
    invite["tipo"] = ""
    response = self.app.post('/invites', invite)
    assert "Papel não foi selecionado" in response, "Erro: Não mostrou mensagem de papel não selecionado"

  def test_inviting_user_without_escola(self):
    "Return a message with the error: 'Escola não foi selecionada'"
    self.app.post('/new/user', registry)
    self.app.post('/login', login)
    core.model.MAGKEYTYPES.update(core.model._MAGKEYTYPES)
    core.model.REGISTRY["teste"]["cod_institute"] = '3107'
    core.model.REGISTRY["teste"]["papeis"] = [ "tnm", "admin", "super_usuario"]
    invite["escola"] = ""
    response = self.app.post('/invites', invite)
    assert "Escola não foi selecionada" in response, "Erro: Não mostrou mensagem 'Escola não foi selecionada'"

  def test_inviting_user_super_usuario(self):
    "Return the invites page, with the new invite listed(super usuário)"
    self.app.post('/new/user', registry)
    self.app.post('/login', login)
    core.model.MAGKEYTYPES.update(core.model._MAGKEYTYPES)
    core.model.REGISTRY["teste"]["cod_institute"] = '3107'
    core.model.REGISTRY["teste"]["papeis"] = [ "tnm" , "super_usuario"]
    invite["tipo"] = "super_usuario"
    response = self.app.post('/invites', invite)
    assert "teste@email.com (super_usuario)" in response, "Erro: Não criou o convite com sucesso(super usuário)"

  def test_inviting_user_funcionario(self):
    "Return the invites page, with the new invite listed(funcionario)"
    self.app.post('/new/user', registry)
    self.app.post('/login', login)
    core.model.MAGKEYTYPES.update(core.model._MAGKEYTYPES)
    core.model.REGISTRY["teste"]["cod_institute"] = '3107'
    core.model.REGISTRY["teste"]["papeis"] = [ "tnm" , "super_usuario"]
    invite["tipo"] = "funcionario"
    response = self.app.post('/invites', invite)
    assert "teste@email.com (funcionario)" in response, "Erro: Não criou o convite com sucesso(funcionário)"

  def test_inviting_user_professor(self):
    "Return the invites page, with the new invite listed(professor)"
    self.app.post('/new/user', registry)
    self.app.post('/login', login)
    core.model.MAGKEYTYPES.update(core.model._MAGKEYTYPES)
    core.model.REGISTRY["teste"]["cod_institute"] = '3107'
    core.model.REGISTRY["teste"]["papeis"] = [ "tnm" , "super_usuario"]
    invite["tipo"] = "docente"
    response = self.app.post('/invites', invite)
    assert "teste@email.com (docente)" in response, "Erro: Não criou o convite com sucesso(docente)"

  def test_inviting_user_aluno(self):
    "Return the invites page, with the new invite listed(aluno)"
    self.app.post('/new/user', registry)
    self.app.post('/login', login)
    core.model.MAGKEYTYPES.update(core.model._MAGKEYTYPES)
    core.model.REGISTRY["teste"]["cod_institute"] = '3107'
    core.model.REGISTRY["teste"]["papeis"] = [ "tnm" , "super_usuario"]
    invite["tipo"] = "aluno"
    response = self.app.post('/invites', invite)
    assert "teste@email.com (aluno)" in response, "Erro: Não criou o convite com sucesso(aluno)"
  
  def test_inviting_user_usuario_convidado(self):
    "Return the invites page, with the new invite listed(usuario convidado)"
    self.app.post('/new/user', registry)
    self.app.post('/login', login)
    core.model.MAGKEYTYPES.update(core.model._MAGKEYTYPES)
    core.model.REGISTRY["teste"]["cod_institute"] = '3107'
    core.model.REGISTRY["teste"]["papeis"] = [ "tnm" , "super_usuario"]
    invite["tipo"] = "usuario_externo"
    response = self.app.post('/invites', invite)
    assert "teste@email.com (usuario_externo)" in response, response #"Erro: Não criou o convite com sucesso(usuário externo)"
    
  def test_inviting_user_estagiario(self):
    "Return the invites page, with the new invite listed(estagiário)"
    self.app.post('/new/user', registry)
    self.app.post('/login', login)
    core.model.MAGKEYTYPES.update(core.model._MAGKEYTYPES)
    core.model.REGISTRY["teste"]["cod_institute"] = '3107'
    core.model.REGISTRY["teste"]["papeis"] = [ "tnm" , "super_usuario"]
    invite["tipo"] = "estagiario"
    response = self.app.post('/invites', invite)
    assert "teste@email.com (estagiario)" in response, "Erro: Não criou o convite com sucesso(estagiário)"    

  def test_invite_user_aluno_resend_screen(self):
    "Return the screen with the magic key"
    self.app.post('/new/user', registry)
    self.app.post('/login', login)
    core.model.MAGKEYTYPES.update(core.model._MAGKEYTYPES)
    core.model.REGISTRY["teste"]["papeis"] = [ "tnm" , "super_usuario"]
    core.model.MAGKEYS.update(INVITE_TEMPLATE)
    core.model.REGISTRY['teste']['mykeys'].append("al9999a54cxwpAbU0lZdEyYQn0XaIT")
    response = self.app.get('/invites/send?key=al9999a54cxwpAbU0lZdEyYQn0XaIT')
    assert "Chave mágica: al9999a54cxwpAbU0lZdEyYQn0XaIT" in response, "Erro: Não mostrou mensagem com a chave mágica."

#  def test_invite_user_aluno_resend_screen(self):
#    "Return the message 'Convite enviado com sucesso'"
#    self.app.post('/new/user', registry)
#    self.app.post('/login', login)
#    core.model.MAGKEYTYPES.update(core.model._MAGKEYTYPES)
#    core.model.REGISTRY["teste"]["papeis"] = [ "tnm" , "super_usuario"]
#    core.model.MAGKEYS.update(INVITE_TEMPLATE)
#    core.model.REGISTRY['teste']['mykeys'].append("al9999a54cxwpAbU0lZdEyYQn0XaIT")
#    response = self.app.post('/invites/send?key=al9999a54cxwpAbU0lZdEyYQn0XaIT')
#    assert "Convite enviado com sucesso" in response, "Erro: Não mostrou a mensagem 'Convite enviado com sucesso'"

  def test_invite_user_aluno_cancel(self):
    "Return the 'convite cancelado' message"
    self.app.post('/new/user', registry)
    self.app.post('/login', login)
    core.model.MAGKEYTYPES.update(core.model._MAGKEYTYPES)
    core.model.REGISTRY["teste"]["papeis"] = [ "tnm" , "super_usuario"]
    core.model.MAGKEYS.update(INVITE_TEMPLATE)
    core.model.REGISTRY['teste']['mykeys'].append("al9999a54cxwpAbU0lZdEyYQn0XaIT")
    response = self.app.get('/invites/delete?key=al9999a54cxwpAbU0lZdEyYQn0XaIT')
    assert "Convite cancelado" in response, "Erro: Não mostrou mensagem de convite cancelado."
    
  def test_invite_user_registry_screen_with_mkey_field(self):
    "Return the registry screen, with the mkey field"
    self.app.post('/new/user', registry)
    self.app.post('/login', login)
    core.model.MAGKEYTYPES.update(core.model._MAGKEYTYPES)
    core.model.REGISTRY["teste"]["papeis"] = [ "tnm" , "super_usuario"]
    core.model.MAGKEYS.update(INVITE_TEMPLATE)
    core.model.REGISTRY['teste']['mykeys'].append("al9999a54cxwpAbU0lZdEyYQn0XaIT")
    registry['mkey'] = 'al9999a54cxwpAbU0lZdEyYQn0XaIT'
    response = self.app.post('/new/user', registry)
    assert "E-mail não corresponde a chave" in response, "Erro: Não mostrou a mensagem 'E-mail não corresponde a chave'"

  def test_invite_user_registry_screen_without_mkey_field(self):
    "Return the registry screen, without the mkey field"
    self.app.post('/new/user', registry)
    self.app.post('/login', login)
    core.model.MAGKEYTYPES.update(core.model._MAGKEYTYPES)
    core.model.REGISTRY["teste"]["papeis"] = [ "tnm" , "super_usuario"]
    core.model.MAGKEYS.update(INVITE_TEMPLATE)
    core.model.REGISTRY['teste']['mykeys'].append("al9999a54cxwpAbU0lZdEyYQn0XaIT")
    registry['user'] = 'teste2'
    registry['mkey'] = 'al9999a54cxwpAbU0lZdEyYQn0XaIT'
    response = self.app.get('/new/user?mkey=al9999a54cxwpAbU0lZdEyYQn0XaIT')
    assert "teste@email.com" in response, "Erro: Não exibiu o email do usuário a ser cadastrado"
    assert 'input name="mkey" value="al9999a54cxwpAbU0lZdEyYQn0XaIT" type="hidden"' in response, "Erro: O campo mkey foi exibido para o usuário"

  def test_invite_user_registry_through_screen_with_mkey_field(self):
    "Try to registry the invited user through the screen with the mkey field"
    self.app.post('/new/user', registry)
    self.app.post('/login', login)
    core.model.MAGKEYTYPES.update(core.model._MAGKEYTYPES)
    core.model.REGISTRY["teste"]["papeis"] = [ "tnm" , "super_usuario"]
    core.model.MAGKEYS.update(INVITE_TEMPLATE)
    core.model.REGISTRY['teste']['mykeys'].append("al9999a54cxwpAbU0lZdEyYQn0XaIT")
    registry['user'] = 'teste2'
    registry['email'] = "teste@email.com"
    registry['mkey'] = 'al9999a54cxwpAbU0lZdEyYQn0XaIT'
    response = self.app.post('/new/user', registry)
    assert "teste2" in core.model.REGISTRY, "Erro: Não registrou usuário!"
    assert "aluno" in core.model.REGISTRY['teste2']['papeis'], "Erro: Não gravou o papel do usuário corretamente!"

  def test_invite_user_registry_through_screen_without_mkey_field(self):
    "Try to registry the invited user through the screen without the mkey field"
    self.app.post('/new/user', registry)
    self.app.post('/login', login)
    core.model.MAGKEYTYPES.update(core.model._MAGKEYTYPES)
    core.model.REGISTRY["teste"]["papeis"] = [ "tnm" , "super_usuario"]
    core.model.MAGKEYS.update(INVITE_TEMPLATE)
    core.model.REGISTRY['teste']['mykeys'].append("al9999a54cxwpAbU0lZdEyYQn0XaIT")
    registry['user'] = 'teste2'
    registry['email'] = 'teste@email.com'
    del registry['mkey']
    response = self.app.post('/new/user?mkey=al9999a54cxwpAbU0lZdEyYQn0XaIT', registry)
    assert "teste2" in core.model.REGISTRY, "Erro: Não registrou usuário!"
    assert "aluno" in core.model.REGISTRY['teste2']['papeis'], "Erro: Não gravou o papel do usuário corretamente!"


  # -------------------------------------------------------------
  # Cadastro de Usuários
  
  def test_returns_complete_registry_form(self):
    "Return a form containing registry data"
    response = self.app.get('/new/user')
    assert 'input name="user" id="user" value="" type="text"' in response, "Erro: Não exibiu formulário de cadastro!"

  def test_returns_registry_form_without_mkey(self):
    "Return a form containing registry data"
    response = self.app.get('/new/user?mkey=al9999CHAVEINEXISTENTEYQn0XaIT')
    assert 'Convite inexistente ou expirado.' in response, "Erro: Não exibiu mensagem de convite inexistente ou expirado!"

  def test_returns_registry_form_without_mkey(self):
    "Return a form containing registry data"
    response = self.app.get('/new/user?mkey=ue99996yt276Yt197AgR5667dGkLO3')
    assert '<input name="mkey" value="ue99996yt276Yt197AgR5667dGkLO3" type="hidden"/>' in response, response #"Erro: Não repassou a chave como hidden!"

  """
  Falta fazer os seguintes testes:
  1) Se houver uma lista comunidades na mkey, verificar se o usuario esta sendo incluido nas comunidades da lista
  2) Se houver atributo name na mkey verificar se está sendo colocado nos campos nome e sobrenome do form de cadastro
  """

  def test_accept_registry_ok(self):
    """ TODO: simular upload de foto! Incrementar dicionário com o método de upload de attachment do CouchDB... """
    "Return home page after registry ok"
    response = self.app.post('/new/user',registry)
    assert 'teste' in core.model.REGISTRY, "Erro: Não conseguiu cadastrar usuário"
    assert core.model.REGISTRY["teste"]["name"] == 'fulano', "Erro: Não armazenou nome no banco"
    assert core.model.REGISTRY["teste"]["lastname"] == 'de tal', "Erro: Não armazenou sobrenome no banco"
    assert core.model.REGISTRY["teste"]["email"] == 'teste@teste.com', "Erro: Não armazenou email no banco"
    assert 'tnm' in core.model.REGISTRY["teste"]["papeis"], "Erro: Não armazenou papel do usuario no banco"
    assert core.model.REGISTRY["teste"]["institute"] == u'Não informada', "Erro: Não armazenou instituto do usuario no banco"
    assert u'Cadastro criado com sucesso.' in response, "Erro: Não exibiu mensagem após cadastrar usuário com sucesso!"

  def test_if_copy_params_from_mkeys_to_registry(self):
    "Verifica se os outros atributos de mkey estão sendo copiados pro registry"
    core.model.MAGKEYS["ue99996yt276Yt197AgR5667dGkLO3"]["x"] = "123"
    core.model.MAGKEYS["ue99996yt276Yt197AgR5667dGkLO3"]["y"] = "456"
    response = self.app.post('/new/user',registry)
    assert 'teste' in core.model.REGISTRY, "Erro: Não conseguiu cadastrar usuário"
    assert core.model.REGISTRY["teste"]["x"] == '123', "Erro: Não armazenou nome no banco"
    assert core.model.REGISTRY["teste"]["y"] == '456', "Erro: Não armazenou sobrenome no banco"
    assert u'Cadastro criado com sucesso.' in response, "Erro: Não exibiu mensagem após cadastrar usuário com sucesso!"

  def test_reject_registry_double_user(self):
    "Return error message: Login já existe!"
    self.app.post('/new/user', registry)
    core.model.MAGKEYS = MAGKEYS_DEFAULT()    # recria chave mágica para que possa fazer outro cadastro
    response = self.app.post('/new/user', registry)
    assert u'Login já existe.' in response, "Erro: Não exibiu a mensagem 'Login já existe.'"

  def test_reject_registry_without_magickey(self):
    "Return error message: Chave mágica incorreta!"
    registry["mkey"]="teste"
    response = self.app.post('/new/user', registry)
    assert u'Chave mágica incorreta ou expirada.' in response, "Erro: Não exibiu a mensagem 'Chave mágica incorreta ou expirada.'"

  #def test_reject_registry_with_community_magickey(self):
  #  "Return error message: Chave mágica incorreta!"
  #  registry["mkey"]="co99993j69sBGFq91o0rjMqL62S07K"
  #  response = self.app.post('/new/user', registry)
  #  assert u'Esta chave mágica só serve para criar comunidades!' in response, "Erro: Não exibiu a mensagem 'Esta chave mágica só serve para criar comunidades!'"
        
  def test_reject_registry_with_reserved_word(self):
    "Return error message: Login inválido."
    registry["user"]="new"
    response = self.app.post('/new/user', registry)
    assert u'Login inválido.' in response, "Erro: Não exibiu a mensagem 'Login inválido.'"

  def test_reject_registry_without_pass_confirm(self):
    "Return error message: Senha diferente da confirmação!"
    registry["npasswd"]="npasswd"
    response = self.app.post('/new/user', registry)
    assert u'Senha diferente da confirmação!' in response, "Erro: Não exibiu a mensagem 'Senha diferente da confirmação.'"

  def test_reject_registry_without_required_field(self):
    "Return error message: campos obrigatórios não preenchidos!"
    registry["name"]=""
    registry["lastname"]=""
    response = self.app.post('/new/user', registry)
    assert u'campos obrigatórios não preenchidos!' in response, "Erro: Não exibiu a mensagem 'campos obrigatórios não preenchidos.'"

  def test_reject_registry_with_invalid_login(self):
    "Return error message:  Login inválido. Utilize apenas letras, números, '_' e '.'!"
    registry["user"]="teste&01"
    response = self.app.post('/new/user', registry)
    assert u"Login inválido. Utilize apenas letras, números, '_' e '.'!" in response, "Erro: Não exibiu a mensagem 'Login inválido.'"


  # -------------------------------------------------------------
  # Login
  
  def test_open_a_login_screen(self):
    "Return a form containing login, senha"
    response = self.app.get('/login')
    assert 'input prompt="login" name="user" value="login" autocomplete="off"' in response, "Erro: Não exibiu tela de login!"

  def test_login_unsuccessful(self):
    "If login is unsuccessful, return the form containing login, senha with error message"
    response = self.app.post('/login', login)
    assert u'Senha incorreta ou usuário inexistente.' in response, "Erro: Não exibiu tela de Login com mensagem de erro!"

  def test_login_successful(self):
    "If login is successful, return the home page on '/user'"
    self.app.post('/new/user', registry)
    response = self.app.post('/login', login).follow()
    assert u'<!-- ***** Identificação do painel de controle de usuários. Utilizado para os testes. ***** -->' in response, "Erro: Não exibiu a página do usuário após realizar login com sucesso!"
    assert '<a href="/user/teste">%s</a>' % login['user'] in response, "Erro: Não exibiu a página do usuário após realizar login com sucesso!"

  
  # -------------------------------------------------------------
  # User Page
  
  def test_user_home(self):
    "Return the home page on '/user'"
    self.app.post('/new/user', registry)
    self.app.post('/login', login)
    response = self.app.get('/user/' + login["user"])
    assert u'<!-- ***** Identificação do painel de controle de usuários. Utilizado para os testes. ***** -->' in response, "Erro: Não exibiu a página do usuário!"
  
  # -------------------------------------------------------------
  # Meu Perfil

  def test_open_profile_screen(self):
    "Return the user profile screen"
    self.app.post('/new/user', registry)
    self.app.post('/login', login)
    response = self.app.get('/profile/' + login["user"])
    assert "<!-- ***** Identificação do painel de controle de usuários. Utilizado para os testes. ***** -->" in response, "Erro, não exibiu o perfil"

  def test_edit_profile_screen(self):
    "Return the user edit profile screen"
    self.app.post('/new/user', registry)
    self.app.post('/login', login)
    response = self.app.get('/profile/edit')
    assert "<!-- ***** Identificação da edição do painel de controle de usuários. Utilizado para os testes. ***** -->" in response, "Erro, não exibiu a tela de edição de perfil"

  def test_edit_profile(self):
    "Return the user edited profile"
    self.app.post('/new/user', registry)
    self.app.post('/login', login)
    self.app.post('/profile/edit', profile_edit)
    assert core.model.REGISTRY["teste"]["name"] == "novo nome", "Erro, não alterou o nome do usuário"
    assert core.model.REGISTRY["teste"]["lastname"] == "novo sobrenome", "Erro, não alterou o sobrenome do usuário"
    assert core.model.REGISTRY["teste"]["email"] == "novoemail@email.com", "Erro, não alterou o email do usuário"
    assert core.model.REGISTRY["teste"]["tags"] == [ "novas", "tags" ], "Erro, não alterou as tags do usuário"
    assert core.model.REGISTRY["teste"]["description"] == "nova descricao", "="+core.model.REGISTRY["teste"]["description"]+"=" #"Erro, não alterou a descrição do usuário"
    assert "teste" in search.model.SEARCHTAGS["novas"]["perfil"], "Erro, não incluiu a tag na tabela de tags"
    assert "teste" in search.model.SEARCHTAGS["tags"]["perfil"], "Erro, não incluiu a tag na tabela de tags"

  def test_edit_profile_remove_tag(self):
    "Return the user edited profile, that has removed a tag"
    self.app.post('/new/user', registry)
    self.app.post('/login', login)
    self.app.post('/profile/edit', profile_edit)
    profile_edit["tags"] = ""
    self.app.post('/profile/edit', profile_edit)    
    assert "teste" not in search.model.SEARCHTAGS["novas"]["perfil"], "Erro, não removeu a tag da tabela de tags"
    assert "teste" not in search.model.SEARCHTAGS["tags"]["perfil"], "Erro, não removeu a tag da tabela de tags"
  
  # -------------------------------------------------------------
  # Alteração de senha
 
  def test_open_changepasswd_screen(self):
    "Return the change passwd screen"
    self.app.post('/new/user', registry)
    self.app.post('/login', login)
    response = self.app.get('/profile/changepasswd')
    assert 'Senha antiga' in response, "Erro: Não exibiu tela de alteração de senha!"

  def test_accept_changepasswd_ok(self):
    "Return home page after professor registry ok"
    self.app.post('/new/user', registry)
    self.app.post('/login', login)    
    response = self.app.post('/profile/changepasswd', changepasswd)
    assert u'Senha alterada com sucesso!' in response, "Erro: Não exibiu a página do usuário após realizar cadastro de professor!"
  
  def test_reject_no_passwd_required_fields(self):
    "Return error message: Há campos não preenchidos!"
    self.app.post('/new/user', registry)
    self.app.post('/login', login)
    changepasswd["oldpasswd"] = ""
    response = self.app.post('/profile/changepasswd', changepasswd)
    assert u'Há campos não preenchidos!' in response, "Erro: Não exibiu a mensagem 'Há campos não preenchidos!'"

     
  def test_reject_incorrect_passwd_confirmation(self):
    "Return error message: Senha diferente da confirmação!"
    self.app.post('/new/user', registry)
    self.app.post('/login', login)
    changepasswd["confpasswd"] = "xyzw"
    response = self.app.post('/profile/changepasswd', changepasswd)
    assert u'Senha diferente da confirmação!' in response, "Erro: Não exibiu a mensagem 'Senha diferente da confirmação!'"
    
  def test_reject_incorrect_size_passwd(self):
    "Return error message: Senha deve ter no mínimo 4 caracteres."
    self.app.post('/new/user', registry)
    self.app.post('/login', login)
    changepasswd["newpasswd"] = "123"
    changepasswd["confpasswd"] = "123"
    response = self.app.post('/profile/changepasswd', changepasswd)
    assert u'Senha deve ter no mínimo 4 caracteres.' in response, "Erro: Não exibiu a mensagem 'Senha deve ter no mínimo 4 caracteres.'"

  def test_reject_incorrect_oldpasswd(self):
    "Return error message: Senha antiga incorreta!"
    self.app.post('/new/user', registry)
    self.app.post('/login', login)
    changepasswd["oldpasswd"] = "1234"
    response = self.app.post('/profile/changepasswd', changepasswd)
    assert u'Senha antiga incorreta!' in response, "Erro: Não exibiu a mensagem 'Senha antiga incorreta!'"
      
       
  # -------------------------------------------------------------
  # Esqueci minha senha
 
  def test_open_forgotpasswd_screen(self):
    "Return the forgot passwd screen"
    self.app.post('/new/user', registry)
    response = self.app.get('/forgotpasswd')
    assert 'Digite aqui o seu login. Uma nova senha será gerada e enviada para o seu e-mail.' in response, "Erro: Não exibiu tela de 'esqueci minha senha'!"

  def test_accept_forgotpasswd_ok(self):
    "Return password change confirmation screen"
    self.app.post('/new/user', registry)
    response = self.app.post('/forgotpasswd', { "user":"teste"})
    assert u'Sua senha foi alterada com sucesso.' in response, "Erro: Não alterou senha do usuário!"
    assert u'Foi enviado um e-mail com sua nova senha confirmando esta operação.' in response, "Erro: Não enviou e-mail!"
  
  def test_reject_no_login_field(self):
    "Return error message empty login "
    self.app.post('/new/user', registry)
    response = self.app.post('/forgotpasswd', { "user":""})
    assert u'Especifique o seu login!' in response, "Erro: Não acusou erro de login vazio!"
    
  def test_reject_incorrect_login_field(self):
    "Return error message incorrect login"
    self.app.post('/new/user', registry)
    response = self.app.post('/forgotpasswd', { "user":"xyzw"})
    assert u'Usuário não encontrado!' in response, "Erro: Não acusou erro de login inexistente!"

  # -------------------------------------------------------------
  # logout
 
  def test_logout(self):
    "Return the homepage"
    self.app.post('/new/user', registry)
    self.app.post('/login', login)
    response = self.app.get('/logout').follow()
    assert u'<td><input type="image" src="/static/imagens/activ/ok.png" border="0" class="form_enviar"/></td>' in response, "Erro: Não exibiu tela de Home!"
