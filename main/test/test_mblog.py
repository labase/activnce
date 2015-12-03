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

import mblog.model as model
import core.model
import log.model
import wiki.model
import unittest

REGISTRY_DEFAULT = lambda: dict( {
                  "comunidade1":
                  { "participantes_pendentes": [],
                    "description": "comunidade um",
                    "participantes":
                     [
                        "teste",
                        "teste2"
                     ],
                    "photo": "",
                    "owner": "teste",
                    "privacidade": u"Pública",
                    "participacao": u"Mediante Convite",
                    "name": "comunidade1",
                    "papeis": ['comunidade']},
                  "comunidade2":
                  { "participantes_pendentes": [],
                    "description": "comunidade dois",
                    "participantes":
                     [
                        "teste2"
                     ],
                    "photo": "",
                    "privacidade": u"Pública",
                    "participacao": u"Mediante Convite",
                    "owner": "teste2",
                    "name": "comunidade2",
                    "papeis": ['comunidade']}
})

MBLOG_DEFAULT =  lambda: dict( {
                "06ed70a43d086c070f0bd99c24c4e2ca":
                { "_id": "06ed70a43d086c070f0bd99c24c4e2ca",
                  "owner": "teste", 
                  "conteudo": "Conteúdo do meu #primeiro Post",
                  "tags": ['primeiro'],
                  "interessados": ["teste"],
                  "registry_id": "teste",
                  "data_cri": "2009-12-15 18:09:17.559390" },
               "1a378bdb22508ebb6434f80d0635a30d":
                { "_id": "1a378bdb22508ebb6434f80d0635a30d",
                  "owner":"teste",
                  "conteudo": "Página a ser apagada!!!",
                  "tags": [],
                  "interessados": ["teste"],
                  "registry_id": "teste",                                
                  "data_cri": "2009-12-17 18:09:17.559390" },
               "1fdaf38b4f7f2365ef56c144b5aca09b":
                { "_id": "1fdaf38b4f7f2365ef56c144b5aca09b",
                  "owner":"teste",
                  "conteudo": "Post da #comunidade 1!!!",
                  "tags": ['comunidade'],
                  "interessados": ["teste", "teste2"],
                  "registry_id": "comunidade1",                                  
                  "data_cri": "2009-12-17 18:09:17.559390" },
               "2a77d638f8a280223bf3e912f174da33":
                { "_id": "2a77d638f8a280223bf3e912f174da33",
                  "owner":"teste",
                  "conteudo": "Outro post da comunidade 1!!!",
                  "tags": [],
                  "interessados": ["teste", "teste2"],
                  "registry_id": "comunidade1",                                  
                  "data_cri": "2009-12-17 18:09:17.559390" }                 
            } )

MBLOG_EXTRA = {
            "00001":
            { "_id": "00001",
              "owner": "teste", 
              "conteudo": "Conteúdo do meu #primeiro Post",
              "tags": ['primeiro'],
              "interessados": ["teste"],
              "registry_id": "teste",
              "data_cri": "2009-12-15 18:09:17.559390" },               
            "00002":
            { "_id": "00002",
              "owner": "teste", 
              "conteudo": "Conteúdo do meu #primeiro Post",
              "tags": ['primeiro'],
              "interessados": ["teste"],
              "registry_id": "teste",
              "data_cri": "2009-12-15 18:09:17.559390" },
            "00003":
            { "_id": "00003",
              "owner": "teste", 
              "conteudo": "Conteúdo do meu #primeiro Post",
              "tags": ['primeiro'],
              "interessados": ["teste"],
              "registry_id": "teste",
              "data_cri": "2009-12-15 18:09:17.559390" },
            "00004":
            { "_id": "00004",
              "owner": "teste", 
              "conteudo": "Conteúdo do meu #primeiro Post",
              "tags": ['primeiro'],
              "interessados": ["teste"],
              "registry_id": "teste",
              "data_cri": "2009-12-15 18:09:17.559390" },
            "00005":
            { "_id": "00005",
              "owner": "teste", 
              "conteudo": "Conteúdo do meu #primeiro Post",
              "tags": ['primeiro'],
              "interessados": ["teste"],
              "registry_id": "teste",
              "data_cri": "2009-12-15 18:09:17.559390" },
            "00006":
            { "_id": "00006",
              "owner": "teste", 
              "conteudo": "Conteúdo do meu #primeiro Post",
              "tags": ['primeiro'],
              "interessados": ["teste"],
              "registry_id": "teste",
              "data_cri": "2009-12-15 18:09:17.559390" },
            "00007":
            { "_id": "00007",
              "owner": "teste", 
              "conteudo": "Conteúdo do meu #primeiro Post",
              "tags": ['primeiro'],
              "interessados": ["teste"],
              "registry_id": "teste",
              "data_cri": "2009-12-15 18:09:17.559390" },
            "00008":
            { "_id": "00008",
              "owner": "teste", 
              "conteudo": "Conteúdo do meu #primeiro Post",
              "tags": ['primeiro'],
              "interessados": ["teste"],
              "registry_id": "teste",
              "data_cri": "2009-12-15 18:09:17.559390" },
            "00009":
            { "_id": "00009",
              "owner": "teste", 
              "conteudo": "Conteúdo do meu #primeiro Post",
              "tags": ['primeiro'],
              "interessados": ["teste"],
              "registry_id": "teste",
              "data_cri": "2009-12-15 18:09:17.559390" },
            "00010":
            { "_id": "00010",
              "owner": "teste", 
              "conteudo": "Conteúdo do meu #primeiro Post",
              "tags": ['primeiro'],
              "interessados": ["teste"],
              "registry_id": "teste",
              "data_cri": "2009-12-15 18:09:17.559390" },
            "00011":
            { "_id": "00011",
              "owner": "teste", 
              "conteudo": "Conteúdo do meu #primeiro Post",
              "tags": ['primeiro'],
              "interessados": ["teste"],
              "registry_id": "teste",
              "data_cri": "2009-12-15 18:09:17.559390" },
            "00012":
            { "_id": "00012",
              "owner": "teste", 
              "conteudo": "Conteúdo do meu #primeiro Post",
              "tags": ['primeiro'],
              "interessados": ["teste"],
              "registry_id": "teste",
              "data_cri": "2009-12-15 18:09:17.559390" },
            "00012":
            { "_id": "00012",
              "owner": "teste", 
              "conteudo": "Conteúdo do meu #primeiro Post",
              "tags": ['primeiro'],
              "interessados": ["teste"],
              "registry_id": "teste",
              "data_cri": "2009-12-15 18:09:17.559390" },
            "00013":
            { "_id": "00013",
              "owner": "teste", 
              "conteudo": "Conteúdo do meu #primeiro Post",
              "tags": ['primeiro'],
              "interessados": ["teste"],
              "registry_id": "teste",
              "data_cri": "2009-12-15 18:09:17.559390" },
            "00014":
            { "_id": "00014",
              "owner": "teste", 
              "conteudo": "Conteúdo do meu #primeiro Post",
              "tags": ['primeiro'],
              "interessados": ["teste"],
              "registry_id": "teste",
              "data_cri": "2009-12-15 18:09:17.559390" },
            "00014":
            { "_id": "00014",
              "owner": "teste", 
              "conteudo": "Conteúdo do meu #primeiro Post",
              "tags": ['primeiro'],
              "interessados": ["teste"],
              "registry_id": "teste",
              "data_cri": "2009-12-15 18:09:17.559390" },
            "00015":
            { "_id": "00015",
              "owner": "teste", 
              "conteudo": "Conteúdo do meu #primeiro Post",
              "tags": ['primeiro'],
              "interessados": ["teste"],
              "registry_id": "teste",
              "data_cri": "2009-12-15 18:09:17.559390" },
            "00016":
            { "_id": "00016",
              "owner": "teste", 
              "conteudo": "Conteúdo do meu #primeiro Post",
              "tags": ['primeiro'],
              "interessados": ["teste"],
              "registry_id": "teste",
              "data_cri": "2009-12-15 18:09:17.559390" },
            "00017":
            { "_id": "00017",
              "owner": "teste", 
              "conteudo": "Conteúdo do meu #primeiro Post",
              "tags": ['primeiro'],
              "interessados": ["teste"],
              "registry_id": "teste",
              "data_cri": "2009-12-15 18:09:17.559390" },
            "00018":
            { "_id": "00018",
              "owner": "teste", 
              "conteudo": "Conteúdo do meu #primeiro Post",
              "tags": ['primeiro'],
              "interessados": ["teste"],
              "registry_id": "teste",
              "data_cri": "2009-12-15 18:09:17.559390" },
            "00019":
            { "_id": "00019",
              "owner": "teste", 
              "conteudo": "Conteúdo do meu #primeiro Post",
              "tags": ['primeiro'],
              "interessados": ["teste"],
              "registry_id": "teste",
              "data_cri": "2009-12-15 18:09:17.559390" },
            "00020":
            { "_id": "00020",
              "owner": "teste", 
              "conteudo": "Conteúdo do meu #primeiro Post",
              "tags": ['primeiro'],
              "interessados": ["teste"],
              "registry_id": "teste",
              "data_cri": "2009-12-15 18:09:17.559390" },
            "00021":
            { "_id": "00021",
              "owner": "teste", 
              "conteudo": "Conteúdo do meu #primeiro Post",
              "tags": ['primeiro'],
              "interessados": ["teste"],
              "registry_id": "teste",
              "data_cri": "2009-12-15 18:09:17.559390" }
}

REGISTRYMBLOG_DEFAULT = lambda: dict ({
                    "teste": {
                        "posts": ["1fdaf38b4f7f2365ef56c144b5aca09b",
                                  "2a77d638f8a280223bf3e912f174da33",
                                  "06ed70a43d086c070f0bd99c24c4e2ca",
                                  "1a378bdb22508ebb6434f80d0635a30d"
                                 ]
                    },

                    "teste2": {
                       "posts": [ "1fdaf38b4f7f2365ef56c144b5aca09b",
                                  "2a77d638f8a280223bf3e912f174da33"
                                ]
                    },
                    "comunidade1": {
                       "posts": [ "1fdaf38b4f7f2365ef56c144b5aca09b",
                                  "2a77d638f8a280223bf3e912f174da33"
                                ]
                    }                     
                 })

REGISTRYMBLOG_EXTRA = {
                    "teste": {
                        "posts": ["00001",
                                  "00002",
                                  "00003",
                                  "00004",
                                  "00005",
                                  "00006",
                                  "00007",
                                  "00008",
                                  "00009",
                                  "00010",
                                  "00011",
                                  "00012",
                                  "00013",
                                  "00014",
                                  "00015",
                                  "00016",
                                  "00017",
                                  "00018",
                                  "00019",
                                  "00020",
                                  "00021",
                                 ]
                    }
                 }

REGISTRYMBLOGOWNERS_DEFAULT = lambda: dict ({
                    "teste": {
                        "posts": ["1fdaf38b4f7f2365ef56c144b5aca09b",
                                  "2a77d638f8a280223bf3e912f174da33",
                                  "06ed70a43d086c070f0bd99c24c4e2ca",
                                  "1a378bdb22508ebb6434f80d0635a30d"
                                 ]
                    },
                    "comunidade1": {
                       "posts": [ "1fdaf38b4f7f2365ef56c144b5aca09b",
                                  "2a77d638f8a280223bf3e912f174da33"
                                ]
                    }                     
                 })

REGISTRYMBLOGOWNERS_EXTRA = {
                    "teste": {
                        "posts": ["00001",
                                  "00002",
                                  "00003",
                                  "00004",
                                  "00005",
                                  "00006",
                                  "00007",
                                  "00008",
                                  "00009",
                                  "00010",
                                  "00011",
                                  "00012",
                                  "00013",
                                  "00014",
                                  "00015",
                                  "00016",
                                  "00017",
                                  "00018",
                                  "00019",
                                  "00020",
                                  "00021",
                                 ]
                    }
                 }


#class TestCadastro(mocker.MockerTestCase):
class TestMblog(unittest.TestCase):
   """Testes unitários para o Blog"""
   def setUp(self):
      #self.mock = Mocker()
      #MEMBER = self.mock.mock()

      log.model.LOG = {}            
      log.model.NEWS = {}
      model.MBLOG = MBLOG_DEFAULT()
      model.REGISTRYMBLOG = REGISTRYMBLOG_DEFAULT()
      model.REGISTRYMBLOGOWNERS = REGISTRYMBLOGOWNERS_DEFAULT()
      wiki.model.WIKI = {}
      wiki.model.WIKIMEMBER = {}
      wiki.model.WIKICOMMUNITY = {}      
      core.model.REGISTRY = REGISTRY_DEFAULT()
      core.model.MAGKEYS = MAGKEYS_DEFAULT()    # recria chave mágica para que possa fazer outro cadastro  
      core.model.INVITES = {}
      core.model.MAGKEYTYPES = {}
      core.model.USERSCHOOL = {}    
      log.model.NOTIFICATIONERROR = {}
      log.model.NOTIFICATION = {}
    
      self.app = TestApp(WsgiApp())
      login.update(LOGIN_FORM)
      registry.update(REGISTRY_FORM)
      self.app.post('/new/user', registry)
      core.model.REGISTRY['teste']['papeis'].append('professor')
      #assert False, core.model.REGISTRY['teste']
      registry['user'] = 'teste2'
      core.model.MAGKEYS = MAGKEYS_DEFAULT()    # recria chave mágica para que possa fazer outro cadastro  
      self.app.post('/new/user', registry)      
      registry['user'] = 'outrousuario'
      core.model.MAGKEYS = MAGKEYS_DEFAULT()    # recria chave mágica para que possa fazer outro cadastro  
      self.app.post('/new/user', registry)      
      self.app.post('/login', login)
      #assert False, core.model.REGISTRY
      
   def tearDown(self):
      #self.mock.restore()
      #self.mock.verify()
      #self.mock,MEMBER =None,None
      pass

  # -------------------------------------------------------------
  # Listar um mblog
  
   def test_list_user_mblog(self):
      "Testa a exibição do mblog do usuário teste"
      response = self.app.get('/mblog/teste')
      assert '<form name="novamsg" action="/mblog/new/teste" method="post">' in response, "Erro: Não exibiu o formulario para novo post!"
      assert 'Conteúdo do meu #primeiro Post' in response, "Erro: Não exibiu o primeiro POST do MBLOG!"
      assert '15 de Dezembro de 2009 às 18:09' in response, "Erro: Não exibiu a data de publicação do primeiro POST!"
      assert 'Página a ser apagada!!!' in response, "Erro: Não exibiu o segundo POST do BLOG!"
      assert 'Post da #comunidade 1!!!' in response, "Erro: Não exibiu o terceiro POST do BLOG!"
      assert 'Outro post da comunidade 1!!!' in response, "Erro: Não exibiu o quarto POST do BLOG!"
      
   def test_list_user_mblog_pages(self):
      "Testa a exibição da paginação do mblog do usuário teste"      
      model.MBLOG = MBLOG_EXTRA
      model.REGISTRYMBLOG = REGISTRYMBLOG_EXTRA
      model.REGISTRYMBLOGOWNERS = REGISTRYMBLOGOWNERS_EXTRA
      response = self.app.get('/mblog/teste?pag=1')
      assert "id=00001" in response, "Erro: Não mostrou o post correto(00001)"
      assert "id=00002" in response, "Erro: Não mostrou o post correto(00002)"
      assert "id=00003" in response, "Erro: Não mostrou o post correto(00003)"
      assert "id=00004" in response, "Erro: Não mostrou o post correto(00004)"
      assert "id=00005" in response, "Erro: Não mostrou o post correto(00005)"
      assert "id=00006" in response, "Erro: Não mostrou o post correto(00006)"
      assert "id=00007" in response, "Erro: Não mostrou o post correto(00007)"
      assert "id=00008" in response, "Erro: Não mostrou o post correto(00008)"
      assert "id=00009" in response, "Erro: Não mostrou o post correto(00009)"
      assert "id=00010" in response, "Erro: Não mostrou o post correto(00010)"
      assert '<a href="?pag=2">2' in response, "Erro: Não mostrou o link para a página(2)"
      assert '<a href="?pag=3">3' in response, "Erro: Não mostrou o link para a página(3)"
      response = self.app.get('/mblog/teste?pag=2')
      assert "id=00011" in response, "Erro: Não mostrou o post correto(00011)"
      assert "id=00012" in response, "Erro: Não mostrou o post correto(00012)"
      assert "id=00013" in response, "Erro: Não mostrou o post correto(00013)"
      assert "id=00014" in response, "Erro: Não mostrou o post correto(00014)"
      assert "id=00015" in response, "Erro: Não mostrou o post correto(00015)"
      assert "id=00016" in response, "Erro: Não mostrou o post correto(00016)"
      assert "id=00017" in response, "Erro: Não mostrou o post correto(00017)"
      assert "id=00018" in response, "Erro: Não mostrou o post correto(00018)"
      assert "id=00019" in response, "Erro: Não mostrou o post correto(00019)"
      assert "id=00020" in response, "Erro: Não mostrou o post correto(00020)"
      assert '<a href="?pag=1">1' in response, "Erro: Não mostrou o link para a página(1)"
      assert '<a href="?pag=3">3' in response, "Erro: Não mostrou o link para a página(3)"
      response = self.app.get('/mblog/teste?pag=3')
      assert "id=00021" in response, "Erro: Não mostrou o post correto(00021)"
      assert '<a href="?pag=1">1' in response, "Erro: Não mostrou o link para a página(1)"
      assert '<a href="?pag=2">2' in response, "Erro: Não mostrou o link para a página(2)"

   def test_list_user_mblog_page_not_found(self):
       "Testa a exibição da mensagem de erro de página não encontrada"
       response = self.app.get('/mblog/teste?pag=0')
       assert u"Número de página não encontrado" in response, "Erro: Não exibiu mensagem 'Número de página não encontrado' (pag 0)"
       response = self.app.get('/mblog/teste?pag=-1')
       assert u"Número de página não encontrado" in response, "Erro: Não exibiu mensagem 'Número de página não encontrado' (pag -1)"
       response = self.app.get('/mblog/teste?pag=10')
       assert u"Número de página não encontrado" in response, "Erro: Não exibiu mensagem 'Número de página não encontrado' (pag 10)"
       
   def test_list_community_mblog(self):
      "Testa a exibição do mblog da comunidade1"      
      #core.model.REGISTRY['teste']['papeis'].append('professor')
      #assert False, core.model.REGISTRY['teste']
      response = self.app.get('/mblog/comunidade1')
      assert '<form name="novamsg" action="/mblog/new/comunidade1" method="post">' in response, "Erro: Não exibiu o formulario para novo post!"
      assert 'Post da #comunidade 1!!!' in response, "Erro: Não exibiu o terceiro POST do BLOG!"
      assert 'Outro post da comunidade 1!!!' in response, "Erro: Não exibiu o quarto POST do BLOG!"
   
       
   def test_reject_list_blog_incorrect_user(self):
      "Testa a exibição do blog de um usuário inexistente"      
      response = self.app.get('/mblog/usuario_inexistente')
      assert 'Usuário ou comunidade inexistentes.' in response, "Erro: Não exibiu o BLOG do usuário!"


  # -------------------------------------------------------------
  # Criar um post
    
  
   '''
   TODO: está com problema na chamada de model.REGISTRYMBLOG.create que
   não é reconhecida no ambiente de teste.
   '''
   def test_save_user_post(self):
      "Testa se um novo post de usuário foi incluído"
      response = self.app.post('/mblog/new/teste', {"conteudo":u"Este novo post foi incluido agora"}).follow()
      assert u'Este novo post foi incluido agora' in response, "Erro: Não exibiu conteúdo do POST do usuário!"
      post_id = ""
      for id in model.MBLOG:
         if model.MBLOG[id]["conteudo"] == 'Este novo post foi incluido agora':
            post_id = id
            break
      assert post_id, "Erro: Não incluiu o post no MBLOG."
      assert post_id in model.REGISTRYMBLOG["teste"]["posts"], "Erro: Não incluiu o post em REGISTRYMBLOG."
      
   def test_save_user_post_with_arroba(self):
      "Testa se um novo post de usuário foi incluído"
      response = self.app.post('/mblog/new/teste', {"conteudo":"Este novo post para @outrousuario"}).follow()
      assert u'Este novo post para @<a title="fulano de tal" href="/mblog/outrousuario">outrousuario</a>' in response, "Erro: Não exibiu conteúdo do POST do usuário!"
      post_id = ""
      for id in model.MBLOG:
         if model.MBLOG[id]["conteudo"] == 'Este novo post para @<a title="fulano de tal" href="/mblog/outrousuario">outrousuario</a>':
            post_id = id
            break
      assert post_id, "Erro: Não incluiu o post no MBLOG."
      assert "outrousuario" in model.MBLOG[post_id]["interessados"], "Erro: Não incluiu o usuário referenciado na lista de interessados."
      assert post_id in model.REGISTRYMBLOG["teste"]["posts"], "Erro: Não incluiu o post em REGISTRYMBLOG."
      assert post_id in model.REGISTRYMBLOG["outrousuario"]["posts"], "Erro: Não incluiu o usuário referenciado na lista de interessados."

   def test_save_user_post_with_sharp(self):
      "Testa se um novo post de usuário foi incluído"
      response = self.app.post('/mblog/new/teste', {"conteudo":"Este novo post com tag #exemplo"}).follow()
      assert u'Este novo post com tag #exemplo' in response, "Erro: Não exibiu conteúdo do POST do usuário!"
      post_id = ""
      for id in model.MBLOG:
         if model.MBLOG[id]["conteudo"] == 'Este novo post com tag #exemplo':
            post_id = id
            break
      assert post_id, "Erro: Não incluiu o post no MBLOG."
      assert "exemplo" in model.MBLOG[id]["tags"], "Erro: não armazenou a tag"
      assert post_id in model.REGISTRYMBLOG["teste"]["posts"], "Erro: Não incluiu o post em REGISTRYMBLOG."

   def test_save_community_post(self):
      "Testa se um novo post de comunidade foi incluído"
      response = self.app.post('/mblog/new/comunidade1', {"conteudo":"Este novo post foi incluido agora"}).follow()
      assert u'Este novo post foi incluido agora' in response, "Erro: Não exibiu conteúdo do POST do usuário!"
      post_id = ""
      for id in model.MBLOG:
         if model.MBLOG[id]["conteudo"] == 'Este novo post foi incluido agora':
            post_id = id
            break
      assert post_id, "Erro: Não incluiu o post no MBLOG."
      assert post_id in model.REGISTRYMBLOG["teste"]["posts"], "Erro: Não incluiu o post em REGISTRYMBLOG."
      
   def test_reject_create_new_post_unauthorized_user(self):
      "Testa o formulário de criação de um novo post se o usuário não for o dono do blog"
      response = self.app.post('/mblog/new/outrousuario', {"conteudo":"Este novo post foi incluído agora"})
      assert 'Você não tem permissão para postar no mblog de outro usuário.' in response, "Erro: Não exibiu mensagem 'Você não tem permissão para postar no blog de outro usuário.'!"
   
   def test_reject_create_new_post_unauthorized_community(self):
      "Testa o formulário de criação de um novo post se o usuário não for o dono do blog"
      response = self.app.post('/mblog/new/comunidade2', {"conteudo":"Este novo post foi incluído agora"})
      assert 'Você não é membro desta comunidade.' in response, "Erro: Não exibiu mensagem 'Você não é membro desta comunidade.'!"


  # -------------------------------------------------------------
  # Remover posts
  
   def test_reject_delete_post_unauthorized_user(self):
      "Testa remover um post de outro usuário."
      self.app.post('/login', {"user":"outrousuario", "passwd": "teste", "tipo": "tnm"})       
      response = self.app.get('/mblog/delete?id=1a378bdb22508ebb6434f80d0635a30d')
      assert 'Você não tem permissão para apagar um post de outro usuário.' in response, "Erro: Não exibiu mensagem 'Você não tem permissão para apagar um post de outro usuário.'!"

   def test_reject_delete_post_unauthorized_community(self):
      "Testa remover um post de comunidade por um usuário que não participa da mesma"
      self.app.post('/login', {"user":"outrousuario", "passwd": "teste", "tipo": "tnm"})       
      response = self.app.get('/mblog/delete?id=2a77d638f8a280223bf3e912f174da33')
      assert 'Você não é membro desta comunidade e por isso não pode apagar este post.' in response, "Erro: Não exibiu mensagem 'Você não é membro desta comunidade.'!"

   def test_reject_delete_incorrect_post(self):
      "Testa erro ao tentar remover post inexistente"
      response = self.app.get('/mblog/delete?id=123456')
      assert u'Post não encontrado' in response, "Erro: Não exibiu mensagem de post não encontrado!"

   def test_delete_post_ok(self):
      "Testa exclusão de post"
      response = self.app.get('/mblog/delete?id=1a378bdb22508ebb6434f80d0635a30d').follow()
      assert u'Post a ser removido' not in response, "Erro: Exibiu título do POST removido!"
      assert "1a378bdb22508ebb6434f80d0635a30d" not in model.MBLOG, "Erro: Não removeu o post no banco."
      for registry_id in model.REGISTRYMBLOG:
         assert "1a378bdb22508ebb6434f80d0635a30d" not in model.REGISTRYMBLOG[registry_id]["posts"], "Erro: Não removeu o post em REGISTRYMBLOG."


