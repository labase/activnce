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

from libs.notify import Notify
from core.model import REGISTRY
from log.model import NOTIFICATION

# Este módulo só deve ser chamado a partir de utilrun.py
#

def notify():

    for user in NOTIFICATION:
        if user not in ['_id', '_rev']:
            # usuário a ser avisado
            to_user_data = REGISTRY[user]
            email = to_user_data["email"]
            nome_destinatario = to_user_data["name"]
            assunto = u"Veja o que aconteceu recentemente por aqui"
            msg = ""
            for registro in NOTIFICATION[user]["registros"]:
    
                msg = msg + registro["subject"] + "\n" +\
                            registro["message"] + "\n" +\
                            "\n----------------------------------------\n\n"
                
            if Notify.enviaEmail (email, assunto, nome_destinatario, msg, "user/"+user):
                print "Email enviado com sucesso para " + email
                
                try:
                    del NOTIFICATION[user]
                except:
                    print "Erro na exclusão de registro: " + user
                

            else:
                print "Erro no envio do email para " + email
    
if __name__ == "__main__":
    pass