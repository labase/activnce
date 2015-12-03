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

from couchdb import Server


_DOCBASES = ['registry']


"""
Corrige os valores dos atributos 'privacidade' e 'participacao' dos documentos do REGISTRY.
Em alguns casos 'Publica' estava sem acento.
"""


class Activ(Server):
    "Active database"
    
    def __init__(self, url):
        print "iniciando a conversão..."
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
REGISTRY = __ACTIV.registry


def main():

    for item in REGISTRY:
        if item.startswith("_design/"):
            continue

        registry_data = {}
        registry_data.update(REGISTRY[item])
        salvar = False
        
        if registry_data['privacidade'] == "Publica" or registry_data['privacidade'] == "":
            print "privacidade corrigida: ", item
            registry_data['privacidade'] = u"Pública"
            salvar = True
            
        elif registry_data['privacidade'] != u"Pública" and registry_data['privacidade'] != u"Privada":
            print "privacidade incorreta: %s (%s)" % (item, registry_data['privacidade'])
            
        if registry_data["type"] == "community":
            if registry_data["participacao"] == "":
                print "participacao corrigida: ", item
                registry_data['participacao'] = "Mediante Convite"
                salvar = True
            elif registry_data['participacao'] not in ["Mediante Convite", u"Voluntária", u"Obrigatória"]:
                print "participacao incorreta: %s (%s)" % (item, registry_data['participacao'])

        #if salvar:            
        #    REGISTRY[item] = registry_data
                
    print "fim do processamento."


if __name__ == "__main__":
    main()