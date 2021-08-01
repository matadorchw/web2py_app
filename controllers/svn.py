import svnhelper


@auth.requires_login()
def show_users():
    return dict(title=T('Show SVN Users'), users=svnhelper.get_users())


@auth.requires_login()
def create_user():
    return dict(title=T('Create SVN User'))


@auth.requires_login()
def set_password():
    response.view = 'svn/create_user.html'
    return dict(title=T('Set Password'), user_name=request.args[0])


@auth.requires_login()
def set_password_done():
    svnhelper.user_set_password(request.vars['name'], request.vars['password'])
    redirect(URL(c='svn', f='show_users'))


@auth.requires_login()
def delete_user():
    svnhelper.user_delete(request.args[0])
    redirect(URL(c='svn', f='show_users'))


@auth.requires_login()
def create_user_done():
    svnhelper.user_create(request.vars['name'], request.vars['password'])
    redirect(URL(c='svn', f='show_users'))
