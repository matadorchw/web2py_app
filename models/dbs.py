db.auth_user._format = "%(first_name)s"
# auth.settings.actions_disabled = ['register']


db.define_table(
    'imei_prefix',
    Field('name', unique=True, label=T('name')),
    Field('imei_prefix', label=T('IMEI Prefix')),
    format='[%(imei_prefix)s] %(name)s'
)
db.imei_prefix.id.label = T('IMEI Prefix Id')

db.define_table(
    'imei_section',
    Field('name', unique=True, label=T('name')),
    Field('imei_prefix', db.imei_prefix,
          requires=IS_IN_DB(db, db.imei_prefix.id, '[%(imei_prefix)s] %(name)s'),
          label=T('IMEI Prefix')),
    Field('section_start', 'integer', default=0,
          label=T('Section Start'),
          represent=lambda v, row: "%06d" % v),
    Field('section_end', 'integer', default=999999,
          label=T('Section End'),
          represent=lambda v, row: "%06d" % v),
    format='%(name)s [%(imei_prefix)s]'
)
db.imei_section.id.label = T('IMEI Section Id')

db.define_table(
    'request',
    Field('description', unique=True, label=T('Description')),
    Field('req_count', 'integer', label=T('Request Count')),
    Field('imei_prefix', db.imei_prefix,
          requires=IS_IN_DB(db, db.imei_prefix.id, '[%(imei_prefix)s] %(name)s'),
          label=T('IMEI Prefix')),
    Field('create_on', 'datetime', default=request.now, label=T('Create Time')),
    Field('create_by', db.auth_user, default=auth.user_id, label=T('Create By'))
)
db.request.description.requires = [IS_NOT_EMPTY(), IS_NOT_IN_DB(db, db.request.description)]
db.request.req_count.requires = IS_NOT_EMPTY()
db.request.imei_prefix.requires = IS_NOT_EMPTY()
db.request.create_on.writable = False
db.request.create_by.writable = False
db.request.id.label = T('Request Id')

db.define_table(
    'imei_assign',
    Field('request', db.request, requires=IS_IN_DB(db, db.request.id, '%(description)s'), label=T('Request')),
    Field('assign_start', 'integer', represent=lambda v, row: "%06d" % v, label=T('Assign Start')),
    Field('assign_end', 'integer', represent=lambda v, row: "%06d" % v, label=T('Assign End'))
)
db.imei_assign.id.label = T('IMEI Assign Id')


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


def get_scope_of_request(imei_assign_id):
    myset = db(
        (db.imei_assign.id == imei_assign_id) &
        (db.request.id == db.imei_assign.request) &
        (db.imei_prefix.id == db.request.imei_prefix)
    )

    r = myset.select(db.imei_prefix.imei_prefix, db.imei_assign.assign_start, db.imei_assign.assign_end).first()
    return "[%s%06d - %s%06d] %d" % (
        r.imei_prefix.imei_prefix,
        r.imei_assign.assign_start,
        r.imei_prefix.imei_prefix,
        r.imei_assign.assign_end,
        r.imei_assign.assign_end - r.imei_assign.assign_start + 1
    )


def get_free_list(r_total, r_used, req_count):
    assign_list = []
    count = 0
    for b1, e1 in r_total:
        used_list = []
        for b2, e2 in r_used:
            if b2 > e1:
                break
            if e2 < b1:
                continue
            used_list.append((b2, e2))

        # free in this section
        free_list = []

        if not used_list:
            free_list.append((b1, e1))
        else:
            for i in range(len(used_list)):
                b, e = used_list[i]
                if i == 0:
                    # head
                    if b > b1:
                        free_list.append((b1, b - 1))
                elif i > 0:
                    # body
                    b_pre, e_pre = used_list[i - 1]
                    if b > e_pre + 1:
                        free_list.append((e_pre + 1, b - 1))

                if i == len(used_list) - 1:
                    if e < e1:
                        # tail
                        free_list.append((e + 1, e1))

        for b, e in free_list:
            count_new = count + e - b + 1
            if count_new < req_count:
                assign_list.append((b, e))
                count = count_new
            else:
                assign_list.append((b, b + req_count - count - 1))
                count = req_count
                break

        if count >= req_count:
            break

    if count != req_count:
        print('{} - {}'.format(count, req_count))

    return assign_list


def assign_imei(req_id):
    myset = db(db.request.id == req_id)
    for record in myset.select():
        r_total = get_imei_section(record.imei_prefix)
        r_used = get_imei_assign(record.imei_prefix)

        assign_list = get_free_list(r_total, r_used, record.req_count)
        for b, e in assign_list:
            db.imei_assign.insert(request=req_id, assign_start=b, assign_end=e)


import numpy as np


def get_data_by_req(req_id):
    data = np.zeros((1000, 1000), dtype=np.int)
    rows = db(
        (db.request.id == req_id) &
        (db.imei_section.imei_prefix == db.request.imei_prefix)
    ).select(
        db.imei_section.imei_prefix,
        db.imei_section.section_start,
        db.imei_section.section_end
    )

    imei_prefix = rows.first().imei_prefix

    for r in rows:
        for snr in range(r.section_start, r.section_end + 1):
            data[snr // 1000][snr % 1000] = 1

    rows = db(
        (db.request.imei_prefix == imei_prefix) &
        (db.imei_assign.request == db.request.id)
    ).select(
        db.request.id,
        db.imei_assign.assign_start,
        db.imei_assign.assign_end
    )
    for r in rows:
        for snr in range(r.imei_assign.assign_start, r.imei_assign.assign_end + 1):
            if r.request.id == req_id:
                data[snr // 1000][snr % 1000] = 3
            else:
                data[snr // 1000][snr % 1000] = 2

    return data
