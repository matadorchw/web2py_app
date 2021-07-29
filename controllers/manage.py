# -*- coding: utf-8 -*-

@auth.requires_membership('administrators')
def manage_table(title, table, fields=None,
                 searchable=True,
                 sortable=True,
                 editable=True,
                 deletable=True,
                 details=True,
                 create=True,
                 links=None):
    grid = SQLFORM.grid(table, fields=fields,
                        searchable=searchable,
                        sortable=sortable,
                        editable=editable,
                        deletable=deletable,
                        details=details,
                        create=create,
                        links=links, maxtextlength=32, csv=False)
    response.view = 'default/grid.html'
    return dict(title=title, grid=grid)


@auth.requires_membership('administrators')
def user():
    return manage_table(T('User'), db.auth_user)


@auth.requires_membership('administrators')
def group():
    return manage_table(T('Group'), db.auth_group)


@auth.requires_membership('administrators')
def membership():
    return manage_table(T('Membership'), db.auth_membership)


