# -*- coding: utf-8 -*-
"""
################################################
Oi Tonomundo - NCE/UFRJ
################################################

:Author: Eduardo Paz
:Contact: edupaz@nce.ufrj.br
:Date: $Date: 2010/08/02  $
:Status: This is a "work in progress"
:Revision: $Revision: 0.01 $
:Home: ``
:Copyright:  
"""

import time
import datetime as dt
from datetime import datetime, timedelta

_diasemana_extenso = (u'Segunda-feira', u'Terça-feira', u'Quarta-feira',
                      u'Quinta-feira', u'Sexta-feira', u'Sábado', u'Domingo')
_diasemana = (u'segunda', u'terça', u'quarta',
              u'quinta', u'sexta', u'sábado', u'domingo')
_meses = (u'janeiro', u'fevereiro', u'março', u'abril', u'maio', u'junho',
          u'julho', u'agosto', u'setembro', u'outubro', u'novembro', u'dezembro')

def date_now():
    return datetime.now()

def str_to_date(date_str):
    return time.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")

def short_datetime(date_str, include_year=True, include_separator=u" às "):
    try:
        date = time.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")
        #return time.strftime("%d/%m/%Y %H:%M:%S", date)
        if include_year:
            return time.strftime((u"%d/%m/%Y" + include_separator + u"%H:%M").encode('utf-8'), date).decode('utf-8')
        else:
            return time.strftime((u"%d/%m" + include_separator + u"%H:%M").encode('utf-8'), date).decode('utf-8')
    except ValueError:
        return u'Data inválida!'

def short_date(date_str, include_year=False):
    try:
        date = time.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")
        if include_year:
            return time.strftime("%d/%m/%Y", date)
        else:
            return time.strftime("%d/%m", date)
    except ValueError:
        return u'Data inválida!'

def elapsed_time(data):
    # Verifica quanto tempo foi decorrido da data até agora
    # Retorna um objeto do tipo datetime.timedelta
    #
    hoje = datetime.now()

    inicio = time.strptime(data,"%Y-%m-%d %H:%M:%S.%f")
    inicio = datetime(inicio.tm_year, inicio.tm_mon, inicio.tm_mday,
              inicio.tm_hour, inicio.tm_min, inicio.tm_sec)
    return hoje - inicio

def human_date(strdate):
    if strdate:
        delta = str(elapsed_time(strdate))
        
        if delta.find(',') > 0:
            days, hours = delta.split(',')
            days = int(days.split()[0].strip())
            hours, minutes, seconds = hours.split(':')
        else:
            hours, minutes, seconds = delta.split(':')
            days = 0
        seconds = seconds.split('.')[0]
        days, hours, minutes, seconds = int(days), int(hours), int(minutes), int(seconds)
        
        if days >= 365:
            return full_month_date(strdate, include_year=True, include_time=True)
        elif days >= 3:
            return full_month_date(strdate, include_time=True)
        elif days >= 1:
            return week_day(strdate, include_time=True)
        elif hours >= 2:
            return u"há %d horas" % hours
        elif hours == 1:
            return u"há \u00B11 hora"
        elif minutes >= 2:
            return u"há %d minutos" % minutes
        elif minutes == 1:
            return u"há \u00B11 minuto"
        elif seconds >= 2:
            return u"há %d segundos" % seconds
        else:
            return u"há \u00B11 segundo"
    else:
        return ""

def old_human_date(strdate):
    # converts a string with date and time to the 
    # format "X days, Y hours ago"

    my_struct_time = time.strptime(strdate,"%Y-%m-%d %H:%M:%S.%f")
    date_time = datetime(my_struct_time.tm_year, my_struct_time.tm_mon, my_struct_time.tm_mday,
                         my_struct_time.tm_hour, my_struct_time.tm_min, my_struct_time.tm_sec)
    current_datetime = datetime.now()
    delta = str(current_datetime - date_time)
    if delta.find(',') > 0:
        days, hours = delta.split(',')
        days = int(days.split()[0].strip())
        hours, minutes = hours.split(':')[0:2]
    else:
        hours, minutes = delta.split(':')[0:2]
        days = 0
    days, hours, minutes = int(days), int(hours), int(minutes)
    datelets =[]
    years, months, xdays = None, None, None
    plural = lambda x: 's' if x!=1 else ''
    monthplural = lambda x: 'es' if x!=1 else ''
    if days >= 365:
        years = int(days/365)
        datelets.append('%d ano%s' % (years, plural(years)))
        days = days%365
    if days >= 30 and days < 365:
        months = int(days/30)
        datelets.append(u'%d mes%s' % (months, monthplural(months)))
        days = days%30
    if not years and days > 0 and days < 30:
        xdays =days
        datelets.append('%d dia%s' % (xdays, plural(xdays)))
    if not (months or years) and hours != 0:
        datelets.append('%d hora%s' % (hours, plural(hours)))
    if not (xdays or months or years):
        if minutes>0:
            datelets.append('%d minuto%s' % (minutes, plural(minutes)))
        else:
            datelets.append('alguns segundos')
    return u'há ' + ', '.join(datelets) + u'.'


def full_week_date(strdate, include_time=False):
    # retorna data nos formatos:
    # Quinta-feira, 27 de Outubro de 2011
    # Quinta-feira, 27 de Outubro de 2011 às 10:20
    #
    mytime = time.strptime(strdate,"%Y-%m-%d %H:%M:%S.%f")
    
    str_ret = _diasemana_extenso[mytime.tm_wday] + ", " + str(mytime.tm_mday) + " de " + _meses[mytime.tm_mon-1] + " de " + str(mytime.tm_year)
    if include_time:
        str_ret = str_ret + " às " + str(mytime.tm_hour) + ":" + str(mytime.tm_min)
    return str_ret

def week_day(strdate, include_time=False):
    # retorna dia da semana nos formatos:
    # Quinta
    # Quinta às 10:20
    #
    mytime = time.strptime(strdate,"%Y-%m-%d %H:%M:%S.%f")
    
    str_ret = _diasemana[mytime.tm_wday]
    if include_time:
        str_ret = str_ret + u" às %02d:%02d" % (mytime.tm_hour, mytime.tm_min)
    return str_ret

def full_month_date(strdate, include_year=False, include_time=False):
    # retorna data nos formatos:
    # 27 de Outubro
    # 27 de Outubro às 10:17
    # 27 de Outubro de 2011
    # 27 de Outubro de 2011 às 10:17
    #
    mytime = time.strptime(strdate,"%Y-%m-%d %H:%M:%S.%f")
    
    str_ret = str(mytime.tm_mday) + " de " + _meses[mytime.tm_mon-1] 
    if include_year:
        str_ret = str_ret + " de " + str(mytime.tm_year)
    if include_time:
        str_ret = str_ret + u" às %02d:%02d" % (mytime.tm_hour, mytime.tm_min)
    return str_ret


def seconds_to_weekday(wkday, hh, mm, ss):
    # wkday = segunda:0, terça:1, quarta:2, quinta:3, sexta:4, sabado:5, domingo:6
    #         diariamente:9
    today = datetime.now()
    
    if wkday == 9:
        nextDay = today.replace(today.year, today.month, today.day, hh, mm, ss)
        # se a hora já passou, só roda amanhã
        if nextDay < today: nextDay = nextDay + timedelta( days = +1 )
        
    else:
        # cálculo do número de dias que faltam para o dia da semana agendado
        numDays = wkday - today.weekday()
        if numDays < 0: numDays = numDays + 7
        # data agendada
        nextDay = today + timedelta( days = +numDays )
        nextDay = nextDay.replace(nextDay.year, nextDay.month, nextDay.day, hh, mm, ss)
        # se o dia é hoje, mas a hora já passou, só roda na próxima semana
        if nextDay < today: nextDay = nextDay + timedelta( days = +7 )
    
    # calcula quanto tempo falta para chegar nextDay
    delta = nextDay - today
    return (delta.days * 24 * 60 * 60 + delta.seconds)
    

def maiorData(data1, data2, short=False):
    """ retorna True se data1 > data2, False caso contrário """
    if short == True:
        inicio = time.strptime(data1,"%d/%m/%Y %H:%M")
        fim = time.strptime(data2,"%d/%m/%Y %H:%M")
    else:
        inicio = time.strptime(data1,"%Y-%m-%d %H:%M:%S.%f")
        fim = time.strptime(data2,"%Y-%m-%d %H:%M:%S.%f")
    
    inicio = datetime(inicio.tm_year, inicio.tm_mon, inicio.tm_mday,
              inicio.tm_hour, inicio.tm_min, inicio.tm_sec)            
    
    fim = datetime(fim.tm_year, fim.tm_mon, fim.tm_mday,
                fim.tm_hour, fim.tm_min, fim.tm_sec)

    return inicio > fim


def maiorHora(hora1, hora2, short=False):
    """ retorna True se hora1 > hora2, False caso contrário """
    if short == True:
        inicio = time.strptime(hora1,"%H:%M")
        fim = time.strptime(hora2,"%H:%M")
    else:
        inicio = time.strptime(hora1,"%H:%M:%S.%f")
        fim = time.strptime(hora2,"%H:%M:%S.%f")
    
    inicio = dt.time(inicio.tm_hour, inicio.tm_min, inicio.tm_sec)            
    
    fim = dt.time(fim.tm_hour, fim.tm_min, fim.tm_sec)

    return inicio > fim

def verificaIntervaloDMY(data_inicio, data_fim):
    # Verifica se a data de hoje está dentro do intervalo data_inicio, data_fim
    
    hoje = datetime.now()

    try:
        inicio = time.strptime(data_inicio,"%d/%m/%Y %H:%M")
    except ValueError:
        inicio = time.strptime(data_inicio,"%d/%m/%Y")
    inicio = datetime(inicio.tm_year, inicio.tm_mon, inicio.tm_mday,
              inicio.tm_hour, inicio.tm_min, inicio.tm_sec)
    
    try:
        fim = time.strptime(data_fim,"%d/%m/%Y %H:%M")
    except ValueError:
        fim = time.strptime(data_fim,"%d/%m/%Y")
    fim = datetime(fim.tm_year, fim.tm_mon, fim.tm_mday,
                fim.tm_hour, fim.tm_min, fim.tm_sec)
    
    if fim < hoje:
        return 1     # data_fim já passou
    elif inicio <= hoje:
        return 0    # dentro do período    
    else:
        return -1    # data_inicio ainda não chegou


def verificaIntervalo(data_inicio, data_fim):
    # Verifica se a data de hoje está dentro do intervalo data_inicio, data_fim
    
    hoje = datetime.now()

    inicio = time.strptime(data_inicio,"%Y-%m-%d %H:%M:%S.%f")
    inicio = datetime(inicio.tm_year, inicio.tm_mon, inicio.tm_mday,
              inicio.tm_hour, inicio.tm_min, inicio.tm_sec)            
    fim = time.strptime(data_fim,"%Y-%m-%d %H:%M:%S.%f")
    fim = datetime(fim.tm_year, fim.tm_mon, fim.tm_mday,
                fim.tm_hour, fim.tm_min, fim.tm_sec)
        
    if fim < hoje:
        return 1     # data_fim já passou
    elif inicio <= hoje:
        return 0    # dentro do período    
    else:
        return -1    # data_inicio ainda não chegou    
    


def converteDataDMYToStr (strdata):
    try:
        (data, hora) = strdata.split(" ")
        (dia, mes, ano) = data.split("/")
        (hora,min) = hora.split(":")
        return "%04d-%02d-%02d %02d:%02d:00.000000" % (int(ano), int(mes), int(dia), int(hora), int(min))

    except ValueError:
        return ""
    
def converteDataDMYToYMDStr (strdata):
    try:
        #(data, hora) = strdata.split(" ")
        (dia, mes, ano) = strdata.split("/")
        return "%04d-%02d-%02d" % (int(ano), int(mes), int(dia))

    except ValueError:
        return ""
    
# ---------------------------------------------------------------------------------
    
def converteDataDMYToMDYStrSemHora (strdata):
    try:
   #     (data, hora) = strdata.split(" ")
        (dia, mes, ano) = strdata.split("-")
        return "%02d/%02d/%04d" % (int(mes), int(dia), int(ano))

    except ValueError:
        return ""
        
def converteDataYMDToMDYStrSemHora (strdata):
    try:
        (data, hora) = strdata.split(" ")
        (ano, mes, dia) = data.split("-")
        return "%02d/%02d/%04d" % (int(mes), int(dia), int(ano))

    except ValueError:
        data = strdata
        (ano, mes, dia) = data.split("-")
        return "%02d/%02d/%04d" % (int(mes), int(dia), int(ano))   
    
def converteDataMDYToYMDStrSemHora (strdata):
    try:
        (data, hora) = strdata.split(" ")
        (mes, dia, ano) = data.split("/")
        return "%04d/%02d/%02d" % (int(ano), int(mes), int(dia))

    except ValueError:
        data = strdata
        (mes, dia, ano) = data.split("/")
        return "%04d/%02d/%02d" % (int(ano), int(mes), int(dia))      
        
def calculaDiferencaDatas(data_inicio, data_fim):
    # Calcula a diferença entre as datas inicial e final
    
    inicio = time.strptime(data_inicio,"%Y-%m-%d")
    inicio = datetime(inicio.tm_year, inicio.tm_mon, inicio.tm_mday)        
    fim = time.strptime(data_fim,"%Y-%m-%d")
    fim = datetime(fim.tm_year, fim.tm_mon, fim.tm_mday)
        
    return fim-inicio

def calculaHoraFinal(hora_inicio, duracao):
    # Calcula a hora final como hora inicial + duracao
    # formato utilizado "HH:MM"
    
    fulldate = datetime(100, 1, 1, int(hora_inicio[0:2]), int(hora_inicio[3:]), 0)
    fulldate = fulldate + timedelta(hours=int(duracao[0:2]), minutes=int(duracao[3:]))
    hora_final = str(fulldate.time())
    return hora_final[0:5]

    
