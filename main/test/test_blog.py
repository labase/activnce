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

import blog.model as model
import core.model
import log.model
import search.model
import wiki.model
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
      "owner": "teste",
      "name": "comunidade1",
      "privacidade": u"Pública",
      "participacao": u"Mediante Convite",
      "admins": ""
   },
   "comunidade2": {
      "participantes_pendentes": [],
      "description": "comunidade dois",
      "participantes": [
          "teste2"
      ],
      "photo": "",
      "owner": "teste2",
      "name": "comunidade2",
      "privacidade": u"Pública",
      "participacao": u"Mediante Convite",
      "admins": ""
   }
}

BLOG_DEFAULT =  lambda: dict( {
                "teste/Meu_Primeiro_Post":
                { "owner": "teste", 
                  "titulo": u"Meu Primeiro Post",
                  "conteudo": "Conteúdo do meu primeiro Post",
                  "tags": ['rio', 'manaus'],
                  "post_id": "Meu_Primeiro_Post",
                  "registry_id": "teste",
                  "data_cri": "2009-12-15 18:09:17.559390" },
               "teste/Post_a_ser_removido":
                { "owner":"teste",
                  "titulo": "Post a ser removido",
                  "conteudo": "<b> Página a ser apagada!!! </b>",
                  "tags": ['teste', 'apagar'],
                  "post_id": "Post_a_ser_removido",
                  "registry_id": "teste",                                
                  "data_cri": "2009-12-17 18:09:17.559390" },
               "comunidade1/pag1":
                { "owner":"teste",
                  "titulo": "pag1",
                  "conteudo": "<b> Página da comunidade 1!!! </b>",
                  "tags": ['teste'],
                  "post_id": "pag1",
                  "registry_id": "comunidade1",                                  
                  "data_cri": "2009-12-17 18:09:17.559390" },
               "comunidade1/pag2":
                { "owner":"teste",
                  "titulo": "pag2",
                  "conteudo": "<b> Outra página da comunidade 1!!! </b>",
                  "tags": ['teste'],
                  "post_id": "pag2",
                  "registry_id": "comunidade1",                                  
                  "data_cri": "2009-12-17 18:09:17.559390" }                 
            } )

REGISTRYBLOG_DEFAULT = lambda: dict ({
                    "teste": {
                        "posts": ["teste/Meu_Primeiro_Post",
                                  "teste/Post_a_ser_removido"
                                 ]
                    },

                    "comunidade1": {
                       "posts": [ "comunidade1/pag1",
                                  "comunidade1/pag2"
                                ]
                    }
                 })

COMMENT_DEFAULT = lambda: dict( {
                "da017890b6968741efb07298077d411c": {
                "_id": "da017890b6968741efb07298077d411c",
                "comment": "gostei do seu post",
                "data_cri": "2010-03-17 09:53:53.129265",
                "owner": "teste2",
                "post_id": "Meu_Primeiro_Post",
                "registry_id": "teste"
                },
                "92348571b6968741efb07298077d411c": {
                "_id": "92348571b6968741efb07298077d411c",
                "comment": "comentário a ser removido",
                "data_cri": "2010-03-17 09:53:53.129265",
                "owner": "teste2",
                "post_id": "Meu_Primeiro_Post",
                "registry_id": "teste"
                }                                
})

POSTCOMMENTS_DEFAULT = lambda: dict({
                "teste/Meu_Primeiro_Post": {
                   "comments": ["da017890b6968741efb07298077d411c",
                                "92348571b6968741efb07298077d411c"]             
                }
})

FORM_POST = { "titulo": "um novo post",
             "conteudo": "<b>Este novo post foi incluído agora</b>",
             "tags": "riodejaneiro carnaval2010"
           }

FORM_POST_COM_ACENTOS = {
             "titulo": "É $ possível # criar @ um % post ! com = acentos???",
             "conteudo": "<b>Este novo post foi incluído agora</b>",
             "tags": "riodejaneiro carnaval2010"
           }

FORM_COMMENT = {
             "comment": "Comentando este post..."
           }


#class TestCadastro(mocker.MockerTestCase):
class TestBlog(unittest.TestCase):
   """Testes unitários para o Blog"""
   def setUp(self):
      #self.mock = Mocker()
      #MEMBER = self.mock.mock()
      
      log.model.LOG = {}            
      log.model.NEWS = {}
      model.BLOG = BLOG_DEFAULT()
      model.REGISTRYBLOG = REGISTRYBLOG_DEFAULT()
      model.COMMENT = COMMENT_DEFAULT()
      model.POSTCOMMENTS = POSTCOMMENTS_DEFAULT()
      search.model.SEARCHTAGS = {}
      wiki.model.WIKI = {}
      wiki.model.WIKIMEMBER = {}
      wiki.model.WIKICOMMUNITY = {}      
      core.model.REGISTRY = REGISTRY_DEFAULT
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
      registry['user'] = 'teste2'
      core.model.MAGKEYS = MAGKEYS_DEFAULT()    # recria chave mágica para que possa fazer outro cadastro    
      self.app.post('/new/user', registry)      
      registry['user'] = 'outrousuario'
      core.model.MAGKEYS = MAGKEYS_DEFAULT()    # recria chave mágica para que possa fazer outro cadastro    
      self.app.post('/new/user', registry)
      self.app.post('/login', login)   
      
   def tearDown(self):
      #self.mock.restore()
      #self.mock.verify()
      #self.mock,MEMBER =None,None
      pass

  # -------------------------------------------------------------
  # Listar um blog
   
   def test_list_blog(self):
      "Testa a exibição do blog do usuário teste"      
      response = self.app.get('/blog/teste', headers={'Accept-Language':'pt-br'})
      assert 'Conteúdo do meu primeiro Post' in response, response #"Erro: Não exibiu o primeiro POST do BLOG!"
      assert 'Página a ser apagada!!!' in response, "Erro: Não exibiu o segundo POST do BLOG!"
      assert 'Postado por <a href="/user/teste">teste</a> em 15/12/2009 às 18:09' in response, locale.getlocale() #"Erro: Não exibiu a data de publicação do primeiro POST do BLOG!"

   def test_list_blog_incorrect_user(self):
      "Testa a exibição do blog do usuário teste"      
      response = self.app.get('/blog/usuario_inexistente')
      assert 'Usuário ou comunidade inexistentes.' in response, "Erro: Não exibiu o BLOG do usuário!"

  # -------------------------------------------------------------
  # Listar um post
  
   def test_list_post(self):
      "Testa a exibição de um post do usuário teste"      
      response = self.app.get('/blog/teste/Meu_Primeiro_Post')
      assert u'Meu Primeiro Post' in response, "Erro: Não exibiu título do POST do usuário!"
      assert u'Conteúdo do meu primeiro Post' in response, "Erro: Não exibiu conteúdo do POST do usuário!"
      
   def test_list_post_incorrect(self):
      "Testa a exibição de um post inexistente"      
      response = self.app.get('/blog/teste/Post_Inexistente')
      assert u'Post não encontrado.' in response, "Erro: Não exibiu mensagem de post inexistente!"

   def test_list_post_incorrect_user(self):
      "Testa a exibição de usuário/post inexistentes"      
      response = self.app.get('/blog/usuario_inexistente/Post_Inexistente')
      assert u'Usuário ou comunidade inexistentes.' in response, "Erro: Não exibiu mensagem de post inexistente!"


  # -------------------------------------------------------------
  # Criar um post
  
   def test_create_new_post_user_form(self):
      "Testa o formulário de criação de um novo post no blog de um usuário"
      response = self.app.get('/blog/new/teste', headers={'Accept-Language':'pt-br'})
      assert '<h2>Título do post:</h2> <input name="titulo" ' in response, "Erro: Não exibiu formulário para criação do post!"
      assert '<textarea name="conteudo">Entre aqui com o conteúdo do seu post. &lt;br/&gt;</textarea>'  in response, "Erro: Não exibiu pedido de entrar conteúdo"
      assert '<script type="text/javascript">' in response, "Erro: Não chamou o editor"
      
   def test_create_new_post_community_form(self):
      "Testa o formulário de criação de um novo post no blog de uma comunidade"
      response = self.app.get('/blog/new/comunidade1', headers={'Accept-Language':'pt-br'})
      assert '<h2>Título do post:</h2> <input name="titulo" ' in response, "Erro: Não exibiu formulário para criação do post!"
      assert '<textarea name="conteudo">Entre aqui com o conteúdo do seu post. &lt;br/&gt;</textarea>'  in response, "Erro: Não exibiu pedido de entrar conteúdo"
      assert '<script type="text/javascript">' in response, "Erro: Não chamou o editor"
   
   def test_reject_create_new_post_unauthorized_user(self):
      "Testa o formulário de criação de um novo post se o usuário não for o dono do blog"
      response = self.app.get('/blog/new/outrousuario')
      assert 'Você não tem permissão para postar neste blog.' in response, "Erro: Não exibiu mensagem 'Você não tem permissão para postar neste blog.'!"

   def test_reject_create_new_post_unauthorized_community(self):
      "Testa o formulário de criação de um novo post se o usuário não for o dono do blog"
      response = self.app.get('/blog/new/comunidade2')
      assert 'Você não tem permissão para postar neste blog.' in response, "Erro: Não exibiu mensagem 'Você não tem permissão para postar neste blog.'!"

   def test_reject_create_new_post_inexistent_user(self):
      "Testa o formulário de criação de uma página nova da wiki"
      response = self.app.get('/blog/new/usuarioinexistente')
      assert 'Usuário ou comunidade inexistentes.' in response, "Erro: Não exibiu mensagem 'registro inexistente'!"
      
   def test_reject_empty_post(self):
      "Testa erro se o conteúdo do post for vazio"
      response = self.app.post('/blog/new/teste', {"titulo": "post vazio", "conteudo": "", "tags": ""})
      assert u'O conteúdo do Post não pode ser vazio.' in response, "Erro: Não exibiu mensagem 'conteúdo vazio'!"

   def test_reject_duplicated_post(self):
      "Testa erro se já existir um post com o mesmo título"
      response = self.app.post('/blog/new/teste', {"titulo": "Meu Primeiro Post", "conteudo": "xxx", "tags": ""})
      assert u'Já existe um post com este título.' in response, "Erro: Não exibiu mensagem de post duplicado!"

   def test_save_user_post(self):
      "Testa se um novo post de usuário foi incluído"
      response = self.app.post('/blog/new/teste', FORM_POST).follow()
      assert u'um novo post' in response, "Erro: Não exibiu título do POST do usuário!"
      assert u'<b>Este novo post foi incluído agora</b>' in response, "Erro: Não exibiu conteúdo do POST do usuário!"
      assert model.BLOG["teste/um_novo_post"]["titulo"] == u'um novo post', "Erro: Não incluiu o título no banco."
      assert "teste/um_novo_post" in model.REGISTRYBLOG["teste"]["posts"], "Erro: Não incluiu o post em REGISTRYBLOG."
      assert "teste/um_novo_post" in search.model.SEARCHTAGS["riodejaneiro"]["posts"], "Erro: Não incluiu a tag na tabela de tags"
      assert "teste/um_novo_post" in search.model.SEARCHTAGS["carnaval2010"]["posts"], "Erro: Não incluiu a tag na tabela de tags"

   def test_save_user_post_with_special_chars(self):
      "Testa se um novo post de usuário foi incluído com títulos com caracteres especiais"
      response = self.app.post('/blog/new/teste', FORM_POST_COM_ACENTOS).follow()
      assert u'É $ possível # criar @ um % post ! com = acentos???' in response, "Erro: Não exibiu título do POST do usuário!"
      assert u'<b>Este novo post foi incluído agora</b>' in response, "Erro: Não exibiu conteúdo do POST do usuário!"
      assert model.BLOG["teste/E__possivel__criar__um__post__com__acentos"]["titulo"] == u'É $ possível # criar @ um % post ! com = acentos???', "Erro: Não incluiu o título no banco."
      assert "teste/E__possivel__criar__um__post__com__acentos" in model.REGISTRYBLOG["teste"]["posts"], "Erro: Não incluiu o post em REGISTRYBLOG."

   def test_save_community_post(self):
      "Testa se um novo post de comunidade foi incluído"
      response = self.app.post('/blog/new/comunidade1', FORM_POST).follow()
      assert u'um novo post' in response, "Erro: Não exibiu título do POST do usuário!"
      assert u'<b>Este novo post foi incluído agora</b>' in response, "Erro: Não exibiu conteúdo do POST do usuário!"
      assert model.BLOG["comunidade1/um_novo_post"]["titulo"] == u'um novo post', "Erro: Não incluiu o título no banco."
      assert "comunidade1/um_novo_post" in model.REGISTRYBLOG["comunidade1"]["posts"], "Erro: Não incluiu o post em REGISTRYBLOG."
      assert "comunidade1/um_novo_post" in search.model.SEARCHTAGS["riodejaneiro"]["posts"], "Erro: Não incluiu a tag na tabela de tags"
      assert "comunidade1/um_novo_post" in search.model.SEARCHTAGS["carnaval2010"]["posts"], "Erro: Não incluiu a tag na tabela de tags"

  # -------------------------------------------------------------
  # Listar/enviar comentários
  
   def test_list_post_comment_form(self):
      "Testa a exibição do form de comentário no post do usuário teste"      
      response = self.app.get('/blog/teste/Meu_Primeiro_Post')
      assert u'<form name="postcomment" action="/blog/comment/teste/Meu_Primeiro_Post" method="post">' in response, "Erro: Não exibiu form de comentário!"
      
   def test_list_post_comment(self):
      "Testa a exibição de comentários no post do usuário teste"      
      response = self.app.get('/blog/teste/Meu_Primeiro_Post')
      assert u'gostei do seu post' in response, "Erro: Não exibiu o texto do comentário!"
      assert u'<a href="/user/teste2">teste2</a> em 17/03/2010 às 09:53' in response, "Erro: Não exibiu assinatura do comentário!"
      
   def test_reject_empty_user_comment(self):
      "Testa erro ao enviar comentário vazio"
      response = self.app.post('/blog/comment/teste/Meu_Primeiro_Post', {"comment": ""})
      assert u'O comentário não pode ser vazio.' in response, "Erro: Não exibiu mensagem de comentário vazio!"

   def test_reject_incorrect_post_comment(self):
      "Testa erro ao enviar comentário de post inexistente"
      response = self.app.post('/blog/comment/teste/Meu_Post_Inexistente', {"comment": ""})
      assert u'Post não encontrado.' in response, "Erro: Não exibiu mensagem de post não encontrado!"

   def test_save_user_comment(self):
      "Testa se um novo comentário foi incluído"
      response = self.app.post('/blog/comment/teste/Meu_Primeiro_Post', FORM_COMMENT).follow()
      assert u'Comentando este post...' in response, "Erro: Não exibiu comentário no POST do usuário!"
      assert "teste/Meu_Primeiro_Post" in model.POSTCOMMENTS.keys(), "Erro: Não incluiu o comentário em POSTCOMMENTS."
   
   
  # -------------------------------------------------------------
  # Alterar posts
  
   def test_edit_post_user_form(self):
      "Testa o formulário de alteração de um post no blog de um usuário"
      response = self.app.get('/blog/edit/teste/Meu_Primeiro_Post')
      assert 'Meu Primeiro Post' in response, "Erro: Não exibiu formulário com título do post!"
      assert 'Conteúdo do meu primeiro Post'  in response, "Erro: Não exibiu formulário com conteúdo do post"
      assert '<script type="text/javascript" src="/static/ckeditor/ckeditor.js"></script>' in response, "Erro: Não chamou o editor"
      
   def test_edit_post_community_form(self):
      "Testa o formulário de alteração de um post no blog de uma comunidade"
      response = self.app.get('/blog/edit/comunidade1/pag1')
      assert 'pag1' in response, "Erro: Não exibiu formulário com título do post!"
      assert 'Página da comunidade 1!!!'  in response, "Erro: Não exibiu formulário com conteúdo do post"
      assert '<script type="text/javascript" src="/static/ckeditor/ckeditor.js"></script>' in response, "Erro: Não chamou o editor"

   def test_reject_edit_post_inexistent_user(self):
      "Testa a edição de post inexistente"
      response = self.app.get('/blog/edit/usuarioinexistente/postinexistente')
      assert 'Usuário ou comunidade inexistentes.' in response, "Erro: Não exibiu mensagem 'post não encontrado'!"
       
   def test_reject_edit_post_unauthorized_user(self):
      "Testa a edição de um post por um usuário não autorizado"
      self.app.post('/login', {"user":"outrousuario", "passwd": "teste", "tipo": "tnm"})       
      response = self.app.get('/blog/edit/teste/Meu_Primeiro_Post')
      assert 'Você não tem permissão para alterar este post.' in response, "Erro: Não exibiu mensagem 'Você não tem permissão para alterar este post.'!"
   
   def test_reject_edit_post_unauthorized_community(self):
      "Testa a edição de um post de comunidade por um usuário que não participa da mesma"
      response = self.app.post('/login', {"user":"outrousuario", "passwd": "teste", "tipo": "tnm"})
      response = self.app.get('/blog/edit/comunidade1/pag1')
      assert u"Você não tem permissão para alterar este post." in response, "Erro: Não exibiu mensagem 'Você não tem permissão para alterar este post.'!"
   
   def test_reject_edit_empty_post(self):
      "Testa erro se o conteúdo do post for vazio"
      post = {}
      post.update(FORM_POST)
      post["conteudo"] = ""
      response = self.app.post('/blog/edit/teste/Meu_Primeiro_Post', post)
      assert u'O conteúdo do Post não pode ser vazio.' in response, "Erro: Não exibiu mensagem 'conteúdo vazio'!"
   
   def test_save_edit_user_post(self):
      "Testa se o post de usuário foi alterado"
      response = self.app.post('/blog/edit/teste/Meu_Primeiro_Post', FORM_POST).follow()
      assert u'um novo post' in response, "Erro: Não exibiu título do POST do usuário!"
      assert u'<b>Este novo post foi incluído agora</b>' in response, "Erro: Não exibiu conteúdo alterado do POST do usuário!"
      assert model.BLOG["teste/Meu_Primeiro_Post"]["titulo"] == u'um novo post', "Erro: Não incluiu o título alterado no banco."
      assert model.BLOG["teste/Meu_Primeiro_Post"]["conteudo"] == u'<b>Este novo post foi incluído agora</b>', "Erro: Não incluiu o conteúdo alterado no banco."
      assert model.BLOG["teste/Meu_Primeiro_Post"]["tags"] == ['riodejaneiro', 'carnaval2010'], "Erro: Não incluiu as tags alteradas no banco."
      assert "teste/Meu_Primeiro_Post" in search.model.SEARCHTAGS["riodejaneiro"]["posts"], "Erro: Não incluiu a tag na tabela de tags"
      assert "teste/Meu_Primeiro_Post" in search.model.SEARCHTAGS["carnaval2010"]["posts"], "Erro: Não incluiu a tag na tabela de tags"

   def test_save_edit_user_post_remove_tag(self):
      "Testa se o post de usuário foi alterado removendo tag"
      self.app.post('/blog/edit/teste/Meu_Primeiro_Post', FORM_POST).follow()
      tags = {}
      tags.update(FORM_POST)
      tags["tags"] = ""
      response = self.app.post('/blog/edit/teste/Meu_Primeiro_Post', tags)
      assert "teste/Meu_Primeiro_Post" not in search.model.SEARCHTAGS["riodejaneiro"]["posts"], "Erro: Não removeu a tag da tabela de tags"
      assert "teste/Meu_Primeiro_Post" not in search.model.SEARCHTAGS["carnaval2010"]["posts"], "Erro: Não removeu a tag da tabela de tags"

  # -------------------------------------------------------------
  # Remover posts
  
   def test_reject_delete_post_unauthorized_user(self):
      "Testa remover um post de outro usuário."
      self.app.post('/login', {"user":"outrousuario", "passwd": "teste", "tipo": "tnm"})       
      response = self.app.get('/blog/delete/teste/Post_a_ser_removido')
      assert 'Você não tem permissão para apagar este post.' in response, "Erro: Não exibiu mensagem 'Você não tem permissão para apagar este post.'!"

   def test_reject_delete_post_unauthorized_community(self):
      "Testa remover um post de comunidade por um usuário que não participa da mesma"
      self.app.post('/login', {"user":"outrousuario", "passwd": "teste", "tipo": "tnm"})       
      response = self.app.get('/blog/delete/comunidade1/pag1')
      assert 'Você não tem permissão para apagar este post.' in response, "Erro: Não exibiu mensagem 'Você não tem permissão para apagar este post.'!"

   def test_reject_delete_incorrect_post(self):
      "Testa erro ao tentar remover post inexistente"
      response = self.app.get('/blog/delete/teste/Meu_Post_Inexistente')
      assert u'Post não encontrado.' in response, "Erro: Não exibiu mensagem de post não encontrado!"

   def test_delete_post_ok(self):
      "Testa exclusão de post"
      response = self.app.get('/blog/delete/teste/Post_a_ser_removido').follow()
      assert u'Post a ser removido' not in response, "Erro: Exibiu título do POST removido!"
      assert "teste/Post_a_ser_removido" not in model.BLOG, "Erro: Não removeu o post no banco."
      assert "teste/Post_a_ser_removido" not in model.REGISTRYBLOG["teste"]["posts"], "Erro: Não removeu o post em REGISTRYBLOG."

   def test_delete_post_remove_tag(self):
      "Testa exclusão de post removendo tag"
      self.app.post('/blog/edit/teste/Meu_Primeiro_Post', FORM_POST).follow()
      response = self.app.get('/blog/delete/teste/Meu_Primeiro_Post').follow()
      assert "teste/Meu_Primeiro_Post" not in search.model.SEARCHTAGS["riodejaneiro"]["posts"], "Erro: Não removeu a tag da tabela de tags"
      assert "teste/Meu_Primeiro_Post" not in search.model.SEARCHTAGS["carnaval2010"]["posts"], "Erro: Não removeu a tag da tabela de tags"


  # -------------------------------------------------------------
  # Remover comentários

   
   def test_reject_delete_comment_unauthorized_user(self):
      "Testa remover um comentário de um post de outro usuário."
      self.app.post('/login', {"user":"outrousuario", "passwd": "teste", "tipo": "tnm"})
      response = self.app.get('/blog/comment/delete?id=92348571b6968741efb07298077d411c')
      assert u'Você não tem permissão para apagar este comentário.' in response, "Erro: Não exibiu mensagem de usuário não autorizado!"

   def test_reject_delete_invalid_comment(self):
      "Testa remover um comentário inexistente."
      response = self.app.get('/blog/comment/delete?id=92348571b69')
      assert u'Comentário não encontrado.' in response, "Erro: Não exibiu mensagem de comentário não encontrado.!"

   def test_delete_comment_by_comment_owner(self):
      "Testa a remoção de um comentário de um post pelo usuário que comentou."
      self.app.post('/login', {"user":"teste2", "passwd": "teste", "tipo": "tnm"})
      response = self.app.get('/blog/comment/delete?id=92348571b6968741efb07298077d411c')
      assert 'comentário a ser removido' not in response, "Erro: Exibiu o comentário removido!"
      assert '92348571b6968741efb07298077d411c' not in model.COMMENT, "Erro: Não removeu o comentário do COMMENT"
      assert '92348571b6968741efb07298077d411c' not in model.POSTCOMMENTS["teste/Meu_Primeiro_Post"]["comments"], "Erro: Não removeu o id do comentário do POSTCOMMENTS"

   def test_delete_comment_by_blog_owner(self):
      "Testa a remoção de um comentário de um post pelo dono do blog."
      response = self.app.get('/blog/comment/delete?id=92348571b6968741efb07298077d411c')
      assert 'comentário a ser removido' not in response, "Erro: Exibiu o comentário removido!"
      assert '92348571b6968741efb07298077d411c' not in model.COMMENT, "Erro: Não removeu o comentário do COMMENT"
      assert '92348571b6968741efb07298077d411c' not in model.POSTCOMMENTS["teste/Meu_Primeiro_Post"]["comments"], "Erro: Não removeu o id do comentário do POSTCOMMENTS"
   