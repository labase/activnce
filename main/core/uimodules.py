# -*- coding: utf-8 -*-
#!/usr/bin/env python

import math
import urlparse
import urllib

import tornado.web
import rating.model

       
""" Molduras """

class ShowMolduraInicio (tornado.web.UIModule):
    def render(self, titulo="", alinha="left", width="", links=[], panel="panel-primary"):
        """
        links = lista de tuplas com os seguintes valores:
                0) hint do icone (onmouseover)
                1) caminho da imagem do ícone
                2) url do link (opcional)
                3) código de script a ser executado no onclick (opcional)
                4) legenda adicional a ser escrita ao lado da imagem (opcional)
                5) boolean indicando se o link deve ser aberto num popup (True) ou em nova página (False) (opcional)
        """
        return self.render_string("modules/widgets/moldura-inicio.html", titulo=titulo, alinha=alinha, width=width, links=links, panel=panel)

class ShowMolduraFim (tornado.web.UIModule):
    def render(self, form=""):
        return self.render_string("modules/widgets/moldura-fim.html", form=form)
    
    
""" Exibição de foto de usuário/comunidade """

class ShowFoto (tornado.web.UIModule):
    def render(self, src="", texto="", alt="", link="", pequeno=True, online=False, admin=False, icone="", chat=""):
        #width  = 45 if pequeno else 75
        width  = 30 if pequeno else 45
        height = 4*width/3
        #height = width
        padd   = 3 if pequeno else 5
        
        return self.render_string("modules/widgets/foto.html", width=width, height=height, padd=padd, src=src, chat=chat, texto=texto, alt=alt, link=link, online=online, admin=admin, icone=icone)

class ShowMolduraFoto (tornado.web.UIModule):
    def render(self, src, alt="", link=""):
        return self.render_string("modules/widgets/moldura-foto.html", src=src, alt=alt, link=link)
    
    
""" Exibição de menu de ícones. Usado no control-panel de usuário e comunidade """

class ShowMenuLinks (tornado.web.UIModule):
    def render(self, alinha="right", width="", links=[]):
        return self.render_string("modules/widgets/menu-links.html", alinha=alinha, width=width, links=links)        
    

class ShowMenuLeft (tornado.web.UIModule):
    def render(self, links=[]):
        return self.render_string("modules/widgets/menu-left.html", links=links)    
    
        
""" Tratamento de tags """
    
class ShowTags (tornado.web.UIModule):
    """ Exibe tags usando estilo padrão """
    
    def css_files(self):
        return ["/static/jquery/tagsinput/jquery.tagsinput.css"]

    def render(self, tags, link=None):
        return self.render_string("modules/widgets/module-showtags.html", tags=tags, link=link)

class InputTags (tornado.web.UIModule):
    """ Gera input text para ser incluído num formulário de digitação de tags ou skills """
    
    def css_files(self):
        #return ["/static/jquery/tagsinput/jquery.tagsinput.css", "/static/jquery/jquery-ui-1.11.0/jquery-ui.min.css"]
        return ["/static/jquery/tagsinput/jquery.tagsinput.css"]
        
    def javascript_files(self):
        #return ["/static/jquery/tagsinput/jquery.tagsinput.js", "/static/jquery/jquery-ui-1.11.0/jquery-ui.min.js"]
        return ["/static/jquery/tagsinput/jquery.tagsinput.js"]
        
    def render(self, tags, tipo="tags"):
        if tipo == "tags":
            from core.model import AUTOCOMPLETE_TAGS
            return self.render_string("modules/widgets/module-inputtags.html", tags=tags, AUTOCOMPLETE_TAGS=AUTOCOMPLETE_TAGS)
        
        if tipo == "academic_skills":
            from core.model import AUTOCOMPLETE_ALL_SKILLS
            return self.render_string("modules/widgets/module-inputskills-academic.html", skills=tags, AUTOCOMPLETE_ALL_SKILLS=AUTOCOMPLETE_ALL_SKILLS)
        if tipo == "professional_skills":
            from core.model import AUTOCOMPLETE_ALL_SKILLS
            return self.render_string("modules/widgets/module-inputskills-professional.html", skills=tags, AUTOCOMPLETE_ALL_SKILLS=AUTOCOMPLETE_ALL_SKILLS)
                    
    
""" Representação de abas """

class ShowTabs (tornado.web.UIModule):
    def render(self, tabs):
        if tabs:
            return self.render_string("modules/widgets/module-tabs.html", tabs=tabs)
        else:
            return ""
        
            
""" Avaliação de artefatos """

class ShowAvaliaArtefato (tornado.web.UIModule):
    """ Exibe estrelas com avaliação de um objeto """

    def css_files(self):
        return ["/static/jquery/rater/jquery.rater.css"]
    
    def render (self, tipo, escopo, objeto, small=True):
        (mean_rating, num_ratings) = rating.model.Rating.getRatingsFromObject(tipo, escopo, objeto)
        
        # mean_rating = média das avaliações do objeto até o momento
        # num_ratings = número de avaliações do objeto até o momento
        return self.render_string("modules/widgets/show-avalia.html", RATINGS=(mean_rating, num_ratings), \
                                  TIPO=tipo, ESCOPO=escopo, OBJETO=objeto, SMALL=small)


class EditAvaliaArtefato (tornado.web.UIModule):
    """ Exibe estrelas com avaliação de um objeto, permitindo que o usuário logado faça sua avaliação (se ele ainda não tiver feito) """
    
    def css_files(self):
        return ["/static/jquery/rater/jquery.rater.css"]
    
    def javascript_files(self):
        return ["/static/jquery/rater/jquery.rater.js", "/static/getcookie.js"]

    def render (self, user, tipo, escopo, objeto):
        my_rating = 0
        get_rating = rating.model.Rating.getUserRatingFromObject(user, tipo, escopo, objeto)
        if get_rating: my_rating = get_rating[1]
        (mean_rating, num_ratings) = rating.model.Rating.getRatingsFromObject(tipo, escopo, objeto)
        
        # my_rating = avaliação que user fez do objeto (0=não avaliou ainda)
        # mean_rating = média das avaliações do objeto até o momento
        # num_ratings = número de avaliações do objeto até o momento
        return self.render_string("modules/widgets/edit-avalia.html", RATINGS=(my_rating, mean_rating, num_ratings), \
                                  USER=user, TIPO=tipo, ESCOPO=escopo, OBJETO=objeto)

""" Skills """
class ShowCustomTooltips (tornado.web.UIModule):
    """ Mostra tooltips customizadas (usado na área de edição das formações acadêmicas e experiências profissionais do usuário) """
    def render(self):
        return self.render_string("modules/widgets/module-showcustomtooltips.html")

class ShowSkillsToValidate (tornado.web.UIModule):
    """ Mostra as skills para validação social nos perfis de usuários amigos """
    def render(self, userdata, skills, autocomplete_all_skills):
        return self.render_string("modules/widgets/module-showskillstovalidate.html", USERDATA=userdata, \
                                   SKILLS_TO_VALIDATE=skills, AUTOCOMPLETE_ALL_SKILLS=autocomplete_all_skills)
        
class ShowPendingSkillsToValidate (tornado.web.UIModule):
    """ Mostra as habilidades pendentes para validação no perfil do próprio usuário """
    def render(self, userdata, skills):
        from skills.control import MAX_HABILIDADES_PENDENTES_WIDGET
        return self.render_string("modules/widgets/module-show_pending_skillstovalidate.html", USERDATA=userdata, \
                                   SKILLS_TO_VALIDATE=skills, \
                                   MAX_HABILIDADES_PENDENTES_WIDGET=MAX_HABILIDADES_PENDENTES_WIDGET)

class ShowSkillChartWidget (tornado.web.UIModule):
    """ Mostra mostra a miniatura de gráfico na widget de skills """
    def render(self, registry_id, skills):
        from skills.control import MAX_HABILIDADES_GRAFICO, MIN_HABILIDADES_GRAFICO
        return self.render_string("modules/widgets/module-show-skillchart-widget.html", REGISTRY_ID=registry_id, \
                                   SKILLS=skills, MAX_HABILIDADES_GRAFICO=MAX_HABILIDADES_GRAFICO, MIN_HABILIDADES_GRAFICO=MIN_HABILIDADES_GRAFICO)

""" Controle de paginação """

def update_querystring(url, **kwargs):
    base_url = urlparse.urlsplit(url)
    query_args = urlparse.parse_qs(base_url.query)
    query_args.update(kwargs)
    for arg_name, arg_value in kwargs.iteritems():
        if arg_value is None:
            if query_args.has_key(arg_name):
                del query_args[arg_name]

    query_string = urllib.urlencode(query_args, True)     
    return urlparse.urlunsplit((base_url.scheme, base_url.netloc,
        base_url.path, query_string, base_url.fragment))

class Paginator(tornado.web.UIModule):
    """ Exibe a régua de paginação """

    def css_files(self):
        return ["/static/paginator/paginator.css"]
    
    def render(self, page, page_size, results_count):
        # page: numero da página visualizada
        # page_size: número de itens em cada página
        # result_count: total de itens a ser dividido pelas páginas

        def get_page_url(page):
            # don't allow ?page=1
            if page <= 1:
                page = None
            return update_querystring(self.request.uri, page=page)
        
        itens_in_rule = 8
        pages = int(math.ceil(float(results_count) / page_size)) if results_count else 0
        
        if page < 1: page = 1
        if page > pages: page = pages
        x = (page-1) // itens_in_rule
        first_page = itens_in_rule * x + 1
        last_page = first_page + itens_in_rule - 1
        if last_page > pages: last_page = pages  

        next_page = page + 1 if page < pages else None
        previous_page = page - 1 if page > 1 else None
        
        """
        print "page=", page
        print "pages=", pages
        print "page_size=", page_size
        print "results_count=", results_count
        print "itens_in_rule=", itens_in_rule
        print "x=", x
        print "first_page=", first_page
        print "last_page=", last_page
        print "next_page=", next_page
        print "previous_page=", previous_page
        print
        """
        
        return self.render_string('modules/widgets/pagination.html', page=page, pages=pages, next=next_page,
                                  previous=previous_page, get_page_url=get_page_url,
                                  first_page=first_page, last_page=last_page)
        



        
""" Modulos antigos: verificar se ainda são necessários """

"""        
class ShowItem (tornado.web.UIModule):
    def render(self, tag):
        return self.render_string("modules/widgets/module-showitem.html", item=tag)

class ShowBotao (tornado.web.UIModule):
    def render(self, botao):
        return self.render_string("modules/widgets/module-showbotao.html", item=botao)

class ShowMenuSup (tornado.web.UIModule):
    def render(self, cor, texto, link):
        click = "location.href='"+link+"'" if link=='/logout' else "window.open('"+link+"','','')" 
        return self.render_string("modules/widgets/botao-menusup.html", cor=cor, texto=texto, click=click)
    
class ShowMenuDir (tornado.web.UIModule):
    def render(self, cor, icone, texto, link):
        return self.render_string("modules/widgets/botao-menudir.html", cor=cor, icone=icone, texto=texto, link=link)

class ShowQuadroInicio (tornado.web.UIModule):
    def render(self, cor, width=""):
        fundo = { "Cinza":"#ECEAE4", "Laranja":"#FBD9AD", "Vermelho":"#FCB0A6", "Verde":"#81E4B2" }[cor]
        return self.render_string("modules/widgets/quadro-inicio.html", cor=cor, width=width, fundo=fundo)

class ShowQuadroFim (tornado.web.UIModule):
    def render(self, cor):
        return self.render_string("modules/widgets/quadro-fim.html", cor=cor)

class ShowEscala (tornado.web.UIModule):
    def render (self, valor, maximo, cor="Roxo"):
        if maximo:
            escala = int(150*valor/float(maximo))
            return self.render_string("modules/widgets/escala.html", valor=valor, maximo=maximo, escala=escala, cor=cor)
        else:
            return ""

class ShowPageIndex (tornado.web.UIModule):
    def render(self, links):
        return self.render_string("modules/widgets/pageIndex.html", links=links)
 """