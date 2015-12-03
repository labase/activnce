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

import os.path
import tornado

#import mocker
#from mocker import Mocker

import search.model as model
import core.model
import wiki.model
import blog.model
import log.model
import unittest
import locale

REGISTRY_DEFAULT = {
   "comunidade1": {
      "participantes_pendentes": [],
      "description": "comunidade um",
      "participantes": [
          "teste",
          "teste2"
      ],
      "photo": "",
      "tags": [ "comunidade", "teste" ],
      "owner": "teste",
      "name": "comunidade1",
      "privacidade": u"Pública",
      "participacao": u"Mediante Convite"
   },
   "amigo_teste": {
      "amigos": [],
      "amigos_convidados": [],
      "amigos_pendentes": [],
      "cod_institute": "",
      "comunidades": [],
      "comunidades_pendentes": [],
      "description": "",
      "email": "amigo_teste@email.com",
      "institute": "",
      "lastname": "amigo",
      "mykeys": [],
      "name": "Amigo do Teste",
      "papeis": [ "tnm" ],
      "passwd": "123456",
      "photo": "",
      "privacidade": "Pública",
      "tags": [ "user", "teste" ],
      "upload_quota": 10485760,
      "upload_size": 0,
      "user": "amigo_teste"
    }
}

BLOG_DEFAULT =  lambda: dict( {
                "teste/Meu_Primeiro_Post":
                { "owner": "teste", 
                  "titulo": u"Meu Primeiro Post",
                  "conteudo": "Conteúdo do meu primeiro Post",
                  "tags": ['blog', 'teste'],
                  "post_id": "Meu_Primeiro_Post",
                  "registry_id": "teste",
                  "data_cri": "2009-12-15 18:09:17.559390" }        
            } )

WIKI_DEFAULT = lambda: dict({
                "teste/home" :
                { "user": "teste", 
                  "owner": "teste",
                  "registry_id": "teste",
                  "nomepag": "home",
                  "conteudo": u"Página inicial do Usuário",
                  "tags": ['wiki', 'teste'],
                  "tipo": "pagina",
                  "data_cri": "2009-12-15 17:09:17.559390" }
            })

SEARCHTAGS = {
    "blog": {
        "comunidades": [],
        "paginas": [],
        "posts": [ "teste/Meu_Primeiro_Post" ],
        "perfil": []
    },
    "comunidade": {
        "comunidades": [ "comunidade1" ],
        "paginas": [],
        "posts": [],
        "perfil": []
    },
    "teste": {
        "comunidades": [ "comunidade1" ],
        "paginas": [ "teste/home" ],
        "posts": [ "teste/Meu_Primeiro_Post" ],
        "perfil": [ "amigo_teste" ]
    },
    "user": {
        "comunidades": [],
        "paginas": [],
        "posts": [],
        "perfil": [ "amigo_teste" ]
    },
    "wiki": {
        "comunidades": [],
        "paginas": [ "teste/home" ],
        "posts": [],
        "perfil": []
    }
}

SEARCH_FORM = {
               "tags": ""
}
search = {}


class TestSearch(unittest.TestCase):
   """Testes unitários para o Blog"""
   def setUp(self):
      #self.mock = Mocker()
      #MEMBER = self.mock.mock()
      
      log.model.LOG = {}
      log.model.NEWS = {}
      model.BLOG = BLOG_DEFAULT()
      model.SEARCHTAGS = SEARCHTAGS
      wiki.model.WIKI = WIKI_DEFAULT()
      wiki.model.WIKIMEMBER = {}
      wiki.model.WIKICOMMUNITY = {}
      core.model.REGISTRY = REGISTRY_DEFAULT
      core.model.MAGKEYS = MAGKEYS_DEFAULT()    # recria chave mágica para que possa fazer outro cadastro
      core.model.INVITES = {}
      core.model.MAGKEYTYPES = {}
      core.model.USERSCHOOL = {}
      log.model.NOTIFICATIONERROR = {}
      log.model.NOTIFICATION = {}
    
      search.update(SEARCH_FORM)
      
      self.app = TestApp(WsgiApp())
      login.update(LOGIN_FORM)
      registry.update(REGISTRY_FORM)
      self.app.post('/new/user', registry)
      self.app.post('/login', login)
      
   def tearDown(self):
      #self.mock.restore()
      #self.mock.verify()
      #self.mock,MEMBER =None,None
      pass

   
   def test_search_index(self):
      "Testa a exibição da página da busca"      
      response = self.app.get('/search')
      assert "<!-- Comentário para o teste da busca -->" in response, "Erro: Não exibiu a tela de busca!"

   def test_search_in_profile(self):
      "Testa a exibição do campo de busca na página principal do usuário"
      response = self.app.get('/user/teste')
      assert "<!-- Comentário para o teste da busca na pagina do perfil -->" in response, "Erro: Não exibiu o campo de busca na página principal do usuário!"
      
   def test_search_blank(self):
      "Testa a busca vazia"      
      response = self.app.post('/search', search)
      assert "<!-- Comentário para o teste da busca -->" in response, "Erro: Não exibiu a tela de busca!"

#   def test_search_blank_in_profile(self):
#      "Testa a busca vazia na página principal do usuário"
#      response = self.app.post('/user/teste',search)
#      assert "<!-- Comentário para o teste da busca -->" in response, "Erro: Não exibiu a tela de busca!"

   def test_search_non_existing_tag(self):
      "Testa a busca por tag não existente"
      search["tags"] = "naoencontrada"
      response = self.app.post('/search', search)
      assert "Tag naoencontrada não encontrada!" in response, "Erro: Não exibiu a tela de busca com a mensagem de erro: 'Tag naoencontrada não encontrada!'!"

   def test_search_tag(self):
      "Testa a busca por tag"
      search["tags"] = "teste"
      response = self.app.post('/search', search)
      assert "amigo_teste" in response, "Erro: Não exibiu usuário que possui a tag!"
      assert "comunidade1" in response, "Erro: Não exibiu comunidade que possui a tag!"
      assert "teste/home" in response, "Erro: Não exibiu página que possui a tag!"
      assert "teste/Meu_Primeiro_Post" in response, "Erro: Não exibiu blog que possui a tag!"

   def test_search_tag_user(self):
      "Testa a busca por tag 'user'"
      search["tags"] = "user"
      response = self.app.post('/search', search)
      assert "amigo_teste" in response, "Erro: Não exibiu usuário que possui a tag!"
      assert "<!-- Comentário para teste Comunidade -->" not in response, "Erro: Exibiu comunidade que não possui a tag!"
      assert "<!-- Comentário para teste Página -->" not in response, "Erro: Exibiu página que não possui a tag!"
      assert "<!-- Comentário para teste Post -->" not in response, "Erro: Exibiu blog que não possui a tag!"

   def test_search_tag_community(self):
      "Testa a busca por tag 'comunidade'"
      search["tags"] = "comunidade"
      response = self.app.post('/search', search)
      assert "comunidade1" in response, "Erro: Não exibiu comunidade que possui a tag!"
      assert "<!-- Comentário para teste Profile -->" not in response, "Erro: Exibiu usuário que não possui a tag!"
      assert "<!-- Comentário para teste Página -->" not in response, "Erro: Exibiu página que não possui a tag!"
      assert "<!-- Comentário para teste Post -->" not in response, "Erro: Exibiu blog que não possui a tag!"

   def test_search_tag_wiki(self):
      "Testa a busca por tag 'wiki'"
      search["tags"] = "wiki"
      response = self.app.post('/search', search)
      assert "teste/home" in response, "Erro: Não exibiu página que possui a tag!"
      assert "<!-- Comentário para teste Comunidade -->" not in response, "Erro: Exibiu comunidade que não possui a tag!"
      assert "<!-- Comentário para teste Profile -->" not in response, "Erro: Exibiu usuário que não possui a tag!"
      assert "<!-- Comentário para teste Post -->" not in response, "Erro: Exibiu blog que não possui a tag!"

   def test_search_tag_post(self):
      "Testa a busca por tag 'blog'"
      search["tags"] = "blog"
      response = self.app.post('/search', search)
      assert "teste/Meu_Primeiro_Post" in response, "Erro: Não exibiu blog que possui a tag!"
      assert "<!-- Comentário para teste Comunidade -->" not in response, "Erro: Exibiu comunidade que não possui a tag!"
      assert "<!-- Comentário para teste Página -->" not in response, "Erro: Exibiu página que não possui a tag!"
      assert "<!-- Comentário para teste Profile -->" not in response, "Erro: Exibiu usuário que não possui a tag!"

   def test_search_tag_user_and_teste(self):
      "Testa a busca por tag 'user & teste'"
      search["tags"] = "user teste"
      response = self.app.post('/search', search)
      assert "amigo_teste" in response, "Erro: Não exibiu usuário que possui a tag!"
      assert "<!-- Comentário para teste Comunidade -->" not in response, "Erro: Exibiu comunidade que não possui a tag!"
      assert "<!-- Comentário para teste Página -->" not in response, "Erro: Exibiu página que não possui a tag!"
      assert "<!-- Comentário para teste Post -->" not in response, "Erro: Exibiu blog que não possui a tag!"

   def test_search_tag_community_and_teste(self):
      "Testa a busca por tag 'comunidade & teste'"
      search["tags"] = "comunidade teste"
      response = self.app.post('/search', search)
      assert "comunidade1" in response, "Erro: Não exibiu comunidade que possui a tag!"
      assert "<!-- Comentário para teste Profile -->" not in response, "Erro: Exibiu usuário que não possui a tag!"
      assert "<!-- Comentário para teste Página -->" not in response, "Erro: Exibiu página que não possui a tag!"
      assert "<!-- Comentário para teste Post -->" not in response, "Erro: Exibiu blog que não possui a tag!"

   def test_search_tag_wiki_and_teste(self):
      "Testa a busca por tag 'wiki & teste'"
      search["tags"] = "wiki teste"
      response = self.app.post('/search', search)
      assert "teste/home" in response, "Erro: Não exibiu página que possui a tag!"
      assert "<!-- Comentário para teste Comunidade -->" not in response, "Erro: Exibiu comunidade que não possui a tag!"
      assert "<!-- Comentário para teste Profile -->" not in response, "Erro: Exibiu usuário que não possui a tag!"
      assert "<!-- Comentário para teste Post -->" not in response, "Erro: Exibiu blog que não possui a tag!"

   def test_search_tag_post_and_teste(self):
      "Testa a busca por tag 'blog & teste'"
      search["tags"] = "blog teste"
      response = self.app.post('/search', search)
      assert "teste/Meu_Primeiro_Post" in response, "Erro: Não exibiu blog que possui a tag!"
      assert "<!-- Comentário para teste Comunidade -->" not in response, "Erro: Exibiu comunidade que não possui a tag!"
      assert "<!-- Comentário para teste Página -->" not in response, "Erro: Exibiu página que não possui a tag!"
      assert "<!-- Comentário para teste Profile -->" not in response, "Erro: Exibiu usuário que não possui a tag!"
