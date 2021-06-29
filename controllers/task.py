# -*- coding: utf-8 -*-

@auth.requires_login()
def request():
    response.view = 'default/index.html'
    return dict(message='request')


@auth.requires_login()
def display():
    response.view = 'default/index.html'
    return dict(message='display')
