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

from main import WsgiApp
from webtest import TestApp
from webob import Request, Response
from test_core import REGISTRY_FORM, LOGIN_FORM, registry, login, \
                      MAGKEYS_DEFAULT

from datetime import datetime
import core.model
import search.model
import unittest

SEARCHTAGS_DEFAULT = lambda: dict({
   #"python": {
   #   "comunidades" : ["Nome da Comunidade"]
   #   , "paginas" : ["registry_id/nomePagina"]
   #   , "posts" : ["registry_id/nomePost"]
   #   , "perfil" : ["user"]
   #   , "projetos" : []
   #},
   "python": {
      "comunidades" : [
            "ComunidadeMauricio",
            "ComunidadeLivia"
         ]
      , "paginas" : [
            "mauricio/MinhaPag1",
            "mauricio/MinhaPag2",
            "mauricio/MinhaPag3",
            "mauricio/MinhaPag4",
            "mauricio/MinhaPag5",
            "mauricio/MinhaPag6",
            "mauricio/MinhaPag7",
            "mauricio/MinhaPag8",
            "mauricio/MinhaPag9",
            "mauricio/MinhaPag10",
            "mauricio/MinhaPag11",
            "mauricio/MinhaPag12",
            "mauricio/MinhaPag13",
            "mauricio/MinhaPag14",
            "mauricio/MinhaPag15",
            "mauricio/MinhaPag16",
            "mauricio/MinhaPag17",
            "mauricio/MinhaPag18",
            "mauricio/MinhaPag19",
            "mauricio/MinhaPag20",
            "mauricio/MinhaPag21",
            "ComunidadeRoberta/PagComuRoberta",
            "Angela/MinhaPag"
         ]
      , "posts" : [
            "ComunidadeLuDaflon/postComuLuDaflon",
            "newUser/postNewUser",
            "Angela/postAngela1",
            "Angela/postAngela2",
            "Angela/postAngela3",
            "Angela/postAngela4",
            "Angela/postAngela5",
            "Angela/postAngela6",
            "Angela/postAngela7",
            "Angela/postAngela8",
            "Angela/postAngela9",
            "Angela/postAngela10",
            "Angela/postAngela11",
            "Angela/postAngela12",
            "Angela/postAngela13",
            "Angela/postAngela14",
            "Angela/postAngela15",
            "Angela/postAngela16",
            "Angela/postAngela17",
            "Angela/postAngela18",
            "Angela/postAngela19",
            "Angela/postAngela20",
            "Angela/postAngela21",
         ]
      , "perfil" : [
            "mauricio",
            "livia",
            "Angela",
            "ludaflon"
         ]
      , "projetos" : []
   },
   "web": {
      "comunidades" : [
            "ComunidadeMauricio"   
         ]
      , "paginas" : [
            "ComunidadeMauricio/pagComuMauricio"
         ]
      , "posts" : [
            "newUser/postNewUser",
            "ComunidadeMauricio/postComuMauricio"
         ]
      , "perfil" : [
            "mauricio",
            "livia",
            "ludaflon"
         ]
      , "projetos" : []
   },
   "nce": {
      "comunidades" : [
            "ComunidadeMauricio",
            "ComunidadeLuDaflon"
         ]
      , "paginas" : [
            "marcinha/MinhaPag"
         ]
      , "posts" : [
            "ComunidadeLivia/postComuLivia"
         ]
      , "perfil" : [
            "mauricio",
            "marcinha",
            "ludaflon"
         ]
      , "projetos" : []
   },
   "mestrado": {
      "comunidades" : [
            "ComunidadeLuDaflon"   
         ]
      , "paginas" : []
      , "posts" : []
      , "perfil" : [
            "livia",
            "ludaflon"
         ]
      , "projetos" : []
   },
   "rj": {
      "comunidades" : [
            "ComunidadeRoberta"   
         ]
      , "paginas" : []
      , "posts" : []
      , "perfil" : [
            "roberta",
            "ludaflon"
         ]
      , "projetos" : []
   },
   "activ": {
      "comunidades" : [
            "ComunidadeLuDaflon",
            "NewCommunity"
         ]
      , "paginas" : []
      , "posts" : []
      , "perfil" : [
            "newUser",
            "ludaflon"
         ]
      , "projetos" : []
   },
   "ufrj": {
      "comunidades" : [
            "ComunidadeMauricio"
         ]
      , "paginas" : []
      , "posts" : []
      , "perfil" : [
            "julianne",
            "ludaflon"
      ]
      , "projetos" : []
   },
   u"computação": {
      "comunidades" : [
            "ComunidadeRoberta"
         ]
      , "paginas" : []
      , "posts" : []
      , "perfil" : [
            "ludaflon"   
         ]
      , "projetos" : []
   }
})

REGISTRY_DEFAULT = lambda: dict ({
   "mauricio": {
      "user" : "mauricio"
      , "passwd" : "41b9f25030b0ef830fd47d450c714e79"
      , "name" : u"Maurício"
      , "lastname" : "Bonfim"
      , "email" : "mauricio@nce.ufrj.br"
      , "tags" : [
            "python",
            "nce",
            "web"
         ] 
      , "description" : "Desenvolvedor da plataforma OITONOMUNDO."        
      , "photo" : ""
      , "cod_institute" : "0002"
      , "institute" : u"Núcleo de Computação Eletrônica"
      , "amigos" : [
                     "julianne",
                     "tomasbomfim",
                     "livia",
                     "marcinha"
                  ]
      , "amigos_pendentes" : []
      , "amigos_convidados" : [
                                 "roberta",
                                 "Angela"
                              ]
      , "comunidades" : [
                           "ComunidadeMauricio",
                           "ComunidadeLuDaflon"
                        ]
      , "comunidades_pendentes" : [
                                    "nova_Comu",
                                    "comu_publica" 
                                 ]
      , "papeis" : [
                     "admin",
                     "tnm",
                     "educo",
                     "digitador",
                     "professor",
                     "gestor",
                     "super_usuario"
                  ]   # serve tb para definir se o usuário é "tnm" ou "educo"
      , "mykeys" : [
                     "a0002tF0aUOfRB9PHx4iCX2Xv7fSN",
                     "p0002OpAmkvPr2AHbSbV4pR1N3WDk",
                     "p01086bLuF1wO47d4zpzCVxebpY7w",
                     "p01279PkiLIgVoWb5vaI4x4v2PD3R"        
                  ]
      , "privacidade" : u"Pública"           # Pública ou Privada
      , "upload_quota" : 10 * 1024 * 1024    # max 10 Mb
      , "upload_size" : 0
   },
   "julianne": {
      "user" : "julianne"
      , "passwd" : "41b9f25030b0ef830fd47d450c714e79"
      , "name" : "Julianne"
      , "lastname" : "de Carvalho"
      , "email" : "juliannedecarvalho@gmail.com"
      , "tags" : [
               "ufrj"
         ] 
      , "description" : ""        
      , "photo" : ""
      , "cod_institute" : "9999"
      , "institute" : u"Não informada"
      , "amigos" : [
                     "mauricio",
                     "livia",
                     "marcinha",
                  ]
      , "amigos_pendentes" : []
      , "amigos_convidados" : []
      , "comunidades" : [
                           "ComunidadeRoberta",
                        ]
      , "comunidades_pendentes" : []
      , "papeis" : [
                     "tnm"
         ]   # serve tb para definir se o usuário é "tnm" ou "educo"
      , "mykeys" : []
      , "privacidade" : u"Pública"           # Pública ou Privada
      , "upload_quota" : 10 * 1024 * 1024    # max 10 Mb
      , "upload_size" : 0
   },
   "tomasbomfim": {
      "user" : "tomasbomfim"
      , "passwd" : "41b9f25030b0ef830fd47d450c714e79"
      , "name" : u"Tomás"
      , "lastname" : "Bomfim"
      , "email" : "tomasbomfim@hotmail.com"
      , "tags" : [] 
      , "description" : ""        
      , "photo" : ""
      , "cod_institute" : "9999"
      , "institute" : u"Não informada"
      , "amigos" : [
                     "mauricio"
                  ]
      , "amigos_pendentes" : []
      , "amigos_convidados" : []
      , "comunidades" : [
                           "ComunidadeMauricio"
                        ]
      , "comunidades_pendentes" : []
      , "papeis" : [
                     "tnm"
         ]   # serve tb para definir se o usuário é "tnm" ou "educo"
      , "mykeys" : []
      , "privacidade" : u"Pública"           # Pública ou Privada
      , "upload_quota" : 10 * 1024 * 1024    # max 10 Mb
      , "upload_size" : 0
   },
   "livia": {
      "user" : "livia"
      , "passwd" : "41b9f25030b0ef830fd47d450c714e79"
      , "name" : u"Lívia"
      , "lastname" : "Monnerat Castro"
      , "email" : "livia.monnerat@gmail.com"
      , "tags" : [
            "python",
            "mestrado",
            "web"
         ] 
      , "description" : ""        
      , "photo" : ""
      , "cod_institute" : "0002"
      , "institute" : u"Núcleo de Computação Eletrônica"
      , "amigos" : [
                     "mauricio",
                     "julianne",
                     "Angela",
                     "marcinha",
                     "roberta",
                     "ludaflon"
                  ]
      , "amigos_pendentes" : []
      , "amigos_convidados" : []
      , "comunidades" : [
                           "ComunidadeLivia",
                           "ComunidadeMauricio",
                        ]
      , "comunidades_pendentes" : []
      , "papeis" : [
                     "admin",
                     "tnm",
                     "educo",
                     "professor"
                  ]   # serve tb para definir se o usuário é "tnm" ou "educo"
      , "mykeys" : []
      , "privacidade" : u"Pública"           # Pública ou Privada
      , "upload_quota" : 10 * 1024 * 1024    # max 10 Mb
      , "upload_size" : 0
   },
   "marcinha": {
      "user" : "marcinha"
      , "passwd" : "41b9f25030b0ef830fd47d450c714e79"
      , "name" : "Marcia"
      , "lastname" : "Cardoso"
      , "email" : "marcia@nce.ufrj.br"
      , "tags" : [
               "nce"
         ] 
      , "description" : ""        
      , "photo" : ""
      , "cod_institute" : "9999"
      , "institute" : u"Não informada"
      , "amigos" : [
                     "mauricio",
                     "julianne",
                     "livia",
                  ]
      , "amigos_pendentes" : [
                              "newUser",
                           ]
      , "amigos_convidados" : []
      , "comunidades" : []
      , "comunidades_pendentes" : []
      , "papeis" : [
                     "admin",
                     "tnm"
                  ]   # serve tb para definir se o usuário é "tnm" ou "educo"
      , "mykeys" : []
      , "privacidade" : u"Pública"           # Pública ou Privada
      , "upload_quota" : 10 * 1024 * 1024    # max 10 Mb
      , "upload_size" : 0
   },
   "roberta": {
      "user" : "roberta"
      , "passwd" : "41b9f25030b0ef830fd47d450c714e79"
      , "name" : "Roberta"
      , "lastname" : "Tancillo"
      , "email" : "roberta_tancillo@yahoo.com.br"
      , "tags" : [
            "rj"
         ] 
      , "description" : ""        
      , "photo" : ""
      , "cod_institute" : "9999"
      , "institute" : u"Não informada"
      , "amigos" : [
                     "livia"
                  ]
      , "amigos_pendentes" : [
                              "mauricio"
                           ]
      , "amigos_convidados" : []
      , "comunidades" : [
                           "ComunidadeRoberta",
                        ]
      , "comunidades_pendentes" : []
      , "papeis" : [
                     "admin",
                     "tnm"
                  ]   # serve tb para definir se o usuário é "tnm" ou "educo"
      , "mykeys" : []
      , "privacidade" : u"Privada"           # Pública ou Privada
      , "upload_quota" : 10 * 1024 * 1024    # max 10 Mb
      , "upload_size" : 0
   },
   "Angela": {
      "user" : "Angela"
      , "passwd" : "41b9f25030b0ef830fd47d450c714e79"
      , "name" : "Angela"
      , "lastname" : u"Mendonça"
      , "email" : "amanume@gmail.com"
      , "tags" : [
               "python"
         ] 
      , "description" : ""        
      , "photo" : ""
      , "cod_institute" : "9999"
      , "institute" : u"Não informada"
      , "amigos" : [
                     "livia",
                  ]
      , "amigos_pendentes" : [
                                 "mauricio",
                              ]
      , "amigos_convidados" : [
                                 "ludaflon"
                              ]
      , "comunidades" : [
                           "ComunidadeAngela",
                           "NewCommunity",
                        ]
      , "comunidades_pendentes" : []
      , "papeis" : [
                     "admin",
                     "tnm"
                  ]   # serve tb para definir se o usuário é "tnm" ou "educo"
      , "mykeys" : []
      , "privacidade" : u"Privada"           # Pública ou Privada
      , "upload_quota" : 10 * 1024 * 1024    # max 10 Mb
      , "upload_size" : 0
   },
   "newUser": {
      "user" : "aluciarodrigues"
      , "passwd" : "41b9f25030b0ef830fd47d450c714e79"
      , "name" : "New"
      , "lastname" : u"User"
      , "email" : "newuser@email.com"
      , "tags" : [
               "activ"
         ] 
      , "description" : ""        
      , "photo" : ""
      , "cod_institute" : "9999"
      , "institute" : u"Não informada"
      , "amigos" : []
      , "amigos_pendentes" : []
      , "amigos_convidados" : []
      , "comunidades" : [
                           "NewCommunity",
                        ]
      , "comunidades_pendentes" : []
      , "papeis" : [
                     "admin",
                     "tnm"
                  ]   # serve tb para definir se o usuário é "tnm" ou "educo"
      , "mykeys" : []
      , "privacidade" : u"Pública"           # Pública ou Privada
      , "upload_quota" : 10 * 1024 * 1024    # max 10 Mb
      , "upload_size" : 0
   },
   "ludaflon": {
      "user" : "ludaflon"
      , "passwd" : "41b9f25030b0ef830fd47d450c714e79"
      , "name" : "Luciana"
      , "lastname" : u"Daflon"
      , "email" : "daflonbotelho@gmail.com"
      , "tags" : [
            "python",
            "nce",
            "mestrado",
            "rj",
            "activ",
            "ufrj",
            u"computação"
         ] 
      , "description" : ""        
      , "photo" : ""
      , "cod_institute" : "9999"
      , "institute" : u"Não informada"
      , "amigos" : [
                     "livia"
                  ]
      , "amigos_pendentes" : [
                              "Angela",
                              "newUser",
                           ]
      , "amigos_convidados" : [
                                 "marcinha",
                              ]
      , "comunidades" : [
                           "ComunidadeLuDaflon",
                        ]
      , "comunidades_pendentes" : []
      , "papeis" : [
                     "admin",
                     "tnm"
                  ]   # serve tb para definir se o usuário é "tnm" ou "educo"
      , "mykeys" : []
      , "privacidade" : u"Pública"           # Pública ou Privada
      , "upload_quota" : 10 * 1024 * 1024    # max 10 Mb
      , "upload_size" : 0
   },
   "ComunidadeMauricio": {
        "name" : "ComunidadeMauricio"
        , "description" : "Comunidade do Maurício"
        , "tags" : [
            "python",
            "nce",
            "web",
            "ufrj"
        ]
        , "owner" : "mauricio"
        , "photo" : ""
        , "participantes_pendentes" : []
        , "participantes" : [
                              "mauricio",
                              "tomasbomfim",
                              "livia"
                          ]
        , "comunidades" : []                   # comunidades em que esta comunidade está incluída
        , "upload_quota" : 20 * 1024 * 1024    # max 20 Mb
        , "upload_size" : 0
        , "papeis" : []
        , "admins" : []
        , "cod_institute" : "9999"
        , "institute" : u"Não informada"
        , "privacidade" : u"Privada"    # Pública ou Privada
        , "participacao" : "Mediante Convite"   # Mediante Convite, Voluntária ou Obrigatória  
   },
   "ComunidadeLuDaflon": {
        "name" : "ComunidadeLuDaflon"
        , "description" : "Comunidade de Luciana Daflon"
        , "tags" : [
            "nce",
            "mestrado",
            "activ"
        ]
        , "owner" : "ludaflon"
        , "photo" : ""
        , "participantes_pendentes" : []
        , "participantes" : [
                              "mauricio",
                              "ludaflon",
                          ]
        , "comunidades" : []                   # comunidades em que esta comunidade está incluída
        , "upload_quota" : 20 * 1024 * 1024    # max 20 Mb
        , "upload_size" : 0
        , "papeis" : []
        , "admins" : []
        , "cod_institute" : "9999"
        , "institute" : u"Não informada"
        , "privacidade" : u"Pública"    # Pública ou Privada
        , "participacao" : "Mediante Convite"   # Mediante Convite, Voluntária ou Obrigatória  
   },
   "ComunidadeRoberta": {
        "name" : "ComunidadeRoberta"
        , "description" : "Comunidade de Roberta"
        , "tags" : [
            "rj",
            "computacao"
        ]
        , "owner" : "roberta"
        , "photo" : ""
        , "participantes_pendentes" : []
        , "participantes" : [
                              "roberta",
                              "julianne",
                          ]
        , "comunidades" : []                   # comunidades em que esta comunidade está incluída
        , "upload_quota" : 20 * 1024 * 1024    # max 20 Mb
        , "upload_size" : 0
        , "papeis" : []
        , "admins" : []
        , "cod_institute" : "9999"
        , "institute" : u"Não informada"
        , "privacidade" : u"Pública"    # Pública ou Privada
        , "participacao" : "Mediante Convite"   # Mediante Convite, Voluntária ou Obrigatória  
   },
   "ComunidadeLivia": {
        "name" : "ComunidadeLivia"
        , "description" : "Comunidade de Livia"
        , "tags" : [
            "python",
        ]
        , "owner" : "livia"
        , "photo" : ""
        , "participantes_pendentes" : []
        , "participantes" : [
                              "livia",
                          ]
        , "comunidades" : []                   # comunidades em que esta comunidade está incluída
        , "upload_quota" : 20 * 1024 * 1024    # max 20 Mb
        , "upload_size" : 0
        , "papeis" : []
        , "admins" : []
        , "cod_institute" : "9999"
        , "institute" : u"Não informada"
        , "privacidade" : u"Pública"    # Pública ou Privada
        , "participacao" : "Mediante Convite"   # Mediante Convite, Voluntária ou Obrigatória  
   },
   "NewCommunity": {
        "name" : "NewCommunity"
        , "description" : "Comunidade de newUser"
        , "tags" : [
            "activ",
        ]
        , "owner" : "newUser"
        , "photo" : ""
        , "participantes_pendentes" : []
        , "participantes" : [
                              "newUser",
                              "Angela"
                          ]
        , "comunidades" : []                   # comunidades em que esta comunidade está incluída
        , "upload_quota" : 20 * 1024 * 1024    # max 20 Mb
        , "upload_size" : 0
        , "papeis" : []
        , "admins" : []
        , "cod_institute" : "9999"
        , "institute" : u"Não informada"
        , "privacidade" : u"Pública"    # Pública ou Privada
        , "participacao" : "Mediante Convite"   # Mediante Convite, Voluntária ou Obrigatória  
   }
})

  # -------------------------------------------------------------
  # A estrutura acima pode ser resumida da seguinte forma:
  
         # ** ComunidadeMauricio, roberta e Angela possuem privacidade = Privada **
  
         #  mauricio:
         #	amigos      ->         julianne     |     tomasbomfim    | livia | marcinha
         #	convidados  ->            []
         #      pendentes   ->            []
         #      comunidades ->   ComunidadeMauricio | ComunidadeLuDaflon
         #      tags        ->         python       |        web         |  nce
         #      privacidade   ->       Pública
         #      sugestões:
         #                    Páginas:
         #                        ComunidadeRoberta/PagComuRoberta   (tag python)
         #                        marcinha/MinhaPag                  (tag nce)
         #                        ComunidadeMauricio/PagComuMauricio (tag web)
         #
         #                    Posts:
         #                       ComunidadeLuDaflon/postComuLuDaflon       (tag python)
         #                       newUser/postNewUser                       (tags python web)
         #                       ComunidadeLivia/postComuLivia             (tag nce)
         #                       ComunidadeMauricio/postComuMauricio       (tag nce)
         #
         #                    Pessoas:
         #                        ludaflon (tags python web nce)
         #
         #                    Comunidades:
         #                        ComunidadeLivia (tag python)
         #
         #  julianne:
         #	amigos        ->       mauricio       | livia | marcinha
         #      convidados    ->          []
         #      pendentes     ->          []
         #      comunidades   ->   ComunidadeRoberta
         #      tags          ->         ufrj
         #      privacidade   ->       Pública
         #      sugestões:
         #                     Páginas:
         #
         #                     Posts:
         #
         #                     Pessoas:
         #                          ludaflon (tag ufrj)
         #
         #                     Comunidades:
         #                          -
         #     
         #  tomasbomfim:
         #	amigos        ->       mauricio
         #      convidados    ->          []
         #      pendentes     ->          []         
         #      comunidades   ->    ComunidadeMauricio
         #      tags          ->          -
         #      privacidade   ->        Pública
         #      sugestões:
         #                     Páginas:
         #                             -
         #                     Posts:
         #                             -
         #                     Pessoas:
         #                             -
         #                     Comunidades:
         #                             -
         #
         #  livia:
         #	amigos        ->       mauricio    |       julianne      |    Angela   |  marcinha    |  roberta  |  ludaflon
         #      convidados    ->          []
         #      pendentes     ->          []
         #      comunidades   ->   ComunidadeLivia |  ComunidadeMauricio
         #      tags          ->        python     |         web         |    mestrado
         #      privacidade   ->       Pública
         #      sugestões:
         #                     Páginas:
         #                          mauricio/MinhPag21                     (tag python)
         #                          ComunidadeRoberta/PagComuRoberta       (tag python)
         #                          Angela/MinhaPag                        (tag python)
         #                          ComunidadeMauricio/PagComuMauricio     (tag web)    
         #
         #                     Posts:
         #                          ComunidadeLuDaflon/postComuLuDaflon       (tag python)
         #                          newUser/postNewUser                       (tags python web)
         #                          Angela/postAngela21                       (tag python)
         #                          ComunidadeMauricio/postComuMauricio       (tag python)
         #
         #                     Pessoas:
         #                          -
         #
         #                     Comunidades:
         #                          ComunidadeLuDaflon (tag mestrado)         
         #
         #  marcinha:
         #	amigos        ->     mauricio | julianne | livia
         #      convidados    ->       []         
         #	pendentes     ->     newUser
         #      comunidades   ->       []
         #      tags          ->       nce
         #      privacidade   ->     Pública
         #      sugestões:
         #                     Páginas:
         #                          -
         #
         #                     Posts:
         #                          ComunidadeLivia/postComuLivia (tag nce)
         #
         #                     Pessoas:
         #                          ludaflon (tag nce)
         #
         #                     Comunidades:
         #                          ComunidadeLuDaflon (tag nce)
         #
         #  roberta:
         #	amigos        ->          livia
         #      convidados    ->           []
         #	pendentes     ->        mauricio
         #      comunidades   ->    ComunidadeRoberta
         #      tags          ->           rj
         #      privacidade   ->         Privada
         #      sugestões:
         #                     Páginas:
         #                          
         #
         #                     Posts:
         #
         #
         #                     Pessoas:
         #                          ludaflon (tag rj)
         #
         #                     Comunidades:
         #                          - 
         #
         #  Angela:
         #	amigos        ->      livia
         #	convidados    ->     ludaflon
         #	pendentes     ->     mauricio
         #      comunidades   ->  ComunidadeAngela |  NewCommunity
         #      tags          ->      python
         #      privacidade   ->     Privada
         #      sugestões:
         #                     Páginas:
         #                         mauricio/MinhaPag21               (tag python)
         #                         ComunidadeRoberta/PagComuRoberta  (tag python)
         #
         #                     Posts:
         #                         ComunidadeLuDaflon/postComuLuDaflon  (tag python)
         #                         newUser/postNewUser                  (tags python web)
         #
         #                     Pessoas:
         #                          -
         #
         #                     Comunidades:
         #                          ComunidadeLivia   (tag python)
         #
         #  newUser:
         #	amigos        ->      []
         #	convidados    ->      []
         #      pendentes     ->      []
         #      comunidades   ->  NewCommunity
         #      tags          ->     activ
         #      privacidade   ->    Pública
         #      sugestões:
         #                     Páginas:
         #                          
         #
         #                     Posts:
         #
         #
         #                     Pessoas:
         #                          ludaflon (tag activ)
         #
         #                     Comunidades:
         #                          ComundadeLudDaflon (tag activ)
         #
         #  ludaflon:
         #	amigos        ->       livia
         #	convidados    ->      marcinha
         #	pendentes     ->       newUser
         #      comunidades   ->  ComunidadeLuDaflon
         #      tags          ->       python        |   web   | nce | mestrado | rj | activ | ufrj | computação
         #      privacidade   ->       Pública
         #      sugestões:
         #                     Páginas:
         #                          mauricio/MinhaPag21                 (tag python)
         #                          ComunidadeRoberta/PagComuRoberta    (tag python)
         #                          marcinha/MinhaPag                   (tag nce)
         #
         #                     Posts:
         #                          ComunidadeLuDaflon/postComuLuDaflon    (tag python)
         #                          newUser/postNewUser                    (tags python web)
         #                          ComunidadeLivia/postComuLivia          (tag nce)
         #
         #                     Pessoas:
         #                          mauricio (tags python web nce)
         #                          julianne (tag ufrj)
         #
         #                     Comunidades:
         #			     ComunidadeRoberta(tags rj computacao)
         #			     NewCommunity(tag activ)
         #			     ComunidadeLivia (tag python)

class TestComunidade(unittest.TestCase):
  """Testes unitários para o gerenciamento de comunidades"""
  def setUp(self):
    
    core.model.REGISTRY = REGISTRY_DEFAULT()
    core.model.MAGKEYS = MAGKEYS_DEFAULT()
    core.model.INVITES = {}
    core.model.USERSCHOOL = {}
    search.model.SEARCHTAGS = SEARCHTAGS_DEFAULT()
    log.model.NOTIFICATIONERROR = {}
    log.model.NOTIFICATION = {}
    
    self.app = TestApp(WsgiApp())
    registry.update(REGISTRY_FORM)

    # Cria usuários para os testes
    #registry['user'] = 'teste'
    self.app.post('/new/user', registry)
    core.model.REGISTRY['teste']['cod_institute'] = u"0002"
     
    # Faz login como usuário teste
    login.update(LOGIN_FORM)
    self.app.post('/login', login)
    core.model.REGISTRY['teste']['papeis'].append('professor')

    core.model.MAGKEYS = MAGKEYS_DEFAULT()    # recria chave mágica para que possa fazer outro cadastro
    
    
  def tearDown(self):
    #self.mock.restore()
    #self.mock.verify()
    #self.mock,MEMBER =None,None
    pass


  # -------------------------------------------------------------
  # Acesso a tela de Sugestões de Amigos

  def test_no_sugest_content(self):
    "Exibe mensagem de que o usuário não possui sugestões de conteúdos por ainda não ter nenhum amigo e/ou comunidades."
    response = self.app.get('/sugestcontent/teste')
    assert u'<p>Ainda não é possível sugerir conteúdo para teste.</p>' in response, "Erro: Sugeriu conteúdo para um usuário que não possui amigos nem comunidades!"
    
  def test_reject_sugest_content(self):
    "Exibe mensagem de erro quando um usuário tenta visualizar as sugestões de conteúdo de outro usuário."
    core.model.REGISTRY["teste"] = core.model.REGISTRY["mauricio"]
    response = self.app.get('/sugestcontent/mauricio')
    assert u'<div class="tnmMSG">Erro: Você não tem permissão de visualizar as sugestões de conteúdo de mauricio.</div> ' in response, "Erro: Exibiu Sugestão de Conteúdo de um usuário para outro usuário!"
    
  def test_sugest_content_mauricio(self):
    "Exibe tela de Sugestão de conteúdo do usuário teste se baseando no registry do usuário mauricio."
    core.model.REGISTRY["teste"] = core.model.REGISTRY["mauricio"]
    response = self.app.get('/sugestcontent/teste')
    assert u'mauricio' in response, "Erro: Não sugeriu o usuário mauricio!"
    assert u'julianne' not in response, "Erro: Sugeriu o usuário julianne!"
    assert u'tomasbomfim' not in response, "Erro: Sugeriu o usuário tomasbomfim!"
    assert u'livia' not in response, "Erro: Sugeriu o usuário livia!"
    #assert u'marcinha'  not in response, "Erro: Sugeriu o usuário marcinha!"
    assert u'roberta' not in response, "Erro: Sugeriu o usuário roberta!"
    #assert u'Angela' not in response, "Erro: Sugeriu o usuário Angela!"
    #assert u'newUser' not in response, "Erro: Sugeriu o usuário newUser!"
    assert u'ludaflon' in response, "Erro: Não sugeriu o usuário ludaflon!"
    #assert u'ComunidadeMauricio' not in response, "Erro: Sugeriu a comunidade ComunidadeMauricio!"
    #assert u'ComunidadeLuDaflon' not in response, "Erro: Sugeriu a comunidade ComunidadeLuDaflon!"
    #assert u'ComunidadeRoberta' not in response, "Erro: Sugeriu a comunidade ComunidadeRoberta!"
    assert u'PagComuRoberta' in response, "Erro: Não sugeriu a página PagComuRoberta da comunidade ComunidadeRoberta!"
    assert u'ComunidadeLivia' in response, "Erro: Não sugeriu a comunidade ComunidadeLivia!"
    assert u'NewCommunity' not in response, "Erro: Sugeriu a comunidade NewCommunity!"
    assert u'MinhaPag21 de mauricio' in response, "Erro: Sugeriu a página MinhaPag21 do usuário mauricio!"
    assert u'MinhaPag1 de mauricio' not in response, "Erro: Sugeriu a página MinhaPag1 do usuário mauricio!"
    assert u'MinhaPag de marcinha' not in response, "Erro: Sugeriu a página MinhaPag do usuário marcinha!"
    assert u'MinhaPag de Angela' not in response, "Erro: Sugeriu a página MinhaPag do usuário Angela!"
    assert u'postComuLivia do Blog de ComunidadeLivia' in response, "Erro: Não sugeriu o post postComuLivia da comunidade ComunidadeLivia!"
    assert u'PagComuRoberta de ComunidadeRoberta' in response, "Erro: Não sugeriu a página PagComuRoberta da comunidade ComunidadeRoberta!"
    assert u'pagComuMauricio de ComunidadeMauricio' in response, "Erro: Não sugeriu a página PagComuMauricio da comunidade ComunidadeMauricio!"
    assert u'postComuMauricio do Blog de ComunidadeMauricio' in response, "Erro: Não sugeriu o post PostComuMauricio da comunidade ComunidadeMauricio!"
    assert u'postComuLuDaflon do Blog de ComunidadeLuDaflon' in response, "Erro: Não sugeriu o post PostComuLuDaflon da comunidade ComunidadeRoberta!"
    assert u'postNewUser do Blog de newUser' in response, "Erro: Não sugeriu o post postNewUser do usuário newUser!"
    assert u'postAngela21 do Blog de Angela' not in response, "Erro: Sugeriu o post postAngela21 do usuário Angela!"
    
  def test_sugest_content_julianne(self):
    "Exibe tela de Sugestão de conteúdo do usuário teste se baseando no registry do usuário julianne."
    core.model.REGISTRY["teste"] = core.model.REGISTRY["julianne"]
    response = self.app.get('/sugestcontent/teste')
    assert u'mauricio' not in response, "Erro: Sugeriu o usuário mauricio!"
    assert u'julianne' in response, "Erro: Não sugeriu o usuário julianne!"
    assert u'tomasbomfim' not in response, "Erro: Sugeriu o usuário tomasbomfim!"
    assert u'livia' not in response, "Erro: Sugeriu o usuário livia!"
    assert u'marcinha'  not in response, "Erro: Sugeriu o usuário marcinha!"
    assert u'roberta' not in response, "Erro: Sugeriu o usuário roberta!"
    assert u'Angela' not in response, "Erro: Sugeriu o usuário Angela!"
    assert u'newUser' not in response, "Erro: Sugeriu o usuário newUser!"
    assert u'ludaflon' in response, "Erro: Não sugeriu o usuário ludaflon!"
    assert u'ComunidadeMauricio' not in response, "Erro: Sugeriu a comunidade ComunidadeMauricio!"
    assert u'ComunidadeLuDaflon' not in response, "Erro: Sugeriu a comunidade ComunidadeLuDaflon!"
    assert u'ComunidadeRoberta' not in response, "Erro: Sugeriu a comunidade ComunidadeRoberta!"
    assert u'ComunidadeLivia' not in response, "Erro: Sugeriu a comunidade ComunidadeLivia!"
    assert u'NewCommunity' not in response, "Erro: Sugeriu a comunidade NewCommunity!"
    assert u'MinhaPag21 de mauricio' not in response, "Erro: Não sugeriu a página MinhaPag21 do usuário mauricio!"
    assert u'MinhaPag de marcinha' not in response, "Erro: Não sugeriu a página MinhaPag do usuário marcinha!"
    assert u'MinhaPag de Angela' not in response, "Erro: Sugeriu a página MinhaPag do usuário Angela!"
    assert u'pagComuMauricio de ComunidadeMauricio' not in response, "Erro: Sugeriu a página PagComuMauricio da comunidade ComunidadeMauricio!"
    assert u'postComuMauricio do Blog de ComunidadeMauricio' not in response, "Erro: Sugeriu o post PostComuMauricio da comunidade ComunidadeMauricio!"
    assert u'postComuLivia do Blog de ComunidadeLivia' not in response, "Erro: Não sugeriu o post postComuLivia da comunidade ComunidadeLivia!"
    assert u'PagComuRoberta de ComunidadeRoberta' not in response, "Erro: Não sugeriu a página PagComuRoberta da comunidade ComunidadeRoberta!"
    assert u'postComuLuDaflon do Blog de ComunidadeLuDaflon'  not in response, "Erro: Não sugeriu o post PostComuLuDaflon da comunidade ComunidadeRoberta!"
    assert u'postNewUser do Blog de newUser' not in response, "Erro: Não sugeriu o post postNewUser do usuário newUser!"
    assert u'postAngela21 do Blog de Angela' not in response, "Erro: Sugeriu o post postAngela21 do usuário Angela!"
    
  def test_accept_sugest_content(self):
    "Exibe tela de confirmação de envio de convite para um dos amigos sugeridos."
    core.model.REGISTRY["teste"] = core.model.REGISTRY["ludaflon"]
    core.model.REGISTRY["teste"]["amigos"].append("mauricio")
    core.model.REGISTRY["teste"]["comunidades"].append("ComunidadeRoberta")
    response = self.app.get('/sugestcontent/teste')
    assert u'<a href="/profile/mauricio"> mauricio ' not in response, "Erro: Usuário já convidado foi sugerido!"
    assert u'<a href="/profile/ComunidadeRoberta"> ComunidadeRoberta ' not in response, "Erro: Comunidade da qual o usuário já faz parte foi sugerida!"

  def test_sugest_content_tomas(self):
    "Exibe tela de Sugestão de conteúdo do usuário teste se baseando nos amigos do usuário tomasbomfim que por não possuir tags também não possui sugestões de conteúdo."
    core.model.REGISTRY["teste"] = core.model.REGISTRY["tomasbomfim"]
    response = self.app.get('/sugestcontent/teste')
    assert u'<p>Ainda não é possível sugerir conteúdo para teste.</p>' in response, "Erro: Não sugeriu o usuário tomasbomfim!"
    
  def test_sugest_content_livia(self):
    "Exibe tela de Sugestão de conteúdo do usuário teste se baseando no registry do usuário livia."
    core.model.REGISTRY["teste"] = core.model.REGISTRY["livia"]
    response = self.app.get('/sugestcontent/teste')
    #assert u'mauricio' not in response, "Erro: Sugeriu o usuário mauricio!"
    assert u'MinhaPag' in response, "Erro: Não sugeriu a página MinhaPag do usuário mauricio!"
    assert u'julianne' not in response, "Erro: Sugeriu o usuário julianne!"
    assert u'tomasbomfim' not in response, "Erro: Sugeriu o usuário tomasbomfim!"
    assert u'livia' in response, "Erro: Não sugeriu o usuário livia!"
    assert u'marcinha'  not in response, "Erro: Sugeriu o usuário marcinha!"
    assert u'roberta' not in response, "Erro: Sugeriu o usuário roberta!"
    #assert u'Angela' not in response, "Erro: Sugeriu o usuário Angela!"
    #assert u'newUser' not in response, "Erro: Sugeriu o usuário newUser!"
    assert u'ludaflon' not in response, "Erro: Sugeriu o usuário ludaflon!"
    #assert u'ComunidadeMauricio' not in response, "Erro: Sugeriu a comunidade ComunidadeMauricio!"
    assert u'ComunidadeLuDaflon' in response, "Erro: Não sugeriu a comunidade ComunidadeLuDaflon!"
    #assert u'ComunidadeRoberta' not in response, "Erro: Sugeriu a comunidade ComunidadeRoberta!"
    assert u'PagComuRoberta' in response, "Erro: Não sugeriu a página PagComuRoberta da comunidade ComunidadeRoberta!"
    assert u'ComunidadeLivia' not in response, "Erro: Sugeriu a comunidade ComunidadeLivia!"
    assert u'NewCommunity' not in response, "Erro: Sugeriu a comunidade NewCommunity!"
    assert u'MinhaPag21 de mauricio' in response, "Erro: Não sugeriu a página MinhaPag21 do usuário mauricio!"
    assert u'MinhaPag1 de mauricio' not in response, "Erro: Sugeriu a página MinhaPag1 do usuário mauricio!"
    assert u'MinhaPag de marcinha' not in response, "Erro: Sugeriu a página MinhaPag do usuário marcinha!"
    assert u'MinhaPag de Angela' in response, "Erro: Não sugeriu a página MinhaPag do usuário Angela!"
    assert u'pagComuMauricio de ComunidadeMauricio' in response, "Erro: Não sugeriu a página PagComuMauricio da comunidade ComunidadeMauricio!"
    assert u'postComuMauricio do Blog de ComunidadeMauricio' in response, "Erro: Não sugeriu o post PostComuMauricio da comunidade ComunidadeMauricio!"
    assert u'postComuLivia do Blog de ComunidadeLivia' not in response, "Erro: Sugeriu o post postComuLivia da comunidade ComunidadeLivia!"
    assert u'PagComuRoberta de ComunidadeRoberta' in response, "Erro: Não sugeriu a página PagComuRoberta da comunidade ComunidadeRoberta!"
    #assert u'postComuLuDaflon do Blog de ComunidadeLuDaflon'  in response, "Erro: Não sugeriu o post PostComuLuDaflon da comunidade ComunidadeLuDaflon!"
    #assert u'postNewUser do Blog de newUser' in response, "Erro: Não sugeriu o post postNewUser do usuário newUser!"
    assert u'postAngela21 do Blog de Angela' in response, "Erro: Não sugeriu o post postAngela21 do usuário Angela!"
    assert u'postAngela1 do Blog de Angela' not in response, "Erro: Sugeriu o post postAngela1 do usuário Angela!"
    
  def test_sugest_content_marcinha(self):
    "Exibe tela de Sugestão de conteúdo do usuário teste se baseando no registry do usuário marcinha."
    core.model.REGISTRY["teste"] = core.model.REGISTRY["marcinha"]
    response = self.app.get('/sugestcontent/teste')
    assert u'mauricio' not in response, "Erro: Sugeriu o usuário mauricio!"
    assert u'julianne' not in response, "Erro: Sugeriu o usuário julianne!"
    assert u'tomasbomfim' not in response, "Erro: Sugeriu o usuário tomasbomfim!"
    assert u'livia' not in response, "Erro: Sugeriu o usuário livia!"
    assert u'marcinha' in response, "Erro: Não sugeriu o usuário marcinha!"
    assert u'roberta' not in response, "Erro: Sugeriu o usuário roberta!"
    assert u'Angela' not in response, "Erro: Sugeriu o usuário Angela!"
    assert u'newUser' not in response, "Erro: Sugeriu o usuário newUser!"
    assert u'ludaflon' in response, "Erro: Não sugeriu o usuário ludaflon!"
    assert u'ComunidadeMauricio' not in response, "Erro: Sugeriu a comunidade ComunidadeMauricio!"
    assert u'ComunidadeLuDaflon' in response, "Erro: Não sugeriu a comunidade ComunidadeLuDaflon!"
    assert u'ComunidadeRoberta' not in response, "Erro: Sugeriu a comunidade ComunidadeRoberta!"
    #assert u'ComunidadeLivia' not in response, "Erro: Sugeriu a comunidade ComunidadeLivia!"
    assert u'NewCommunity' not in response, "Erro: Sugeriu a comunidade NewCommunity!"
    assert u'MinhaPag21 de mauricio' not in response, "Erro: Sugeriu a página MinhaPag21 do usuário mauricio!"
    assert u'MinhaPag de marcinha' in response, "Erro: Não sugeriu a página MinhaPag do usuário marcinha!"
    assert u'MinhaPag de Angela' not in response, "Erro: Sugeriu a página MinhaPag do usuário Angela!"
    assert u'pagComuMauricio de ComunidadeMauricio' not in response, "Erro: Sugeriu a página PagComuMauricio da comunidade ComunidadeMauricio!"
    assert u'postComuMauricio do Blog de ComunidadeMauricio' not in response, "Erro: Sugeriu o post PostComuMauricio da comunidade ComunidadeMauricio!"
    assert u'postComuLivia do Blog de ComunidadeLivia' in response, "Erro: Não sugeriu o post postComuLivia da comunidade ComunidadeLivia!"
    assert u'PagComuRoberta de ComunidadeRoberta' not in response, "Erro: Sugeriu a página PagComuRoberta da comunidade ComunidadeRoberta!"
    assert u'postComuLuDaflon do Blog de ComunidadeLuDaflon' not in response, "Erro: Sugeriu o post PostComuLuDaflon da comunidade ComunidadeRoberta!"
    assert u'postNewUser do Blog de newUser' not in response, "Erro: Sugeriu o post postNewUser do usuário newUser!"
    assert u'postAngela21 do Blog de Angela' not in response, "Erro: Sugeriu o post postAngela do usuário Angela!"
    
  def test_sugest_content_roberta(self):
    "Exibe tela de Sugestão de conteúdo do usuário teste se baseando no registry do usuário roberta."
    core.model.REGISTRY["teste"] = core.model.REGISTRY["roberta"]
    response = self.app.get('/sugestcontent/teste')
    assert u'mauricio' not in response, "Erro: Sugeriu o usuário mauricio!"
    assert u'julianne' not in response, "Erro: Sugeriu o usuário julianne!"
    assert u'tomasbomfim' not in response, "Erro: Sugeriu o usuário tomasbomfim!"
    assert u'livia' not in response, "Erro: Sugeriu o usuário livia!"
    assert u'marcinha' not in response, "Erro: Sugeriu o usuário marcinha!"
    assert u'roberta' in response, "Erro: Não sugeriu o usuário roberta!"
    assert u'Angela' not in response, "Erro: Sugeriu o usuário Angela!"
    assert u'newUser' not in response, "Erro: Sugeriu o usuário newUser!"
    assert u'ludaflon' in response, "Erro: Não sugeriu o usuário ludaflon!"
    assert u'ComunidadeMauricio' not in response, "Erro: Sugeriu a comunidade ComunidadeMauricio!"
    assert u'ComunidadeLuDaflon' not in response, "Erro: Sugeriu a comunidade ComunidadeLuDaflon!"
    assert u'ComunidadeRoberta' not in response, "Erro: Sugeriu a comunidade ComunidadeRoberta!"
    assert u'ComunidadeLivia' not in response, "Erro: Sugeriu a comunidade ComunidadeLivia!"
    assert u'NewCommunity' not in response, "Erro: Sugeriu a comunidade NewCommunity!"
    assert u'MinhaPag21 de mauricio' not in response, "Erro: Sugeriu a página MinhaPag21 do usuário mauricio!"
    assert u'MinhaPag de marcinha' not in response, "Erro: Sugeriu a página MinhaPag do usuário marcinha!"
    assert u'MinhaPag de Angela' not in response, "Erro: Sugeriu a página MinhaPag do usuário Angela!"
    assert u'pagComuMauricio de ComunidadeMauricio' not in response, "Erro: Sugeriu a página PagComuMauricio da comunidade ComunidadeMauricio!"
    assert u'postComuMauricio do Blog de ComunidadeMauricio' not in response, "Erro: Sugeriu o post PostComuMauricio da comunidade ComunidadeMauricio!"
    assert u'postComuLivia do Blog de ComunidadeLivia' not in response, "Erro: Sugeriu o post postComuLivia da comunidade ComunidadeLivia!"
    assert u'PagComuRoberta de ComunidadeRoberta' not in response, "Erro: Sugeriu a página PagComuRoberta da comunidade ComunidadeRoberta!"
    assert u'postComuLuDaflon do Blog de ComunidadeLuDaflon' not in response, "Erro: Sugeriu o post PostComuLuDaflon da comunidade ComunidadeRoberta!"
    assert u'postNewUser do Blog de newUser' not in response, "Erro: Sugeriu o post postNewUser do usuário newUser!"
    assert u'postAngela21 do Blog de Angela' not in response, "Erro: Sugeriu o post postAngela do usuário Angela!"
    
  def test_sugest_content_Angela(self):
    "Exibe tela de Sugestão de conteúdo do usuário teste se baseando no registry do usuário Angela."
    core.model.REGISTRY["teste"] = core.model.REGISTRY["Angela"]
    response = self.app.get('/sugestcontent/teste')
    #assert u'mauricio' not in response, "Erro: Sugeriu o usuário mauricio!"
    assert u'julianne' not in response, "Erro: Sugeriu o usuário julianne!"
    assert u'tomasbomfim' not in response, "Erro: Sugeriu o usuário tomasbomfim!"
    assert u'livia' not in response, "Erro: Sugeriu o usuário livia!"
    assert u'marcinha' not in response, "Erro: Sugeriu o usuário marcinha!"
    assert u'roberta' not in response, "Erro: Sugeriu o usuário roberta!"
    #assert u'newUser' not in response, "Erro: Sugeriu o usuário newUser!"
    assert u'ludaflon' not in response, "Erro: Sugeriu o usuário ludaflon!"
    assert u'ComunidadeMauricio' not in response, "Erro: Não sugeriu a comunidade ComunidadeMauricio!"
    #assert u'ComunidadeLuDaflon' not in response, "Erro: Sugeriu a comunidade ComunidadeLuDaflon!"
    #assert u'ComunidadeRoberta' not in response, "Erro: Sugeriu a comunidade ComunidadeRoberta!"
    assert u'PagComuRoberta' in response, "Erro: Não sugeriu a página PagComuRoberta da comunidade ComunidadeRoberta!"
    assert u'ComunidadeLivia' in response, "Erro: Não sugeriu a comunidade ComunidadeLivia!"
    assert u'NewCommunity' not in response, "Erro: Sugeriu a comunidade NewCommunity!"
    assert u'MinhaPag21 de mauricio' in response, "Erro: Não sugeriu a página MinhaPag21 do usuário mauricio!"
    assert u'MinhaPag1 de mauricio' not in response, "Erro: Sugeriu a página MinhaPag1 do usuário mauricio!"
    assert u'MinhaPag de marcinha' not in response, "Erro: Sugeriu a página MinhaPag do usuário marcinha!"
    assert u'MinhaPag de Angela' not in response, "Erro: Sugeriu a página MinhaPag do usuário Angela!"
    assert u'pagComuMauricio de ComunidadeMauricio' not in response, "Erro: Sugeriu a página PagComuMauricio da comunidade ComunidadeMauricio!"
    assert u'postComuMauricio do Blog de ComunidadeMauricio' not in response, "Erro: Sugeriu o post PostComuMauricio da comunidade ComunidadeMauricio!"
    assert u'postComuLivia do Blog de ComunidadeLivia' not in response, "Erro: Sugeriu o post postComuLivia da comunidade ComunidadeLivia!"
    assert u'PagComuRoberta de ComunidadeRoberta' in response, "Erro: Não sugeriu a página PagComuRoberta da comunidade ComunidadeRoberta!"
    assert u'postComuLuDaflon do Blog de ComunidadeLuDaflon' in response, "Erro: Não sugeriu o post PostComuLuDaflon da comunidade ComunidadeRoberta!"
    assert u'postNewUser do Blog de newUser' in response, "Erro: Não sugeriu o post postNewUser do usuário newUser!"
    assert u'postAngela21 do Blog de Angela' not in response, "Erro: Sugeriu o post postAngela do usuário Angela!"
    
  def test_sugest_content_newUser(self):
    "Exibe tela de Sugestão de conteúdo do usuário teste se baseando no registry do usuário newUser."
    core.model.REGISTRY["teste"] = core.model.REGISTRY["newUser"]
    response = self.app.get('/sugestcontent/teste')
    assert u'mauricio' not in response, "Erro: Sugeriu o usuário mauricio!"
    assert u'julianne' not in response, "Erro: Sugeriu o usuário julianne!"
    assert u'tomasbomfim' not in response, "Erro: Sugeriu o usuário tomasbomfim!"
    assert u'livia' not in response, "Erro: Sugeriu o usuário livia!"
    assert u'marcinha' not in response, "Erro: Sugeriu o usuário marcinha!"
    assert u'roberta' not in response, "Erro: Sugeriu o usuário roberta!"
    assert u'Angela' not in response, "Erro: Sugeriu o usuário Angela!"
    assert u'newUser' in response, "Erro: Não sugeriu o usuário newUser!"
    assert u'ludaflon' in response, "Erro: Não sugeriu o usuário ludaflon!"
    assert u'ComunidadeMauricio' not in response, "Erro: Sugeriu a comunidade ComunidadeMauricio!"
    assert u'ComunidadeLuDaflon' in response, "Erro: Não sugeriu a comunidade ComunidadeLuDaflon!"
    assert u'ComunidadeRoberta' not in response, "Erro: Sugeriu a comunidade ComunidadeRoberta!"
    assert u'ComunidadeLivia' not in response, "Erro: Sugeriu a comunidade ComunidadeLivia!"
    assert u'NewCommunity' not in response, "Erro: Sugeriu a comunidade NewCommunity!"
    assert u'MinhaPag21 de mauricio' not in response, "Erro: Sugeriu a página MinhaPag21 do usuário mauricio!"
    assert u'MinhaPag de marcinha' not in response, "Erro: Sugeriu a página MinhaPag do usuário marcinha!"
    assert u'MinhaPag de Angela' not in response, "Erro: Sugeriu a página MinhaPag do usuário Angela!"
    assert u'pagComuMauricio de ComunidadeMauricio' not in response, "Erro: Sugeriu a página PagComuMauricio da comunidade ComunidadeMauricio!"
    assert u'postComuMauricio do Blog de ComunidadeMauricio' not in response, "Erro: Sugeriu o post PostComuMauricio da comunidade ComunidadeMauricio!"
    assert u'postComuLivia do Blog de ComunidadeLivia' not in response, "Erro: Sugeriu o post postComuLivia da comunidade ComunidadeLivia!"
    assert u'PagComuRoberta de ComunidadeRoberta' not in response, "Erro: Sugeriu a página PagComuRoberta da comunidade ComunidadeRoberta!"
    assert u'postComuLuDaflon do Blog de ComunidadeLuDaflon' not in response, "Erro: Sugeriu o post PostComuLuDaflon da comunidade ComunidadeRoberta!"
    assert u'postNewUser do Blog de newUser' not in response, "Erro: Sugeriu o post postNewUser do usuário newUser!"
    assert u'postAngela21 do Blog de Angela' not in response, "Erro: Sugeriu o post postAngela do usuário Angela!"
    
  def test_sugest_content_ludaflon(self):
    "Exibe tela de Sugestão de conteúdo do usuário teste se baseando no registry do usuário ludaflon."
    core.model.REGISTRY["teste"] = core.model.REGISTRY["ludaflon"]
    response = self.app.get('/sugestcontent/teste')
    assert u'mauricio' in response, "Erro: Não sugeriu o usuário mauricio!"
    assert u'julianne' in response, "Erro: Não sugeriu o usuário julianne!"
    assert u'tomasbomfim' not in response, "Erro: Sugeriu o usuário tomasbomfim!"
    assert u'livia' not in response, "Erro: Sugeriu o usuário livia!"
    #assert u'marcinha' not in response, "Erro: Sugeriu o usuário marcinha!"
    #assert u'Angela' not in response, "Erro: Sugeriu o usuário Angela!"
    #assert u'newUser' not in response, "Erro: Sugeriu o usuário newUser!"
    assert u'ludaflon' in response, "Erro: Não sugeriu o usuário ludaflon!"
    assert u'ComunidadeMauricio' not in response, "Erro: Sugeriu a comunidade ComunidadeMauricio!"
    #assert u'ComunidadeLuDaflon' not in response, "Erro: Sugeriu a comunidade ComunidadeLuDaflon!"
    assert u'ComunidadeRoberta' in response, "Erro: Não sugeriu a comunidade ComunidadeRoberta!"
    assert u'ComunidadeLivia' in response, "Erro: Não sugeriu a comunidade ComunidadeLivia!"
    assert u'NewCommunity' in response, "Erro: Não sugeriu a comunidade NewCommunity!"
    assert u'MinhaPag21 de mauricio' in response, "Erro: Não sugeriu a página MinhaPag21 do usuário mauricio!"
    assert u'MinhaPag1 de mauricio' not in response, "Erro: Sugeriu a página MinhaPag1 do usuário mauricio!"
    assert u'MinhaPag de marcinha' not in response, "Erro: Sugeriu a página MinhaPag do usuário marcinha!"
    assert u'MinhaPag de Angela' not in response, "Erro: Sugeriu a página MinhaPag do usuário Angela!"
    assert u'pagComuMauricio de ComunidadeMauricio' not in response, "Erro: Sugeriu a página PagComuMauricio da comunidade ComunidadeMauricio!"
    assert u'postComuMauricio do Blog de ComunidadeMauricio' not in response, "Erro: Sugeriu o post PostComuMauricio da comunidade ComunidadeMauricio!"
    assert u'postComuLivia do Blog de ComunidadeLivia' in response, "Erro: Não sugeriu o post postComuLivia da comunidade ComunidadeLivia!"
    assert u'PagComuRoberta de ComunidadeRoberta' in response, "Erro: Não sugeriu a página PagComuRoberta da comunidade ComunidadeRoberta!"
    assert u'postComuLuDaflon do Blog de ComunidadeLuDaflon' in response, "Erro: Não sugeriu o post PostComuLuDaflon da comunidade ComunidadeRoberta!"
    assert u'postNewUser do Blog de newUser' in response, "Erro: Não sugeriu o post postNewUser do usuário newUser!"
    assert u'postAngela21 do Blog de Angela' not in response, "Erro: Sugeriu o post postAngela21 do usuário Angela!"