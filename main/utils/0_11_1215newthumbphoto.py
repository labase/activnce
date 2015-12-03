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
        , tags = [] 
        , description = ""
        , cod_institute = ""
        , institute = ""
        , amigos = []
        , amigos_pendentes = []
        , amigos_convidados = []
        , comunidades = []
        , comunidades_pendentes = []
        , papeis = []
        , mykeys = []
        , privacidade = u"Pública"           # Pode ser: Pública ou Privada
        , blog_aberto = "N"                  # Indica se o blog deste usuário 
                                             # pode ser acessado de fora da plataforma
        , upload_quota = 10 * 1024 * 1024    # max 10 Mb
        , upload_size = 0  
        , notify = "2"  # notificações de e-mail
                        # 0 = não receber
                        # 1 = receber apenas um boletim semanal
                        # 2 = receber sempre
        , data_cri = ""
        , data_alt = ""
    )


_EMPTYCOMMUNITY = lambda: dict(
          name = ""
        , description = ""
        , tags = []
        , owner = ""
        , participantes_pendentes = []
        , participantes = []
        , comunidades = []                   # comunidades em que esta comunidade está incluída
        , upload_quota = 60 * 1024 * 1024    # max 60 Mb
        , upload_size = 0
        , papeis = []
        , admins = []
        , cod_institute = ""
        , institute = ""
        , privacidade = ""    # Pública ou Privada
        , blog_aberto = "N"   # Indica se o blog deste usuário 
                              # pode ser acessado de fora da plataforma
        , participacao = ""   # Mediante Convite, Voluntária ou Obrigatória
        , data_cri = ""
        , data_alt = ""
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

        
def Thumbnail(content, size="G"):
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
            imFile = imFile.convert("RGB")
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


def main():
    for item in REGISTRY:
        if "passwd" in REGISTRY[item]:
            user_data = _EMPTYMEMBER()
        else:
            user_data = _EMPTYCOMMUNITY()
        
        user_data.update(REGISTRY[item])
        
        if "photo" not in user_data or not user_data["photo"]:
            print "Registro ignorado:", item
            continue
        
        # remove o atributo photo do REGISTRY
        photo = user_data["photo"]
        del user_data["photo"]
        REGISTRY[item] = user_data
        
        # Lê attachment com a foto original
        foto_original = REGISTRY.get_attachment(item, photo)

        if foto_original:
            # cria os novos thumbnails da foto
            thumb_g = Thumbnail(foto_original, "G")
            if not thumb_g:
                print "*** Erro na leitura da foto de", item
                continue
            
            thumb_m = Thumbnail(foto_original, "M")
            if not thumb_m:
                print "*** Erro na leitura da foto de", item
                continue
            
            thumb_p = Thumbnail(foto_original, "P")
            if not thumb_p:
                print "*** Erro na leitura da foto de", item
                continue
            
            try:
                REGISTRY.put_attachment(REGISTRY[item],
                       thumb_g, "thumbG.png", "image/png")
                REGISTRY.put_attachment(REGISTRY[item],
                       thumb_m, "thumbM.png", "image/png")
                REGISTRY.put_attachment(REGISTRY[item],
                       thumb_p, "thumbP.png", "image/png")
            except Exception as detail:
                print "*** Erro ao salvar attachments no banco", item
                continue
    
            try:
                REGISTRY.delete_attachment(REGISTRY[item], photo)
            except Exception as detail:
                print "*** Erro ao remover attachment do banco", item
                continue


    
if __name__ == "__main__":
    main()