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

from PIL import Image
import StringIO

def thumbnail(content, size="G"):
    ''' Rotina para gerar uma imagem thumbnail de um arquivo de imagem '''
    
    #tbWidth  = 240 # largura padrao em pixels para o thumbnail
    #tbHeight = 320 # altura  padrao em pixels para o thumbnail

    # Define largura e altura padrão de acordo com o tamanho do thumbnail
    if size=="G":
        (tbWidth, tbHeight) = (120, 160)
    elif size=="M":
        (tbWidth, tbHeight) = (45, 60)
    elif size=="P":
        (tbWidth, tbHeight) = (30, 40)
    else:
        return ""       # tamanho do thumbnail inválido
    
    # usa um wraper StringIO para transformar os bytes da string numa imagem
    try:
            imFile = Image.open(StringIO.StringIO(content))
            imFile = imFile.convert("RGBA")
    except IOError:
            return ""   # erro na leitura da imagem
    
    (imWidth,imHeight) = imFile.size
    imAspect = imWidth / float(imHeight) # aspecto da imagem original
    tbAspect = tbWidth / float(tbHeight) # aspecto do thumbnail (padrao 3x4)
    
    # determina melhor forma para corte (conforme orientacao, portrait ou landscape)
    if imAspect > tbAspect:
            # imagem tipo landscape (escala na largura, mantendo altura)
            zoom = tbHeight / float(imHeight)
            imWidth = int(zoom*imWidth)
            imNew = imFile.resize((imWidth,tbHeight),Image.ANTIALIAS)
            
            # determina pixel do corte (corta na largura, canto superior esquerdo)
            pxLeft = (imWidth-tbWidth)/2
            pxTop  = 0
    else:
            # imagem tipo portrait (escala na altura, mantendo largura)
            zoom = tbWidth/ float(imWidth)
            imHeight = int(zoom*imHeight)
            imNew = imFile.resize((tbWidth,imHeight),Image.ANTIALIAS)
            
            # determina pixel do corte (corta na altura, canto superior esquerdo)
            pxLeft = 0
            pxTop  = (imHeight-tbHeight)/2

    # pixel de corte (canto inferior direito)
    pxRight  = pxLeft+tbWidth
    pxBottom = pxTop +tbHeight

    # efetua o corte conforme regiao de clipping
    clip = (pxLeft,pxTop,pxRight,pxBottom)
    imNew = imNew.crop(clip)

    # usa um wraper StringIO para salvar os bytes da imagem numa string
    buff = StringIO.StringIO()
    try:
            imNew.save(buff,"PNG")
    except IOError:
            return ""
    
    bytes = buff.getvalue() 
    buff.close()
    return bytes


def resizeImage(content, size="G"):
    ''' Rotina para gerar uma imagem reduzida de um arquivo de imagem '''
    
    # Define largura e altura padrão de acordo com o tamanho da redução
    if size=="G":
        (tbWidth, tbHeight) = (1024, 768)
    elif size=="P":
        (tbWidth, tbHeight) = (240, 180)
    else:
        return ""       # tamanho da redução inválida
    
    # usa um wraper StringIO para transformar os bytes da string numa imagem
    try:
            imFile = Image.open(StringIO.StringIO(content))
            imFile = imFile.convert("RGBA")
    except IOError:
            return ""   # erro na leitura da imagem
    
    (imWidth,imHeight) = imFile.size
    if imWidth > tbWidth or imHeight > tbHeight:
        if imWidth < imHeight:
            # imagem original é portrait
            zoom = tbHeight / float(imHeight)
        else:
            #imagem original é landscape
            zoom = tbWidth / float(imWidth)
        imWidth = int(zoom*imWidth)
        imHeight = int(zoom*imHeight)
        imNew = imFile.resize((imWidth,imHeight),Image.ANTIALIAS)
    else:
        imNew = imFile
        
    # usa um wraper StringIO para salvar os bytes da imagem numa string
    buff = StringIO.StringIO()
    try:
            imNew.save(buff,"PNG")
    except IOError:
            return ""
        
    bytes = buff.getvalue() 
    buff.close()
    return bytes
