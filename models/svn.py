import binascii
import wmi

import svnhelper


def svn_get_users():
    return svnhelper.get_users()


def svn_user_create(name, password):
    err_msg = None
    try:
        svnhelper.user_create(name, password)
    except wmi.x_wmi as e:
        err_msg = svn_err_msg_encode(e.com_error.args[2][2])
    return err_msg


def svn_user_set_password(name, password):
    svnhelper.user_set_password(name, password)


def svn_user_delete(name):
    svnhelper.user_delete(name)


def svn_get_groups():
    return svnhelper.get_groups()


def svn_group_create(name):
    err_msg = None
    try:
        svnhelper.group_create(name)
    except wmi.x_wmi as e:
        err_msg = svn_err_msg_encode(e.com_error.args[2][2])
    return err_msg


def svn_group_delete(name):
    svnhelper.group_delete(name)


def svn_group_get_members(name):
    return svnhelper.group_get_members(name)


def svn_group_set_members(group, members):
    svnhelper.group_set_members(group, members)


###

def svn_group_delete_member(group, member):
    members = svn_group_get_members(group)
    members.remove(member)
    svn_group_set_members(group, members)


def svn_err_msg_encode(err_msg):
    return binascii.b2a_hex(err_msg.encode('utf-8')).decode()


def svn_err_msg_decode(err_msg):
    return binascii.a2b_hex(err_msg).decode('utf-8')


def svn_group_add_member(group, member):
    members = svn_group_get_members(group)
    members.append(member)
    err_msg = None
    try:
        svn_group_set_members(group, members)
    except wmi.x_wmi as e:
        err_msg = svn_err_msg_encode(e.com_error.args[2][2])
    return err_msg


def svn_user_belongs_groups(user):
    groups = []
    for g in svn_get_groups():
        if user in svn_group_get_members(g):
            groups.append(g)
    return groups


def svn_group_get_members_by_type(group_name):
    members = svn_group_get_members(group_name)

    users = []
    for user in svn_get_users():
        if user in members:
            users.append(user)

    groups = []
    for group in svn_get_groups():
        if group in members:
            groups.append(group)

    return users, groups
