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
from operator import itemgetter

import tornado.web
from tornado.web import HTTPError
import tornado.template

import model
from core.dispatcher import BaseHandler, HANDLERS, URL_TO_PAGETITLE, \
                            NOMEUSERS, FILENAMECHARS, PAGENAMECHARS
                            
import core.model
from core.model import isUserOrOwner
import question.control
from question.control import prepareQuestions, NUM_MAX_QUESTOES
from config import PLATAFORMA_URL
import log.model
import question.model
from libs.notify import Notify
from libs.dateformat import short_datetime, verificaIntervaloDMY, maiorData
from libs.strformat import remove_diacritics, remove_special_chars, remove_html_tags, str_limit
import libs.permissions
from libs.permissions import isAllowedToDeleteObject, \
                             isAllowedToReadObject, isAllowedToWriteObject

''' importa definição do tutorial deste módulo, se existir _tutorial.py '''
from config import TUTORIAL
try:
    import _tutorial
except ImportError:
    pass
    
# Número máximo de quiz exibidas 
NUM_MAX_QUIZ = 20


TIPO_QUIZ = { "Teste": u"Teste de múltipla escolha",
              "Survey": u"Pesquisa de opinião"
            }

def prepareQuiz(user, quiz_list):
    for quiz in quiz_list:
        #quiz["titulo"] = str_limit(remove_html_tags(quiz["titulo"]), 200)
        #quiz["descricao"] = str_limit(remove_html_tags(quiz["descricao"]), 200)
        quiz["descricao"] = quiz["descricao"].replace("\n", "<br/>")

        # permissões para remover e alterar um quiz
        quiz["apagar"] = isAllowedToWriteObject(user, "quiz", quiz["registry_id"], quiz["_id"]) and not model.Quiz.quizIsAnswered(quiz["_id"])
        quiz["alterar"] = isAllowedToWriteObject(user, "quiz", quiz["registry_id"], quiz["_id"])
        
        # tipo do quiz em extenso
        quiz["tipo"] = TIPO_QUIZ[quiz["subtype"]]

        # datas formatadas
        quiz["data_fmt"] = short_datetime(quiz["data_cri"])
        if "data_alt" in quiz and quiz["data_alt"]:
            quiz["data_alt"] = short_datetime(quiz["data_alt"])

        # condição para permitir que o quiz seja respondido
        dentro_do_periodo = verificaIntervaloDMY(quiz["data_inicio"], quiz["data_fim"]) == 0    
        
        ja_respondeu = model.Quiz.getQuizAnswers(quiz["_id"], user)
        
        quiz["nao_pode_responder"] =  (ja_respondeu and ja_respondeu["finalizado"]=="S") or \
                                      not dentro_do_periodo or \
                                      not isAllowedToReadObject(user, "quiz", quiz["registry_id"])
                                            
    return sorted(quiz_list, key=itemgetter("data_cri"), reverse=True)




class NewQuizHandler(BaseHandler):
    ''' Inclusão de um quiz '''

    def prepareQuestionList(self, question_list):
        return [ { "_id": item["_id"], 
                   "registry_id": item["registry_id"], 
                   "enunciado": str_limit(remove_html_tags(item["enunciado"]), 200) }         
                 for item in question_list ]   
        
                
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('quiz')
    @libs.permissions.canWriteService ("quiz")
    def get (self, registry_id):
        user = self.get_current_user()
        subtype = self.get_argument ("subtype", "")
        if subtype == "":
            raise HTTPError (400)
            return

        questions = self.prepareQuestionList(question.model.Question.listObjectsBySubtype(subtype, registry_id))
        
        msg = ""
        links = []
        if not questions:
            msg = u"Você não pode criar %s pois o banco de questões não possui nenhuma questão deste tipo" % TIPO_QUIZ[subtype]
            if isAllowedToReadObject(user, "question", registry_id):
                links.append((u"Banco de Questões", "/static/imagens/icones/question32.png", "/question/"+registry_id))
 
        self.render("modules/quiz/quiz-form.html",  NOMEPAG=u"Quiz", MSG=msg, \
                                        QUIZ=model.Quiz(), REGISTRY_ID=registry_id, \
                                        QUESTIONS=questions, \
                                        TITLE=u"Criar Quiz ("+TIPO_QUIZ[subtype]+")", \
                                        LINKS=links, SUBTYPE=subtype)     
        
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('quiz')
    @libs.permissions.canWriteService ("quiz")
    def post(self, registry_id): 
        user = self.get_current_user()
        subtype = self.get_argument ("subtype","")
        if subtype == "":
            raise HTTPError (400)
            return
        
        _quiz = model.Quiz()
        _quiz.titulo = self.get_argument("titulo","")
        _quiz.questions = self.get_arguments("questions")
        _quiz.descricao = self.get_argument("descricao","")
        _quiz.data_inicio = self.get_argument("data_start","")        
        _quiz.data_fim = self.get_argument("data_end","") 
        _quiz.exibicao = self.get_argument("exibicao", "")       
        
        msg = ""
        if _quiz.titulo == "":
            msg += u"Título do quiz não preenchido.<br/>"
        
        else:
            quiz_id = remove_special_chars(remove_diacritics(_quiz.titulo.replace(" ","_")))
            if quiz_id == "":
                 msg += u"Título do quiz inválido<br/>"
                 
        if not _quiz.descricao:
            msg += u"Descrição do quiz não preenchida.<br/>"       
        
        if not _quiz.questions:
            msg += u"Selecione pelo menos uma questão para fazer parte do quiz.<br/>"    
        
        if not _quiz.data_inicio:
            msg += u"O quiz deve possuir uma data de início.<br/>"        
            
        if not _quiz.data_fim:
            msg += u"O quiz deve possuir uma data de encerramento.<br/>"
        
        if not msg and not maiorData(_quiz.data_fim, _quiz.data_inicio, short=True):
            msg += u"A Data/hora de encerramento não pode ser anterior à Data/hora de início.<br/>"
        
        if msg:
            self.render("modules/quiz/quiz-form.html", NOMEPAG=u"Quiz", QUIZ=_quiz, REGISTRY_ID=registry_id, \
                                                 MSG=msg, \
                                                 QUESTIONS=self.prepareQuestionList(question.model.Question.listObjectsBySubtype(subtype, registry_id)), \
                                                 TITLE=u"Criar Quiz ("+TIPO_QUIZ[subtype]+")", \
                                                 LINKS=[], SUBTYPE=subtype )  
            return
                       
        else:
            _quiz.data_cri = str(datetime.now())
            _quiz.data_alt = _quiz.data_cri
            _quiz.service = "quiz"
            _quiz.type = "quiz"
            _quiz.subtype = subtype
            doc_id = uuid4().hex
            _quiz.registry_id = registry_id
            _quiz.owner = user
            try:
                _quiz.save(id=doc_id)
            except Exception as detail:
                self.render("modules/quiz/quiz-form.html",  NOMEPAG=u"Questionário", QUIZDATA=_quiz, REGISTRY_ID=registry_id, \
                                                 QUESTIONS=self.prepareQuestionList(question.model.Question.listObjectsBySubtype(subtype, registry_id)), \
                                                 SUBTYPE=subtype,\
                                                 TITLE=u"Criar Quiz ("+TIPO_QUIZ[subtype]+")", \
                                                 LINKS=[], \
                                                 MSG=u"Já existe um quiz com este título.")
                return
                
            log.model.log(user, u'criou quiz em', objeto=registry_id, tipo="quiz",link="/quiz/%s"%quiz_id)
            self.redirect("/quiz/%s" % registry_id)

    
class QuizListHandler(BaseHandler):
    ''' Lista todos os quizes de uma comunidade '''
   
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('quiz')
    @libs.permissions.canReadService ("quiz")   
    def get (self, registry_id):
        user = self.get_current_user()
        page = int(self.get_argument("page","1"))
        quiz_count = model.Quiz.countObjectsByRegistryId(registry_id)
        lista_quiz = prepareQuiz(user, model.Quiz.listObjects(registry_id, page, NUM_MAX_QUIZ))
        
        links = []
        if isAllowedToReadObject(user, "question", registry_id):
            links.append((u"Banco de questões", "/static/imagens/icones/question32.png", "/question/"+registry_id))
        if isAllowedToWriteObject(user, "quiz", registry_id):
            links.append((u"Novo teste de múltipla escolha", "/static/imagens/icones/add_test32.png", "/quiz/new/%s?subtype=Teste"%registry_id))
            links.append ((u"Nova pesquisa de opinião", "/static/imagens/icones/add_survey32.png", "/quiz/new/%s?subtype=Survey"%registry_id))
         
        log.model.log(user, u'acessou a lista de quizes de', objeto=registry_id, tipo="quiz", news=False)
                 
        self.render("modules/quiz/quiz-list.html", NOMEPAG="Quiz", REGISTRY_ID=registry_id, \
                                              IS_ADMIN=isUserOrOwner(user, registry_id), \
                                              QUIZ=lista_quiz, QUIZ_COUNT=quiz_count, \
                                              PAGE=page, PAGESIZE=NUM_MAX_QUIZ, \
                                              LINKS=links)
        

class QuizAnswerHandler(BaseHandler):
    ''' Apresenta um quiz para um usuário respondê-lo '''
   
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('quiz')
    @libs.permissions.canReadService ("quiz")   
    def get (self, registry_id, quiz_id):
        user = self.get_current_user()
        _quiz = model.Quiz().retrieve(quiz_id)
        
        if _quiz:
            status = model.Quiz.getQuizAnswers(quiz_id, user)
            
            if status and status["finalizado"]=="S":
                # este usuário já terminou de respoder a este quiz
                raise HTTPError(403)
                    
            else:
                _questions = _quiz.listQuestionsInQuiz()
                if _quiz.exibicao == u"Uma questão de cada vez":
                    i = int(self.get_argument("i","0"))
                    
                    if (i>len(_quiz.questions)-1):
                        # a questão a ser respondida está além do tamanho do quiz
                        raise HTTPError(404)   
                        return                 
                    
                    self.render("modules/quiz/quiz-single.html", NOMEPAG="Quiz",  \
                                REGISTRY_ID=registry_id, \
                                QUIZ=_quiz, TITLE=u"Quiz de %s" % registry_id, \
                                QUESTIONS=_questions, N_QUESTION = i, \
                                ANSWERS=status["respostas"] if status else {}, \
                                IMGLIST=["resp_a.gif", "resp_b.gif", "resp_c.gif", "resp_d.gif", "resp_e.gif"]
                            )   

                else:                           
                    self.render("modules/quiz/quiz-all.html", NOMEPAG="Quiz",  \
                                    REGISTRY_ID=registry_id, QUESTIONS=_questions, \
                                    QUIZ=_quiz, TITLE=u"Quiz de %s" % registry_id, \
                                    IMGLIST=["resp_a.gif", "resp_b.gif", "resp_c.gif", "resp_d.gif", "resp_e.gif"]
                                )
                           
        else:  
            # quiz não existe                  
            raise HTTPError(404)
            

    #@tornado.web.authenticated
    #@core.model.allowedToAccess
    #@core.model.serviceEnabled('quiz')
    #@libs.permissions.canReadService ("quiz")   
    def post (self, registry_id, quiz_id):
        user = self.get_current_user()
        _quiz= model.Quiz().retrieve(quiz_id)
        
        if _quiz.exibicao == u"Uma questão de cada vez":
            atual = int(self.get_argument("atual","0"))
            prox = self.get_argument("prox","0")
            if prox != "FIM":
                prox = int(prox)
            
            question_id = self.get_argument("pergunta"+str(atual),"")
            resp_marcada = self.get_argument("resposta"+str(atual),"")
            
            status = model.Quiz.getQuizAnswers(quiz_id, user)
            if status:
                # user já está respondendo este quiz
                _answer = model.Answer().retrieve(status["answer_id"])
                
                _answer.respostas[question_id] = resp_marcada
                _answer.data_alt = str(datetime.now())
                _answer.alterado_por = user
                                        
                if prox=="FIM":
                    _answer.finalizado = "S"    
                    if _quiz.subtype == "Teste":           
                        _answer.nota = _answer.calculaNota()          
                    url_redirect = "/quiz/%s" % registry_id

                    log.model.log(user, u'Respondeu um quiz em', objeto=registry_id, tipo="quiz", link="/quiz/%s"%registry_id)
            
                else:
                    url_redirect = "/quiz/%s/%s?i=%s" % (registry_id, quiz_id, prox)
                    
                _answer.save()
              
            else:
                # user começou agora a responder o quiz
                _answer = model.Answer()
                answer_id = uuid4().hex
                
                _answer.respostas[question_id] = resp_marcada
                
                _answer.data_cri = str(datetime.now())
                _answer.data_alt = _answer.data_cri
                _answer.owner = user
                _answer.registry_id = registry_id
                if _quiz.subtype == "Teste":           
                    _answer.nota = u"não finalizado"
                _answer.service = "quiz"
                _answer.type = "answer"
                _answer.quiz_id = quiz_id
                
                if prox=="FIM":
                    _answer.finalizado = "S"                
                    if _quiz.subtype == "Teste":           
                        _answer.nota = _answer.calculaNota()
                        
                    url_redirect = "/quiz/%s" % registry_id
                    log.model.log(user, u'Respondeu um quiz em', objeto=registry_id, tipo="quiz", link="/quiz/%s"%registry_id)
                    
                else:
                    url_redirect = "/quiz/%s/%s?i=%s" % (registry_id, quiz_id, prox)
           
                _answer.save(id=answer_id)                

            self.redirect(url_redirect)
            
        else:
            # todas as questões de uma vez só
            _answer = model.Answer()
            answer_id = uuid4().hex

            for i in range(len(_quiz.questions)):
                question_id = self.get_argument("pergunta"+str(i),"")
                resp_marcada = self.get_argument("resposta"+str(i),"")
                _answer.respostas[question_id] = resp_marcada
            
            _answer.data_cri = str(datetime.now())
            _answer.owner = user
            _answer.registry_id = registry_id
            _answer.type = "answer"
            _answer.quiz_id = quiz_id
            _answer.finalizado = "S"     
            if _quiz.subtype == "Teste":           
                _answer.nota = _answer.calculaNota()
                                 
            _answer.save(id=answer_id)                

            log.model.log(user, u'Respondeu um quiz em', objeto=registry_id, tipo="quiz", link="/quiz/%s"%registry_id)
            self.redirect("/quiz/%s" % registry_id)
              
                
class QuizAnswerKeyHandler(BaseHandler):
    ''' Lista gabarito de um quiz de uma comunidade '''
   
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('quiz')
    @libs.permissions.canWriteService ("quiz")   
    def get (self, registry_id, id):
        user = self.get_current_user()
        page = int(self.get_argument("page","1"))
        #id = self.get_argument("id","")
        
        links = []
        
        _quiz= model.Quiz().retrieve(id)
        
        if _quiz:
            _questions = _quiz.listQuestionsInQuiz()
               
            if isAllowedToWriteObject(user, "quiz", registry_id):
                links.append(("Alterar este quiz", "/static/imagens/icones/edit32.png", "/quiz/edit/%s/%s"%(registry_id,id)))

            self.render("modules/quiz/quiz-answerkey.html", NOMEPAG="Quiz",  \
                        REGISTRY_ID=registry_id, \
                        QUIZ=_quiz, TITLE=u"Quiz de %s" % registry_id, \
                        QUESTIONS=_questions, \
                        IMGLIST=["resp_a.gif", "resp_b.gif", "resp_c.gif", "resp_d.gif", "resp_e.gif"], \
                        LINKS=links)              
        else:                   
            raise HTTPError(404) 
            
class QuizEditHandler(BaseHandler):
    ''' Edição de um quiz '''
   
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('quiz')
    @libs.permissions.canWriteService ("quiz")
    def get (self, registry_id, id):
        user = self.get_current_user()
        _quiz= model.Quiz().retrieve(id)
        links = []
        if _quiz:
            if isUserOrOwner(user, registry_id):
                links.append((u"Alterar permissões deste quiz", "/static/imagens/icones/permissions32.png", "/permission/quiz/"+registry_id+"/"+id, "", "", True))
            self.render("modules/quiz/quiz-edit.html", NOMEPAG=u"Quiz", LINKS=links, QUIZDATA=_quiz, REGISTRY_ID=registry_id, MSG="")
        else:
            raise HTTPError(404)

      
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('quiz')
    @libs.permissions.canWriteService ("quiz")
    def post(self, registry_id, id):
        user = self.get_current_user()
        _quiz = model.Quiz().retrieve(id)
       
        msg = ""
       
        _quiz.titulo = self.get_argument("titulo","")
        _quiz.descricao = self.get_argument("descricao","")
        _quiz.data_inicio = self.get_argument("data_start","")       
        _quiz.data_fim = self.get_argument("data_end","")
        _quiz.exibicao = self.get_argument("exibicao", "")      
       
       
        if _quiz.titulo == "":
            msg += u"Título do quiz não preenchido.<br/>"
        
        if not _quiz.descricao:
            msg += u"Descrição do quiz não preenchida.<br/>"      
       
       
        if not _quiz.data_inicio:
            msg += u"O quiz deve possuir uma data de início.<br/>"       
           
       
        if not _quiz.data_fim:
            msg += u"O quiz deve possuir uma data de encerramento.<br/>"
       
        if not msg and not maiorData(_quiz.data_fim, _quiz.data_inicio, short=True):
            msg += u"A Data/hora de encerramento não pode ser anterior à Data/hora de início.<br/>"
       
        if msg:
           self.render("modules/quiz/quiz-edit.html",  NOMEPAG=u"Quiz", QUIZDATA=_quiz, REGISTRY_ID=registry_id, \
                                                MSG=msg) 
           return
                      
        else:
            # registro da atualização
            # guarda-se apenas a ultima alteração
           
            _quiz.data_alt = str(datetime.now())
            _quiz.alterado_por = user     
                       
            _quiz.save()
           

            log.model.log(user, u'alterou quiz em', objeto=registry_id, tipo="quiz",link="/quiz/%s")
            self.redirect("/quiz/%s"%(registry_id))
        
class QuizDeleteHandler(BaseHandler):
    ''' Apaga um quiz '''
    
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('quiz')
    @libs.permissions.canWriteService ("quiz")
    def get(self, registry_id, id):
        user = self.get_current_user()
        
        _quiz = model.Quiz().retrieve(id)
                
        if _quiz != None:
            quiz_owner = _quiz.owner
            
            if not isAllowedToDeleteObject(user, quiz_owner, registry_id+"/"+id):
                raise HTTPError(403) 

            if _quiz.deleteQuiz():
                                
                log.model.log(user, u'removeu um quiz de', objeto=registry_id, tipo="quiz")
                
                self.redirect("/quiz/%s" % registry_id)
                return
            
            else:
                self.render("home.html", MSG=u"Este quiz não pode ser apagado pois ele já foi respondido.", \
                            NOMEPAG=u'Quiz', REGISTRY_ID=registry_id)
     
        else:
            self.redirect("/quiz/%s" % registry_id)


                
class QuizResultHandler(BaseHandler):
    ''' Lista os resultados de um quiz de uma comunidade '''
   
    @tornado.web.authenticated
    @core.model.allowedToAccess
    @core.model.serviceEnabled('quiz')
    @libs.permissions.canWriteService ("quiz")   
    def get (self, registry_id, quiz_id):
        _quiz = model.Quiz().retrieve(quiz_id)
        if _quiz:
            if model.Quiz().quizIsAnswered(quiz_id):   
                
                if _quiz["subtype"] == "Teste":
                    self.render("modules/quiz/quiz-result-teste.html", NOMEPAG="Quiz",  \
                                REGISTRY_ID=registry_id, TITLE=u"Quiz de %s" % registry_id, \
                                ANSWERS=model.Quiz.getQuizAnswers(quiz_id), QUIZ=_quiz, \
                                LINKS=[]
                                )    
                elif _quiz["subtype"] == "Survey":
                    #mexer no html
                    _answers =  model.Quiz.respDadas(quiz_id)  
                    _questions = _quiz.listQuestionsInQuiz()
                    
                 
                    self.render("modules/quiz/quiz-result-survey.html", NOMEPAG="Quiz",  \
                                REGISTRY_ID=registry_id, TITLE=u"Quiz de %s" % registry_id, \
                                ANSWERS=_answers, QUIZ=_quiz, QUESTIONS= _questions, \
                                IMGLIST=["resp_a.gif", "resp_b.gif", "resp_c.gif", "resp_d.gif", "resp_e.gif"], \
                                LINKS=[]
                                )   
                   
        else:    
            raise HTTPError(404) 
           



URL_TO_PAGETITLE.update ({
        "quiz": u"Quiz"
    })


HANDLERS.extend([
            (r"/quiz/new/%s"              % (NOMEUSERS),                     NewQuizHandler),        
            (r"/quiz/%s"                  % (NOMEUSERS),                     QuizListHandler),
            (r"/quiz/%s/%s"               % (NOMEUSERS, NOMEUSERS),          QuizAnswerHandler),
            (r"/quiz/edit/%s/%s"          % (NOMEUSERS, NOMEUSERS),          QuizEditHandler),
            (r"/quiz/delete/%s/%s"        % (NOMEUSERS, NOMEUSERS),          QuizDeleteHandler),
            (r"/quiz/answerkey/%s/%s"     % (NOMEUSERS, NOMEUSERS),          QuizAnswerKeyHandler),
            (r"/quiz/result/%s/%s"        % (NOMEUSERS, NOMEUSERS),          QuizResultHandler)
            
    ])
