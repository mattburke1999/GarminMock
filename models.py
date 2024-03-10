# coding: utf-8
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, Table, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


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


class RawGarminDataSession(Base):
    __tablename__ = 'raw_garmin_data_session'

    activity_id = Column(Text, primary_key=True)
    start_time = Column(DateTime(True))
    timestamp = Column(DateTime(True))
    sport = Column(Text)
    sub_sport = Column(Text)
    total_timer_time = Column(Text)
    total_elapsed_time = Column(Text)
    total_distance = Column(Text)
    total_cycles = Column(Text)
    total_calories = Column(Text)
    start_position_lat = Column(Text)
    start_position_long = Column(Text)
    message_index = Column(Text)
    enhanced_avg_speed = Column(Text)
    avg_speed = Column(Text)
    first_lap_index = Column(Text)
    num_laps = Column(Text)
    event = Column(Text)
    event_type = Column(Text)
    avg_heart_rate = Column(Text)
    max_heart_rate = Column(Text)
    avg_running_cadence = Column(Text)
    max_running_cadence = Column(Text)
    trigger = Column(Text)
    total_strides = Column(Text)
    total_moving_time = Column(Text)
    avg_pos_vertical_speed = Column(Text)
    unknown_33 = Column(Text)
    num_active_lengths = Column(Text)
    unknown_142 = Column(Text)
    unknown_157 = Column(Text)
    unknown_158 = Column(Text)
    avg_cadence = Column(Text)
    max_cadence = Column(Text)
    nec_lat = Column(Text)
    nec_long = Column(Text)
    swc_lat = Column(Text)
    swc_long = Column(Text)
    unknown_110 = Column(Text)
    enhanced_max_speed = Column(Text)
    max_speed = Column(Text)
    total_ascent = Column(Text)
    total_descent = Column(Text)
    total_training_effect = Column(Text)
    unknown_81 = Column(Text)
    avg_fractional_cadence = Column(Text)
    max_fractional_cadence = Column(Text)
    unknown_38 = Column(Text)
    unknown_39 = Column(Text)
    unknown_152 = Column(Text)
    unknown_151 = Column(Text)
    unknown_196 = Column(Text)
    unknown_178 = Column(Text)
    unknown_184 = Column(Text)
    unknown_202 = Column(Text)
    temp_id = Column(Integer)
    activity_title = Column(Text)
    description = Column(Text)


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


t_raw_garmin_data_laps = Table(
    'raw_garmin_data_laps', metadata,
    Column('timestamp', DateTime(True)),
    Column('start_time', DateTime(True)),
    Column('start_position_lat', Text),
    Column('start_position_long', Text),
    Column('end_position_lat', Text),
    Column('end_position_long', Text),
    Column('total_elapsed_time', Text),
    Column('total_timer_time', Text),
    Column('total_distance', Text),
    Column('message_index', Text),
    Column('total_calories', Text),
    Column('enhanced_avg_speed', Text),
    Column('avg_speed', Text),
    Column('event', Text),
    Column('event_type', Text),
    Column('avg_heart_rate', Text),
    Column('max_heart_rate', Text),
    Column('avg_running_cadence', Text),
    Column('max_running_cadence', Text),
    Column('lap_trigger', Text),
    Column('sport', Text),
    Column('activity_id', ForeignKey('raw_garmin_data_session.activity_id', ondelete='CASCADE', onupdate='CASCADE')),
    Column('total_strides', Text),
    Column('total_moving_time', Text),
    Column('avg_pos_vertical_speed', Text),
    Column('num_active_lengths', Text),
    Column('unknown_125', Text),
    Column('unknown_126', Text),
    Column('total_cycles', Text),
    Column('avg_cadence', Text),
    Column('max_cadence', Text),
    Column('unknown_27', Text),
    Column('unknown_28', Text),
    Column('unknown_29', Text),
    Column('unknown_30', Text),
    Column('enhanced_max_speed', Text),
    Column('max_speed', Text),
    Column('total_ascent', Text),
    Column('total_descent', Text),
    Column('wkt_step_index', Text),
    Column('sub_sport', Text),
    Column('avg_fractional_cadence', Text),
    Column('max_fractional_cadence', Text),
    Column('unknown_155', Text),
    Column('unknown_145', Text)
)


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
    Column('activity_id', ForeignKey('raw_garmin_data_session.activity_id', ondelete='CASCADE', onupdate='CASCADE'))
)
