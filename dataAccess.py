import psycopg2
import bcrypt
import json
import pandas as pd
import uuid
from config import Config as environ

class DataAccess:
    def __init__(self, redis_cnxn=None):
        # self.redis_cnxn = redis_cnxn
        pass

    def connect_to_postgres(self):
        db_params = json.loads(environ.PG_DESKTOP)
        cnxn = psycopg2.connect(**db_params)
        cnxn.autocommit = True
        return cnxn
    
    def verify_user(self, username, password):
        with self.connect_to_postgres() as cnxn:
            query = 'select id, userid, password from public.accounts where "userid" = %s'
            users = pd.read_sql_query(query, cnxn, params=[username])
        if not users.empty:
            stored_password_bytes = bytes(users['password'].iloc[0])
            provided_password_bytes = password.encode('utf-8')
            # Verify the password
            if bcrypt.checkpw(provided_password_bytes, stored_password_bytes):
                return users['id'].iloc[0]  # Login successful
            else:
                return None  # Password does not match
        else:
            return None

    def get_new_account_id(self):
        with self.connect_to_postgres() as cnxn:
            query = 'select max(AccountId) as max from public.accounts'
            df = pd.read_sql_query(query, cnxn)
        if len(df)==0 or df.iloc[0]['max'] is None:
            return 1
        return int(int(df.iloc[0]['max']) + 1)

    def hash_password(self, password):
        # Convert the password to bytes
        password_bytes = password.encode('utf-8')
        # Generate a salt and hash the password
        hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        return hashed

    def register_user(self, firstname, lastname, userid, password):
        with self.connect_to_postgres() as cnxn:          
            query = '''
                insert into public.accounts("id", "firstname", "lastname", "userid", "password", "creationdate")
                values(%s,%s,%s,%s,%s, current_timestamp)    
            '''
            params = [self.get_new_account_id(), firstname, lastname, userid, self.hash_password(password)]
            cnxn.cursor().execute(query, params)
            cnxn.commit()
        return
    
    # def create_cookie(self, value, expire=3600):
    #     cookie_key = str(uuid.uuid4())
    #     self.redis_cnxn.setex(cookie_key, expire, value)
    #     return cookie_key

    # def get_cookie_value(self, id):
    #     value = self.redis_cnxn.get(id)
    #     if value:
    #         return value.decode('utf-8')
    #     print('no value from redis')
    #     return None
        
    def convert_timestamps(self, df, columns, from_tz='UTC', to_tz='America/Chicago'):
        for column in columns:
            if column in df.columns and pd.api.types.is_datetime64_any_dtype(df[column]):
                # Check if the datetime data is naive or timezone-aware
                if df[column].dt.tz is None:
                    # If naive, localize to the original timezone then convert
                    df[column] = pd.to_datetime(df[column]).dt.tz_localize(from_tz, ambiguous='infer').dt.tz_convert(to_tz)
                else:
                    # If already timezone-aware, directly convert to the new timezone
                    df[column] = df[column].dt.tz_convert(to_tz)
        return df
    
    def get_recent_posts(self, accountid,  offset, limit, sport):
        with self.connect_to_postgres() as cnxn:
            cnxn.autocommit = False
            with cnxn.cursor() as cursor:
                cursor.callproc('get_recent_posts', (accountid, sport, offset, limit))

                session_curs, lap_curs, record_curs = cursor.fetchone()
                
                session_df = pd.read_sql_query(f'FETCH ALL IN "{session_curs}"', cnxn)
                lap_df = pd.read_sql_query(f'FETCH ALL IN "{lap_curs}"', cnxn)
                record_df = pd.read_sql_query(f'FETCH ALL IN "{record_curs}"', cnxn)
        return session_df, lap_df, record_df

    def get_activity_info_by_date(self, date, accountid):
        with self.connect_to_postgres() as cnxn:
            cnxn.autocommit = False
            with cnxn.cursor() as cursor:
                cursor.callproc('get_activity_info_by_date', (date, accountid))

                session_curs, lap_curs, record_curs = cursor.fetchone()

                session_info = self.convert_timestamps(pd.read_sql_query(f'FETCH ALL IN "{session_curs}"', cnxn), ['start_time', 'timestamp'])
                lap_info = self.convert_timestamps(pd.read_sql_query(f'FETCH ALL IN "{lap_curs}"', cnxn), ['start_time', 'timestamp'])
                record_info = self.convert_timestamps(pd.read_sql_query(f'FETCH ALL IN "{record_curs}"', cnxn), ['timestamp'])

        return session_info, lap_info, record_info

    def get_activity_info_by_date_range(self, start_date, end_date, accountid):
        with self.connect_to_postgres() as cnxn:
            cnxn.autocommit = False
            with cnxn.cursor() as cursor:
                cursor = cnxn.cursor()
                cursor.callproc('get_activity_info_by_date_range', (start_date, end_date, accountid))

                session_curs, lap_curs, record_curs = cursor.fetchone()

                session_info = self.convert_timestamps(pd.read_sql_query(f'FETCH ALL IN "{session_curs}"', cnxn), ['start_time', 'timestamp'])
                lap_info = self.convert_timestamps(pd.read_sql_query(f'FETCH ALL IN "{lap_curs}"', cnxn), ['start_time', 'timestamp'])
                record_info = self.convert_timestamps(pd.read_sql_query(f'FETCH ALL IN "{record_curs}"', cnxn), ['timestamp'])

        return session_info, lap_info, record_info
    
    def updateTitle(self, new_title, new_description, new_timestamp, activity_id):
        #check to see what is getting passed as new title, new description, new timestamp
        new_title = None if new_title == '' else new_title
        new_description = None if new_description == '' else new_description
        new_timestamp = None if new_timestamp == '' else new_timestamp
        cnxn = self.connect_to_postgres()
        cnxn.autocommit = True
        # call function edit title with above params
        cursor = cnxn.cursor()
        query = 'select public.edittitle(%s, %s, %s, %s)'
        cursor.execute(query, (activity_id, new_title, new_description, new_timestamp))
        # cursor.callproc('edittitle', (activity_id, new_title, new_description, new_timestamp))
        cursor.close()
        cnxn.close()
        return
    
    def get_activity_by_id(self, activity_id, accountid):
        with self.connect_to_postgres() as cnxn:
            query = 'select * from session_info(%s, null, null, null, %s)'
            session_info = pd.read_sql_query(query, cnxn, params=[activity_id, accountid])
            query = 'select * from lap_info(%s, null, null, null, %s)'
            lap_info = pd.read_sql_query(query, cnxn, params=[activity_id, accountid])
            query = 'select * from record_info(%s, null, null, %s)'
            record_info = pd.read_sql_query(query, cnxn, params=[activity_id, accountid])
        return session_info, lap_info, record_info
    
    def get_raw_session_by_activity_id(self, activity_id, accountid):
        with self.connect_to_postgres() as cnxn:
            query = 'select * from raw_garmin_data_session where activity_id = %s and accountid = %s'
            session_info = pd.read_sql_query(query, cnxn, params=[activity_id, accountid])
        return session_info
    
    def get_raw_lap_by_activity_id(self, activity_id, accountid):
        with self.connect_to_postgres() as cnxn:
            query = 'select * from raw_garmin_data_laps where activity_id = %s and accountid = %s order by message_index'
            lap_info = pd.read_sql_query(query, cnxn, params=[activity_id, accountid])
        return lap_info
    
    def get_raw_record_by_activity_id(self, activity_id, accountid):
        with self.connect_to_postgres() as cnxn:
            query = 'select * from raw_garmin_data_records where activity_id = %s and accountid = %s order by timestamp'
            record_info = pd.read_sql_query(query, cnxn, params=[activity_id, accountid])
        return record_info
    
    def get_calendar_info(self, year, month, accountid):
        with self.connect_to_postgres() as cnxn:
            query = 'select * from public.calendar_info(%s, %s)'
            df = self.convert_timestamps(pd.read_sql_query(query, cnxn, params=[month, year]), ['start_time'])
        return df
    
    def search_activities_for_editing(self, date, title, accountid):
        with self.connect_to_postgres() as cnxn:
            query = 'SELECT * from public.search_activity_by_date(%s, %s, %s)'
            df = pd.read_sql_query(query, cnxn, params=[date, title, accountid])
        return df
    
    def get_lap_columns(self):
        with self.connect_to_postgres() as cnxn:
            query = 'select * from raw_garmin_data_laps where 1=0'
            df = pd.read_sql_query(query, cnxn)
        return df.columns.tolist()
    
    def generate_new_activity_id(self):
        with self.connect_to_postgres() as cnxn:
            query = 'select max(activity_id) as max from session_info()'
            df = pd.read_sql_query(query, cnxn)
        if len(df)==0 or df.iloc[0]['max'] is None:
            return 1
        return int(df.iloc[0]['max']) + 1

    def generate_new_temp_id(self):
        with self.connect_to_postgres() as cnxn:
            query = 'select max(temp_id) as max from raw_garmin_data_session'
            df = pd.read_sql_query(query, cnxn)
        if len(df)==0 or df.iloc[0]['max'] is None:
            return 1
        return int(df.iloc[0]['max']) + 1
    
    def insert_dataframe(self, table_name, df, cnxn):
        query = f'insert into raw_garmin_data_{table_name} ({", ".join(df.columns)}) values ({", ".join(["%s" for i in range(len(df.columns))])})'
        with cnxn.cursor() as cursor:
            for row in df.itertuples(index=False):
                cursor.execute(query, row)
        return

    def insert_merge_activity_history(self, merged_activity_id, activity1_id, activity2_id, cnxn):
        with cnxn.cursor() as cursor:
            cursor.execute('''
                insert into merged_activities(merged_activity_id, activity1_id, activity2_id, merge_date)
                values (%s, %s, %s, current_timestamp)
            ''', (merged_activity_id, activity1_id, activity2_id))
        return
    
    def get_merge_activity_by_merge_id(self, merge_id):
        with self.connect_to_postgres() as cnxn:
            with cnxn.cursor() as cursor:
                cursor.execute('select merged_activity_id, activity1_id, activity2_id from merged_activities where id = %s', 
                    (merge_id,))
                results = cursor.fetchone()
        return results
    
    def get_merge_id_by_merged_activity_id(self, merge_activity_id):
        with self.connect_to_postgres() as cnxn:
            with cnxn.cursor() as cursor:
                cursor.execute('select id from merged_activities where merged_activity_id = %s', 
                    (merge_activity_id,))
                results = cursor.fetchone()
        return results[0] if results else None
    
    def get_merge_activity_by_activity_ids(self, activity1_id, activity2_id):
        with self.connect_to_postgres() as cnxn:
            with cnxn.cursor() as cursor:
                cursor.execute('select merged_activity_id from merged_activities where activity1_id = %s and activity2_id = %s', 
                    (activity1_id, activity2_id))
                results = cursor.fetchone()
        return results[0] if results else None
    
    def mark_activity_as_invisible(self, activity_id, cnxn):
        with cnxn.cursor() as cursor:
            cursor.execute('''
                update raw_garmin_data_session
                set is_visible = false
                where activity_id = %s
            ''', (activity_id,))
        return
    
    def mark_activity_as_visible(self, activity_id, cnxn):
        with cnxn.cursor() as cursor:
            cursor.execute('''
                update raw_garmin_data_session
                set is_visible = true
                where activity_id = %s
            ''', (activity_id,))
                