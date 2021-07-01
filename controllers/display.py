@auth.requires_login()
def display():
    grid = SQLFORM.grid(db.request.create_by == auth.user_id,
                        fields=[
                            db.request.id,
                            db.request.description,
                            db.request.imei_prefix,
                            db.request.req_count
                        ],
                        links=[
                            dict(header='',
                                 body=lambda row: A(T('detail'),
                                                    _class="btn btn-secondary",
                                                    _href=URL(c="display",
                                                              f="detail",
                                                              vars=dict(req_id=row.id),
                                                              user_signature=True))
                                 )
                        ],
                        orderby=~db.request.create_on,
                        maxtextlength=32,
                        searchable=False,
                        sortable=False,
                        editable=False,
                        deletable=True,
                        details=False,
                        create=False,
                        csv=False)

    response.view = 'default/grid.html'
    return dict(title=T('My Requests'), grid=grid)


@auth.requires_login()
def detail():
    title = T('All My Requests Detail')
    q = (db.request.create_by == auth.user_id) & (db.request.id == db.imei_assign.request)
    if request.vars.req_id:
        req_id = int(request.vars.req_id)
        q = (db.request.id == req_id) & q
        title = T('Request Detail') + '[%d]' % req_id
    grid = SQLFORM.grid(q,
                        fields=[
                            db.request.id,
                            db.request.description,
                            db.request.imei_prefix,
                            db.request.req_count,
                            db.imei_assign.id,
                        ],
                        links=[
                            dict(header='assign section', body=lambda row: get_scope_of_request(row.imei_assign.id))
                        ],
                        orderby=~db.request.create_on,
                        maxtextlength=32,
                        paginate=100,
                        searchable=False,
                        sortable=False,
                        editable=False,
                        deletable=False,
                        details=False,
                        create=False,
                        csv=False)

    response.view = 'default/grid.html'
    return dict(title=title, grid=grid)
