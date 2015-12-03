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

try:
  from couchdb.schema import Document, TextField, IntegerField, LongField, DateTimeField, DictField, ListField, Schema, FloatField
except ImportError:
  from couchdb.mapping import Document, TextField, IntegerField, LongField, DateTimeField, DictField, ListField, FloatField
  from couchdb.mapping import Mapping as Schema

import database
from database import _CONTEUDO_REMOVIDO
from search.model import addTag, removeTag
from libs.strformat import remove_diacritics, str_limit
from libs.permissions import isAllowedToDeleteObject, isAllowedToComment, isAllowedToDeleteComment, isAllowedToReadObject
from libs.dateformat import short_datetime

from datetime import datetime
import operator
from operator import itemgetter

_NOMEPAG_DEFAULT = { 
    "home":   u"Página inicial",
    "indice": u"Índice"
}

_CONTEUDO_DEFAULT = { 
    "home": u"<br/><br/><br/>Esta é a página de apresentação de %s no ActivUFRJ." +\
            u"<br/><br/><br/><br/><br/>",
    "indice":  u"Este texto é apresentado em todas as suas páginas. " +\
               u"Altere-o incluindo links que permitam facilitar a navegação.<br/>" +\
               u"Exemplo:<br/>" +\
               u"<a href='/wiki/%s/home'>Página Inicial</a><br/>"
}


class Wiki(Document):
    user           = TextField() # usuário ou comunidade (registry_id)
                                 # esta chave era do bd antigo (???)
    registry_id    = TextField() # dono da página: usuário ou comunidade
    owner          = TextField() # quem criou.
                                 # caso wiki seja de uma comunidade, owner!=registry_id
    nomepag        = TextField(default=u"Nova Página")
    nomepag_id     = TextField(default="NovaPagina")

    tags           = ListField(TextField())
    data_cri       = TextField()
    comentarios    = ListField(DictField())
    #    Schema.build(
    #                            owner    = TextField(),
    #                            comment  = TextField(),
    #                            data_cri = TextField()
    #                     )

    is_folder       = TextField(default="N") # "S" ou "N": indica se esta entrada corresponde a uma pasta ou página
    parent_folder   = TextField(default="")  # "" indica que esta entrada está na raiz (não tem pasta pai)
    folder_items    = ListField(TextField())
    
    """ somente folders """
    data_alt       = TextField()    # somente folders possuem data_alt
    alterado_por   = TextField()    # somente folders possuem alterado_por

    """ somente páginas """
    historico = ListField(DictField())
    #    somente páginas possuem histórico
    #    Schema.build(
    #                    conteudo       = TextField(),
    #                    data_alt       = TextField(),
    #                    alterado_por   = TextField()
    #                 )
    
    
    @classmethod
    def listFolderPages(self, user, registry_id, folder, page, page_size, only_removed=False):
        # chamadas:
        # only_removed = False
        # /wiki/%s -> lista pastas e páginas não removidas do registry_id
        # only_removed = True
        # /wiki/deleted/%s -> lista todas as páginas removidas
        paginas = []
        if only_removed:
            for row in database.WIKI.view('wiki/removed_data',startkey=[registry_id, {}],endkey=[registry_id], \
                                          descending="true", skip=(page-1)*page_size , limit=page_size):
                  (registry_id, data_alt, doc_id) = row.key
                  pagina_data = dict()
                  pagina_data.update(row.value)
                  pagina_data["registry_id"]  = registry_id
                  pagina_data["doc_id"]       = doc_id
                  paginas.append(pagina_data)
        else:
            for row in database.WIKI.view('wiki/folder_data',startkey=[registry_id, folder, {}],endkey=[registry_id, folder], \
                                          descending="true", skip=(page-1)*page_size , limit=page_size):
                  (registry_id, folder, data_alt, doc_id) = row.key
                  
                  pagina_data = dict()
                  pagina_data.update(row.value)
                  
                  pagina_data["registry_id"]  = registry_id
                  pagina_data["doc_id"]       = doc_id
                  paginas.append(pagina_data)
                          
        return paginas

    @classmethod
    def listPortfolio(self, user, registry_id, page, page_size):
        # chamadas:
        # /wiki/portfolio/%s -> lista todas as páginas de todas as pastas
        paginas = []
        for row in database.WIKI.view('wiki/portfolio',startkey=[registry_id, {}],endkey=[registry_id], \
                                      descending="true", skip=(page-1)*page_size, limit=page_size):
              (registry_id, data_alt, doc_id) = row.key
              
              if isAllowedToReadObject(user, "wiki", registry_id, doc_id):
                  # listagem das pastas e páginas não removidas 
                  pagina_data = dict()
                  pagina_data.update(row.value)
                  pagina_data["registry_id"]  = registry_id
                  pagina_data["doc_id"]       = doc_id
                  
                  pagina_data["data_alt"]     = short_datetime(row.value["data_alt"], include_year=True)
                  pagina_data["data_nofmt"]   = row.value["data_alt"]
                  
                  paginas.append(pagina_data)
                          
        return paginas

    @classmethod
    def listWikiFolders(self, registry_id):
        folders = [("", "/")]
        for row in database.WIKI.view("wiki/partial_data",startkey=[registry_id],endkey=[registry_id, {}]):
              (registry_id, doc_id) = row.key
              if row.value["is_folder"]=="S":
                  folders.append((row.value["nomepag_id"], str_limit(row.value["nomepag"], 50)))
                          
        #folders = sorted(folders, key=itemgetter("data_nofmt"), reverse = True)
        return folders

    @classmethod
    def listWikiFolderItens(self, registry_id, encoding='utf-8'):
        folders = {}
        foldernames = {}
        for row in database.WIKI.view('wiki/folder_itens',startkey=[registry_id],endkey=[registry_id, {}]):
              (registry_id, folder) = row.key
              if encoding=='iso-8859-1':
                  folder = folder.encode('iso-8859-1')
                  folders[folder] = [ item.encode('iso-8859-1') for item in row.value["folder_items"] ]
                  foldernames[folder] = row.value["nomepag"]
              else:
                  folders[folder] = row.value["folder_items"]
                  foldernames[folder] = row.value["nomepag"]
                          
        return (folders, foldernames)

    @classmethod
    def nomepagExists(self, registry_id, nomepag):
        # Verifica se já existe algum item (página ou pasta) cadastrado com um determinado nome
        return (database.WIKI.view('wiki/nomepag_exists',startkey=[registry_id,nomepag],endkey=[registry_id,nomepag, {}]))
    
    
    """
    @classmethod
    def getNomepag(self, registry_id, nomepag_id):
        if nomepag_id == "":
            # pasta raiz
            return "/"
        doc_id = registry_id+"/"+nomepag_id
        _wiki = Wiki().retrieve(doc_id)
        if _wiki:
            # nome da página/pasta
            return _wiki.nomepag
        else:
            # página/pasta não encontradas
            return ""
    """
    
        
    @classmethod 
    def countRootFolderPages(self, registry_id):
        for row in database.WIKI.view('wiki/count_rootpages',key=registry_id, group="true"):
            return row.value
        return 0

    @classmethod 
    def countRemovedPages(self, registry_id):
        for row in database.WIKI.view('wiki/count_removedpages',key=registry_id, group="true"):
            return row.value
        return 0
        
    def countFolderPages(self):
        return len(self.folder_items)

    @classmethod 
    def countPortfolioPages(self, registry_id):
        for row in database.WIKI.view('wiki/count_portfolio',key=registry_id, group="true"):
            return row.value
        return 0
               
    def getPagePath(self, links=True, includefolder=True, includepage=False):
        # links: indica se o path deve conter links html para cada item do path
        # includefolder: indica se, caso o item seja um folder, deve retornar o caminho até o item inclusive.
        path = ""
        
        no = self
        folder = None
        folder_id = None
        while no.parent_folder != "":
            if folder_id != None:
                if links:
                    path = "<a href='/wiki/%s?folder=%s'>%s</a>/" % (no.registry_id, folder_id, folder) + path
                else:
                    path = folder + "/" + path
            no = Wiki().retrieve(no.registry_id+"/"+no.parent_folder)
            folder_id = no.nomepag_id
            folder = no.nomepag
        if folder_id != None:
            if links:
                path = "<a href='/wiki/%s?folder=%s'>%s</a>/" % (no.registry_id, folder_id, folder) + path
            else:
                path = folder + "/" + path
        if links:
            path = "/<a href='/wiki/%s'>%s</a>/"%(no.registry_id,no.registry_id) + path
        else:
            path = "/" + no.registry_id + "/" + path
            
        if includefolder and self.is_folder=="S":
            # se o item é um folder, retorna o caminho até o item (inclusive)
            if links:
                path = path + "<a href='/wiki/%s?folder=%s'>%s</a>" % (no.registry_id, self.nomepag_id, self.nomepag)
            else:
                path = path + self.nomepag
                
        if includepage and self.is_folder=="N":
            # se o item não é um folder, retorna o caminho até a página (inclusive)
            if links:
                path = path + "<a href='/wiki/%s/%s'>%s</a>" % (no.registry_id, self.nomepag_id, self.nomepag)
            else:
                path = path + self.nomepag
                                
        return path


    def getDescendentsList(self):
        lista_desc = []
        no = self
        if no.is_folder=="S":
            lista_desc.append((no.nomepag_id, no.nomepag))
        
            for item in no.folder_items:
                no = Wiki().retrieve(no.registry_id+"/"+item)
                filhos = no.getDescendentsList()
                if filhos: lista_desc.extend(filhos)
        return lista_desc


    def getWikiPage(self, user, versao=-1):
        if versao > len(self.historico)-1:
            versao = -1
        
        # recupera dados no BD
        wiki_data = dict(
                registry_id    = self.registry_id,
                owner          = self.owner,
                nomepag        = self.nomepag,
                nomepag_id     = self.nomepag_id,
                conteudo       = self.historico[versao]["conteudo"],
                tags           = self.tags,
                data_cri       = self.data_cri,
                data_alt       = self.historico[versao]["data_alt"],
                alterado_por   = self.historico[versao]["alterado_por"],
                comentarios    = self.comentarios,
        )

        wiki_data["pag"]      = self.id
        return wiki_data


    def getWikiHistory(self):
        # recupera dados no BD
        wiki_data = dict(
                registry_id    = self.registry_id,
                owner          = self.owner,
                nomepag        = self.nomepag,
                nomepag_id     = self.nomepag_id,
                historico      = []
        )

        for i in range(len(self.historico)):
            wiki_data["historico"].append(dict(
                versao         = str(i),
                data_alt       = short_datetime(self.historico[i]["data_alt"]),
                alterado_por   = self.historico[i]["alterado_por"]
                ))
        wiki_data["historico"].reverse()
        return wiki_data
    
    
    def restoreVersion (self, versao):
        self.historico.append(dict(
            conteudo       = self.historico[versao]["conteudo"],
            data_alt       = self.historico[versao]["data_alt"],
            alterado_por   = self.historico[versao]["alterado_por"]
            ))
        self.save()
        
        # recria tags do documento restaurado se ele foi removido anteriormente
        if self.historico[-2]["conteudo"] == _CONTEUDO_REMOVIDO:
            for tag in self.tags:
                addTag(tag, self.registry_id, self.owner, "wiki", self.id, self.nomepag, self.historico[-1]["data_alt"])        
        
        
    def removeItemFromParent(self, user, item):
        self.folder_items.remove(item)
        self.data_alt = str(datetime.now())
        self.alterado_por = user
                    
        self.save()
        

    def addItemToParent(self, user, item):
        self.folder_items.append(item)
        self.data_alt = str(datetime.now())
        self.alterado_por = user
        self.save()
        
        
    def moveWiki (self, registry_id, user, old_parent, new_parent):
        self.parent_folder = new_parent
        self.save()
        
        if old_parent:
            old = Wiki().retrieve(registry_id+"/"+old_parent)
            old.removeItemFromParent(user, self.nomepag_id)
        
        if new_parent:
            new = Wiki().retrieve(registry_id+"/"+new_parent)
            new.addItemToParent(user, self.nomepag_id)
        
    def createInitialPage (self, nome_pag, registry_id, owner):
        doc_id = registry_id + "/" + nome_pag
        self.user = registry_id
        self.owner = owner
        self.edicao_publica = "N" if owner==registry_id else "S"
        self.registry_id = registry_id
        self.nomepag_id = nome_pag
        self.nomepag = _NOMEPAG_DEFAULT[nome_pag]
        
        self.historico = [ dict(
                                conteudo = _CONTEUDO_DEFAULT[nome_pag] % registry_id,
                                data_alt = str(datetime.now()),
                                alterado_por = self.owner
                                ) ]
        self.tags = []
        self.data_cri = self.historico[-1]["data_alt"]
        self.saveWiki(id=doc_id)


    def saveWiki(self, id=None, old_tags=None):
        if id==None:
            self.save()
        else:
            self.save(id=id)
        
        # folders não possuem tags
        if self.is_folder!="S":
            # compara as tags anteriores com as modificadas, atualizando a lista de tags no BD
            data_tag = str(datetime.now())
            for tag in self.tags:
                if old_tags==None or tag not in old_tags:
                    addTag(tag, self.registry_id, self.owner, "wiki", self.id, self.nomepag, data_tag)
    
            if old_tags != None:
                for tag in old_tags:
                    if tag not in self.tags:
                        removeTag(remove_diacritics(tag.lower()), "wiki", self.id)
    
    
    def deleteWiki(self, user, permanently=False):
        registry_id = self.registry_id
        nomepag_id = self.nomepag_id
        parent = self.parent_folder
        tags = self.tags

        if permanently or self.is_folder=="S":
            # se é um folder, remove-o
            self.delete()
        else:
            # se é uma página, cria entrada no histórico marcando a página como removida
            self.historico.append(dict(
                                       conteudo=_CONTEUDO_REMOVIDO,
                                       alterado_por=user,
                                       data_alt=str(datetime.now())
                            ))
            
            # toda página removida vai para a pasta raiz
            self.parent_folder = ""
            
            self.save()
        
            #remove as tags
            for tag in tags:
                removeTag(remove_diacritics(tag.lower()), "wiki", self.id)

            # remove da lista de filhos do pai
            if parent:
                parent_obj = Wiki().retrieve(registry_id+"/"+parent)
                parent_obj.removeItemFromParent(user, nomepag_id)

    
    def newWikiComment(self, owner, comment):
        self.comentarios.append(dict(
                                  owner = owner,
                                  comment = comment,
                                  data_cri = str(datetime.now())
                                ))
        self.save()
    
    def deleteWikiComment(self, owner, data_cri):
        for row in database.WIKI.view('wiki/comment',key=[self.id, owner, data_cri]):
            comentario = dict()
            comentario["comment"] = row.value
            comentario["data_cri"] = data_cri
            comentario["owner"] = owner
            
            self.comentarios.remove(comentario)
            self.save()
            return True
        return False
    
    def save(self, id=None, db=database.WIKI):
        if not self.id and id: self.id = id
        self.store(db)
        
    def retrieve(self, id, db=database.WIKI, include_removed=False):
        wk = Wiki.load(db, id)
        if wk:
            if include_removed or wk.is_folder=="S":
                return wk
            elif wk.historico[-1]["conteudo"] != _CONTEUDO_REMOVIDO:
                return wk
            else:
                return None
        else:
            return None
        
    def delete(self, db=database.WIKI):
        #db.delete(self)
        del db[self.id]
        
        
        
