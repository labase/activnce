# -*- coding: utf-8 -*-
"""
################################################
Plataforma ActivUFRJ
################################################

:Author: *Fernando de Mesentier Silva*
:Contact: fms2005@gmail.com
:Date: $Date: 2010/09/14  $
:Status: This is a "work in progress"
:Revision: $Revision: 0.01 $
:Home: `LABASE `__
:Copyright: ©2009, `GPL 
"""
from couchdb import Server
from config import COUCHDB_URL
from couchdb.design import ViewDefinition

from datetime import datetime, timedelta
from uuid import uuid4

from libs.dateformat import human_date
from libs.strformat import valid_latin1

_DOCBASES = ['tags']

_EMPTYTAG = lambda:dict(
    # _id = <couchdb_id>
    tag = "",
    texto = "",     # Texto onde a tag se encontra. Utilizado no resultado da busca.
    registry_id = "",
    owner = "",
    tipo = "",	    # community/wiki/blog/user/mblog/file
    objeto = "",
    data_cri = ""
)


# Cache do Tagcloud
_CACHE_TAGCLOUD = dict()
_CACHE_EXP_DATE = dict()

# Palavras ignoradas na lista de tags
STOPWORDS = ['de', 'a', 'o', 'que', 'e', 'do', 'da', 'em', 'um', 'para', 'com', u'não', 'uma', 'os', 'no', 'se', 'na', 'por', 'mais', 'as',
             'dos', 'como', 'mas', 'ao', 'ele', 'das', u'à', 'seu', 'sua', 'ou', 'quando', 'muito', 'nos', u'já', 'eu', 
             u'também', u'só', 'pelo', 'pela', u'até', 'isso', 'ela', 'entre', 'depois', 'sem', 'mesmo', 'aos', 'seus', 'quem', 
             'nas', 'me', 'esse', 'eles', u'você', 'essa', 'num', 'nem', 'suas', 'meu', u'às', 'minha', 'numa', 'pelos', 
             'elas', 'qual', u'nós', 'lhe', 'deles', 'essas', 'esses', 'pelas', 'este', 'dele', 'tu', 'te', u'vocês', 'vos', 
             'lhes', 'meus', 'minhas', 'teu', 'tua', 'teus', 'tuas', 'nosso', 'nossa', 'nossos', 'nossas', 'dela', 'delas', 'esta', 'estes',
             'estas', 'aquele', 'aquela', 'aqueles', 'aquelas', 'isto', 'aquilo',
             'estou', u'está', 'estamos', u'estão', 'estive', 'esteve', 'estivemos', 'estiveram', 'estava', u'estávamos', 
             'estavam', 'estivera', u'estivéramos', 'esteja', 'estejamos', 'estejam', 'estivesse', u'estivéssemos', 'estivessem', 
             'estiver', 'estivermos', 'estiverem', 'hei', u'há', 'havemos', u'hão', 'houve', 'houvemos', 'houveram', 'houvera', 
             u'houvéramos', 'haja', 'hajamos', 'hajam', 'houvesse', u'houvéssemos', 'houvessem', 'houver', 'houvermos', 'houverem', 
             'houverei', u'houverá', 'houveremos', u'houverão', 'houveria', u'houveríamos', 'houveriam', 'sou', u'é', 'somos', 
             u'são', 'era', u'éramos', 'eram', 'fui', 'foi', 'fomos', 'foram', 'fora', u'fôramos', 'seja', 'sejamos', 'sejam', 
             'fosse', u'fôssemos', 'fossem', 'for', 'formos', 'forem', 'serei', u'será', 'seremos', u'serão', 'seria', 
             u'seríamos', 'seriam', 'tenho', 'tem', 'temos', u'têm', 'tinha', u'tínhamos', 'tinham', 'tive', 'teve', 'tivemos', 
             'tiveram', 'tivera', u'tivéramos', 'tenha', 'tenhamos', 'tenham', 'tivesse', u'tivéssemos', 'tivessem', 'tiver', 'tivermos', 
             'tiverem', 'terei', u'terá', 'teremos', u'terão', 'teria', u'teríamos', 'teriam']

def validTag(tag):
    return all(valid_latin1(ord(char)) for char in tag)

def splitTags (strTags):
    if not strTags:
        return []
    
    strTags = strTags.lower()
    listWords = list(set(strTags.split(',')))
    
    listTags=[]
    for word in listWords:
        if word not in STOPWORDS:
            word = word.lstrip("#")
    
            new_word = ''
            for i in range(len(word)):
                if valid_latin1(ord(word[i])):
                    new_word = new_word + word[i]

            listTags.append(new_word)
    
    return list(set(listTags))

def formatTags(tags):
    return ",".join(tags)

def addTag(tag, registry_id, owner, tipo, objeto, texto, data_tag):
    tag_data = _EMPTYTAG()
    tag_data["tag"] = tag
    tag_data["registry_id"] = registry_id
    tag_data["owner"] = owner
    tag_data["tipo"] = tipo
    tag_data["objeto"] = objeto
    tag_data["texto"] = texto
    tag_data["data_cri"] = data_tag
    
    tag_id = uuid4().hex
    tag_data["_id"] = tag_id
    TAGS[tag_id] = tag_data
    #print "addTag: ", tag_id
    
def removeTag(tag, tipo, objeto):
    for row in TAGS.view('search/searchtags',key=[tag,tipo,objeto]):
        tag_id = row.value["tag_id"]
        del TAGS[tag_id]
        #print "removeTag: ", tag_id
        
def findTag(tag):
    resultado = {}
    for row in TAGS.view('search/searchtags',startkey=[tag], endkey=[tag, {}]):
        (tag, tipo, objeto) = row.key
        if tipo not in resultado:
            resultado[tipo] = []
        resultado[tipo].append((row.value["texto"], row.value["owner"], row.value["registry_id"], objeto, row.value["data_cri"], human_date(row.value["data_cri"])))   
    return resultado
   
def cloudTag(registry_id=""):
    if registry_id:
        # obtem todas as tags de um registry_id
        if registry_id in _CACHE_TAGCLOUD and registry_id in _CACHE_EXP_DATE and \
           _CACHE_EXP_DATE[registry_id] > datetime.now():
            # retorna a cloudtag do cache se ela não estiver expirada
            return _CACHE_TAGCLOUD[registry_id]
        
        # obtem a cloudtag no banco definindo a expiração para daqui a 30 minutos
        _CACHE_TAGCLOUD[registry_id] = dict()
        _CACHE_EXP_DATE[registry_id] = datetime.now() + timedelta(minutes=30)
        for row in TAGS.view('search/tagcloud',startkey=[registry_id], endkey=[registry_id, {}], group="true"):
            _CACHE_TAGCLOUD[registry_id][row.key[1]] = row.value
        
        return _CACHE_TAGCLOUD[registry_id]
            
    else:
        # chamada sem passar o registry_id obtem todas as tags de todos os usuários para o autocomplete
        # não precisa fazer cache pois a chamada é feita a partir de uma thread
        resultado = dict()
        for row in TAGS.view('search/tagcloud', group="true"):
            try:
                tag = row.key[1].encode('iso-8859-1')
                resultado[tag] = row.value 
            except Exception as detail:
                # ignora tag com erro (caracteres inválidos)
                #print "tag com erro:", row.key[1]
                pass
                 
        return resultado
   

def userTag(registry_id, tag):
    resultado = {}
    for row in TAGS.view('search/usertag',key=[registry_id, tag]):
        if row.value["tipo"] not in resultado:
            resultado[row.value["tipo"]] = []
        resultado[row.value["tipo"]].append((row.value["texto"], row.key[0], row.value["registry_id"], row.value["objeto"], row.value["data_cri"], human_date(row.value["data_cri"])))
            
    return resultado


def removeUserTags(registry_id):
    """ Remove todas as tags de registry_id """
    for row in TAGS.view('search/usertag',startkey=[registry_id], endkey=[registry_id, {}]):
        tag_id = row.value["tag_id"]
        del TAGS[tag_id]        



class Activ(Server):
    "Active database"
    tags = {}

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
TAGS = __ACTIV.tags




# Agrupa as tags por: tag e tipo 
# Retorna objeto onde a tag foi usada.

search_searchtags = ViewDefinition('search','searchtags', \
                          u'''
                          function(doc) { 
                            String.prototype.removeDiacritics = function() {
                                var diacritics = [
                                    [/[\300-\306]/g, 'A'],
                                    [/[\340-\346]/g, 'a'],
                                    [/[\310-\313]/g, 'E'],
                                    [/[\350-\353]/g, 'e'],
                                    [/[\314-\317]/g, 'I'],
                                    [/[\354-\357]/g, 'i'],
                                    [/[\322-\330]/g, 'O'],
                                    [/[\362-\370]/g, 'o'],
                                    [/[\331-\334]/g, 'U'],
                                    [/[\371-\374]/g, 'u'],
                                    [/[\321]/g, 'N'],
                                    [/[\361]/g, 'n'],
                                    [/[\307]/g, 'C'],
                                    [/[\347]/g, 'c'],
                                ];
                                var s=this;
                                for (var i = 0; i < diacritics.length; i++) {
                                    s = s.replace(diacritics[i][0], diacritics[i][1]);
                                }
                                return s;
                            }
                          
                             emit([doc.tag.toLowerCase().removeDiacritics(),doc.tipo,doc.objeto],
                                  {"tag_id":doc._id,
                                   "texto":doc.texto,
                                   "owner":doc.owner,
                                   "registry_id":doc.registry_id,
                                   "data_cri":doc.data_cri});
                          }
                          ''')

# Totaliza numero de utilizações de uma tag por registry_id.
# Retorna total.

search_tagcloud = ViewDefinition('search','tagcloud', \
                          u'''
                          function(doc) { 
                             emit([doc.registry_id,doc.tag], 1); 
                             if (doc.registry_id != doc.owner) {
 							     emit([doc.owner,doc.tag], 1); 
                             }
                          }
                          ''',
                          u'''
                          function(keys, values) {
                             return sum(values);
                          }
                          ''')


search_usertag = ViewDefinition('search','usertag', \
                          u'''
                          function(doc) { 
                            String.prototype.removeDiacritics = function() {
                                var diacritics = [
                                    [/[\300-\306]/g, 'A'],
                                    [/[\340-\346]/g, 'a'],
                                    [/[\310-\313]/g, 'E'],
                                    [/[\350-\353]/g, 'e'],
                                    [/[\314-\317]/g, 'I'],
                                    [/[\354-\357]/g, 'i'],
                                    [/[\322-\330]/g, 'O'],
                                    [/[\362-\370]/g, 'o'],
                                    [/[\331-\334]/g, 'U'],
                                    [/[\371-\374]/g, 'u'],
                                    [/[\321]/g, 'N'],
                                    [/[\361]/g, 'n'],
                                    [/[\307]/g, 'C'],
                                    [/[\347]/g, 'c'],
                                ];
                                var s=this;
                                for (var i = 0; i < diacritics.length; i++) {
                                    s = s.replace(diacritics[i][0], diacritics[i][1]);
                                }
                                return s;
                            }

                             emit([doc.registry_id,doc.tag.toLowerCase().removeDiacritics()],
                                      {"tag_id":doc._id,
                                       "texto":doc.texto,
                                       "objeto":doc.objeto,
                                       "registry_id":doc.registry_id,
                                       "tipo":doc.tipo,
                                       "data_cri":doc.data_cri});
                             if (doc.registry_id != doc.owner) {
                                  emit([doc.owner,doc.tag.toLowerCase().removeDiacritics()], 
                                          {"tag_id":doc._id,
                                           "texto":doc.texto,
                                           "objeto":doc.objeto,
                                           "registry_id":doc.registry_id,
                                           "tipo":doc.tipo,
                                           "data_cri":doc.data_cri}); 
                             }
                          }
                          ''')



ViewDefinition.sync_many(TAGS, [search_searchtags, \
                                search_tagcloud, \
                                search_usertag])
