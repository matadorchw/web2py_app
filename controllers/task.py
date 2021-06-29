# -*- coding: utf-8 -*-

def request_check(form):
    req_count = form.vars.req_count
    imei_prefix = form.vars.imei_prefix


@auth.requires_login()
def request():
    response.view = 'default/submit.html'
    form = SQLFORM(db.request)

    # set options
    options = []
    myset = db(db.imei_prefix)
    for record in myset.select():
        options.append(OPTION('[{}] {}'.format(record.imei_prefix, record.name), _value=int(record.id)))

    form.custom.widget.imei_prefix = SELECT(*options,
                                            _class='form-control generic-widget',
                                            _name='imei_prefix')

    if form.process(onvalidation=request_check).accepted:
        response.flash = 'submit succ!'
    elif form.errors:
        response.flash = 'submit fail!'

    if not form.errors:
        pass

    return dict(title=T('Request'), form=form)


@auth.requires_login()
def display():
    response.view = 'default/index.html'
    return dict(message='display')
