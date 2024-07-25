from fitparse import FitFile
import pandas as pd
import os
import warnings
warnings.filterwarnings("ignore")
from dotenv import load_dotenv
load_dotenv()
import json
import psycopg2
from sqlalchemy import create_engine
import traceback

def connect_to_postgres():
        db_params = json.loads(os.environ.get('PostgreSQL_desktop'))
        cnxn = psycopg2.connect(**db_params)
        cnxn.autocommit = True
        return cnxn
    
def verify_activity_id(activity_id):
    cnxn = connect_to_postgres()
    query = "SELECT activity_id FROM raw_garmin_data_session WHERE activity_id = %s"
    existing_activity_id = pd.read_sql(query, cnxn, params=[activity_id])['activity_id']
    if existing_activity_id.empty:
        cnxn.close()
        return activity_id
    else:
        query = 'select max(activity_id) max_id from raw_garmin_data_session'
        max_activity_id = pd.read_sql(query, cnxn)['max_id'].iloc[0]
        cnxn.close()
        return int(max_activity_id) + 1
    
def generate_temp_id():
    cnxn = connect_to_postgres()
    query = 'select max(temp_id) max_id from raw_garmin_data_session'
    max_temp_id = pd.read_sql(query, cnxn)['max_id'].iloc[0]
    cnxn.close()
    return int(max_temp_id) + 1

def adjust_columns(df, recordType):
    cnxn = connect_to_postgres()
    if recordType == 'lap':
        recordType = 'laps'
    query = f"SELECT * from raw_garmin_data_{recordType} where 1=0"
    column_names = list(pd.read_sql(query, cnxn).columns)
    cnxn.close()
    for cols in column_names:
        if cols not in df.columns:
            if cols in ('description', 'activity_title'):
                df[cols] = ''
            else:
                df[cols] = None
    return df[column_names]
    
def fix_columns_record_df(df):
    all_columns = ['timestamp', 'position_lat', 'position_long','distance', 'enhanced_speed', 'enhanced_altitude', 'heart_rate', 'cadence', 'activity_id']
    fix_columns = ['distance', 'enhanced_speed', 'enhanced_altitude', 'heart_rate', 'cadence']
    if 'fractional_cadence' in df.columns:
        df['cadence'] = df['cadence'].astype(float) + df['fractional_cadence'].astype(float)
    if 'position_lat' not in df.columns or 'position_long' not in df.columns:
        df['position_lat'] = -1
        df['position_long'] = -1
    missing_columns = list(set(fix_columns) - set(df.columns))
    df[missing_columns] = 0.0
    df[fix_columns] = df[fix_columns].fillna(0)
    return df[all_columns]    
    
def process_fit_file(filePath, folder, recordType, lap_activity_id = None):
    try:
        fitfile = FitFile(filePath)
        record_df = pd.DataFrame()
        for record in fitfile.get_messages(recordType):
            record_dict = record.get_values()
            if record_dict:
                record_df = pd.concat([record_df, pd.DataFrame(record_dict, index=[0])], axis=0)
        if not record_df.empty:
            record_df = record_df.reset_index(drop=True)
            if recordType == 'session':
                activity_id_temp = filePath.replace(folder, '').replace(r'\activitie_', '').replace('.fit', '')
                activity_id = verify_activity_id(activity_id_temp)
            else:
                activity_id = lap_activity_id
            record_df['activity_id'] = str(activity_id)
            if recordType == 'session':
                record_df['temp_id'] = generate_temp_id()
                
        if recordType != 'record':
            record_df = adjust_columns(record_df, recordType)
        else:
            record_df = fix_columns_record_df(record_df)
        if recordType == 'session':     
            return record_df, activity_id, activity_id_temp
        else:
            return record_df
    except:
        print(f'Error2 with {filePath.replace(folder, "")} for {recordType}')
        print(traceback.format_exc())
        return pd.DataFrame()

def create_postgres_engine():
    # Define connection parameters
    db_params = json.loads(os.environ.get('PostgreSQL_desktop'))
    user = db_params['user']
    password = db_params['password']
    host = db_params['host']
    database = db_params['dbname']
    
    # Construct the connection string
    connection_string = f"postgresql+psycopg2://{user}:{password}@{host}/{database}"
    
    # Create and return the SQLAlchemy engine
    engine = create_engine(connection_string)
    return engine
def insert_into_sessions(df):
    engine = create_postgres_engine()
    # Use the session to insert data
    df.to_sql('raw_garmin_data_session', engine, if_exists='append', index=False, method='multi')
    engine.dispose()
    return
def insert_into_laps(df):
    engine = create_postgres_engine()
    
    df.to_sql('raw_garmin_data_laps', engine, if_exists='append', index=False, method='multi')
    engine.dispose()
    return    

def insert_into_records(df):
    engine = create_postgres_engine()
    
    df.to_sql('raw_garmin_data_records', engine, if_exists='append', index=False, method='multi')
    engine.dispose()
    return

def change_times(df, start_time=True):
    if start_time:
        df['start_time'] = pd.to_datetime(df['start_time']).dt.tz_localize('UTC')
    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize('UTC')

    # Now convert them to 'America/Chicago'
    if start_time:
        df['start_time'] = df['start_time'].dt.tz_convert('America/Chicago')
    df['timestamp'] = df['timestamp'].dt.tz_convert('America/Chicago')
    return df

if __name__ == '__main__':
    folder = r"C:\Users\mattb\OneDrive\Documents\LoginTEST\garmin data\NEW_UPLOADS"
    files = os.listdir(folder)
    files = [f for f in files if f.endswith('.fit')]
    for file in files:
        try:
            print(f'processing {file}\n')
            filePath = os.path.join(folder, file)
            session_df, activity_id, old_activity_id = process_fit_file(filePath, folder, 'session')
            if not session_df.empty:
                print(f'session processed for {file}')
                session_df = change_times(session_df)
            else:
                print(f'Error1 with  session {file}')
                break
            lap_df = process_fit_file(filePath, folder, 'lap', activity_id)
            if not lap_df.empty:
                print(f'lap processed for {file}')
                lap_df = change_times(lap_df)
            else:
                print(f'Error1 with lap {file}')
                break
            record_df = process_fit_file(filePath, folder, 'record', activity_id)
            if not record_df.empty:
                print(f'record processed for {file}')
                record_df = change_times(record_df, False)
            else:
                print(f'Error1 with record {file}')
                break
            if activity_id != old_activity_id:
                os.rename(filePath, filePath.replace(f'activitie_{old_activity_id}', f'activitie_{activity_id}'))
                print(f'file renamed for {file}')
            insert_into_sessions(session_df)
            print(f'session inserted for {file}')
            insert_into_laps(lap_df)
            print(f'lap inserted for {file}')
            insert_into_records(record_df)
            print(f'record inserted for {file}')
        except:
            print(f'Error with {file}')
            print(traceback.format_exc())
            break
        print('\n')