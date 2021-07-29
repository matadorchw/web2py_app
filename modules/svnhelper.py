import wmi


class VisualSvnHelper:
    def __init__(self, computer='', user='', password=''):
        self.ns = wmi.WMI(namespace='root/VisualSVN')
        self.user = self.ns.get('VisualSVN_User')
        self.group = self.ns.get('VisualSVN_Group')

    def get_users(self):
        return [user.Name for user in self.ns.instances('VisualSVN_User')]

    def create_user(self, name, password):
        self.user.Create(name, password)

    def delete_user(self, name):
        self.user.Delete(name)

    def get_groups(self):
        return [group.Name for group in self.ns.instances('VisualSVN_Group')]

    def get_group_members(self, group):
        members = []
        for g in self.ns.instances('VisualSVN_Group'):
            if g.Name == group:
                for m in g.GetMembers()[0]:
                    members.append(m.Name)
                break
        return members


if __name__ == '__main__':
    h = VisualSvnHelper()
    print(h.get_users())
