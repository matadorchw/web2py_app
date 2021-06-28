# -*- coding: utf-8 -*-

if 'adminLanguage' in request.cookies and not (request.cookies['adminLanguage'] is None):
    T.force(request.cookies['adminLanguage'].value)
