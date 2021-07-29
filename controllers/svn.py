import svnhelper


def show_users():
    h = svnhelper.VisualSvnHelper()
    return dict(title=T('Show Users'), users=h.get_users())


def create_user():
    return dict(message='Welcome')
