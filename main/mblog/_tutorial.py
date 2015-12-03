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

TUTORIAL["mblog"] = {
         "menu": u"Utilizando o Microblog",
         "descricao": u"O <b>Microblog</b> é uma ferramenta de comunicação que permite ao usuário postar mensagens de até 350 caracteres para seus amigos ou comunidades.<br><i>As mensagens postadas no <b>Microblog</b> são públicas, para mensagens privadas utilize <b>Recados</b> ou <b>Chat</b>.</i>",
         "tutoriais": [
               {
               "titulo": u"Tutorial 1: Como utilizar o Microblog",
               "telas": [                         
                          {"titulo": u"1.1 - Escrevendo uma mensagem para seus amigos",
                           "subtitulo": u"Página 1 de 8",
                           "texto": u"Para começar a enviar mensagens, basta seguir os passos abaixo:<ul><li>No menu principal, vá em <b>Comunicação</b> e selecione a opção <b>Microblog</b>.</li><li>Agora, digite sua mensagem na caixa de texto e clique em enviar</li></ul>Pronto! Seus amigos poderão ver que você postou uma mensagem no microblog em <b>Novidades</b> no perfil."

                           },
                         
                          {"titulo": u"1.2 - Tenha certeza de que uma ou mais pessoas no Activ vão ler sua mensagem",
                           "subtitulo": u"Página 2 de 8",
                           "texto": u"Para ter certeza de que alguém específico irá ler sua mensagem, você pode mencionar ela usando <b>@'NomeDoUsuário'</b> e a pessoa será notificada por email de sua mensagem."
                           },
                         
                          {"titulo": u"1.3 - Escrevendo uma mensagem para uma comunidade",
                           "subtitulo": u"Página 3 de 8",
                           "texto": u"Para mandar uma mensagem em uma comunidade, siga os seguintes passos:<ul><li>Entre na página da comunidade.</li><li>No menu principal, vá em <b>Comunicação</b> e selecione a opção <b>Microblog</b>.</li><li>Agora, digite sua mensagem na caixa de texto e clique em enviar.</li></ul>Pronto, a mensagem irá aparecer no <b>Microblog</b> da comunidade."
                           },
                          
                          {"titulo": u"1.4 - Escrevendo uma mensagem para as pessoas de uma comunidade",
                           "subtitulo": u"Página 4 de 8",
                           "texto": u"Para escrever uma mensagem diretamente a todas as pessoas de uma comunidade, você pode mencionar a comunidade usando <b>@'NomeDaComunidade'</b> e todas as pessoas que fazem parte da comunidade serão notificadas por email de sua mensagem."
                           },
                         
                          {"titulo": u"1.5 - Respondendo uma mensagem",
                           "subtitulo": u"Página 5 de 8",
                           "texto": u"Para responder uma mensagem, basta clicar no ícone <img src = '/static/imagens/icones/reply16.png'/> (responder), digitar sua resposta e enviar. Sua mensagem fará parte da conversa da mensagem original."
                           },
                         
                           {"titulo": u"1.6 - Visualizando uma conversa",
                           "subtitulo": u"Página 6 de 8",
                           "texto": u"Para vizualizar uma conversa, basta clicar no ícone <img src = '/static/imagens/icones/talk16.png'/> (ler conversa) da mensagem da qual você deseja ler a conversa.<br><i>Para esta função estar disponível é necessário que a mensagem tenha pelomenos uma resposta.</i>"
                           },
                         
                           {"titulo": u"1.7 - Removendo uma mensagem",
                           "subtitulo": u"Página 7 de 8",
                           "texto": u"Para remover uma mensagem, basta clicar no ícone <img src='/static/imagens/icones/delete16.png'/> (apagar) da mensagem que você deseja deletar e clicar em <b>Ok</b> na janela de confirmação.<br><i>Você não pode apagar mensagens de outros usuários e se a mensagem tiver alguma resposta, elas não serão apagadas.</i>"
                           },
                         
                           {"titulo": u"1.8 - Compartilhando uma mensagem",
                            "subtitulo": u"Página 8 de 8",
                            "texto": u"Para compartilhar uma mensagem, basta clicar no ícone <img src = '/static/imagens/icones/share16.png'/> (compartilhar). Na página seguinte, você poderá comentar a mensagem que será compartilhada e escolher se ela será compartilhada com seus amigos ou uma comunidade."                           
                            }
                        ]
                },
                       
                {
               "titulo": u"Tutorial 2: Diferentes Vizualizações do Microblog",
               "telas": [
                          {"titulo": u"1.1 - Histórico",
                           "subtitulo": u"Página 1 de 5",
                           "texto": u"Quando você entra em seu microblog uma lista de posts aparecem e você pode selecionar nas opções ao lado quais tipos de post que você quer vizualizar. Por padrão, é mostrado o histótico de todos os seus posts, dos posts das comunidades das quais você participa e dos posts que você foi mencionado."
                           },
                         
                          {"titulo": u"1.2 - Menções",
                           "subtitulo": u"Página 2 de 5",
                           "texto": u"Para visualizar somente os posts em que você foi mencionado, selecione o ícone <img src = '/static/imagens/icones/at32.png' style = 'width: 16px;'/> e somente os posts em que você foi mencionado irá aparecer."
                           },
                         
                          {"titulo": u"1.3 - Meu Microblog",
                           "subtitulo": u"Página 3 de 5",
                           "texto": u"Para vizualizar os posts que você escreveu, selecione o ícone <img src = '/static/imagens/icones/myposts32.png' style = 'width: 16px;'/> (Mblogs de @'SeuNome')."
                           },
                         
                          {"titulo": u"1.4 - Microblog de Comunidades",
                           "subtitulo": u"Página 4 de 5",
                           "texto": u"Nas comunidades, só é possível dois tipos de vizualizações: O histórico e as menções"
                           },
                         
                          {"titulo": u"1.5 - Microblog de seus amigos",
                           "subtitulo": u"Página 4 de 5",
                           "texto": u"Você pode vizualizar o <b>Microblog</b> de um amigo indo em seu perfil e no menu principal em <b>Comunicação</b>, escolha <b>Microblog</b> e você poderá vizualizar o <b>Microblog</b> e as <b>menções</b> feitas a seu amigo."
                           }
                        ]
                }                       
        ]
      }