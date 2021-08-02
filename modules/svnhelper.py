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
    result = []
    pythoncom.CoInitialize()
    for group in __get_groups():
        if group.Name == name:
            result = [m.Name for m in group.GetMembers()[0]]
            break
    pythoncom.CoUninitialize()
    result.sort()
    return result


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


if __name__ == '__main__':
    print(get_repositories())
