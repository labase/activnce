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

from datetime import datetime
from uuid import uuid4
import re

_DOCBASES = ['registry', \
             'magkeys',\
             'requestinviteform', \
             'requestinvite']


class Activ(Server):
    "Active database"
    
    def __init__(self, url):
        print "conectando com o banco..."
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
REGISTRY = __ACTIV.registry
MAGKEYS = __ACTIV.magkeys
REQUESTINVITEFORM = __ACTIV.requestinviteform
REQUESTINVITE = __ACTIV.requestinvite


def main():
    print u"criando dicionário por email..."

    dict_by_email = dict()
    for item in REGISTRY:
        if "passwd" in REGISTRY[item]:
            email = REGISTRY[item]["email"]
            user = REGISTRY[item]["user"]
            if email in dict_by_email:
                dict_by_email[email].append(user)
            else:
                dict_by_email[email] = [user]
                
    # para cada formulário...
    for form in REQUESTINVITEFORM.view('requestinviteform/all_data'):
        form_id = form.key[1]           # registry_id/nome_form
        print u"Formulário: ", form_id, "-", form.value["titulo"]
        
        user = form_id.split("/")[0]
        
        # processa suas inscrições pendentes...
        for request in REQUESTINVITE.view('requestinvitespendentes/all_data',startkey=[user,form_id],endkey=[user,form_id, {}]):
            nome = request.value["nome"]
            email = request.value["email"]
            print "   pendente: ", nome, email
            if email in dict_by_email:
                print u"   email já cadastrado: %s (%s)" % (email, len(dict_by_email[email]))
                for cadastrado in dict_by_email[email]:
                    print "      %s" % cadastrado
            
        # processa suas inscrições recusadas...
        for request in REQUESTINVITE.view('requestinvitesrecusados/all_data',startkey=[user,form_id],endkey=[user,form_id, {}]):
            nome = request.value["nome"]
            email = request.value["email"]
            print "   recusada: ", nome, email
            if email in dict_by_email:
                print u"   email já cadastrado: %s (%s)" % (email, len(dict_by_email[email]))
                for cadastrado in dict_by_email[email]:
                    print "      %s" % cadastrado
    
        # processa suas inscrições aprovadas...
        for request in REQUESTINVITE.view('requestinvitesaprovados/all_data',startkey=[user,form_id],endkey=[user,form_id, {}]):
            nome = request.value["nome"]
            email = request.value["email"]
            print "   aprovada: ", nome, email
            if email in dict_by_email:
                print u"   email já cadastrado: %s (%s)" % (email, len(dict_by_email[email]))
                for cadastrado in dict_by_email[email]:
                    print "      %s" % cadastrado

    print "fim do processamento ..."

if __name__ == "__main__":
    main()