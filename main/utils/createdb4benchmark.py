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
import re
from uuid import uuid4

try:
  from couchdb.schema import Document, TextField, IntegerField, LongField, DateTimeField, DictField, ListField, Schema, FloatField
except ImportError:
  from couchdb.mapping import Document, TextField, IntegerField, LongField, DateTimeField, DictField, ListField, FloatField
  from couchdb.mapping import Mapping as Schema

_DOCBASES = ['jicblog', 'jicpost','jiccomments', 'jicdb']


class Activ(Server):
    
    
    def __init__(self, url):
        print "iniciando a verificação..."
        Server.__init__(self, url)
        act = self
        test_and_create = lambda db: db in act and act[db] or act.create(db)
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
BLOGJIC = __ACTIV.jicblog
POSTJIC = __ACTIV.jicpost
COMMENTSJIC = __ACTIV.jiccomments
JICDB = __ACTIV.jicdb

class Blog(Document):
    #_id           = <couchdb_id>   
    
    nome           = TextField()
    posts          = ListField(TextField())
#//cria _design in blogjic
    def retrieve(self, id, db=BLOGJIC):
        # retorna um objeto da classe ActivDB
        # para converter para um objeto correspondente ao tipo armazenado no atributo type, sobreescreva essa método
        return Blog.load(db, id)

    
    def save(self, id=None, db=BLOGJIC):
        if not self.id and id: self.id = id
        self.store(db)

#//cria _design in jicdb
    def retrieveinJIC(self, id, db=JICDB):
        # retorna um objeto da classe ActivDB
        # para converter para um objeto correspondente ao tipo armazenado no atributo type, sobreescreva essa método
        return Blog.load(db, id)

    
    def saveinJIC(self, id=None, db=JICDB):
        if not self.id and id: self.id = id
        self.store(db)
        
class Post(Document):
    #_id           = <couchdb_id>   
    
    nome           = TextField()
    comments       = ListField(TextField())
    
#//cria _design in Postjic
    def retrieve(self, id, db=POSTJIC):
        # retorna um objeto da classe ActivDB
        # para converter para um objeto correspondente ao tipo armazenado no atributo type, sobreescreva essa método
        return Post.load(db, id)

    
    def save(self, id=None, db=POSTJIC):
        if not self.id and id: self.id = id
        self.store(db)
    
#//cria _deign in jicdb
    def retrieveinJIC(self, id, db=JICDB):
        # retorna um objeto da classe ActivDB
        # para converter para um objeto correspondente ao tipo armazenado no atributo type, sobreescreva essa método
        return Post.load(db, id)

    
    def saveinJIC(self, id=None, db=JICDB):
        if not self.id and id: self.id = id
        self.store(db)
        
class Comment(Document):
    #_id           = <couchdb_id>   
    
    nome           = TextField()
    
#//cria _design in commentjic  
    def retrieve(self, id, db=COMMENTSJIC):
        # retorna um objeto da classe ActivDB
        # para converter para um objeto correspondente ao tipo armazenado no atributo type, sobreescreva essa método
        return Comment.load(db, id)

    
    def save(self, id=None, db=COMMENTSJIC):
        if not self.id and id: self.id = id
        self.store(db)

#//cria _design in JICDB 
    def retrieveinJIC(self, id, db=JICDB):
        # retorna um objeto da classe ActivDB
        # para converter para um objeto correspondente ao tipo armazenado no atributo type, sobreescreva essa método
        return Comment.load(db, id)

    
    def saveinJIC(self, id=None, db=JICDB):
        if not self.id and id: self.id = id
        self.store(db)

class Pop:

    def popDBs(self):
        #//popula ['blogjic', 'postjic','commentsjic']
        
        #//Números de blogs
        I=1
        #//Número de posts por blog
        J=10
        #//Número de comentários por post em blog
        K=10
        
        #//vetor de posts a serem salvos em Blog().posts de um Blog() específico
        post_list=[]
        #//vetor de comentários a serem salvos em Post() de um Post() específico
        comment_list=[]
    
        #//Popula os DBs blogjic, postjic e commentjic
        for i in range(I):
            blog=Blog()
            for j in range (J):
                post=Post()
                for z in range (K):
                    comments=Comment()
                    c_id = uuid4().hex
                     
                    comments.nome = "comments"+" "+str((j+1)*(z+1))
                    comments.save(id=c_id)
                    comment_list.append(c_id)
                    
                
                p_id = uuid4().hex
                 
                post.nome = "post"+" "+str((j+1)*(i+1))
                post.comments= comment_list
                post.save(id=p_id)
                post_list.append(p_id)
                comment_list=[]             
        
            doc_id = uuid4().hex
            blog.posts = post_list
            blog.nome = "blog"+" "+str(i)
            blog.save(id=doc_id)
        print "registros criados em blogjic, postjic, commentsjic"
    
    def popJICDBs(self):
           #//popula ['jicdb']
        
        #//Números de blogs
        I=1
        #//Número de posts por blog
        J=10
        #//Número de comentários por post em blog
        K=10
        
        #//vetor de posts a serem salvos em Blog().posts de um Blog() específico
        post_list=[]
        #//vetor de comentários a serem salvos em Post() de um Post() específico
        comment_list=[]
        
        #//Popula o banco jicdb
        for i in range(I):
            blog=Blog()
            for j in range (J):
                post=Post()
                for z in range (K):
                    comments=Comment()
                    c_id = uuid4().hex
                     
                    comments.nome = "comments"+" "+str((j+1)*(z+1))
                    comments.saveinJIC(id=c_id)
                    comment_list.append(c_id)
                    
                
                p_id = uuid4().hex
                 
                post.nome = "post"+" "+str((j+1)*(i+1))
                post.comments= comment_list
                post.saveinJIC(id=p_id)
                post_list.append(p_id)
                comment_list=[]
            
            doc_id = uuid4().hex
            blog.posts = post_list
            blog.nome = "blog"+" "+str(i)
            blog.saveinJIC(id=doc_id)            
        print "registros criados  em jicdb"
    
def main():   
    hora_inicio = datetime.now()
    print "inicio=", hora_inicio
    
    pop=Pop()
    #//cria e/ou popula os bancos ['blogjic', 'postjic','commentsjic']
    pop.popDBs()
    
    #//cria e/ou popula o banco ['jicdb']
    pop.popJICDBs()

    hora_fim = datetime.now()
    print "criando db... %s -> %s = %s\n" % (str(hora_inicio), str(hora_fim), str(hora_fim-hora_inicio))

    # listando o blog com abordagem 1
    

    
    # listando o blog com abordagem 3
    
    
    
    print "Fim"

if __name__ == "__main__":
    main()