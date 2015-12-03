# -*- coding: utf-8 -*-
#
# uimethods.py
# Modulo para definição de funções globais para uso nos templates
# as funções sempre devem ter nome em minúsculas e receber o primeiro
# parametro handler
# 


def str_cut(handler, str, size):
    return str if len(str) <= size else str[:size]+"..."

    