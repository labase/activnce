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

from config import TUTORIAL

TUTORIAL["chat"] = {
         "menu": u"Utilizando o Chat",
         "descricao": u"O <b>chat</b> é uma ferramenta de comunicação privada e instantânea onde duas pessoas que estão online podem conversar entre si.<br><i>Para mensagens privadas e offline escolha a ferramenta <b>Recados</b> e para mensagens offline e públicas ecolha a ferramenta <b>Microblog</b>.</i>",
         "tutoriais": [
               {
               "titulo": u"Tutorial 1: Como utilizar o Chat com amigos",
               "telas": [
                          {"titulo": u"1.1 - Escolhendo um amigo para uma conversa",
                           "subtitulo": u"Página 1 de 4",
                           "texto": u"Para iniciar um chat com um amigo, vá em seu perfil e clique em <b>Amigos</b>. Lá aparecerá uma lista com todos os seus amigos e clicando no ícone <img src = '/static/imagens/icones/talk24.png' style = 'width: 16px;'/> (iniciar chat com 'NomeDoAmigo'), você pode iniciar um chat com ele."
        
                           },
                         
                          {"titulo": u"1.2 - Enviando uma mensagem",
                           "subtitulo": u"Página 2 de 4",
                           "texto": u"Para enviar uma mensagem pelo chat, basta escrever sua mensagem na caixa de texto e clicar em <b>Enviar</b>. Seu amigo irá receber uma notificação de que você enviou uma mensagem."
                           },
                         
                          {"titulo": u"1.3 - Recebendo uma mensagem",
                           "subtitulo": u"Página 3 de 4",
                           "texto": u"Quando um amigo mandar uma mensagem para você, você irar receber uma notificação em sua tela como esta: <img src = '/static/imagens/icones/talk24.png' style = 'widith: 16px;'><b>'SeuAmigo' está chamando</b>. Clique na notificação para abrir o chat."
                           },
                         
                           {"titulo": u"1.4 - Vendo o histórico de mensagens",
                           "subtitulo": u"Página 4 de 4",
                           "texto": u"Para ver o histórico de todas as mensagens enviadas e recebidas, vá até sua página inicial e no menu principal em comunicação, escolha a opção chat. Irá aparecer uma lista dos amigos que você já conversou pelo chat e clicando em um deles você poderá ver todas as mensagens enviadas e recebidas."
                           },
                        ]
                    },
                         
                {
                "titulo": u"Tutorial 2: Como utilizar o Chat com comunidades",
                "telas": [
                          {"titulo": u"1.1 - Iniciando uma conversa com uma comunidade",
                           "subtitulo": u"Página 1 de 2",
                           "texto": u"Para iniciar um chat com uma comunidade, vá até a página da comunidade e no menu principal em comunicação escolha a opção chat. Quando você entrar, aparecerá uma mensagem de que você entrou no chat. E você já pode conversar com os membros da comunidade que também estão no chat."
                           },
                          
                          {"titulo": u"1.2 - Descobrindo se alguém está online",
                           "subtitulo": u"Página 2 de 2",
                           "texto": u"Para saber se algum membro da comunidade está no chat, basata entrar na página da comunidade e se alguém estiver lá, aparecerá uma tela na qual estará os nomes dos membros online. Caso não tenha ninguém, a tela não irá aparecer."
                           },               
                        ]
                }                       
        ]
      }