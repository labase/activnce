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
import socket
import os

# Versão da Plataforma
VERSAO_TNM = "0.15.1103"

# Instância da Plataforma:
# alterar este nome ao criar uma nova instância.
PLATAFORMA = "ActivUFRJ"

# Indica se esta executando no servidor ou não
INSERVER = (socket.gethostname().lower()=='activufrj')

# Endereço da Plataforma
if INSERVER:
    PLATAFORMA_URL = "activufrj.nce.ufrj.br"
    #DIR_RAIZ_ACTIV = "/opt/activufrj/main/"
else:
    PLATAFORMA_URL = "localhost:8888"
    #DIR_RAIZ_ACTIV = "/home/administrador/workspace-activ/activnce/main/"
    #DIR_RAIZ_ACTIV = "/home/fanelli/workspace/Activ/main/"
    #PLATAFORMA_URL = "146.164.250.81:8888"

DIR_RAIZ_ACTIV = os.path.dirname(os.path.realpath(__file__))+"/"


# Localização do CouchDB
COUCHDB_URL = 'http://127.0.0.1:5984/'

# Configuração do servidor SMTP
SMTP = {
            'servidor': 'smtp.nce.ufrj.br',
            'porta': 25,
            'remetente': 'noreply@nce.ufrj.br'
        }

# Indica se deve escrever na console os emails enviados pela plataforma
DEBUG_EMAIL = False

# Indica se deve enviar emails do servidor de teste
ENVIAR_EMAIL_DE_LOCALHOST = False

# Indica email para envio de mensagens reportando erro 500 (internal server error)
EMAIL_ERROR_NOTIFY = "marcia@nce.ufrj.br,mauricio@nce.ufrj.br"

#LABVAD_URL = "http://146.164.3.24/ucanacuca/labvad/"
#LABVAD_LOGIN_URL = "http://146.164.3.24/ucanacuca/labvad/login_activ.php"
LABVAD_URL = "http://146.164.3.33/labvad2/labvad.php"
LABVAD_LOGIN_URL = "http://146.164.3.33/labvad2/login_activufrj.php"


# Dicionário com definição de todos os tutoriais
# Cada tutorial pode ser criado no arquivo _tutorial.py dentro de cada módulo
TUTORIAL = dict()

# Indica se deve gerar arquivo txt com log da execução das threads
LOG_THREADS = True             
LOG_THREADS_FILE = "threads.log"
             
# Pontos de Entrada da Aplicação:
# Dependendo da URL chamada, mostra uma tela de login diferente
#
ENTRY_POINTS = {
        "activnce.nce.ufrj.br":{
                "arq_home": "index-activ_NCE.html",
                "arq_logo": ""
                },
        "medicina.activ.nce.ufrj.br":{
                "arq_home": "index-activ_medicina.html",
                "arq_logo": ""
                },
        "cafeecerebro.nce.ufrj.br":{
                "arq_home": "index-activ_cafe.html",
                "arq_logo": ""
                },
        "cafenamerenda.nce.ufrj.br":{
                "arq_home": "index-activ_cafenamerenda.html",
                "arq_logo": ""
                },
        "pulodogato.nce.ufrj.br":{
                "arq_home": "index-activ_gato.html",
                "arq_logo": ""
                },
        "localhost:8888":{
                #"arq_home": "index-activ_cafe.html",
                #"arq_home": "index-activ_medicina.html",
                #"arq_home": "index-activ_gato.html",
                #"arq_home": "index-activ_NCE.html",
                "arq_home": "index-activ_UFRJ2.html",
                "arq_logo": ""
                },
        "146.164.250.233:8888":{
                #"arq_home": "index-activ_UFRJ.html",
                # "arq_home": "index-activ_medicina.html",
                # "arq_home": "index-activ_cafe.html",
                "arq_home": "index-activ_cafenamerenda.html",
                "arq_logo": ""
                }
        }

DEFAULT_ENTRY_POINT = {
        "arq_home": "index-activ_UFRJ2.html",
        "arq_logo": ""
        }

# ------ Descreve cada um dos processos que serão iniciados como threads -----------

# Processos executados imediatamente quando a aplicação inicia e depois
# num intervalo de tempo definido (em minutos).
# Para desabilitar e execução de uma thread, use minutos=0.
#
THREAD_PROCESSES = {
        # Copia o log e o news para o banco de dados e processa a ordenação das listas de amigos e comunidades.
        # implementado por model.log.saveLog()
        "Logger":             10,       # a cada 5 minutos
        
        # Carrega lista de tags para o autocomplete
        # implementado por core.model.saveAutocompleteStrings()
        "AutocompleteLoader":  5,       # a cada 5 minutos
        
        # Envia email com notificação do chat
        # implementado por chat.model.batch_notify()
        "ChatNotify":         30,       # a cada 30 minutos
        }

# Processos executados num dia da semana/hora definidos.
# Dias da semana => 
#    segunda:0, terça:1, quarta:2, quinta:3, sexta:4, sabado:5, domingo:6
#    diariamente:9
#
DATED_THREAD_PROCESSES = {
        # Envia todas as notificações pendentes em batch
        # implementado por Notify.batch_notify()
        "Notifier":  { "wkday": 6,   # Aos domingos às 00:00:00 horas
                       "hh": 0,
                       "mm": 0,
                       "ss": 0
                    },
                          
        # Remove as novidades antigas do banco de dados
        # implementado por log.model.cleanNews()
        "NewsCleaner": { "wkday": 9,  # Diariamente às 03:00:00 horas
                         "hh": 3, # 3
                         "mm": 0, # 0
                         "ss": 0
                    }
        }


# Usuário criado automaticamente
USER_ADMIN       = "activ_admin"
SENHA_USER_ADMIN = "123456"                            # Senha padrão que deve ser alterada após instalação

# Comunidades criadas automaticamente
COMUNIDADE_BEMVINDO = "Bem_Vindo"

# Descrição dos privilégios criados automaticamente
PRIV_SUPORTE_ACTIV = "Priv_Suporte_Activ"
PRIV_CONVIDAR_USUARIOS = "Priv_Convidar_Usuarios"
PRIV_GLOBAL_ADMIN = "Priv_Global_Admin"
PRIV_CRIAR_COMUNIDADES = "Priv_Criar_Comunidades"

PRIVILEGIOS = {
               PRIV_SUPORTE_ACTIV: {
                    'desc': u"Suporte aos usuários do %s" % PLATAFORMA,
                    'apps': {"/admin/listusers": u"Procurar usuários, alterar quota de upload",
                             "/admin/onlineusers": u"Listar usuários online",
                             "/admin/listcommunities":u"Listar todas as comunidades, alterar quota de upload"
                            },
                    'services': []
               }, 
               PRIV_CONVIDAR_USUARIOS: {
                    'desc': u"Enviar convites do %s" % PLATAFORMA,
                    'apps': {"/invites": "Gerenciar convites"},
                    'services': []
               },
               PRIV_CRIAR_COMUNIDADES: {
                    'desc': u"Criar comunidades",
                    'apps': {"/communities/new": "Criar uma comunidade"},
                    'services': []
               },
               PRIV_GLOBAL_ADMIN: {
                    'desc': u"Administração do %s" % PLATAFORMA,
                    'apps': {"/shutdown": u"Finalizar aplicação salvando logs e news",
                             "/stats": u"Estatísticas de acesso à plataforma",
                             "/admin/totalusers": u"Totais de usuários na plataforma",
                             "/reactivateuser": u"Reativa um usuário suspenso",
                             "/admin/skillstats": u"Estatísticas de uso das ferramentas de habilidades"
                            },
                    'services': ['blog', 'noticia']
               },
               COMUNIDADE_BEMVINDO: {
                    'desc': u"Bem-Vindo ao %s" % PLATAFORMA,
                    'apps': {},
                    'services': ['mblog', 'wiki', 'file', 'blog', 'noticia']
               }
}

# Hierarquia dos menus de usuários e comunidades

MENU = {
            "member": [  {"name": "Pessoas",
                          "icon": "fa-user",
                          "subitens": ["amigos", "comunidades"]
                          },
                          {"name": u"Comunicação",
                           "icon": "fa-bullhorn",
                           "subitens": ["mblog", "chat", "recados"]
                          },
                          {"name": "Conhecimento",
                           "icon": "fa-book",
                           "subitens": ["skills", "wiki", "file", "blog", 
                                            "bookmarks", "glossary", "paint", "videoaula"]
                          },
                          {"name": "Eventos",
                           "icon": "fa-calendar",
                           "subitens": ["agenda", "activity"]
                          }
                      ],
            "community": [  {"name": "Pessoas",
                          "icon": "fa-user",
                          "subitens": ["participantes"]
                          },
                          {"name": u"Comunicação",
                           "icon": "fa-bullhorn",
                           "subitens": ["mblog", "forum", "chat", "noticia", "recados"]
                          },
                          {"name": "Conhecimento",
                           "icon": "fa-book",
                           "subitens": ["wiki", "file", "blog", "bookmarks", "glossary", 
                                     "evaluation", "task", "studio", "quiz", "videoaula"]
                          },
                          {"name": "Eventos",
                           "icon": "fa-calendar",
                           "subitens": ["agenda", "activity"]
                          }
                      ],

        }


# Descrição dos serviços                     
SERVICES = {
            "member": { 
                       "amigos": {
                                   "my_link": "/friends/",
                                   "link": "/friends/",
                                   "description": "Amigos",
                                   "my_hint": "Minha lista de amigos.",       # Texto do hint quando vejo as minhas páginas.
                                   "hint": "Lista de amigos de %s.",    # Texto do hint quando vejo as páginas de outras pessoas.
                                   "optional": False,                       # Indica se o usuário pode ou não selecionar este serviço no perfil.
                                   
                                   "editable_perm": False,                  # Indica se a permissão sobre este serviço pode ser definida pelo usuário ou não.
                                   "perm_type": "",                         # Pode ser "service" se a permissão se aplica ao serviço como um todo
                                                                            # (ex: blog, bookmarks, etc)
                                                                            # ou "object" se a permissão se aplica individualmente a um objeto do serviço
                                                                            # (ex: página Wiki, arquivo, avaliação, etc).
                                   "legenda_perm_r": "",                    # legendas para o form de alteração de permissões
                                   "legenda_perm_w": "",
                                   "perm_r": [],                            # Lista de permissões de leitura possíveis.
                                   "perm_w": [],                            # Lista de escrita de leitura possíveis.
                                   "default_r": {"Privada": "", u"Pública": ""}, # Permissão default de leitura.
                                   "default_w": {"Privada": "", u"Pública": ""}  # Permissão default de escrita.
                        },
                       "comunidades": {
                                   "my_link": "/communities/",
                                   "link": "/communities/",
                                   "description": "Comunidades",
                                   "my_hint": "Minha lista de comunidades.",
                                   "hint": "Lista de comunidades de %s.",
                                   "optional": False,
                                   
                                   "editable_perm": False,
                                   "perm_type": "",
                                   "legenda_perm_r": "",                    # legendas para o form de alteração de permissões
                                   "legenda_perm_w": "",
                                   "perm_r": [],
                                   "perm_w": [],
                                   "default_r": {"Privada": "", u"Pública": ""}, 
                                   "default_w": {"Privada": "", u"Pública": ""} 
                        },
                       "blog": {
                                   "my_link": "/blog/",
                                   "link": "/blog/",
                                   "description": "Blog",
                                   "my_hint": u"Publicação de conteúdos organizados cronologicamente.",
                                   "hint": u"Publicação de conteúdos organizados cronologicamente.",
                                   "optional": True,
                                   
                                   "editable_perm": True,
                                   "perm_type": "service",
                                   "legenda_perm_r": "Quem pode ler?",                    # legendas para o form de alteração de permissões
                                   "legenda_perm_w": "Quem pode alterar?",
                                   "perm_r": ["acesso_privado", "acesso_grupos", "acesso_comunidade", "acesso_activ", "acesso_publico"],
                                   "perm_w": ["acesso_privado"],
                                   "default_r": {"Privada": "acesso_comunidade", u"Pública": "acesso_activ"},
                                   "default_w": {"Privada": "acesso_privado", u"Pública": "acesso_privado"}
                        },
                       
                        "mblog": {
                                   "my_link": "/mblog/",
                                   "link": "/mblog/",
                                   "description": "Microblog",
                                   "my_hint": u"Publicação de mensagens curtas, com até 350 caracteres.",
                                   "hint": u"Publicação de mensagens curtas, com até 350 caracteres.",
                                   "optional": True,
                                   
                                   "editable_perm": False,
                                   "perm_type": "",
                                   "legenda_perm_r": "",                    # legendas para o form de alteração de permissões
                                   "legenda_perm_w": "",
                                   "perm_r": [],
                                   "perm_w": [],
                                   "default_r": {"Privada": "", u"Pública": ""}, 
                                   "default_w": {"Privada": "", u"Pública": ""} 
                        },
                        "chat": {
                                   "my_link": "/chat/",
                                   "link": "/chat/",
                                   "description": "Chat",
                                   "my_hint": "Minhas conversas",
                                   "hint": u"Comunicação em tempo real com %s.",
                                   "optional": False,
                                   
                                   "editable_perm": False,
                                   "perm_type": "",
                                   "legenda_perm_r": "",                    # legendas para o form de alteração de permissões
                                   "legenda_perm_w": "",
                                   "perm_r": [],
                                   "perm_w": [],
                                   "default_r": {"Privada": "", u"Pública": ""}, 
                                   "default_w": {"Privada": "", u"Pública": ""} 
                        },
                        "wiki": {
                                   "my_link": "/wiki/",
                                   "link": "/wiki/",
                                   "description": u"Páginas",
                                   "my_hint": u"Publicação de conteúdos na forma de páginas Web.",
                                   "hint": u"Publicação de conteúdos na forma de páginas Web.",
                                   "optional": True,
                                   
                                   "editable_perm": True,
                                   "perm_type": "object",
                                   "legenda_perm_r": "Quem pode ler?",                    # legendas para o form de alteração de permissões
                                   "legenda_perm_w": "Quem pode alterar?",
                                   "perm_r": ["acesso_privado", "acesso_grupos", "acesso_comunidade", "acesso_activ", "acesso_publico"],
                                   "perm_w": ["acesso_privado"],
                                   "default_r": {"Privada": "acesso_comunidade", u"Pública": "acesso_activ"},
                                   "default_w": {"Privada": "acesso_privado", u"Pública": "acesso_privado"}
                        },
                        "file": {
                                   "my_link": "/file/",
                                   "link": "/file/",
                                   "description": "Arquivos",
                                   "my_hint": u"Meu repositório de arquivos.",
                                   "hint": u"Repositório de arquivos de %s.",
                                   "optional": True,
                                   
                                   "editable_perm": True,
                                   "perm_type": "object",
                                   "legenda_perm_r": "Quem pode ler?",                    # legendas para o form de alteração de permissões
                                   "legenda_perm_w": "Quem pode alterar?",
                                   "perm_r": ["acesso_privado", "acesso_grupos", "acesso_comunidade", "acesso_activ", "acesso_publico"],
                                   "perm_w": ["acesso_privado"],
                                   "default_r": {"Privada": "acesso_comunidade", u"Pública": "acesso_activ"},
                                   "default_w": {"Privada": "acesso_privado", u"Pública": "acesso_privado"}
                        },
                       "skills": {
                                   "my_link": "/profile/skills/",
                                   "link": "/profile/skills/chart/user/",
                                   "description": "Habilidades",
                                   "my_hint": "Minha lista de habilidades.",
                                   "hint": "Habilidades de %s.",
                                   "optional": False,
                                   
                                   "editable_perm": False,
                                   "perm_type": "",
                                   "legenda_perm_r": "",                    # legendas para o form de alteração de permissões
                                   "legenda_perm_w": "",
                                   "perm_r": [],
                                   "perm_w": [],
                                   "default_r": {"Privada": "", u"Pública": ""}, 
                                   "default_w": {"Privada": "", u"Pública": ""} 
                        },
                        "agenda": {
                                   "my_link": "/agenda/",
                                   "link": "/agenda/",
                                   "description": "Agenda",
                                   "my_hint": u"Registro de eventos e compromissos.",
                                   "hint": u"Registro de eventos e compromissos.",
                                   "optional": True,
                                   
                                   "editable_perm": True,
                                   "perm_type": "service",
                                   "legenda_perm_r": "Quem pode ler?",                    # legendas para o form de alteração de permissões
                                   "legenda_perm_w": "Quem pode alterar?",
                                   "perm_r": ["acesso_privado", "acesso_grupos", "acesso_comunidade", "acesso_activ"],
                                   "perm_w": ["acesso_privado"],
                                   "default_r": {"Privada": "acesso_comunidade", u"Pública": "acesso_activ"},
                                   "default_w": {"Privada": "acesso_privado", u"Pública": "acesso_privado"}
                        },
                        "paint": {
                                   "my_link": "/paint/",
                                   "link": "/paint/",
                                   "description": "Desenhos",
                                   "my_hint": u"Criação de desenhos.",
                                   "hint": u"Criação de desenhos.",
                                   "optional": True,
                                   
                                   "editable_perm": False,
                                   "perm_type": "",
                                   "legenda_perm_r": "",                    # legendas para o form de alteração de permissões
                                   "legenda_perm_w": "",
                                   "perm_r": [],
                                   "perm_w": [],
                                   "default_r": {"Privada": "", u"Pública": ""}, 
                                   "default_w": {"Privada": "", u"Pública": ""} 
                        },
                        "bookmarks": {
                                   "my_link": "/bookmarks/",
                                   "link": "/bookmarks/",
                                   "description": "Favoritos",
                                   "my_hint": u"Meus favoritos (coleção de links).",
                                   "hint": u"Favoritos de %s (coleção de links).",
                                   "optional": True,
                                   
                                   "editable_perm": True,
                                   "perm_type": "service",
                                   "legenda_perm_r": "Quem pode ler?",                    # legendas para o form de alteração de permissões
                                   "legenda_perm_w": "Quem pode alterar?",
                                   "perm_r": ["acesso_privado", "acesso_grupos", "acesso_comunidade", "acesso_activ"],
                                   "perm_w": ["acesso_privado"],
                                   "default_r": {"Privada": "acesso_comunidade", u"Pública": "acesso_activ"},
                                   "default_w": {"Privada": "acesso_privado", u"Pública": "acesso_privado"}
                        },
                        "glossary": {
                                   "my_link": "/glossary/",
                                   "link": "/glossary/",
                                   "description": u"Glossário",
                                   "my_hint": u"Armazenamento de termos e suas respectivas definições.",
                                   "hint": u"Armazenamento de termos e suas respectivas definições.",
                                   "optional": True,
                                   
                                   "editable_perm": True,
                                   "perm_type": "service",
                                   "legenda_perm_r": "Quem pode ler?",                    # legendas para o form de alteração de permissões
                                   "legenda_perm_w": "Quem pode alterar?",
                                   "perm_r": ["acesso_privado", "acesso_grupos", "acesso_comunidade", "acesso_activ"],
                                   "perm_w": ["acesso_privado"],
                                   "default_r": {"Privada": "acesso_comunidade", u"Pública": "acesso_activ"},
                                   "default_w": {"Privada": "acesso_privado", u"Pública": "acesso_privado"}
                        },
                        "gcalendar": {
                                   "my_link": "/google/",
                                   "link": "/google/",
                                   "description": "Agenda Google",
                                   "my_hint": u"Acesso a Agenda do Google",
                                   "hint": u"Acesso a Agenda do Google",
                                   "optional": True,
                                   
                                   "editable_perm": False,
                                   "perm_type": "",
                                   "legenda_perm_r": "",                    # legendas para o form de alteração de permissões
                                   "legenda_perm_w": "",
                                   "perm_r": [],
                                   "perm_w": [],
                                   "default_r": {"Privada": "", u"Pública": ""}, 
                                   "default_w": {"Privada": "", u"Pública": ""} 
                        },
                        "videoaula": {
                                   "my_link": "/videoaula/",
                                   "link": "/videoaula/",
                                   "description": "Videoaulas",
                                   "my_hint": u"Apresentação de aula em vídeo sincronizado com slides.",
                                   "hint": u"Apresentação de aula em vídeo sincronizado com slides.",
                                   "optional": True,
                                   
                                   "editable_perm": True,
                                   "perm_type": "object",
                                   "legenda_perm_r": "Quem pode ler?",                    # legendas para o form de alteração de permissões
                                   "legenda_perm_w": "Quem pode alterar?",
                                   "perm_r": ["acesso_privado", "acesso_grupos", "acesso_comunidade", "acesso_activ", "acesso_publico"],
                                   "perm_w": ["acesso_privado"],
                                   "default_r": {"Privada": "acesso_comunidade", u"Pública": "acesso_activ"},
                                   "default_w": {"Privada": "acesso_privado", u"Pública": "acesso_privado"}
                        },
                        "activity": {
                                   "my_link": "/activity/pendent/",
                                   "link": "/activity/",
                                   "description": "Atividades",
                                   "my_hint": u"Controle de projetos e de atividades.",
                                   "hint": u"Controle de projetos e de atividades.",
                                   "optional": True,
                                   
                                   "editable_perm": True,
                                   "perm_type": "service",
                                   "legenda_perm_r": u"Quem pode ver as atividades?",                    # legendas para o form de alteração de permissões
                                   "legenda_perm_w": u"Quem pode criar e alterar atividades?",
                                   "perm_r": ["acesso_privado", "acesso_grupos", "acesso_comunidade", "acesso_activ"],
                                   "perm_w": ["acesso_privado"],
                                   "default_r": {"Privada": "acesso_comunidade", u"Pública": "acesso_activ"},
                                   "default_w": {"Privada": "acesso_privado", u"Pública": "acesso_privado"}
                        }, 
                        "recados": {
                                   "my_link": "/scrap/",
                                   "link": "/scrap/",
                                   "description": "Recados",
                                   "my_hint": u"Acesso aos meus recados recebidos por e-mail.",
                                   "hint": u"Envio de recados por e-mail para %s.",                                   
                                   "optional": False,
                                   
                                   "editable_perm": False,
                                   "perm_type": "",
                                   "legenda_perm_r": "",                    # legendas para o form de alteração de permissões
                                   "legenda_perm_w": "",
                                   "perm_r": [],
                                   "perm_w": [],
                                   "default_r": {"Privada": "", u"Pública": ""}, 
                                   "default_w": {"Privada": "", u"Pública": ""} 
                        }                                          
            },
            
            "community": { 
                       "participantes": {
                                   "link": "/members/",
                                   "description": "Participantes",
                                   "hint": u"Lista de participantes da comunidade %s.",
                                   "optional": False,
                                   
                                   "editable_perm": False,
                                   "perm_type": "",
                                   "legenda_perm_r": "",                    # legendas para o form de alteração de permissões
                                   "legenda_perm_w": "",
                                   "perm_r": [],
                                   "perm_w": [],
                                   "default_r": {"Privada": "", u"Pública": ""}, 
                                   "default_w": {"Privada": "", u"Pública": ""} 
                        },
                        "forum": {
                                   "link": "/forum/",
                                   "description": "Forum",
                                   "hint": u"Fórum de discussão estruturado em tópicos.",
                                   "optional": True,
                                   
                                   "editable_perm": True,
                                   "perm_type": "service",
                                   "legenda_perm_r": "Quem pode ler?",                    # legendas para o form de alteração de permissões
                                   "legenda_perm_w": "Quem pode postar?",
                                   "perm_r": ["acesso_privado", "acesso_grupos", "acesso_comunidade", "acesso_activ"],
                                   "perm_w": ["acesso_privado", "acesso_grupos", "acesso_comunidade", "acesso_activ"],
                                   "default_r": {"Privada": "acesso_comunidade", u"Pública": "acesso_activ"},
                                   "default_w": {"Privada": "acesso_comunidade", u"Pública": "acesso_comunidade"}
                        },
                        "blog": {
                                   "link": "/blog/",
                                   "description": "Blog",
                                   "hint": u"Publicação colaborativa de conteúdos organizados cronologicamente.",
                                   "optional": True,
                                   
                                   "editable_perm": True,
                                   "perm_type": "service",
                                   "legenda_perm_r": "Quem pode ler?",                    # legendas para o form de alteração de permissões
                                   "legenda_perm_w": "Quem pode alterar?",
                                   "perm_r": ["acesso_privado", "acesso_grupos", "acesso_comunidade", "acesso_activ", "acesso_publico"],
                                   "perm_w": ["acesso_privado", "acesso_grupos", "acesso_comunidade"],
                                   "default_r": {"Privada": "acesso_comunidade", u"Pública": "acesso_activ"},
                                   "default_w": {"Privada": "acesso_comunidade", u"Pública": "acesso_comunidade"}
                        },
                        "mblog": {
                                   "link": "/mblog/",
                                   "description": "Microblog",
                                   "hint": u"Publicação de mensagens curtas, com até 350 caracteres.",
                                   "optional": True,
                                   
                                   "editable_perm": False,
                                   "perm_type": "",
                                   "legenda_perm_r": "",                    # legendas para o form de alteração de permissões
                                   "legenda_perm_w": "",
                                   "perm_r": [],
                                   "perm_w": [],
                                   "default_r": {"Privada": "", u"Pública": ""}, 
                                   "default_w": {"Privada": "", u"Pública": ""} 
                        },
                        "wiki": {
                                   "link": "/wiki/",
                                   "description": u"Páginas",
                                   "hint": u"Publicação colaborativa de conteúdos na forma de páginas Web.",
                                   "optional": True,
                                   
                                   "editable_perm": True,
                                   "perm_type": "object",
                                   "legenda_perm_r": "Quem pode ler?",                    # legendas para o form de alteração de permissões
                                   "legenda_perm_w": "Quem pode alterar?",
                                   "perm_r": ["acesso_privado", "acesso_grupos", "acesso_comunidade", "acesso_activ", "acesso_publico"],
                                   "perm_w": ["acesso_privado", "acesso_grupos", "acesso_comunidade"],
                                   "default_r": {"Privada": "acesso_comunidade", u"Pública": "acesso_activ"},
                                   "default_w": {"Privada": "acesso_comunidade", u"Pública": "acesso_comunidade"}
                        },
                        "file": {
                                   "link": "/file/",
                                   "description": "Arquivos",
                                   "hint": u"Repositório de arquivos de %s.",
                                   "optional": True,
                                   
                                   "editable_perm": True,
                                   "perm_type": "object",
                                   "legenda_perm_r": "Quem pode ler?",                    # legendas para o form de alteração de permissões
                                   "legenda_perm_w": "Quem pode alterar?",
                                   "perm_r": ["acesso_privado", "acesso_grupos", "acesso_comunidade", "acesso_activ", "acesso_publico"],
                                   "perm_w": ["acesso_privado", "acesso_grupos", "acesso_comunidade"],
                                   "default_r": {"Privada": "acesso_comunidade", u"Pública": "acesso_activ"},
                                   "default_w": {"Privada": "acesso_comunidade", u"Pública": "acesso_comunidade"}
                        },
                        "agenda": {
                                   "link": "/agenda/",
                                   "description": "Agenda",
                                   "hint": u"Registro de eventos e compromissos.",
                                   "optional": True,
                                   
                                   "editable_perm": True,
                                   "perm_type": "service",
                                   "legenda_perm_r": "Quem pode ler?",                    # legendas para o form de alteração de permissões
                                   "legenda_perm_w": "Quem pode alterar?",
                                   "perm_r": ["acesso_privado", "acesso_grupos", "acesso_comunidade", "acesso_activ"],
                                   "perm_w": ["acesso_privado", "acesso_grupos", "acesso_comunidade"],
                                   "default_r": {"Privada": "acesso_comunidade", u"Pública": "acesso_activ"},
                                   "default_w": {"Privada": "acesso_comunidade", u"Pública": "acesso_comunidade"}
                        },
                        "evaluation": {
                                   "link": "/evaluation/",
                                   "description": u"Avaliações",
                                   "hint": "Avaliação de conteúdos pelos membros da comunidade.",
                                   "optional": True,
                                   
                                   "editable_perm": True,
                                   "perm_type": "object",
                                   "legenda_perm_r": "Quem pode avaliar?",                    # legendas para o form de alteração de permissões
                                   "legenda_perm_w": "Quem pode alterar?",
                                   "perm_r": ["acesso_privado", "acesso_grupos", "acesso_comunidade"],
                                   "perm_w": ["acesso_privado"],
                                   "default_r": {"Privada": "acesso_comunidade", u"Pública": "acesso_comunidade"},
                                   "default_w": {"Privada": "acesso_privado", u"Pública": "acesso_privado"}
                        },
                        "noticia": {
                                   "link": "/noticia/",
                                   "description": u"Notícias",
                                   "hint": u"Publicação de notícias/avisos para os membros da comunidade.",
                                   "optional": True,
                                   
                                   "editable_perm": False,
                                   "perm_type": "",
                                   "legenda_perm_r": "",                    # legendas para o form de alteração de permissões
                                   "legenda_perm_w": "",
                                   "perm_r": [],
                                   "perm_w": [],
                                   "default_r": {"Privada": "", u"Pública": ""}, 
                                   "default_w": {"Privada": "", u"Pública": ""} 
                        },
                        "chat": {
                                   "link": "/chat/",
                                   "description": "Chat",
                                   "hint": u"Comunicação em tempo real entre os membros da comunidade.",
                                   "optional": True,
                                   
                                   "editable_perm": False,
                                   "perm_type": "",
                                   "legenda_perm_r": "",                    # legendas para o form de alteração de permissões
                                   "legenda_perm_w": "",
                                   "perm_r": [],
                                   "perm_w": [],
                                   "default_r": {"Privada": "", u"Pública": ""}, 
                                   "default_w": {"Privada": "", u"Pública": ""} 
                        },
                        "studio": {
                                   "link": "/studio/",
                                   "description": u"Estúdio de Games",
                                   "hint": u"Repositório de ilustrações para desenvolvimento de games.",
                                   "optional": True,
                                   
                                   "editable_perm": False,
                                   "perm_type": "",
                                   "legenda_perm_r": "",                    # legendas para o form de alteração de permissões
                                   "legenda_perm_w": "",
                                   "perm_r": [],
                                   "perm_w": [],
                                   "default_r": {"Privada": "", u"Pública": ""}, 
                                   "default_w": {"Privada": "", u"Pública": ""} 
                        },
                        "bookmarks": {
                                   "link": "/bookmarks/",
                                   "description": "Favoritos",
                                   "hint": u"Favoritos de %s (coleção de links).",
                                   "optional": True,
                                   
                                   "editable_perm": True,
                                   "perm_type": "service",
                                   "legenda_perm_r": "Quem pode ler?",                    # legendas para o form de alteração de permissões
                                   "legenda_perm_w": "Quem pode alterar?",
                                   "perm_r": ["acesso_privado", "acesso_grupos", "acesso_comunidade", "acesso_activ"],
                                   "perm_w": ["acesso_privado", "acesso_grupos", "acesso_comunidade"],
                                   "default_r": {"Privada": "acesso_comunidade", u"Pública": "acesso_activ"},
                                   "default_w": {"Privada": "acesso_comunidade", u"Pública": "acesso_comunidade"}
                        },
                        "glossary": {
                                   "link": "/glossary/",
                                   "description": u"Glossário",
                                   "hint": u"Armazenamento de termos e suas respectivas definições.",
                                   "optional": True,
                                   
                                   "editable_perm": True,
                                   "perm_type": "service",
                                   "legenda_perm_r": "Quem pode ler?",                    # legendas para o form de alteração de permissões
                                   "legenda_perm_w": "Quem pode alterar?",
                                   "perm_r": ["acesso_privado", "acesso_grupos", "acesso_comunidade", "acesso_activ"],
                                   "perm_w": ["acesso_privado", "acesso_grupos", "acesso_comunidade"],
                                   "default_r": {"Privada": "acesso_comunidade", u"Pública": "acesso_activ"},
                                   "default_w": {"Privada": "acesso_comunidade", u"Pública": "acesso_comunidade"}
                        },
                        "task": {
                                   "link": "/task/",
                                   "description": "Tarefas",
                                   "hint": u"Realização de tarefas individuais ou em grupo pelos membros da comunidade.",
                                   "optional": True,
                                   
                                   "editable_perm": False,
                                   "perm_type": "",
                                   "legenda_perm_r": "",                    # legendas para o form de alteração de permissões
                                   "legenda_perm_w": "",
                                   "perm_r": [],
                                   "perm_w": [],
                                   "default_r": {"Privada": "", u"Pública": ""}, 
                                   "default_w": {"Privada": "", u"Pública": ""} 
                        },
                        "gcalendar": {
                                   "link": "/google/",
                                   "description": "Agenda Google",
                                   "hint": u"Acesso a Agenda do Google",
                                   "optional": True,
                                   
                                   "editable_perm": False,
                                   "perm_type": "",
                                   "legenda_perm_r": "",                    # legendas para o form de alteração de permissões
                                   "legenda_perm_w": "",
                                   "perm_r": [],
                                   "perm_w": [],
                                   "default_r": {"Privada": "", u"Pública": ""}, 
                                   "default_w": {"Privada": "", u"Pública": ""} 
                        },
                        "quiz": {
                                   "link": "/quiz/",
                                   "description": u"Quiz e Banco de Questões",
                                   "hint": u"Armazenamento de questões de múltipla escolha para utilização em um Quiz.",
                                   "optional": True,
                                   
                                   "editable_perm": True,
                                   "perm_type": "object",
                                   "legenda_perm_r": "Quem pode responder este quiz?",                    # legendas para o form de alteração de permissões
                                   "legenda_perm_w": "Quem pode alterar ou remover este quiz?",
                                   "perm_r": ["acesso_privado", "acesso_grupos", "acesso_comunidade", "acesso_activ"],
                                   "perm_w": ["acesso_privado"],
                                   "default_r": {"Privada": "acesso_comunidade", u"Pública": "acesso_comunidade"},
                                   "default_w": {"Privada": "acesso_privado", u"Pública": "acesso_privado"}
                        },
                        "question": {
                                   "link": "",
                                   "description": "",
                                   "hint": "",
                                   "optional": False,
                                   
                                   "editable_perm": True,
                                   "perm_type": "service",
                                   "legenda_perm_r": u"Quem pode ver as questões?",                    # legendas para o form de alteração de permissões
                                   "legenda_perm_w": u"Quem pode criar e alterar questões?",
                                   "perm_r": ["acesso_privado", "acesso_grupos", "acesso_comunidade"],
                                   "perm_w": ["acesso_privado", "acesso_grupos", "acesso_comunidade"],
                                   "default_r": {"Privada": "acesso_privado", u"Pública": "acesso_privado"},
                                   "default_w": {"Privada": "acesso_privado", u"Pública": "acesso_privado"}
                        },
                        "videoaula": {
                                   "link": "/videoaula/",
                                   "description": "Videoaulas",
                                   "hint": u"Apresentação de aula em vídeo sincronizado com slides.",
                                   "optional": True,
                                   
                                   "editable_perm": True,
                                   "perm_type": "object",
                                   "legenda_perm_r": "Quem pode ler?",                    # legendas para o form de alteração de permissões
                                   "legenda_perm_w": "Quem pode alterar?",
                                   "perm_r": ["acesso_privado", "acesso_grupos", "acesso_comunidade", "acesso_activ", "acesso_publico"],
                                   "perm_w": ["acesso_privado", "acesso_grupos", "acesso_comunidade"],
                                   "default_r": {"Privada": "acesso_comunidade", u"Pública": "acesso_activ"},
                                   "default_w": {"Privada": "acesso_privado", u"Pública": "acesso_privado"}
                        },
                        "activity": {
                                   "link": "/activity/",
                                   "description": "Atividades",
                                   "hint": u"Controle de projetos e de atividades",
                                   "optional": True,
                                   
                                   "editable_perm": True,
                                   "perm_type": "service",
                                   "legenda_perm_r": u"Quem pode ver as atividades?",                    # legendas para o form de alteração de permissões
                                   "legenda_perm_w": u"Quem pode criar e alterar atividades?",
                                   "perm_r": ["acesso_privado", "acesso_grupos", "acesso_comunidade", "acesso_activ"],
                                   "perm_w": ["acesso_privado", "acesso_grupos", "acesso_comunidade"],
                                   "default_r": {"Privada": "acesso_comunidade", u"Pública": "acesso_activ"},
                                   "default_w": {"Privada": "acesso_comunidade", u"Pública": "acesso_comunidade"}
                        },                          
                        "recados": {
                                   "link": "/scrap/",
                                   "description": "Recados",
                                   "hint": u"Envio de recados por e-mail para os participantes de %s.",                           
                                   "optional": False,
                                   
                                   "editable_perm": False,
                                   "perm_type": "",
                                   "legenda_perm_r": "",                    # legendas para o form de alteração de permissões
                                   "legenda_perm_w": "",
                                   "perm_r": [],
                                   "perm_w": [],
                                   "default_r": {"Privada": "", u"Pública": ""}, 
                                   "default_w": {"Privada": "", u"Pública": ""} 
                        }                            
            },
}


# Widgets do painel de controle.
# ainda não está sendo usado
                       
WIDGETS = {
            "member":    ["Amigos", "Comunidades", "Novidades", "Agenda", "Microblog", "Recados", "Aplicativos"],
            "community": []
}

                    
            