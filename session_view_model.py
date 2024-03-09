# coding: utf-8
from sqlalchemy import Column, DateTime, Float, Integer, MetaData, Table, Text

metadata = MetaData()


t_session_view = Table(
    'session_view', metadata,
    Column('activity_id', Text),
    Column('start_time', DateTime(True)),
    Column('timestamp', DateTime(True)),
    Column('sport', Text),
    Column('sub_sport', Text),
    Column('total_time', Float(53)),
    Column('total_elapsed_time', Float(53)),
    Column('total_distance', Float(53)),
    Column('avg_hr', Integer),
    Column('max_hr', Integer),
    Column('recovery_hr', Integer),
    Column('avg_running_cadence', Integer),
    Column('max_running_cadence', Integer),
    Column('total_strides', Integer),
    Column('resting_calories', Integer),
    Column('total_calories', Integer),
    Column('sweat_loss', Integer),
    Column('total_descent', Integer),
    Column('total_ascent', Integer),
    Column('total_cycles', Integer),
    Column('activity_title', Text),
    Column('description', Text)
)
