# -*- coding: utf-8 -*-

def request_check(form):
    req_count = int(form.vars.req_count)
    imei_prefix = int(form.vars.imei_prefix)

    if req_count > get_imei_left(imei_prefix):
        form.errors.request_check = 'not enough'


@auth.requires_login()
def request():
    response.view = 'default/submit.html'
    form = SQLFORM(db.request)

    # set options
    options = []
    myset = db(db.imei_prefix)
    for record in myset.select():
        options.append(OPTION('[{}] {} - {}'.format(record.imei_prefix, record.name, get_imei_left(record.id)),
                              _value=int(record.id)))

    form.custom.widget.imei_prefix = SELECT(*options,
                                            _class='form-control generic-widget',
                                            _name='imei_prefix')

    if form.process(onvalidation=request_check).accepted:
        response.flash = 'submit succ!'
    elif form.errors:
        response.flash = 'submit fail!'
        if form.errors.request_check:
            response.flash = form.errors.request_check

    if not form.errors:
        if form.vars.imei_prefix and form.vars.req_count:
            assign_imei(form.vars.id)
            redirect(URL(f='display'))

    return dict(title=T('Request'), form=form)


@auth.requires_login()
def display():
    grid = SQLFORM.grid(db.request.create_by == auth.user_id,
                        fields=[db.request.id,
                                db.request.description,
                                db.request.imei_prefix,
                                db.request.req_count],
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
    return dict(title=T('my requests'), grid=grid)


def detail():
    grid = SQLFORM.grid((db.request.create_by == auth.user_id) & (db.request.id == db.imei_assign.request),
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
    return dict(title=T('my requests result'), grid=grid)
