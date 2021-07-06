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
                                 body=lambda row: A(T('Detail'),
                                                    _class="btn btn-secondary",
                                                    _href=URL(c="display",
                                                              f="detail",
                                                              vars=dict(req_id=row.id),
                                                              user_signature=True))
                                 ),
                            dict(header='',
                                 body=lambda row: A(T('export as csv file'),
                                                    _class="btn btn-secondary",
                                                    _href=URL(c="display",
                                                              f="export_imei_set_by_req",
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
                            dict(header=T('IMEI Assign Section'),
                                 body=lambda row: get_scope_of_request(row.imei_assign.id))
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


def calc_15th_of_imei(imei14):
    sum = 0
    for i in range(14):
        n = ord(imei14[i]) - ord('0')
        if i % 2:
            sum += (n * 2) // 10 + (n * 2) % 10
        else:
            sum += n

    return (sum % 10) and (10 - sum % 10) or 0


import gluon.contenttype
import cStringIO
import csv


@auth.requires_login()
def export_imei_set_by_req():
    if request.vars.req_id:
        response.headers['Content-Type'] = gluon.contenttype.contenttype('.csv')
        req_id = int(request.vars.req_id)
        response.headers['Content-disposition'] = 'attachment; filename=%d.csv' % req_id

        s = cStringIO.StringIO()
        writer = csv.writer(s)
        writer.writerow(['Prefix', 'Snr', 'CRC', 'IMEI'])

        myset = db(
            (db.request.id == req_id) &
            (db.request.id == db.imei_assign.request) &
            (db.imei_prefix.id == db.request.imei_prefix)
        ).select(
            db.imei_prefix.imei_prefix,
            db.imei_assign.assign_start,
            db.imei_assign.assign_end
        )
        for r in myset:
            for snr in range(r.imei_assign.assign_start, r.imei_assign.assign_end + 1):
                imei14 = "%08s%06d" % (r.imei_prefix.imei_prefix, snr)
                d15 = calc_15th_of_imei(imei14)
                writer.writerow([
                    "%08s" % r.imei_prefix.imei_prefix,
                    "%06d" % snr,
                    d15,
                    "%s%d" % (imei14, d15)])

        return s.getvalue()
