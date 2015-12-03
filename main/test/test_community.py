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
import wiki.model
import log.model
import unittest

CREATE_COMMUNITY_FORM = { "name": "comunidade1",
                          "description": "Primeira Comunidade",
                          "participacao": "Mediante Convite",
                          "privacidade": "Pública" }
create_community = {}

LOGIN_FORM_AMIGO = { "user":"amigo1", "passwd": "teste" }

REGISTRY_DEFAULT = lambda: dict ({
   "comunidadepub": {
      "participantes_pendentes": [],
      "description": "comunidade um",
      "participantes": [
          "teste",
          "userpub"
      ],
      "photo": "",
      "owner": "teste",
      "privacidade": u"Pública",
      "participacao": u"Mediante Convite",
      "name": "comunidadepub",
      "admins": ["userpub"]
   },
   "comunidadepriv": {
      "participantes_pendentes": [],
      "description": "comunidade dois",
      "participantes": [
          "userpub"
      ],
      "photo": "",
      "privacidade": u"Privada",
      "participacao": u"Mediante Convite",
      "owner": "userpub",
      "name": "comunidadepriv",
      "admins": []
     
   }
})

COMMUNITY_INVITE = dict(
    login = "userpub",
    numero = "3"
)

invite = {}


#class TestAmigo(mocker.MockerTestCase):
class TestComunidade(unittest.TestCase):
  """Testes unitários para o gerenciamento de comunidades"""
  def setUp(self):
    #self.mock = Mocker()
    #MEMBER = self.mock.mock()
    
    core.model.REGISTRY = REGISTRY_DEFAULT()
    wiki.model.WIKI = {}
    wiki.model.WIKIMEMBER = {}
    wiki.model.WIKICOMMUNITY = {}      
    wiki.model.FILES = {}
    core.model.MAGKEYS = MAGKEYS_DEFAULT()
    core.model.INVITES = {}
    core.model.USERSCHOOL = {}    
    log.model.NOTIFICATIONERROR = {}
    log.model.NOTIFICATION = {}
    
    #core.model.MAGKEYTYPES = {}
    #core.model.MAGKEYINSTITUTES = {}
    core.model.USERSCHOOL = {}
    log.model.LOG = {}
    log.model.NEWS = {}
    
    invite.update(COMMUNITY_INVITE)
    
    self.app = TestApp(WsgiApp())
    registry.update(REGISTRY_FORM)

    # Cria usuários para os testes
    #registry['user'] = 'teste'
    self.app.post('/new/user', registry)
    core.model.REGISTRY['teste']['cod_institute'] = u"0002"
     
    registry['user'] = 'userpub'
    core.model.MAGKEYS = MAGKEYS_DEFAULT()    # recria chave mágica para que possa fazer outro cadastro  
    self.app.post('/new/user', registry)
    core.model.REGISTRY['userpub']['cod_institute'] = u'0002'
    
    registry['user'] = 'userpriv'
    core.model.MAGKEYS = MAGKEYS_DEFAULT()    # recria chave mágica para que possa fazer outro cadastro  
    self.app.post('/new/user', registry)
    core.model.REGISTRY['userpriv']['privacidade'] = "Privada"
    
    registry['user'] = 'amigo1'
    core.model.MAGKEYS = MAGKEYS_DEFAULT()    # recria chave mágica para que possa fazer outro cadastro  
    self.app.post('/new/user', registry)
    
    registry['user'] = 'amigo2'
    core.model.MAGKEYS = MAGKEYS_DEFAULT()    # recria chave mágica para que possa fazer outro cadastro    
    self.app.post('/new/user', registry)
    
    registry['user'] = 'amigo3'
    core.model.MAGKEYS = MAGKEYS_DEFAULT()    # recria chave mágica para que possa fazer outro cadastro    
    self.app.post('/new/user', registry)
    
    # Faz login como usuário teste
    login.update(LOGIN_FORM)
    self.app.post('/login', login)
    core.model.REGISTRY['teste']['papeis'].append('docente')
    create_community.update(CREATE_COMMUNITY_FORM)
    core.model.MAGKEYS = MAGKEYS_DEFAULT()    # recria chave mágica para que possa fazer outro cadastro
    
    
  def tearDown(self):
    #self.mock.restore()
    #self.mock.verify()
    #self.mock,MEMBER =None,None
    pass


  # -------------------------------------------------------------
  # Invites to create communities
  def test_user_invites_home(self):
    "Acesso a tela de convites"
    core.model.REGISTRY["teste"]["papeis"] = ["tnm" , "super_usuario"]
    response = self.app.get('/invites')
    assert u'Autorizar a criação de comunidade' in response, "Erro: Não exibiu opção de envio de convites para criar comunidades!"  
  
  def test_user_invite_without_number(self):
    "Retorna mensagem de erro 'Autorização não concedida: número de comunidades não especificado.'"
    core.model.REGISTRY["teste"]["papeis"] = ["tnm" , "super_usuario"]
    invite['numero'] = ""
    response = self.app.post('/invites/authcommunity', invite)
    assert u'Autorizar a criação de comunidade' in response, "Erro: Não exibiu mensagem de erro 'Autorização não concedida: número de comunidades não especificado.'"  

  def test_user_invite_non_existing_member(self):
    "Retorna mensagem de erro 'Autorização não concedida: usuário não encontrado.'"
    core.model.REGISTRY["teste"]["papeis"] = ["tnm" , "super_usuario"]
    invite['login'] = ""
    response = self.app.post('/invites/authcommunity', invite)
    assert u'Autorização não concedida: usuário não encontrado.' in response, "Erro: Não exibiu mensagem de erro 'Autorização não concedida: usuário não encontrado.'"  
    invite['login'] = "usuarionaoexistente"
    response = self.app.post('/invites/authcommunity', invite)
    assert u'Autorização não concedida: usuário não encontrado.' in response, "Erro: Não exibiu mensagem de erro 'Autorização não concedida: usuário não encontrado.'"  

  def test_user_invite_member_from_another_school(self):
    "Retorna mensagem de erro 'Autorização não concedida: você não pode autorizar pessoas de outra escola a criar comunidades.'"
    core.model.REGISTRY["teste"]["papeis"] = [ "tnm" , "super_usuario"]
    core.model.REGISTRY['userpub']['cod_institute'] = u'0123'
    response = self.app.post('/invites/authcommunity', invite)
    assert u'Autorização não concedida: você não pode autorizar pessoas de outra escola a criar comunidades.' in response, "Erro: Não exibiu mensagem de erro 'Autorização não concedida: você não pode autorizar pessoas de outra escola a criar comunidades.'"  

  def test_user_invite_member_that_can_already_create_communities(self):
    "Retorna mensagem de erro 'Autorização não concedida: userpub já tem permissão para criar comunidades."
    core.model.REGISTRY["teste"]["papeis"] = [ "tnm" , "super_usuario"]
    core.model.REGISTRY["userpub"]["papeis"] = [ "docente" ]
    response = self.app.post('/invites/authcommunity', invite)
    assert u'Autorização não concedida: userpub já tem permissão para criar comunidades.' in response, response #"Erro: Não exibiu mensagem de erro 'Autorização não concedida: userpub já tem permissão para criar comunidades.'"  

  
  def test_user_invite_member_create_communities(self):
    "Retorna mensagem de erro 'Autorização não concedida: userpub já tem permissão para criar comunidades."
    core.model.REGISTRY["teste"]["papeis"] = [ "tnm" , "super_usuario"]
    core.model.REGISTRY["userpub"]["papeis"] = [ "aluno" ]
    core.model.REGISTRY["userpub"]["mykeys"] = []
    response = self.app.post('/invites/authcommunity', invite)
    assert u'A autorização para criar comunidades foi concedida.' in response, "Erro: Não concedeu autorização para criar comunidades."
    assert len(core.model.REGISTRY["userpub"]["mykeys"]) == 3, "Erro: Não criou as 3 chaves de comunidade para o usuário"
    login['user'] = 'userpub'
    self.app.post('/login', login)
    response = self.app.get('/scrap/userpub')
    assert u"Você foi autorizado a criar 3 comunidade(s)" in response, "Erro: Não exibiu recado ao usuário que foi autorizado a criar as comunidades"
  
  # -------------------------------------------------------------
  # Acess to public and private users and communities
  
  def test_userpub_access_userpub(self):
    "Um usuário público consegue visualizar o perfil de outro usuário público"
    response = self.app.get('/profile/userpub')
    assert u'<!-- ***** Identificação do painel de controle de usuários. Utilizado para os testes. ***** -->' in response, "Erro: Não painel de controle do usuário!"
  
  def test_userpub_access_userpriv(self):
    "Um usuário público não consegue visualizar o perfil de um usuário privado"
    response = self.app.get('/profile/userpriv')
    assert u'Este conteúdo só pode ser acessado pelos amigos de userpriv.' in response, "Erro: Não painel de controle do usuário!"
  
  def test_friend_access_userpriv(self):
    "Amigo consegue visualizar o perfil do usuário"
    core.model.REGISTRY['userpriv']['amigos'].append ('teste')
    core.model.REGISTRY['teste']['amigos'].append ('userpriv')
    response = self.app.get('/profile/userpriv')
    assert u'<!-- ***** Identificação do painel de controle de usuários. Utilizado para os testes. ***** -->' in response, "Erro: Não painel de controle do usuário!"

  def test_user_access_communitypub(self):
    "Um usuário qualquer consegue visualizar o perfil de uma comunidade pública"
    response = self.app.get('/profile/comunidadepub')
    assert u'<!-- ***** Identificação do painel de controle de comunidades. Utilizado para os testes. ***** -->' in response, "Erro: Não painel de controle da comunidade!"
  
  def test_user_access_communitypriv(self):
    "Um usuário qualquer não consegue visualizar o perfil de uma comunidade privada"
    response = self.app.get('/profile/comunidadepriv')
    assert u'Este conteúdo só pode ser acessado pelos participantes da comunidade comunidadepriv.' in response, "Erro: Não painel de controle da comunidade!"

  def test_user_access_communitypriv(self):
    "Um participante consegue visualizar o perfil de uma comunidade privada"
    login['user'] = 'userpub'
    self.app.post('/login', login)
    response = self.app.get('/profile/comunidadepriv')
    assert u'<!-- ***** Identificação do painel de controle de comunidades. Utilizado para os testes. ***** -->' in response, "Erro: Não painel de controle da comunidade!"

  # -------------------------------------------------------------
  # Ações em cada comunidade dependendo do tipo de participação
  
  def test_owner_access_communitypub(self):
    "O dono consegue convidar usuários para a sua comunidade"
    response = self.app.get('/profile/comunidadepub')
    assert u'<h2><a href="/searchmembers/comunidadepub">Adicionar participantes</a></h2>' in response, "Erro: Não exibiu mensagem de convidar usuários!"
  
  def test_member_access_communitypub(self):
    "Um participante consegue sair de uma comunidade com tipo de participação mediante convite"
    login['user'] = 'userpub'
    self.app.post('/login', login)
    response = self.app.get('/profile/comunidadepub')
    assert u'Sair desta comunidade' in response, "Erro: Não exibiu mensagem de sair da comunidade!"
  
  def test_not_member_access_communitypub(self):
    "Um usuário que não é participante consegue visualizar o perfil de uma comunidade com partipação do tipo mediante convite"
    login['user'] = 'userpriv'
    self.app.post('/login', login)
    response = self.app.get('/profile/comunidadepub')
    assert u'<h2><a href="/agenda/comunidadepub">Agenda</a></h2>' in response, "Erro: Não exibiu o perfil da comunidade!"
    
  def test_owner_access_comunidade_obrigatoria(self):
    "O dono de uma comunidade com tipo de participação obrigatória consegue visualizar o perfil da sua comunidade"
    core.model.REGISTRY['comunidadepub']['participacao'] = u"Obrigatória"
    response = self.app.get('/profile/comunidadepub')
    assert u'<h2><a href="/community/admin/comunidadepub">Administrar participantes</a></h2>' in response, "Erro: Não exibiu link de administrar administradores!"
    assert u'<h2><a href="/community/owners/comunidadepub">Delegar o papel de administrador</a></h2>' in response, "Erro: Não exibiu link de delegar administradores!"
    
  def test_admin_access_comunidade_obrigatoria(self):
    "Um administrador de uma comunidade com tipo de participação obrigatória consegue visualizar o perfil da mesma"
    core.model.REGISTRY['comunidadepub']['participacao'] = u"Obrigatória"
    login['user'] = 'userpub'
    response = self.app.get('/profile/comunidadepub')
    assert u'<h2><a href="/community/owners/comunidadepub">Delegar o papel de administrador</a></h2>' in response, "Erro: Não exibiu mensagem de delegar administradores!"

  def test_member_access_comunidade_voluntaria(self):
    "Um participante de uma comunidade do tipo voluntária consegue sair desta comunidade"
    core.model.REGISTRY['comunidadepub']['participacao'] = u"Voluntária"
    login['user'] = 'userpub'
    self.app.post('/login', login)
    response = self.app.get('/profile/comunidadepub')
    assert u'Sair desta comunidade' in response, "Erro: Não exibiu mensagem de sair da comunidade!"
    
  def test_not_member_access_comunidade_voluntaria(self):
    "Um usuário que não é participante consegue entrar de uma comunidade com partipação do tipo voluntária"
    core.model.REGISTRY['comunidadepub']['participacao'] = u"Voluntária"
    login['user'] = 'userpriv'
    self.app.post('/login', login)
    response = self.app.get('/profile/comunidadepub')
    assert u'Entrar nesta comunidade' in response, "Erro: Não exibiu mensagem de entrar na comunidade!"
  
  def test_member_sair_comunidade_voluntaria(self):
    "Um usuário que é participante consegue sair de uma comunidade com partipação do tipo voluntária"
    core.model.REGISTRY['comunidadepub']['participacao'] = u"Voluntária"
    core.model.REGISTRY['comunidadepub']['participantes'].append('userpriv')
    login['user'] = 'userpriv'
    self.app.post('/login', login)
    response = self.app.get('/profile/comunidadepub')
    assert u'Sair desta comunidade' in response, "Erro: Não exibiu mensagem de sair da comunidade!"  

  # -------------------------------------------------------------
  # Create new community
  
  def test_returns_newcommunity_form_for_a_not_admin_user(self):
    "Retorna formulário para criação de nova comunidade para um usuário que não tem papel de admin."
    response = self.app.get('/new/community')
    assert '<input type="radio" name="participacao" value="Mediante Convite" checked="checked" /> Mediante Convite' in response, "Erro: Não exibiu formulário para criar comunidade!"
    assert '<input type="radio" name="participacao" value="Voluntária" /> Voluntária' in response, "Erro: Não exibiu formulário para criar comunidade!"
  
  def test_returns_newcommunity_form_for_an_admin_user(self):
    "Retorna formulário para criação de nova comunidade para um usuário que tem papel de admin."
    core.model.REGISTRY['teste']['papeis'].append("admin")
    response = self.app.get('/new/community')
    assert '<input type="radio" name="participacao" value="Mediante Convite" checked="checked" /> Mediante Convite' in response, "Erro: Não exibiu formulário para criar comunidade!"
    assert '<input type="radio" name="participacao" value="Voluntária" /> Voluntária' in response, "Erro: Não exibiu formulário para criar comunidade!"
    assert '<input type="radio" name="participacao" value="Obrigatória" /> Obrigatória' in response, "Erro: Não exibiu formulário para criar comunidade!"

  def test_rejects_newcommunity_if_not_admin(self):
    "Exibe mensagem de erro quando um usuário que não tem papel de admin deseja criar uma comunidade com tipo de participação obrigatória."
    create_community['participacao'] = 'Obrigatória'
    response = self.app.post('/new/community', create_community)
    assert 'Você não tem permissão para criar comunidades obrigatórias.' in response, "Erro: Não exibiu mensagem de erro!"  
  
  def test_accept_newcommunity_ok(self):
    """ TODO: simular upload de foto! Incrementar dicionário com o método de upload de attachment do CouchDB... """
    "Return list of communities after registry ok"
    response = self.app.post('/new/community', create_community).follow()
    assert u'<a href="/community/comunidade1" title="Primeira Comunidade" style="color:black">' in response, "Erro: Não exibiu tela com a comunidade criada!"
    assert "comunidade1" in core.model.REGISTRY, "Erro: Não incluiu a nova comunidade no banco."
    assert "teste" in core.model.REGISTRY["comunidade1"]["participantes"], "Erro: Não incluiu o usuário na lista de participantes da comunidade."
    assert 'comunidade' in core.model.REGISTRY["comunidade1"]["papeis"], "Erro: Não armazenou papel do usuario no banco"
    assert core.model.REGISTRY["comunidade1"]["institute"] == u'Não informada', "Erro: Não armazenou instituto do usuario no banco"

  def test_reject_newcommunity_double_community_name(self):
    "Return error message: Já existe uma comunidade com este mesmo nome!"
    self.app.post('/new/community', create_community)
    core.model.MAGKEYS = MAGKEYS_DEFAULT()    # recria chave mágica para que possa fazer outro cadastro
    response = self.app.post('/new/community', create_community)
    assert u'Já existe um usuário ou comunidade com este nome.' in response, "Erro: Não exibiu a mensagem 'Já existe um cadastro com este mesmo nome!'"
  
  def test_reject_newcommunity_with_invalid_name(self):
    "Return error message:  Nome inválido. Utilize apenas letras, números, '_' e '.'!"
    create_community["name"]="teste&01"
    response = self.app.post('/new/community', create_community)
    assert u"Nome inválido. Utilize apenas letras sem acentos, números, '_' e '.'." in response, "Erro: Não exibiu a mensagem 'Nome inválido!'"

  def test_create_newcommunity_professor(self):
    "Sucesso na criação de comunidade por um professor!"
    self.app.post('/new/community', create_community).follow()
    assert 'comunidade1' in core.model.REGISTRY, "Não criou a comunidade no banco."

  def test_create_newcommunity_aluno(self):
    "Sucesso na criação de comunidade por um aluno!"
    login['user'] = 'amigo1'
    self.app.post('/login', login)
    core.model.REGISTRY['amigo1']['papeis'].append('aluno')
    core.model.REGISTRY['amigo1']['mykeys'].append('co99993j69sBGFq91o0rjMqL62S07K')
    self.app.post('/new/community', create_community).follow()
    assert 'comunidade1' in core.model.REGISTRY, "Não criou a comunidade no banco."

  def test_reject_newcommunity_without_required_field(self):
    "Return error message: campos obrigatórios não preenchidos!"
    create_community["name"] = ""
    response = self.app.post('/new/community', create_community)
    assert u'campos obrigatórios não preenchidos.' in response, "Erro: Não exibiu a mensagem 'campos obrigatórios não preenchidos!'"
  
  # -------------------------------------------------------------
  # List of Communities
  
  def test_empty_list_of__communities(self):
    "Return empty list of communities"
    response = self.app.get('/communities/teste')
    assert u'teste não participa de nenhuma comunidade.' in response, "Erro: Não exibiu mensagem 'O usuário não participa de nenhuma comunidade.'"
        
  def test_list_of__communities(self):
    "Return list of communities"
    self.app.post('/new/community', create_community)
    response = self.app.get('/communities/teste')
    assert u'<a href="/community/comunidade1" title="Primeira Comunidade" style="color:black">' in response, "Erro: Não exibiu tela com a comunidade criada!"
     
     
  # -------------------------------------------------------------
  # Community Page
  
  def test_community_home(self):
    "Return the home page on '/community/<nome da comunidade>'"
    self.app.post('/new/community', create_community)
    response = self.app.get('/community/comunidade1').follow()
    assert u'<!-- ***** Identificação do painel de controle de comunidades. Utilizado para os testes. ***** -->' in response, "Erro: Não exibiu a página do usuário!"
  
  # -------------------------------------------------------------
  # Invite to Community
  
  def test_return_invite_user_form(self):
    "Testa sucesso no envio de convite para participar da comunidade"
    self.app.post('/new/community', create_community)    
    response = self.app.get('/searchmembers/comunidade1')
    assert u'Digite aqui o login, e-mail ou nome do usuário a ser convidado' in response, "Erro: Não exibiu formulário de convite!"
  
  def test_search_members_fail(self):
    "Testa falha no envio de convite: Caracteres insuficientes"
    self.app.post('/new/community', create_community)
    response = self.app.post('/searchmembers/comunidade1', {'member': 'a'})
    assert u'Digite pelo menos 3 caracteres para procurar participantes.' in response, "Erro: Não exibiu mensagem de caracteres insuficientes!"

  """
  #esta função utiliza views e por isso o teste não funciona.
  def test_search_member_not_found(self):
    "Testa falha no envio de convite: Usuário inexistente"
    self.app.post('/new/community', create_community)
    response = self.app.post('/searchmembers/comunidade1', {'member': 'inexistente'})
    assert u'Nenhum usuário encontrado.' in response, "Erro: Não exibiu mensagem de usuário inexistente!"
    
  #esta função utiliza views e por isso o teste não funciona.
  def test_search_members(self):
    "Testa busca de usuários"
    self.app.post('/new/community', create_community)
    response = self.app.post('/searchmembers/comunidade1', {'member': 'amigo1'})
    assert u'<a href="/invite/comunidade1?member=amigo1">Convidar</a>' in response, "Erro: Não exibiu mensagem de caracteres insuficientes!"
  """

  def test_search_member_community_not_found(self):
    "Testa falha no envio de convite: Comunidade inexistente"
    response = self.app.get('/searchmembers/inexistente?member=amigo1')
    assert u'Comunidade não encontrada.' in response, "Erro: Não exibiu mensagem de Comunidade não encontrada!"

  def test_invite_friend_success(self):
    "Testa sucesso no envio de convite"
    self.app.post('/new/community', create_community)    
    response = self.app.get('/invite/comunidade1?member=amigo1')
    #assert u'Convite para usuário enviado com sucesso!' in response, "Erro: Não exibiu mensagem de envio de convite!"
    assert 'amigo1' in core.model.REGISTRY['comunidade1']['participantes_pendentes'], "Erro: Não adicionou usuário na lista de participantes pendentes da comunidade!"
    assert 'comunidade1' in core.model.REGISTRY['amigo1']['comunidades_pendentes'], "Erro: Não adicionou comunidade na lista de comuidades pendentes do usuário!"
  
  def test_invite_user_fail(self):
    "Testa falha no envio de convite: usuário inexistente"
    self.app.post('/new/community', create_community)
    response = self.app.get('/invite/comunidade1?member=amigo').follow()
    assert u'Usuário Inexistente!' in response, "Erro: Não exibiu mensagem de usuário inexistente!"
    assert 'amigo' not in core.model.REGISTRY['comunidade1']['participantes_pendentes'], "Erro: Adicionou usuário inexistente!"

  def test_invite_no_user_fail(self):
    "Testa falha no envio de convite: usuário não especificado"
    self.app.post('/new/community', create_community)
    response = self.app.get('/invite/comunidade1?member=').follow()
    assert u'Usuário Inexistente!' in response, "Erro: Não exibiu mensagem de usuário inexistente!"
    
  def test_invite_self_user_fail(self):
    "Testa falha no envio de convite: o dono da comunidade não pode convidar a si mesmo"
    self.app.post('/new/community', create_community)
    response = self.app.get('/invite/comunidade1?member=teste').follow()
    assert u'Usuário já está nesta comunidade!' in response, "Erro: Não exibiu mensagem 'Usuário já está nesta comunidade!'"
    assert 'teste' not in core.model.REGISTRY['comunidade1']['participantes_pendentes'], "Erro: Adicionou prório usuário como amigo!"
  
  def test_invite_duplicate_user_fail(self):
    "Testa falha no envio de convite: não pode convidar amigo já convidado anteriormente"
    self.app.post('/new/community', create_community)    
    self.app.get('/invite/comunidade1?member=amigo2')
    response = self.app.get('/invite/comunidade1?member=amigo2').follow()
    assert u'Usuário já convidado! Aguardando resposta...' in response, "Erro: Não exibiu mensagem 'Usuário já convidado! Aguardando resposta...'"
    assert 'amigo2' in core.model.REGISTRY['comunidade1']['participantes_pendentes'], "Erro: Não adicionou usuário na lista de participantes pendentes da comunidade!"
    assert 'comunidade1' in core.model.REGISTRY['amigo2']['comunidades_pendentes'], "Erro: Não adicionou comunidade na lista de comuidades pendentes do usuário!"
  
  # -------------------------------------------------------------
  # Accept/Reject Community
  
  def test_accept_community_success(self):
    "Testa sucesso na aceitação do convite para participar de comunidade"
    self.app.post('/new/community', create_community)    
    self.app.get('/invite/comunidade1?member=amigo1')
    login.update(LOGIN_FORM_AMIGO)
    self.app.post('/login', login)
    response = self.app.get('/accept/comunidade1')
    assert u'Agora você participa desta comunidade!' in response, "Erro: Não exibiu mensagem de aceitação de convite!"
    assert 'amigo1' in core.model.REGISTRY['comunidade1']['participantes'], "Erro: Não adicionou usuário na lista de participantes!"
    assert 'comunidade1' in core.model.REGISTRY['amigo1']['comunidades'], "Erro: Não adicionou comunidade na lista de comunidades do usuário!"
    assert 'amigo1' not in core.model.REGISTRY['comunidade1']['participantes_pendentes'],"Erro: Não removeu usuário da lista de participantes pendentes!"
    assert 'comunidade1' not in core.model.REGISTRY['amigo1']['comunidades_pendentes'], "Erro: A comunidade não foi removida da lista de comunidades pendentes!"

  def test_reject_community_success(self):
    "Testa sucesso na recusa do convite para comunidade"
    self.app.post('/new/community', create_community)    
    self.app.get('/invite/comunidade1?member=amigo1')
    login.update(LOGIN_FORM_AMIGO)
    self.app.post('/login', login)
    response = self.app.get('/reject/comunidade1')
    assert u'Você recusou participar desta comunidade!' in response, "Erro: Não exibiu mensagem de aceitação de convite!"
    assert 'amigo1' not in core.model.REGISTRY['comunidade1']['participantes'], "Erro: Adicionou usuário na lista de participantes!"
    assert 'comunidade1' not in core.model.REGISTRY['amigo1']['comunidades'], "Erro: Adicionou comunidade na lista de comunidades do usuário!"
    assert 'amigo1' not in core.model.REGISTRY['comunidade1']['participantes_pendentes'],"Erro: Não removeu usuário da lista de participantes pendentes!"
    assert 'comunidade1' not in core.model.REGISTRY['amigo1']['comunidades_pendentes'], "Erro: A comunidade não foi removida da lista de comunidades pendentes!"

  def test_returns_list_of_pendent_communities_success(self):
    "Retorna lista de comunidades pendentes no perfil do usuário"
    core.model.REGISTRY['teste']['comunidades_pendentes'] = ['comunidade1', 'comunidade2', 'comunidade3'] 
    response = self.app.get('/invites')
    response.mustcontain("comunidade1", "comunidade2", "comunidade3")

# -------------------------------------------------------------
  #List Community Files by owner
  
  def test_upload_community_file_form(self):
    ''' TODO: simular upload de foto! Incrementar dicionário com o método de upload de attachment do CouchDB... '''
    "Return list of communities after registry ok"
    self.app.post('/new/community', create_community)
    response = self.app.get('/upload/comunidade1')
    assert u'<form name="upload" action="/upload/comunidade1" method="post" enctype="multipart/form-data">' in response, "Erro: Não exibiu formulário de upload!"
    
  def test_upload_community_file(self):
    ''' TODO: simular upload de arquivo! Incrementar dicionário com o método de upload de attachment do CouchDB... '''
    "Upload File"
    self.app.post('/new/community', create_community)
    self.app.get('/community/comunidade1')
    response = self.app.post('/upload/comunidade1', {'arquivo': ''})
   
   
  # -------------------------------------------------------------
  # Perfil da comunidade

  def test_open_profile_screen(self):
    "Return the community profile screen"
    self.app.post('/new/community', create_community)
    response = self.app.get('/profile/comunidade1')
    response.mustcontain("Nome", u"Descrição")
   
  def test_open_edit_profile_screen(self):
    "Return the community profile screen"
    self.app.post('/new/community', create_community)
    response = self.app.get('/profile/comunidade1/edit')
    assert u'<form name="cadastro" action="/profile/comunidade1/edit" method="post" enctype="multipart/form-data">' in response, "Erro: Não exibiu formulário de edição de perfil de comunidade!"
    
  def test_open_edit_profile_community_not_exists(self):
    "Community not exists"    
    response = self.app.get('/profile/comunidadeX/edit')
    assert u"Comunidade não existe." in response, "Erro: Não exibiu u'Comunidade não existe.'!"

  def test_open_edit_profile_community_fail(self):
    "Current user is not community's owner"
    self.app.post('/new/community', create_community)
    login.update(LOGIN_FORM_AMIGO)
    self.app.post('/login', login)

    response = self.app.get('/profile/comunidade1/edit')    
    assert u"Você não tem permissão para alterar o perfil desta comunidade." in response, "Erro: Não exibiu u'Você não tem permissão para alterar o perfil desta comunidade.'!"
    #response = self.app.get('/profile/comunidade1/edit', status=403)
    #assert '403 Forbidden' in response.status, "Erro: Permitiu alguém que não é dono da comunidade editar."

  def test_edit_profile_ok(self):
    "Return the community profile screen"
    self.app.post('/new/community', create_community)
    self.app.get('/profile/comunidade1/edit')
    create_community["description"] = "nova descricao"
    response = self.app.post('/profile/comunidade1/edit')
    "nova descricao" in core.model.REGISTRY["comunidade1"]["description"], "Erro: Não alterou descricao da comunidade!"
  
  

