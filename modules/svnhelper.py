import wmi
import pythoncom


class VisualSvnHelper:
    def __init__(self, computer='', user='', password=''):
        pythoncom.CoInitialize()
        self.ns = wmi.WMI(namespace='root/VisualSVN')
        self.user = self.ns.get('VisualSVN_User')
        self.group = self.ns.get('VisualSVN_Group')
        pythoncom.CoUninitialize()

    def get_users(self):
        pythoncom.CoInitialize()
        result = [user.Name for user in self.ns.instances('VisualSVN_User')]
        pythoncom.CoUninitialize()
        return result

    def create_user(self, name, password):
        pythoncom.CoInitialize()
        self.user.Create(name, password)
        pythoncom.CoUninitialize()

    def set_password(self, name, password):
        pythoncom.CoInitialize()
        for user in self.ns.instances('VisualSVN_User'):
            if user.Name == name:
                user.SetPassword(password)
                break
        pythoncom.CoUninitialize()

    def delete_user(self, name):
        pythoncom.CoInitialize()
        self.user.Delete(name)
        pythoncom.CoUninitialize()

    def get_groups(self):
        pythoncom.CoInitialize()
        result = [group.Name for group in self.ns.instances('VisualSVN_Group')]
        pythoncom.CoUninitialize()
        return result

    def get_group_members(self, group):
        pythoncom.CoInitialize()
        members = []
        for g in self.ns.instances('VisualSVN_Group'):
            if g.Name == group:
                for m in g.GetMembers()[0]:
                    members.append(m.Name)
                break
        pythoncom.CoUninitialize()
        return members


if __name__ == '__main__':
    h = VisualSvnHelper()
    h.set_password('yangchw', '123')
