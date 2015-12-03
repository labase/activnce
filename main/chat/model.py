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

from datetime import datetime

try:
  from couchdb.schema import Document, TextField, IntegerField, LongField, DateTimeField, DictField, ListField, Schema, FloatField
except ImportError:
  from couchdb.mapping import Document, TextField, IntegerField, LongField, DateTimeField, DictField, ListField, FloatField
  from couchdb.mapping import Mapping as Schema
  
import tornadoredis
import redis

import database
from core.model import isFriend, isMember, isACommunity, isAUser
from config import LOG_THREADS, LOG_THREADS_FILE, DIR_RAIZ_ACTIV
from libs.notify import Notify

# USUARIOS_NO_CHAT: Controle de usuários online no Chat de comunidades
# para notificação no popup de notícias.
# { 
#    channel_name: [user1, user2, ...],
#    'user1:user2': [user1, user2]
#    ...
# }
USUARIOS_NO_CHAT = dict()


#
# channel_name: se comunidade => é o registry_id da comunidade
#               se conversa entre amigos => user1:user2
#
def channel_name(user, registry_id):
    if isACommunity(registry_id):
        if isMember(user, registry_id):   
            return registry_id
        else:
            return None
            
    else:
        if isFriend(user, registry_id):
            channel = [user, registry_id]   
            channel.sort()
            return ":".join(channel)
        else:
            return None
  
def getUsuariosNoChat(registry_id):
    # retorna lista de usuários no chat de uma comunidade
    if registry_id in USUARIOS_NO_CHAT:
        return USUARIOS_NO_CHAT[registry_id]
    else:
        return []


# iniciando conexão com o REDIS
REDIS_PUBSUB = tornadoredis.Client()
REDIS_PUBSUB.connect()

REDIS = redis.StrictRedis(host='localhost', port=6379, db=0)
#REDIS_PUBSUB = REDIS.pubsub()





class NotificationChat(Document):
    # _id       = <registry_id>
    email       = TextField() 
    name        = TextField() 
    registros   = ListField(TextField())

    def deleteItem(self, registry_id):
        ''' remove todos os itens de registry_id na lista de registros de notificações do chat de user '''
        registros = []
        registros.extend(self.registros)
        for item in registros:
            if "<b>%s</b>: " % registry_id in item:
                self.registros.remove(item)
            
    def save(self, id=None, db=database.NOTIFICATION_CHAT):
        if not self.id and id: self.id = id
        self.store(db)
        
    def retrieve(self, id, db=database.NOTIFICATION_CHAT):
        return NotificationChat.load(db, id)
    
    def delete(self, db=database.NOTIFICATION_CHAT):
        #db.delete(self)
        del db[self.id]


def batch_notify():
    num = 0
    data_inicio = str(datetime.now())
    for user in database.NOTIFICATION_CHAT:
        if "_design/" in user or user in ['_id', '_rev']:
            continue
        
        # usuário a ser avisado
        assunto = u"Mensagens de chat para você"
        msg = ""
        _notification = NotificationChat().retrieve(user)
        email = _notification.email
        nome_destinatario = _notification.name
        for reg in _notification.registros:
            msg = msg + reg + "\n" + \
                  "----------------------------------------\n\n"
            
        if Notify.enviaEmail (email, assunto, nome_destinatario, msg, "chat/"+user+"/messages"):
            # print "Email enviado com sucesso para " + email
            _notification.delete()
            num = num + 1

        #else:
        #print "Erro no envio do email para " + email

    if LOG_THREADS:
        # se estiver rodando em localhost e ENVIAR_EMAIL_DE_LOCALHOST for False 
        # não envia o email apesar da mensagem do log dizer que enviou
        text_file = open(DIR_RAIZ_ACTIV+LOG_THREADS_FILE, "a+")
        text_file.write(u"[%s - %s] ChatNotifier: %d emails enviados.\n" % (data_inicio, str(datetime.now()), num))
        text_file.close()
        