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

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

import core.model as model
from core.model import isAUser, isACommunity
import core.database as database
import log.model
from log.database import _EMPTYNOTIFICATION, _EMPTYNOTIFICATIONERROR
from config import SMTP, PLATAFORMA, PLATAFORMA_URL, \
                   DEBUG_EMAIL, ENVIAR_EMAIL_DE_LOCALHOST, \
                   LOG_THREADS, LOG_THREADS_FILE, DIR_RAIZ_ACTIV

from libs.dateformat import short_datetime
from libs.strformat import remove_non_latin1



def _enviaEmail (destinatario, assunto, msgTxt, msgHtml):
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = assunto
    msg['From'] = SMTP['remetente']
    msg['To'] = destinatario
    
    # Create the body of the message (a plain-text and an HTML version).
    #msgTxt = msgTxt.encode('utf-8')
    #msgHtml = msgHtml.encode('utf-8')
    
    msgTxt = msgTxt.encode('iso8859-1')
    msgHtml = msgHtml.encode('iso8859-1')
    
    
    #msgTxt = remove_non_latin1(msgTxt).encode('iso8859-1')
    #msgHtml = remove_non_latin1(msgHtml).encode('iso8859-1')


    
    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(msgTxt, 'plain')
    part2 = MIMEText(msgHtml, 'html')
    
    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)
    
    try:
        smtpObj = smtplib.SMTP(SMTP['servidor'], SMTP['porta'])
        # teste do e-mail enviado
        if DEBUG_EMAIL:
            print "Enviando email"
            print "destinatario=", destinatario
            print "msg=", msg.as_string()
        if PLATAFORMA_URL != "localhost:8888" or ENVIAR_EMAIL_DE_LOCALHOST:
            smtpObj.sendmail(SMTP['remetente'], destinatario.split(","), msg.as_string()) # message.encode('utf-8'))
        smtpObj.quit()
        return True
    except smtplib.SMTPException:
       return False
    except smtplib.SMTPConnectError:
       return False

class Notify:
    
#Situações em que o usuário será notificado:
#
#blog
#notifica o dono do post comentado
#
#forum
#notifica o dono do tópico respondido
#
#mblog
#notifica todos os usuários mencionados por uma mensagem (ignora se uma comunidade for mencionada)
#se uma mensagem for compartilhada, notifica seu dono
#
#scrapbook
#notifica usuário que recebeu um recado
#
#wiki
#notifica dono de página alterada
#notifica dono de página removida
#
#file
#notifica dono de arquivo removido
#
#friend
#notifica usuário ao receber convite de amizade
#
#community
#notifica usuário ao receber convite para participar de comunidade
#notifica usuário ao ser incluído numa comunidade obrigatória
#
    @classmethod
    def email_notify_old(cls, user, sujeito, assunto, message="", link=""):
        if user!=sujeito and isAUser(user) and isAUser(sujeito):
            
            # usuário a ser avisado
            to_user_data = model._EMPTYMEMBER()
            to_user_data.update(database.REGISTRY[user])
            email = to_user_data["email"]
            notify = to_user_data["notify"]
            nome_destinatario = to_user_data["name"]
            
            # usuário que realizou a ação
            from_user_data = database.REGISTRY[sujeito]
            nome_completo = from_user_data["name"] + " " + from_user_data["lastname"]
            assunto = nome_completo + " " + assunto
            
            if notify == "2":
                # envia e-mail imediatamente
                if not Notify.enviaEmail (email, assunto, nome_destinatario, message, link):
                    # erro no envio do e-mail: guarda mensagem em NOTIFICATIONERROR
                    notify_data = _EMPTYNOTIFICATIONERROR()
                    if user in log.database.NOTIFICATIONERROR:
                        notify_data.update(log.database.NOTIFICATIONERROR[user])
                    reg = dict(
                               sujeito= sujeito,
                               subject= assunto,
                               message= message,
                               data_inclusao= str(datetime.now())
                    )
                    notify_data["registros"].append(reg)
                    log.database.NOTIFICATIONERROR[user] = notify_data
                    #print "Erro no envio do email. Msg salva em NOTIFICATIONERROR"
                else:
                    #print "Email enviado com sucesso para "+email
                    pass
                    
            elif notify == "1":
                # guarda mensagem no banco para depois enviar resumo semanal
                notify_data = _EMPTYNOTIFICATION()
                if user in log.database.NOTIFICATION:
                    notify_data.update(log.database.NOTIFICATION[user])
                reg = dict(
                           sujeito= sujeito,
                           subject= assunto,
                           message= message,
                           data_inclusao= str(datetime.now())
                )
                notify_data["registros"].append(reg)
                log.database.NOTIFICATION[user] = notify_data
                #print "Email salvo em NOTIFICATION"
            else:
                #print "Usuário não deseja ser notificado"
                pass
        
    @classmethod
    def email_notify(cls, user, sujeito, assunto, message="", link="", sendToMyself=False):
        # user -> quem deve ser avisado
        # sujeito -> quem realizou a ação
        # sendToMyself=True indica que a mensagem deve ser enviada para mim, mesmo que eu tenha realizado a ação. Ex: troca de senha.
        
        if (sendToMyself or user!=sujeito) and isAUser(sujeito):
            if isAUser(user):
                # usuário a ser avisado
                to_user_data = model._EMPTYMEMBER()
                to_user_data.update(database.REGISTRY[user])
                email = to_user_data["email"]
                notify = to_user_data["notify"]
                nome_destinatario = to_user_data["name"]
                
                # usuário que realizou a ação
                from_user_data = database.REGISTRY[sujeito]
                nome_completo = from_user_data["name"] + " " + from_user_data["lastname"]
                assunto = sendToMyself and assunto or nome_completo + " " + assunto
                
                if notify == "2":
                    # envia e-mail imediatamente
                    if not Notify.enviaEmail (email, assunto, nome_destinatario, message, link):
                        # erro no envio do e-mail: guarda mensagem em NOTIFICATIONERROR
                        notify_data = _EMPTYNOTIFICATIONERROR()
                        if user in log.database.NOTIFICATIONERROR:
                            notify_data.update(log.database.NOTIFICATIONERROR[user])
                        reg = dict(
                                   sujeito= sujeito,
                                   subject= assunto,
                                   message= message,
                                   data_inclusao= str(datetime.now())
                        )
                        notify_data["registros"].append(reg)
                        log.database.NOTIFICATIONERROR[user] = notify_data
                        #print "Erro no envio do email. Msg salva em NOTIFICATIONERROR"
                    else:
                        #print "Email enviado com sucesso para "+email
                        pass
                        
                elif notify == "1":
                    # guarda mensagem no banco para depois enviar resumo semanal
                    notify_data = _EMPTYNOTIFICATION()
                    if user in log.database.NOTIFICATION:
                        notify_data.update(log.database.NOTIFICATION[user])
                    reg = dict(
                               sujeito= sujeito,
                               subject= assunto,
                               message= message,
                               data_inclusao= str(datetime.now())
                    )
                    notify_data["registros"].append(reg)
                    log.database.NOTIFICATION[user] = notify_data
                    #print "Email salvo em NOTIFICATION"
                else:
                    #print "Usuário não deseja ser notificado"
                    pass
                    
            elif isACommunity(user):
                for participante in database.REGISTRY[user]["participantes"]:
                    Notify.email_notify(participante, sujeito, assunto, message, link)
            
        
    @classmethod
    def assinatura (cls, user, registry_id, data):
        str = user
        if model.getType(registry_id)[0]=="community":
            str += " na comunidade %s" % registry_id
        str += u" em %s" % short_datetime(data)
        return str

    @classmethod
    def enviaEmail (cls, email, assunto, nome, msg, link):
        assunto = assunto.encode('utf-8')
        nome = nome.encode('utf-8')
        
        # remove todos os caracteres que poderiam provocar erro ao codificar como iso8859-1
        msg = remove_non_latin1(msg, control=True).encode('utf-8')
        
        msgTxt  = u"Olá " + nome.decode('utf-8') + "\n\n" + msg.decode('utf-8') + "\n"
        
        msgHtml = u"""
                    <html>
                      <head></head>
                      <body>
                      <table>
                      <tr><td style="padding:10px;background-color:rgb(12,100,155);color:#fff;border-left:none;border-right:none;border-top:none;border-bottom:none;font-size:18px;font-family:tahoma,verdana,arial,sans-serif"><b>%s</b></td></tr>
                      <tr><td>
                      <!-- Saudação -->
                      <p>Olá %s,</p>
                      <!-- Título -->
                      <p>%s.</p>
                      <!-- Mensagem -->
                      <blockquote><i>%s</i></blockquote>
                      <br/>
                        <table border="1"><tr><td style="vertical-align: middle; background: #606060;">
                        <a href="http://%s/%s" style="text-decoration: none; width: 150px; height: 24px; font-size: 12px; font-family: arial, helvetica, sans-serif; font-weight: bold; text-align: center; color: #ffffff;">Ir para o ActivUFRJ</a>
                        </td></tr></table>
                      </td></tr>
                      <tr><td>&nbsp;</td></tr>
                      <tr><td style="padding:10px;color:#ccc;border-left:none;border-right:none;border-top:1px solid #ccc;border-bottom:none;font-size:10px;font-family:tahoma,verdana,arial,sans-serif">
                      Esta mensagem foi enviada para %s. Se você não desejar mais receber estes emails do %s, você pode fazer esta opção no seu perfil. NCE/UFRJ
                      </td></tr>
                      </table>
                      </body>
                    </html>""" \
                    % (PLATAFORMA, nome.decode('utf-8'), assunto.decode('utf-8'), msg.replace("\n", "<br/>").decode('utf-8'), \
                       PLATAFORMA_URL, link, email, PLATAFORMA)

        return _enviaEmail (email, PLATAFORMA+": "+assunto, msgTxt, msgHtml)


    @classmethod
    def batch_notify(cls):
        num = 0
        data_inicio = str(datetime.now())
        for user in log.database.NOTIFICATION:
            if "_design/" in user or user in ['_id', '_rev']:
                continue
            
            # usuário a ser avisado
            to_user_data = database.REGISTRY[user]
            email = to_user_data["email"]
            nome_destinatario = to_user_data["name"]
            assunto = u"Veja o que aconteceu recentemente por aqui"
            msg = ""
            for registro in log.database.NOTIFICATION[user]["registros"]:
                msg = msg + registro["subject"] + "\n" +\
                            registro["message"] + "\n" +\
                            "\n----------------------------------------\n\n"
                
            if Notify.enviaEmail (email, assunto, nome_destinatario, msg, "user/"+user):
                # print "Email enviado com sucesso para " + email
                del log.database.NOTIFICATION[user]
                num = num + 1

            #else:
            #print "Erro no envio do email para " + email

        if LOG_THREADS:
            # se estiver rodando em localhost e ENVIAR_EMAIL_DE_LOCALHOST for False 
            # não envia o email apesar da mensagem do log dizer que enviou
            text_file = open(DIR_RAIZ_ACTIV+LOG_THREADS_FILE, "a+")
            text_file.write(u"[%s - %s] Notifier: %d emails enviados.\n" % (data_inicio, str(datetime.now()), num))
            text_file.close()
        
