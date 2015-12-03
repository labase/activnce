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
:Home: `LABASE <http://labase.nce.ufrj.br/>`__
:Copyright: ©2009, `GPL <http://is.gd/3Udt>__.
"""

REGISTRY_FORM = { "user":"teste",
                  "passwd": "teste",
                  "npasswd": "teste",
                  "name": "fulano",
                  "lastname": "de tal",
                  "email": "teste@localhost",
                  "mkey": "ACTIV_wJGcOEzG8zPDq3BZoReYZxiD" }

LOGIN_FORM = { "user":"teste", "passwd": "teste" }

registry = {}
login = {}

MAGKEYS_DEFAULT = lambda: dict ({
   "_id": "ACTIV_wJGcOEzG8zPDq3BZoReYZxiD",
   #"_rev": "1-3102d912d41b555f8715f85e22165631",
   "comunidades": ["dev_comu_teste"],
   "data_convite": "2012-12-06 11:11:07.287512",
   "magic": "ACTIV_wJGcOEzG8zPDq3BZoReYZxiD",
   "email": "",
   "user": "mauricio"
        
})

PRIVILEGIOS_DEFAULT =  lambda: dict ({
   "Priv_Suporte_Educopedia": {
      "participantes_pendentes": [],
      "description": u"Comunidade dos Responsáveis pelo Suporte aos Usuários da Educopédia",
      "participantes": [
          "teste"
      ],
      "photo": "",
      "owner": "teste",
      "name": "Priv_Suporte_Educopedia",
      "privacidade": u"Privada",
      "participacao": u"Obrigatória",
      "apps": {
                    "/admin/listusers_educo": u"Procurar usuários",
                    "/admin/newusers": u"Convidar novos usuários para a Educopédia"      
        }
   },
   "PRIV_SUPORTE_ACTIV": {
      "participantes_pendentes": [],
      "description": u"Comunidade dos Responsáveis pelo Suporte aos Usuários da plataforma TNM",
      "participantes": [
          "teste"
      ],
      "photo": "",
      "owner": "teste",
      "name": "PRIV_SUPORTE_ACTIV",
      "privacidade": u"Privada",
      "participacao": u"Obrigatória",
      "apps": {
                    "/admin/listusers_tnm": u"Procurar usuários",
                    "/admin/onlineusers": u"Listar usuários online"      
        }
   }
})

