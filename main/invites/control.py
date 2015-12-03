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
from uuid import uuid4

import tornado.web
from tornado.web import HTTPError
import tornado.template
import model
from model import  _EMPTYKEYS, _EMPTYINVITES, _EMPTYREQUESTINVITEFORM, _REQUESTINVITEFORM, _EDITREQUESTINVITEFORM, \
                   _EMPTYREQUESTINVITE

import core.model
from core.model import _EMPTYMEMBER, _EMPTYCOMMUNITY
from core.model import isMember
from core.model import emailExists, usersByEmail, isACommunity, isOwner

import core.database
from core.dispatcher import BaseHandler, HANDLERS,  URL_TO_PAGETITLE, \
                            NOMEUSERS, PAGENAMECHARS, \
                            GenMagicKey, validateEmail
                            
import log.model
from config import PLATAFORMA, PLATAFORMA_URL, PRIV_GLOBAL_ADMIN, PRIV_CONVIDAR_USUARIOS
from libs.notify import Notify
from libs.dateformat import verificaIntervaloDMY, short_datetime, short_date
from libs.strformat import remove_diacritics, remove_special_chars

''' importa definição do tutorial deste módulo, se existir _tutorial.py '''
from config import TUTORIAL
try:
    import _tutorial
except ImportError:
    pass

def enviaConvite(self, user, convidado, key):
    
    assunto = "Convite para a plataforma %s" % PLATAFORMA
    msgTxt = (u"Você foi convidado por %s para a plataforma educacional %s.\n\n" + \
              u"Clique no botão abaixo ou copie e cole o endereço " + \
              u"http://%s/new/user?mkey=%s\n\n no seu navegador para se cadastrar. \n\n") % \
                  (user, PLATAFORMA, PLATAFORMA_URL, key)

    if Notify.enviaEmail (convidado, assunto, convidado, msgTxt, "new/user?mkey=%s" % key):
       return u"Convite enviado com sucesso.<br/>"
    else:
       return u"Erro no envio do E-mail. Clique em reenviar para tentar novamente.<br/>"    


def showInvitesPage (cls, user, msg, email_list="", community_list=""):
    
    magic_keys = dict()
    forms = dict()

    # processa lista de convidados de um usuário
    for key in core.database.REGISTRY[user]['mykeys']:
        if key in model.MAGKEYS:
            key_data = _EMPTYKEYS()
            key_data.update(model.MAGKEYS[key])
            key_data["datafmt"] = short_datetime (key_data["data_convite"])
            magic_keys[key] = key_data
            

    # para cada formulário...
    for form in model.REQUESTINVITEFORM.view('requestinviteform/all_data',startkey=[user],endkey=[user, {}]):
        form_id = form.key[1]           # registry_id/nome_form
        forms[form_id] = dict(titulo=form.value["titulo"], \
                                      data_inicio=form.value["data_inicio"], \
                                      data_encerramento=form.value["data_encerramento"],
                                      pendentes=[],
                                      recusados=[],
                                      aprovados=[])
        
        # processa suas inscrições pendentes...
        for rqst in model.REQUESTINVITE.view('requestinvitespendentes/all_data',startkey=[user,form_id],endkey=[user,form_id, {}]):
            request_dict = dict(request_id=rqst.value["_id"], 
                                nome=rqst.value["nome"], 
                                email=rqst.value["email"], 
                                campo_livre=rqst.value["campolivre"], 
                                data_cri=short_datetime(rqst.value["data_cri"]))
            forms[form_id]["pendentes"].append(request_dict)
    
        # processa suas inscrições recusadas...
        for rqst in model.REQUESTINVITE.view('requestinvitesrecusados/all_data',startkey=[user,form_id],endkey=[user,form_id, {}]):
            request_dict = dict(request_id=rqst.value["_id"], 
                                nome=rqst.value["nome"], 
                                email=rqst.value["email"], 
                                campo_livre=rqst.value["campolivre"], 
                                data_cri=short_datetime(rqst.value["data_cri"]))
            forms[form_id]["recusados"].append(request_dict)
    
        # processa suas inscrições aprovadas...
        for rqst in model.REQUESTINVITE.view('requestinvitesaprovados/all_data',startkey=[user,form_id],endkey=[user,form_id, {}]):
            # verifica se este email já existe no registry
            usuarios = usersByEmail(rqst.value["email"])
            if usuarios:
                # se encontrar mais de um usuário cadastrado com este email, assume o primeiro encontrado.
                msgUsuario = u"<input type='checkbox' name='users' value='%s'> Usuário já cadastrado: %s" % (usuarios[0], usuarios[0])
            else:
                msgUsuario = u"Convite enviado: aguardando registro do usuário."

            request_dict = dict(request_id=rqst.value["_id"], 
                                nome=rqst.value["nome"], 
                                email=rqst.value["email"], 
                                campo_livre=rqst.value["campolivre"], 
                                msg=msgUsuario,
                                data_cri=short_datetime(rqst.value["data_cri"]))
            forms[form_id]["aprovados"].append(request_dict)
    
    links = []
    if isMember(user, PRIV_CONVIDAR_USUARIOS):
        links.append((u"Novo formulário", "/static/imagens/icones/new32.png", "/invites/createform"))

    cls.render("modules/invites/invites.html", REGISTRY_ID=user, MAGICKEYS=magic_keys, \
                    EMAIL_LIST=email_list, COMMUNITY_LIST=community_list, \
                    REQUESTINVITEFORMS=forms, \
                    IS_ADMIN= isMember(user, PRIV_GLOBAL_ADMIN), \
                    IS_ALLOWED_TO_INVITE= isMember(user, PRIV_CONVIDAR_USUARIOS), \
                    LINKS=links, \
                    MSG=msg, \
                    NOMEPAG="convites")
        
        
class InvitesHandler(BaseHandler):
    ''' GET: Lista a página de convites de um usuário '''
    ''' POST: Convida um usuário '''


    def _send_invites(self, email, user, comunidades):
        #Cria nova chave que sera utilizada pelo usuario convidado
        magic_data = _EMPTYKEYS()
        magic_data['user'] = user
        newKey = GenMagicKey()
        magic_data['magic'] = newKey
        magic_data['email'] = email
        magic_data['comunidades'] = comunidades
        magic_data['data_convite'] = str(datetime.now())
        model.MAGKEYS[newKey] = magic_data
        
        # Atualiza a lista de chaves emitidas pelo usuário que fez o convite
        user_data = _EMPTYMEMBER()
        user_data.update(core.database.REGISTRY[user])
        user_data["mykeys"].append(newKey)
        core.database.REGISTRY[user] = user_data
        
        # Guarda log com o convite enviado
        invite_data = _EMPTYINVITES()
        if user in model.INVITES:
            invite_data.update(model.INVITES[user])
        invite_data["convites_enviados"].append (
                         { "email": email,
                           "data_cri": magic_data['data_convite'] }
        )
        model.INVITES[user] = invite_data
        
        # envia e-mail com convite
        msg = enviaConvite(self, user, email, newKey)


    def _validate_emails(self, email_array):
        msg_erro = ''
        for email in email_array:
            if not validateEmail(email):
                msg_erro += u"E-mail inválido: %s<br/>"%email
        return msg_erro
    
    def _already_invited(self, email_array, lista_invited):
        invited_before = [email for email in lista_invited if email in email_array]
        return invited_before
          
    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        showInvitesPage(self, user, "")
        
    @tornado.web.authenticated
    def post(self):
        user = self.get_current_user()
        msg = ""
            
        #Email agora é um array
        emails = self.get_argument("email", "")
        email_array = list(set(emails.split()))
        
        msg += self._validate_emails(email_array)
        
        user_keys = core.database.REGISTRY[user]['mykeys']
        lista_invited = [ model.MAGKEYS[key]["email"] for key in user_keys]
            
        invited_before = self._already_invited(email_array,lista_invited)
        
        if invited_before:
            for mail in invited_before:
                msg += u"Você já convidou o e-mail: %s<br/>" %mail
        
        for email in email_array:
            if emailExists(email):
                msg += u"Já existe um usuário cadastrado com o email: %s<br/>" % email
        
        # Comunidades é uma lista das comunidades default do usuário
        # que vai se cadastrar com esta chave
        comunidades = []
        for comu in list(set(self.get_argument("comunidades", "").split())):
            if isACommunity(comu):
                if isOwner(user, comu) or isMember(user, PRIV_GLOBAL_ADMIN):
                    comunidades.append(comu)
                else:
                    msg += u"Você deve ser dono ou administrador da comunidade %s.<br/>" % comu
                    
            else:
                msg += u"Comunidade %s não existente.<br/>" % comu
        
        if not msg:
            [self._send_invites(mail, user, comunidades) for mail in email_array]

            request_id = self.get_argument("request_id", "")
            if request_id != "":
                request_data = _EMPTYREQUESTINVITE()
                request_data.update(model.REQUESTINVITE[request_id])
                request_data["estado"] = "aprovado"
                model.REQUESTINVITE[request_id] = request_data
        else:
            msg += u"Os convites não foram enviados.<br/>"

        if msg:
            showInvitesPage(self, user, msg, email_list=emails, community_list=self.get_argument("comunidades", ""))
        else:
            showInvitesPage(self, user, u"Convites enviados com sucesso.<br/>")
            


class DeleteInviteHandler(BaseHandler):
    ''' Remove um convite de um usuário '''
    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        key = self.get_argument("key","")
        if key and key in model.MAGKEYS and user == model.MAGKEYS[key]["user"]:
            user_data = core.database.REGISTRY[user]
            if key in user_data["mykeys"]:
                user_data["mykeys"].remove(key)
                core.database.REGISTRY[user] = user_data
            
            del model.MAGKEYS[key]
            
            msg = u"Convite cancelado."
        else:
            msg = u"Convite inválido."
        showInvitesPage(self, user, msg)


class SendInviteHandler(BaseHandler):
    ''' Reenvia um convite para um usuário '''
    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        key = self.get_argument("key","")
        if key and key in model.MAGKEYS and \
           user == model.MAGKEYS[key]["user"]:
            
            self.render("modules/invites/send-invite.html", REGISTRY_ID=user, \
                        KEY=key, EMAIL=model.MAGKEYS[key]["email"], \
                        NOMEPAG="convites")
            
        else:
            self.render("home.html", REGISTRY_ID=user, MSG=u"Convite inválido.", \
                        NOMEPAG="convites")

    @tornado.web.authenticated
    def post(self):
        user = self.get_current_user()
        key = self.get_argument("key","")
        if key and key in model.MAGKEYS and user == model.MAGKEYS[key]["user"]:
            msg = enviaConvite(self, user, self.get_argument("email",""), key)
            showInvitesPage(self, user, msg)
        else:
            self.render("home.html", REGISTRY_ID=user, MSG=u"Convite inválido.", \
                        NOMEPAG="convites")


class ShowFormInviteHandler(BaseHandler):
    ''' Exibe um formulário de Solicitação de Convites '''
    def get(self, registry_id, form):
        user = self.get_current_user()
        form_id = "%s/%s" % (registry_id, form)
        
        formdata = _EMPTYREQUESTINVITEFORM()
        formdata.update(model.REQUESTINVITEFORM[form_id])
        
        # verifica se está dentro do periodo de validade do formulário 
        v = verificaIntervaloDMY(formdata["data_inicio"], formdata["data_encerramento"])
        if v == 0:
            self.render("modules/invites/show-form-invite.html", REGISTRY_ID=user, \
                        MSG="", \
                        FORMDATA=formdata, \
                        NOMEPAG="convites")
        elif v == -1:
            self.render("home.html", REGISTRY_ID=user, MSG=u"Período de solicitação de convite ainda não iniciado.", \
                        NOMEPAG="convites")
        elif v == 1:
            self.render("home.html", REGISTRY_ID=user, MSG=u"Período de solicitação de convite encerrado.", \
                        NOMEPAG="convites")

    def post(self, registry_id, form):
        
        form_id = "%s/%s" % (registry_id, form)
        
        request_data = _EMPTYREQUESTINVITE()
        request_data["nome"] = self.get_argument("nome","")
        request_data["email"] = self.get_argument("email","")
        request_data["campolivre"] = self.get_argument("campolivre","")

        if request_data["nome"]=="" or request_data["email"]=="" or request_data["campolivre"]=="":
            formdata = _EMPTYREQUESTINVITEFORM()
            formdata.update(model.REQUESTINVITEFORM[form_id])
            self.render("modules/invites/show-form-invite.html", \
                        MSG=u"Todos os campos são obrigatórios", \
                        FORMDATA=formdata, \
                        NOMEPAG="convites")
            
        elif emailExists(request_data["email"]):
            msg = u"O email %s já está cadastrado na plataforma. <a href='/forgotpasswd'>Clique aqui para recuperar a sua senha</a>." % request_data["email"]
            formdata = _EMPTYREQUESTINVITEFORM()
            formdata.update(model.REQUESTINVITEFORM[form_id])
            self.render("modules/invites/show-form-invite.html", \
                        MSG=msg, \
                        FORMDATA=formdata, \
                        NOMEPAG="convites")
            
        else:
            request_data["owner"] = registry_id
            request_data["nome_form"] = form_id
            request_data["estado"] = "pendente"
            request_data["data_cri"] = str(datetime.now())
            
            request_id = uuid4().hex
            model.REQUESTINVITE[request_id] = request_data
            
            formdata = _EMPTYREQUESTINVITEFORM()
            formdata.update(model.REQUESTINVITEFORM[form_id])
            msg = formdata["resposta"]
            self.render("home.html", MSG=msg, \
                        NOMEPAG="convites")


class CreateFormInviteHandler(BaseHandler):
    ''' Cria um formulário de Solicitação de Convites '''
    @tornado.web.authenticated
    @core.model.userIsCommunityMember (PRIV_CONVIDAR_USUARIOS)
    def get(self):
        user = self.get_current_user()
        formdata = _EMPTYREQUESTINVITEFORM()
        self.render("modules/invites/create-form-invite.html", REGISTRY_ID=user, \
                    MSG="", \
                    FORMDATA=formdata, \
                    NOMEPAG="convites")


    @tornado.web.authenticated
    @core.model.userIsCommunityMember (PRIV_CONVIDAR_USUARIOS)
    def post(self):
        user = self.get_current_user()
        
        formdata = _EMPTYREQUESTINVITEFORM()
        erros = 0
        msg = ""
        for key in _REQUESTINVITEFORM:
            if self.get_argument(key, "") != "" :
                formdata[key] = self.get_argument(key)
            else:
                erros += 1

        if erros > 0:
            msg += u"Há %d campos obrigatórios não preenchidos!<br/>" % erros

        if formdata["titulo"]!="":
            formdata["nome"] = remove_special_chars(remove_diacritics(formdata["titulo"].replace(" ","_")))
            if formdata["nome"]=="":
                msg += u"Título do formulário inválido.<br/>"
            
        if msg:
            self.render("modules/invites/create-form-invite.html", REGISTRY_ID=user, \
                        FORMDATA=formdata, \
                        MSG=msg,\
                        NOMEPAG="convites")
        else:
            formdata["owner"] = user
            formdata["data_cri"] = str(datetime.now())
            formdata["data_alt"] = formdata["data_cri"]
            
            id = "%s/%s" % (user, formdata["nome"])
            model.REQUESTINVITEFORM[id] = formdata
            
            showInvitesPage(self, user, "")


class EditFormInviteHandler(BaseHandler):
    ''' Altera um formulário de Solicitação de Convites '''
    @tornado.web.authenticated
    @core.model.userIsCommunityMember (PRIV_CONVIDAR_USUARIOS)
    def get(self, registry_id, form):
        user = self.get_current_user()
        # Se o formulário não foi criado por mim, ele não pode ser alterado
        if user != registry_id:
            raise HTTPError(403)    
        else:
            form_id = "%s/%s" % (registry_id, form)
            if form_id in model.REQUESTINVITEFORM:
        
                formdata = _EMPTYREQUESTINVITEFORM()
                formdata.update(model.REQUESTINVITEFORM[form_id])
                
                self.render("modules/invites/edit-form-invite.html", REGISTRY_ID=user, \
                            MSG="", \
                            FORMDATA=formdata, \
                            NOMEPAG="convites")
            else:
                raise HTTPError(404)    

    @tornado.web.authenticated
    @core.model.userIsCommunityMember (PRIV_CONVIDAR_USUARIOS)
    def post(self, registry_id, form):
        user = self.get_current_user()
        # Se o formulário não foi criado por mim, ele não pode ser alterado
        if user != registry_id:
            raise HTTPError(403)    
        else:
            form_id = "%s/%s" % (registry_id, form)
            if form_id in model.REQUESTINVITEFORM:
        
                formdata = _EMPTYREQUESTINVITEFORM()
                formdata.update(model.REQUESTINVITEFORM[form_id])

                erros = 0
                
                for key in _EDITREQUESTINVITEFORM:
                    if self.get_argument(key, "") != "" :
                        formdata[key] = self.get_argument(key)
                    else:
                        erros += 1
        
                if erros > 0:
                    msg = u"Há %d campos obrigatórios não preenchidos!<br/>" % erros
                    self.render("modules/invites/edit-form-invite.html", REGISTRY_ID=user, \
                                FORMDATA=formdata, \
                                MSG=msg,\
                                NOMEPAG="convites")
                else:
                    formdata["data_alt"] = str(datetime.now())
                    model.REQUESTINVITEFORM[form_id] = formdata
                    showInvitesPage(self, user, u"Formulário alterado com sucesso.")

            else:
                raise HTTPError(404)    


class DeleteFormInviteHandler(BaseHandler):
    ''' Remove um formulário de Solicitação de Convites '''
    @tornado.web.authenticated
    @core.model.userIsCommunityMember (PRIV_CONVIDAR_USUARIOS)
    def get(self, registry_id, form):
        user = self.get_current_user()

        # Se o formulário não foi criado por mim, ele não pode ser apagado
        if user != registry_id:
            raise HTTPError(403)    
        else:
            form_id = "%s/%s" % (registry_id, form)
            if form_id in model.REQUESTINVITEFORM:
                
                # se houver solicitações pendentes neste formulário, ele não pode ser apagado
                if model.REQUESTINVITE.view('requestinvites/exists',startkey=[registry_id,form_id],endkey=[registry_id,form_id, {}]):
                    msg = u"Este formulário já possui solicitações de convite e não pode mais ser removido."
                else:
                    del model.REQUESTINVITEFORM[form_id]
                    msg = u"Formulário removido com sucesso."
                showInvitesPage(self, user, msg)
                
            else:
                raise HTTPError(404)    


class RejectInviteRequestHandler(BaseHandler):
    ''' GET: Lista a página de convites de um usuário '''
    ''' POST: Convida um usuário '''

    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        request_id = self.get_argument("request_id", "")
        if request_id != "":
            request_data = _EMPTYREQUESTINVITE()
            request_data.update(model.REQUESTINVITE[request_id])
            
            if user == request_data["owner"]:
                request_data["estado"] = "recusado"
                model.REQUESTINVITE[request_id] = request_data
                msg = u"Solicitação de convite para %s recusada." % request_data["email"]
            else:
                msg = u"Você não tem permissão para recusar esta solicitação."
        else:
            msg = u"Solicitação inválida."
        showInvitesPage(self, user, msg)


class AddUserToCommunityHandler(BaseHandler):
    ''' Adiciona lista de usuários a uma comunidade obrigatória '''
    
    def incluirParticipantes(self, users):
        msg = ""
        users = users[0].split("\r\n")
        for user1 in users:
            user_id = user1.strip(" ")
            if user_id:
                _member = core.model.Registry().retrieve(user_id)
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
        
        self._comu.save()

        if msg:
            msg = "Usuários não encontrados: " + msg
        else:
            msg = "Todos os usuários foram incluídos."
        # o dono da comunidade não vai na lista pois ele não pode ser removido
        # o usuário logado também não pode ser removido
        participantes = [x for x in self._comu.participantes if x != self._comu.owner and x != self._user]

        self.render("modules/community/admin.html", REGISTRY_ID=self._comu.id, \
                    NOMEPAG='comunidades', \
                    PARTICIPANTES=participantes, \
                    PENDENTES=self._comu.participantes_pendentes, \
                    MSG=msg)
        
    @tornado.web.authenticated
    def post(self):
        self._user = self.get_current_user()
        id_community = self.get_argument("comunidade", "")
        
        if id_community:
            self._comu = core.model.Community().retrieve(id_community)
            if self._comu:
                if self._comu.isObrigatoria():
                    if self._comu.isOwner(self._user):
                        if "users" in self.request.arguments:
                            users = self.request.arguments["users"] # users é uma lista
                            self.incluirParticipantes(users)
                        else:
                            self.render("home.html", MSG=u"Nenhum usuário foi selecionado.", REGISTRY_ID=self._user, \
                                NOMEPAG="convites")
                    else:
                        self.render("home.html", MSG=u"Você não é dono desta comunidade.", REGISTRY_ID=id_community, \
                                    NOMEPAG='comunidades')
                else:
                    self.render("home.html", MSG=u"A forma de participação da comunidade deve ser 'obrigatória'.", REGISTRY_ID=self._user, \
                                NOMEPAG="convites")
            else:
                self.render("home.html", MSG=u"Comunidade inexistente.", REGISTRY_ID=self._user, \
                            NOMEPAG="convites")       

        else:
            self.render("home.html", MSG=u"Comunidade não preenchida.", REGISTRY_ID=self._user, \
                        NOMEPAG="convites")       

                
URL_TO_PAGETITLE.update ({
        "invites":      "Convites"
    })

HANDLERS.extend([
            (r"/invites",                                                InvitesHandler),
            (r"/invites/delete",                                         DeleteInviteHandler),
            (r"/invites/send",                                           SendInviteHandler),
            (r"/invites/showform/%s/%s" % (NOMEUSERS, PAGENAMECHARS),    ShowFormInviteHandler),
            (r"/invites/createform",                                     CreateFormInviteHandler),
            (r"/invites/editform/%s/%s" % (NOMEUSERS, PAGENAMECHARS),    EditFormInviteHandler),
            (r"/invites/deleteform/%s/%s" % (NOMEUSERS, PAGENAMECHARS),  DeleteFormInviteHandler),
            (r"/invites/rejectinviterequest",                            RejectInviteRequestHandler),
            (r"/invites/addusertocommunity",                             AddUserToCommunityHandler),
        ])
