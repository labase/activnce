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
import log.model
import unittest

LOGIN_FORM_AMIGO = { "user":"amigo1", "passwd": "teste" }

NEWS_EXTRA = {
        "teste": {
            "avisos": [
               {
                   "sujeito": "teste1",
                   "objeto": "teste1",
                   "data_inclusao": "2010-10-27 13:57:46.402923",
                   "tipo": "mblog",
                   "verbo": "postou no mblog"
               },
               {
                   "sujeito": "teste2",
                   "objeto": "teste2",
                   "data_inclusao": "2010-10-27 13:57:46.402923",
                   "tipo": "mblog",
                   "verbo": "postou no mblog"
               },
               {
                   "sujeito": "teste3",
                   "objeto": "teste3",
                   "data_inclusao": "2010-10-27 13:57:46.402923",
                   "tipo": "mblog",
                   "verbo": "postou no mblog"
               },
               {
                   "sujeito": "teste4",
                   "objeto": "teste4",
                   "data_inclusao": "2010-10-27 13:57:46.402923",
                   "tipo": "mblog",
                   "verbo": "postou no mblog"
               },
               {
                   "sujeito": "teste5",
                   "objeto": "teste5",
                   "data_inclusao": "2010-10-27 13:57:46.402923",
                   "tipo": "mblog",
                   "verbo": "postou no mblog"
               },
               {
                   "sujeito": "teste6",
                   "objeto": "teste6",
                   "data_inclusao": "2010-10-27 13:57:46.402923",
                   "tipo": "mblog",
                   "verbo": "postou no mblog"
               },
               {
                   "sujeito": "teste7",
                   "objeto": "teste7",
                   "data_inclusao": "2010-10-27 13:57:46.402923",
                   "tipo": "mblog",
                   "verbo": "postou no mblog"
               },
               {
                   "sujeito": "teste8",
                   "objeto": "teste8",
                   "data_inclusao": "2010-10-27 13:57:46.402923",
                   "tipo": "mblog",
                   "verbo": "postou no mblog"
               },
               {
                   "sujeito": "teste9",
                   "objeto": "teste9",
                   "data_inclusao": "2010-10-27 13:57:46.402923",
                   "tipo": "mblog",
                   "verbo": "postou no mblog"
               },
               {
                   "sujeito": "teste10",
                   "objeto": "teste10",
                   "data_inclusao": "2010-10-27 13:57:46.402923",
                   "tipo": "mblog",
                   "verbo": "postou no mblog"
               },
               {
                   "sujeito": "teste11",
                   "objeto": "teste11",
                   "data_inclusao": "2010-10-27 13:57:46.402923",
                   "tipo": "mblog",
                   "verbo": "postou no mblog"
               },
               {
                   "sujeito": "teste12",
                   "objeto": "teste12",
                   "data_inclusao": "2010-10-27 13:57:46.402923",
                   "tipo": "mblog",
                   "verbo": "postou no mblog"
               },
               {
                   "sujeito": "teste13",
                   "objeto": "teste13",
                   "data_inclusao": "2010-10-27 13:57:46.402923",
                   "tipo": "mblog",
                   "verbo": "postou no mblog"
               },
               {
                   "sujeito": "teste14",
                   "objeto": "teste14",
                   "data_inclusao": "2010-10-27 13:57:46.402923",
                   "tipo": "mblog",
                   "verbo": "postou no mblog"
               },
               {
                   "sujeito": "teste15",
                   "objeto": "teste15",
                   "data_inclusao": "2010-10-27 13:57:46.402923",
                   "tipo": "mblog",
                   "verbo": "postou no mblog"
               },
               {
                   "sujeito": "teste16",
                   "objeto": "teste16",
                   "data_inclusao": "2010-10-27 13:57:46.402923",
                   "tipo": "mblog",
                   "verbo": "postou no mblog"
               },
               {
                   "sujeito": "teste17",
                   "objeto": "teste17",
                   "data_inclusao": "2010-10-27 13:57:46.402923",
                   "tipo": "mblog",
                   "verbo": "postou no mblog"
               },
               {
                   "sujeito": "teste18",
                   "objeto": "teste18",
                   "data_inclusao": "2010-10-27 13:57:46.402923",
                   "tipo": "mblog",
                   "verbo": "postou no mblog"
               },
               {
                   "sujeito": "teste19",
                   "objeto": "teste19",
                   "data_inclusao": "2010-10-27 13:57:46.402923",
                   "tipo": "mblog",
                   "verbo": "postou no mblog"
               },
               {
                   "sujeito": "teste20",
                   "objeto": "teste20",
                   "data_inclusao": "2010-10-27 13:57:46.402923",
                   "tipo": "mblog",
                   "verbo": "postou no mblog"
               },
               {
                   "sujeito": "teste21",
                   "objeto": "teste21",
                   "data_inclusao": "2010-10-27 13:57:46.402923",
                   "tipo": "mblog",
                   "verbo": "postou no mblog"
               },
               {
                   "sujeito": "teste22",
                   "objeto": "teste22",
                   "data_inclusao": "2010-10-27 13:57:46.402923",
                   "tipo": "mblog",
                   "verbo": "postou no mblog"
               },
               {
                   "sujeito": "teste23",
                   "objeto": "teste23",
                   "data_inclusao": "2010-10-27 13:57:46.402923",
                   "tipo": "mblog",
                   "verbo": "postou no mblog"
               },
               {
                   "sujeito": "teste24",
                   "objeto": "teste24",
                   "data_inclusao": "2010-10-27 13:57:46.402923",
                   "tipo": "mblog",
                   "verbo": "postou no mblog"
               },
               {
                   "sujeito": "teste25",
                   "objeto": "teste25",
                   "data_inclusao": "2010-10-27 13:57:46.402923",
                   "tipo": "mblog",
                   "verbo": "postou no mblog"
               }
            ]
        }
}

#class TestAmigo(mocker.MockerTestCase):
class TestAmigo(unittest.TestCase):
  """Testes unitários para o gerenciamento de amigos"""
  def setUp(self):
    #self.mock = Mocker()
    #MEMBER = self.mock.mock()
    
    core.model.REGISTRY = {}
    core.model.MAGKEYS = MAGKEYS_DEFAULT()    # recria chave mágica para que possa fazer outro cadastro  
    core.model.INVITES = {}
    core.model.MAGKEYTYPES = {}
    core.model.USERSCHOOL = {}    
      
    log.model.LOG = {}
    log.model.NEWS = {}
    wiki.model.WIKI = {}
    wiki.model.WIKIMEMBER = {}
    wiki.model.WIKICOMMUNITY = {}
    log.model.NOTIFICATIONERROR = {}
    log.model.NOTIFICATION = {}
    
    self.app = TestApp(WsgiApp())
    registry.update(REGISTRY_FORM)
    self.app.post('/new/user', registry)
    registry['user'] = 'amigo1'
    core.model.MAGKEYS = MAGKEYS_DEFAULT()    # recria chave mágica para que possa fazer outro cadastro  
    
    self.app.post('/new/user', registry)
    login.update(LOGIN_FORM)
    self.app.post('/login', login)

  def tearDown(self):
    #self.mock.restore()
    #self.mock.verify()
    #self.mock,MEMBER =None,None
    pass

  def test_returns_empty_news_list(self):
    "Retorna página de novidades vazia"
    response = self.app.get('/news/teste')
    assert u'Não há novidades para teste.' in response, "Erro: Não exibiu mensagem de novidades inexistentes!"
  
  def test_returns_news_list(self):
    "Retorna página de novidades"
    self.app.get('/newfriend?friend=amigo1')
    login.update(LOGIN_FORM_AMIGO)
    self.app.post('/login', login) # login como amigo1
    self.app.get('/acceptfriend/teste') # teste é amigo de amigo1
    response = self.app.get('/news/teste')
    #assert u'Novidades para teste:' in response, "Erro: Não produziu aviso para o usuário!"
    #assert log.model.TEMP_NEWS["amigo1"]["avisos"][0]["sujeito"]=="amigo1", "Erro: não avisou amigo1. não gravou campo sujeito"
    #assert log.model.TEMP_NEWS["amigo1"]["avisos"][0]["verbo"]==u"começou uma amizade com", "Erro: não avisou amigo1. não gravou campo verbo"
    #assert log.model.TEMP_NEWS["amigo1"]["avisos"][0]["objeto"]=="teste", "Erro: não avisou amigo1. não gravou campo objeto"
    assert log.model.TEMP_NEWS["teste"]["avisos"][0]["sujeito"]=="amigo1", "Erro: não avisou teste. não gravou campo sujeito"
    assert log.model.TEMP_NEWS["teste"]["avisos"][0]["verbo"]==u"começou uma amizade com", "Erro: não avisou teste. não gravou campo verbo"
    assert log.model.TEMP_NEWS["teste"]["avisos"][0]["objeto"]=="teste", "Erro: não avisou teste. não gravou campo objeto"

  def test_list_of_news_page(self):
    "Testa a exibição da lista de novidades paginada"
    log.model.NEWS = NEWS_EXTRA
    response = self.app.get('/news/teste?pag=1')
    assert "teste1" in response, "Erro: Não exibiu mensagem Notícia (teste1)"
    assert "teste2" in response, "Erro: Não exibiu mensagem Notícia (teste2)"
    assert "teste3" in response, "Erro: Não exibiu mensagem Notícia (teste3)"
    assert "teste4" in response, "Erro: Não exibiu mensagem Notícia (teste4)"
    assert "teste5" in response, "Erro: Não exibiu mensagem Notícia (teste5)"
    assert "teste6" in response, "Erro: Não exibiu mensagem Notícia (teste6)"
    assert "teste7" in response, "Erro: Não exibiu mensagem Notícia (teste7)"
    assert "teste8" in response, "Erro: Não exibiu mensagem Notícia (teste8)"
    assert "teste9" in response, "Erro: Não exibiu mensagem Notícia (teste9)"
    assert "teste10" in response, "Erro: Não exibiu mensagem Notícia (teste10)"
    assert "teste11" in response, "Erro: Não exibiu mensagem Notícia (teste11)"
    assert "teste12" in response, "Erro: Não exibiu mensagem Notícia (teste12)"
    assert "teste13" in response, "Erro: Não exibiu mensagem Notícia (teste13)"
    assert "teste14" in response, "Erro: Não exibiu mensagem Notícia (teste14)"
    assert "teste15" in response, "Erro: Não exibiu mensagem Notícia (teste15)"
    assert "teste16" in response, "Erro: Não exibiu mensagem Notícia (teste16)"
    assert "teste17" in response, "Erro: Não exibiu mensagem Notícia (teste17)"
    assert "teste18" in response, "Erro: Não exibiu mensagem Notícia (teste18)"
    assert "teste19" in response, "Erro: Não exibiu mensagem Notícia (teste19)"
    assert "teste20" in response, "Erro: Não exibiu mensagem Notícia (teste20)"
    assert '<a href="?pag=2">2' in response, "Erro: Não mostrou o link para a página(2)"
    response = self.app.get('/news/teste?pag=2')
    assert "teste21" in response, "Erro: Não exibiu mensagem Notícia (teste21)"
    assert "teste22" in response, "Erro: Não exibiu mensagem Notícia (teste22)"
    assert "teste23" in response, "Erro: Não exibiu mensagem Notícia (teste23)"
    assert "teste24" in response, "Erro: Não exibiu mensagem Notícia (teste24)"
    assert "teste25" in response, "Erro: Não exibiu mensagem Notícia (teste25)"
    assert '<a href="?pag=1">1' in response, "Erro: Não mostrou o link para a página(1)"

  def test_list_of_news_page_not_found(self):
    "Testa a exibição da mensagem de erro de página não encontrada"
    log.model.NEWS = NEWS_EXTRA
    response = self.app.get('/news/teste?pag=0')
    assert u"Número de página não encontrado" in response, "Erro: Não exibiu mensagem 'Número de página não encontrado' (pag 0)"
    response = self.app.get('/news/teste?pag=-1')
    assert u"Número de página não encontrado" in response, "Erro: Não exibiu mensagem 'Número de página não encontrado' (pag -1)"
    response = self.app.get('/news/teste?pag=10')
    assert u"Número de página não encontrado" in response, "Erro: Não exibiu mensagem 'Número de página não encontrado' (pag 10)"
