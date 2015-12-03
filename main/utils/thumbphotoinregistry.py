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
from PIL import Image
import StringIO


_DOCBASES = ['registry']

_EMPTYMEMBER = lambda: dict(
          user = ""
        , passwd = ""
        , name = ""
        , lastname = ""
        , email = ""
        , photo = ""
        , amigos = []
        , amigos_pendentes = []
        , amigos_convidados = []
        , comunidades = []
        , comunidades_pendentes = []
    )

_EMPTYCOMMUNITY = lambda: dict(
          name = ""
        , description = ""
        , owner = ""
        , photo = ""
        , participantes_pendentes = []
        , participantes = []
    )

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

def Thumbnail(content):
	''' Rotina para gerar uma imagem thumbnail de um arquivo de imagem '''
	
	tbWidth  = 240 # largura padrao em pixels para o thumbnail
	tbHeight = 320 # altura  padrao em pixels para o thumbnail
	
	# usa um wraper StringIO para transformar os bytes da string numa imagem
	try:
		imFile = Image.open(StringIO.StringIO(content))
                imFile = imFile.convert("RGB")
	except IOError:
		return ""
	
	
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

def main():
    for item in REGISTRY:
          if "passwd" in REGISTRY[item]:
              print "user: %s" % REGISTRY[item]["user"]
              user_data = _EMPTYMEMBER()
              user_data.update(REGISTRY[item])
              REGISTRY[item] = user_data            
          else:
              print "community: %s" % REGISTRY[item]["name"]
              user_data = _EMPTYCOMMUNITY()
              user_data.update(REGISTRY[item])
              REGISTRY[item] = user_data            

          
          # cria um thumbnail da foto
          thumb = Thumbnail(REGISTRY.get_attachment(item, user_data["photo"]))
          if not thumb:
              print "Thumb not found. Para %s" % item
          else:
                    try:
                        REGISTRY[item] = user_data
                        REGISTRY.put_attachment(REGISTRY[item],
                               thumb,
                               REGISTRY[item]["photo"],
                               "image/png")
                        print "Salvei %s no banco" % item
                    except Exception as detail:
                        print "Não salvou %s no banco" % item
                        
    
if __name__ == "__main__":
    main()