# coding: utf-8
from sqlalchemy import Column, DateTime, Float, MetaData, Table, Text

metadata = MetaData()


t_record_view = Table(
    'record_view', metadata,
    Column('activity_id', Text),
    Column('timestamp', DateTime(True)),
    Column('latitude', Float(53)),
    Column('longitude', Float(53)),
    Column('distance', Float(53)),
    Column('speed', Float(53)),
    Column('altitude', Float(53)),
    Column('hr', Float(53)),
    Column('cadence', Float(53))
)
