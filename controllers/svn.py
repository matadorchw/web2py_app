import svnhelper

h = svnhelper.VisualSvnHelper()


def show_users():
    return dict(title=T('Show SVN Users'), users=h.get_users())


def create_user():
    form = FORM(INPUT(_name='name'),
                INPUT(_name='password'),
                INPUT(_type='submit'))

    return dict(title='Create SVN User', form=form)


def create_user_done():
    print(request.vars)
    h.create_user(request.vars['name'], request.vars['password'])
    redirect(URL(c='svn', f='show_users'))
