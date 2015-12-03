# -*- coding: utf-8 -*-
"""
###############################################
AgileUFRJ - Implementando as teses do PPGI
###############################################

:Author: *Carlo E. T. Oliveira*
:Contact: carlo@nce.ufrj.br
:Date: $Date: 2010/07/03  $
:Status: This is a "work in progress"
:Revision: $Revision: 0.01 $
:Home: `LABASE <http://labase.nce.ufrj.br/>`__
:Copyright: ©2009, `GPL <http://is.gd/3Udt>`__. 
"""

import tornado.web
import logging
from core.dispatcher import BaseHandler
import functools

def delist_arguments(args):
    """
    Takes a dictionary, 'args' and de-lists any single-item lists then
    returns the resulting dictionary.

    In other words, {'foo': ['bar']} would become {'foo': 'bar'}
    """
    for arg, value in args.items():
        if len(value) == 1:
            args[arg] = value[0]
    return args


def authenticated(method):
    """Decorate methods with this to require that the user be logged in."""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.get_current_gamesession():
            self.redirect("/api/")
            return
        return method(self, *args, **kwargs)
    return wrapper


class MethodDispatcher(BaseHandler):
    """
    Subclasss this to have all of your class's methods exposed to the web
    for both GET and POST requests.  Class methods that start with an
    underscore (_) will be ignored.
    """

    def get_current_gamesession(self):
        return self.get_secure_cookie("gamesession")

    
    def _dispatch(self):
        """
        Load up the requested URL if it matches one of our own methods.
        Skip methods that start with an underscore (_).
        """
        self.user = self.get_current_user()
        args = None
        # Sanitize argument lists:
        if self.request.arguments:
            args = delist_arguments(self.request.arguments)
        # Special index method handler:
        if self.request.uri.endswith('/'):
            func = getattr(self, 'index', None)
            if args:
                return func(**args)
            else:
                return func()
        path = self.request.uri.split('?')[0]
        method = path.split('/')[-1]
        if not method.startswith('_'):
            func = getattr(self, method, None)
            if func:
                if args:
                    return func(**args)
                else:
                    return func()
            else:
                raise tornado.web.HTTPError(404)
        else:
            raise tornado.web.HTTPError(404)

    # @tornado.web.authenticated
    def get(self,*a):
        """Returns self._dispatch()"""
        self.user = self.get_current_user()
        return self._dispatch()

    # @tornado.web.authenticated
    def post(self):
        """Returns self._dispatch()"""
        return self._dispatch()

