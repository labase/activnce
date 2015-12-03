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
import forum.model

CREATE_TOPIC_FORM = {   "titulo": "novo topico",
                        "conteudo": "descricao do novo topico",
                        "receber_email": True
                     }
create_topic = {}

CREATE_POST_FORM = {    "title": "novo post",
                        "message": "descricao do novo post"
                   }
create_post = {}

CREATE_SEARCH_FORM = {    "texto_busca": "novo comunidade" }
create_search = {}

CREATE_CONFIG_FORM = {    "num_topics": "6",
                          "num_posts": "6"
                     }
create_config = {}

REGISTRY_DEFAULT = lambda: dict ({
   "comunidadeteste": {
      "participantes_pendentes": [],
      "description": "comunidade de teste",
      "participantes": [
          "teste",
          "userteste",
          "usercomum",
          "mauricio"
      ],
      "photo": "",
      "owner": "teste",
      "privacidade": u"Pública",
      "participacao": u"Mediante Convite",
      "name": "comunidadepub",
      "admins": ["userteste"]
   }
})

FORUM_DEFAULT = lambda: dict ({
   "comunidadeteste": {
      "topics": [
                  {
                      "dt_creation_post": "2011-02-14 17:42:08.962448",
                      "title": "topico1 da comunidade",
                      "receber_email": "",
                      "posts": [
                          {
                              "owner": "teste",
                              "message": u"kdlsçad,laçsd",
                              "data": "2011-02-14 17:45:27.087998",
                              "title": "comentario 1"
                          },
                          {
                              "owner": "mauricio",
                              "message": u"mdslaçdmlaçsd,a",
                              "data": "2011-02-14 17:45:38.622557",
                              "title": "comentario 2"
                          }
                      ],
                      "dt_last_post": "2011-02-14 17:45:38.622557",
                      "num_posts": 2,
                      "owner": "mauricio",
                      "content": u"dkasmdaçsmd"
                  },
                  {
                      "dt_creation_post": "2011-02-14 17:42:21.158186",
                      "title": "topico2",
                      "receber_email": "",
                      "posts": [
                          {
                              "owner": "mauricio",
                              "message": u"mdsçadmlaçda",
                              "data": "2011-02-14 17:46:07.805259",
                              "title": "comentario1"
                          },
                          {
                              "owner": "mauricio",
                              "message": u"kdslçadkalçdal",
                              "data": "2011-02-14 17:46:18.722616",
                              "title": "comentario2"
                          }
                      ],
                      "dt_last_post": "2011-02-14 17:46:18.722616",
                      "num_posts": 2,
                      "owner": "userteste",
                      "content": u"jksladmlaçsda"
                  },
                  {
                      "dt_creation_post": "2011-02-14 17:42:30.541648",
                      "title": "topico3",
                      "receber_email": "yes",
                      "posts": [
                          {
                              "owner": "mauricio",
                              "message": u"dksamdalçdma",
                              "data": "2011-02-14 17:46:54.245783",
                              "title": "comentario1"
                          },
                          {
                              "owner": "mauricio",
                              "message": u"jdsçamdalçdla",
                              "data": "2011-02-14 17:47:13.292298",
                              "title": "comentario2"
                          }
                      ],
                      "dt_last_post": "2011-02-14 17:47:13.292298",
                      "num_posts": 2,
                      "owner": "mauricio",
                      "content": u"kdlsçad,laçsd,a"
                  },
                  {
                      "dt_creation_post": "2011-02-14 17:48:21.842428",
                      "title": "topico4",
                      "receber_email": "",
                      "posts": [
                      ],
                      "dt_last_post": "",
                      "num_posts": 0,
                      "owner": "mauricio",
                      "content": "fmdlsfmslkfmsd"
                  },
                  {
                      "dt_creation_post": "2011-02-14 17:43:11.719349",
                      "title": "novo topico da comunidade",
                      "receber_email": "",
                      "posts": [
                          {
                              "owner": "mauricio",
                              "message": u"dlsçad,laçsd,las",
                              "data": "2011-02-14 17:49:08.392649",
                              "title": "comentario1"
                          },
                          {
                              "owner": "mauricio",
                              "message": u"dlsçadmalçsdalçsd,",
                              "data": "2011-02-14 17:49:24.409984",
                              "title": "comentario2"
                          }
                      ],
                      "dt_last_post": "2011-02-14 17:49:24.409984",
                      "num_posts": 2,
                      "owner": "usercomum",
                      "content": u"mksmdlaçsd,a"
                  },
                  {
                      "dt_creation_post": "2011-02-14 17:43:28.387222",
                      "title": "novo topico4",
                      "receber_email": "",
                      "posts": [
                          {
                              "owner": "mauricio",
                              "message": u"klçdalçsdlaçsd",
                              "data": "2011-02-14 17:49:51.411355",
                              "title": "comentario1"
                          },
                          {
                              "owner": "mauricio",
                              "message": u"kdlçsamdlças,d",
                              "data": "2011-02-14 17:50:00.551695",
                              "title": "comentario2"
                          },
                          {
                              "owner": "mauricio",
                              "message": u"mdksaçlmdaçdmas",
                              "data": "2011-02-14 17:50:08.946478",
                              "title": "comentario3"
                          },
                          {
                              "owner": "mauricio",
                              "message": u"kdlçsamdlaçsda",
                              "data": "2011-02-14 17:50:17.635317",
                              "title": "comentario4"
                          },
                          {
                              "owner": "mauricio",
                              "message": u"dklasmdalçsmdalçsda",
                              "data": "2011-02-14 17:50:28.994642",
                              "title": "comentario5"
                          },
                          {
                              "owner": "mauricio",
                              "message": "fdlmdflasdmalsdm",
                              "data": "2011-02-14 17:50:44.975139",
                              "title": "comentario6"
                          }
                      ],
                      "dt_last_post": "2011-02-14 17:50:44.975139",
                      "num_posts": 6,
                      "owner": "mauricio",
                      "content": u"dklsçadlaçdsalsd"
                  }
      ]
   }
})

class TestComunidade(unittest.TestCase):
  """Testes unitários para o gerenciamento de comunidades"""
  def setUp(self):
    #self.mock = Mocker()
    #MEMBER = self.mock.mock()
    
    core.model.REGISTRY = REGISTRY_DEFAULT()
    core.model.MAGKEYS = MAGKEYS_DEFAULT()
    core.model.INVITES = {}
    core.model.USERSCHOOL = {}    
    core.model.MAGKEYTYPES = {}
    core.model.MAGKEYINSTITUTES = {}

    wiki.model.WIKI = {}
    wiki.model.WIKIMEMBER = {}
    wiki.model.WIKICOMMUNITY = {}      
    wiki.model.FILES = {}
    forum.model.FORUM = FORUM_DEFAULT()
    log.model.LOG = {}
    log.model.NEWS = {}
    log.model.NOTIFICATIONERROR = {}
    log.model.NOTIFICATION = {}
    
    self.app = TestApp(WsgiApp())
    registry.update(REGISTRY_FORM)

    # Cria usuários para os testes
    #registry['user'] = 'teste'
    self.app.post('/new/user', registry)
    core.model.REGISTRY['teste']['cod_institute'] = u"0002"
     
    registry['user'] = 'userteste'
    core.model.MAGKEYS = MAGKEYS_DEFAULT()    # recria chave mágica para que possa fazer outro cadastro  
    self.app.post('/new/user', registry)
    core.model.REGISTRY['userteste']['cod_institute'] = u'0002'
    
    registry['user'] = 'usercomum'
    core.model.MAGKEYS = MAGKEYS_DEFAULT()    # recria chave mágica para que possa fazer outro cadastro  
    self.app.post('/new/user', registry)
    core.model.REGISTRY['usercomum']['cod_institute'] = u'0002'    
    
    registry['user'] = 'mauricio'
    core.model.MAGKEYS = MAGKEYS_DEFAULT()    # recria chave mágica para que possa fazer outro cadastro  
    self.app.post('/new/user', registry)
    core.model.REGISTRY['usercomum']['cod_institute'] = u'0002'
    
    # Faz login como usuário teste
    login.update(LOGIN_FORM)
    self.app.post('/login', login)
    core.model.REGISTRY['teste']['papeis'].append('professor')

    create_topic.update(CREATE_TOPIC_FORM)
    create_post.update(CREATE_POST_FORM)
    create_search.update(CREATE_SEARCH_FORM)
    create_config.update(CREATE_CONFIG_FORM)
    core.model.MAGKEYS = MAGKEYS_DEFAULT()    # recria chave mágica para que possa fazer outro cadastro
    
    
  def tearDown(self):
    #self.mock.restore()
    #self.mock.verify()
    #self.mock,MEMBER =None,None
    pass


  # -------------------------------------------------------------
  # Acesso ao fórum

  def test_access_forum(self):
    "Acesso a tela do fórum"
    response = self.app.get('/forum/comunidadeteste')
    assert u'<a href="/forum/comunidadeteste">Exibir todos os t&oacute;picos</a><br/>' in response, "Erro: Não exibiu o fórum da comunidade!"
    
  def test_return_to_topics(self):
    "Exibe todos os tópicos após clicar no link: 'Retornar para aos tópicos'."
    self.app.get('/forum/comunidadeteste/post?t_rel=0')
    response = self.app.get('/forum/comunidadeteste?n=0')
    assert u'<a href="/forum/comunidadeteste">Exibir todos os t&oacute;picos</a><br/>' in response, "Erro: Não exibiu o fórum da comunidade!"
  
  # -------------------------------------------------------------
  # Criação de novos tópicos e posts no fórum  

  def test_form_new_topic(self):
    "Exibe formulário de criação de um novo tópico."
    response = self.app.get('/forum/comunidadeteste/newtopic')
    assert '<form name="novotopico" action="/forum/comunidadeteste/newtopic" method="post">' in response, "Erro: Não exibiu a tela de criação de um novo tópico!"
    
  def test_create_new_topic(self):
    "Verfica se um novo tópico foi criado com sucesso."
    response = self.app.post('/forum/comunidadeteste/newtopic', create_topic).follow()
    assert '<td align="left"><a href=/forum/comunidadeteste/post?t_rel=0><u>novo topico</u></a></td>' in response, "Erro: Não foi criado um novo tópico no fórum da comunidade!"
    assert 'novo topico' in forum.model.FORUM['comunidadeteste']['topics'][5]['title'], "Erro: Não adicionou novo topico na lista de topicos do forum da comunidade!"
    
  def test_form_post(self):
    "Exibe formulário de criação de um novo post."
    response = self.app.get('/forum/comunidadeteste/newpost')
    assert '<form name="novotopico" action="/forum/comunidadeteste/newpost" method="post">' in response, "Erro: Não exibiu a tela de criação de um novo post!"

  def test_create_new_post(self):
    "Verfica se um novo post foi criado com sucesso."
    self.app.get('/forum/comunidadeteste/post?t_rel=0')
    response = self.app.post('/forum/comunidadeteste/newpost', create_post).follow()
    assert '<em>novo post</em><br/>' in response, "Erro: Não foi criado um novo post!"
    assert 'novo post' in forum.model.FORUM['comunidadeteste']['topics'][5]['posts'][6]['title'], "Erro: Não adicionou novo topico na lista de topicos do forum da comunidade!"
    

  # -------------------------------------------------------------
  # Busca por tópicos

  def test_search(self):
    "Verifica se uma busca por determinado tópico foi feita com sucesso."
    response = self.app.post('/forum/comunidadeteste', create_search).follow()
    assert '<u><font  style="background-color: #ffff00">novo</font> topico4</u>' in response, "Erro: Não exibiu a tela com o resultado da busca!"

  # -------------------------------------------------------------
  # Configuração

  def test_config(self):
    "Exibe tela de configuração para o usuário."
    response = self.app.get('/forum/comunidadeteste/admin')
    assert '<form name="configurar" action="/forum/comunidadeteste/admin" method="post">' in response, "Erro: Não exibiu a tela com o forumulário de configuração!"
    
  def test_config_topics(self):
    "Exibe tela dos tópicos após serem feitas alterações na quantidade de tópicos a serem mostrados por página."    
    response = self.app.post('/forum/comunidadeteste/admin', create_config).follow()
    assert '&nbsp;&nbsp;&nbsp;1-6 de 6&nbsp;&nbsp;&nbsp;' in response, "Erro: Não executou as alterações de quantidade de tópicos por página feitas pelo usuário!"

  def test_config_posts(self):
    "Exibe tela dos posts após serem feitas alterações na quantidade de posts a serem mostrados por página."    
    self.app.post('/forum/comunidadeteste/admin', create_config).follow()
    response = self.app.get('/forum/comunidadeteste/post?t_rel=0')
    assert '&nbsp;&nbsp;&nbsp;1-6 de 6&nbsp;&nbsp;&nbsp;' in response, "Erro: Não executou as alterações de quantidade de posts por página feitas pelo usuário!"

  # -------------------------------------------------------------
  # Ordenação de tópicos e posts 
  
  def test_invert_topics_order(self):
    "Exibe os tópicos mais antigos."
    self.app.get('/forum/comunidadeteste')
    response = self.app.get('/forum/comunidadeteste?n=0&ordem=1')
    assert '<a href="/forum/comunidadeteste?n=0&ordem=0">Exibir mais recentes primeiro</a><br/>' in response, "Erro: Não exibiu os tópicos mais antigos primeiro!"
    
  def test_invert_posts_order(self):
    "Exibe os posts mais antigos."
    self.app.get('/forum/comunidadeteste')
    response = self.app.get('/forum/comunidadeteste/post?t_rel=0&ordem=1')
    assert '<a href=/forum/comunidadeteste/post?t_rel=0&ordem=0>Exibir mais recentes primeiro</a><br/>' in response, "Erro: Não exibiu os posts mais antigos primeiro!"
    
  # -------------------------------------------------------------
  # Remoção de tópicos e posts
  
  def test_delete_topics_by_community_owner(self):
    "Verifica se um tópico foi removido com sucesso pelo dono da comunidade."
    self.app.get('/forum/comunidadeteste')
    response = self.app.get('/forum/comunidadeteste/deltopic?indice=1').follow()
    assert '<a href=/forum/comunidadeteste/post?t_rel=1><u>topico4</u></a>' in response, "Erro: Dono da comunidade não removeu o tópico selecionado!"

  def test_delete_topics_by_topic_owner(self):
    "Verifica se o dono de um tópico (que não é o dono da comunidade) removeu um tópico com sucesso."
    login["user"] = "usercomum"
    self.app.post('/login', login)
    self.app.get('/forum/comunidadeteste')
    response = self.app.get('/forum/comunidadeteste/deltopic?indice=1').follow()
    assert '<a href=/forum/comunidadeteste/post?t_rel=1><u>topico4</u></a>' in response, "Erro: Dono do tópico não removeu o tópico selecionado!"
    
  def test_reject_delete_topics(self):
    "Verifica se um usuário comum não tem sucesso ao remover um tópico de outro usuário."
    login["user"] = "usercomum"
    self.app.post('/login', login)
    self.app.get('/forum/comunidadeteste')
    response = self.app.get('/forum/comunidadeteste/deltopic?indice=0')
    assert '<div class="tnmMSG">Você não tem permissão para remover este tópico.</div>' in response, "Erro: Usuário comum removeu tópico de outro usuário!"

  def test_delete_posts(self):
    "Verifica se dono da comunidade tem sucesso ao remover um post."
    self.app.get('/forum/comunidadeteste/post?t_rel=0')
    response = self.app.get('/forum/comunidadeteste/delpost?indice=1').follow()
    assert '<em>***** Mensagem removida *****</em><br/>' in response, "Erro: Dono da comunidade não conseguiu remover post!"
    
  def test_reject_delete_posts(self):
    "Verifica se um usuário comum não tem sucesso ao remover um post de outro usuário."
    login["user"] = "usercomum"
    self.app.post('/login', login)
    self.app.get('/forum/comunidadeteste/post?t_rel=0')
    response = self.app.get('/forum/comunidadeteste/delpost?indice=0')
    assert '<div class="tnmMSG">Você não tem permissão para remover este post.</div> ' in response, "Erro: Usuário comum removeu post!"
    
  # -------------------------------------------------------------
  # Edição de tópicos
  
  def test_form_edit_topic_by_community_owner(self):
    "Exibe formulário de edição de um tópico para o dono da comunidade."
    response = self.app.get('/forum/comunidadeteste/newtopic?indice=0')
    assert '<form name="novotopico" action="/forum/comunidadeteste/newtopic" method="post">' in response, "Erro: Não exibiu a tela de criação de um novo tópico!"

  def test_form_edit_topic_by_topics_owner(self):
    "Exibe formulário de edição de um tópico para o dono do mesmo."
    login["user"] = "mauricio"
    self.app.post('/login', login)
    self.app.get('/forum/comunidadeteste')
    response = self.app.get('/forum/comunidadeteste/newtopic?indice=0')
    assert '<form name="novotopico" action="/forum/comunidadeteste/newtopic" method="post">' in response, "Erro: Não exibiu a tela de criação de um novo tópico!"    
  
  def test_reject_edit_topic_by_common_user(self):
    "Um usuário só pode alterar o seu próprio tópico, a não ser que seja o dono da comunidade ou administrador da mesma."
    login["user"] = "usercomum"
    self.app.post('/login', login)
    self.app.get('/forum/comunidadeteste')
    response = self.app.get('/forum/comunidadeteste/newtopic?indice=0')
    assert 'Você não tem permissão para alterar este tópico.' in response, "Erro: Não exibiu a tela de criação de um novo tópico!"      
  
  def test_edit_topic_by_community_owner(self):
    "Verfica se um tópico foi editado com sucesso pelo dono da comunidade."
    self.app.get('/forum/comunidadeteste')
    response = self.app.post('/forum/comunidadeteste/newtopic?indice=0', create_topic).follow()
    assert '<a href=/forum/comunidadeteste/post?t_rel=0><u>novo topico</u></a>' in response, "Erro: Não foi criado um novo tópico no fórum da comunidade!"
    assert 'novo topico' in forum.model.FORUM['comunidadeteste']['topics'][5]['title'], "Erro: Não adicionou novo topico na lista de topicos do forum da comunidade!"

  def test_edit_topic_by_topics_owner(self):
    "Verfica se um tópico foi editado com sucesso pelo dono do mesmo."
    login["user"] = "mauricio"
    self.app.post('/login', login)
    response = self.app.post('/forum/comunidadeteste/newtopic?indice=0', create_topic).follow()
    assert '<a href=/forum/comunidadeteste/post?t_rel=0><u>novo topico</u></a>' in response, "Erro: Não foi criado um novo tópico no fórum da comunidade!"
    assert 'novo topico' in forum.model.FORUM['comunidadeteste']['topics'][5]['title'], "Erro: Não adicionou novo topico na lista de topicos do forum da comunidade!"
