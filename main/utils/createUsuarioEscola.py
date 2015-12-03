from couchdb import Server

_DOCBASES = ['registry', 'usuarios_escola']

_EMPTYUSERSCHOOL = {
        "professor" : [],
        "gestor" : [],
        "aluno" : [],
        "super_usuario" : [],
        "usuario_convidado" : [],
        "comunidade" : []
}


class Activ(Server):
    "Active database"
    
    def __init__(self, url):
        print "Iniciando..."
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
USERSCHOOL = __ACTIV.usuarios_escola


def addUserSchool(nome, tipo, escola):
    if escola not in USERSCHOOL:
        school_data = {}
        school_data = _EMPTYUSERSCHOOL
        USERSCHOOL[escola] = school_data
    
    if tipo in _EMPTYUSERSCHOOL and nome not in USERSCHOOL[escola][tipo]:
        school_data = {}
        school_data = USERSCHOOL[escola]
        school_data[tipo].append(nome)
        USERSCHOOL[escola] = school_data
        
        return True
    else:
        return False

def main():
    for registro in REGISTRY:
        if "cod_institute" in REGISTRY[registro] and REGISTRY[registro]["cod_institute"] != "":
            intersecao = list(set(REGISTRY[registro]["papeis"]) & set(_EMPTYUSERSCHOOL))
            if intersecao != []:
                for papel in intersecao:
                    if addUserSchool(registro, papel, REGISTRY[registro]["cod_institute"]):
                        print "usuario " + registro + " adicionado a escola " + REGISTRY[registro]["cod_institute"] + " com papel " + papel
    
    print "FIM!"

if __name__ == "__main__":
    main()
