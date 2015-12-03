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

import operator
from operator import itemgetter
import re
import time
from datetime import datetime
from string import find, replace
from uuid import uuid4
from urllib import quote,unquote
import locale

import tornado.web
from tornado.web import HTTPError
import tornado.template

from config import PLATAFORMA_URL
import model
from model import _EMPTYMBLOG
from search.model import addTag, removeTag
import core.model
from core.model import isUserOrMember, isAUser, isACommunity, isAllowedToAccess, getType
import core.database
from core.database import PASSWD_USER_SUSPENDED
import log.model
from core.dispatcher import BaseHandler, HANDLERS, URL_TO_PAGETITLE, \
                            NOMEUSERS, FILENAMECHARS, PAGENAMECHARS
from libs.dateformat import short_datetime, human_date
from libs.notify import Notify
from libs.strformat import remove_diacritics

''' importa definição do tutorial deste módulo, se existir _tutorial.py '''
from config import TUTORIAL
try:
    import _tutorial
except ImportError:
    pass


# Número máximo de caracteres de um post
MAX_CHR_MBLOG = 350

# Número máximo de posts na paginação do Mblog
NUM_MAX_MBLOG = 20


def processa_tags (id, mblog_data):
    tag_list = list(set(re.findall(r"#\w+", mblog_data["conteudo"], re.UNICODE)))
    data_tag = str(datetime.now())
    for i in range(len(tag_list)):
        tag_list[i] = tag_list[i].lstrip('#')
        addTag(tag_list[i], mblog_data["registry_id"], mblog_data["owner"], "mblog", id, mblog_data["conteudo"], data_tag)
        
    return tag_list

def processa_url (conteudo):
    r1 = r"(\b(http|https)://([-A-Za-z0-9+&@#/%?=~_()|!:,.;]*[-A-Za-z0-9+&@#/%=~_()|]))"
    return re.sub(r1, r'<a title="\1" href="\1">\1</a>', conteudo)
    
def processa_arroba (conteudo):
    # Retorna duas listas com todas as menções feitas numa mensagem.
    # lista_original: inclui usuários e comunidades mencionadas;
    #                 não inclui @ seguido de usuario/comunidade inexistentes
    # lista_processada: Caso seja feita menção a uma comunidade, a lista inclui
    #                   todos os participantes da comunidade mencionada.
    
    # found_list = [i.lstrip('@') for i in list(set(re.findall(r"@\w+", conteudo)))]
    found_list = [i.lstrip('@') for i in list(set(re.findall(r"@[a-zA-Z0-9][\w\.]+\w", conteudo)))]
    
    ref_list = []
    proc_list = []
    
    # conteudo email utiliza urls absolutas e conteudo utiliza urls relativas.
    conteudo_email = conteudo
    
    for registry_id in found_list:
        if registry_id in core.database.REGISTRY:
            ref_list.append(registry_id)
            user_data = core.model.Registry().retrieve(registry_id)
            type = user_data.getType()
            if type=="community":
                # referência a uma comunidade
                conteudo = replace(conteudo, "@%s"%registry_id, \
                                   '@<a title="%s" href="/mblog/%s">%s</a>'%(user_data.description, registry_id, registry_id))
                conteudo_email = replace(conteudo_email, "@%s"%registry_id, \
                                   '@<a title="%s" href="http://%s/mblog/%s">%s</a>'%(user_data.description, PLATAFORMA_URL, registry_id, registry_id))
                proc_list.extend(user_data.participantes)
            elif type=="member":
                # referência a um usuário
                conteudo = replace(conteudo, "@%s"%registry_id, \
                                   '@<a title="%s" href="/mblog/%s">%s</a>'%(user_data.name+" "+user_data.lastname, registry_id, registry_id))
                conteudo_email = replace(conteudo_email, "@%s"%registry_id, \
                                   '@<a title="%s" href="http://%s/mblog/%s">%s</a>'%(user_data.name+" "+user_data.lastname, PLATAFORMA_URL, registry_id, registry_id))
                proc_list.append(registry_id)

    return dict( conteudo=conteudo,
                 conteudo_email=conteudo_email,
                 lista_original=ref_list,
                 lista_processada=list(set(proc_list) )
    )
    

def autocomplete_mblog (user, registry_id):
    permission = False
    autocomplete = dict()    
    if isUserOrMember(user, registry_id):
        permission = True
        
        _member = core.model.Member().retrieve(user)
        autocomplete_list = []
        autocomplete_list.extend(_member.getFriendsList()[1])
        autocomplete_list.extend(_member.getCommunitiesList())
        if isACommunity(registry_id):
            _member = core.model.Community().retrieve(registry_id)
            autocomplete_list.extend(_member.getMembersList()[1])
        
        for item in autocomplete_list:
            autocomplete[item[0].encode('iso-8859-1', 'ignore')] = item[1].encode('iso-8859-1', 'ignore')
            
    return (permission, autocomplete)
                
                    
class MblogHandler(BaseHandler):
    ''' Lista a página de MBlogs de um usuario ou comunidade '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('mblog')
    def get (self, registry_id):
        user = self.get_current_user()
        page = int(self.get_argument("page","1"))
        myposts = int(self.get_argument("myposts","0"))
        
        if user == registry_id and myposts!=1:
            # Estou vendo meu próprio mblog: vejo mensagens que me interessam.
            myself = True
            legenda = u"Meu histórico"
         
        else:
            # estou vendo o mblog de outra pessoa ou de uma comunidade: 
            # só vejo mensagens postadas por ela.
            legenda = "Mblogs de %s" % registry_id
            myself = False
            
        lista_posts = model.Mblog.listPosts(user, registry_id, page, NUM_MAX_MBLOG, myself, myposts)
        mblog_count = model.Mblog.countPosts(user, registry_id, myself)

        (permission, autocomplete) = autocomplete_mblog(user, registry_id)

        links = []
        links.append((u"Menções a @"+registry_id, "/static/imagens/icones/at32.png", "/mblog/mentions/"+registry_id))

        if user == registry_id:
            if myposts!=1:
                links.append((u"Mblogs de @"+registry_id, "/static/imagens/icones/myposts32.png", "/mblog/%s?myposts=1"%registry_id))
            else:
                links.append((u"Meu histórico", "/static/imagens/icones/history32.png", "/mblog/"+registry_id))
              

        log.model.log(user, u'acessou mblogs de', objeto=registry_id, tipo="mblog", news=False)
        self.render("modules/mblog/mblog.html", NOMEPAG="microblog", \
                    REGISTRY_ID=registry_id, \
                    POSTS=lista_posts, \
                    MAX_CHR_MBLOG=MAX_CHR_MBLOG, \
                    MBLOG_COUNT=mblog_count,\
                    PAGE=page, PAGESIZE=NUM_MAX_MBLOG, \
                    TITULO=legenda, \
                    TIPO="timeline", \
                    PERMISSION=permission, \
                    AUTOCOMPLETE_LIST=autocomplete, \
                    LINKS=links)


class NewMblogHandler(BaseHandler):
    ''' Inclusão de um novo post no Mblog '''

    @tornado.web.authenticated
    @core.model.serviceEnabled('mblog')
    def post(self, registry_id):
        user = self.get_current_user()
        mblog_id_reply_to = self.get_argument("id","")
        
        self._registry = core.model.Registry().retrieve(registry_id)
        if not self._registry:
            raise HTTPError(404)
            return   
            
        if not self._registry.isUserOrMember(user):
            raise HTTPError(403)
            return   
        
        self._mblog = model.Mblog()
        self._mblog.conteudo = self.get_argument("conteudo","")

        if self._mblog.conteudo:
            if len (self._mblog.conteudo) > MAX_CHR_MBLOG:
                self._mblog.conteudo = self._mblog.conteudo[:MAX_CHR_MBLOG]
                
            self._mblog.data_cri = str(datetime.now())
            self._mblog.registry_id = registry_id
            self._mblog.owner = user
            self._mblog.reply_to = mblog_id_reply_to
            
            # preenche a lista de interessados
            self._mblog.interessados = [registry_id]
            
            type = self._registry.getType()
            if type=="member":
                self._mblog.interessados.extend(self._registry.amigos)
            elif type=="community":
                self._mblog.interessados.extend(self._registry.participantes)

            # processa as tags mencionadas neste mblog
            mblog_id = uuid4().hex
            self._mblog.tags = processa_tags(mblog_id, self._mblog)
            
            # trata injeção de tags html e acrescenta links nas urls
            self._mblog.conteudo = replace(self._mblog.conteudo,"<","&lt;")
            self._mblog.conteudo = replace(self._mblog.conteudo,">","&gt;")
            self._mblog.conteudo = processa_url(self._mblog.conteudo)
            
            ret = processa_arroba(self._mblog.conteudo)
            self._mblog.mencionados = ret["lista_original"]
            self._mblog.interessados.extend(ret["lista_processada"])
            self._mblog.interessados = list(set(self._mblog.interessados))
            self._mblog.conteudo = ret["conteudo"]
            
            try:
                self._mblog.save(id=mblog_id)
            except Exception as detail:
                self.render("home.html", MSG=u"Erro: %s" % detail, NOMEPAG="microblog")
                return

            # notifica cada usuário mencionado por essa mensagem
            for mentioned in ret["lista_original"]:
                email_msg = ret["conteudo_email"]+"\n"+\
                            Notify.assinatura(user, registry_id, self._mblog.data_cri)+"\n\n"
                Notify.email_notify(mentioned, user, u"mencionou %s no Mblog" % mentioned, \
                               message=email_msg, \
                               link="mblog/mentions/"+mentioned)
            
            log.model.log(user, u'escreveu no mblog de', objeto=registry_id, tipo="mblog", link="/mblog/post?id="+mblog_id)
        self.redirect("/mblog/%s" % registry_id)


class ListTalkMblogHandler(BaseHandler):
    ''' Lista uma conversa a partir de um mblog_id '''

    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        mblog_id = self.get_argument("id","")
        
        self._mblog = model.Mblog().retrieve(mblog_id)
        if not self._mblog:
            raise HTTPError(404)
            return      
                
        # registry_id é o da mensagem original
        registry_id = self._mblog.registry_id
        
        lista_posts = []
        # varre a cadeia de mensagens da conversa
        while mblog_id:
            self._prox = model.Mblog().retrieve(mblog_id)
            if self._prox:
                post_data = self._prox.props()

                post_data["data_cri"] = human_date(post_data["data_cri"])
                post_data["apagar"] = (post_data["owner"] == user)
                lista_posts.append(post_data)
            
                # procura a próxima (a mensagem que esta respondeu)
                if "reply_to" in post_data:
                    mblog_id = post_data["reply_to"]
                else:
                    break
            else:
                break
         
         
        legenda = u"Meu histórico" if user == registry_id else "Mblogs de %s" % registry_id
        links = []
        links.append((legenda, "/static/imagens/icones/history32.png", "/mblog/"+registry_id))
        links.append((u"Menções a @"+registry_id, "/static/imagens/icones/at32.png", "/mblog/mentions/"+registry_id))

        self.render("modules/mblog/mblog.html", NOMEPAG="microblog", \
                    POSTS=lista_posts, \
                    PAGE=1, PAGESIZE=len(lista_posts), \
                    MBLOG_COUNT=len(lista_posts), \
                    REGISTRY_ID=registry_id, \
                    PERMISSION=False, AUTOCOMPLETE_LIST={}, \
                    MAX_CHR_MBLOG=MAX_CHR_MBLOG, \
                    TITULO="Conversa com @"+registry_id, \
                    TIPO="talk", \
                    LINKS=links)


class ReplyMblogHandler(BaseHandler):
    ''' Responde um mblog_id '''

    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        mblog_id = self.get_argument("id","")
        community_id = self.get_argument("community","")
        registry_id = user if not community_id else community_id
        
        self._mblog = model.Mblog().retrieve(mblog_id)
        if not self._mblog:
            raise HTTPError(404)
            return    
        
        self._mblog.data_cri = human_date(self._mblog.data_cri)

        (permission, autocomplete) = autocomplete_mblog(user, registry_id)
        
        legenda = u"Meu histórico" if user == registry_id else "Mblogs de %s" % registry_id
        links = []
        links.append((legenda, "/static/imagens/icones/history32.png", "/mblog/"+registry_id))
        links.append((u"Menções a @"+registry_id, "/static/imagens/icones/at32.png", "/mblog/mentions/"+registry_id))
        
        self.render("modules/mblog/reply.html", NOMEPAG="microblog", \
                    POST=self._mblog, \
                    PERMISSION=permission, AUTOCOMPLETE_LIST=autocomplete, \
                    REGISTRY_ID=registry_id, \
                    MAX_CHR_MBLOG=MAX_CHR_MBLOG, \
                    LINKS=links, \
                    MBLOG_ID=mblog_id)


class ShareMblogHandler(BaseHandler):
    ''' Compartilha um mblog_id '''

    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        mblog_id = self.get_argument("id","")
        
        self._mblog = model.Mblog().retrieve(mblog_id)
        if not self._mblog:
            raise HTTPError(404)
            return    
        
        self._mblog.data_cri = short_datetime(self._mblog.data_cri)

        (permission, autocomplete) = autocomplete_mblog(user, user)

        self.render("modules/mblog/share.html", NOMEPAG="microblog", \
                    POST=self._mblog, \
                    REGISTRY_ID=user, \
                    PERMISSION=permission, AUTOCOMPLETE_LIST=autocomplete, \
                    MAX_CHR_MBLOG=MAX_CHR_MBLOG, \
                    MBLOG_ID=mblog_id)

    @tornado.web.authenticated
    def post(self):
        user = self.get_current_user()
        mblog_id = self.get_argument("mblog_id","")
        registry_id = self.get_argument("registry_id","")

        self._registry = core.model.Registry().retrieve(registry_id)
        if not self._registry:
            raise HTTPError(404)
            return   
            
        if not self._registry.isUserOrMember(user):
            raise HTTPError(403)
            return   
        
        self._mblog = model.Mblog().retrieve(mblog_id)
        self._mblog_novo = model.Mblog()
              
        self._mblog_novo.conteudo = self.get_argument("conteudo","")

        if len (self._mblog_novo.conteudo) > MAX_CHR_MBLOG:
            self._mblog_novo.conteudo = self._mblog_novo.conteudo[:MAX_CHR_MBLOG]
            
        self._mblog_novo.registry_id = registry_id
        self._mblog_novo.owner = user
        self._mblog_novo.data_cri = str(datetime.now())
        
        if self._mblog.conteudo_original:
            # estou compartilhando uma msg já compartilhada
            self._mblog_novo.conteudo_original = self._mblog.conteudo_original
            self._mblog_novo.data_original = self._mblog.data_original
            self._mblog_novo.registry_id_original = self._mblog.registry_id_original
            self._mblog_novo.owner_original = self._mblog.owner_original
            self._mblog_novo.mblog_id_original = self._mblog.mblog_id_original
            
        else:
            # estou compartilhando uma msg que ainda não foi compartilhada
            self._mblog_novo.conteudo_original = self._mblog.conteudo
            self._mblog_novo.data_original = self._mblog.data_cri
            self._mblog_novo.registry_id_original = self._mblog.registry_id
            self._mblog_novo.owner_original = self._mblog.owner
            self._mblog_novo.mblog_id_original = mblog_id
            
        mblog_id_original = self._mblog_novo.mblog_id_original
        self._mblog_novo.tags = self._mblog.tags
        
        # preenche a lista de interessados
        self._mblog_novo.interessados = [registry_id]
        type = self._registry.getType()
        if type=="member":
            self._mblog_novo.interessados.extend(self._registry.amigos)
        elif type=="community":
            self._mblog_novo.interessados.extend(self._registry.participantes)

        # trata injeção de tags html e acrescenta links nas urls
        self._mblog_novo.conteudo = replace(self._mblog_novo.conteudo,"<","&lt;")
        self._mblog_novo.conteudo = replace(self._mblog_novo.conteudo,">","&gt;")
        self._mblog_novo.conteudo = processa_url(self._mblog_novo.conteudo)
        
        ret = processa_arroba(self._mblog_novo.conteudo)
        self._mblog.mencionados = ret["lista_original"]
        self._mblog_novo.interessados.extend(ret["lista_processada"])
        self._mblog_novo.interessados = list(set(self._mblog_novo.interessados))
        self._mblog_novo.conteudo = ret["conteudo"]
        
        mblog_id_novo = uuid4().hex

        try:
            self._mblog_novo.save(id=mblog_id_novo)
            self._mblog.save()
        except Exception as detail:
            self.render("home.html", MSG=u"Erro: %s" % detail, NOMEPAG="microblog")
            return
        
        # acrescenta esse post a lista de compartilhamentos da mensagem original
        self._mblog_original = model.Mblog().retrieve(mblog_id_original)        
        if self._mblog_original:
            self._mblog_original.share_list.append (mblog_id_novo)
            self._mblog_original.save()
        
        # se uma mensagem for compartilhada, notifica seu dono
        email_msg = ret["conteudo_email"]+"\n"+\
                    self._mblog_novo.owner+" em "+short_datetime(self._mblog_novo.data_cri)+"\n\n"+\
                    self._mblog_original.conteudo+"\n"+\
                    Notify.assinatura (self._mblog_original.owner, self._mblog_original.registry_id, self._mblog_original.data_cri)+"\n\n"
        Notify.email_notify(self._mblog_original.owner, \
                            user, u"compartilhou uma mensagem sua no Mblog", \
                            message=email_msg, \
                            link="mblog/"+self._mblog_original.owner)

        log.model.log(user, u'compartilhou um mblog de', objeto=self._mblog_novo.registry_id_original, tipo="mblog", link="/mblog/post?id="+mblog_id_novo)
        self.redirect("/mblog/%s" % registry_id)


class MentionsMblogHandler(BaseHandler):
    ''' Lista menções feitas a um usuário/comunidade '''

    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('mblog')
    def get(self, registry_id):
        user = self.get_current_user()
        page = int(self.get_argument("page","1"))

        lista_posts = model.Mblog.listMentions(user, registry_id, page, NUM_MAX_MBLOG)
        mblog_count = model.Mblog.countMentions(registry_id)

        (permission, autocomplete) = autocomplete_mblog(user, registry_id)
                 
        legenda = u"Meu histórico" if user==registry_id else "Mblogs de %s" % registry_id
        links = []
        links.append((legenda, "/static/imagens/icones/history32.png", "/mblog/"+registry_id))

        if user == registry_id:
            links.append((u"Mblogs de @"+registry_id, "/static/imagens/icones/myposts32.png", "/mblog/%s?myposts=1"%registry_id))

                
        log.model.log(user, u'acessou menções ao mblog de', objeto=registry_id, tipo="mblog", news=False)
                
        self.render("modules/mblog/mblog.html", NOMEPAG="microblog", \
                    REGISTRY_ID=registry_id, \
                    POSTS=lista_posts, \
                    MBLOG_COUNT=mblog_count,\
                    PAGE=page, PAGESIZE=NUM_MAX_MBLOG, \
                    PERMISSION=permission, \
                    AUTOCOMPLETE_LIST=autocomplete, \
                    MAX_CHR_MBLOG=MAX_CHR_MBLOG, \
                    TIPO="mentions", \
                    TITULO=u"Menções a @"+registry_id, \
                    LINKS=links)


class SuporteActivHandler(BaseHandler):
    ''' Lista menções feitas a comunidade Suporte_Activ e permite envio de mblog num único template '''

    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        _usr = core.model.Member().retrieve(user)
        has_mblog_service = "mblog" in _usr.getServices
        
        _reg = core.model.Registry().retrieve('Suporte_Activ')
        if not _reg:
            self.render("home.html", NOMEPAG="microblog", MSG=u"Serviço não habilitado. Comunidade Suporte_Activ não encontrada.", REGISTRY_ID=user)   
            return
                
        registry_id = 'Suporte_Activ'
        page = int(self.get_argument("page","1"))
        lista_posts = model.Mblog.listMentions(user, registry_id, page, NUM_MAX_MBLOG)
        mblog_count = model.Mblog.countMentions(registry_id)

        (permission, autocomplete) = autocomplete_mblog(user, user)

        legenda = u"Meu histórico" if user==registry_id else "Mblogs de %s" % registry_id
        links = []
        links.append((legenda, "/static/imagens/icones/history32.png", "/mblog/"+registry_id))
        
        log.model.log(user, u'acessou mblogs de', objeto=registry_id, tipo="mblog", news=False)
        self.render("modules/mblog/support.html", NOMEPAG="microblog", \
                    REGISTRY_ID=registry_id, \
                    HAS_MBLOG_SERVICE=has_mblog_service, \
                    POSTS=lista_posts, \
                    MBLOG_COUNT=mblog_count,\
                    PAGE=page, PAGESIZE=NUM_MAX_MBLOG, \
                    USER=user, \
                    PERMISSION=permission, \
                    AUTOCOMPLETE_LIST=autocomplete, \
                    MAX_CHR_MBLOG=MAX_CHR_MBLOG, \
                    TIPO="mentions", \
                    TITULO=u"Menções a @"+registry_id, \
                    LINKS=links)


class ShowMblogPostHandler(BaseHandler):
    ''' Exibe um Post do MBlog '''
    
    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        post_id = self.get_argument("id","")
        
        self._mblog = model.Mblog().retrieve(post_id)
        if self._mblog:
            mblog_data = self._mblog.props()

            registry_id = mblog_data["registry_id"]    

            (type, privacidade) = getType(registry_id)
            if type == "member" or type == "community":
                
                if isAllowedToAccess(user, registry_id) == 0:
                                  
                    mblog_data["apagar"] = (mblog_data["owner"] == user)
                    mblog_data["data_cri"] = human_date(mblog_data["data_cri"])
                    if "data_original" in mblog_data:
                        mblog_data["data_original"] = human_date(mblog_data["data_original"])
        
                    (permission, autocomplete) = autocomplete_mblog(user, registry_id)
                                
                    self.render("modules/mblog/post.html", NOMEPAG="microblog", \
                        REGISTRY_ID=registry_id, POST=mblog_data, \
                        MAX_CHR_MBLOG=MAX_CHR_MBLOG, \
                        PERMISSION=permission, \
                        AUTOCOMPLETE_LIST=autocomplete)
                else:
                    raise HTTPError(403)
            else:
                # usuario suspenso
                raise HTTPError(404)
        else:
            raise HTTPError(404)
        
        
class DeleteMblogHandler(BaseHandler):
    ''' Apaga um Post do MBlog '''
    
    @tornado.web.authenticated
    def get(self):
        
        user = self.get_current_user()
        mblog_id = self.get_argument("id","")
        
        self._mblog = model.Mblog().retrieve(mblog_id)
        if not self._mblog:
            raise HTTPError(404)
            return  
            
        registry_id = self._mblog.registry_id
        owner = self._mblog.owner
        
        if user != owner:
            raise HTTPError(403)
            return   
        
        # remove o post
        try:
            tags = self._mblog.tags
            self._mblog.delete()
            for tag in tags:
                removeTag(remove_diacritics(tag.lower()), "mblog", mblog_id)
                                        
        except Exception as detail:
            self.render("home.html", MSG=u"Erro: %s" % detail, REGISTRY_ID=registry_id, NOMEPAG="microblog")
            return
                
        log.model.log(user, u'removeu uma mensagem do mblog de', objeto=registry_id, tipo="none")
        self.redirect("/mblog/%s" % registry_id)


URL_TO_PAGETITLE.update ({
        "mblog": "Microblog"
    })

HANDLERS.extend([
            (r"/mblog/new/%s" % (NOMEUSERS),        NewMblogHandler),
            (r"/mblog/mentions/%s" % (NOMEUSERS),   MentionsMblogHandler),
            (r"/mblog/talk",                        ListTalkMblogHandler),
            (r"/mblog/reply",                       ReplyMblogHandler),
            (r"/mblog/share",                       ShareMblogHandler),
            (r"/mblog/delete",                      DeleteMblogHandler),
            (r"/mblog/post",                        ShowMblogPostHandler),
            (r"/mblog/support",                     SuporteActivHandler),
            (r"/mblog/%s" % (NOMEUSERS),            MblogHandler)
    ])
