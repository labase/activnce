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

import tornado.web
from tornado.web import HTTPError
import tornado.template
import search.model
from search.model import findTag

from couchdb.http import ResourceConflict

import core.database
import core.model as model
from core.model import _EMPTYMEMBER
from core.model import isAUser

import core.database as database

from core.dispatcher import BaseHandler, HANDLERS,  URL_TO_PAGETITLE, \
                            NOMEUSERS
import log.model
import wiki.model
import blog.model

from libs.notify import Notify
from libs.strformat import remove_diacritics

''' importa definição do tutorial deste módulo, se existir _tutorial.py '''
from config import TUTORIAL
try:
    import _tutorial
except ImportError:
    pass

# Número de itens por página.
# Usado pelo controlador que lista Amigos
NUM_MAX_FRIENDS = 20


class NewFriendHandler(BaseHandler):
    ''' Envio de convite de amizade '''
    
    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        user_data = _EMPTYMEMBER()
        user_data.update(database.REGISTRY[user])
        
        msg = ''
        friend = self.get_argument('friend', "")

        if friend == user:
            msg = u'Você não pode convidar a si mesmo como amigo.'

        elif isAUser(friend):
            if friend in user_data['amigos_convidados']:
                msg = u'Você já convidou %s anteriormente. Aguardando resposta.' % friend
            elif friend in user_data['amigos_pendentes']:
                msg = u'%s já te convidou anteriormente. Aguardando sua resposta.' % friend
            elif friend in user_data['amigos']:
                msg = u'Você já é amigo de %s.' % friend
            else:
                user_data['amigos_convidados'].append(friend)
                
                try:
                    database.REGISTRY[user] = user_data
                except ResourceConflict as detail:
                    # se o registry está sendo usado ao mesmo tempo pela thread dá erro 503
                    raise HTTPError(503)
                
                friend_data = _EMPTYMEMBER()
                friend_data.update(database.REGISTRY[friend])
                friend_data['amigos_pendentes'].append(user)
                database.REGISTRY[friend] = friend_data
                msg = u'Convite para %s enviado com sucesso.' % friend
                
                # notifica o usuário convidado
                email_msg = u"Para aceitar esta solicitação clique no botão abaixo ou acesse o seu Painel de Controle e clique em Convites.\n\n"
                Notify.email_notify(friend, user, u"convidou você para amigo", \
                               message=email_msg, \
                               link="invites")
 
                log.model.log(user, u'convidou um usuário para amigo', tipo="user", news=False)                                      
        else:
            msg = u'Usuário não encontrado.'

        self.render("modules/friends/friend-form.html", NOMEPAG="amigos", REGISTRY_ID=user, MSG=msg)

class SearchFriendsHandler(BaseHandler):
    ''' Busca de amigos do usuário '''
    
    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        self.render("modules/friends/friend-form.html", NOMEPAG="amigos", REGISTRY_ID=user, MSG="")

    @tornado.web.authenticated
    def post(self):
        user = self.get_current_user()
        
        friend_name = self.get_argument('friend_name', "")
        friend_login = friend_name.split(":")[0]

        for row in core.database.REGISTRY.view('users/partial_data', key=friend_login):
                self._member = core.model.Member().retrieve(user)
                encontrados = dict()
                if friend_login in self._member.amigos:
                    encontrados[friend_login] = (friend_name, u"Já é seu amigo","")
                elif friend_login in self._member.amigos_pendentes:
                    encontrados[friend_login] = (friend_name, u"Aceitar convite", "/acceptfriend/"+friend_login)
                elif friend_login in self._member.amigos_convidados:
                    encontrados[friend_login] = (friend_name, u"Já foi convidado", "")
                else:
                    encontrados[friend_login] = (friend_name, "Convidar", "/newfriend?friend="+friend_login)
                        
                self.render("modules/friends/select-friend.html", NOMEPAG="amigos", REGISTRY_ID=user, ENCONTRADOS=encontrados)
                return
            
        self.render("modules/friends/friend-form.html", NOMEPAG="amigos", \
                    REGISTRY_ID=user, MSG=u"Usuário não encontrado.")
        return


class ListFriendsHandler(BaseHandler):
    ''' Lista de amigos de um usuário '''

    @tornado.web.authenticated
    @model.allowedToAccess
    def get(self, registry_id):
        user = self.get_current_user()
        if isAUser(registry_id):
            page = int(self.get_argument("page","1"))
            group = self.get_argument("group","")

            self._user = core.model.Member().retrieve(registry_id)
            
            # Se o grupo não existe, mostra todos os amigos do usuário.
            # Este caso acontece qdo o grupo acabou de ser removido.
            # Impede a visualização de um grupo de outra pessoa.
            if group not in self._user.groups or user!=registry_id:
                group = ""
                
            (friends_count, amigos) = self._user.getFriendsList(group, page, NUM_MAX_FRIENDS, user=user)

            links=[]
            if group:
                links.append(("Remover este grupo", "/static/imagens/icones/delete32.png", "/groups/delete/"+registry_id+"?group="+group, "return confirm('Deseja realmente remover este grupo? Os participantes não sairão da sua lista de amigos.','');"))
                links.append(("Gerenciar participantes deste grupo", "/static/imagens/icones/group32.png", "/groups/"+registry_id+"?group="+group, "", "", True))
            if user==registry_id:
                links.append(("Procurar amigos", "/static/imagens/icones/search32.png", "/friends/search"))
                links.append(("Responder convites", "/static/imagens/icones/invite32.png", "/invites"))
            elif user not in self._user.amigos:
                links.append(("Adicionar "+registry_id+" como amigo", "/static/imagens/icones/add_friend32.png", "/newfriend?friend="+registry_id))

            if group:
                msg = u"Este grupo ainda não possui nenhum amigo."
            else:
                msg = u"Este usuário ainda não possui nenhum amigo."

            log.model.log(user, u'acessou a lista de amigos de', objeto=registry_id, tipo="user", news=False)   
                                
            self.render("modules/friends/friend-list.html", NOMEPAG='amigos', \
                        REGISTRY_ID=registry_id, \
                        FRIENDS=amigos, \
                        FRIENDS_COUNT=friends_count, \
                        PAGE=page, PAGESIZE=NUM_MAX_FRIENDS, \
                        THIS_GROUP=group, GROUPS=self._user.groups.keys(), \
                        MSG=msg, \
                        LINKS=links)
        else:
            # se o registry_id for de uma comunidade
            raise HTTPError(404)    


class SugestFriendsHandler(BaseHandler):
    ''' Amigos sugeridos a um usuário '''

    @tornado.web.authenticated
    def get(self, registry_id):
        user = self.get_current_user()

        if user != registry_id:
            raise HTTPError(403)    
                  
        else:
            self._user = core.model.Member().retrieve(registry_id)
                                    
            # Lista de amigos do usuário
            friends = self._user.getFriendsList()[1]
            
            amigos_pendentes = self._user.amigos_pendentes
            amigos_convidados = self._user.amigos_convidados
            lista_amigos    = []
            conjunto_amigos = []
            friends_list    = []
            lista_final     = []
            
            if friends != []:
                # Lista de amigos dos amigos do usuário
                for friend in friends:
                    self._friend = core.model.Member().retrieve(friend[0])
                    friend_of_friend = self._friend.getFriendsList()[1]
                    
                    if friend_of_friend:
                        lista_amigos.append(friend_of_friend)

                # Eliminação do usuário e seus amigos da lista anterior
                for item in lista_amigos:
                    for item2 in item:
                        if item2[0] != user and item2 not in friends and \
                            item2[0] not in amigos_pendentes and \
                            item2[0] not in amigos_convidados:
                            conjunto_amigos.append(item2)

                # Número de ocorrências dos usuários
                contador = 0
                dict = {}
                conj_amigos = []
                for item in conjunto_amigos:
                    conj_amigos.append(item[0])
                
                for item in conjunto_amigos:
                    contador = conj_amigos.count(item[0])
                    dict[item] = contador
                    contador = 0

                # Ordem decrescente do número de ocorrências
                dicionario = dict.items()
                dict = sorted(dicionario, key=lambda dicionario: dicionario[1])
                dict.reverse()
                dicionario = dict

                # Exibição dos 5 primeiros usuários
                for item in range(0,5):
                    if item < len(dicionario):
                        lista_final.append((dicionario[item][0],dicionario[item][1]))
                    else:
                        break

            self.render("modules/friends/sugest-friend.html", NOMEPAG="amigos", \
                        REGISTRY_ID=registry_id, AMIGOS=lista_final)
 


class AcceptFriendHandler(BaseHandler):
    ''' Gerenciador de amigos do usuário '''
    
    @tornado.web.authenticated
    def get(self, friend):
        user = self.get_current_user()
        user_data = _EMPTYMEMBER()
        user_data.update(database.REGISTRY[user])
        if friend in user_data['amigos_pendentes']:
            user_data['amigos'].append(friend)
            user_data['amigos_pendentes'].remove(friend)
            friend_data = _EMPTYMEMBER()
            friend_data.update(database.REGISTRY[friend])    
            friend_data['amigos'].append(user)
            if user in friend_data['amigos_convidados']:
               friend_data['amigos_convidados'].remove(user)
               
            try:
                database.REGISTRY[user] = user_data
                database.REGISTRY[friend] = friend_data
                log.model.log(user, u'começou uma amizade com', objeto=friend, tipo="user")    
                
                self.redirect("/invites")
            except Exception as detail:
                self.render("home.html", MSG=u"Erro: %s" % detail, REGISTRY_ID=user, \
                        NOMEPAG="amigos")
                
        else:
            self.render("home.html", MSG=u"Convite não encontrado.", REGISTRY_ID=user, \
                        NOMEPAG="amigos")


class RejectFriendHandler(BaseHandler):
    ''' Gerenciador de amigos do usuário '''
    
    @tornado.web.authenticated
    def get(self, friend):
        user = self.get_current_user()
        user_data = _EMPTYMEMBER()
        user_data.update(database.REGISTRY[user])
        if friend in user_data['amigos_pendentes']:       
            user_data['amigos_pendentes'].remove(friend)
            friend_data = _EMPTYMEMBER()
            friend_data.update(database.REGISTRY[friend])    
            if user in friend_data['amigos_convidados']:
               friend_data['amigos_convidados'].remove(user)
            try:
                database.REGISTRY[user] = user_data
                database.REGISTRY[friend] = friend_data
                self.redirect("/invites")
            except Exception as detail:
                self.render("home.html", MSG=u"Erro: %s" % detail, REGISTRY_ID=user, \
                        NOMEPAG="amigos")
        else:
            self.render("home.html", MSG=u"Convite não encontrado.", REGISTRY_ID=user, \
                        NOMEPAG="amigos")


class SugestContentHandler(BaseHandler):
    ''' Conteúdos sugeridos a um usuário '''
    
    def inclui (self, elem, tag, lista):
        if elem not in (x[0] for x in lista):
            lista.append([elem, tag])
        else:
            for i in range(len(lista)):
                if elem == lista[i][0]:
                    lista[i][1] = lista[i][1] + " " + tag
                    break

    @tornado.web.authenticated
    def get(self, registry_id):
        user = self.get_current_user()

        if user != registry_id:
            raise HTTPError(403)             

        else:
            self._user = core.model.Member().retrieve(user)
            tags = self._user.tags
            friends_list = self._user.getFriendsList()[1]
            friends = [ friend[0] for friend in friends_list ]
            
            tags_comuns = []
            paginas = []
            posts = []
            perfis = []
            comunidades = []
            
            if tags:
                for tag in tags:
                    resultado = findTag(remove_diacritics(tag.lower()))
                    tags_comuns.append((tag,resultado))
                
                for item in tags_comuns:
                    # Páginas encontradas
                    for pagina in item[1]['wiki']:
                        registry_id_found = pagina[2]
                        doc_id_found = pagina[3]
                        
                        if registry_id_found in database.REGISTRY and wiki.model.Wiki.nomepagExists(registry_id_found, doc_id_found.split("/")[1]):
                            if database.REGISTRY[registry_id_found]["privacidade"] == u"Pública":
                                if doc_id_found and registry_id_found != user:
                                    self.inclui (doc_id_found, item[0], paginas)
                            else:
                                if isAUser(registry_id_found):
                                    if doc_id_found and registry_id_found != user and \
                                        registry_id_found in database.REGISTRY[user]["amigos"]:
                                        self.inclui (doc_id_found, item[0], paginas)
                                else:
                                    if doc_id_found and registry_id_found in database.REGISTRY[user]["comunidades"]:
                                        self.inclui (doc_id_found, item[0], paginas)

                    # Blogs encontrados
                    for post in item[1]['blog']:
                        registry_id_found = post[2]
                        doc_id_found = post[3]
                        if registry_id_found in database.REGISTRY and doc_id_found in blog.database.BLOG:
                            if database.REGISTRY[registry_id_found]["privacidade"] == u"Pública":
                                if doc_id_found and registry_id_found != user:
                                    self.inclui (doc_id_found, item[0], posts)
                            else:
                                if core.model.isFriendOrMember(user, registry_id_found):
                                    self.inclui (doc_id_found, item[0], posts)
                                '''
                                if isAUser(post.split("/")[0]):
                                    if doc_id_found and registry_id_found != user and \
                                        post.split("/")[0] in database.REGISTRY[user]["amigos"]:
                                        self.inclui (doc_id_found, item[0], posts)
                                else:
                                    if doc_id_found and registry_id_found in database.REGISTRY[user]["comunidades"]:
                                        self.inclui (doc_id_found, item[0], posts)
                                '''
                    
                    # Usuários encontrados
                    for perfil in item[1]['user']:
                        registry_id_found = perfil[2]
                        if registry_id_found and \
                            registry_id_found in database.REGISTRY and \
                            registry_id_found not in friends and \
                            registry_id_found != user and \
                            registry_id_found not in database.REGISTRY[user]["amigos_convidados"] and \
                            registry_id_found not in database.REGISTRY[user]["amigos_pendentes"] and \
                            database.REGISTRY[registry_id_found]["privacidade"] == u"Pública":
                            self.inclui (registry_id_found, item[0], perfis)

                    # Comunidades encontradas
                    for comunidade in item[1]['community']:
                        registry_id_found = comunidade[2]
                        if registry_id_found  and \
                            registry_id_found in database.REGISTRY and \
                            registry_id_found not in database.REGISTRY[user]["comunidades"] and \
                            database.REGISTRY[registry_id_found]["privacidade"] == u"Pública" and \
                            user not in database.REGISTRY[registry_id_found]["participantes"] and \
                            user not in database.REGISTRY[registry_id_found]["participantes_pendentes"] :
                            self.inclui (registry_id_found, item[0], comunidades)

                    paginas.reverse()
                    posts.reverse()

            self.render("modules/friends/sugest-content.html", NOMEPAG="amigos", \
                        REGISTRY_ID=registry_id, PAGINAS=paginas[:20], POSTS=posts[:20], PERFIL=perfis, \
                        COMUNIDADES=comunidades)
  


URL_TO_PAGETITLE.update ({
        "newfriend":     "Amigos",
        "friends":       "Amigos",
        "searchfriends": "Amigos",
        "sugestfriends": "Sugestões",
        "acceptfriend":  "Convites",
        "rejectfriend":  "Convites",
        "sugestcontent": "Sugestões"
    })

HANDLERS.extend([
            (r"/newfriend",                        NewFriendHandler),
            (r"/friends/search",                   SearchFriendsHandler),
            (r"/friends/%s" % NOMEUSERS,           ListFriendsHandler),
            (r"/sugestfriends/%s" % NOMEUSERS,     SugestFriendsHandler),
            (r"/sugestcontent/%s" % NOMEUSERS,     SugestContentHandler),
            (r"/acceptfriend/%s" % (NOMEUSERS),    AcceptFriendHandler),
            (r"/rejectfriend/%s" % (NOMEUSERS),    RejectFriendHandler)
        ])