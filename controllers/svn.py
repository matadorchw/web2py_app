import svnhelper

h = svnhelper.VisualSvnHelper()


def show_users():
    return dict(title=T('Show SVN Users'), users=h.get_users())


def create_user():
    return dict(title='Create SVN User')


def set_password():
    response.view = 'svn/create_user.html'
    return dict(title='Set Password', user_name=request.args[0])


def set_password_done():
    h.set_password(request.vars['name'], request.vars['password'])
    redirect(URL(c='svn', f='show_users'))


def delete_user():
    h.delete_user(request.args[0])
    redirect(URL(c='svn', f='show_users'))


def create_user_done():
    h.create_user(request.vars['name'], request.vars['password'])
    redirect(URL(c='svn', f='show_users'))
