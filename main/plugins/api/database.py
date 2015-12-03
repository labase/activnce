# -*- coding: utf-8 -*-
"""
###############################################
AgileUFRJ - Implementando as teses do PPGI
###############################################

:Author: *Carlo E. T. Oliveira*
:Contact: carlo@nce.ufrj.br
:Date: $Date: 2010/07/13  $
:Status: This is a "work in progress"
:Revision: $Revision: 0.01 $
:Home: `LABASE `__
:Copyright: ©2009, `GPL 
"""
from couchdb import Server


from datetime import datetime
from time import mktime, strptime
ANY, INI = 'A_N_Y', 'I_N_I'
GROUP = ANY
import logging

class Activ(Server):
    "Active database"
    application = {}
   
    def __init__(self, url,dbases):
        Server.__init__(self, url)
        self.d_b_s= dbases
        act = self
        test_and_create = lambda doc: doc in act and act[doc] or act.create(doc)
        for attribute in self.d_b_s:
            if '_' in attribute :
                attr = attribute.split('_')[1]
            else:
                attr = attribute
            setattr(Activ, attr, test_and_create(attribute))
            
    def erase_database(self):
        'erase tables'
        for table in self.d_b_s:
            try:
                del self[table]
            except:
                pass

try:
    from db import _DOCBASES
except:
    _DOCBASES = ['application']
    
logging.info("got answers:  %s" ,_DOCBASES)    
ACTIV = Activ('http://127.0.0.1:5984/',_DOCBASES)

DAPP = ACTIV.application

