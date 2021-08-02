import svnhelper


@auth.requires_login()
def show_users():
    return dict(title=T('SVN Users'), users=svnhelper.get_users())


@auth.requires_login()
def create_user():
    action = URL(c='svn', f='create_user_done')
    return dict(title=T('Create SVN User'), action=action)


@auth.requires_login()
def set_password():
    response.view = 'svn/create_user.html'
    action = URL(c='svn', f='set_password_done')
    return dict(title=T('Set Password'), action=action, user_name=request.args[0])


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


@auth.requires_login()
def show_groups():
    return dict(title=T('SVN Groups'), groups=svnhelper.get_groups())


@auth.requires_login()
def create_group():
    action = URL(c='svn', f='create_group_done')
    return dict(title=T('Create SVN Group'), action=action)


@auth.requires_login()
def create_group_done():
    svnhelper.group_create(request.vars['name'])
    redirect(URL(c='svn', f='show_groups'))


@auth.requires_login()
def delete_group():
    svnhelper.group_delete(request.args[0])
    redirect(URL(c='svn', f='show_groups'))


@auth.requires_login()
def group_members():
    group = request.args[0]
    members = svnhelper.group_get_members(group)
    return dict(title=T('Group Members') + f'[{group}]', group_name=group, members=members)


@auth.requires_login()
def delete_group_member():
    group, member = request.args
    members = svnhelper.group_get_members(group)
    members.remove(member)
    svnhelper.group_set_members(group, members)
    redirect(URL(c='svn', f='group_members', args=group, user_signature=True))


@auth.requires_login()
def add_group_member():
    group = request.args[0]
    users = svnhelper.get_users()
    groups = svnhelper.get_groups()
    members = svnhelper.group_get_members(group)
    return dict(title=T('Add Group Member') + f'[{group}]',
                group_name=group, users=users, groups=groups,
                members=members)


@auth.requires_login()
def add_group_member_done():
    group, member = request.args
    members = svnhelper.group_get_members(group)
    members.append(member)
    print(members)
    svnhelper.group_set_members(group, members)
    redirect(URL(c='svn', f='group_members', args=group, user_signature=True))
