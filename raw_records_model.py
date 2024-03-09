# coding: utf-8
from sqlalchemy import Column, DateTime, Float, MetaData, Table, Text

metadata = MetaData()


t_raw_garmin_data_records = Table(
    'raw_garmin_data_records', metadata,
    Column('timestamp', DateTime(True)),
    Column('position_lat', Float(53)),
    Column('position_long', Float(53)),
    Column('distance', Float(53)),
    Column('enhanced_speed', Float(53)),
    Column('enhanced_altitude', Float(53)),
    Column('heart_rate', Float(53)),
    Column('cadence', Float(53)),
    Column('activity_id', Text)
)
