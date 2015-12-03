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

import re
import search.model
import files.model as model
import core.model
import log.model
import unittest


_EMPTYFILES = lambda:dict(
# _id = "registry_id/nome_arquivo"
# _attachments = <conteúdo do arquivo armazenado>
          user = ""           # usuário que fez o upload do arquivo,
                              # esta chave era do bd antigo = owner novo
        , registry_id = ""    # dono do arquivo: usuário ou comunidade
        , owner = ""          # quem fez upload.
                              # caso file seja de uma comunidade, owner!=registry_id
        , filename = ""
        , data_upload = ""
)

_EMPTYREGISTRYFILE = lambda:dict(
# _id = "registry_id"
# permite obter a lista de arquivos de um determinado registry_id.
         files = []          # lista de "registry_id/nomedofile"
)

FILES_DEFAULT = lambda: dict ({
                "comunidade1/teste.txt": {
                "_id": "comuteste2/teste.txt",
                "_rev": "2-2e6789eb36d54b905bdf5f8304a39bf9",
                "owner": "teste1",
                "data_upload": "2011-10-28 17:52:38.106478",
                "registry_id": "comuteste2",
                "user": "",
                "filename": "teste.txt",
                "_attachments": {
                             "teste.txt": {
                                     "content_type": "text/plain",
                                     "revpos": 2,
                                     "length": 99
                                     }
                             }
                },
                "comunidade1/teste.txt": {
                "_id": "comunidade1/teste.txt",
                "_rev": "2-2e6789eb36d54b905bdf5f8304a39bf9",
                "owner": "teste1",
                "data_upload": "2011-10-28 17:52:38.106478",
                "registry_id": "comunidade1",
                "user": "",
                "filename": "teste.txt",
                "_attachments": {
                    "teste.txt": {
                        "content_type": "text/plain",
                        "revpos": 2,
                        "length": 99
                        }
                      }
               },
               "comunidade1/aactchim": {
               "_id": "comunidade1/aactchim",
               "_rev": "2-6658114c784cad2fab1498175b7fc0d9",
               "owner": "teste",
               "data_upload": "2011-10-26 17:16:50.498715",
               "registry_id": "comunidade1",
               "user": "",
               "filename": "",
               "_attachments": {
                   "aactchim": {
                       "content_type": "application/octet-stream",
                       "revpos": 2,
                       "length": 0
                       }
                    }
                },
               "teste/xxx" : {  
               "_id": "marcinha/xxx",
               "_rev": "2-9f3fca2e62bdb32c5ac788eaea4d8063",
               "owner": "teste",
               "data_upload": "2011-10-26 17:41:19.348115",
               "registry_id": "teste",
               "user": "",
               "filename": "xxx",
               "_attachments": {
                   "xxx": {
                       "content_type": "application/octet-stream",
                       "revpos": 2,
                       "length": 47
                       }
                   }
                }
})

FILEREGISTRY_DEFAULT = lambda: dict ({
    "teste" : {
   "_id": "teste",
   "_rev": "1-76ed59005e5b1c0a4bac4432000dd8ac",
   "files": [
       "teste/xxx"
   ]},
    "comunidade1" : {
   "_id": "comunidade1",
   "_rev": "15-7e68a97b1123d926c0336e6d49c75e56",
   "files": [
       "comunidade1/arvore_smb.txt",
       "comunidade1/aactchim",
       "comunidade1/teste.txt"
   ]}
})


REGISTRY_DEFAULT = lambda: dict({
   "comunidade1": {
      "participantes_pendentes": [],
      "description": "comunidade 1",
      "participantes": [
          "teste",
          "teste2"
      ],
      "photo": "",
      "admins": [],
      "owner": "teste",
      "name": "comunidade1",
      "privacidade": "Pública",
      "participacao": "Mediante Convite"
   }            
})

file = {}

#class TestCadastro(mocker.MockerTestCase):
class TestFile(unittest.TestCase):
   """Testes unitários para a wiki"""
   def setUp(self):
      #self.mock = Mocker()
      #MEMBER = self.mock.mock()

      log.model.LOG = {}            
      log.model.NEWS = {}
      model.FILE = FILES_DEFAULT()
      model.REGISTRYFILE = FILEREGISTRY_DEFAULT()
      core.model.REGISTRY = REGISTRY_DEFAULT()
      core.model.MAGKEYS = MAGKEYS_DEFAULT()    # recria chave mágica para que possa fazer outro cadastro
      core.model.INVITES = {}
      core.model.MAGKEYTYPES = {}
      core.model.USERSCHOOL = {}
      
      search.model.SEARCHTAGS = {}  
      log.model.NOTIFICATIONERROR = {}
      log.model.NOTIFICATION = {}
    
      self.app = TestApp(WsgiApp())
      login.update(LOGIN_FORM)
      registry.update(REGISTRY_FORM)
      self.app.post('/new/user', registry)
      registry['user'] = 'teste'
      core.model.MAGKEYS = MAGKEYS_DEFAULT()    # recria chave mágica para que possa fazer outro cadastro  
      self.app.post('/new/user', registry)
      registry['user'] = 'teste2'
      core.model.MAGKEYS = MAGKEYS_DEFAULT()    # recria chave mágica para que possa fazer outro cadastro  
      self.app.post('/new/user', registry)         
      self.app.post('/login', login)
      core.model.MAGKEYS = MAGKEYS_DEFAULT()    # recria chave mágica para que possa fazer outro cadastro  
      
      
   def tearDown(self):
      #self.mock.restore()
      #self.mock.verify()
      #self.mock,MEMBER =None,None
      pass

  # -------------------------------------------------------------
  # Lista arquivos
   
   def test_list_pages_of_user(self):
      "Test show list of files of user teste"  
      #response = self.app.get('/file/teste')
      pass

#   def test_list_pages_of_community(self):
#      "Test show list of communidade1 Wiki pages"      
#      response = self.app.get('/wiki/comunidade1')
#      #assert 'comunidade1' in response, "Erro: Não exibiu lista de páginas Wiki da comunidade!"
#      assert 'comunidade1/pag1' in response, "Erro: Não exibiu link para a primeira páginas Wiki da comunidade!"
#      assert 'comunidade1/pag2' in response, "Erro: Não exibiu link para a segunda página Wiki da comunidade!"
#      
#   def test_list_pages_of_incorrect_user(self):
#      "Testa a lista de páginas Wiki de um usuário/comunidade inexistente"      
#      response = self.app.get('/wiki/usuario_inexistente')
#      assert 'Usuário ou comunidade inexistentes.' in response, "Erro: Não exibiu mensagem de usuário inexistente!"
#
#   def test_empty_list_of_pages(self):
#      "Testa uma lista de páginas vazia de usuário/comunidade"      
#      response = self.app.get('/wiki/teste2')
#      assert '<p>teste2 ainda não possui nenhuma página.</p>' in response, "Erro: Não exibiu mensagem de páginas não encontradas!"

#  # -------------------------------------------------------------
#  # Criação de páginas Wiki
#
#   def test_create_user_home_page(self):
#      "Verifica se a página inicial do usuário teste foi criada automaticamente no primeiro acesso"      
#      self.app.get('/wiki/teste/home')
#      assert 'teste/home' in model.WIKI, "Erro: Não criou página inicial do usuário!"
#       
#   def test_create_community_home_page(self):
#      "Verifica se a página inicial de uma comunidade foi criada automaticamente no primeiro acesso"      
#      self.app.get('/wiki/comunidade1/home')
#      assert 'comunidade1/home' in model.WIKI, "Erro: Não criou página inicial da comunidade!"
#    
#   def test_reject_new_page_of_incorrect_user(self):
#      "Testa a criação de páginas Wiki de um usuário/comunidade inexistente"      
#      response = self.app.get('/wiki/newpage/usuario_inexistente')
#      assert 'Usuário ou comunidade inexistentes.' in response, "Erro: Não exibiu mensagem de usuário inexistente!"
#  
#   def test_reject_new_page_unauthorized_user(self):
#      "Testa o formulário de criação de uma página nova para um outro usuário"
#      response = self.app.get('/wiki/newpage/teste2')
#      assert '<div class="tnmMSG">Você não tem permissão para criar página aqui.</div>' in response, "Erro: Não exibiu mensagem de falta de permissão!"
#
#   def test_reject_new_community_page_unauthorized_user(self):
#      "Testa o formulário de criação de uma página nova para uma comunidade que o usuário não participa"
#      self.app.post('/login', {"user":"teste3", "passwd": "teste", "tipo": "tnm"})       
#      response = self.app.get('/wiki/newpage/comunidade1')
#      assert '<div class="tnmMSG">Você não tem permissão para criar página aqui.</div>' in response, "Erro: Não exibiu mensagem de falta de permissão!"
#
#   def test_create_new_wiki_form(self):
#      "Testa o formulário de criação de uma página pessoal"
#      response = self.app.get('/wiki/newpage/teste')
#      assert u'<h2>Nome da página:</h2>'  in response, "Erro: Não exibiu pedido de nome da página!"
#      assert 'Conteúdo:'  in response, "Erro: Não exibiu pedido de entrar conteúdo"
#      assert '<script type="text/javascript" src="/static/ckeditor/ckeditor.js"></script>' in response, "Erro: Não chamou o editor"
#      assert 'Todos os participantes da comunidade podem alterar esta página.' not in response, "Erro: incluiu campo edicao_publica numa página pessoal"
#
#   def test_create_new_wiki_community_form(self):
#      "Testa o formulário de criação de uma página de comunidade"
#      response = self.app.get('/wiki/newpage/comunidade1')
#      assert u'<h2>Nome da página:</h2>'  in response, "Erro: Não exibiu pedido de nome da página!"
#      assert 'Conteúdo:'  in response, "Erro: Não exibiu pedido de entrar conteúdo"
#      assert '<script type="text/javascript" src="/static/ckeditor/ckeditor.js"></script>' in response, "Erro: Não chamou o editor"
#      assert 'Todos os participantes da comunidade podem alterar esta página.' in response, "Erro: não incluiu campo edicao_publica numa página pessoal"
#
#   def test_save_user_page(self):
#      "Testa se uma nova página de usuário foi incluída"
#      response = self.app.post('/wiki/newpage/teste', pagina).follow()
#      assert u'<b> Meu texto novinho </b>' in response, "Erro: Não exibiu conteúdo da página incluída!"
#      #assert u'riodejaneiro' in response, "Erro: Não exibiu a tag da página incluída!"
#      #assert u'carnaval2010' in response, "Erro: Não exibiu a tag da página incluída!"
#      #assert u'<span class="tooltip">Editar página.</span>' in response, "Erro: Não exibiu botão para editar página!"
#      assert 'teste/minha_pag_novinha' in model.WIKI, "Erro: Não incluiu a página!"
#      assert 'teste/minha_pag_novinha' in model.REGISTRYWIKI["teste"]["paginas"], "Erro: Não incluiu a página no REGISTRYWIKI!"
#      assert 'teste/minha_pag_novinha' in search.model.SEARCHTAGS['riodejaneiro']['paginas'], "Erro: Não incluiu a tag na tabela de tags"
#      assert 'teste/minha_pag_novinha' in search.model.SEARCHTAGS['carnaval2010']['paginas'], "Erro: Não incluiu a tag na tabela de tags"
#
#   def test_save_user_diacritics_page(self):
#      "Testa se uma nova página com acentos foi incluída"
#      pagina = WIKI_FORM_COM_ACENTOS()
#      response = self.app.post('/wiki/newpage/teste', pagina).follow()
#      assert u'<b> Meu texto novinho </b>' in response, response #"Erro: Não exibiu conteúdo da página incluída!"
#      #assert u'riodejaneiro' in response, "Erro: Não exibiu a tag da página incluída!"
#      #assert u'carnaval2010' in response, "Erro: Não exibiu a tag da página incluída!"
#      #assert u'<span class="tooltip">Editar página.</span>' in response, "Erro: Não exibiu botão para editar página!"
#      assert u'teste/Atenção_Nome_com_Acentos' in model.WIKI, "Erro: Não incluiu a página!"
#      assert u'teste/Atenção_Nome_com_Acentos' in model.REGISTRYWIKI["teste"]["paginas"], "Erro: Não incluiu a página no REGISTRYWIKI!"
#
#   def test_reject_user_page_with_special_chars(self):
#      "Testa se uma nova página de usuário foi incluída"
#      pagina = WIKI_FORM_COM_INVALIDOS()
#      response = self.app.post('/wiki/newpage/teste', pagina)
#      assert u'Nome inválido' in response, "Erro: Não exibiu mensagem de nome inválido!"
#
#   def test_save_community_page(self):
#      "Testa se uma nova página de comunidade foi incluída"
#      response = self.app.post('/wiki/newpage/comunidade1', pagina).follow()
#      assert u'<b> Meu texto novinho </b>' in response, "Erro: Não exibiu conteúdo da página incluída!"
#      #assert u'riodejaneiro' in response, "Erro: Não exibiu a tag da página incluída!"
#      #assert u'carnaval2010' in response, "Erro: Não exibiu a tag da página incluída!"
#      #assert u'<span class="tooltip">Editar página.</span>' in response, "Erro: Não exibiu botão para editar página!"
#      assert 'comunidade1/minha_pag_novinha' in model.WIKI, response #"Erro: Não incluiu a página!"
#      assert 'comunidade1/minha_pag_novinha' in model.REGISTRYWIKI["comunidade1"]["paginas"], "Erro: Não incluiu a página no REGISTRYWIKI!"
#      assert 'comunidade1/minha_pag_novinha' in search.model.SEARCHTAGS['riodejaneiro']['paginas'], "Erro: Não incluiu a tag na tabela de tags"
#      assert 'comunidade1/minha_pag_novinha' in search.model.SEARCHTAGS['carnaval2010']['paginas'], "Erro: Não incluiu a tag na tabela de tags"
#
#
#  # -------------------------------------------------------------
#  # Alteração de páginas Wiki
#    
#   def test_reject_edit_wiki_incorrect_user(self):
#      "Testa formulário de alteração de uma página para um usuário inexistente"
#      response = self.app.get('/wiki/usario_inexistente/minha_pagina/edit')  
#      assert u'Usuário ou comunidade inexistentes.' in response, "Erro: Não exibiu mensagem de usuário ou comunidade inexistente!"
#
#   def test_reject_edit_wiki_user_page_form(self):
#      "Testa formulário de alteração de uma página por um outro usuário"
#      registry["user"] = "outro_user"
#      response = self.app.post('/new/user', registry)
#      login["user"] = "outro_user"      
#      self.app.post('/login', login)        
#      response = self.app.get('/wiki/teste/minha_pagina/edit')  
#      assert u'<div class="tnmMSG">Você não tem permissão para alterar esta página.</div>' in response, "Erro: Não exibiu mensagem de erro de permissão!"
#   
#   def test_edit_wiki_user_page_form(self):
#      "Testa formulário de alteração de uma página"
#      response = self.app.get('/wiki/teste/minha_pagina/edit')  
#      assert u'<h2>Nome da página:</h2>minha_pagina' in response, "Erro: Não exibiu o formulário para editar página de usuário!"
#      assert u'Meu novo texto total' in response, "Erro: Não exibiu o conteúdo da página"
#   
#   def test_edit_wiki_page(self):
#      "Testa alteração de uma página"
#      pagina=WIKI_FORM()
#      response = self.app.post('/wiki/teste/minha_pagina/edit', pagina_alterada).follow()
#      assert u'<b> Meu texto alterado </b>' in response, "Erro: Não exibiu o texto alterado pela edição da página!"
#      #assert u'saopaulo' in response, "Erro: Não exibiu a tag alterada pela edição da página!"
#      assert model.WIKI["teste/minha_pagina"]["conteudo"] == u'<b> Meu texto alterado </b>', "Erro: Não incluiu o conteúdo alterado no banco."
#      assert model.WIKI["teste/minha_pagina"]["tags"] == ['saopaulo'], "Erro: Não incluiu as tags alteradas no banco."
#      assert 'teste/minha_pagina' in search.model.SEARCHTAGS['saopaulo']['paginas'], "Erro: Não incluiu a tag na tabela de tags"
#
#   def test_edit_wiki_page_concorrente(self):
#      "Testa alteração de uma página se outro usuario alterou primeiro"
#      pagina_alterada_outro_usu["_rev"]="543"
#      response = self.app.post('/wiki/teste/minha_pagina/edit', pagina_alterada_outro_usu)
#      #assert u"Conflito" in response, response
#      #pagina_alterada_outro_usu["_rev"]="1234"
#      #pagina_alterada_outro_usu["revision"] = "1234567"
#      #response = self.app.post('/wiki/teste/minha_pagina/edit', pagina_alterada_outro_usu).follow()
#      assert u'Conflito ao salvar o documento. Enquanto você editava-o, ele foi alterado por outro usuário.' in response, "Erro: Não exibiu mensagem sobre conflito na alteracao"
#        
#   def test_edit_wiki_page_remove_tag(self):
#      "Testa alteração de uma página removendo tag"
#      response = self.app.post('/wiki/teste/minha_pagina/edit', pagina_alterada).follow()
#      pagina_alterada["tags"] = ""
#      response = self.app.post('/wiki/teste/minha_pagina/edit', pagina_alterada).follow()
#      assert 'teste/minha_pagina' not in search.model.SEARCHTAGS['saopaulo']['paginas'], "Erro: Não removeu a tag da tabela de tags"
#
#   def test_edit_wiki_community_page1_by_owner_form(self):
#      "Testa formulário de alteração de uma página de comunidade pelo dono da mesma"
#      response = self.app.get('/wiki/comunidade1/pag1/edit')  
#      assert u'<h2>Nome da página:</h2>pag1' in response, "Erro: Não exibiu o formulário para editar página de comunidade!"
#   
#   def test_edit_wiki_community_page2_by_owner_form(self):
#      "Testa formulário de alteração de uma página de comunidade por um membro da mesma"
#      response = self.app.get('/wiki/comunidade1/pag2/edit')  
#      assert u'<h2>Nome da página:</h2>pag2' in response, "Erro: Não exibiu o formulário para editar página de comunidade!"
#
#   def test_edit_wiki_community_page3_by_owner_form(self):
#      "Testa formulário de alteração de uma página de comunidade pelo seu dono"
#      response = self.app.get('/wiki/comunidade1/pag3/edit')  
#      assert u'<h2>Nome da página:</h2>pag3' in response, "Erro: Não exibiu o formulário para editar página de comunidade!"
#      
#   def test_reject_wiki_community_page1_by_member_form(self):
#      "Testa formulário de alteração de uma página de comunidade por um não membro"
#      registry["user"] = "teste2"
#      response = self.app.post('/new/user', registry)
#      login["user"] = "teste2"      
#      self.app.post('/login', login)
#      response = self.app.get('/wiki/comunidade1/pag1/edit')  
#      assert u'<div class="tnmMSG">Você não tem permissão para alterar esta página.</div>' in response, "Erro: Não exibiu mensagem de erro de permissão!"
#   
#   def test_edit_wiki_community_page2_by_member_form(self):
#      "Testa formulário de alteração de uma página de comunidade por um membro da mesma que é o criador da página"
#      registry["user"] = "teste2"
#      response = self.app.post('/new/user', registry)
#      login["user"] = "teste2"      
#      self.app.post('/login', login)
#      response = self.app.get('/wiki/comunidade1/pag2/edit')  
#      assert u'<h2>Nome da página:</h2>pag2' in response, response #"Erro: Não exibiu o formulário para editar página de comunidade!"
#   
#   def test_edit_wiki_community_page3_by_member_form(self):
#      "Testa formulário de alteração de uma página de comunidade que possui permissão para ser editado publicamente"
#      registry["user"] = "teste2"
#      response = self.app.post('/new/user', registry)
#      login["user"] = "teste2"      
#      self.app.post('/login', login)
#      response = self.app.get('/wiki/comunidade1/pag3/edit')  
#      assert u'<h2>Nome da página:</h2>pag3' in response, "Erro: Não exibiu o formulário para editar página de comunidade!"
#   
#   def test_reject_edit_wiki_community_page1_by_notmember_form(self):
#      "Testa formulário de alteração de uma página de comunidade por um usuário não membro"
#      registry["user"] = "outro_user"
#      response = self.app.post('/new/user', registry)
#      login["user"] = "outro_user"      
#      self.app.post('/login', login)        
#      response = self.app.get('/wiki/comunidade1/pag1/edit')  
#      assert u'<div class="tnmMSG">Você não tem permissão para alterar esta página.</div>' in response, "Erro: Não exibiu mensagem de erro de permissão!"
#      
#   def test_reject_edit_wiki_community_page2_by_notmember_form(self):
#      "Testa formulário de alteração de uma página de comunidade por um usuário não membro"
#      registry["user"] = "outro_user"
#      response = self.app.post('/new/user', registry)
#      login["user"] = "outro_user"      
#      self.app.post('/login', login)        
#      response = self.app.get('/wiki/comunidade1/pag2/edit')  
#      assert u'<div class="tnmMSG">Você não tem permissão para alterar esta página.</div>' in response, "Erro: Não exibiu mensagem de erro de permissão!"
#
#   def test_reject_edit_wiki_community_page3_by_notmember_form(self):
#      "Testa formulário de alteração de uma página de comunidade por um usuário não membro"
#      registry["user"] = "outro_user"
#      response = self.app.post('/new/user', registry)
#      login["user"] = "outro_user"      
#      self.app.post('/login', login)        
#      response = self.app.get('/wiki/comunidade1/pag3/edit')  
#      assert u'<div class="tnmMSG">Você não tem permissão para alterar esta página.</div>' in response, "Erro: Não exibiu mensagem de erro de permissão!"
#
#  # -------------------------------------------------------------
#  # Remoção de páginas Wiki
#
#   def test_reject_edit_wiki_incorrect_user(self):
#      "Testa remoção de uma página para um usuário/comunidade inexistente"
#      response = self.app.get('/wiki/delete/usario_inexistente/minha_pagina')  
#      assert u'Usuário ou comunidade inexistentes.' in response, "Erro: Não exibiu mensagem de usuário ou comunidade inexistentes!"
#  
#   def test_delete_wiki_page_success(self):
#      "Testa apagar uma página"
#      response = self.app.get('/wiki/delete/teste/delete_pagina')
#      #assert u'Página apagada com sucesso.' in response, response #"Erro: Não exibiu mensagem de página apagada com sucesso!"
#      assert 'teste/delete_pagina' not in model.WIKI, "Erro: Não apagou a página do WIKI!"
#      assert 'teste/delete_pagina' not in model.REGISTRYWIKI['teste']['paginas'], "Erro: Não apagou a página do WIKIREGISTRY!"
#
#   def test_delete_wiki_page_remove_tag(self):
#      "Testa apagar uma página removendo tag"
#      response = self.app.post('/wiki/teste/minha_pagina/edit', pagina_alterada).follow()
#      response = self.app.get('/wiki/delete/teste/minha_pagina')
#      assert 'teste/minha_pagina' not in search.model.SEARCHTAGS['saopaulo']['paginas'], "Erro: Não removeu a tag da tabela de tags"
#
#   def test_delete_wiki_page_fail_not_found(self):
#      "Testa falha ao apagar uma página: não existe"
#      response = self.app.get('/wiki/delete/teste/delete_pagina_nao_existe')
#      assert u'Página não encontrada.' in response, "Erro: Não exibiu mensagem de página não encontrada!"
#      assert 'teste/delete_pagina_nao_existe' not in model.WIKI, "Erro: Página existe no BD!"
#
#   def test_delete_wiki_user_page_fail_not_owner(self):
#      "Testa formulário de exclusão de uma página de usuário"
#      registry["user"] = "outro_user"
#      response = self.app.post('/new/user', registry)
#      login["user"] = "outro_user"      
#      self.app.post('/login', login)        
#      response = self.app.get('/wiki/delete/teste/minha_pagina')  
#      assert u'Você não tem permissão para remover esta página.' in response, "Erro: Não exibiu mensagem de erro de permissão!"
#
#   def test_delete_wiki_community_page_fail_not_owner(self):
#      "Testa formulário de exclusão de uma página de comunidade"
#      registry["user"] = "outro_user"
#      response = self.app.post('/new/user', registry)
#      login["user"] = "outro_user"      
#      self.app.post('/login', login)        
#      response = self.app.get('/wiki/delete/comunidade1/pag1')  
#      assert u'Você não tem permissão para remover esta página.' in response, "Erro: Não exibiu mensagem de erro de permissão!"
#
#  # -------------------------------------------------------------
#  # Exibição de páginas Wiki
#
#   def test_reject_show_wiki_page_incorrect_user(self):
#      "Testa exibição de uma página para um usuário/comunidade inexistente"
#      response = self.app.get('/wiki/usuario_inexistente/minha_pagina')  
#      assert u'Usuário ou comunidade inexistentes.' in response, "Erro: Não exibiu mensagem de usuário ou comunidade inexistentes!"
#      
#   def test_reject_show_wiki_page_incorrect_page(self):
#      "Testa exibição de uma página  inexistente"
#      response = self.app.get('/wiki/teste/minha_pagina_inexistente')  
#      assert u'Página não encontrada.' in response, "Erro: Não exibiu mensagem de página não encontrada!"
#
#   def test_show_wiki_page(self):
#      "Testa exibição de uma página de usuário/comunidade"
#      response = self.app.get('/wiki/teste/minha_pagina')  
#      assert u'Meu novo texto total' in response, "Erro: Não exibiu conteúdo da página!"
#
#   def test_show_wiki_home_page(self):
#      "Testa exibição de uma página inicial de usuário/comunidade"
#      response = self.app.get('/wiki/teste/home')  
#      assert u'Página inicial do Usuário' in response, "Erro: Não exibiu conteúdo da página inicial de teste!"
#
#   def test_show_create_wiki_home_page(self):
#      "Testa a criação e exibição de uma página inicial de usuário/comunidade"
#      response = self.app.get('/wiki/teste2/home')  
#      assert u'Página inicial de [teste2].' in response, "Erro: Não exibiu conteúdo da página inicial de teste2!"
#      assert u'teste2/home' in model.WIKI, "Erro: Não incluiu a página home!"
#      assert u'teste2/home' in model.REGISTRYWIKI["teste2"]["paginas"], "Erro: Não incluiu a página home no REGISTRYWIKI!"
#
## -------------------------------------------------------------
#  # Portfolio de comunidade
#  
#   def test_list_pages_of_community(self):
#      "Testa a exibicao do portfolio de uma comunidade"      
#      response = self.app.get('/wiki/portfolio/comunidade1')
#      #assert '<p>Páginas da Comunidade comunidade1:' in response, response #"Erro: Não exibiu lista de páginas Wiki da comunidade!"
#      assert 'comunidade1/pag1' in response, "Erro: Não exibiu link para a primeira páginas Wiki da comunidade!"
#      assert 'Primeira página da comunidade 1!!!' in response, "Erro: Não exibiu conteudo da primeira página Wiki da comunidade!"
#      assert 'comunidade1/pag2' in response, "Erro: Não exibiu link para a segunda página Wiki da comunidade!"
#      assert 'Segunda página da comunidade 1!!!' in response, "Erro: Não exibiu conteudo da segunda página Wiki da comunidade!"
   