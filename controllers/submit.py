# -*- coding: utf-8 -*-

def request_check(form):
    req_count = int(form.vars.req_count)
    imei_prefix = int(form.vars.imei_prefix)

    if req_count > get_imei_left(imei_prefix):
        form.errors.request_check = T('Not enough')


@auth.requires_login()
def request_submit():
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
        response.flash = T('Submit succ!')
    elif form.errors:
        response.flash = T('Submit fail!')
        if form.errors.request_check:
            response.flash = form.errors.request_check

    if not form.errors:
        if form.vars.imei_prefix and form.vars.req_count:
            assign_imei(form.vars.id)
            redirect(URL(c='display', f='detail', vars=dict(req_id=form.vars.id)))

    return dict(title=T('Request'), form=form)
