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
:Home: `LABASE `__
:Copyright: ©2009, `GPL 
"""
from couchdb import Server
import urllib

import smtplib
import sys

_DOCBASES = ['magkeys']

# SMTP do IG
#SMTP = {
#            'servidor': 'smtp-p.ig.com.br',
#            'porta': 25,
#            'remetente': 'oitonomundo@oi.com.br'
#            }

# SMTP do NCE/UFRJ
SMTP = {
            'servidor': 'smtp.ufrj.br',
            'porta': 25,
            'remetente': 'projetoactiv@nce.ufrj.br'
            }

""" Lista de futuros usuários. activufrj """
PLATAFORMA = "ActivUFRJ"
PLATAFORMA_URL = "activufrj.nce.ufrj.br"
_EMPTYALLOWED_USERS= lambda: dict(
        # _id = <email>
          email = ""          # fulano@qualquer.coisa
        , nome = ""           # nome completo    
        , papel = ""          # aluno, docente
        , magic = ""          # chave de cadastro
        , comunidade = []     # se houver comunidade default
        , CPF = ""
        , curso_codigo_SIGA = ""
        , curso = ""
        , Matricula_UFRJ = ""
        , curso_centro = ""
        , curso_unidade = ""
        , Orientador = ""
        , Email_Orientador = ""
)
_MAGKEYTYPES = dict(
      super_usuario = dict(
                      papeis = [ "super_usuario", "docente", "docente_externo", "funcionario", "aluno", "aluno_externo", "estagiario", "comunidade", "usuario_externo"],
                      codigo="su"
                      ),
      docente = dict(
                      papeis = ["comunidade"],
                      codigo="do"
                      ),
      docente_externo = dict(
                      papeis = [],
                      codigo="de"
                      ),
      funcionario = dict(
                      papeis = ["comunidade"],
                      codigo="fu"
                      ),
      estagiario = dict(
                       papeis = [],
                       codigo="es"
                       ),
      aluno = dict(
                papeis = [],
                codigo="al"
                ),
      aluno_externo = dict(
                       papeis = [],
                       codigo="ae"
                       ),
      usuario_externo = dict(
                       papeis = [],
                       codigo="ue"
                       ),
      comunidade = dict(
                       papeis = [],
                       codigo="co"
                       )
)
text_message = lambda: dict(
    docente = 
              u"Prezado %s, orientador de IC, \n" +\
              u"\n" +\
              u"Estamos apresentando para você o 'ActivUFRJ - Ambiente Cooperativo " +\
              u"de Trabalho Integrado e Virtual', criado por um grupo de pesquisa do " +\
              u"Instituto Tércio Pacitti de Aplicações e Pesquisas Computacionais (NCE). " +\
              u"Agora, o ActivUFRJ em parceria com o PIBIC e a JIC vem convidá-lo a participar " +\
              u"deste projeto que tem o objetivo de dinamizar as relações institucionais " +\
              u"dentro do programa de Iniciação Científica. Através do ActivUFRJ você poderá encontrar " +\
              u"alunos e docentes com interesses semelhantes, trocar informações, protocolos, apresentações, " +\
              u"artigos científicos e muito mais. Através do ActivUFRJ você também poderá tirar dúvidas " +\
              u"sobre o PIBIC e a JIC e outros programas da Universidade. Esperamos que no próximo ano " +\
              u"o ActivUFRJ se torne também um instrumento de divulgação e organização da Jornada.\n\n" +\
              u"O ActivUFRJ está sempre em construção, como todos os ambientes computacionais. " +\
              u"Estamos trabalhando para incluir ferramentas que poderão, por exemplo, recomendar trabalhos " +\
              u"que podem interessar aos usuários (sistema de recomendação), sugerir pessoas que possam " +\
              u"interagir (combinação social), reconhecer as melhores contribuições em fórum de discussão (reputação), " +\
              u"entre outras funcionalidades." +\
              u"A idéia é que não precisemos mais contar apenas com a sorte para encontrar pessoas que tem o mesmo " +\
              u"interesse que o nosso.\n\n" +\
              u"O ActivUFRJ conta com sua participação para que esta ferramenta possa se tornar um diferencial " +\
              u"na sua vida acadêmica.\n" +\
              u"Para entrar no ActivUFRJ, utilize o endereço abaixo e cadastre-se.\n\n" + \
              u"http://%s/new/user?mkey=%s \n\n" +\
              u"Seja bem vindo e faça bom uso do ActivUFRJ, \n" +\
              u"\n" +\
              u"Lina Zingali\n" +\
              u"Coordenação PIBIC e JIC UFRJ\n",
    aluno = 
              u"Prezado %s, aluno de IC, \n\n" +\
              u"\n" +\
              u"Estamos apresentando para você o 'ActivUFRJ - Ambiente Cooperativo " +\
              u"de Trabalho Integrado e Virtual', criado por um grupo de pesquisa do " +\
              u"Instituto Tércio Pacitti de Aplicações e Pesquisas Computacionais (NCE). " +\
              u"Agora, o ActivUFRJ em parceria com o PIBIC e a JIC vem convidá-lo a participar " +\
              u"deste projeto que tem o objetivo de dinamizar as relações institucionais " +\
              u"dentro do programa de Iniciação Científica. Através do ActivUFRJ você poderá encontrar " +\
              u"alunos e docentes com interesses semelhantes, trocar informações, protocolos, apresentações, " +\
              u"artigos científicos e muito mais. Através do ActivUFRJ você também poderá tirar dúvidas " +\
              u"sobre o PIBIC e a JIC e outros programas da Universidade. Esperamos que no próximo ano " +\
              u"o ActivUFRJ se torne também um instrumento de divulgação e organização da Jornada.\n\n" +\
              u"O ActivUFRJ está sempre em construção, como todos os ambientes computacionais. " +\
              u"Estamos trabalhando para incluir ferramentas que poderão, por exemplo, recomendar trabalhos " +\
              u"que podem interessar aos usuários (sistema de recomendação), sugerir pessoas que possam " +\
              u"interagir (combinação social), reconhecer as melhores contribuições em fórum de discussão (reputação), " +\
              u"entre outras funcionalidades." +\
              u"A idéia é que não precisemos mais contar apenas com a sorte para encontrar pessoas que tem o mesmo " +\
              u"interesse que o nosso.\n\n" +\
              u"O ActivUFRJ conta com sua participação para que esta ferramenta possa se tornar um diferencial " +\
              u"na sua vida acadêmica e na sua formação.\n" +\
              u"Para entrar no ActivUFRJ, utilize o endereço abaixo e cadastre-se.\n\n" + \
              u"http://%s/new/user?mkey=%s \n\n" +\
              u"Seja bem vindo e faça bom uso do ActivUFRJ, \n" +\
              u"\n" +\
              u"Lina Zingali\n" +\
              u"Coordenação PIBIC e JIC UFRJ\n"
)

class Activ(Server):
    "Active database"
    
    def __init__(self, url):
        print "iniciando o servidor..."
        Server.__init__(self, url)
        act = self
        test_and_create = lambda doc: doc in act and act[doc] or act.create(doc)
        for attribute in _DOCBASES:
            setattr(Activ, attribute, test_and_create(attribute))
                
    def erase_database(self):
        'erase tables'
        for table in _DOCBASES:
            try:
                del self[table]
            except:
                pass

__ACTIV = Activ('http://127.0.0.1:5984/')
USERS_JIC = __ACTIV.magkeys

"""
Este programa envia e-mail com convite/chave mágica para acesso à plataforma activ para todos
os emails  no documento MAGKEYS
"""
def main(argv):

    if len(argv) == 1:
          papel = argv[0]
          if papel != "docente" and papel != "aluno":
               print "Uso: envia_email_user_jic.py docente|aluno"
               exit()
    else:
          #papel = "jic"
          print "Uso: envia_email_user_jic.py docente|aluno"
          exit()
          
    ''' Envia E-mail com link magic Key para cadastro na plataforma '''
    codigo = _MAGKEYTYPES[papel]["codigo"]
    user_data = _EMPTYALLOWED_USERS()
    texto_data = text_message()
    message = ""
    for chave in USERS_JIC:
        user_data.update(USERS_JIC[chave])
        #Envia somente para o papel chave[0:2] == codigo e uma outra instrucao qualquer. No caso da JIC,
        # a instrucao é que o email convidado tenha jicac2011 como comunidade default em seu documento
        if chave[0:2] == codigo and ('comunidades' in user_data and 'jicac2011' in user_data['comunidades']):
             sender = SMTP['remetente']
             receivers = user_data["email"]
             message = (u"From: Projeto Activ <projetoactiv@nce.ufrj.br>\n" +\
                        u"To: %s <%s>\n" +\
                        u"Subject: Convite para a Plataforma ActivUFRJ\n\n") %\
                           (user_data["email"], user_data["nome"]) +\
                        texto_data[papel] % (user_data["nome"], PLATAFORMA_URL, chave)
             try:
               smtpObj = smtplib.SMTP(SMTP['servidor'], SMTP['porta'])
               #Print de teste - comentar quando for enviar as mensagens
               print "Enviando para: ",  chave, user_data["nome"], user_data["email"]

               # Descomentar as pŕóximas 3 linhas quando desejar enviar os e-mails...

               #smtpObj.sendmail(sender, receivers, message.encode('utf-8'))
               #smtpObj.quit()
               #print u"Mensagem enviada para: %s" % user_data["email"]
             
             except smtplib.SMTPException as detail:
               print u"Erro no envio do E-mail para %s.\n%s" % (user_data["email"], detail)
               
    #print "message=", message

if __name__ == "__main__":
    main(sys.argv[1:])                 

