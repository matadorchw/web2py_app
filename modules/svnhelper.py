import sys

sys.coinit_flags = 0

import wmi
import pythoncom


def __get_ns(computer='', user='', password=''):
    return wmi.WMI(namespace='root/VisualSVN')


def __get_user():
    return __get_ns().get('VisualSVN_User')


def __get_users():
    return __get_ns().instances('VisualSVN_User')


def get_users():
    pythoncom.CoInitialize()
    result = [user.Name for user in __get_users()]
    pythoncom.CoUninitialize()
    result.sort()
    return result


def user_create(name, password):
    pythoncom.CoInitialize()
    __get_user().Create(name, password)
    pythoncom.CoUninitialize()


def user_set_password(name, password):
    pythoncom.CoInitialize()
    for user in __get_users():
        if user.Name == name:
            user.SetPassword(password)
            break
    pythoncom.CoUninitialize()


def user_delete(name):
    pythoncom.CoInitialize()
    __get_user().Delete(name)
    pythoncom.CoUninitialize()


def __get_group():
    return __get_ns().get('VisualSVN_Group')


def __get_groups():
    return __get_ns().instances('VisualSVN_Group')


def get_groups():
    pythoncom.CoInitialize()
    result = [group.Name for group in __get_groups()]
    pythoncom.CoUninitialize()
    result.sort()
    return result


def group_create(name, members=[]):
    pythoncom.CoInitialize()
    __get_group().Create(Name=name, Members=members)
    pythoncom.CoUninitialize()


def group_delete(name):
    pythoncom.CoInitialize()
    __get_group().Delete(name)
    pythoncom.CoUninitialize()


def group_get_members(name):
    pythoncom.CoInitialize()
    members = []
    for group in __get_groups():
        if group.Name == name:
            members = [m.Name for m in group.GetMembers()[0]]
            break
    pythoncom.CoUninitialize()
    return members


def group_set_members(name, members):
    pythoncom.CoInitialize()
    new_members = []
    for user in __get_users():
        if user.Name in members:
            new_members.append(user.path())

    for group in __get_groups():
        if group.Name in members:
            new_members.append(group.path())

    for group in __get_groups():
        if group.Name == name:
            group.SetMembers(Members=new_members)
            break
    pythoncom.CoUninitialize()


def __get_repository():
    return __get_ns().get('VisualSVN_Repository')


def __get_repositories():
    return __get_ns().instances('VisualSVN_Repository')


def get_repositories():
    pythoncom.CoInitialize()
    result = [(repo.Name, repo.URL) for repo in __get_repositories()]
    pythoncom.CoUninitialize()
    result.sort()
    return result


class VisualSVN_RepositoryEntry:
    def __init__(self, entry):
        self.RepositoryName = entry.RepositoryName
        self.Path = entry.Path
        self.InheritedOnlyPermissions = entry.InheritedOnlyPermissions
        self.Name = entry.Name
        self.ParentPath = entry.ParentPath
        self.URL = entry.URL
        self.Kind = entry.Kind

    def __str__(self):
        return (
            f'RepositoryName[{self.RepositoryName}] '
            f'Path[{self.Path}] '
            f'InheritedOnlyPermissions[{self.InheritedOnlyPermissions}] '
            f'Name[{self.Name}] '
            f'ParentPath[{self.ParentPath}] '
            f'URL[{self.URL}] '
            f'Kind[{self.Kind}]')


def repo_get_security(repo_name, path):
    pythoncom.CoInitialize()
    permissions = []
    for r in __get_repositories():
        if r.Name == repo_name:
            for p in r.GetSecurity(path)[0]:
                permissions.append((p.Account.Name, p.AccessLevel))
            break
    pythoncom.CoUninitialize()
    return permissions


def repo_set_security(repo_name, path, permissions, reset_children=False):
    pythoncom.CoInitialize()
    Permissions = []
    for account, access_level in permissions:
        Account = None
        if Account is None:
            for user in __get_users():
                if user.Name == account:
                    Account = user
                    break
        if Account is None:
            for group in __get_groups():
                if group.Name == account:
                    Account = group
                    break

        permission = __get_ns().new_instance_of('VisualSVN_PermissionEntry', Account=Account, AccessLevel=access_level)

        Permissions.append(permission)

    for r in __get_repositories():
        if r.Name == repo_name:
            r.SetSecurity(Path=path, Permissions=Permissions, ResetChildren=reset_children)
            break
    pythoncom.CoUninitialize()


def repo_get_children(repo_name, path):
    pythoncom.CoInitialize()
    children = []
    for r in __get_repositories():
        if r.Name == repo_name:
            try:
                for entry in r.GetChildren(path)[0]:
                    children.append(VisualSVN_RepositoryEntry(entry))
            except:
                pass
            break
    pythoncom.CoUninitialize()
    return children


if __name__ == '__main__':
    pass
