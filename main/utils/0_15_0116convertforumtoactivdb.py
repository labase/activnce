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

from uuid import uuid4

from couchdb import Server


_DOCBASES = ['forum', 'activdb']

_EMPTYTOPIC= lambda: dict(
    #_id            = <couchdb_id>
    type           = "", # tipo do documento: member, community, wiki, etc
    subtype        = "",
    service        = "", # nome do serviço: wiki,file,blog,etc  (precisa existir ??? ou pode usar somente type/subtype ???)
    registry_id    = "", # usuário ou comunidade onde está localizado o objeto
    name_id        = "", # identificador do objeto (nome do objeto sem caracteres especiais)
    titulo         = "",
    owner          = "",           # usuário que criou o objeto
    tags           = [],
    group_id       = "",
    data_cri       = "",
    data_alt       = "",
    alterado_por   = "",

    conteudo          = "",
    receber_email     = "N", # "S" ou "N" se o dono do tópico recebe ou não emails em cada post
    ultimo_reply      = "",
) 
    
        
_EMPTYREPLY= lambda: dict(
    #_id            = <couchdb_id>
    type           = "", # tipo do documento: member, community, wiki, etc
    subtype        = "",
    service        = "", # nome do serviço: wiki,file,blog,etc  (precisa existir ??? ou pode usar somente type/subtype ???)
    registry_id    = "", # usuário ou comunidade onde está localizado o objeto
    name_id        = "", # identificador do objeto (nome do objeto sem caracteres especiais)
    titulo         = "",
    owner          = "",           # usuário que criou o objeto
    tags           = [],
    group_id       = "",
    data_cri       = "",
    data_alt       = "",
    alterado_por   = "",    

    conteudo        = "",
)    
    
    
    
class Activ(Server):
    "Active database"
    
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


__ACTIV = Activ('http://127.0.0.1:5984/')
FORUM = __ACTIV.forum
ACTIVDB = __ACTIV.activdb

def exists(service, type, registry_id, name_id):
    print "testando se existe %s, %s, %s, %s" % (service, type, registry_id, name_id)
    
    if ACTIVDB.view('object/exists', key=[service, type, registry_id, name_id]):
        return True
    else:
        return False
        
def remove_diacritics(str):
    special_chars = [u'à', u'á', u'ã', u'â', u'À', u'Á', u'Ã', u'Â',\
                     u'é', u'ê', u'É', u'Ê',\
                     u'í', u'Í', \
                     u'ó', u'õ', u'ô', u'Ó',u'Õ', u'Ô', \
                     u'ú', u'ü', u'Ú', u'Ü', \
                     u'ç', u'Ç' ]
    chars = ['a', 'a', 'a', 'a', 'A', 'A', 'A', 'A',\
             'e', 'e', 'E', 'E',\
             'i',  'I', \
             'o', 'o', 'o', 'O', 'O', 'O', \
             'u', 'u', 'U', 'U', \
             'c', 'C' ]

    for i in range(len(special_chars)):
        str=str.replace(special_chars[i], chars[i])
           
    return str


def remove_special_chars(str):
    strnew = ""
    for i in range(len(str)):
        if (str[i]>="A" and str[i]<="Z") or\
           (str[i]>="a" and str[i]<="z") or\
           (str[i]>="0" and str[i]<="9") or\
           (str[i]=="-") or\
           (str[i]=="_") or\
           (str[i]=="."):
            strnew += str[i]
            
    return strnew


def main():
    print ">>> iniciando a conversão..."
    print 
    
    conversion_receber_email = {"yes": "Y", "no": "N"}
    
    for registry_id in FORUM:
        if "_design" not in registry_id:
            print "registry_id=", registry_id
            for old_topic in FORUM[registry_id]["topics"]:
                print u"topico original = ", old_topic["title"]
                if "dt_creation_post" not in old_topic:
                    print u">>> topico ignorado (sem dt_creation_post)."
                    continue
                
                new_topic = _EMPTYTOPIC()
                new_topic["service"]        = "forum"
                new_topic["type"]           = "topic"
                new_topic["subtype"]        = None
                new_topic["registry_id"]    = registry_id
                
                new_topic["name_id"]        = remove_special_chars(remove_diacritics(old_topic["title"].replace(" ","_")))
                if new_topic["name_id"] == "":
                    print u">>> topico ignorado (erro na conversão do name_id)."
                    continue
                
                i=0
                name_id_base = new_topic["name_id"]
                while exists("forum", "topic", registry_id, new_topic["name_id"]):
                    i=i+1
                    new_topic["name_id"] = "%s_%s" % (name_id_base, str(i))
                    print u"conflito no nome: name_id utilizado %s" % new_topic["name_id"]
                    
                new_topic["titulo"]         = old_topic["title"]
                new_topic["owner"]          = old_topic["owner"]
                new_topic["tags"]           = []
                new_topic["group_id"]       = None
                new_topic["data_cri"]       = old_topic["dt_creation_post"]
                new_topic["data_alt"]       = new_topic["data_cri"]
                new_topic["alterado_por"]   = old_topic["owner"]
            
                new_topic["conteudo"]       = old_topic["content"]
                if old_topic["receber_email"] not in conversion_receber_email.keys():
                    old_topic["receber_email"] = "no"
                new_topic["receber_email"]  = conversion_receber_email[old_topic["receber_email"]] 
                
                new_topic["ultimo_reply"]   = None
                if old_topic["posts"]:
                    new_topic["ultimo_reply"]   = old_topic["posts"][-1]["data"]
                
                topic_id = uuid4().hex
                #ACTIVDB[topic_id] = new_topic
                print u"topico convertido (%s) = %s" % (topic_id, new_topic)
                    
                for old_reply in old_topic["posts"]:
                    print u"   reply original = ", old_reply

                    new_reply = _EMPTYREPLY()
                    new_reply["service"]        = "forum"
                    new_reply["type"]           = "reply"
                    new_reply["subtype"]        = None
                    new_reply["registry_id"]    = registry_id
                    new_reply["name_id"]        = None
                    new_reply["titulo"]         = old_reply["title"]
                    new_reply["owner"]          = old_reply["owner"]
                    new_reply["tags"]           = []
                    new_reply["group_id"]       = topic_id
                    new_reply["data_cri"]       = old_reply["data"]
                    new_reply["data_alt"]       = new_reply["data_cri"]
                    new_reply["alterado_por"]   = old_reply["owner"]
                
                    new_reply["conteudo"]       = old_reply["message"]

                    reply_id = uuid4().hex
                    #ACTIVDB[reply_id] = new_reply
                    print u"   reply convertido (%s) = %s" % (reply_id, new_reply)
            print
            
    print ">>> fim do processamento..."


if __name__ == "__main__":
    main()