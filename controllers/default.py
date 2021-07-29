# -*- coding: utf-8 -*-


def index():
    return dict(message='Welcome')


def user():
    return dict(form=auth())
