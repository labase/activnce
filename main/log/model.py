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
from datetime import datetime, timedelta
import os

try:
  from couchdb.schema import Document, TextField, IntegerField, LongField, DateTimeField, DictField, ListField, Schema, FloatField
except ImportError:
  from couchdb.mapping import Document, TextField, IntegerField, LongField, DateTimeField, DictField, ListField, FloatField
  from couchdb.mapping import Mapping as Schema
  
import database
from database import _EMPTYNEWS, _EMPTYLOG, \
                     VERBOS_ESCRITA, VERBOS_LEITURA

import core.model
import core.database
import core.dispatcher
from libs.dateformat import short_date, short_datetime, elapsed_time, \
                            converteDataDMYToYMDStr, converteDataDMYToMDYStrSemHora, calculaDiferencaDatas, \
                            converteDataYMDToMDYStrSemHora, converteDataMDYToYMDStrSemHora
from config import LOG_THREADS, LOG_THREADS_FILE, DIR_RAIZ_ACTIV

LIMITE_DIAS_NOTICIAS = 30   # notícias anteriores são automaticamente excluídas



class Log(Document):
    # _id = "member_id"
    #registros = ListField(DictField())    # lista de todos os acessos do user

    sujeito = TextField()
    verbo = TextField()
    objeto = TextField()
    tipo = TextField()
    link = TextField()
    news = TextField()
    data_inclusao = TextField()
                         
    def lastAccess(self):
        if self.registros:
            return self.registros[0]["data_inclusao"]
        else:
            return "1970-01-01 00:00:00.000000"

    @classmethod
    def get_system_stats (self, tipo, data_inicial, data_final):
        return_list = []
        temp_dict = {'00':0, '01':0, '02':0, '03':0, '04':0, '05':0, '06':0, '07':0, '08':0, '09':0, '10':0, '11':0, \
                     '12':0, '13':0, '14':0, '15':0, '16':0, '17':0, '18':0, '19':0, '20':0, '21':0, '22':0, '23':0 }
        if tipo=="Dia":
            for row in database.LOG.view('log/total_by_day', startkey=[data_inicial], endkey=[data_final,{}], group="true", group_level=1):
                return_list.append((row.key[0], row.value))
        elif tipo=="Hora":
            """
            print data_inicial, data_final
            for row in database.LOG.view('log/total_by_hour', startkey=["0", data_inicial], endkey=["23", data_final, {}], group="true", group_level=2):
                print row.key, row.value
                temp_dict[row.key[0]] = temp_dict[row.key[0]] + row.value
            """
            
            for row in database.LOG.view('log/total_by_day', startkey=[data_inicial], endkey=[data_final,{}], group="true", group_level=2):
                temp_dict[row.key[1]] = temp_dict[row.key[1]] + row.value
            
            keys_list = temp_dict.keys()
            keys_list.sort()
            for key in keys_list:
                return_list.append((key, temp_dict[key]))
            
        return return_list
    
    @classmethod
    def get_system_user_stats (self, num_usuarios, data_inicial, data_final):
        return_list = []
        lista_membros = []

        for row in database.LOG.view('log/total_by_user', startkey=[data_inicial], endkey=[data_final,{}], group="true", group_level=2):
            if row.key[1] not in lista_membros:
                lista_membros.append(row.key[1])
                return_list.append((row.key[1], str(row.value)))
            else:
                for item in return_list:
                    if item[0] == row.key[1]:
                        return_list.append((row.key[1], str(row.value + int(item[1]))))
                        return_list.remove(item)
                        break
                    
        return_list.sort(key=lambda x: (int(x[1])), reverse = True)
        #lista[:5] corta a lista, ficando com apenas as 5 primeiras posições
        return (return_list[:int(num_usuarios)], lista_membros)
        
    def save(self, id=None, db=database.LOG):
        if not self.id and id: self.id = id
        self.store(db)
        
    def delete(self, db=database.LOG):
        #db.delete(self)
        del db[self.id]

    def retrieve(self, id, db=database.LOG):
        return Log.load(db, id)

        
def log(sujeito, verbo, objeto="", tipo="", link="", news=True):

    def grava_news(user, sujeito, verbo, objeto, tipo, link, data_inclusao):
        registro = dict(
                     sujeito=sujeito,
                     verbo=verbo,
                     objeto=objeto,
                     tipo=tipo,
                     link=link,
                     data_inclusao=data_inclusao
                )
        
        news_data = _EMPTYNEWS()
        if user in database.TEMP_NEWS:
            news_data.update(database.TEMP_NEWS[user])
            news_data["avisos"].insert(0,registro)
        else:
            news_data["avisos"] = [registro]
        database.TEMP_NEWS[user] = news_data
          
    
    def grava_log(sujeito, verbo, objeto, tipo, link, data_inclusao, news):
        registro = dict(
                     sujeito=sujeito,
                     verbo=verbo,
                     objeto=objeto,
                     tipo=tipo,
                     link=link,
                     news=news,
                     data_inclusao=data_inclusao
                )
        
        database.TEMP_LOG.append(registro)

     
    if sujeito and sujeito!=None:
        data_inclusao = str(datetime.now())
        #if news:       # só pra testar
        if not link and tipo!="none":
            link = "/%s/%s" % (tipo, objeto)
        grava_log(sujeito, verbo, objeto, tipo, link, data_inclusao, news)
        #        else:
        #            #print os.path.dirname(os.path.abspath(__file__))
        #            text_file = open(os.path.dirname(os.path.abspath(__file__))+"/Log.txt", "a+")
        #            text_file.write("'%s', '%s', '%s', '%s', '%s', '%s', '%s'\n" % (sujeito, verbo, objeto, tipo, link, data_inclusao, news))
        #            text_file.close()            
        
        if news:
            # objeto pode ser: user, community, wiki, file, etc.
            if "/" in objeto:
                (objeto_id, pagina) = objeto.split("/") # wiki, file, etc
            else:
                objeto_id = objeto                     # user ou community
            
            _sujeito = core.model.Member().retrieve(sujeito)
        
            if objeto_id:
                _objeto = core.model.Registry().retrieve(objeto_id)
                        
            # se não existir objeto ou se o objeto não for privado,
            # armazena uma notícia para cada amigo do sujeito
            if not objeto or _objeto.privacidade != "Privada":
                for amigo in _sujeito.amigos:
                    grava_news(amigo, sujeito, verbo, objeto, tipo, link, data_inclusao)
                
            # armazena uma notícia para cada amigo/participante
            # do dono do objeto, dependendo do caso.
            if objeto and sujeito!=objeto_id:
                type = _objeto.getType()
                if type=="member":
                    # avisa ao dono do objeto se ele ainda não foi avisado
                    if objeto_id not in _sujeito.amigos:
                        grava_news(objeto_id, sujeito, verbo, objeto, tipo, link, data_inclusao)
                elif type=="community":
                    # se o objeto for uma comunidade
                    
                    # inclui noticia para a comunidade
                    grava_news(objeto_id, sujeito, verbo, objeto, tipo, link, data_inclusao)
                    
                    # inclui notícia para cada participante da comunidade
                    for participante in _objeto.participantes:
                        if participante not in _sujeito.amigos and participante != sujeito:
                            grava_news(participante, sujeito, verbo, objeto, tipo, link, data_inclusao)
    

def get_news_list(user_id, date_time=False):
    # retorna lista de dicionários com novidades para um user_id
    novidades = []
    if user_id in database.NEWS and "avisos" in database.NEWS[user_id]:
        novidades = database.NEWS[user_id]["avisos"]
    for item in novidades:
        item["data_inclusao"] = short_datetime(item["data_inclusao"], include_year=True) if date_time else short_date(item["data_inclusao"])
    return novidades


def get_log_list(user_id, date_time=False, limit=300, news=True):
    # retorna lista de dicionários com todas as ações realizadas por um user_id
    novidades = []
    view_name = news and 'log/log_list_news' or 'log/log_list'
    
    for row in database.LOG.view(view_name,startkey=[user_id, {}], endkey=[user_id], descending="true", skip=0, limit=limit):
        row.value["data_inclusao"] = short_datetime(row.value["data_inclusao"], include_year=True) if date_time else short_date(row.value["data_inclusao"])
        novidades.append(row.value)
    return novidades     
    
    
def get_recent_actions(user, limit=30, news=False):
    recentes = []
    log_list = get_log_list(user, date_time=True, limit=limit, news=news)

    for i in range(len(log_list)):
        achei = False
        for item in recentes:
            if item["verbo"]==log_list[i]["verbo"] and item["objeto"]==log_list[i]["objeto"]:
                achei = True
                break
        if not achei and log_list[i]["link"]!="//":
            recentes.append({"verbo": log_list[i]["verbo"],
                             "objeto":log_list[i]["objeto"],
                             "link":  log_list[i]["link"]})
            
    return recentes
  
  
def change_list_order(sujeito, objeto):
    """ reposiciona objeto acessado nas listas de amigos/participantes/comunidades """
    
    # objeto pode ser: user, community, wiki, file, etc.
    if "/" in objeto:
        (objeto_id, pagina) = objeto.split("/") # wiki, file, etc
    else:
        objeto_id = objeto                     # user ou community
                    
    _sujeito = core.model.Member().retrieve(sujeito)
    
    if objeto_id:
        _objeto = core.model.Registry().retrieve(objeto_id)
        
        # se sujeito participa da comunidade objeto
        if _objeto and _objeto.isACommunity() and sujeito in _objeto.participantes:
            # sujeito vai pra frente da lista de participantes do objeto
            _objeto.participantes.remove(sujeito)
            _objeto.participantes.insert(0, sujeito)
            _objeto.save()
            
        # se a comunidade objeto está na lista de comunidades do sujeito
        if objeto_id in _sujeito.comunidades:
            # comunidade objeto vai pra frente da lista de comunidades do sujeito
            _sujeito.comunidades.remove(objeto_id)
            _sujeito.comunidades.insert(0, objeto_id)
        
        # se o usuário objeto é amigo do sujeito
        if objeto_id in _sujeito.amigos:
            # usuário objeto vai pra frente da lista de amigos do sujeito
            _sujeito.amigos.remove(objeto_id)
            _sujeito.amigos.insert(0, objeto_id)
          
        if objeto_id in _sujeito.comunidades or objeto_id in _sujeito.amigos: 
            _sujeito.save()    

                              
def saveLog():
    """ Persiste o log de acessos no banco de dados """

    if LOG_THREADS:
        hora_inicio = str(datetime.now())
        tam_log = len(database.TEMP_LOG)
        tam_news = len(database.TEMP_NEWS)

    temp_log = database.TEMP_LOG
    database.TEMP_LOG = []
    
    for item in temp_log:
        _log = Log()
        _log.sujeito = item["sujeito"]
        _log.verbo = item["verbo"]
        _log.objeto = item["objeto"]
        _log.tipo = item["tipo"]
        _log.link = item["link"]
        _log.news = item["news"]
        _log.data_inclusao = item["data_inclusao"]          
        log_id = uuid4().hex          
        try:
            _log.save(id=log_id)
        except Exception as detail:
            if LOG_THREADS:
                #print "Erro ao salvar o log: %s %s %s (%s)" % (_log.sujeito, _log.verbo, _log.objeto, _log.data_inclusao)
                text_file = open(DIR_RAIZ_ACTIV+LOG_THREADS_FILE, "a+")
                text_file.write("Erro: '%s', '%s', '%s', '%s'\n" % (_log.sujeito, _log.verbo, _log.objeto, _log.data_inclusao))
                text_file.close()
        
        change_list_order(item["sujeito"], item["objeto"])  
                  
    # salvando NEWS...
    temp_news = database.TEMP_NEWS
    database.TEMP_NEWS = dict()
    
    for k,v in temp_news.iteritems():
        if k in database.NEWS:
            news_data = database.NEWS[k]
            temp_list = v["avisos"]
            temp_list.extend(news_data["avisos"])
            news_data["avisos"] = temp_list
            database.NEWS[k] = news_data
        else:
            database.NEWS[k] = v
    
    if LOG_THREADS:
        hora_fim = str(datetime.now())
        #print "Salvando... Log:%s; News:%s\n%s -> %s" % (tam_log, tam_news, hora_inicio, hora_fim)
        text_file = open(DIR_RAIZ_ACTIV+LOG_THREADS_FILE, "a+")
        text_file.write("[%s - %s] Logger: Log=%s; News=%s;\n" % (hora_inicio, hora_fim, tam_log, tam_news))
        text_file.close()

def cleanNews():
    """ Remove novidades antigas do banco de dados """
    data_inicio = str(datetime.now())
      
    num = 0     # total de notícias apagadas
    for registry_id in database.NEWS:
        alterou = False
        news_data = _EMPTYNEWS()
        news_data.update (database.NEWS[registry_id])

        news = []
        for item in news_data["avisos"]:
            delta = elapsed_time(item["data_inclusao"])
            if delta.days > LIMITE_DIAS_NOTICIAS:
                # remove este item
                alterou = True
                num = num + 1
            else:
                # mantem este item
                news.append (item)
        
        if alterou:
            news_data["avisos"] = news
            database.NEWS[registry_id] = news_data

    if LOG_THREADS:
        text_file = open(DIR_RAIZ_ACTIV+LOG_THREADS_FILE, "a+")
        text_file.write(u"[%s - %s] NewsCleaner: %d noticias apagadas com mais de %s dias.\n" % (data_inicio, str(datetime.now()), num, LIMITE_DIAS_NOTICIAS))
        text_file.close()
 

                
                
                
def get_community_user_action_list(nome_comunidade, data_inicial, data_final, tipo_servico, membro, tipo_log, format):
    listaDeDados = []
    listaDeMembros = []
    listaTemp = []
    existente = False
    data_temp = datetime.strptime(data_inicial, format)
       
    if tipo_servico == "todos":
        if membro =="*":
            for row in database.LOG.view('log/stats_by_all_users',startkey=[nome_comunidade, data_inicial], endkey=[nome_comunidade, data_final,{}], group="true"):
                if (tipo_log == "leitura" and row.key[3] in VERBOS_LEITURA) or (tipo_log == "escrita" and row.key[3] in VERBOS_ESCRITA) or \
                    (tipo_log == "todos" and (row.key[3] in VERBOS_LEITURA or row.key[3] in VERBOS_ESCRITA)):      
                    if row.key[2] not in listaDeMembros:
                        listaDeMembros.append(row.key[2])
                    
                    for i in listaDeDados:
                        if (converteDataYMDToMDYStrSemHora(row.key[1]) in i[0]) and (row.key[2] in i[2]):
                            listaDeDados.append((converteDataYMDToMDYStrSemHora(row.key[1]), str(int(i[1]) + int(row.value)), row.key[2]))
                            listaDeDados.remove(i)
                            existente = True
                            break
                        else:
                            existente = False
                    
                    if not existente:
                        listaDeDados.append((converteDataYMDToMDYStrSemHora(row.key[1]), str(row.value), row.key[2]))
                        listaTemp.append((converteDataYMDToMDYStrSemHora(row.key[1]), row.key[2]))
                          
            while (data_temp) <= (datetime.strptime(data_final, format)):
                for membro in listaDeMembros:
                    #se data_temp = data_incial e não há ações nesta data
                    if ((data_temp) == (datetime.strptime(data_inicial, format))) and ((str(converteDataYMDToMDYStrSemHora(str(data_temp))), membro) not in listaTemp):
                        listaDeDados.append((str(converteDataYMDToMDYStrSemHora(str(data_temp))), '0', membro))
                        
                    if ((data_temp) == (datetime.strptime(data_final, format))) and ((str(converteDataYMDToMDYStrSemHora(str(data_temp))), membro) not in listaTemp):
                        listaDeDados.append((str(converteDataYMDToMDYStrSemHora(str(data_temp))), '0', membro))
                    
                    if (str(converteDataYMDToMDYStrSemHora(str(data_temp))), membro) in listaTemp:                        
                        if ((str(converteDataYMDToMDYStrSemHora(str(data_temp - timedelta(days=1)))), membro) not in listaTemp and \
                        ((data_temp - timedelta(days=1)) > (datetime.strptime(data_inicial, format)))):
                            listaDeDados.append((str(converteDataYMDToMDYStrSemHora(str(data_temp - timedelta(days=1)))), '0', membro))
                            
                        if ((str(converteDataYMDToMDYStrSemHora(str(data_temp + timedelta(days=1)))), membro) not in listaTemp and \
                        ((data_temp + timedelta(days=1)) < (datetime.strptime(data_final, format)))):
                            listaDeDados.append((str(converteDataYMDToMDYStrSemHora(str(data_temp + timedelta(days=1)))), '0', membro))
                            
                data_temp += timedelta(days=1)
    
    
        else:
            for row in database.LOG.view('log/stats_by_all_users',startkey=[nome_comunidade, data_inicial], endkey=[nome_comunidade, data_final,{}], group="true"):
                if row.key[2] == membro:
                    if (tipo_log == "leitura" and row.key[3] in VERBOS_LEITURA) or (tipo_log == "escrita" and row.key[3] in VERBOS_ESCRITA) or \
                        (tipo_log == "todos" and (row.key[3] in VERBOS_LEITURA or row.key[3] in VERBOS_ESCRITA)):   
                    
                        for i in listaDeDados:
                            if (converteDataYMDToMDYStrSemHora(row.key[1]) in i[0]) and (row.key[2] in i[2]):
                                listaDeDados.append((converteDataYMDToMDYStrSemHora(row.key[1]), str(int(i[1]) + int(row.value)), row.key[2]))
                                listaDeDados.remove(i)
                                existente = True
                                break
                            else:
                                existente = False
                        
                        if not existente:                
                            listaDeDados.append((converteDataYMDToMDYStrSemHora(row.key[1]), str(row.value), row.key[2]))
                            listaTemp.append(converteDataYMDToMDYStrSemHora(row.key[1]))
                        
            listaDeMembros.append(membro)
            
            while (data_temp) <= (datetime.strptime(data_final, format)):
                for membro in listaDeMembros:
                    #se data_temp = data_incial e não há ações nesta data
                    if ((data_temp) == (datetime.strptime(data_inicial, format))) and ((str(converteDataYMDToMDYStrSemHora(str(data_temp)))) not in listaTemp):
                        listaDeDados.append((str(converteDataYMDToMDYStrSemHora(str(data_temp))), '0', membro))
                        
                    if ((data_temp) == (datetime.strptime(data_final, format))) and ((str(converteDataYMDToMDYStrSemHora(str(data_temp)))) not in listaTemp):
                        listaDeDados.append((str(converteDataYMDToMDYStrSemHora(str(data_temp))), '0', membro))
                    
                    if (str(converteDataYMDToMDYStrSemHora(str(data_temp)))) in listaTemp:                        
                        if ((str(converteDataYMDToMDYStrSemHora(str(data_temp - timedelta(days=1))))) not in listaTemp and \
                        ((data_temp - timedelta(days=1)) > (datetime.strptime(data_inicial, format)))):
                            listaDeDados.append((str(converteDataYMDToMDYStrSemHora(str(data_temp - timedelta(days=1)))), '0', membro))
                        if ((str(converteDataYMDToMDYStrSemHora(str(data_temp + timedelta(days=1))))) not in listaTemp and \
                        ((data_temp + timedelta(days=1)) < (datetime.strptime(data_final, format)))):
                            listaDeDados.append((str(converteDataYMDToMDYStrSemHora(str(data_temp + timedelta(days=1)))), '0', membro))
                            
                data_temp += timedelta(days=1)
                
                
                
    #Se tipo_servico != todos  
    else:
        if membro =="*":
            for row in database.LOG.view('log/stats_by_user',startkey=[nome_comunidade, tipo_servico, data_inicial], endkey=[nome_comunidade, tipo_servico, data_final,{}], group="true"):
                if (tipo_log == "leitura" and row.key[4] in VERBOS_LEITURA) or (tipo_log == "escrita" and row.key[4] in VERBOS_ESCRITA) or \
                (tipo_log == "todos" and (row.key[4] in VERBOS_LEITURA or row.key[4] in VERBOS_ESCRITA)):      
                    if row.key[3] not in listaDeMembros:
                        listaDeMembros.append(row.key[3])
                    
                    for i in listaDeDados:
                        if (converteDataYMDToMDYStrSemHora(row.key[2]) in i[0]) and (row.key[3] in i[2]):
                            listaDeDados.append((converteDataYMDToMDYStrSemHora(row.key[2]), str(int(i[1]) + int(row.value)), row.key[3]))
                            listaDeDados.remove(i)
                            existente = True
                            break
                        else:
                            existente = False
                            
                    if not existente:
                        listaDeDados.append((converteDataYMDToMDYStrSemHora(row.key[2]), str(row.value), row.key[3]))
                        listaTemp.append((converteDataYMDToMDYStrSemHora(row.key[2]), row.key[3]))
                          
            while (data_temp) <= (datetime.strptime(data_final, format)):
                for membro in listaDeMembros:
                    #se data_temp = data_incial e não há ações nesta data
                    if ((data_temp) == (datetime.strptime(data_inicial, format))) and ((str(converteDataYMDToMDYStrSemHora(str(data_temp))), membro) not in listaTemp):
                        listaDeDados.append((str(converteDataYMDToMDYStrSemHora(str(data_temp))), '0', membro))
                        
                    if ((data_temp) == (datetime.strptime(data_final, format))) and ((str(converteDataYMDToMDYStrSemHora(str(data_temp))), membro) not in listaTemp):
                        listaDeDados.append((str(converteDataYMDToMDYStrSemHora(str(data_temp))), '0', membro))
                    
                    if (str(converteDataYMDToMDYStrSemHora(str(data_temp))), membro) in listaTemp:                        
                        if ((str(converteDataYMDToMDYStrSemHora(str(data_temp - timedelta(days=1)))), membro) not in listaTemp and \
                        ((data_temp - timedelta(days=1)) > (datetime.strptime(data_inicial, format)))):
                            listaDeDados.append((str(converteDataYMDToMDYStrSemHora(str(data_temp - timedelta(days=1)))), '0', membro))
                        if ((str(converteDataYMDToMDYStrSemHora(str(data_temp + timedelta(days=1)))), membro) not in listaTemp and \
                        ((data_temp + timedelta(days=1)) < (datetime.strptime(data_final, format)))):
                            listaDeDados.append((str(converteDataYMDToMDYStrSemHora(str(data_temp + timedelta(days=1)))), '0', membro))
                            
                data_temp += timedelta(days=1)

        else:
            for row in database.LOG.view('log/stats_by_user',startkey=[nome_comunidade, tipo_servico, data_inicial], endkey=[nome_comunidade, tipo_servico, data_final,{}], group="true"):
                if row.key[3] == membro:
                    if (tipo_log == "leitura" and row.key[4] in VERBOS_LEITURA) or (tipo_log == "escrita" and row.key[4] in VERBOS_ESCRITA) or \
                    (tipo_log == "todos" and (row.key[4] in VERBOS_LEITURA or row.key[4] in VERBOS_ESCRITA)):
                    
                        for i in listaDeDados:
                            if (converteDataYMDToMDYStrSemHora(row.key[2]) in i[0]) and (row.key[3] in i[2]):
                                listaDeDados.append((converteDataYMDToMDYStrSemHora(row.key[2]), str(int(i[1]) + int(row.value)), row.key[3]))
                                listaDeDados.remove(i)
                                existente = True
                                break
                            else:
                                existente = False
                                
                        if not existente:
                            listaDeDados.append((converteDataYMDToMDYStrSemHora(row.key[2]), str(row.value), row.key[3]))
                            listaTemp.append(converteDataYMDToMDYStrSemHora(row.key[2]))
            
            listaDeMembros.append(membro)
            
            while (data_temp) <= (datetime.strptime(data_final, format)):
                for membro in listaDeMembros:
                    #se data_temp = data_incial e não há ações nesta data
                    if ((data_temp) == (datetime.strptime(data_inicial, format))) and ((str(converteDataYMDToMDYStrSemHora(str(data_temp)))) not in listaTemp):
                        listaDeDados.append((str(converteDataYMDToMDYStrSemHora(str(data_temp))), '0', membro))
                        
                    if ((data_temp) == (datetime.strptime(data_final, format))) and ((str(converteDataYMDToMDYStrSemHora(str(data_temp)))) not in listaTemp):
                        listaDeDados.append((str(converteDataYMDToMDYStrSemHora(str(data_temp))), '0', membro))
                    
                    if (str(converteDataYMDToMDYStrSemHora(str(data_temp)))) in listaTemp:                        
                        if ((str(converteDataYMDToMDYStrSemHora(str(data_temp - timedelta(days=1))))) not in listaTempand \
                        ((data_temp - timedelta(days=1)) > (datetime.strptime(data_inicial, format)))):
                            listaDeDados.append((str(converteDataYMDToMDYStrSemHora(str(data_temp - timedelta(days=1)))), '0', membro))
                        if ((str(converteDataYMDToMDYStrSemHora(str(data_temp + timedelta(days=1))))) not in listaTempand \
                        ((data_temp + timedelta(days=1)) < (datetime.strptime(data_final, format)))):
                            listaDeDados.append((str(converteDataYMDToMDYStrSemHora(str(data_temp + timedelta(days=1)))), '0', membro))
                            
                data_temp += timedelta(days=1)
            
            
                    
    listaDeDados.sort(key=lambda x: x[2])
    listaDeDados.sort(key=lambda x: (converteDataMDYToYMDStrSemHora(x[0])))
    #listaDeDados.sort(key=lambda x: str(x[0]).split("/")[1])        #str(converteDataMDYToYMDStrSemHora(x[0])))
    #listaDeDados.sort(key=lambda x: str(x[0]).split("/")[0])
    #listaDeDados.sort(key=lambda x: str(x[0]).split("/")[2])

    return (listaDeDados, listaDeMembros)

def get_community_object_action_list(nome_comunidade, data_inicial, data_final, tipo_servico, tipo_log, format):
    listaDeDados = []
    listaDeObjetos = []
    listaTemp = []
    existente = False
    data_temp = datetime.strptime(data_inicial, format)
       
    if tipo_servico == "todos":
        for row in database.LOG.view('log/stats_by_all_objects',startkey=[nome_comunidade, data_inicial], endkey=[nome_comunidade, data_final,{}], group="true"):
                if (tipo_log == "leitura" and row.key[3] in VERBOS_LEITURA) or (tipo_log == "escrita" and row.key[3] in VERBOS_ESCRITA) or \
                    (tipo_log == "todos" and (row.key[3] in VERBOS_LEITURA or row.key[3] in VERBOS_ESCRITA)):
                    if row.key[4] != "none":
                        nome_objeto = core.dispatcher.URL_TO_PAGETITLE[row.key[4]]+": "+row.key[2]
                          
                    if nome_objeto not in listaDeObjetos:
                        listaDeObjetos.append(nome_objeto)
                    
                    for i in listaDeDados:
                        if (converteDataYMDToMDYStrSemHora(row.key[1]) in i[0]) and (nome_objeto in i[2]):
                            listaDeDados.append((converteDataYMDToMDYStrSemHora(row.key[1]), str(int(i[1]) + int(row.value)), nome_objeto))
                            listaDeDados.remove(i)
                            existente = True
                            break
                        else:
                            existente = False
                    
                    if not existente:    
                        listaDeDados.append((converteDataYMDToMDYStrSemHora(row.key[1]), str(row.value), nome_objeto))
                        listaTemp.append((converteDataYMDToMDYStrSemHora(row.key[1]), nome_objeto))
                      
        while (data_temp) <= (datetime.strptime(data_final, format)):
            for object in listaDeObjetos:
                #se data_temp = data_incial e não há ações nesta data
                if ((data_temp) == (datetime.strptime(data_inicial, format))) and ((str(converteDataYMDToMDYStrSemHora(str(data_temp))), object) not in listaTemp):
                    listaDeDados.append((str(converteDataYMDToMDYStrSemHora(str(data_temp))), '0', object))
                    
                if ((data_temp) == (datetime.strptime(data_final, format))) and ((str(converteDataYMDToMDYStrSemHora(str(data_temp))), object) not in listaTemp):
                    listaDeDados.append((str(converteDataYMDToMDYStrSemHora(str(data_temp))), '0', object))
                
                if (str(converteDataYMDToMDYStrSemHora(str(data_temp))), object) in listaTemp:                
                    if (((str(converteDataYMDToMDYStrSemHora(str(data_temp - timedelta(days=1)))), object) not in listaTemp) and \
                    ((data_temp - timedelta(days=1)) > (datetime.strptime(data_inicial, format)))):
                        listaDeDados.append((str(converteDataYMDToMDYStrSemHora(str(data_temp - timedelta(days=1)))), '0', object))
                        
                    if ((str(converteDataYMDToMDYStrSemHora(str(data_temp + timedelta(days=1)))), object) not in listaTemp and \
                    ((data_temp + timedelta(days=1)) < (datetime.strptime(data_final, format)))):
                        listaDeDados.append((str(converteDataYMDToMDYStrSemHora(str(data_temp + timedelta(days=1)))), '0', object))
                                
            data_temp += timedelta(days=1)
                
    else:
        for row in database.LOG.view('log/stats_by_object',startkey=[nome_comunidade, tipo_servico, data_inicial], endkey=[nome_comunidade, tipo_servico, data_final,{}], group="true"):
                if (tipo_log == "leitura" and row.key[4] in VERBOS_LEITURA) or (tipo_log == "escrita" and row.key[4] in VERBOS_ESCRITA) or \
                (tipo_log == "todos" and (row.key[4] in VERBOS_LEITURA or row.key[4] in VERBOS_ESCRITA)):   
                    if row.key[3] not in listaDeObjetos:
                        listaDeObjetos.append(row.key[3])
                    
                    for i in listaDeDados:
                        if (converteDataYMDToMDYStrSemHora(row.key[2]) in i[0]) and (row.key[3] in i[2]):
                            listaDeDados.append((converteDataYMDToMDYStrSemHora(row.key[2]), str(int(i[1]) + int(row.value)), row.key[3]))
                            listaDeDados.remove(i)
                            existente = True
                            break
                        else:
                            existente = False
                            
                    if not existente:
                        listaDeDados.append((converteDataYMDToMDYStrSemHora(row.key[2]), str(row.value), row.key[3]))
                        listaTemp.append((converteDataYMDToMDYStrSemHora(row.key[2]), row.key[3]))
             
             
        while (data_temp) <= (datetime.strptime(data_final, format)):
            for object in listaDeObjetos:
                #se data_temp = data_incial e não há ações nesta data
                if ((data_temp) == (datetime.strptime(data_inicial, format))) and ((str(converteDataYMDToMDYStrSemHora(str(data_temp))), object) not in listaTemp):
                    listaDeDados.append((str(converteDataYMDToMDYStrSemHora(str(data_temp))), '0', object))
                    
                if ((data_temp) == (datetime.strptime(data_final, format))) and ((str(converteDataYMDToMDYStrSemHora(str(data_temp))), object) not in listaTemp):
                    listaDeDados.append((str(converteDataYMDToMDYStrSemHora(str(data_temp))), '0', object))
                
                if (str(converteDataYMDToMDYStrSemHora(str(data_temp))), object) in listaTemp:                        
                    if (((str(converteDataYMDToMDYStrSemHora(str(data_temp - timedelta(days=1)))), object) not in listaTemp) and \
                    ((data_temp - timedelta(days=1)) > (datetime.strptime(data_inicial, format)))):
                        listaDeDados.append((str(converteDataYMDToMDYStrSemHora(str(data_temp - timedelta(days=1)))), '0', object))
                        
                    if ((str(converteDataYMDToMDYStrSemHora(str(data_temp + timedelta(days=1)))), object) not in listaTemp and \
                    ((data_temp + timedelta(days=1)) < (datetime.strptime(data_final, format)))):
                        listaDeDados.append((str(converteDataYMDToMDYStrSemHora(str(data_temp + timedelta(days=1)))), '0', object))
                                
            data_temp += timedelta(days=1)
                    
    listaDeDados.sort(key=lambda x: x[2])
    listaDeDados.sort(key=lambda x: (converteDataMDYToYMDStrSemHora(x[0])))
    #listaDeDados.sort(key=lambda x: str(x[0]).split("/")[1])        #str(converteDataMDYToYMDStrSemHora(x[0])))
    #listaDeDados.sort(key=lambda x: str(x[0]).split("/")[0])
    #listaDeDados.sort(key=lambda x: str(x[0]).split("/")[2])

    return (listaDeDados, listaDeObjetos)

def get_community_users_action_list_bar_chart(nome_comunidade, data_inicial, data_final, tipo_servico, tipo_log, format):
    listaDeDados = []
    listaDeMembros = []
    existente = False

    if tipo_servico == "todos":
        for row in database.LOG.view('log/users_by_all_types_bar_chart',startkey=[nome_comunidade, data_inicial, " ", "escrita"], endkey=[nome_comunidade, data_final, "z","leitura",{}], group="true"):            
            if ((tipo_log == row.key[3]) or (tipo_log=="todos")):
                for i in listaDeDados:
                    if row.key[2] == i[0]:
                        existente = True
                        if row.key[3] == "escrita":
                            listaDeDados.append((row.key[2], str(row.value+int(i[1])), i[2]))
                            listaDeDados.remove(i)
                        elif row.key[3] == "leitura":
                            listaDeDados.append((row.key[2], i[1], str(row.value+int(i[2]))))
                            listaDeDados.remove(i)
                        break
                    else:
                        existente = False
                        
                if not existente:
                        if row.key[3] == "escrita":
                            listaDeDados.append((row.key[2], str(row.value), "0"))
                            listaDeMembros.append(row.key[2])
                        elif row.key[3] == "leitura":
                            listaDeDados.append((row.key[2], "0", str(row.value)))
                            listaDeMembros.append(row.key[2])
    else:

        for row in database.LOG.view('log/users_by_types_bar_chart',startkey=[nome_comunidade, tipo_servico, data_inicial, " ", "escrita"], endkey=[nome_comunidade, tipo_servico, data_final, "z", "leitura",{}], group="true"):
            for i in listaDeDados:
                if row.key[3] == i[0]:
                    existente = True
                    if row.key[4] == "escrita":
                        listaDeDados.append((row.key[3], str(row.value+int(i[1])), i[2]))
                        listaDeDados.remove(i)
                    elif row.key[4] == "leitura":
                        listaDeDados.append((row.key[3], i[1], str(row.value+int(i[2]))))
                        listaDeDados.remove(i)
                    break
                else:
                    existente = False
                    
            if not existente:
                    if row.key[4] == "escrita":
                        listaDeDados.append((row.key[3], str(row.value), "0"))
                        listaDeMembros.append(row.key[3])
                    elif row.key[4] == "leitura":
                        listaDeDados.append((row.key[3], "0", str(row.value)))
                        listaDeMembros.append(row.key[3])

                        
    listaDeDados.sort(key=lambda x: (int(x[1])+int(x[2])), reverse = True)
                         
    return (listaDeDados, listaDeMembros)


def get_community_object_action_list_bar_chart(nome_comunidade, data_inicial, data_final, tipo_servico, tipo_log, format):
    listaDeDados = []
    listaDeObjetos = []
    existente = False

    if tipo_servico == "todos":
        for row in database.LOG.view('log/objects_by_all_types_bar_chart',startkey=[nome_comunidade, data_inicial, " ", "escrita"], endkey=[nome_comunidade, data_final, "z","leitura",{}], group="true"):            
            if ((tipo_log == row.key[3]) or (tipo_log=="todos")):
                for i in listaDeDados:
                    if row.key[2] == i[0]:
                        existente = True
                        if row.key[3] == "escrita":
                            listaDeDados.append((row.key[2], str(row.value+int(i[1])), i[2]))
                            listaDeDados.remove(i)
                        elif row.key[3] == "leitura":
                            listaDeDados.append((row.key[2], i[1], str(row.value+int(i[2]))))
                            listaDeDados.remove(i)
                        break
                    else:
                        existente = False
                        
                if not existente:
                        if row.key[3] == "escrita":
                            listaDeDados.append((row.key[2], str(row.value), "0"))
                            listaDeObjetos.append(row.key[2])
                        elif row.key[3] == "leitura":
                            listaDeDados.append((row.key[2], "0", str(row.value)))
                            listaDeObjetos.append(row.key[2])
    else:
        for row in database.LOG.view('log/objects_by_types_bar_chart',startkey=[nome_comunidade, tipo_servico, data_inicial, " ", "escrita"], endkey=[nome_comunidade, tipo_servico, data_final, "z", "leitura",{}], group="true"):
            for i in listaDeDados:
                if row.key[3] == i[0]:
                    existente = True
                    if row.key[4] == "escrita":
                        listaDeDados.append((row.key[3], str(row.value+int(i[1])), i[2]))
                        listaDeDados.remove(i)
                    elif row.key[4] == "leitura":
                        listaDeDados.append((row.key[3], i[1], str(row.value+int(i[2]))))
                        listaDeDados.remove(i)
                    break
                else:
                    existente = False
                    
            if not existente:
                    if row.key[4] == "escrita":
                        listaDeDados.append((row.key[3], str(row.value), "0"))
                        listaDeObjetos.append(row.key[3])
                    elif row.key[4] == "leitura":
                        listaDeDados.append((row.key[3], "0", str(row.value)))
                        listaDeObjetos.append(row.key[3])
    listaDeDados.sort(key=lambda x: (int(x[1])+int(x[2])), reverse = True)   
    return (listaDeDados, listaDeObjetos)

def get_maximum_axis_size(listaDeDados, periodo_estatistica="diario"):
    maximo = 0
    if periodo_estatistica == "total":
        for object in listaDeDados:
            temp = int(object[1]) + int(object[2])
            if temp > maximo:
                maximo = temp
        
        if maximo <= 10:
            return "10"
        else:
            if (maximo % 10) != 0:
                maximo = (10 - (maximo % 10)) + maximo
            return str(maximo)
    elif periodo_estatistica == "diario":
        for object in listaDeDados:
            temp = int(object[1])
            if temp > maximo:
                maximo = temp
                
        if maximo <= 10:
            return "10"
        else:
            if (maximo % 10) != 0:
                maximo = (10 - (maximo % 10)) + maximo
            return str(maximo)