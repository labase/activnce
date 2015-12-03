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

from datetime import datetime
from uuid import uuid4

import tornado.web
from tornado.web import HTTPError
import tornado.template

from core.dispatcher import BaseHandler, HANDLERS, URL_TO_PAGETITLE, \
                            NOMEUSERS, \
                            FILENAMECHARS, PAGENAMECHARS
import model
import core.model
from core.model import isUserOrOwner, isUserOrMember
import core.database
import log.model
from search.model import addTag, removeTag, splitTags
from libs.notify import Notify
from libs.dateformat import short_datetime
from libs.strformat import str_limit, remove_diacritics, remove_html_tags
import libs.permissions
from libs.permissions import isAllowedToDeleteObject, isAllowedToWriteObject

''' importa definição do tutorial deste módulo, se existir _tutorial.py '''
from config import TUTORIAL
try:
    import _tutorial
except ImportError:
    pass


# Número máximo de questões exibidas na página que lista questões
NUM_MAX_QUESTOES = 20

def prepareQuestions(user, questions, include_removed=False):
    for question in questions:
        question["enunciado"] = str_limit(remove_html_tags(question["enunciado"]), 200)
        
        # permissões para remover e alterar uma questão
        question_used = model.Question.questionIsUsed(question["_id"])
        question["alterar"] = isAllowedToWriteObject(user, "question", question["registry_id"]) and not question_used
        question["apagar"] = isAllowedToDeleteObject(user, question["owner"], question["registry_id"]+"/"+question["_id"]) and not question_used
        
        # datas formatadas
        question["data_fmt"] = short_datetime(question["data_cri"])
        if "data_alt" in question and question["data_alt"]:
            question["data_alt"] = short_datetime(question["data_alt"])
        
    #return sorted(questions, key=itemgetter("data_cri"), reverse=True)
    return questions

    
class QuestionHandler(BaseHandler):
    ''' Lista as questoes de um usuario ou comunidade '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('quiz')
    @libs.permissions.canReadService ("question")   
    def get (self, registry_id):
        user = self.get_current_user()
        page = int(self.get_argument("page","1"))
        id = self.get_argument("id","")   
        
        if id:
            # lista somente uma questão
            _question= model.Question().retrieve(id)
            if _question:
                question_used = model.Question.questionIsUsed(id)                
                links = []
                links.append((u"Quizes de "+registry_id, "/static/imagens/icones/quiz32.png", "/quiz/%s"%registry_id))
                if isAllowedToWriteObject(user, "question", registry_id) and not question_used:
                    links.append((u"Alterar esta questão", "/static/imagens/icones/edit32.png", "/question/edit/%s?id=%s"%(registry_id,id)))
                if isAllowedToDeleteObject(user, _question.owner, registry_id+"/"+id) and not question_used:
                    links.append((u"Apagar esta questão", "/static/imagens/icones/delete32.png", "/question/delete/%s?id=%s"%(registry_id,id),
                                  "return confirm('Deseja realmente apagar esta questão?');"))
                    
                self.render("modules/question/question.html", NOMEPAG=u"Questões",  \
                            REGISTRY_ID=registry_id, \
                            QUESTION=_question, \
                            IMGLIST=["resp_a.gif", "resp_b.gif", "resp_c.gif", "resp_d.gif", "resp_e.gif"], \
                            LINKS=links)              
            else:       
                raise HTTPError(404)             
                
   
        else:     
            # lista todas as questões
            
            questions_count = model.Question.countObjectsByRegistryId(registry_id)
            lista_questions = prepareQuestions(user, model.Question.listObjects(registry_id, page, NUM_MAX_QUESTOES))
    
            tags_list = model.Question.listAllTags(registry_id)
            links = []    
            links.append((u"Quizes de "+registry_id, "/static/imagens/icones/quiz32.png", "/quiz/%s"%registry_id))
        
            if isAllowedToWriteObject(user, "question", registry_id):
                links.append((u"Nova questão", "/static/imagens/icones/new32.png", "/question/new/"+registry_id))
            if isUserOrOwner(user, registry_id):
                links.append((u"Alterar permissões do Banco de Questões", "/static/imagens/icones/permissions32.png", "/permission/question/"+registry_id, "", "", True))   
             
            log.model.log(user, u'acessou o banco de questões de', objeto=registry_id, tipo="question", news=False)
                     
            self.render("modules/question/question-list.html", NOMEPAG=u"Questões", REGISTRY_ID=registry_id, \
                                                  QUESTIONS=lista_questions, QUESTIONS_COUNT=questions_count, \
                                                  PAGE=page, PAGESIZE=NUM_MAX_QUESTOES, \
                                                  TITLE=u"Questões de %s" % registry_id, \
                                                  TAGS = tags_list, \
                                                  LINKS=links)


class NewQuestionHandler(BaseHandler):
    ''' Inclusão de uma question '''

    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('quiz')
    @libs.permissions.canWriteService ("question")
    def get (self, registry_id):
        user = self.get_current_user()
        self.render("modules/question/question-form.html",  NOMEPAG=u"Questões", QUESTIONDATA=model.Question(), REGISTRY_ID=registry_id, MSG="")  

    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('quiz')
    @libs.permissions.canWriteService ("question")
    def post(self, registry_id):
        user = self.get_current_user()
        self._question = model.Question()
        msg = ""
        
        self._question.enunciado = self.get_argument("enunciado","")
        if self._question.enunciado == "":
            msg += u"Enunciado da questão não preenchido.<br/>"
                
        self._question.tags = splitTags(self.get_argument("tags",""))
        self._question.subtype = self.get_argument("subtype","")
        if not self._question.subtype :
            msg += u"Escolha o tipo de questão a ser criada.<br/>"
       
        self._question.respostas = self.get_arguments("resposta")
        #testa o subtipo de questão e verifica a necessidade de resposta certa
        if self._question.subtype == u"Teste":
            
            self._question.resp_certa = self.get_argument("resp_certa","")
            if not self._question.resp_certa :
                msg += u"Resposta certa não selecionada.<br/>"
                
            else: 
                if not self._question.respostas[int(self._question.resp_certa)]:
                    msg += u"Resposta certa não pode ser vazia.<br/>"    
            
            self._question.nivel = self.get_argument("nivel","")
            if self._question.nivel == "":
                msg += u"Nível de dificuldade da questão não selecionado.<br/>"  
                

        
        acabou = False  
        fora_de_ordem = False  
        n_resp = 0
        
        for i in range (5):    
            if  acabou and self._question.respostas[i]:
                fora_de_ordem = True
            
            if not self._question.respostas[i]:
                acabou = True     
            else:
                n_resp = n_resp + 1
                
        if n_resp<2:
            msg += u"Preencha pelo menos duas respostas.<br/>"
            
        if fora_de_ordem:
            msg += u"As respostas precisam ser preenchidas na ordem.<br/>"
        
        self._question.respostas = [ value for value in self._question.respostas if value != "" ]                                      
                 
        if msg:
            self.render("modules/question/question-form.html",  NOMEPAG=u"Questões", QUESTIONDATA=self._question, REGISTRY_ID=registry_id, MSG=msg)  
            return
                
        else:
            # cria uma tag artificial com o nível da questão (utiliza uma @ no início para diferenciá-la das demais)
            if self._question.subtype != u"Survey":
                self._question.tags.append("@"+self._question.nivel.lower())
                self._question.tags.append(u"@teste múltipla escolha")
            else:
                self._question.tags.append(u"@pesquisa de opinião")
                
            self._question.tags = list(set(self._question.tags))
            
            self._question.data_cri = str(datetime.now())
            self._question.data_alt = self._question.data_cri

            doc_id = uuid4().hex
            self._question.service = "question"
            self._question.type = "question"
            self._question.registry_id = registry_id
            self._question.owner = user
            self._question.save(id=doc_id)
            
            '''
            As tags do banco de questões são utilizadas apenas para classificação das questões.
            Como elas não aparecerão no tagcloud nem devem ser encontradas pelas buscas, 
            não é necessário adicioná-las ao banco de tags.
            
            data_tag = str(datetime.now())
            for tag in self._question.tags:
                addTag(tag, registry_id, user, "question", doc_id, str_limit(remove_html_tags(self._question.enunciado), 50), data_tag)
            '''
            
            log.model.log(user, u'criou questão em', objeto=registry_id, tipo="question",link="/question/%s?id=%s"%(registry_id,doc_id))
            self.redirect("/question/%s" % registry_id)
        



class QuestionEditHandler(BaseHandler):
    ''' Edição de uma questão '''

    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('quiz')
    @libs.permissions.canWriteService ("question")
    
    def get (self, registry_id):
        user = self.get_current_user()
        id = self.get_argument("id","")   
        self._question = model.Question().retrieve(id)
  
        # remove as tags artificiais antes de apresentar o form de alteração
        self._question.tags = [ tag for tag in self._question.tags if tag[0]!="@" ]
        if self._question:
            if model.Question.questionIsUsed(id):
                # questão usada por um quiz não pode ser editada
                raise HTTPError(403)
            
            else:         
                self.render("modules/question/question-edit.html", NOMEPAG=u"Questões", \
                             QUESTIONDATA=self._question, REGISTRY_ID=registry_id, MSG="")
        else:
            raise HTTPError(404)
        
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('quiz')
    @libs.permissions.canWriteService ("question")
    
    def post(self, registry_id ):
        user = self.get_current_user()
        id = self.get_argument("id","")
        self._question = model.Question().retrieve(id)
        if self._question:
            if model.Question.questionIsUsed(id):
                # questão usada por um quiz não pode ser editada
                raise HTTPError(403)
            
            else:                
                msg = ""
                self._question.enunciado = self.get_argument("enunciado","")
                if self._question.enunciado == "":
                    msg += u"Enunciado da questão não preenchido.<br/>"        
                            
                self._question.respostas = self.get_arguments("resposta")
                self._question.subtype = self.get_argument("subtype", "")    
                #testa o subtipo de questão e verifica a necessidade de resposta certa
                if self._question.subtype == "Teste":
                    
                    self._question.resp_certa = self.get_argument("resp_certa","")
                    if not self._question.resp_certa :
                        msg += u"Resposta certa não selecionada.<br/>"
                        
                    else: 
                        if not self._question.respostas[int(self._question.resp_certa)]:
                            msg += u"Resposta certa não pode ser vazia.<br/>"    
                    
                    self._question.nivel = self.get_argument("nivel","")
                    if self._question.nivel == "":
                        msg += u"Nível de dificuldade da questão não selecionado.<br/>" 
                        
                elif self._question.subtype == "Survey":
                    self._question.resp_certa = None
                    self._question.nivel = None
                    
                acabou = False  
                fora_de_ordem = False  
                n_resp = 0
                for i in range (5):    
                    if  acabou and self._question.respostas[i]:
                        fora_de_ordem = True
                    
                    if not self._question.respostas[i]:
                        acabou = True     
                    else:
                        n_resp = n_resp + 1
                if n_resp<2:
                    msg += u"Preencha pelo menos duas respostas.<br/>"
                    
                if fora_de_ordem:
                    msg += u"As respostas precisam ser preenchidas na ordem.<br/>"
        
                self._question.respostas = [ value for value in self._question.respostas if value != "" ]                                        
                
                old_tags = self._question.tags
                self._question.tags = splitTags(self.get_argument("tags",""))
                
                if msg:
                    self.render("modules/question/question-edit.html",  NOMEPAG=u"Questões", \
                                QUESTIONDATA=self._question, REGISTRY_ID=registry_id, MSG=msg)  
                    return
    
                '''
                As tags do banco de questões são utilizadas apenas para classificação das questões.
                Como elas não aparecerão no tagcloud nem devem ser encontradas pelas buscas, 
                não é necessário adicioná-las ao banco de tags.
                
                else:
                    data_tag = str(datetime.now())
                    for tag in self._question.tags:
                        if tag not in old_tags:
                            addTag(tag, registry_id, user, "question", id, str_limit(remove_html_tags(self._question.enunciado), 50), data_tag)
    
                    for tag in old_tags:
                        if tag not in self._question.tags:
                            removeTag(remove_diacritics(tag.lower()), "question", id)
                '''
                
                # re-inclui a tag que representa o nível
                if self._question.subtype != u"Survey":
                    self._question.tags.append("@"+self._question.nivel.lower())
                    self._question.tags.append(u"@teste múltipla escolha")                   
                else:
                    self._question.tags.append(u"@pesquisa de opinião")
               
                if self._question.enunciado == "":
                    msg += u"O enunciado da questão não pode ser vazio.<br/>"
                               
                # registro da atualização
                # guarda-se apenas a ultima alteração 
                
                self._question.data_alt = str(datetime.now())
                self._question.alterado_por = user      
                            
                self._question.save()
                
                log.model.log(user, u'alterou uma questão de', objeto=registry_id, tipo="question", news=False)    
                self.redirect(r"/question/%s?id=%s" % (registry_id, id))       
                         
        else:
            raise HTTPError(404)

class QuestionDeleteHandler(BaseHandler):
    ''' Apaga questão '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('quiz')
    @libs.permissions.canWriteService ("question")
    def get(self, registry_id):
        user = self.get_current_user()
        
        question_id = self.get_argument("id","")
        self._question = model.Question().retrieve(question_id)
        
        if self._question != None:
            question_owner = self._question.owner
            if not isAllowedToDeleteObject(user, question_owner, registry_id+"/"+question_id):
                self.render("home.html", MSG=u"Você não tem permissão para remover esta questão.", \
                            NOMEPAG=u'Questões', REGISTRY_ID=registry_id)
                return

            enunciado = str_limit(remove_html_tags(self._question.enunciado), 200) 
            if self._question.deleteQuestion():
            
                # notifica o dono da questão excluída
                email_msg = u"Questão removida: "+enunciado+"\n"+\
                            Notify.assinatura(user, registry_id, str(datetime.now()))+"\n\n"
                Notify.email_notify(question_owner, user, u"removeu uma questão criada por você", \
                               message=email_msg, \
                               link="question/"+registry_id)
                                
                log.model.log(user, u'removeu uma questão de', objeto=registry_id, tipo="question")
                
                self.redirect("/question/%s" % registry_id)
                return
            
            else:
                self.render("home.html", MSG=u"Esta questão não pode ser apagada pois ela está sendo utilizada em um Quiz.", \
                            NOMEPAG=u'Questões', REGISTRY_ID=registry_id)
                
                
        else:
            raise HTTPError(404)
            
class QuestionTagHandler(BaseHandler):
    ''' Exibe Questões de um usuário com uma tag específica '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('quiz')
    @libs.permissions.canWriteService ("question")
    
    def get(self, registry_id, tag):
        user = self.get_current_user()
        #page = int(self.get_argument("page","1"))
        #bookm_count = model.Bookmarks.countBookmarksByRegistryIdAndTag(registry_id, tag)
        page = 1
        questions_count = model.Question.countObjectsByRegistryIdTags(registry_id, tag)
        lista_questions = prepareQuestions(user, model.Question.listObjects(registry_id, page, NUM_MAX_QUESTOES, tag=tag))
        tags_list = model.Question.listAllTags(registry_id, tag)
   
        links = []            
        links.append((u"Quizes de "+registry_id, "/static/imagens/icones/quiz32.png", "/quiz/%s"%registry_id))
        if isAllowedToWriteObject(user, "question", registry_id):
            links.append(("Nova questão", "/static/imagens/icones/new32.png", "/question/new/"+registry_id))
        if isUserOrOwner(user, registry_id):
            links.append((u"Alterar permissões do Banco de Questões", "/static/imagens/icones/permissions32.png", "/permission/question/"+registry_id, "", "", True))   
                        
        log.model.log(user, u'acessou uma questão de', objeto=registry_id, tipo="question", news=False)        

        self.render("modules/question/question-list.html", NOMEPAG=u"Questões", \
                    REGISTRY_ID=registry_id, CRIAR=isUserOrMember(user,registry_id), \
                    TAGS = tags_list, LINKS=links, \
                    PAGE=page, PAGESIZE=NUM_MAX_QUESTOES, \
                    QUESTIONS=lista_questions, QUESTIONS_COUNT=questions_count, \
                    TITLE=u"Questões de %s com a tag %s"%(registry_id,tag), \
                    MSG="")
      

URL_TO_PAGETITLE.update ({
        "question": u"Banco de Questões"
    })

HANDLERS.extend([
            (r"/question/new/%s"           % (NOMEUSERS),                     NewQuestionHandler),
            (r"/question/edit/%s"          % (NOMEUSERS),                     QuestionEditHandler),
            (r"/question/delete/%s"        % (NOMEUSERS),                     QuestionDeleteHandler),
            (r"/question/%s/%s"            % (NOMEUSERS, PAGENAMECHARS),      QuestionTagHandler),
            (r"/question/%s"               % (NOMEUSERS),                     QuestionHandler),
    ])
