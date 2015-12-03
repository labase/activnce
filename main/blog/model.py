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

try:
  from couchdb.schema import Document, TextField, IntegerField, LongField, DateTimeField, DictField, ListField, Schema, FloatField
except ImportError:
  from couchdb.mapping import Document, TextField, IntegerField, LongField, DateTimeField, DictField, ListField, FloatField
  from couchdb.mapping import Mapping as Schema

from search.model import removeTag

import database
from database import _CONTEUDO_REMOVIDO
from libs.strformat import remove_html_tags, remove_diacritics, str_limit
from libs.dateformat import short_datetime
from datetime import datetime

"""
_EMPTYBLOG = lambda:dict(
# _id = "registry_id/nome_post"
          registry_id = ""    # dono do blog: usuário ou comunidade.
        , owner = ""          # quem postou.
                              # caso blog seja de uma comunidade, owner!=registry_id
        , titulo = "Novo Post"
        , post_id = ""        # identificador do post.
                              # é obtido a partir do título, extraíndo caracteres especiais,
                              # letras acentuadas e subtituindo espaços por _.
        , conteudo = "Entre aqui com o conteúdo do seu post. <br/>"
        , tags = []
        , data_cri = ""
        , data_alt = ""         # data da última alteração
        , alterado_por = ""     # quem alterou o post pela última vez
        , historico = []
     )


_EMPTYCOMMENT = lambda:dict(
# _id = "couchdb_id"
          registry_id = ""    # dono do blog  
        , owner = ""          # quem fez o comentário
        , post_id = ""        # post comentado
        , comment = "Entre aqui com o conteúdo do seu post. <br/>"
        , data_cri = ""
     )
"""

class Blog(Document):
    # _id = <registry_id>/<nome_post>
    registry_id    = TextField() # dono do blog: usuário ou comunidade
    owner          = TextField() # quem criou o blog.
                                 # caso blog seja de uma comunidade, owner!=registry_id
    titulo         = TextField(default=u"Novo Post")
    post_id        = TextField()
    conteudo       = TextField(default=u"Entre aqui com o conteúdo do seu post. <br/>")
    tags           = ListField(TextField())
    data_cri       = TextField()
    data_alt       = TextField()
    alterado_por   = TextField()
    historico      = ListField(DictField())

    @classmethod
    def get_blog_archive(self, registry_id):
        archive = dict()
        for row in database.BLOG.view('blog/archive',startkey=[registry_id,{}],endkey=[registry_id], descending="true"):
            ano = row.key[1]
            mes = row.key[2]
            data_cri = row.key[3]
            post_id = row.key[4]
            titulo = str_limit(row.value, 30)
            
            if ano not in archive:
                archive[ano] = {mes: [(post_id, titulo)]}
            elif mes not in archive[ano]:
                archive[ano][mes] = [(post_id, titulo)]
            else:
                archive[ano][mes].append ((post_id, titulo))
        return archive

    @classmethod    
    def listBlogPosts(self, registry_id, page, page_size, control_panel=False, only_removed=False):
        lista_posts = []
        
        if only_removed:
            for row in database.BLOG.view('blog/removed_data',startkey=[registry_id, {}],endkey=[registry_id], \
                                          descending="true", skip=(page-1)*page_size , limit=page_size):
                  (registry_id, data_alt, doc_id) = row.key
                  blog_data = dict()
                  blog_data.update(row.value)
                  blog_data["registry_id"]  = registry_id
                  blog_data["doc_id"]       = doc_id
                  lista_posts.append(blog_data)
        else:
            for row in database.BLOG.view('blog/all_data',startkey=[registry_id, {}], endkey=[registry_id], descending="true", skip=(page-1)*page_size , limit=page_size):
                # (registry_id, post_id) = row.key
                blog_data = dict()
                blog_data.update(row.value)
                
                if control_panel:
                    blog_data["conteudo"]  = remove_html_tags(blog_data["conteudo"])
                    if len(blog_data["conteudo"]) > 100:
                        blog_data["conteudo"] = str_limit(blog_data["conteudo"], 100)
                    blog_data["data_fmt"] = short_datetime(blog_data["data_cri"])                                
                lista_posts.append(blog_data)
            
        return lista_posts
      
    @classmethod    
    def countPostsByRegistryId(self, registry_id):
        for row in database.BLOG.view('blog/count_posts',key=registry_id, group="true"):
            return row.value
        return 0

    @classmethod 
    def countRemovedPosts(self, registry_id):
        for row in database.BLOG.view('blog/count_removedposts',key=registry_id, group="true"):
            return row.value
        return 0
    
    def getNumComments(self):  
        plural = lambda x: 's' if x!=1 else ''
        
        rows = database.COMMENT.view('blog/all_comments',startkey=[self.id],endkey=[self.id, {}])
        if rows:
            return u"%d comentário%s" % (len(rows), plural(len(rows)))
        else:
            return u"nenhum comentário"
    
    def addComment(self, user, data, comment):
        """ Adiciona um comentário do Blog """
        if not comment:
            return ""
        else:
            comment_data = BlogComment()
            comment_data.comment = comment
            comment_data.owner = user
            comment_data.registry_id = self.registry_id
            comment_data.post_id = self.post_id
            comment_data.data_cri = data        
            comment_data.save(id=uuid4().hex)
            return comment_data
            
                          
    def getBlogPost(self, user, versao=-1):
        """ retorna dicionário com um post e todos os seus comentários. """
        if versao > len(self.historico)-1:
            versao = -1
        
        # recupera dados no BD
        post_data = dict(
                _id            = self.id,
                registry_id    = self.registry_id,
                owner          = self.owner,
                titulo         = self.titulo,
                post_id        = self.post_id,
                conteudo       = self.historico[versao]["conteudo"],
                tags           = self.tags,
                data_cri       = self.data_cri,
                data_alt       = self.historico[versao]["data_alt"],
                alterado_por   = self.historico[versao]["alterado_por"],
                comentarios    = [],
        )
        
        doc_id = '/'.join([post_data["registry_id"], post_data["post_id"]])
        
        for row in database.COMMENT.view('blog/all_comments',startkey=[doc_id],endkey=[doc_id, {}]):
            comentario = dict()
            comentario.update(row.value)
            post_data["comentarios"].append(comentario)
        
        return post_data
      
    def deletePost(self, user, permanently=False):
        registry_id = self.registry_id
        post_id = self.post_id
        tags = self.tags

        if permanently:
            # se permanentemente, deleta
            self.delete()
            
            #remove os comentários deste post
            for row in database.COMMENT.view('blog/all_comments',startkey=[self.id],endkey=[self.id, {}]):
                (doc_id, comment_id) = row.key
                _comment = BlogComment(comment_id)
                _comment.delete()
        else:
            # se não, cria entrada no histórico marcando a página como removida
            self.historico.append(dict(
                                       conteudo=_CONTEUDO_REMOVIDO,
                                       alterado_por=user,
                                       data_alt=str(datetime.now())
                            ))
            
            self.save()        
            #remove as tags
            #TODO? Mover tags para historico
            for tag in tags:
                removeTag(remove_diacritics(tag.lower()), "blog", self.id)


    def save(self, id=None, db=database.BLOG):
        if not self.id and id: self.id = id
        self.store(db)
        
  
    def retrieve(self, id, include_removed=False, db=database.BLOG):
      bg = Blog.load(db, id)
      if bg:
          if include_removed:
              return bg
          elif bg.historico[-1]["conteudo"] != _CONTEUDO_REMOVIDO:
              return bg
          else:
              return None
      else:
          return None
      
    def getBlogHistory(self):
        # recupera dados no BD
        blog_data = dict(
                registry_id    = self.registry_id,
                owner          = self.owner,
                titulo         = self.titulo,
                post_id        = self.post_id,
                historico      = []
        )

        for i in range(len(self.historico)):
            blog_data["historico"].append(dict(
                versao         = str(i),
                data_alt       = short_datetime(self.historico[i]["data_alt"]),
                alterado_por   = self.historico[i]["alterado_por"]
                ))
        blog_data["historico"].reverse()
        return blog_data
  
    def restoreVersion (self, versao):
      self.historico.append(dict(
          conteudo       = self.historico[versao]["conteudo"],
          data_alt       = self.historico[versao]["data_alt"],
          alterado_por   = self.historico[versao]["alterado_por"]
          ))
      self.save()
    
    def delete(self, db=database.BLOG):
        #db.delete(self)
        del db[self.id]



class BlogComment(Document):
    # _id = <couchdb_id>
    registry_id    = TextField() # dono do blog: usuário ou comunidade
    owner          = TextField() # quem fez o comentário.
    post_id        = TextField() # post comentado
    comment        = TextField()
    data_cri       = TextField()


            
    def save(self, id=None, db=database.COMMENT):
        if not self.id and id: self.id = id
        self.store(db)
        
    def retrieve(self, id, db=database.COMMENT):
        return BlogComment.load(db, id)
    
    def delete(self, db=database.COMMENT):
        #db.delete(self)
        del db[self.id]
            