db.auth_user._format = "%(first_name)s"
# auth.settings.actions_disabled = ['register']


db.define_table(
    'imei_prefix',
    Field('name', unique=True),
    Field('imei_prefix'),
    format='[%(imei_prefix)s] %(name)s'
)

db.define_table(
    'imei_section',
    Field('name', unique=True),
    Field('imei_prefix', db.imei_prefix,
          requires=IS_IN_DB(db, db.imei_prefix.id, '[%(imei_prefix)s] %(name)s')),
    Field('section_start', 'integer', default=0),
    Field('section_end', 'integer', default=999999),
    format='%(name)s [%(imei_prefix)s]'
)

db.define_table(
    'request',
    Field('description', unique=True, label=T('description')),
    Field('req_count', 'integer'),
    Field('imei_prefix', db.imei_prefix,
          requires=IS_IN_DB(db, db.imei_prefix.id, '[%(imei_prefix)s] %(name)s')),
    Field('create_on', 'datetime', default=request.now, label=T('create time')),
    Field('create_by', db.auth_user, default=auth.user_id, label=T('create by'))
)
db.request.description.requires = [IS_NOT_EMPTY(), IS_NOT_IN_DB(db, db.request.description)]
db.request.req_count.requires = IS_NOT_EMPTY()
db.request.imei_prefix.requires = IS_NOT_EMPTY()
db.request.create_on.writable = False
db.request.create_by.writable = False

db.define_table(
    'imei_assign',
    Field('request', db.request, requires=IS_IN_DB(db, db.request.id, '%(description)s')),
    Field('assign_start', 'integer'),
    Field('assign_end', 'integer')
)


# functions

def get_imei_left(imei_prefix):
    total = 0
    myset = db(db.imei_section.imei_prefix == imei_prefix)
    for record in myset.select(db.imei_section.ALL):
        total = total + record.section_end - record.section_start + 1
    used = 0
    myset = db((db.request.imei_prefix == imei_prefix) &
               (db.imei_assign.request == db.request.id))
    for record in myset.select(db.imei_assign.ALL):
        used = used + record.assign_end - record.assign_start + 1
    return total - used


def get_imei_section(imei_prefix):
    result = []
    myset = db(db.imei_section.imei_prefix == imei_prefix)
    for record in myset.select(db.imei_section.ALL, orderby=db.imei_section.section_start):
        result.append((record.section_start, record.section_end))
    return result


def get_imei_assign(imei_prefix):
    result = []
    myset = db((db.request.imei_prefix == imei_prefix) &
               (db.imei_assign.request == db.request.id))
    for record in myset.select(db.imei_assign.ALL, orderby=db.imei_assign.assign_start):
        result.append((record.assign_start, record.assign_end))
    return result


def get_free_list(r_total, r_used, req_count):
    free_list = []
    for b1, e1 in r_total:
        free = list(range(b1, e1 + 1))
        for b2, e2 in r_used:
            if b2 > e1:
                break
            if e2 < b1:
                continue
            for v in range(b1, e1 + 1):
                if b2 <= v <= e2:
                    free.remove(v)
        if free:
            free_list.append(free)

        free_count = 0
        for free in free_list:
            free_count += len(free)

        if free_count >= req_count:
            break

    assign = []
    done = False
    for free in free_list:
        for v in free:
            if len(assign) < req_count:
                assign.append(v)
            else:
                done = True
                break
        if done:
            break
    return assign


def assign_imei(req_id):
    myset = db(db.request.id == req_id)
    for record in myset.select():
        print(record.req_count, record.imei_prefix)
        r_total = get_imei_section(record.imei_prefix)
        r_used = get_imei_assign(record.imei_prefix)

        assign = get_free_list(r_total, r_used, record.req_count)

        b = assign[0]
        e = assign[0]
        for i in range(1, len(assign)):
            if assign[i] == e + 1:
                e += 1
            else:
                print(b, e)
                db.imei_assign.insert(request=req_id, assign_start=b, assign_end=e)
                b = assign[i]
                e = assign[i]
        print(b, e)
        db.imei_assign.insert(request=req_id, assign_start=b, assign_end=e)
