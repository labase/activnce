# -*- coding: utf-8 -*-
"""
################################################
Oi Tonomundo - NCE/UFRJ
################################################

:Author: Eduardo Paz
:Contact: edupaz@nce.ufrj.br
:Date: $Date: 2010/08/02  $
:Status: This is a "work in progress"
:Revision: $Revision: 0.01 $
:Home: ``
:Copyright:  
"""
from datetime import datetime
from uuid import uuid4

import tornado.web
import tornado.template
from tornado.web import HTTPError

from config import PLATAFORMA_URL
import model
import core.model
from core.model import isOwner, isMember, isUserOrOwner
from core.dispatcher import BaseHandler, HANDLERS, URL_TO_PAGETITLE, \
                            NOMEUSERS, NUMERO, \
                            FILENAMECHARS, PAGENAMECHARS
import core.database
import log.model
import bookmarks.model
from libs.notify import Notify
from libs.dateformat import human_date, short_datetime
from libs.strformat import remove_special_chars, remove_diacritics, remove_html_tags, str_limit
import libs.permissions
from libs.permissions import isAllowedToDeleteObject, isAllowedToWriteObject, objectOwnerFromService

from search.model import addTag, removeTag, splitTags

''' importa definição do tutorial deste módulo, se existir _tutorial.py '''
from config import TUTORIAL
try:
    import _tutorial
except ImportError:
    pass


NUM_MAX_TOPICOS = 10


def prepareTopicos(user, topicos):
    prepared_topics = []
    for t in topicos:
        tmp = dict()
        tmp["titulo"] = str_limit(remove_html_tags(t["titulo"]), 120)
        tmp["owner"] = t["owner"]
        tmp["name_id"] = t["name_id"]
        
        # somente o dono do tópico ou o dono/admins da comunidade podem apagar um tópico
        tmp["apagar"] = isAllowedToDeleteObject(user, t["owner"], t["registry_id"]+"/"+t["_id"])
        
        # somente o dono do objeto pode alterar
        tmp["alterar"] = (user == t["owner"])

        # map/reduce para contar o número de replies do tópico
        tmp["num_replies"] = model.Topic.countObjectsByGroup(t["_id"])

        # datas formatadas
        tmp["data_cri"] = t["data_cri"]
        tmp["data_cri_fmt"] = short_datetime(t["data_cri"])
        
        tmp["ultimo_reply"] = t["ultimo_reply"]
        tmp["ultimo_reply_fmt"] = short_datetime(tmp["ultimo_reply"]) if tmp["ultimo_reply"] else "-"
        
        prepared_topics.append(tmp)
      
    return prepared_topics


def prepareReplies(user, replies):
    prepared_list = []
    i = 0
    for obj in replies:
        tmp = dict()
        tmp.update(obj)
        
        # somente o dono da resposta ou o dono/admins da comunidade podem apagar
        tmp["apagar"] = isAllowedToDeleteObject(user, obj["owner"], obj["registry_id"]+"/"+obj["_id"])
        
        # somente o dono do objeto pode alterar
        tmp["alterar"] = (user == obj["owner"])

        # datas formatadas
        tmp["data_cri_fmt"] = short_datetime(obj["data_cri"])
        tmp["data_alt_fmt"] = short_datetime(obj["data_alt"])
        
        if i==0:
            prepared_list.append(tmp)       # retorna primeiro o tópico
        else:
            prepared_list.insert(1, tmp)     # e depois a lista de replies em ordem cronológica inversa
            
        i = i + 1
      
    return prepared_list


class ForumHandler(BaseHandler):
    ''' Lista o forum de uma comunidade '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('forum')
    @libs.permissions.canReadService ('forum')   
    def get (self, registry_id):
        user = self.get_current_user()
        page = int(self.get_argument("page","1"))
        ordem = self.get_argument("ordem","0")
        tag = self.get_argument("tag","")
        
        if tag:
            topics_count = model.Topic.countObjectsByRegistryIdTags(registry_id, tag)
            topics_list = prepareTopicos(user, model.Topic.listForumTopics(registry_id, page, NUM_MAX_TOPICOS, ordem, tag))            
        else:
            topics_count = model.Topic.countObjectsByRegistryId(registry_id)
            topics_list = prepareTopicos(user, model.Topic.listForumTopics(registry_id, page, NUM_MAX_TOPICOS, ordem))
        
        tags_list = model.Topic.listAllTags(registry_id)

        links = []
        if isAllowedToWriteObject(user, 'forum', registry_id):
            links.append((u"Novo tópico", "/static/imagens/icones/new32.png", "/forum/newtopic/"+registry_id))
        if isUserOrOwner(user, registry_id):
            links.append((u"Alterar permissões deste forum", "/static/imagens/icones/permissions32.png", "/permission/forum/"+registry_id, "", "", True))   
        if ordem == "1":
            links.append(("Exibir mais recentes primeiro", "/static/imagens/icones/descending32.png", "/forum/"+registry_id+"?ordem=0"))
        else:
            links.append(("Exibir mais antigos primeiro", "/static/imagens/icones/ascending32.png", "/forum/"+registry_id+"?ordem=1"))

        log.model.log(user, u'acessou o forum', objeto=registry_id, tipo="forum", news=False)
            
        self.render("modules/forum/forum-list.html", NOMEPAG='forum', \
                                  REGISTRY_ID=registry_id, \
                                  TOPICOS=topics_list, TOPICOS_COUNT=topics_count, \
                                  PAGE=page, PAGESIZE=NUM_MAX_TOPICOS, \
                                  ORDEM=ordem, \
                                  TITULO=u"Forum de %s" % registry_id if not tag else u"Forum de %s com a tag %s" % (registry_id, tag), \
                                  TAGS = tags_list, \
                                  LINKS=links)       
        
        
class NewTopicHandler(BaseHandler):
    ''' Criar novo tópico '''

    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('forum')
    @libs.permissions.canWriteService ('forum')   
    def get (self, registry_id):
        user = self.get_current_user()

        self.render("modules/forum/forum-form.html", NOMEPAG='forum', \
                                    REGISTRY_ID=registry_id, TOPICO=model.Topic(), MSG="")

                
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('forum')
    @libs.permissions.canWriteService ('forum')   
    def post(self, registry_id):
        user = self.get_current_user()
        msg = ""
        
        _topic = model.Topic()
        _topic.titulo = self.get_argument("titulo","")
        if _topic.titulo == "":
            msg += u"O título do tópico não pode ser vazio.<br/>"
        else:
            _topic.name_id = remove_special_chars(remove_diacritics(_topic.titulo.replace(" ","_")))
            if _topic.name_id == "":
                msg += u"Título do tópico inválido<br/>"
               
        if model.Topic.exists(registry_id, _topic.name_id):
            msg += u"Já existe um tópico com este nome"
                
        _topic.tags = splitTags(self.get_argument("tags",""))
        
        _topic.conteudo = self.get_argument("conteudo","")
        if _topic.conteudo == "":
            msg += u"O conteúdo do tópico não pode ser vazio.<br/>"
        
        if msg:
            self.render("modules/forum/forum-form.html", NOMEPAG="forum", REGISTRY_ID=registry_id, TOPICO=_topic, MSG=msg)
            return
                
        else:
            _topic.receber_email = self.get_argument("receber_email", "N")
            _topic.data_cri = str(datetime.now())
            _topic.data_alt = _topic.data_cri
            _topic.service = "forum"
            _topic.type = "topic"

            doc_id = uuid4().hex

            _topic.registry_id = registry_id
            _topic.owner = user
            _topic.alterado_por = user
             
            try:
                _topic.save(id=doc_id)
            except Exception as detail:
                self.render("modules/forum/forum-form.html", NOMEPAG="forum", REGISTRY_ID=registry_id, TOPICO=_topic, \
                            MSG=u"Já existe um tópico neste forum com este título.")
                return
            
            data_tag = str(datetime.now())
            for tag in _topic.tags:
                addTag(tag, registry_id, user, "forum", registry_id+"/"+_topic.name_id, _topic.titulo, data_tag)

            log.model.log(user, u'criou um tópico no forum', objeto=registry_id, tipo="forum")
            self.redirect("/forum/%s" % registry_id)
        
        

class TopicHandler(BaseHandler):
    '''Listar um tópico e todas as suas respostas'''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('forum')
    @libs.permissions.canReadService ('forum') 
    def get (self, registry_id, topic_id):
        user = self.get_current_user()
        doc_id = '/'.join([registry_id, topic_id])
        
        _topic = model.Topic.retrieve_by_name_id(registry_id, topic_id)
        
        if _topic == None:
            raise HTTPError(404)
            return
                        
        lista = prepareReplies(user, model.Topic.listObjectByGroup(registry_id, _topic.id))
        
        links=[]
        reg = core.model.Registry().retrieve(user)
        if reg and "bookmarks"  in reg.getServices:                              
            links.append(bookmarks.model.Bookmarks.createBookmarkLink(user, "http://"+PLATAFORMA_URL+self.request.path))        
        #links.append((u"Retornar aos tópicos", "/static/imagens/icones/back32.png", "/forum/"+registry_id))
        if isAllowedToWriteObject(user, 'forum', registry_id):
            links.append(("Responder", "/static/imagens/icones/reply32.png", "/forum/reply/"+doc_id))

        log.model.log(user, u'acessou um tópico do forum', objeto=doc_id, tipo="forum", news=False)

        self.render("modules/forum/topic.html", NOMEPAG='forum', \
                    REGISTRY_ID=registry_id, USER=user, \
                    LINKS=links, \
                    LISTA=lista, TOPIC_ID=topic_id)


class EditTopicHandler(BaseHandler):
    '''Alterar um tópico'''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('forum')
    @libs.permissions.canWriteService ('forum') 
    def get (self, registry_id, topic_id):
        user = self.get_current_user()
        doc_id = '/'.join([registry_id, topic_id])
        
        _topic = model.Topic.retrieve_by_name_id(registry_id, topic_id)
        if _topic:
            # somente o dono do tópico pode alterá-lo
            if _topic.owner != user:
                raise HTTPError(403)
                return

            self.render("modules/forum/forum-form.html", NOMEPAG='forum', \
                                        REGISTRY_ID=registry_id, TOPICO=_topic, MSG="")    
                        
        else:
            raise HTTPError(404)
        
        
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('forum')
    @libs.permissions.canWriteService ('forum') 
    def post(self, registry_id, topic_id):
        user = self.get_current_user()
        doc_id = '/'.join([registry_id, topic_id])
        
        _topic = model.Topic.retrieve_by_name_id(registry_id, topic_id)
        if _topic:
            # somente o dono do tópico pode alterá-lo
            if _topic.owner != user:
                raise HTTPError(403)
                return
                
            msg = ""

            _topic.titulo = self.get_argument("titulo","")
            if _topic.titulo == "":
                msg += u"O título do tópico não pode ser vazio.<br/>"
            
            old_tags = _topic.tags                                   # preserva tags anteriores
            _topic.tags = splitTags(self.get_argument("tags",""))
            
            _topic.conteudo = self.get_argument("conteudo","")
            if _topic.conteudo == "":
                msg += u"O conteúdo do tópico não pode ser vazio.<br/>"
            
            if msg:
                self.render("modules/forum/forum-form.html", NOMEPAG="forum", REGISTRY_ID=registry_id, TOPICO=_topic, MSG=msg)
                return
                    
            else:
                _topic.receber_email = self.get_argument("receber_email", "N")
                _topic.data_alt = str(datetime.now())
                _topic.alterado_por = user
                
                _topic.saveTopic(old_tags=old_tags)
                
                log.model.log(user, u'alterou um tópico no forum', objeto=registry_id, tipo="forum")
                self.redirect("/forum/%s/%s" % (registry_id, topic_id))        
        else:
            raise HTTPError(404)
                            

class ReplyHandler(BaseHandler):
    ''' Inclusão de uma resposta '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('forum')
    @libs.permissions.canWriteService ('forum') 
    def get (self, registry_id, name_id):
        _topic = model.Topic().retrieve_by_name_id(registry_id, name_id)
        _reply = model.Reply()
        _reply.titulo = "Re: %s" % _topic.titulo
        if _topic:
            self.render("modules/forum/reply-form.html", NOMEPAG='forum', \
                        REGISTRY_ID=registry_id, \
                        REPLY=_reply, MSG="")
        else:
            raise HTTPError(404)

    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('forum')
    @libs.permissions.canWriteService ('forum') 
    def post(self, registry_id, name_id):
        
        user = self.get_current_user()
        msg = ""
        
        _reply = model.Reply()
        _reply.titulo = self.get_argument("titulo","")
        _reply.conteudo = self.get_argument("conteudo","")
        if _reply.conteudo == "":
            msg += u"O conteúdo do tópico não pode ser vazio.<br/>"
        
            self.render("modules/forum/reply-form.html", NOMEPAG="forum", REGISTRY_ID=registry_id, REPLY=_reply, MSG=msg)
            return
                
        else:
            _reply.data_cri = str(datetime.now())
            _reply.data_alt = _reply.data_cri
            _reply.service = "forum"
            _reply.type = "reply"

            doc_id = uuid4().hex

            _reply.registry_id = registry_id
            _reply.owner = user
            _reply.alterado_por = user
            
            _topic = model.Topic().retrieve_by_name_id(registry_id, name_id)
            
            _reply.group_id = _topic.id             # inclui a referênca ao tópico no reply
            _reply.save(id=doc_id)
            
        
            _topic.ultimo_reply = _reply.data_cri   # atualiza data do último reply no tópico
            try:
                _topic.save(id=_topic.id)
            except ResourceConflict:
                # ignora se houve conflito ao salvar o tópico
                pass

            if _topic.receber_email=="S":
                # Notifica o dono do tópico respondido
                assunto = u"respondeu um tópico que você criou no Fórum da comunidade %s" % registry_id
                email_msg = u"Comunidade: "+registry_id+"\n" + \
                            u"Tópico: "+_topic.titulo+"\n\n" + \
                              _reply.titulo+"\n"+ \
                              _reply.conteudo+"\n\n"+ \
                              Notify.assinatura(_reply.owner,registry_id,_reply.data_cri)+"\n\n"
                Notify.email_notify(_topic.owner, _reply.owner, assunto, \
                               message=email_msg, \
                               link="forum/"+registry_id)
            log.model.log(user, u'respondeu um tópico do forum', objeto=registry_id, tipo="forum")
    
            self.redirect("/forum/%s/%s" % (registry_id, name_id))
    

        
class DeleteTopicHandler(BaseHandler):
    '''Remove um tópico'''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('forum')
    @libs.permissions.canWriteService ('forum') 
    def get (self, registry_id, name_id):
        user = self.get_current_user()
           
        # remove somente o tópico e todas as suas tags.
        # todas as respostas ficam no activdb e poderão ser removidas posteriormente pelo dbclean.     
        _topic = model.Topic().retrieve_by_name_id(registry_id, name_id)
        
        if isAllowedToDeleteObject(user, _topic.owner, registry_id+"/"+name_id):
            _topic.deleteTopic()
                
            log.model.log(user, u'removeu um tópico do forum', objeto=registry_id, tipo="forum")
            self.redirect("/forum/" + registry_id)

        else:
            raise HTTPError(403)


class EditReplyHandler(BaseHandler):
    ''' Altera uma resposta do tópico '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('forum')
    @libs.permissions.canWriteService ('forum') 
    def get (self, registry_id):
        # Apagar resposta equivale a limpar sem remover
        user = self.get_current_user()        
        id = self.get_argument("id","")
        
        _reply = model.Reply().retrieve(id)
        
        if not _reply or registry_id != _reply.registry_id:
            # chamada inválida (id não existe ou reply não corresponde a um forum do registry_id)
            raise HTTPError(404)
            return
        
        if user != _reply.owner:
            # sem permissão
            raise HTTPError(403)
            return   
           
        self.render("modules/forum/reply-form.html", NOMEPAG='forum', \
                    REGISTRY_ID=registry_id, \
                    REPLY=_reply, MSG="")
        
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('forum')
    @libs.permissions.canWriteService ('forum') 
    def post(self, registry_id):
        user = self.get_current_user()
        id = self.get_argument("id","")
        
        _reply = model.Reply().retrieve(id)
        
        if not _reply or registry_id != _reply.registry_id:
            # chamada inválida (id não existe ou reply não corresponde a um forum do registry_id)
            raise HTTPError(404)
            return
        
        if user != _reply.owner:
            # sem permissão
            raise HTTPError(403)
            return   
           
        _reply.titulo = self.get_argument("titulo","")
        _reply.conteudo = self.get_argument("conteudo","")
        if _reply.conteudo == "":
            msg = u"O conteúdo do tópico não pode ser vazio.<br/>"
            self.render("modules/forum/reply-form.html", NOMEPAG="forum", REGISTRY_ID=registry_id, REPLY=_reply, MSG=msg)
            return
                
        _reply.data_alt = str(datetime.now())
        _reply.alterado_por = user
        _reply.save()
        
        _topic = model.Topic().retrieve(_reply.group_id)
        _topic.ultimo_reply = _reply.data_alt   # atualiza data do último reply no tópico
        try:
            _topic.save()
        except ResourceConflict:
            # ignora se houve conflito ao salvar o tópico
            pass

        if _topic.receber_email=="S":
            # Notifica o dono do tópico respondido
            assunto = u"alterou uma resposta de um tópico que você criou no Fórum da comunidade %s" % registry_id
            email_msg = u"Comunidade: "+registry_id+"\n" + \
                        u"Tópico: "+_topic.titulo+"\n\n" + \
                          _reply.titulo+"\n"+ \
                          _reply.conteudo+"\n\n"+ \
                          Notify.assinatura(_reply.owner,registry_id,_reply.data_alt)+"\n\n"
            Notify.email_notify(_topic.owner, _reply.owner, assunto, \
                           message=email_msg, \
                           link="forum/"+registry_id)
        log.model.log(user, u'alterou uma resposta de um tópico do forum', objeto=registry_id, tipo="forum")

        self.redirect("/forum/%s/%s" % (registry_id, _topic.name_id))
    
            
class DeleteReplyHandler(BaseHandler):
    ''' Apaga uma resposta do tópico '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('forum')
    @libs.permissions.canWriteService ('forum') 
    def get (self, registry_id):    
        # Apagar resposta equivale a limpar sem remover
        user = self.get_current_user()        
        id = self.get_argument("id","")
        
        _reply = model.Reply().retrieve(id)
        
        if not _reply or registry_id != _reply.registry_id:
            # chamada inválida (id não existe ou reply não corresponde a um forum do registry_id)
            raise HTTPError(404)
            return


        
        if isAllowedToDeleteObject(user, _reply.owner, registry_id+"/"+id):      
            _reply.titulo = "***** Mensagem Removida *****"
            _reply.conteudo = ""
            _reply.data_alt = str(datetime.now())
            _reply.alterado_por = user            
            _reply.save()
                        
            log.model.log(user, u'removeu uma resposta de um tópico do forum', objeto=_reply.registry_id, tipo="forum")
            
            # busca o tópico para recuperar o name_id e poder redirecionar para a página do tópico
            _topic = model.Topic().retrieve(_reply.group_id)
            if _topic:
                self.redirect("/forum/%s/%s" % (_reply.registry_id, _topic.name_id))
            else:
                self.redirect("/forum/%s" % _reply.registry_id)
                
        else:
            raise HTTPError(403)
        

    

#==============================================================================
URL_TO_PAGETITLE.update ({
        "forum": "Forum"
    })

HANDLERS.extend([
            (r"/forum/%s" % NOMEUSERS,                                ForumHandler),
            (r"/forum/newtopic/%s" % NOMEUSERS,                       NewTopicHandler),
            (r"/forum/%s/%s" % (NOMEUSERS, PAGENAMECHARS),            TopicHandler),
            (r"/forum/edit/%s/%s" % (NOMEUSERS, PAGENAMECHARS),       EditTopicHandler),
            (r"/forum/delete/%s/%s" % (NOMEUSERS, PAGENAMECHARS),     DeleteTopicHandler),
            (r"/forum/reply/edit/%s" % NOMEUSERS,                     EditReplyHandler),     # ?id=xxxxxxxx
            (r"/forum/reply/delete/%s" % NOMEUSERS,                   DeleteReplyHandler),   # ?id=xxxxxxxx
            (r"/forum/reply/%s/%s" % (NOMEUSERS, PAGENAMECHARS),      ReplyHandler),
    ])
