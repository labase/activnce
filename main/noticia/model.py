# -*- coding: utf-8 -*-
"""
################################################
Oi Tonomundo - NCE/UFRJ
################################################

:Author: Eduardo Paz
:Contact: edupaz@nce.ufrj.br
:Date: $Date: 2010/08/20  $
:Status: This is a "work in progress"
:Revision: $Revision: 0.01 $
:Home: ``
:Copyright:  
"""
from datetime import datetime

from couchdb import Server
from config import COUCHDB_URL

from libs.strformat import remove_html_tags, str_limit
from libs.dateformat import short_date, human_date


_DOCBASES = ['noticias']

_EMPTYNOTICIA = lambda:dict(
# _id = "registry_id/id"        # nome da comunidade/id da noticia
          id            = 0     # indice da noticia
        , titulo        = ""    # titulo
        , resumo        = ""    # resumo
        , texto         = ""    # corpo da noticia
        , url           = ""    # no lugar do corpo da noticia usar uma url
        , fonte         = ""    # fonte
        , dt_publicacao = ""    # data da publicação
        , dt_validade   = ""    # data limite de exibição da noticia
        , popup         = ""    # indica se a notícia deve aparecer no popup ou não
     )

class Activ(Server):
    "Active database"
    noticias = {}
    
    def __init__(self, url):
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


__ACTIV = Activ(COUCHDB_URL)
NOTICIAS = __ACTIV.noticias

#=============== Classe dados =================================================
    
def _formatar_data(data):
    dt = data.split(".")[0]
    if len(dt) == 19:
        lista = data.split(" ")
        d = lista[0]
        h = lista[1]
        if str(datetime.now()).split(" ")[0] == d:
            return h[0:5]
        else:
            return d[8:10]+"/"+d[5:7]+"/"+d[0:4]
    else:
        return data
    
class Noticias:
    def __init__(self, registry_id):
        self.__registry_id = registry_id
        if registry_id not in NOTICIAS:
            NOTICIAS[registry_id] = {"news": []}
        self.news = list(NOTICIAS[registry_id]["news"])
        return
        
    def get_dict_lista_noticias(self, user=None, popup="N"):
        '''Retorna a lista de dicionários a ser exibida para o usuário.
           Chamada pelo control-panel
        '''
        # popup="S" retorna somente as notícias que devem ser exibidas agora.
        
        lista = []
        for n in range(len(self.news)):
            # popup="S" retorna somente as notícias que devem ser exibidas agora.
            if popup == "N" or (popup == "S" and  self.news[n]["popup"] == "S" and (self.news[n]["dt_validade"] == "" or  self.news[n]["dt_validade"] > str(datetime.now())[0:11])):
                self.news[n]["resumo"] = self.__formatar_texto_html(self.news[n]["resumo"])
                self.news[n]["dt_publicacao_fmt"] = human_date(self.news[n]["dt_publicacao"])
                self.news[n]["dt_publicacao"] = short_date(self.news[n]["dt_publicacao"])
                self.news[n]["id"] = n
                lista.append(self.news[n])
        lista.reverse()
        return lista


    def get_obj_lista_noticias(self, user=None, popup="N"):
        '''Retorna a lista de objetos a ser exibida para o usuário.
           Chamada pelo controlador de notícias.
        '''
        # popup="S" retorna somente as notícias que devem ser exibidas agora.
        
        lista = []
        for n in range(len(self.news)):
            notic = Noticia(self.__registry_id, n)
            
            # popup="S" retorna somente as notícias que devem ser exibidas agora.
            if popup == "N" or (popup == "S" and  notic.popup == "S" and (notic.dt_validade == "" or  notic.dt_validade > str(datetime.now())[0:11])):
                notic.resumo = self.__formatar_texto_html(notic.resumo)
                notic.dt_publicacao_fmt = human_date(notic.dt_publicacao)
                notic.dt_publicacao = short_date(notic.dt_publicacao)
                notic.id = n
                lista.append(notic)
        lista.reverse()
        return lista
    
                
    def insert_noticia(self, noticia):
        if noticia.id >= 0:
            #alterar
            self.news[noticia.id] = noticia.get_noticia()
        else:
            #novo
            self.news.append(noticia.get_noticia())
        temp = dict(NOTICIAS[self.__registry_id])
        temp["news"] = self.news
        NOTICIAS[self.__registry_id] = temp
        self.news = list(NOTICIAS[self.__registry_id]["news"])
        return
    
    def __formatar_texto_html(self, texto):
        '''trocar return por <br>'''
        return texto.replace("\r","").replace("\n", "<br>")
        
    
class Noticia:
    def __init__(self, registry_id, id):
        # criar nova instancia de uma notícia
        self.id = id
        if id > len(NOTICIAS[registry_id]["news"])-1 or id < 0:
            self.__temp = _EMPTYNOTICIA()
        else:
            self.__temp = dict( NOTICIAS[registry_id]["news"][id] )
            
        self.titulo         = self.__temp["titulo"]
        self.resumo         = self.__temp["resumo"]
        self.texto          = self.__temp["texto"]
        self.url            = self.__temp["url"]
        self.fonte          = self.__temp["fonte"]
        self.dt_publicacao  = self.__temp["dt_publicacao"]
        self.dt_validade    = self.__temp["dt_validade"]
        self.fonte_data     = self.__get_fonte_data()
        self.popup          = self.__temp["popup"]
        return
    
    def get_noticia(self):
        self.__temp["titulo"]         = self.titulo
        self.__temp["resumo"]         = self.resumo
        self.__temp["texto"]          = self.texto
        self.__temp["url"]            = self.url
        self.__temp["fonte"]          = self.fonte
        self.__temp["dt_publicacao"]  = self.dt_publicacao
        self.__temp["dt_validade"]    = self.dt_validade
        self.__temp["popup"]          = self.popup
        return self.__temp
    
    def get_resumo(self):
        if self.resumo == "":
            return str_limit(self.texto, 200)
        else:
            return self.resumo

    def get_resumo_sem_html(self):
        if self.resumo == "":
            tmpResumo = remove_html_tags(self.texto.replace("<br>", "\n"))
            return str_limit(tmpResumo, 200)
        else:
            return remove_html_tags(self.resumo.replace("<br>", "\n"))
        
    def __get_fonte_data(self):
        if self.fonte != "":
            return self.fonte+ " - " + _formatar_data(self.dt_publicacao)
        else:
            return _formatar_data(self.dt_publicacao)
    
    
