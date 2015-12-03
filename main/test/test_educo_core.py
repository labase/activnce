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
import unittest

import core.model
import educo_core.model

from core.model import COMUNIDADE_EDUCOPEDISTAS

ALLOWED_USERS_DEFAULT = lambda: dict({
         "testeprofessor@rioeduca.net" : {
                     "email" : "testeprofessor@rioeduca.net"          # fulano@rioeduca.net
                    ,"nome" : "Professor Teste da Silva"           # nome completo    
                    ,"papel" : "professor"         # "professor" ou "aluno"
                    ,"comunidades" : []    # lista de comunidades (turmas) nas quais                   
                                          # este usuário se inscreverá automaticamente
                                          # no momento do cadastro.
                    ,"mkey" : "u99996yt276Yt197AgR5667dGkLO3"  # preenchido somente se professor
         },
            "testeprofessor1@rioeduca.net" : {
                     "email" : "testeprofessor@rioeduca.net"          # fulano@rioeduca.net
                    ,"nome" : "Digitador Teste da Silva"           # nome completo    
                    ,"papel" : "digitador"          # "professor" ou "aluno"
                    ,"comunidades" : []    # lista de comunidades (turmas) nas quais                   
                                          # este usuário se inscreverá automaticamente
                                          # no momento do cadastro.
                    ,"mkey" : "u99996yt276Yt197AgR5667dGkLO3"  # preenchido somente se professor
         },
            "testealuno@rioeduca.net" : {
                     "email" : "testealuno@rioeduca.net"          # fulano@rioeduca.net
                    ,"nome" : "Aluno Teste da Silva"           # nome completo    
                    ,"papel" : "aluno"          # "professor" ou "aluno"
                    ,"comunidades" : []    # lista de comunidades (turmas) nas quais                   
                                          # este usuário se inscreverá automaticamente
                                          # no momento do cadastro.
                    ,"mkey" : ""  # preenchido somente se professor
            }
})

REGISTRY_FORM = { "user":"testeprofessor@rioeduca.net",
                  "passwd": "teste",
                  "npasswd": "teste",
                  "name":  "Professor Teste da Silva",
                  "lastname": "",
                  "email": "testeprofessor@rioeduca.net",
                  "mkey": "u99996yt276Yt197AgR5667dGkLO3",
		  "aceito" : "S" }

EDUCOMEMBERPROFESSOR_FORM = { "user":"testeprofessor@rioeduca.net",
                     "passwd": "teste",
                     "npasswd": "teste",
                     "papel": "professor",
                     "email": "testeprofessor@rioeduca.net",   
                     "mkey": "u99996yt276Yt197AgR5667dGkLO3",
		     "aceito" : "S" }
EDUCOMEMBERALUNO_FORM = { "user":"testealuno@rioeduca.net",
                     "passwd": "teste",
                     "npasswd": "teste",
                     "email": "testealuno@rioeduca.net",
                     "papel": "aluno",
		     "aceito" : "S" }
EDUCOMEMBERDIGITADOR_FORM = { "user":"testeprofessor1@rioeduca.net",
                     "passwd": "teste",
                     "npasswd": "teste",
                     "papel": "digitador",
                     "email": "testeprofessor1@rioeduca.net",   
                     "mkey": "u99996yt276Yt197AgR5667dGkLO3",
                     "aceito" : "S" }


LOGIN_FORM = { "user":"testeprofessor@rioeduca.net", "passwd": "teste", "tipo": "educo" }
LOGINDIGITADOR_FORM = { "user":"testeprofessor1@rioeduca.net", "passwd": "teste", "tipo": "educo" }
LOGINALUNO_FORM = { "user":"testealuno@rioeduca.net", "passwd": "teste", "tipo": "educo" }

SLIDE_EDIT_FORM = { "conteudo": "Teste de edição de slide" }

EDUCOATIVIDADES2 = dict(
        MAT = {
             "nome": u"Matemática",
             "01": dict(
                  bimestre = "I",
                  tema = "Soma",
                  plano = "N",   
                  apostila = "N",  
                  apresentacao = "N",  
                  imagens = [],
                  atividades = []                               
             ),
             '02': dict(
                  bimestre = "II",
                  tema = u"Subtração",
                  plano = "N",   
                  apostila = "N",  
                  apresentacao = "N",  
                  imagens = [],
                  atividades = []
             ),
             "03": dict(
                  bimestre = "III",
                  tema = u"Multiplicação",
                  plano = "N",   
                  apostila = "N",  
                  apresentacao = "N",  
                  imagens = [],
                  atividades = []                               
             ),
             "04": dict(
                  bimestre = "IV",
                  tema = "Divisão",
                  plano = "N",   
                  apostila = "N",  
                  apresentacao = "N",  
                  imagens = [],
                  atividades = []                               
             )
        },
        LPT = {
             "nome": u"Língua Portuguesa",
             '01': dict(
                  bimestre = "I",
                  tema = u"Substantivos",
                  plano = "N",   
                  apostila = "N",  
                  apresentacao = "N",  
                  imagens = [],
                  atividades = []                            
             ),
             '02': dict(
                  bimestre = "II",
                  tema = u"Verbos",
                  plano = "N",   
                  apostila = "N",  
                  apresentacao = "N",  
                  imagens = [],
                  atividades = []                              
             ),      
             '03': dict(
                  bimestre = "III",
                  tema = u"Verbos 2",
                  plano = "N",   
                  apostila = "N",  
                  apresentacao = "N",  
                  imagens = [],
                  atividades = []                              
             ),
             '04': dict(
                  bimestre = "IV",
                  tema = u"Verbos 3",
                  plano = "N",   
                  apostila = "N",  
                  apresentacao = "N",  
                  imagens = [],
                  atividades = []                             
             )
        }
)

EDUCOATIVIDADES3 = dict(
        MAT = {
             "nome": u"Matemática",
             '01': dict(
                  bimestre = "I",
                  tema = u"Logarítmos",
                  plano = "N",   
                  apostila = "N",  
                  apresentacao = "N",  
                  imagens = [],
                  atividades = [ "00", "3MAT0101" ]                               
             ),
             '02': dict(
                  bimestre = "II",
                  tema = u"Logarítmos 2",
                  plano = "N",   
                  apostila = "N",  
                  apresentacao = "N",  
                  imagens = [],
                  atividades = [ "00" ]                               
             ),
             '03': dict(
                  bimestre = "III",
                  tema = u"Logarítmos 3",
                  plano = "N",   
                  apostila = "N",  
                  apresentacao = "N",  
                  imagens = [],
                  atividades = [ "00" ]                               
             ),
             '04': dict(
                  bimestre = "IV",
                  tema = u"Logarítmos 4",
                  plano = "N",   
                  apostila = "N",  
                  apresentacao = "N",  
                  imagens = [],
                  atividades = [ "00" ]                               
             )
        },
        LPT = {
             "nome": u"Língua Portuguesa",
             '01': dict(
                  bimestre = "I",
                  tema = u"Orações Subordinadas",
                  plano = "N",   
                  apostila = "N",  
                  apresentacao = "N",  
                  imagens = [],
                  atividades = []                            
             ),
             '02': dict(
                  bimestre = "II",
                  tema = u"Orações Subordinadas 2",
                  plano = "N",   
                  apostila = "N",  
                  apresentacao = "N",  
                  imagens = [],
                  atividades = []                            
             ),
             '03': dict(
                  bimestre = "III",
                  tema = u"Orações Subordinadas 3",
                  plano = "N",   
                  apostila = "N",  
                  apresentacao = "N",  
                  imagens = [],
                  atividades = []                            
             ),
             '04': dict(
                  bimestre = "IV",
                  tema = u"Orações Subordinadas 4",
                  plano = "N",   
                  apostila = "N",  
                  apresentacao = "N",  
                  imagens = [],
                  atividades = []                            
             )
        }
)

SLIDE = {
    COMUNIDADE_EDUCOPEDISTAS + '/3MAT0100' : {
      'user' : ""
    , 'registry_id' : "educopedia"
    , 'owner' : ""
    , 'nomepag' : ""
    , 'conteudo' : ""
    , 'tipo' : "slide"
    , 'tags' : []
    , 'data_cri' : ""
    }
}

educo_allowed_users = {}
registry = {}
registryeduco = {}
registryeducoaluno = {}
registryeducodigitador = {}
login = {}
loginaluno = {}
logindigitador = {}
registry_slide_edit = {}

class TestEducoCore(unittest.TestCase):
  """Testes unitários para os métodos do educo_core"""
  def setUp(self):
    educo_core.model.ALLOWED_USERS = {}
    educo_core.model.CADERNOS      = {}
    educo_core.model.ATIVIDADES    = {}
    educo_core.model.ACESSOS       = {}
    educo_core.model.SLIDES        = {}
    educo_core.model.LOG_DELETED_FILES = {}
    core.model.REGISTRY = {}

    self.app = TestApp(WsgiApp())
    educo_core.model.ALLOWED_USERS = ALLOWED_USERS_DEFAULT()
    registry.update(REGISTRY_FORM)
    registryeduco.update(EDUCOMEMBERPROFESSOR_FORM)
    registryeducoaluno.update(EDUCOMEMBERALUNO_FORM)
    registryeducodigitador.update(EDUCOMEMBERDIGITADOR_FORM)
    login.update(LOGIN_FORM)
    loginaluno.update(LOGINALUNO_FORM)
    logindigitador.update(LOGINDIGITADOR_FORM)
    registry_slide_edit.update(SLIDE_EDIT_FORM)

    educo_core.model.ATIVIDADES['2'] = EDUCOATIVIDADES2
    educo_core.model.ATIVIDADES['3'] = EDUCOATIVIDADES3

    educo_core.model.SLIDES = SLIDE

  def tearDown(self):
    #self.mock.restore()
    #self.mock.verify()
    #self.mock,REGISTRY =None,None
    pass
"""
  # -------------------------------------------------------------
  # Home Page

  def test_returns_home_on_root(self):
    "Return the home page on '/educopedia'"
    response = self.app.get('/educopedia')
    assert u'form name="login" action="/educopedia/entrar" method="post"' in response, "Erro: Não exibiu tela de Home!"

# ---------------------- Cadastro de Usuário Educopédia/SME

# Teste de class EducoRegistryHandler - Cadastro do usuário SME educopedia
  
  def test_returns_registry_form_on_root(self):
    "Return a form containing registry data"
    response = self.app.get('/educopedia/cadastrar')
    assert '<input class="form-email" type="text" name="email" size="20"' in response, "Erro: Não exibiu formulário de cadastro!"

  def test_accept_registry_ok(self):
    "Return Index.html  after registry ok"
    response = self.app.post('/educopedia/cadastrar',registryeduco)
    assert 'testeprofessor@rioeduca.net' in core.model.REGISTRY, "Erro: Não conseguiu cadastrar usuário"
    assert core.model.REGISTRY["testeprofessor@rioeduca.net"]["name"] == 'Professor', "Erro: Não armazenou nome no banco"
    assert core.model.REGISTRY["testeprofessor@rioeduca.net"]["lastname"] == 'Teste da Silva', "Erro: Não armazenou sobrenome no banco"
    assert core.model.REGISTRY["testeprofessor@rioeduca.net"]["email"] == 'testeprofessor@rioeduca.net', "Erro: Não armazenou email no banco"
    assert 'educo' in core.model.REGISTRY["testeprofessor@rioeduca.net"]["papeis"], "Erro: Não armazenou papel do usuario no banco"
    assert 'testeprofessor@rioeduca.net' not in educo_core.model.ALLOWED_USERS, "Erro: Não removeu usuário cadastrado do ALLOWED_USERS"
    assert u'Cadastro criado com sucesso.' in response, "Erro: Não exibiu mensagem após cadastrar usuário com sucesso!"
 
  def test_reject_registry_double_user(self):
    "Return error message: Login já existe!"
    self.app.post('/educopedia/cadastrar', registryeduco)
    educo_core.model.ALLOWED_USERS = ALLOWED_USERS_DEFAULT()
    response = self.app.post('/educopedia/cadastrar', registryeduco)
    assert u'Já existe um usuário cadastrado com este login.' in response, "Erro: Não exibiu a mensagem 'Login já existe!'"
   
  def test_reject_registry_invalid_email(self):
    "Return error message: Email inválido!"
    self.app.post('/educopedia/cadastrar', registryeduco)
    response = self.app.post('/educopedia/cadastrar', registryeduco)
    assert u'E-mail inválido.<br/>' in response, "Erro: Não exibiu a mensagem 'Email inválido!'"
    
  def test_reject_registry_without_email(self):
    "Return error message: Email não preenchido"
    registryeduco["email"]=""
    response = self.app.post('/educopedia/cadastrar', registryeduco)
    assert u'E-mail não preenchido.' in response, "Erro: Não exibiu a mensagem 'E-mail não preenchido.'"
 
  def test_reject_registry_without_magickey(self):
    "Return error message: Chave inválida para cadastro."
    registryeduco["mkey"]="teste"
    response = self.app.post('/educopedia/cadastrar', registryeduco)
    assert  u'Chave inválida para cadastro.<br/>' in response, "Erro: Não exibiu a mensagem 'Chave inválida para cadastro.'"

  def test_reject_registry_without_mintam_pass(self):
    "Return error message: Senha deve ter no mínimo %s caracteres.<br/>"
    registryeduco["passwd"]=""
    response = self.app.post('/educopedia/cadastrar', registryeduco)
    assert u'Senha deve ter no mínimo' in response, "Erro: Não exibiu a mensagem 'Senha deve ter no mínimo'"
  
  def test_reject_registry_without_pass_confirm(self):
    "Return error message: Senha diferente da confirmação!"
    registryeduco["npasswd"]="npasswd"
    response = self.app.post('/educopedia/cadastrar', registryeduco)
    assert u'Senha diferente da confirmação' in response, "Erro: Não exibiu a mensagem 'Senha diferente da confirmação'"

  def test_reject_registry_without_accepting_terms(self):
    "Return error message: Você deve aceitar os termos de uso da Educopédia."
    registryeduco["aceito"]=""
    response = self.app.post('/educopedia/cadastrar', registryeduco)
    assert u'Você deve aceitar os termos de uso da Educopédia.' in response, "Erro: Não exibiu a mensagem 'Você deve aceitar os termos de uso da Educopédia.'"

# Teste de class ForgotMkeyHandler - Teste para esqueceu a chave


#  def test_reject_registry_without_mintam_pass(self):
#    "Test if sendmail with mkey ok"
    #assert u'Email enviado' in response, "Erro: Não exibiu a mensagem 'Email enviado'"

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

  def test_login_prof_successful(self):
    "If login is successful, return Selecione o Ano , if thereis no activity - retorna educopedia/aula'"
    self.app.post('/educopedia/cadastrar', registryeduco)
    response = self.app.post('/login', login).follow().follow()
    assert u'<img class="pastas" id="anos" src="/static/educopedia/images/buttons/ano_0.png" width="750" height="340" alt="Anos" usemap="#anos">' in response, "Erro: Não exibiu a página com Selecione o Ano, após professor logar ."

  def test_login_aluno_successful(self):
    "If login is successful, return Selecione o Ano , if thereis no activity - retorna educopedia/aula'"
    registryeduco = {}
    registryeduco.update(EDUCOMEMBERALUNO_FORM)
    self.app.post('/educopedia/cadastrar', registryeduco)
    login = {}
    login.update(LOGINALUNO_FORM)
    response = self.app.post('/login', login).follow().follow()
    assert u'<img class="pastas" id="anos" src="/static/educopedia/images/buttons/ano_0.png" width="750" height="340" alt="Anos" usemap="#anos">' in response, "Erro: Não exibiu a página com Selecione o Ano, após aluno logar ."


# Teste de login para papel digitador - retorna educopedia/admin
  def test_returns_aula_home_digitador(self):
    "Return the principal aula page if digitador - retorna educopedia/admin"
    registryeduco = {}
    registryeduco.update(EDUCOMEMBERDIGITADOR_FORM)
    self.app.post('/educopedia/cadastrar', registryeduco)
    login = {}
    login.update(LOGINDIGITADOR_FORM)
    response = self.app.post('/login', login).follow().follow()
    assert u'<img class="pastas" id="anos" src="/static/educopedia/images/buttons/ano_0.png" width="750" height="340" alt="Anos" usemap="#anos">' in response, "Erro: Não exibiu a página com Selecione o Ano, após digitador logar ."


# ------ Logout -------------------------------------

  def test_logout(self):
    "Return the logout return screen(home)"
    self.app.post('/educopedia/cadastrar', registryeduco)
    self.app.post('/educopedia/entrar', login)
    response = self.app.get('/educopedia/sair').follow()
    assert u'form name="login" action="/educopedia/entrar" method="post"' in response, "Erro: Não exibiu formulário de cadastro após fazer logout!"


# ------ Lembrar senha ------------------------------

# Teste de class EducoForgotPasswdHandler

  def test_open_forgotpasswd_screen(self):
    "Return the forgot passwd screen"
    self.app.post('/educopedia/cadastrar', registryeduco)
    response = self.app.get('/educopedia/lembrarsenha')
    assert 'Digite o seu login. Uma nova senha será gerada e enviada para o seu e-mail.' in response, "Erro: Não exibiu tela de 'esqueci minha senha'!"

#------ Página principal de um usuário ---------------

  def test_user_year_screen(self):
    "Return the select year screen"
    self.app.post('/educopedia/cadastrar', registryeduco)
    self.app.post('/educopedia/entrar', login).follow().follow()
    response = self.app.get('/educopedia/aula')
    assert u'<!-- Tela de seleção de ano -->' in response, "Erro: Não mostrou anos"

  def test_user_year_not_found(self):
    "Return the year not found screen"
    self.app.post('/educopedia/cadastrar', registryeduco)
    self.app.post('/educopedia/entrar', login).follow().follow()
    response = self.app.get('/educopedia/aula/100')
    assert u'<!-- Tela de seleção de ano -->' in response, "Erro: Não mostrou ano não selecionado"

  def test_user_subject_screen(self):
    "Return the select a subject screen"
    self.app.post('/educopedia/cadastrar', registryeduco)
    self.app.post('/educopedia/entrar', login).follow().follow()
    response = self.app.get('/educopedia/aula/3')
    assert u'<!-- Tela de seleção de matéria -->' in response, "Erro: Não mostrou as matérias"

  def test_user_subject_not_found_screen(self):
    "Return the subject not found screen"
    self.app.post('/educopedia/cadastrar', registryeduco)
    self.app.post('/educopedia/entrar', login).follow().follow()
    response = self.app.get('/educopedia/aula/3/AAA')
    assert u'<!-- Tela de seleção de matéria -->' in response, "Erro: Não mostrou matéria não selecionada"

  def test_user_lesson_screen(self):
    "Return the select a lesson screen"
    self.app.post('/educopedia/cadastrar', registryeduco)
    self.app.post('/educopedia/entrar', login).follow().follow()
    response = self.app.get('/educopedia/aula/3/MAT')
    assert u'<!-- Tela de seleção de aulas -->' in response, "Erro: Não mostrou as aulas"

  def test_user_activity_slide(self):
    "Return the activity slide screen"
    self.app.post('/educopedia/cadastrar', registryeduco)
    self.app.post('/educopedia/entrar', login).follow().follow()
    response = self.app.get('/educopedia/aula/3/MAT/01/00')
    assert '<!-- conteudo do slide -->' in response, "Erro: Não mostrou os slides da atividade"

  def test_user_return_home(self):
    "Return the activity not found screen"
    self.app.post('/educopedia/cadastrar', registryeduco)
    self.app.post('/educopedia/entrar', login).follow().follow()
    response = self.app.get('/educopedia/aula/3/MAT/01/99')
    assert u'Atividade não encontrada' in response, "Erro: Não mostrou Atividade não encontrada"

  def test_user_home(self):
    "Return the home with the last activity screen"
    self.app.post('/educopedia/cadastrar', registryeduco)
    self.app.post('/educopedia/entrar', login).follow().follow()
    self.app.get('/educopedia/aula/3/MAT/01/00')
    self.app.get('/educopedia/sair')
    response = self.app.post('/educopedia/entrar', login).follow().follow()
    assert '<!-- conteudo do slide -->' in response, response #"Erro: Não mostrou ultima atividade"

#------ Acessos ---------------

  def test_educo_user_acessing_tnm(self):
    "Return the home from tnm screen, if the user made the registry through educopedia"
    self.app.post('/educopedia/entrar', login)
    response = self.app.get('/')
    assert u'<input type="image" src="/static/imagens/activ/ok.png" border="0"/>' in response, "Erro: Não exibiu tela de Home!"

  def test_professor_acessing_admin(self):
    "Return status forbidden, when trying to acess admin(professor)"
    self.app.post('/educopedia/cadastrar', registryeduco)
    self.app.post('/educopedia/entrar', login)
    response = self.app.get('/educopedia/admin', status='*')
    assert response.status[:3] == '403', "Erro: Não bloqueou acesso para o professor acessar admin"

  def test_aluno_acessing_admin(self):
    "Return status forbidden, when trying to acess admin(aluno)"
    self.app.post('/educopedia/cadastrar', registryeducoaluno)
    self.app.post('/educopedia/entrar', loginaluno)
    response = self.app.get('/educopedia/admin', status='*')
    assert response.status[:3] == '403', "Erro: Não bloqueou acesso para o aluno acessar admin"

# FALTA VER COMO TESTAR A PÁGINA INICIAL PARA ADMIN
#  def test_digitador_acessing_admin(self):
#    "Return"
#    self.app.post('/educopedia/cadastrar', registryeducodigitador)
#    self.app.post('/educopedia/entrar', logindigitador)
#    response = self.app.get('/educopedia/admin')
#    print response
#    assert u'<!-- *** página inicial tnm *** -->' in response, "Erro: Não exibiu tela aqui"

  def test_professor_acessing_admin_subjects(self):
    "Return status forbidden, when trying to acess admin(aluno)"
    self.app.post('/educopedia/cadastrar', registryeduco)
    self.app.post('/educopedia/entrar', login)
    response = self.app.get('/educopedia/admin/3/MAT/01', status='*')
    assert response.status[:3] == '403', "Erro: Não bloqueou acesso para o professor acessar a tela de editar atividades"

  def test_aluno_acessing_admin_subjects(self):
    "Return status forbidden, when trying to acess admin(aluno)"
    self.app.post('/educopedia/cadastrar', registryeducoaluno)
    self.app.post('/educopedia/entrar', loginaluno)
    response = self.app.get('/educopedia/admin/3/MAT/01', status='*')
    assert response.status[:3] == '403', "Erro: Não bloqueou acesso para o aluno acessar a tela de editar atividades"

  def test_digitador_acessing_admin_subjects(self):
    "Return the edit activities screen"
    self.app.post('/educopedia/cadastrar', registryeducodigitador)
    self.app.post('/educopedia/entrar', logindigitador)
    response = self.app.get('/educopedia/admin/3/MAT/01')
    assert u'form action="/educopedia/admin/3/MAT/01" enctype="multipart/form-data" method="post"' in response, "Erro: Não exibiu tela de editar atividades"

#-------- Criação/Edição de Slides ---------

  def test_slide_edit_screen(self):
    "Return the slide edit screen"
    self.app.post('/educopedia/cadastrar', registryeducodigitador)
    self.app.post('/educopedia/entrar', logindigitador)
    response = self.app.get('/educopedia/admin/3/MAT/01/00')
    assert 'form name="criarpagina" class="form_settings" action="/educopedia/admin/3/MAT/01/00" method="post"' in response, "Erro: Não exibiu a edição de slides"

  def test_edit_slide_not_found_screen(self):
    "Return the slide not found screen(digitador)"
    self.app.post('/educopedia/cadastrar', registryeducodigitador)
    self.app.post('/educopedia/entrar', logindigitador)
    response = self.app.get('/educopedia/admin/3/MAT/01/99')
    assert u'Atividade não encontrada' in response, "Erro: Não exibiu a tela de atividade não encontrada"

  def test_slide_edit(self):
    "Return the slide edited"
    self.app.post('/educopedia/cadastrar', registryeducodigitador)
    self.app.post('/educopedia/entrar', logindigitador)
    self.app.post('/educopedia/admin/3/MAT/01/00', registry_slide_edit)
    response = self.app.get('/educopedia/aula/3/MAT/01/00')
    assert u'Teste de edição de slide' in response, "Erro: Não editou o slide corretamente"

  def test_slide_create(self):
    "Return the slide creation screen"
    self.app.post('/educopedia/cadastrar', registryeducodigitador)
    self.app.post('/educopedia/entrar', logindigitador)
    response = self.app.get('/educopedia/admin/3/MAT/01/incluir')
    assert u'form name="criarpagina" class="form_settings" action="/educopedia/admin/3/MAT/01/incluir" method="post"' in response, "Erro: Não exibiu a tela de criação de slides"

  def test_slide_creation(self):
    "Return the slide created"
    self.app.post('/educopedia/cadastrar', registryeducodigitador)
    self.app.post('/educopedia/entrar', logindigitador)
    self.app.post('/educopedia/admin/3/MAT/01/incluir', registry_slide_edit)
    response = self.app.get('/educopedia/aula/3/MAT/01/02')
    assert u'Teste de edição de slide' in response, "Erro: Não criou o slide corretamente"
"""