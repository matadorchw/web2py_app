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


@auth.requires_membership('administrators')
def imei_prefix():
    return manage_table(T('IMEI Prefix'), db.imei_prefix, links=[
        dict(header='',
             body=lambda row: A(T('Detail'),
                                _class="btn btn-secondary",
                                _href=URL(c="display",
                                          f="imei_prefix_detail",
                                          vars=dict(imei_prefix=row.id),
                                          user_signature=True))
             )
    ])


@auth.requires_membership('administrators')
def imei_section():
    return manage_table(T('IMEI Section'), db.imei_section)


@auth.requires_membership('administrators')
def imei_assign():
    return manage_table(T('IMEI Assign'), db.imei_assign)


@auth.requires_membership('administrators')
def requests():
    grid = SQLFORM.smartgrid(db.request, maxtextlength=32, csv=False)
    response.view = 'default/grid.html'
    return dict(title=T('Requests'), grid=grid)
