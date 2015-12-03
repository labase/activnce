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
import pymssql


_DOCBASES = ['registry', 'dbintranet']


"""
Cria lista de vínculos de todos os usuários do registry
buscando as informações na intranet/ufrj.
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
REGISTRY   = __ACTIV.registry
DBINTRANET = __ACTIV.dbintranet


def main():

    # conecta com a intranet
    dbinfo = {}
    dbinfo.update(DBINTRANET["intranet"])
    
    try:
        conn = pymssql.connect(host=dbinfo["host"], user=dbinfo["user"], password=dbinfo["passwd"], database=dbinfo["database"])
    except Exception as e:
        print "Erro na conexao ao servidor de BD da Intranet."
        return
        
    # percorre o registry, atualizando cada usuário...
    for item in REGISTRY:
        if item.startswith("_design/"):
            continue

        registry_data = {}
        registry_data.update(REGISTRY[item])
        
        if registry_data["type"] == "member":
            registry_data["vinculos"] = []
                
            if "cpf" in registry_data and registry_data["cpf"]!="":
                where_clause = "identificacaoUFRJ='%s'" % registry_data["cpf"]
            else:
                where_clause = "Email='%s'" % registry_data["email"]
                
            # É professor ?
            cur = conn.cursor()
            cur.execute('''SELECT IdentificacaoUFRJ, MatriculaSiape, ativo, DescricaoLocal, Email FROM view_eh_professor
                           WHERE %s ''' % where_clause)
            row = cur.fetchone()
            while row:
                registry_data["vinculos"].append({"vinculo":"P", "instituicao":"UFRJ", "cpfufrj":row[0], "emailufrj": row[4], "ativo": row[2], "siape": row[1], 
                                                  "localizacao": row[3].strip().decode('iso-8859-1')})
                row = cur.fetchone()
            cur.close()
            
            # É funcionário ?
            cur = conn.cursor()
            cur.execute('''SELECT IdentificacaoUFRJ, MatriculaSiape, ativo, DescricaoLocal, Email FROM view_eh_tec_adm
                           WHERE %s ''' % where_clause)
            row = cur.fetchone()
            while row:
                registry_data["vinculos"].append({"vinculo":"F", "instituicao":"UFRJ", "cpfufrj":row[0], "emailufrj": row[4], "siape": row[1], "ativo": row[2], 
                                                  "localizacao": row[3].strip().decode('iso-8859-1')})
                row = cur.fetchone()
            cur.close()
            
            # É aluno de graduação ?
            cur = conn.cursor()
            cur.execute('''SELECT IdentificacaoUFRJ, registroSIRA, ativo, nome, Email FROM view_eh_aluno_grad
                           WHERE %s ''' % where_clause)
            row = cur.fetchone()
            while row:
                registry_data["vinculos"].append({"vinculo":"A", "instituicao":"UFRJ", "tipo": "Grad", "cpfufrj":row[0], "emailufrj": row[4], "dre": row[1], "ativo": row[2], 
                                                  "curso": row[3].strip().decode('iso-8859-1')})
                row = cur.fetchone()
            cur.close()
            
            # É aluno de pós-graduação ?
            cur = conn.cursor()
            cur.execute('''SELECT IdentificacaoUFRJ, registroSIRA, ativo, nome, Email FROM view_eh_aluno_pos
                           WHERE %s ''' % where_clause)
            row = cur.fetchone()
            while row:
                registry_data["vinculos"].append({"vinculo":"A", "instituicao":"UFRJ", "tipo": "Pos", "cpfufrj":row[0], "emailufrj": row[4], "dre": row[1], "ativo": row[2], 
                                                  "curso": row[3].strip().decode('iso-8859-1')})
                row = cur.fetchone()
            cur.close()
            
            print item, registry_data["vinculos"]
            
            #salva o documento
            #REGISTRY[item] = registry_data
                
    conn.close()        
    print "fim do processamento."


if __name__ == "__main__":
    main()