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

from datetime import datetime
import core.model
import unittest

REGISTRY_DEFAULT = lambda: dict ({
   "mauricio": {
      "user" : "mauricio"
      , "passwd" : "41b9f25030b0ef830fd47d450c714e79"
      , "name" : u"Maurício"
      , "lastname" : "Bonfim"
      , "email" : "mauricio@nce.ufrj.br"
      , "tags" : [
            "python",
            "nce",
            "web"
         ] 
      , "description" : "Desenvolvedor da plataforma OITONOMUNDO."        
      , "photo" : ""
      , "cod_institute" : "0002"
      , "institute" : u"Núcleo de Computação Eletrônica"
      , "amigos" : [
                     "julianne",
                     "tomasbomfim",
                     "livia",
                     "marcinha"
                  ]
      , "amigos_pendentes" : []
      , "amigos_convidados" : [
                                 "roberta",
                                 "Angela"
                              ]
      , "comunidades" : [
                           "q2q2",
                           "PRIV_SUPORTE_ACTIV",
                           "com1",
                           "Priv_Consultar_Cadastro",
                           "testeObrigatoria",
                           "xxxxx",
                           "qqqq",
                           "Comu_voluntaria",
                           "zzzz",
                           "BCBS",
                           "cteste",
                           "Priv_Suporte_Educopedia",
                           "etert345rtert",
                           "nova_comunidade",
                           "9999_1201_MAT_2010",
                           "tnm",
                           "comun_do_aluno_5",
                           "0002_88_EDF_2010",
                           "proj_comunitario",
                           "comunidade_priv",
                           "hjjk",
                           "9999_1202_MAT_2010",
                           "DevTnM",
                           "Alunos_de_mauricio2",
                           "qweqwe",
                           "0002_1202_LPT_2010",
                           "asdasdqweqwe",
                           "ComunidadeAluno"
                        ]
      , "comunidades_pendentes" : [
                                    "nova_Comu",
                                    "comu_publica" 
                                 ]
      , "papeis" : [
                     "admin",
                     "tnm",
                     "educo",
                     "digitador",
                     "professor",
                     "gestor",
                     "super_usuario"
                  ]   # serve tb para definir se o usuário é "tnm" ou "educo"
      , "mykeys" : [
                     "a0002tF0aUOfRB9PHx4iCX2Xv7fSN",
                     "p0002OpAmkvPr2AHbSbV4pR1N3WDk",
                     "p01086bLuF1wO47d4zpzCVxebpY7w",
                     "p01279PkiLIgVoWb5vaI4x4v2PD3R"        
                  ]
      , "privacidade" : u"Pública"           # Pública ou Privada
      , "upload_quota" : 10 * 1024 * 1024    # max 10 Mb
      , "upload_size" : 0
   },
   "julianne": {
      "user" : "julianne"
      , "passwd" : "41b9f25030b0ef830fd47d450c714e79"
      , "name" : "Julianne"
      , "lastname" : "de Carvalho"
      , "email" : "juliannedecarvalho@gmail.com"
      , "tags" : [] 
      , "description" : ""        
      , "photo" : ""
      , "cod_institute" : "9999"
      , "institute" : u"Não informada"
      , "amigos" : [
                     "mauricio",
                     "livia",
                     "marcinha",
                  ]
      , "amigos_pendentes" : []
      , "amigos_convidados" : []
      , "comunidades" : [
                           "Design",
                           "DevTnM"
                        ]
      , "comunidades_pendentes" : []
      , "papeis" : [
                     "tnm"
         ]   # serve tb para definir se o usuário é "tnm" ou "educo"
      , "mykeys" : []
      , "privacidade" : u"Pública"           # Pública ou Privada
      , "upload_quota" : 10 * 1024 * 1024    # max 10 Mb
      , "upload_size" : 0
   },
   "tomasbomfim": {
      "user" : "tomasbomfim"
      , "passwd" : "41b9f25030b0ef830fd47d450c714e79"
      , "name" : u"Tomás"
      , "lastname" : "Bomfim"
      , "email" : "tomasbomfim@hotmail.com"
      , "tags" : [] 
      , "description" : ""        
      , "photo" : ""
      , "cod_institute" : "9999"
      , "institute" : u"Não informada"
      , "amigos" : [
                     "mauricio"
                  ]
      , "amigos_pendentes" : []
      , "amigos_convidados" : []
      , "comunidades" : []
      , "comunidades_pendentes" : []
      , "papeis" : [
                     "tnm"
         ]   # serve tb para definir se o usuário é "tnm" ou "educo"
      , "mykeys" : []
      , "privacidade" : u"Pública"           # Pública ou Privada
      , "upload_quota" : 10 * 1024 * 1024    # max 10 Mb
      , "upload_size" : 0
   },
   "livia": {
      "user" : "livia"
      , "passwd" : "41b9f25030b0ef830fd47d450c714e79"
      , "name" : u"Lívia"
      , "lastname" : "Monnerat Castro"
      , "email" : "livia.monnerat@gmail.com"
      , "tags" : [] 
      , "description" : ""        
      , "photo" : ""
      , "cod_institute" : "0002"
      , "institute" : u"Núcleo de Computação Eletrônica"
      , "amigos" : [
                     "mauricio",
                     "julianne",
                     "Angela",
                     "marcinha",
                     "roberta",
                     "ludaflon"
                  ]
      , "amigos_pendentes" : []
      , "amigos_convidados" : []
      , "comunidades" : [
                           "zzzz",
                           "comu",
                           "DevTnM",
                           "qqqq",
                           "nova_Comu",
                           "comu_publica"
                        ]
      , "comunidades_pendentes" : []
      , "papeis" : [
                     "admin",
                     "tnm",
                     "educo",
                     "professor"
                  ]   # serve tb para definir se o usuário é "tnm" ou "educo"
      , "mykeys" : []
      , "privacidade" : u"Pública"           # Pública ou Privada
      , "upload_quota" : 10 * 1024 * 1024    # max 10 Mb
      , "upload_size" : 0
   },
   "marcinha": {
      "user" : "marcinha"
      , "passwd" : "41b9f25030b0ef830fd47d450c714e79"
      , "name" : "Marcia"
      , "lastname" : "Cardoso"
      , "email" : "marcia@nce.ufrj.br"
      , "tags" : [] 
      , "description" : ""        
      , "photo" : ""
      , "cod_institute" : "9999"
      , "institute" : u"Não informada"
      , "amigos" : [
                     "mauricio",
                     "julianne",
                     "livia",
                  ]
      , "amigos_pendentes" : [
                              "aluciarodrigues",
                           ]
      , "amigos_convidados" : []
      , "comunidades" : [
                           "qqqq",
                           "tttt",
                           "DevTnM",
                           "BCBS",
                           "Comunidade_de_teste",
                           "nomecom"
                        ]
      , "comunidades_pendentes" : []
      , "papeis" : [
                     "admin",
                     "tnm"
                  ]   # serve tb para definir se o usuário é "tnm" ou "educo"
      , "mykeys" : []
      , "privacidade" : u"Pública"           # Pública ou Privada
      , "upload_quota" : 10 * 1024 * 1024    # max 10 Mb
      , "upload_size" : 0
   },
   "roberta": {
      "user" : "roberta"
      , "passwd" : "41b9f25030b0ef830fd47d450c714e79"
      , "name" : "Roberta"
      , "lastname" : "Tancillo"
      , "email" : "roberta_tancillo@yahoo.com.br"
      , "tags" : [] 
      , "description" : ""        
      , "photo" : ""
      , "cod_institute" : "9999"
      , "institute" : u"Não informada"
      , "amigos" : [
                     "livia"
                  ]
      , "amigos_pendentes" : [
                              "mauricio"
                           ]
      , "amigos_convidados" : []
      , "comunidades" : [
                           "qqqq",
                           "tttt",
                           "DevTnM",
                           "BCBS",
                           "Comunidade_de_teste",
                           "nomecom"
                        ]
      , "comunidades_pendentes" : []
      , "papeis" : [
                     "admin",
                     "tnm"
                  ]   # serve tb para definir se o usuário é "tnm" ou "educo"
      , "mykeys" : []
      , "privacidade" : u"Pública"           # Pública ou Privada
      , "upload_quota" : 10 * 1024 * 1024    # max 10 Mb
      , "upload_size" : 0
   },
   "Angela": {
      "user" : "Angela"
      , "passwd" : "41b9f25030b0ef830fd47d450c714e79"
      , "name" : "Angela"
      , "lastname" : u"Mendonça"
      , "email" : "amanume@gmail.com"
      , "tags" : [] 
      , "description" : ""        
      , "photo" : ""
      , "cod_institute" : "9999"
      , "institute" : u"Não informada"
      , "amigos" : [
                     "livia",
                  ]
      , "amigos_pendentes" : [
                                 "mauricio",
                              ]
      , "amigos_convidados" : [
                                 "ludaflon"
                              ]
      , "comunidades" : [
                           "qqqq",
                           "tttt",
                           "DevTnM",
                           "BCBS",
                           "Comunidade_de_teste",
                           "nomecom"
                        ]
      , "comunidades_pendentes" : []
      , "papeis" : [
                     "admin",
                     "tnm"
                  ]   # serve tb para definir se o usuário é "tnm" ou "educo"
      , "mykeys" : []
      , "privacidade" : u"Pública"           # Pública ou Privada
      , "upload_quota" : 10 * 1024 * 1024    # max 10 Mb
      , "upload_size" : 0
   },
   "aluciarodrigues": {
      "user" : "aluciarodrigues"
      , "passwd" : "41b9f25030b0ef830fd47d450c714e79"
      , "name" : "Ana Lucia"
      , "lastname" : u"Rodrigues"
      , "email" : "ana_lucia@nce.ufrj.br"
      , "tags" : [] 
      , "description" : ""        
      , "photo" : ""
      , "cod_institute" : "9999"
      , "institute" : u"Não informada"
      , "amigos" : [
                     "mauricio"
                  ]
      , "amigos_pendentes" : []
      , "amigos_convidados" : [
                                 "marcinha",
                                 "ludaflon"
                              ]
      , "comunidades" : [
                           "qqqq",
                           "tttt",
                           "DevTnM",
                           "BCBS",
                           "Comunidade_de_teste",
                           "nomecom"
                        ]
      , "comunidades_pendentes" : []
      , "papeis" : [
                     "admin",
                     "tnm"
                  ]   # serve tb para definir se o usuário é "tnm" ou "educo"
      , "mykeys" : []
      , "privacidade" : u"Pública"           # Pública ou Privada
      , "upload_quota" : 10 * 1024 * 1024    # max 10 Mb
      , "upload_size" : 0
   },
   "ludaflon": {
      "user" : "ludaflon"
      , "passwd" : "41b9f25030b0ef830fd47d450c714e79"
      , "name" : "Luciana"
      , "lastname" : u"Daflon"
      , "email" : "daflonbotelho@gmail.com"
      , "tags" : [] 
      , "description" : ""        
      , "photo" : ""
      , "cod_institute" : "9999"
      , "institute" : u"Não informada"
      , "amigos" : [
                     "livia"
                  ]
      , "amigos_pendentes" : [
                              "Angela",
                              "aluciarodrigues",
                           ]
      , "amigos_convidados" : [
                                 "marcinha",
                              ]
      , "comunidades" : [
                           "qqqq",
                           "tttt",
                           "DevTnM",
                           "BCBS",
                           "Comunidade_de_teste",
                           "nomecom"
                        ]
      , "comunidades_pendentes" : []
      , "papeis" : [
                     "admin",
                     "tnm"
                  ]   # serve tb para definir se o usuário é "tnm" ou "educo"
      , "mykeys" : []
      , "privacidade" : u"Privada"           # Pública ou Privada
      , "upload_quota" : 10 * 1024 * 1024    # max 10 Mb
      , "upload_size" : 0
   }
})

  # -------------------------------------------------------------
  # A estrutura acima pode ser resumida da seguinte forma:
  
         #  mauricio:
         #	amigos     ->     julianne | tomasbomfim | livia | marcinha
         #	convidados ->     roberta  |    analu    | Angela
         #      pendentes  ->     []
         #
         #  julianne:
         #	amigos     ->     mauricio | livia | marcinha
         #      convidados ->     []
         #      pendentes  ->     []         
         #     
         #  tomasbomfim:
         #	amigos     ->     mauricio
         #      convidados ->     []
         #      pendentes  ->     []         
         #
         #  livia:
         #	amigos     ->     mauricio | julianne | Angela | marcinha | roberta | ludaflon
         #      convidados ->     []
         #      pendentes  ->     []         
         #
         #  marcinha:
         #	amigos     ->     mauricio | julianne | livia
         #      convidados ->     []         
         #	pendentes  ->     aluciarodrigues
         #
         #  roberta:
         #	amigos     ->     livia
         #	pendentes  ->     mauricio
         #
         #  Angela:
         #	amigos     ->     livia
         #	convidados ->     ludaflon
         #	pendentes  ->     mauricio
         #
         #  aluciarodrigues:
         #	amigos     ->     mauricio
         #	convidados ->     marcinha | ludaflon
         #      pendentes  ->     []
         #
         #  ludaflon:
         #	amigos     ->     livia
         #	convidados ->     marcinha
         #	pendentes  ->     Angela | aluciarodrigues

class TestComunidade(unittest.TestCase):
  """Testes unitários para o gerenciamento de comunidades"""
  def setUp(self):
    
    core.model.REGISTRY = REGISTRY_DEFAULT()
    core.model.MAGKEYS = MAGKEYS_DEFAULT()
    core.model.INVITES = {}
    core.model.USERSCHOOL = {}
    log.model.NOTIFICATIONERROR = {}
    log.model.NOTIFICATION = {}
    
    self.app = TestApp(WsgiApp())
    registry.update(REGISTRY_FORM)

    # Cria usuários para os testes
    #registry['user'] = 'teste'
    self.app.post('/new/user', registry)
    core.model.REGISTRY['teste']['cod_institute'] = u"0002"
     
    # Faz login como usuário teste
    login.update(LOGIN_FORM)
    self.app.post('/login', login)
    core.model.REGISTRY['teste']['papeis'].append('professor')

    core.model.MAGKEYS = MAGKEYS_DEFAULT()    # recria chave mágica para que possa fazer outro cadastro
    
    
  def tearDown(self):
    #self.mock.restore()
    #self.mock.verify()
    #self.mock,MEMBER =None,None
    pass


  # -------------------------------------------------------------
  # Acesso a tela de Sugestões de Amigos

  def test_no_sugest_friends(self):
    "Exibe mensagem de que o usuário não possui sugestões de amigos por ainda não ter nenhum amigo."
    response = self.app.get('/sugestfriends/teste')
    assert u'<p>Ainda não é possível sugerir amigos para teste.</p>' in response, "Erro: Sugeriu amigos para um usuário que não possui amigos!"
    
  def test_reject_sugest_friends(self):
    "Exibe mensagem de erro quando um usuário tenta visualizar as sugestões de amigos de outro usuário."
    core.model.REGISTRY["teste"] = core.model.REGISTRY["mauricio"]
    response = self.app.get('/sugestfriends/mauricio')
    assert u'<div class="tnmMSG">Erro: Você não tem permissão de visualizar as sugestões de amigos de mauricio.</div> ' in response, "Erro: Exibiu Sugestão de Amigos de um usuário para outro usuário!"
    
  def test_sugest_friends_mauricio(self):
    "Exibe tela de Sugestão de amigos do usuário teste se baseando nos amigos do usuário mauricio."
    core.model.REGISTRY["teste"] = core.model.REGISTRY["mauricio"]
    response = self.app.get('/sugestfriends/teste')
    assert u'<a href="/user/mauricio" title="Maurício Bonfim" style="color:black">' in response, "Erro: Não sugeriu o usuário mauricio!"
    assert u'<a href="/user/ludaflon" title="Luciana Daflon" style="background-color:white;">' not in response, "Erro: Sugeriu o usuário privado ludaflon!"
    
  def test_sugest_friends_julianne(self):
    "Exibe tela de Sugestão de amigos do usuário teste se baseando nos amigos do usuário julianne."
    core.model.REGISTRY["teste"] = core.model.REGISTRY["julianne"]
    response = self.app.get('/sugestfriends/teste')
    assert u'<a href="/user/julianne" title="Julianne de Carvalho" style="color:black">' in response, "Erro: Não sugeriu o usuário julianne!"
    assert u'<a href="/user/ludaflon" title="Luciana Daflon" style="color:black">' not in response, "Erro: Não sugeriu o usuário ludaflon!"
    assert u'<a href="/user/tomasbomfim" title="Tomás Bomfim" style="color:black">' in response, "Erro: Não sugeriu o usuário tomasbomfim!"
    assert u'<a href="/user/roberta" title="Roberta Tancillo" style="color:black">' in response, "Erro: Não sugeriu o usuário roberta!"
    assert u'<a href="/user/Angela" title="Angela Mendonça" style="color:black">' in response, "Erro: Não sugeriu o usuário Angela!"
    
  def test_accept_sugest_friends(self):
    "Exibe tela de confirmação de envio de convite para um dos amigos sugeridos."
    core.model.REGISTRY["teste"] = core.model.REGISTRY["julianne"]
    self.app.get('/sugestfriends/teste')
    response = self.app.get('/newfriend?friend=tomasbomfim')
    assert u'<div class="tnmMSG">Convite para tomasbomfim enviado com sucesso.</div> ' in response, "Erro: Usuário não foi convidado!"    
    
  def test_sugest_new_friends(self):
    "Exibe tela de Sugestão de amigos com novas sugestões após o usuário ter convidado algum(s) do(s) amigo(s) sugeridos."
    core.model.REGISTRY["teste"] = core.model.REGISTRY["julianne"]
    self.app.get('/sugestfriends/teste')
    self.app.get('/newfriend?friend=tomasbomfim')
    response = self.app.get('/sugestfriends/teste')
    assert u'<a href="/user/julianne" title="Julianne de Carvalho" style="color:black">' in response, "Erro: Não sugeriu o usuário julianne!"
    assert u'<a href="/user/ludaflon" title="Luciana Daflon" style="color:black">' not in response, "Erro: Sugeriu o usuário privado ludaflon!"
    assert u'<a href="/user/tomasbomfim" title="Tomás Bomfim" style="color:black">' not in response, "Erro: Sugeriu o usuário tomasbomfim!"
    assert u'<a href="/user/roberta" title="Roberta Tancillo" style="color:black">' in response, "Erro: Não sugeriu o usuário roberta!"
    assert u'<a href="/user/Angela" title="Angela Mendonça" style="color:black">' in response, "Erro: Não sugeriu o usuário Angela!"
    
  def test_sugest_friends_tomas(self):
    "Exibe tela de Sugestão de amigos do usuário teste se baseando nos amigos do usuário tomasbomfim."
    core.model.REGISTRY["teste"] = core.model.REGISTRY["tomasbomfim"]
    response = self.app.get('/sugestfriends/teste')
    assert u'<a href="/user/tomasbomfim" title="Tomás Bomfim" style="color:black">' in response, "Erro: Não sugeriu o usuário tomasbomfim!"
    assert u'<a href="/user/livia" title="Lívia Monnerat Castro" style="color:black">' in response, "Erro: Não sugeriu o usuário livia!"
    assert u'<a href="/user/julianne" title="Julianne de Carvalho" style="color:black">' in response, "Erro: Não sugeriu o usuário julianne!"
    assert u'<a href="/user/marcinha" title="Marcia Cardoso" style="color:black">' in response, "Erro: Não sugeriu o usuário marcinha!"
    
  def test_sugest_friends_livia(self):
    "Exibe tela de Sugestão de amigos do usuário teste se baseando nos amigos do usuário livia."
    core.model.REGISTRY["teste"] = core.model.REGISTRY["livia"]
    response = self.app.get('/sugestfriends/teste')
    assert u'<a href="/user/tomasbomfim" title="Tomás Bomfim" style="color:black">' in response, "Erro: Não sugeriu o usuário tomasbomfim!"
    assert u'<a href="/user/livia" title="Lívia Monnerat Castro" style="color:black">' in response, "Erro: Não sugeriu o usuário livia!"
    
  def test_sugest_friends_marcinha(self):
    "Exibe tela de Sugestão de amigos do usuário teste se baseando nos amigos do usuário marcinha."
    core.model.REGISTRY["teste"] = core.model.REGISTRY["marcinha"]
    response = self.app.get('/sugestfriends/teste')
    assert u'<a href="/user/marcinha" title="Marcia Cardoso" style="color:black">' in response, "Erro: Não sugeriu o usuário marcinha!"
    assert u'<a href="/user/tomasbomfim" title="Tomás Bomfim" style="color:black">' in response, "Erro: Não sugeriu o usuário tomasbomfim!"
    assert u'<a href="/user/Angela" title="Angela Mendonça" style="color:black">' in response, "Erro: Não sugeriu o usuário Angela!"
    assert u'<a href="/user/roberta" title="Roberta Tancillo" style="color:black">' in response, "Erro: Não sugeriu o usuário roberta!"
    assert u'<a href="/user/ludaflon" title="Luciana Daflon" style="color:black">' not in response, "Erro: Sugeriu o usuário privado ludaflon!"
    
  def test_sugest_friends_roberta(self):
    "Exibe tela de Sugestão de amigos do usuário teste se baseando nos amigos do usuário roberta."
    core.model.REGISTRY["teste"] = core.model.REGISTRY["roberta"]
    response = self.app.get('/sugestfriends/teste')
    assert u'<a href="/user/Angela" title="Angela Mendonça" style="color:black">' in response, "Erro: Não sugeriu o usuário Angela!"
    assert u'<a href="/user/marcinha" title="Marcia Cardoso" style="color:black">' in response, "Erro: Não sugeriu o usuário marcinha!"
    assert u'<a href="/user/julianne" title="Julianne de Carvalho" style="color:black">' in response, "Erro: Não sugeriu o usuário julianne!"
    assert u'<a href="/user/roberta" title="Roberta Tancillo" style="color:black">' in response, "Erro: Não sugeriu o usuário roberta!"
    assert u'<a href="/user/ludaflon" title="Luciana Daflon" style="color:black">' not in response, "Erro: Sugeriu o usuário privado ludaflon!"
    
  def test_sugest_friends_Angela(self):
    "Exibe tela de Sugestão de amigos do usuário teste se baseando nos amigos do usuário Angela."
    core.model.REGISTRY["teste"] = core.model.REGISTRY["Angela"]
    response = self.app.get('/sugestfriends/teste')
    assert u'<a href="/user/Angela" title="Angela Mendonça" style="color:black">' in response, "Erro: Não sugeriu o usuário Angela!"
    assert u'<a href="/user/marcinha" title="Marcia Cardoso" style="color:black">' in response, "Erro: Não sugeriu o usuário marcinha!"
    assert u'<a href="/user/julianne" title="Julianne de Carvalho" style="color:black">' in response, "Erro: Não sugeriu o usuário julianne!"
    assert u'<a href="/user/roberta" title="Roberta Tancillo" style="color:black">' in response, "Erro: Não sugeriu o usuário roberta!"
      
  def test_sugest_friends_aluciarodrigues(self):
    "Exibe tela de Sugestão de amigos do usuário teste se baseando nos amigos do usuário aluciarodrigues."
    core.model.REGISTRY["teste"] = core.model.REGISTRY["aluciarodrigues"]
    response = self.app.get('/sugestfriends/teste')
    assert u'<a href="/user/julianne" title="Julianne de Carvalho" style="color:black">' in response, "Erro: Não sugeriu o usuário julianne!"
    assert u'<a href="/user/tomasbomfim" title="Tomás Bomfim" style="color:black">' in response, "Erro: Não sugeriu o usuário tomasbomfim!"
    assert u'<a href="/user/livia" title="Lívia Monnerat Castro" style="color:black">' in response, "Erro: Não sugeriu o usuário livia!"
    
  def test_sugest_friends_ludaflon(self):
    "Exibe tela de Sugestão de amigos do usuário teste se baseando nos amigos do usuário ludaflon."
    core.model.REGISTRY["teste"] = core.model.REGISTRY["ludaflon"]
    response = self.app.get('/sugestfriends/teste')
    assert u'<a href="/user/mauricio" title="Maurício Bonfim" style="color:black">' in response, "Erro: Não sugeriu o usuário mauricio!"
    assert u'<a href="/user/julianne" title="Julianne de Carvalho" style="color:black">' in response, "Erro: Não sugeriu o usuário julianne!"
    assert u'<a href="/user/roberta" title="Roberta Tancillo" style="color:black">' in response, "Erro: Não sugeriu o usuário roberta!"
    assert u'<a href="/user/ludaflon" title="Luciana Daflon" style="color:black">' not in response, "Erro: Sugeriu o usuário privado ludaflon!"