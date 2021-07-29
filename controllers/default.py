# -*- coding: utf-8 -*-

import svnhelper


def index():
    h = svnhelper.VisualSvnHelper()
    return dict(message=str(h.get_users()))


def user():
    return dict(form=auth())
