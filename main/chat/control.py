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

import uuid
from datetime import datetime
from operator import itemgetter
import time

import tornado.httpserver
import tornado.web
import tornado.websocket
import tornado.ioloop
import tornado.gen

import tornadoredis

import tornado.auth
import tornado.escape
import tornado.options
import tornado.template

import model
from config import PLATAFORMA_URL
import core.model
from core.model import isFriend, isMember, isACommunity, isAUser
from core.dispatcher import BaseHandler, HANDLERS, URL_TO_PAGETITLE, \
                            NOMEUSERS
import log.model
from libs.dateformat import short_datetime

''' importa definição do tutorial deste módulo, se existir _tutorial.py '''
from config import TUTORIAL
try:
    import _tutorial
except ImportError:
    pass

# Formatação da mensagem armazenada no BD
#msg_chat = lambda user, msg: "<b>%s</b>: %s<div class='date'>%s</div>" % (user, msg, short_datetime(str(datetime.now()), include_year=False))

# Número máximo de mensagens exibidas num chat
NUM_MAX_CHAT_MSGS = 100

 
def msg_chat (user, msg):
    d = str(datetime.now())
    return "<div style='display:none'>%s</div><b>%s</b>: %s<div class='date'>%s</div>" % (d, user, msg, short_datetime(d, include_year=False))


class MyChatHandler(BaseHandler):
    """ Página com meus Chats """
    @tornado.web.authenticated
    #@tornado.web.asynchronous
    def get(self):
        self._user = self.get_current_user()
        
        # Minhas mensagens no chat:
        # /chat => Meus Amigos
        # /chat?type=C => Minhas Comunidades
        self._type = self.get_argument("type", "")
        
        # Recupera os nomes de todos os canais existentes ou 
        # das minhas conversas com amigos dependendo do parâmetro type
        pattern = "*"+self._user+"*" if self._type!="C" else "*"    
        #model.REDIS.keys(pattern, callback=self.async_callback(self.retrieve_channels))
        self.retrieve_channels(model.REDIS.keys(pattern))
        return

    def retrieve_channels(self, channel_list):
        # recupera a lista de todos os canais de chat de user
        self._msg_list = []
        if self._type != "C":
            # canais de chat usuário-usuário
            self._channel_list = [ channel for channel in channel_list if ":" in channel ]
        else:
            # canais de chat de comunidades que participo
            _member = core.model.Member().retrieve(self._user)
            self._channel_list = [ channel for channel in channel_list if ":" not in channel and channel in _member.comunidades]
           
        if self._channel_list:
            # recupera a última mensagem de cada canal
            for channel in self._channel_list:
                #model.REDIS.lrange(channel, 0, 0, callback=self.async_callback(self.retrieve_messages))   
                self.retrieve_messages(model.REDIS.lrange(channel, 0, 0))
        else:
            # se a lista de canais está vazia, gera uma página vazia
            tabs = []
            if self._type != "C":
                tabs.append(("Meus Amigos", ""))
                tabs.append(("Minhas Comunidades", "/chat?type=C"))
            else:
                tabs.append(("Meus Amigos", "/chat"))
                tabs.append(("Minhas Comunidades", ""))            
            self.render("modules/chat/mychat.html", REGISTRY_ID=self._user, \
                        TABS=tabs, \
                        LIST=[], NOMEPAG='chat')            
       
    def retrieve_messages(self, message_list):
        self._msg_list.extend(message_list)
        
        if len(self._msg_list) == len(self._channel_list):
            
            # junta tudo numa única lista de tuplas e ordena com os mais recentes primeiro
            self._list = zip(self._msg_list, self._channel_list)
            self._list = sorted(self._list, key=itemgetter(0), reverse=True)

            tabs = []
            if self._type != "C":
                tabs.append(("Meus Amigos", ""))
                tabs.append(("Minhas Comunidades", "/chat?type=C"))
            else:
                tabs.append(("Meus Amigos", "/chat"))
                tabs.append(("Minhas Comunidades", ""))

            log.model.log(self._user, u'acessou o seu chat', tipo="chat", news=False)
                                        
            self.render("modules/chat/mychat.html", REGISTRY_ID=self._user, \
                        TABS=tabs, \
                        LIST=self._list, NOMEPAG='chat')
            
        else:        
            return
        
                   
class ChatHandler(BaseHandler):
    """ Página do Chat de usuários e comunidades """
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabledToCommunity('chat')    
    #@tornado.web.asynchronous
    def get(self, registry_id):
        self._user = self.get_current_user()
        self._registry_id = registry_id

        if self._user==self._registry_id:
            self.redirect("/chat")
            return
        
        channel = model.channel_name(self._user, registry_id)
        
        if channel:
            self.retrieve_messages(model.REDIS.lrange(channel, 0, NUM_MAX_CHAT_MSGS))
            
        else:
            self.render("home.html", NOMEPAG='chat', \
                        MSG=u"Acesso negado a este Chat.", \
                        REGISTRY_ID=registry_id)
                
    def retrieve_messages(self, msg_list):
        # e se o chat for de comunidade? precisa fazer isso?
        
        self._msg_list = msg_list
        self.retrieve_notify(model.REDIS.lrange(self._user, 0, NUM_MAX_CHAT_MSGS))

    def retrieve_notify(self, msg_notify):
        _notification = model.NotificationChat().retrieve(self._user)
        if _notification:
            _notification.deleteItem(self._registry_id)
            _notification.save()
            
        # remove todas as notificações do registry_id para o user 
        for msg in msg_notify:
            if "<b>"+self._registry_id+"</b>: " in msg.decode('utf-8'):
                # count=0 => remove todas as ocorrencias de msg em self._user
                model.REDIS.lrem(self._user, 0, msg)
           
        log.model.log(self._user, u'acessou o chat de', objeto=self._registry_id, tipo="chat", news=False)   
                
        # exibe página do Chat     
        self.render("modules/chat/chat.html", REGISTRY_ID=self._registry_id, \
                    MSG_LIST=self._msg_list, NOMEPAG='chat')
        

class MessageNewHandler(BaseHandler):
    """ Envio de mensagem no Chat

        Sempre que uma mensagem de chat é enviada, ela é publicada num canal (PUBLISH) e armazenada numa lista (LPUSH) com mesmo nome.
        Estes nomes possuem a seguinte regra de formação:
            Chat entre dois usuários: "user1:user2" em ordem alfabética
            Chat de uma comunidade: "nome-da-comunidade"

        Além disso, as notificações para um usuário também são publicadas e armazenadas numa lista com nome "login-do-usuário". 
        Esta informação será utilizada no controlador que exibe notificações: /chat/%s/messages
        Não confundir com as notificações por email que são armazenadas no couchdb.
    """
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabledToCommunity('chat')    
    def post(self, registry_id):
        user = self.get_current_user()
        message = self.get_argument('message')
        channel_chat = model.channel_name(user, registry_id)
        channel_notify = registry_id
        
        if channel_chat:
            msg = msg_chat(user, message)
           
            
            model.REDIS_PUBSUB.publish(channel_chat, msg)
            model.REDIS_PUBSUB.lpush(channel_chat, msg)
            log.model.log(user, u'escreveu no chat de', objeto=registry_id, tipo="chat", news=False)
            
            # publica no canal de notificações somente se a conversa não é em comunidade e o usuário com quem eu falo não está no chat
            if ":" in channel_chat and (channel_chat not in model.USUARIOS_NO_CHAT or registry_id not in model.USUARIOS_NO_CHAT[channel_chat]):            
                model.REDIS_PUBSUB.publish(channel_notify, msg)
                model.REDIS_PUBSUB.lpush(channel_notify, msg)
              
                # Armazena no couchdb a notificação que será enviada por email pela thread
                self._notification = model.NotificationChat().retrieve(registry_id)
                if self._notification:
                    self._notification.registros.append(msg)
                    self._notification.save()
                    
                else:
                    self._reg = core.model.Member().retrieve(registry_id)
                    self._notification = model.NotificationChat()
                    self._notification.email = self._reg.email
                    self._notification.name = self._reg.name
                    self._notification.registros = [msg]
                    self._notification.save(id=registry_id)
                      
            #self.set_header('Content-Type', 'text/plain')
            #self.write('sent: %s' % (message))


class MessageUpdatesHandler(BaseHandler, tornado.websocket.WebSocketHandler):
    """ Atualiza um chat recebendo novas mensagens """
    _channel_chat = None
    _channel_notify = None
    
    def __init__(self, *args, **kwargs):
        super(MessageUpdatesHandler, self).__init__(*args, **kwargs)

    def user_online(self):
        # acrescenta usuário no dicionário USUARIOS_NO_CHAT quando ele entra no chat
        user = self.get_current_user()
        if self._channel_chat in model.USUARIOS_NO_CHAT:
            if user not in model.USUARIOS_NO_CHAT[self._channel_chat]:
                model.USUARIOS_NO_CHAT[self._channel_chat].append(user)
        else:
            model.USUARIOS_NO_CHAT[self._channel_chat] = [user]
        #print "inclui USUARIOS_NO_CHAT=", model.USUARIOS_NO_CHAT
            
    def user_offline(self):
        # retira usuário no dicionário USUARIOS_NO_CHAT quando ele sai do chat
        user = self.get_current_user()
        if self._channel_chat in model.USUARIOS_NO_CHAT:
            if user in model.USUARIOS_NO_CHAT[self._channel_chat]:
                model.USUARIOS_NO_CHAT[self._channel_chat].remove(user)
            if not model.USUARIOS_NO_CHAT[self._channel_chat]:
                del model.USUARIOS_NO_CHAT[self._channel_chat]                
        #print "removi USUARIOS_NO_CHAT=", model.USUARIOS_NO_CHAT
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabledToCommunity('chat')    
    def open(self, registry_id):
        user = self.get_current_user()
        #print "open: ", user, "-", registry_id
        self._channel_chat =  model.channel_name(user, registry_id)
        self._channel_notify = registry_id
        #print "MessagesUpdate, open, channel_chat = ", self._channel_chat
        self.listen()
        
        # acrescenta mensagem de entrada se o canal for de uma comunidade
        if self._channel_chat and ":" not in self._channel_chat:
            model.REDIS_PUBSUB.publish(self._channel_chat, msg_chat(user, "Entrou no Chat."))
            model.REDIS_PUBSUB.lpush(self._channel_chat, msg_chat(user, "Entrou no Chat."))
               
    #@tornado.gen.engine
    @tornado.gen.coroutine
    def listen(self):
        #print "listen: MessagesUpdate, listen channel_chat = ", self._channel_chat
        self.client = tornadoredis.Client()
        self.client.connect()
        
        if self._channel_chat:
            #print u"self._channel_chat é True"
            yield tornado.gen.Task(self.client.subscribe, self._channel_chat)
            #print "USUARIOS_NO_CHAT=", model.USUARIOS_NO_CHAT
            self.client.listen(self.on_message)
            
            self.user_online()
            
        else:
            #print u"self._channel_chat é False"
            yield tornado.gen.Task(self.client.subscribe, self._channel_notify)    
            self.client.listen(self.on_message)  

    def on_message(self, msg):
        #print "on_message: ", msg.kind
        
        
        if msg.kind == 'message':
            self.write_message(str(msg.body.encode('utf-8')))
        if msg.kind == 'disconnect':
            # Do not try to reconnect, just send a message back
            # to the client and close the client connection
            self.write_message('The connection terminated due to a Redis server error.')
            self.close()

    def on_close(self):
        #print "on_close: "
        if self.client.subscribed:        
            user = self.get_current_user()

            # acrescenta mensagem de saída se o canal for de uma comunidade
            if self._channel_chat and ":" not in self._channel_chat:
                model.REDIS_PUBSUB.publish(self._channel_chat, msg_chat(user, "Saiu do Chat."))
                model.REDIS_PUBSUB.lpush(self._channel_chat, msg_chat(user, "Saiu do Chat."))
            
            # Persiste dados do chat sempre que alguem sai
            model.REDIS_PUBSUB.save()
            model.REDIS.save()
            
            if self._channel_chat:
                self.client.unsubscribe(self._channel_chat)
                self.user_offline()
            else:
                self.client.unsubscribe(self._channel_notify)

            self.client.disconnect()


class MessagesHandler(BaseHandler):
    """ Lista todas as notificações de Chat com as mensagens recebidas pelo registry_id enquanto ele estava offline """
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    #@tornado.web.asynchronous
    def get(self, registry_id):
        self._user = self.get_current_user()
        self._registry_id = registry_id

        if self._user==registry_id:
            _notification = model.NotificationChat().retrieve(self._user)
            if _notification:
                _notification.delete()  
                       
            self.retrieve_messages(model.REDIS.lrange(registry_id, 0, NUM_MAX_CHAT_MSGS))
        else:
            self.render("home.html", NOMEPAG='chat', \
                        MSG=u"Acesso inválido.", REGISTRY_ID=user)
    
    def retrieve_messages(self, msg_list):
        # gera página com lista de notificações para registry_id
        
        links = []
        if msg_list:
            links.append((u"Limpar notificações", "/static/imagens/icones/delete32.png", "/chat/"+self._registry_id+"/clear"))

        log.model.log(self._user, u'acessou notificações de chat de', objeto=self._registry_id, tipo="chat", news=False)                    
        self.render("modules/chat/chat-messages.html", \
                    REGISTRY_ID=self._registry_id, \
                    MSG_LIST=msg_list, \
                    LINKS=links, \
                    NOMEPAG='chat')


class NotificationsClearHandler(BaseHandler):
    """ Remove todas as mensagens de notificação de Chat recebidas pelo registry_id """
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    #@tornado.web.asynchronous
    def get(self, registry_id):
        user = self.get_current_user()
        self._registry_id = registry_id

        if user==registry_id:
            self.retrieve_messages(model.REDIS.delete(self._registry_id))
        else:
            self.render("home.html", NOMEPAG='chat', \
                        MSG=u"Acesso inválido.", REGISTRY_ID=user)
    
    def retrieve_messages(self, delete_status):
        self.redirect("/chat/%s/messages" % self._registry_id)
 
  
class NumNotificationsHandler(BaseHandler):
    """ Retorna JSON com número de notificações de chat para um registry_id """
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabledToCommunity('chat')    
    #@tornado.web.asynchronous
    def get(self, registry_id):
        user = self.get_current_user()
        self.retrieve_num_notifications(model.REDIS.llen(registry_id))
                
    def retrieve_num_notifications(self, num):
        self.write(dict(status=0, result=num))
        self.finish()


""" Testes para funcionar o funcionamento do WebSocket """
 
class EchoWebSocket(tornado.websocket.WebSocketHandler):
    def open(self):
        print "WebSocket opened"

    def on_message(self, message):
        self.write_message(u"You said: " + message)

    def on_close(self):
        print "WebSocket closed"
              
class TestWebSocket(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("modules/chat/websocket-test.html", NOMEPAG="Chat")
        
                                              
URL_TO_PAGETITLE.update ({
        "chat": "Chat"
    })

HANDLERS.extend([
            (r"/chat",                                MyChatHandler),
            (r"/chat/%s" % (NOMEUSERS),               ChatHandler),
            (r"/chat/%s/new" % (NOMEUSERS),           MessageNewHandler),
            (r"/chat/%s/updates" % (NOMEUSERS),       MessageUpdatesHandler),
            (r"/chat/%s/messages" % (NOMEUSERS),      MessagesHandler),
            (r"/chat/%s/clear" % (NOMEUSERS),         NotificationsClearHandler),
            (r"/chat/%s/notifications" % (NOMEUSERS), NumNotificationsHandler),
            (r"/websocket", EchoWebSocket),
            (r"/websocket/test", TestWebSocket)
    ])
