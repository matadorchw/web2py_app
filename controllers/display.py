import base64
from io import BytesIO
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Rectangle
import numpy as np
import matplotlib.colors as mcolors

my_colors = ['white', 'wheat', 'skyblue', 'lawngreen']

my_colors_hex = [mcolors.to_rgb(name) for name in my_colors]


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


def get_data_by_req(req_id):
    q = (db.request.id == req_id) & (db.imei_section.imei_prefix == db.request.imei_prefix)
    rows = db(q).select(
        db.imei_section.imei_prefix,
        db.imei_section.section_start,
        db.imei_section.section_end
    )

    imei_prefix = rows.first().imei_prefix

    data = np.empty((1000, 1000, 3), dtype=np.float)

    for i in range(1000):
        for j in range(1000):
            data[i][j] = my_colors_hex[0]

    for r in rows:
        for snr in range(r.section_start, r.section_end + 1):
            data[snr // 1000][snr % 1000] = my_colors_hex[1]

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
                data[snr // 1000][snr % 1000] = my_colors_hex[3]
            else:
                data[snr // 1000][snr % 1000] = my_colors_hex[2]
    return data


def get_data_by_imei_prefix(imei_prefix):
    q = db.imei_section.imei_prefix == imei_prefix
    rows = db(q).select(
        db.imei_section.imei_prefix,
        db.imei_section.section_start,
        db.imei_section.section_end
    )

    data = np.empty((1000, 1000, 3), dtype=np.float)

    for i in range(1000):
        for j in range(1000):
            data[i][j] = my_colors_hex[0]

    for r in rows:
        for snr in range(r.section_start, r.section_end + 1):
            data[snr // 1000][snr % 1000] = my_colors_hex[1]

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
            data[snr // 1000][snr % 1000] = my_colors_hex[2]
    return data


def generate_image(data):
    fig = Figure(figsize=(15, 11))

    gs = GridSpec(5, 7, figure=fig)

    ax1 = fig.add_subplot(gs[:, :5])
    ax1.set_xlim(-50, 1050)
    ax1.set_ylim(-50, 1050)

    ax2 = fig.add_subplot(gs[:, 5:])

    ax2.set_ylim(0, 100)
    ax2.set_xlim(0, 100)
    ax2.yaxis.set_visible(False)
    ax2.xaxis.set_visible(False)
    ax2.set_axis_off()

    names = ['not available', 'can be use', 'used', 'current used']
    for i in range(4):
        ax2.add_patch(
            Rectangle(xy=(0, 2 + i * 11), width=98,
                      height=10, facecolor=my_colors[i], edgecolor='0.7')
        )
        ax2.text(5, 2 + i * 11 + 5, names[i], fontsize=12,
                 horizontalalignment='left',
                 verticalalignment='center')

    ax1.imshow(data, origin='upper')

    buf = BytesIO()
    canvas = FigureCanvasAgg(fig)
    fig.savefig(buf, format="png")
    return base64.b64encode(buf.getvalue()).decode("ascii")


@auth.requires_login()
def detail():
    title = T('All My Requests Detail')
    q = (db.request.create_by == auth.user_id) & (db.request.id == db.imei_assign.request)

    image_data = None

    if request.vars.req_id:
        req_id = int(request.vars.req_id)
        q = (db.request.id == req_id) & q
        title = T('Request Detail') + '[%d]' % req_id
        image_data = generate_image(get_data_by_req(req_id))

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
    return dict(title=title, grid=grid, image_data=image_data)


def imei_prefix_detail():
    title = T('IMEI Prefix')
    image_data = None
    if request.vars.imei_prefix:
        imei_prefix = int(request.vars.imei_prefix)
        image_data = generate_image(get_data_by_imei_prefix(imei_prefix))

        r = db(db.imei_prefix.id == imei_prefix).select().first()
        title = title + ' [{}]{}'.format(r.imei_prefix, r.name)
    response.view = 'default/grid.html'
    return dict(title=title, grid=None, image_data=image_data)


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

try:
    from cStringIO import StringIO
except ImportError:
    try:
        from StringIO import StringIO
    except ImportError:
        from io import StringIO

import csv


@auth.requires_login()
def export_imei_set_by_req():
    if request.vars.req_id:
        response.headers['Content-Type'] = gluon.contenttype.contenttype('.csv')
        req_id = int(request.vars.req_id)
        response.headers['Content-disposition'] = 'attachment; filename=%d.csv' % req_id

        s = StringIO()
        writer = csv.writer(s)
        writer.writerow(['Prefix', 'Snr', 'CRC', 'IMEI'])

        rows = db(
            (db.request.id == req_id) &
            (db.request.id == db.imei_assign.request) &
            (db.imei_prefix.id == db.request.imei_prefix)
        ).select(
            db.imei_prefix.imei_prefix,
            db.imei_assign.assign_start,
            db.imei_assign.assign_end
        )
        for r in rows:
            for snr in range(r.imei_assign.assign_start, r.imei_assign.assign_end + 1):
                imei14 = "%08s%06d" % (r.imei_prefix.imei_prefix, snr)
                d15 = calc_15th_of_imei(imei14)
                writer.writerow([
                    "%08s" % r.imei_prefix.imei_prefix,
                    "%06d" % snr,
                    d15,
                    "%s%d" % (imei14, d15)])

        return s.getvalue()
