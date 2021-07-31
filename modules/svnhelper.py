import wmi
import pythoncom


def __get_ns(computer='', user='', password=''):
    return wmi.WMI(namespace='root/VisualSVN')


def __get_user():
    ns = __get_ns()
    user = ns.get('VisualSVN_User')
    return user


def get_users():
    pythoncom.CoInitialize()
    ns = __get_ns()
    result = [user.Name for user in ns.instances('VisualSVN_User')]
    pythoncom.CoUninitialize()
    return result


def create_user(name, password):
    pythoncom.CoInitialize()
    user = __get_user()
    user.Create(name, password)
    pythoncom.CoUninitialize()


def set_password(name, password):
    pythoncom.CoInitialize()
    ns = __get_ns()
    for user in ns.instances('VisualSVN_User'):
        if user.Name == name:
            user.SetPassword(password)
            break
    pythoncom.CoUninitialize()


def delete_user(name):
    pythoncom.CoInitialize()
    user = __get_user()
    user.Delete(name)
    pythoncom.CoUninitialize()


if __name__ == '__main__':
    print(get_users())
