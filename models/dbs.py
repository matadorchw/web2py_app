db.auth_user._format = "%(first_name)s"
# auth.settings.actions_disabled = ['register']

db.define_table(
    'imei_prefix',
    Field('name', unique=True),
    Field('imei_prefix'),
    format='%(name)s [%(imei_prefix)s]'
)

db.define_table(
    'imei_section',
    Field('name', unique=True),
    Field('imei_prefix', db.imei_prefix,
          requires=IS_IN_DB(db, db.imei_prefix.id, '%(name)s [%(imei_prefix)s]')),
    Field('section_start', 'integer', default=0),
    Field('section_end', 'integer', default=999999),
    format='%(name)s [%(imei_prefix)s]'
)

db.define_table(
    'request',
    Field('description', unique=True, label=T('description')),
    Field('req_count', 'integer'),
    Field('imei_prefix', db.imei_prefix,
          requires=IS_IN_DB(db, db.imei_prefix.id, '%(name)s [%(imei_prefix)s]')),
    Field('create_on', 'datetime', default=request.now, label=T('create time')),
    Field('create_by', db.auth_user, default=auth.user_id, label=T('create by'))
)
db.request.description.requires = IS_NOT_EMPTY()
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
