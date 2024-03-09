# coding: utf-8
from sqlalchemy import Column, DateTime, Float, Integer, MetaData, Table, Text

metadata = MetaData()


t_lap_view = Table(
    'lap_view', metadata,
    Column('activity_id', Text),
    Column('start_time', DateTime(True)),
    Column('timestamp', DateTime(True)),
    Column('sport', Text),
    Column('total_time', Float(53)),
    Column('total_elapsed_time', Float(53)),
    Column('total_distance', Float(53)),
    Column('lap_num', Integer),
    Column('total_calories', Integer),
    Column('avg_speed', Float(53)),
    Column('avg_hr', Integer),
    Column('max_hr', Integer),
    Column('avg_running_cadence', Integer),
    Column('max_running_cadence', Integer),
    Column('total_strides', Integer),
    Column('total_moving_time', Integer),
    Column('total_cycles', Float(53)),
    Column('avg_cadence', Integer),
    Column('max_cadence', Integer),
    Column('max_speed', Float(53)),
    Column('total_ascent', Integer),
    Column('total_descent', Integer),
    Column('workout_step', Integer),
    Column('lap_trigger', Text),
    Column('sub_sport', Text)
)
