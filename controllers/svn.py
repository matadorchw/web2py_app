@auth.requires_login()
def show_users():
    return dict(title=T('SVN Users'), users=svn_get_users())


@auth.requires_login()
def create_user():
    if len(request.args) > 0:
        err_msg = request.args[0]
        if err_msg == 'succ':
            response.flash = T('Created successfully')
        else:
            response.flash = svn_decode(err_msg)

    action = URL(c='svn', f='create_user_done')
    return dict(title=T('Create SVN User'), action=action)


@auth.requires_login()
def create_user_done():
    args = []
    name = request.vars['name']
    password = request.vars['password']
    if name.strip():
        err_msg = svn_user_create(name, password)
        if err_msg:
            args.append(err_msg)
        else:
            args.append('succ')
    else:
        args.append(svn_encode(T('name is empty').encode()))
    redirect(URL(c='svn', f='create_user', args=args, user_signature=True))


@auth.requires_login()
def set_password():
    response.view = 'svn/create_user.html'
    action = URL(c='svn', f='set_password_done')
    return dict(title=T('Set Password'), action=action, user_name=request.args[0])


@auth.requires_login()
def set_password_done():
    svn_user_set_password(request.vars['name'], request.vars['password'])
    redirect(URL(c='svn', f='show_users'))


@auth.requires_login()
def user_detail():
    user = request.args[0]
    groups = svn_user_belongs_groups(user)
    return dict(title=T('SVN Users') + f'{user}' + T('Detail'), user=user, groups=groups)


@auth.requires_login()
def delete_user():
    svn_user_delete(request.args[0])
    redirect(URL(c='svn', f='show_users'))


@auth.requires_login()
def show_groups():
    return dict(title=T('SVN Groups'), groups=svn_get_groups())


@auth.requires_login()
def create_group():
    if len(request.args) > 0:
        err_msg = request.args[0]
        if err_msg == 'succ':
            response.flash = T('Created successfully')
        else:
            response.flash = svn_decode(err_msg)

    action = URL(c='svn', f='create_group_done')
    return dict(title=T('Create SVN Group'), action=action)


@auth.requires_login()
def create_group_done():
    args = []
    name = request.vars['name']
    if name.strip():
        err_msg = svn_group_create(name)
        if err_msg:
            args.append(err_msg)
        else:
            args.append('succ')
    else:
        args.append(svn_encode(T('name is empty').encode()))
    redirect(URL(c='svn', f='create_group', args=args, user_signature=True))


@auth.requires_login()
def delete_group():
    svn_group_delete(request.args[0])
    redirect(URL(c='svn', f='show_groups'))


@auth.requires_login()
def group_members():
    group_name = request.args[0]
    users, groups = svn_group_get_members_by_type(group_name)
    return dict(title=T('Group Members') + f'[{group_name}]', group_name=group_name, users=users, groups=groups)


@auth.requires_login()
def delete_group_member():
    group, member = request.args
    svn_group_delete_member(group, member)
    redirect(URL(c='svn', f='group_members', args=group, user_signature=True))


@auth.requires_login()
def add_group_member():
    group = request.args[0]

    if len(request.args) > 1:
        err_msg = request.args[1]
        response.flash = svn_decode(err_msg)

    users = svn_get_users()
    groups = svn_get_groups()
    members = svn_group_get_members(group)

    return dict(title=T('Add Group Member') + f'[{group}]',
                group_name=group, users=users, groups=groups,
                members=members)


@auth.requires_login()
def add_group_member_done():
    group, member = request.args

    args = [group]
    err_msg = svn_group_add_member(group, member)
    if err_msg:
        args.append(err_msg)

    redirect(URL(c='svn', f='add_group_member', args=args, user_signature=True))


@auth.requires_membership('administrators')
def show_repositories():
    return dict(title=T('SVN Repositories'), repositories=svn_get_repositories())


@auth.requires_membership('administrators')
def show_path():
    repo = request.args[0]
    path = svn_decode(request.args[1])
    folders, files = svn_repo_get_children(repo, path)
    folders.sort(key=lambda f: f.Name)
    files.sort(key=lambda f: f.Name)
    return dict(title=T('SVN Repositories'), repo=repo, path=path, children=folders + files)


@auth.requires_membership('administrators')
def show_security():
    repo = request.args[0]
    path = svn_decode(request.args[1])
    if len(request.args) > 2:
        err_msg = request.args[2]
        response.flash = svn_decode(err_msg)
    security = svn_repo_get_security(repo, path)

    users = svn_get_users()
    groups = svn_get_groups()

    special_permission = []
    users_permission = []
    groups_permission = []
    for s in security:
        if s[0] == 'Everyone':
            special_permission.append(s)
        elif s[0] in users:
            users_permission.append(s)
        elif s[0] in groups:
            groups_permission.append(s)
    security = special_permission + users_permission + groups_permission

    return dict(title=T('SVN Security'), repo=repo, path=path, security=security)


@auth.requires_membership('administrators')
def add_permission():
    repo = request.args[0]
    path = svn_decode(request.args[1])
    action = URL(c='svn', f='add_permission_done')
    return dict(title=T('Add Permission'), action=action, repo=repo, path=path)


def submit_permission_done(msg):
    repo = request.vars['repo']
    path = svn_decode(request.vars['path'])
    account = request.vars['account']
    permission = None
    if 'permission' in request.vars:
        permission = int(request.vars['permission'])

    args = [repo, svn_encode(path)]
    if permission is None:
        err_msg = svn_encode(T('please choose permission').encode())
    else:
        err_msg = svn_repo_add_permission(repo, path, (account, permission))

    if not err_msg:
        err_msg = svn_encode(msg)

    if err_msg:
        args.append(err_msg)

    redirect(URL(c='svn', f='show_security', args=args, user_signature=True))


@auth.requires_membership('administrators')
def add_permission_done():
    submit_permission_done(T('Add permission successfully').encode())


@auth.requires_membership('administrators')
def edit_permission():
    repo = request.args[0]
    path = svn_decode(request.args[1])
    account = request.args[2]
    permission = int(request.args[3])

    response.view = 'svn/add_permission.html'
    action = URL(c='svn', f='edit_permission_done')
    return dict(title=T('Edit Permission'), action=action, repo=repo, path=path, account=account, permission=permission)


@auth.requires_membership('administrators')
def edit_permission_done():
    submit_permission_done(T('Edit permission successfully').encode())


@auth.requires_membership('administrators')
def delete_permission():
    repo = request.args[0]
    path = svn_decode(request.args[1])
    account = request.args[2]
    permission = int(request.args[3])

    args = [repo, svn_encode(path)]
    err_msg = svn_repo_delete_permission(repo, path, (account, permission))
    if not err_msg:
        err_msg = svn_encode(T('Delete permission successfully').encode())
    if err_msg:
        args.append(err_msg)

    redirect(URL(c='svn', f='show_security', args=args, user_signature=True))
