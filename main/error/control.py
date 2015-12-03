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

from core.dispatcher import BaseHandler, HANDLERS, URL_TO_PAGETITLE

from tornado.web import HTTPError

""" Atenção: este módulo deve ser o último controlador a ser importado no main.py """

class ErrorHandler(BaseHandler):
    ''' Alternativa para gerar erro 404 quando a url não é atendida por nenhum outro controlador '''
    
    def get(self, x):
        raise HTTPError(404)        


URL_TO_PAGETITLE.update ({
        "Error": "error"
    })

HANDLERS.extend([
            (r"/(.*)",    ErrorHandler)
    ])
