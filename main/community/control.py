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

import re
from datetime import datetime
from uuid import uuid4
from operator import itemgetter

import tornado.web
from tornado.web import HTTPError
import tornado.template

import core.model
from core.model import isACommunity, usersByEmail
import core.database
from core.dispatcher import BaseHandler, HANDLERS,  URL_TO_PAGETITLE, \
                            NOMEUSERS, validateEmail
from config import PLATAFORMA, PLATAFORMA_URL, PRIV_CRIAR_COMUNIDADES
import mblog.model
import wiki.model
import files.model
import blog.model
import forum.model
import agenda.model
import noticia.model
import evaluation.model
import log.model
from libs.notify import Notify

''' importa definição do tutorial deste módulo, se existir _tutorial.py '''
from config import TUTORIAL
try:
    import _tutorial
except ImportError:
    pass

# Número de itens por página.
# Usado pelos controladores que listam: Participantes e Comunidades
NUM_MAX_ITENS = 30

class UserCommunitiesHandler(BaseHandler):
    ''' Lista as comunidades que um usuário participa '''
    @tornado.web.authenticated
    def get(self, registry_id):
        user = self.get_current_user()
        page = int(self.get_argument("page","1"))
        group = self.get_argument("group","")

        _member = core.model.Registry().retrieve(registry_id)
        if not _member or not _member.isAUser():
            raise HTTPError(404)
            return
        
        # Impede a visualização de um grupo de outra pessoa.
        groups_list = []
        if user!=registry_id:
            group = ""

        # Se o grupo não existe, mostra todas as comunidades do usuário.
        # Este caso acontece qdo o grupo acabou de ser removido.
        groups_list = _member.community_groups.keys()
        if group not in groups_list:
            group = ""
                
        communities = _member.getCommunitiesList(group, page, NUM_MAX_ITENS)
        communities_count = _member.countCommunities(group)     
                           
        links=[]
        if group:
            links.append(("Remover este grupo", "/static/imagens/icones/delete32.png", "/communitygroups/delete/"+registry_id+"?group="+group, "return confirm('Deseja realmente remover este grupo? Você continuará participando das comunidades dele.','');"))
            links.append(("Gerenciar participantes deste grupo", "/static/imagens/icones/group32.png", "/communitygroups/"+registry_id+"?group="+group, "", "", True))
        
        if user==registry_id:
            links.append(("Procurar comunidade", "/static/imagens/icones/search32.png", "/communities/search"))
            if PRIV_CRIAR_COMUNIDADES in core.database.REGISTRY[user]["comunidades"]:
                links.append(("Criar comunidade", "/static/imagens/icones/privileges/_communities_new.jpg", "/communities/new"))
                
            #links.append((u"Criar avaliação para várias comunidades", "", "/evaluation/new"))
            
        if group:
            msg = u"Este grupo ainda não possui nenhuma comunidade."
        else:
            msg = u"Este usuário ainda não participa de nenhuma comunidade."
              
        log.model.log(user, u'acessou a lista de comunidades de', objeto=registry_id, tipo="communities", news=False)
                            
        self.render("modules/community/communities-list.html", NOMEPAG='comunidades', \
                    REGISTRY_ID=registry_id, COMMUNITIES=communities, \
                    COMMUNITIES_COUNT=communities_count, \
                    PAGE=page, PAGESIZE=NUM_MAX_ITENS, \
                    THIS_GROUP=group, GROUPS=groups_list, \
                    MSG=msg, \
                    LINKS=links)
    
        
class CommunityHandler(BaseHandler):
    ''' Lista página inicial de uma comunidade '''
    @tornado.web.authenticated
    def get(self, community_id):
        if not isACommunity(community_id):
            raise HTTPError(404)
            return
                    
        # Para evitar esse teste, manter a wiki sempre habilitada.
        if "wiki" in core.database.REGISTRY[community_id]['services']:
            self.redirect ("/wiki/%s/home" % community_id)
        else:
            self.redirect ("/profile/%s" % community_id)


class CommunitySearchHandler(BaseHandler):
    ''' Busca de comunidades '''
    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        self.render("modules/community/community-search-form.html", NOMEPAG="comunidades", REGISTRY_ID=user, MSG="")

    @tornado.web.authenticated
    def post(self):
        user = self.get_current_user()
        comu_description = self.get_argument('comu_description', "")
        id_community = comu_description.split(":")[0]
        
        result = dict()
        if id_community:
            _comu = core.model.Community().retrieve(id_community)
            if _comu:
                url = ""
                texto_link = ""
                if _comu.isVoluntaria():
                    if user not in _comu.participantes and user not in _comu.participantes_pendentes:
                        url = "/community/join/"+id_community
                        texto_link = "Participar desta comunidade"
                if user in _comu.participantes_pendentes:
                    url = "/invites"
                    texto_link = "Aceitar convite para esta comunidade"
                    
                result[id_community] = [_comu.description, _comu.participacao, texto_link, url]
       
        self.render("modules/community/communities-search-list.html", NOMEPAG="comunidades", REGISTRY_ID=user, \
                    RESULTADO=result)


class InviteUserHandler(BaseHandler):
    ''' Convida um usuário para uma comunidade '''

    def setTabs(self, comu):
        tabs = []
        tabs.append(("Papel de administrador", "/community/owners/%s"%comu.id))
        if comu.isMedianteConvite():
            tabs.append((u"Convidar usuário", ""))
            tabs.append((u"Convidar grupo de usuários", "/members/searchgroup/%s"%comu.id))
            tabs.append(("Excluir participantes", "/members/delete/%s"%comu.id))
        else:
            # Não é possível buscar participantes em comunidades obrigatórias e voluntárias 
            self.redirect("/community/owners/%s"%comu.id)
        return tabs
        
    @tornado.web.authenticated
    def get(self, id_community):
        user = self.get_current_user()
        member = self.get_argument('member', "")

        msg = ''
        _comu = core.model.Community().retrieve(id_community)            
        
        if _comu:
            if not _comu.isOwner(user) or not _comu.isMedianteConvite():
                raise HTTPError(403)
                return

            elif not member:
                msg = u'Usuário não especificado!'
             
            else:   
                _member = core.model.Member().retrieve(member)   
                #print [item for item in _member]
                
                if _member:
                    if member in _comu.participantes_pendentes:
                        msg = u'Usuário já convidado! Aguardando resposta...'

                    elif member in _comu.participantes:
                        msg = u'Usuário já está nesta comunidade!'

                    else:
                        _comu.participantes_pendentes.append(member)
                        _comu.save()
                                        
                        _member.comunidades_pendentes.append(id_community)
                        _member.save()
                        
                        # notifica o usuário convidado
                        email_msg = u"Comunidade: "+_comu.description+" ("+id_community+")\n"+\
                                    u"Para aceitar esta solicitação clique no botão abaixo ou acesse o seu Painel de Controle e clique em Convites.\n\n"+\
                                    Notify.assinatura(user, id_community, str(datetime.now()))+"\n\n"
                        Notify.email_notify(member, user, u"convidou você para participar de uma comunidade", \
                                       message=email_msg, \
                                       link="invites")
    
                        log.model.log(user, u'convidou um participante para a comunidade', objeto=id_community, tipo="community", news=False)
                        
                        msg = u'Convite para usuário enviado com sucesso!'
                        
                else:
                    msg = u'Usuário inexistente!'

        else:
            raise HTTPError(404)
            return
            
        #self.redirect("/profile/%s?msg=%d" % (id_community,err))
        self.render("modules/community/invite-form.html", NOMEPAG='participantes', REGISTRY_ID=id_community, MSG=msg,\
                    TABS=self.setTabs(_comu))

      
class SearchMembersHandler(BaseHandler):
    ''' Busca de participantes para a comunidade '''

    def setTabs(self, comu):
        tabs = []
        tabs.append(("Papel de administrador", "/community/owners/%s"%comu.id))
        if comu.isMedianteConvite():
            tabs.append((u"Convidar usuário", ""))
            tabs.append((u"Convidar grupo de usuários", "/members/searchgroup/%s"%comu.id))
            tabs.append(("Excluir participantes", "/members/delete/%s"%comu.id))
        else:
            # Não é possível buscar participantes em comunidades obrigatórias e voluntárias 
            self.redirect("/community/owners/%s"%comu.id)
        return tabs
    
    @tornado.web.authenticated
    def get(self, id_community):
        user = self.get_current_user()
        _comu = core.model.Registry().retrieve(id_community)
        if _comu.isACommunity():
            self.render("modules/community/invite-form.html", NOMEPAG='participantes', \
                        REGISTRY_ID=id_community, MSG="", TABS=self.setTabs(_comu))
        else:
            raise HTTPError(404)

    @tornado.web.authenticated
    def post(self, id_community):
        user = self.get_current_user()
        member_name = self.get_argument('member_name', "")
        member_login = member_name.split(":")[0]
        
        _comu = core.model.Registry().retrieve(id_community)

        for row in core.database.REGISTRY.view('users/partial_data', key=member_login):
            if row.value["nome_completo"] not in member_name:
                self.render("modules/community/invite-form.html", NOMEPAG='participantes', TABS=self.setTabs(_comu), \
                            REGISTRY_ID=id_community, MSG=u"Usuário não encontrado")                            
                return
            
            else:
                _comu = core.model.Community().retrieve(id_community)
                encontrados = dict()
                if member_login in _comu.participantes:
                    encontrados[member_login] = (member_name, u"já participa desta comunidade", "")
                elif member_login in _comu.participantes_pendentes:
                    encontrados[member_login] = (member_name, u"já foi convidado", "")
                else:
                    encontrados[member_login] = (member_name, "convidar", "/invite/"+id_community+"?member="+member_login)
        
                self.render("modules/community/select-member.html", ENCONTRADOS=encontrados, TABS=self.setTabs(_comu), \
                            NOMEPAG='participantes', REGISTRY_ID=id_community)
                return
            
        self.render("modules/community/invite-form.html", NOMEPAG='participantes', TABS=self.setTabs(_comu), \
                    REGISTRY_ID=id_community, MSG=u"Usuário não encontrado")                    
        return


class DeleteMembersHandler(BaseHandler):
    ''' Exclusão de participantes da comunidade '''
    
    def setTabs(self, comu):
        tabs = []
        tabs.append(("Papel de administrador", "/community/owners/%s"%comu.id))
        if comu.isMedianteConvite():
            tabs.append((u"Convidar usuário", "/members/search/%s"%comu.id))
            tabs.append((u"Convidar grupo de usuários", "/members/searchgroup/%s"%comu.id))
            tabs.append(("Excluir participantes", ""))
        else:
            # Esta tela só funciona para comunidades Obrigadórias ou Mediante Convite
            self.redirect("/community/owners/%s"%comu.id)
        return tabs

    @tornado.web.authenticated
    @core.model.owner    
    def get(self, registry_id):
        user = self.get_current_user()

        _comu = core.model.Community().retrieve(registry_id)
        members = _comu.getMembersList()[1]
        members.sort(key=lambda x: x[1])
        members.sort(key=lambda x: x[2], reverse=True)
        
        msg = ""
        if not members:
            msg = u"Esta comunidade ainda não possui nenhum participante."

        self.render("modules/community/del-members-form.html", NOMEPAG='participantes', \
                    REGISTRY_ID=registry_id, TABS=self.setTabs(_comu),\
                    MEMBERS=members, \
                    MSG=msg)

    @tornado.web.authenticated
    @core.model.owner    
    def post(self, registry_id):
        user = self.get_current_user()
        
        msg = ""
        _comu = core.model.Community().retrieve(registry_id)
        members = _comu.getMembersList()[1]
        for member in members:
            if self.get_argument(member[0],"") == "on":
                _comu = core.model.Community().retrieve(registry_id)     
                _comu.delMember(member[0])       

                _member = core.model.Member().retrieve(member[0])                
                _member.delCommunity(registry_id)
                
                msg += member[0] + " removido da comunidade; <br/>"


        if msg=="":
            msg = u"Nenhum participante foi marcado para exclusão da comunidade."

        # pega lista atualizada de participantes
        members = _comu.getMembersList()[1]
        members.sort(key=lambda x: x[1])
        members.sort(key=lambda x: x[2], reverse=True)
            
        self.render("modules/community/del-members-form.html", NOMEPAG='participantes', \
                    REGISTRY_ID=registry_id, TABS=self.setTabs(_comu),\
                    MEMBERS=members, \
                    MSG=msg)
            
class ListMembersHandler(BaseHandler):
    ''' Lista de participantes da comunidade '''
    @tornado.web.authenticated
    @core.model.allowedToAccess
    def get(self, registry_id):
        user = self.get_current_user()
        _comu = core.model.Registry().retrieve(registry_id)

        if _comu.isACommunity():
            page = int(self.get_argument("page","1"))
            group = self.get_argument("group","")
                        
            # se o grupo não existe, mostra todos os participantes da comunidade.
            # este caso acontece qdo o grupo acabou de ser removido.
            if group not in _comu.groups:
                group = "" 
               
            (members_count, members) = _comu.getMembersList(group, page, NUM_MAX_ITENS)
            
            msg = ""
            if not members:
                if group:
                    msg = u"Este grupo ainda não possui nenhum participante."
                else:
                    msg = u"Esta comunidade ainda não possui nenhum participante."

            links = []
            if _comu.isOwner(user):
                if group:
                    links.append(("Remover este grupo", "/static/imagens/icones/delete32.png", "/groups/delete/"+registry_id+"?group="+group, "return confirm('Deseja realmente remover este grupo? Os participantes não serão removidos da comunidade.','');"))
                    links.append(("Gerenciar participantes deste grupo", "/static/imagens/icones/group32.png", "/groups/"+registry_id+"?group="+group, "", "", True))
                if _comu.isMedianteConvite():
                    links.append(("Procurar um usuário e convidá-lo para a comunidade", "/static/imagens/icones/search_member32.png", "/members/search/"+registry_id))
                    links.append(("Convidar um grupo de participantes para a comunidade", "/static/imagens/icones/add_members32.png", "/members/searchgroup/"+registry_id))
                    links.append(("Remover participantes da comunidade", "/static/imagens/icones/del_members32.png", "/members/delete/"+registry_id))
                if _comu.isObrigatoria():
                    links.append(("Convidar um grupo de participantes para a comunidade", "/static/imagens/icones/add_members32.png", "/members/searchgroup/"+registry_id))
                    links.append((u"Administrar participantes (comunidade obrigatória)", "/static/imagens/icones/admin_member32.png", "/members/admin/"+registry_id))            

            log.model.log(user, u'acessou a lista de participantes da comunidade', objeto=registry_id, tipo="community", news=False)
                                    
            self.render("modules/community/members-list.html", NOMEPAG='participantes', \
                        REGISTRY_ID=registry_id, \
                        MEMBERS=members, \
                        MEMBERS_COUNT=members_count, \
                        PAGE=page, PAGESIZE=NUM_MAX_ITENS, \
                        THIS_GROUP=group, GROUPS=_comu.groups.keys(), \
                        IS_OWNER=_comu.isOwner(user), \
                        LINKS=links, \
                        MSG=msg)
            
        else:
            raise HTTPError(404)                    
                    
class AcceptCommunityHandler(BaseHandler):
    ''' Aceita um convite para participar de uma comunidade '''
    
    @tornado.web.authenticated
    def get(self, id_community):
        user = self.get_current_user()
        
        _member = core.model.Member().retrieve(user)  
        if id_community in _member.comunidades_pendentes:
            try:
                _member.comunidades.append(id_community)
                _member.comunidades_pendentes.remove(id_community)
            
                _comu = core.model.Community().retrieve(id_community)  
                _comu.participantes.append(user)
                if user in _comu.participantes_pendentes:
                    _comu.participantes_pendentes.remove(user)
                _comu.save()
    
                _member.save()
            except Exception:
                # se o registry do usuário ou da comunidade está sendo usado ao mesmo tempo pela thread ou por outra requisição, dá erro 503
                raise HTTPError(503)
                return

                        
            log.model.log(user, u'entrou para a comunidade', objeto=id_community, tipo="community")
            self.redirect("/invites")
            
        else:
            # Bad Request
            raise HTTPError(400)  



class RejectCommunityHandler(BaseHandler):
    ''' Rejeita um convite para participar de uma comunidade '''
    
    @tornado.web.authenticated
    def get(self, id_community):      
        user = self.get_current_user()
        
        _member = core.model.Member().retrieve(user)   
        _member.comunidades_pendentes.remove(id_community)
        
        _comu = core.model.Community().retrieve(id_community)   
        _comu.participantes_pendentes.remove(user)

        _member.save()
        _comu.save()
        self.redirect("/invites")


class MembersAdminHandler(BaseHandler):
    ''' Administração de participantes da comunidade '''

    def setTabs(self, comu):
        tabs = []
        tabs.append(("Papel de administrador", "/community/owners/%s"%comu.id))
        if comu.isObrigatoria():
            tabs.append((u"Administrar participantes", ""))
            tabs.append((u"Convidar grupo de usuários", "/members/searchgroup/%s"%comu.id))
        else:
            # Esta tela só funciona para comunidades Obrigadórias ou Mediante Convite
            self.redirect("/community/owners/%s"%comu.id)
        return tabs

    @tornado.web.authenticated
    @core.model.owner
    def get(self, registry_id):
        user = self.get_current_user()
        self._comu = core.model.Registry().retrieve(registry_id)
        if self._comu and self._comu.isACommunity():
            if self._comu.isObrigatoria():
                self.render("modules/community/admin.html", REGISTRY_ID=registry_id, TABS=self.setTabs(self._comu), \
                            NOMEPAG='participantes', \
                            PARTICIPANTES=[x for x in self._comu.participantes if x != self._comu.owner and x != user], \
                            PENDENTES=self._comu.participantes_pendentes, \
                            MSG="")
            else:
                raise HTTPError(403)     
        else:
            raise HTTPError(404)  
        
        
    def excluirParticipantes(self, users):
        for user_id in users:
            if user_id in self._comu.participantes:
                self._comu.participantes.remove(user_id)
            if user_id in self._comu.admins:
                self._comu.admins.remove(user_id)
                
            _member = core.model.Member().retrieve(user_id)
            if self._comu.id in _member.comunidades:
                _member.comunidades.remove(self._comu.id)
            _member.save()
        
        return u"Participantes excluídos."
    
    def incluirParticipantes(self, users):
        msg = ""
        users = users[0].split("\r\n")
        for u in users:
            user_id = u.strip(" ")
            if user_id:
                _member = core.model.Member().retrieve(user_id)
                if _member and _member.isAUser():
                    
                    if user_id not in self._comu.participantes:
                        self._comu.participantes.append(user_id)

                    if self._comu.id not in _member.comunidades:
                        _member.comunidades.append(self._comu.id)
                        _member.save()
                        
                        # notifica o usuário incluído na comunidade
                        email_msg = "Comunidade: "+self._comu.description+" ("+self._comu.id+")\n"+\
                                    u"Clique no botão abaixo para visitá-la.\n\n"+\
                                    Notify.assinatura(self._user, self._comu.id, str(datetime.now()))+"\n\n"
                        Notify.email_notify(user_id, self._user, u"incluiu você como participante de uma comunidade", \
                                       message=email_msg, \
                                       link="community/"+self._comu.id)

                else:
                    msg += user_id + " "

        return "Usuário(s) não encontrado(s): " + msg if msg else "Todos os usuários foram incluídos."
        
    def incluirPendentes(self, users):
        msg = ""
        for user_id in users:

            if user_id:
                _member = core.model.Member().retrieve(user_id)
                if _member and _member.isAUser():
                    
                    if user_id not in self._comu.participantes:
                        self._comu.participantes.append(user_id)

                    if user_id in self._comu.participantes_pendentes:
                        self._comu.participantes_pendentes.remove(user_id)

                    if self._comu.id not in _member.comunidades:
                        _member.comunidades.append(self._comu.id)
                    
                    if self._comu.id in _member.comunidades_pendentes:
                        _member.comunidades_pendentes.remove(self._comu.id)
                    
                    _member.save()
                   
            else:
                msg += user_id + " "
                
        return "Usuário(s) não encontrado(s): " + msg if msg else "Convidados pendentes incluídos."
        
    def excluirPendentes(self, users):
        for user_id in users:
            if user_id in self._comu.participantes_pendentes:
                self._comu.participantes_pendentes.remove(user_id)
                
            _member = core.model.Member().retrieve(user_id)
            if self._comu.id in _member.comunidades_pendentes:
                _member.comunidades_pendentes.remove(self._comu.id)
            _member.save()
        
        return u"Convidados pendentes excluídos."

        
    @tornado.web.authenticated
    @core.model.owner
    def post(self, registry_id):
        self._user = self.get_current_user()
        self._comu = core.model.Registry().retrieve(registry_id)

        if self._comu and self._comu.isACommunity():
            if self._comu.isObrigatoria():
                tipo = self.get_argument("tipo", "")
                oper = self.get_argument("oper", "")
                
                if "users" in self.request.arguments:
                    users = self.request.arguments["users"] # users é uma lista
                    if tipo == "excluirparticipantes":
                        msg = self.excluirParticipantes(users)
                        self._comu.save()
                    elif tipo == "incluirparticipantes":
                        msg = self.incluirParticipantes(users)
                        self._comu.save()
                    elif tipo == "alterarpendentes":
                        if oper == "Incluir":
                            msg = self.incluirPendentes(users)
                            self._comu.save()
                        elif oper == "Excluir":
                            msg = self.excluirPendentes(users)
                            self._comu.save()
                        else:
                            msg = u"Erro: operação inválida."
                    else:
                        msg = u"Erro: tipo inválido."
                else:
                    msg = u"Erro: nenhum usuário foi selecionado."
  
                self.render("modules/community/admin.html", REGISTRY_ID=self._comu.id, TABS=self.setTabs(self._comu), \
                            NOMEPAG='participantes', \
                            PARTICIPANTES=[x for x in self._comu.participantes if x != self._comu.owner and x != self._user], \
                            PENDENTES=self._comu.participantes_pendentes, \
                            MSG=msg)
                            
            else:
                raise HTTPError(403)     
        else:
            raise HTTPError(404)  


class CommunityOwnersHandler(BaseHandler):
    ''' Delegação do papel de administrador de uma comunidade '''
    
    def setTabs(self, comu):
        tabs = []
        tabs.append(("Papel de administrador", ""))
        if comu.isMedianteConvite():
            tabs.append((u"Convidar usuário", "/members/search/%s"%comu.id))
            tabs.append((u"Convidar grupo de usuários", "/members/searchgroup/%s"%comu.id))
            tabs.append(("Excluir participantes", "/members/delete/%s"%comu.id))
        if comu.isObrigatoria():
            tabs.append((u"Administrar participantes", "/members/admin/%s"%comu.id))
            tabs.append((u"Convidar grupo de usuários", "/members/searchgroup/%s"%comu.id))
        return tabs

    @tornado.web.authenticated
    @core.model.owner
    def get(self, id_community):
        _comu = core.model.Registry().retrieve(id_community)
        if _comu.isACommunity():
            self.render("modules/community/owners.html", REGISTRY_ID=id_community, TABS=self.setTabs(_comu), \
                        NOMEPAG='comunidades', MSG="")
        else:
            raise HTTPError(404)

    def excluirAdmins(self, id_community, users):
        _comu = core.model.Registry().retrieve(id_community)        
        for user_id in users:
            if user_id in _comu.admins:
                _comu.admins.remove(user_id)
        _comu.save()

        self.render("modules/community/owners.html", REGISTRY_ID=id_community, TABS=self.setTabs(_comu), \
                    NOMEPAG='comunidades', MSG=u"Exclusão realizada com sucesso.")


    def incluirAdmin(self, id_community, novo_admin):
        _comu = core.model.Registry().retrieve(id_community)        
        if novo_admin not in _comu.admins:
            _comu.admins.append(novo_admin)
            _comu.save()      

        self.render("modules/community/owners.html", REGISTRY_ID=id_community, TABS=self.setTabs(_comu), \
                    NOMEPAG='comunidades', MSG=u"Inclusão realizada com sucesso.")


    @tornado.web.authenticated
    @core.model.owner
    def post(self, id_community):
        tipo = self.get_argument("tipo", "")
        if tipo == "excluir_admins":
            users = self.request.arguments["users"] # users é uma lista
            self.excluirAdmins(id_community, users)
            
        elif tipo == "incluir_admins":
            novo_admin = self.get_argument("novo_admin", "")
            if novo_admin:
                self.incluirAdmin(id_community, novo_admin)
            else:
                self.render("modules/community/owners.html", REGISTRY_ID=id_community, TABS=self.setTabs(_comu), \
                            NOMEPAG='comunidades', MSG=u"Selecione um participante para ser incluído como administrador.")                
        else:
            # Bad Request
            raise HTTPError(400)  


class CommunityJoinHandler(BaseHandler):
    ''' Usuário entra numa comunidade Voluntária '''
    @tornado.web.authenticated
    def get(self, id_community):
        user = self.get_current_user()
            
        _comu = core.model.Registry().retrieve(id_community)
        if _comu and _comu.isVoluntaria():
            
            _member = core.model.Registry().retrieve(user)
            if id_community not in _member.comunidades:
                _member.comunidades.append(id_community)
                _member.save()
                                
            if user not in _comu.participantes:
                _comu.participantes.append(user)
            _comu.save()
                
            self.redirect("/profile/%s" % id_community)
        else:
            raise HTTPError(403)  
        

class CommunityLeaveHandler(BaseHandler):
    ''' Usuário sai de uma comunidade não obrigatória '''
    @tornado.web.authenticated
    def get(self, registry_id):
        user = self.get_current_user()
        _comu = core.model.Registry().retrieve(registry_id)
        if _comu and not _comu.isObrigatoria():
            
            _member = core.model.Registry().retrieve(user)
            if registry_id in _member.comunidades:
                _member.comunidades.remove(registry_id)
                _member.save()

            if user in _comu.participantes:
                _comu.participantes.remove(user)
            if user in _comu.admins:
                _comu.admins.remove(user)
            _comu.save()

            log.model.log(user, u'saiu da comunidade', objeto=registry_id, tipo="community")
            
            # u'Você não participa mais desta comunidade!'
            self.redirect("/profile/%s?msg=101" % registry_id)
            
        else:
            raise HTTPError(403)  


    
    
class DeleteCommunityHandler(BaseHandler):
    ''' Exclusão de comunidade vazia '''
    
    def communityHasWiki(self,community_id):
    
        for row in wiki.database.WIKI.view('wiki/partial_data',startkey=[community_id],endkey=[community_id, {}]):
          (registry_id, doc_id) = row.key
          if doc_id.split("/")[1] != "indice" and doc_id.split("/")[1] != "home":
              return True
        return False
        
    def deleteCommunity(self, community_id, remove_content=False):
        user = self.get_current_user()
        
        community_data = core.database.REGISTRY[community_id]
        
        # remove a comunidade da lista de comunidades de cada participante
        for part in community_data["participantes"]:
            user_data = core.database.REGISTRY[part]
            if community_id in user_data["comunidades"]:
                user_data["comunidades"].remove(community_id)
                core.database.REGISTRY[part] = user_data
            
        # remove a comunidade da lista de comunidades_pendentes de cada participante_pendente
        for pend in community_data["participantes_pendentes"]:
            user_data = core.database.REGISTRY[pend]
            if community_id in user_data["comunidades_pendentes"]:
                user_data["comunidades_pendentes"].remove(community_id)
                core.database.REGISTRY[pend] = user_data
                
        if remove_content:
            pass
            # remove wikis
            # remove blogs
            # remove mblogs
            # remove arquivos
            # remove forum
            # remove agenda
            # remove notícias
            # remove avaliações
            # etc
    
        # remove as páginas indice e home da wiki
        _wiki = wiki.model.Wiki().retrieve("%s/home" % community_id)
        if _wiki: _wiki.deleteWiki(user, permanently=True)
                        
        _wiki = wiki.model.Wiki().retrieve("%s/indice" % community_id)
        if _wiki: _wiki.deleteWiki(user, permanently=True)
    
        # remove a comunidade
        del core.database.REGISTRY[community_id]
           
    @tornado.web.authenticated
    @core.model.owner
    def get(self, community_id):
        user = self.get_current_user()

        if not mblog.database.MBLOG.view('mblog/by_followers',startkey=[community_id],endkey=[community_id, {}]) and \
           not self.communityHasWiki(community_id) and \
           not files.database.FILES.view('files/partial_data',startkey=[community_id],endkey=[community_id, {}]) and \
           not blog.database.BLOG.view('blog/partial_data',startkey=[community_id],endkey=[community_id, {}]) and \
           not core.model.ActivDB.registry_id_has_objects(community_id) and \
           (community_id not in agenda.database.AGENDA or agenda.database.AGENDA[community_id]["events"] == {}) and \
           (community_id not in noticia.model.NOTICIAS or noticia.model.NOTICIAS[community_id]["news"] == []) and \
           not evaluation.database.EVALUATION.view('evaluation/all_data',startkey=[community_id],endkey=[community_id, {}]):

                self.deleteCommunity(community_id)
                self.render("home.html", MSG=u"Comunidade excluída com sucesso.", NOMEPAG='comunidades')
        
        else:
             self.redirect("/profile/%s?msg=106" % community_id)


class SearchGroupHandler(BaseHandler):
    ''' Busca um grupo de emails (já cadastrados no Activ ou não) para convidá-los para uma comunidade '''

    def setTabs(self, comu):
        tabs = []
        tabs.append(("Papel de administrador", "/community/owners/%s"%comu.id))
        if comu.isMedianteConvite():
            tabs.append((u"Convidar usuário", "/members/search/%s"%comu.id))
            tabs.append((u"Convidar grupo de usuários", ""))
            tabs.append(("Excluir participantes", "/members/delete/%s"%comu.id))
        elif comu.isObrigatoria():
            tabs.append((u"Administrar participantes", "/members/admin/%s"%comu.id))
            tabs.append((u"Convidar grupo de usuários", ""))
        else:
            # Esta tela só funciona para comunidades Obrigadórias ou Mediante Convite
            self.redirect("/community/owners/%s"%comu.id)
        return tabs

    @tornado.web.authenticated
    @core.model.owner
    def get(self, id_community): 
        _comu = core.model.Community().retrieve(id_community)    

        if _comu.isACommunity():
            self.render("modules/community/searchgroup-form.html", REGISTRY_ID=id_community, TABS=self.setTabs(_comu), \
                        NOMEPAG='participantes', MSG=u"")        
        else:
            raise HTTPError(404)
  
  
    @tornado.web.authenticated
    @core.model.owner
    def post(self, id_community):
        user = self.get_current_user()
        _comu = core.model.Community().retrieve(id_community)            
        
        if _comu:
            emails = self.get_argument("emails", "").lower()
            #print emails
            #re.split(',|\s', emails)
            #print emails
            email_array = list(set(emails.split()))
            
            users_list = []
            not_users_list = []
            error_list = []
            
            form_convidar = False
            form_chamar = False
                          
            if not email_array:
                self.render("modules/community/searchgroup-form.html", REGISTRY_ID=id_community, TABS=self.setTabs(_comu), \
                            NOMEPAG='participantes', MSG=u"Informe a lista de emails que deseja convidar.")  
                
            else:
                for email in email_array:
                    if not validateEmail(email):
                        error_list.append(email)
                    else:
                        member_list = usersByEmail(email)
                        if member_list:
                            for member in member_list:
                                _member = core.model.Member().retrieve(member)   
                                status = ""
                                if member in _comu.participantes:
                                    status = u"já participa desta comunidade"
                                elif member in _comu.participantes_pendentes:
                                    status = u"já foi convidado"
                                else:
                                    status = "convidar"
                                    form_convidar = True
    
                                users_list.append((member,_member.getFullName(), status, email))
                                users_list = sorted(users_list, key=itemgetter(2), reverse=True)
                        else: 
                            status = ""
                            if email in _comu.participantes_chamados:
                                status = u"já foi chamado"
                            else:
                                status = "chamar"
                                form_chamar = True
    
                            not_users_list.append((email, status))
                            not_users_list = sorted(not_users_list, key=itemgetter(1), reverse=True)

                self.render("modules/community/invitegroup-form.html", REGISTRY_ID=id_community, TABS=self.setTabs(_comu), \
                            EMAILS=emails, \
                            USERSLIST=users_list, NOTUSERSLIST=not_users_list, ERRORLIST=error_list, \
                            FORMCONVIDAR=form_convidar, FORMCHAMAR=form_chamar, \
                            NOMEPAG='participantes', MSG=u"")                            


        else:
            raise HTTPError(404)
                                

class InviteGroupHandler(BaseHandler):
    ''' Convida um grupo usuários para uma comunidade '''

    @tornado.web.authenticated
    @core.model.owner
    def post(self, id_community):
        user = self.get_current_user()
        
        _comu = core.model.Community().retrieve(id_community)            
        if _comu:
            convidados = self.get_arguments("users")
            emails = self.get_argument("emails", "")
            
            for convidado in convidados:
                _member = core.model.Member().retrieve(convidado)   

                if _comu.isMedianteConvite():
                    
                    # convida usuário para a comunidade 
                    
                    if convidado not in _comu.participantes_pendentes and convidado not in _comu.participantes:
                        _comu.participantes_pendentes.append(convidado)
                        _comu.save()
                                        
                        _member.comunidades_pendentes.append(id_community)
                        _member.save()
                        
                        # notifica o usuário convidado
                        email_msg = u"Comunidade: "+_comu.description+" ("+id_community+")\n"+\
                                    u"Para aceitar esta solicitação clique no botão abaixo ou acesse o seu Painel de Controle e clique em Convites.\n\n"+\
                                    Notify.assinatura(user, id_community, str(datetime.now()))+"\n\n"
                        Notify.email_notify(convidado, user, u"convidou você para participar de uma comunidade", \
                                       message=email_msg, \
                                       link="invites")

                elif _comu.isObrigatoria():   # obrigatória
                    
                    # inclui usuário na comunidade
                    
                    if convidado not in _comu.participantes:
                        _comu.participantes.append(convidado)
                        _comu.save()

                    if _comu.id not in _member.comunidades:
                        _member.comunidades.append(_comu.id)
                        _member.save()
                        
                        # notifica o usuário incluído na comunidade
                        email_msg = "Comunidade: "+_comu.description+" ("+_comu.id+")\n"+\
                                    u"Clique no botão abaixo para visitá-la.\n\n"+\
                                    Notify.assinatura(user, _comu.id, str(datetime.now()))+"\n\n"
                        Notify.email_notify(convidado, user, u"incluiu você como participante de uma comunidade", \
                                       message=email_msg, \
                                       link="community/"+_comu.id)                      

            # POST   /members/searchgroup/%s
            # gera novamente a tela com os usuários
            log.model.log(user, u'convidou um grupo de usuários para a comunidade', objeto=id_community, tipo="community", news=False)            
            self.render("modules/community/searchgroup-hidden-form.html", REGISTRY_ID=id_community, EMAILS=emails)
            
        else:
            raise HTTPError(404)            
            

class CallGroupHandler(BaseHandler):
    ''' Chama um grupo de emails para o Activ '''

    def _send_email(self, quem_convidou, convidado, comunidade):
        assunto = "Convite para participar da comunidade %s na plataforma %s" % (comunidade, PLATAFORMA)
    
        msg_txt = (u"Você foi convidado por %s para participar da comunidade %s no %s e seu email %s não consta entre os usuários cadastrados na plataforma.\n\n" + \
                   u"Caso você já seja usuário do %s e esteja cadastrado com outro email, avise %s para que ele possa lhe reenviar o convite para o email correto.\n\n" + \
                   u"Para se cadastrar no %s, acesse a intranet da UFRJ e clique em 'ActivUFRJ' na tela principal. \n\n") % \
                   (quem_convidou, comunidade, PLATAFORMA, convidado, PLATAFORMA, quem_convidou, PLATAFORMA)
                    
        if Notify.enviaEmail (convidado, assunto, convidado, msg_txt, ""):
           return u"E-mail enviado com sucesso.<br/>"
        else:
           return u"Erro no envio do E-mail.<br/>"    
     
  
    @tornado.web.authenticated
    @core.model.owner
    def post(self, id_community):
        user = self.get_current_user()
        
        _comu = core.model.Community().retrieve(id_community)  
        if _comu:
            convidados = self.get_arguments("users")
            emails = self.get_argument("emails", "")

            if convidados:
                _user = core.model.Member().retrieve(user)
                quem_convidou = _user.getFullName()
                                        
                for convidado in convidados:
                    
                    # salva o email do convidado na lista de participantes chamados da comunidade
                    # para quando o usuário se cadastrar pela intranet
                    if convidado not in _comu.participantes_chamados:
                        _comu.participantes_chamados.append(convidado)
                        
                    # envia email com texto instruíndo o usuário a se cadastrar no activ através da intranet
                    self._send_email(quem_convidou, convidado, id_community)        
                    
                _comu.save()
                
                # POST   /members/searchgroup/%s
                # gera novamente a tela com os usuários
                log.model.log(user, u'chamou um grupo de usuários para a comunidade', objeto=id_community, tipo="community", news=False)            
                self.render("modules/community/searchgroup-hidden-form.html", REGISTRY_ID=id_community, EMAILS=emails)
            
        else:
            raise HTTPError(404)   
            
                               
URL_TO_PAGETITLE.update ({
        "communities":   "Comunidades",
        "community":     "Comunidades",
        "members":       "Participantes",
        "invite":        "Comunidades",
        "accept":        "Convites",
        "reject":        "Convites"
    })

HANDLERS.extend([
            (r"/communities/search",                        CommunitySearchHandler),
            (r"/communities/%s" % NOMEUSERS,                UserCommunitiesHandler),
            (r"/community/%s" % NOMEUSERS,                  CommunityHandler),
            (r"/community/owners/%s" % NOMEUSERS,           CommunityOwnersHandler),
            (r"/community/join/%s" % NOMEUSERS,             CommunityJoinHandler),
            (r"/community/leave/%s" % NOMEUSERS,            CommunityLeaveHandler),
            (r"/community/delete/%s" % NOMEUSERS,           DeleteCommunityHandler),
            (r"/members/%s" % NOMEUSERS,                    ListMembersHandler),
            (r"/invite/%s" % NOMEUSERS,                     InviteUserHandler),
            (r"/accept/%s" % NOMEUSERS,                     AcceptCommunityHandler),
            (r"/reject/%s" % NOMEUSERS,                     RejectCommunityHandler),
            (r"/members/admin/%s" % NOMEUSERS,              MembersAdminHandler),
            (r"/members/delete/%s" % NOMEUSERS,             DeleteMembersHandler),            
            (r"/members/search/%s" % NOMEUSERS,             SearchMembersHandler),
            (r"/members/searchgroup/%s" % NOMEUSERS,        SearchGroupHandler),
            (r"/members/invitegroup/%s" % NOMEUSERS,        InviteGroupHandler),
            (r"/members/callgroup/%s" % NOMEUSERS,          CallGroupHandler)
        ])
