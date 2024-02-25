import psycopg2
import bcrypt
import json
import os
import pandas as pd

class DataAccess:

    def connect_to_postgres(self):
        db_params = json.loads(os.environ.get('PostgreSQL_desktop'))
        cnxn = psycopg2.connect(**db_params)
        cnxn.autocommit = True
        return cnxn
    
    def verify_user(self, username, password):
        cnxn = self.connect_to_postgres()
        query = 'select * from public.accounts where "userid" = %s'
        users = pd.read_sql_query(query, cnxn, params=[username])
        cnxn.close()
        stored_password_bytes = bytes(users['password'].iloc[0])
        if not users.empty:
            provided_password_bytes = password.encode('utf-8')
            # Verify the password
            if bcrypt.checkpw(provided_password_bytes, stored_password_bytes):
                return users['accountid'].iloc[0]  # Login successful
            else:
                return None  # Password does not match
        else:
            return None

    def get_new_account_id(self):
        cnxn = self.connect_to_postgres()
        query = 'select max(AccountId) as max from public.accounts'
        df = pd.read_sql_query(query, cnxn)
        cnxn.close()
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
        cnxn = self.connect_to_postgres()
        query = '''
            insert into public.accounts("accountid", "firstname", "lastname", "userid", "password", "creationdate")
            values(%s,%s,%s,%s,%s, current_timestamp)    
        '''
        params = [self.get_new_account_id(), firstname, lastname, userid, self.hash_password(password)]
        cnxn.cursor().execute(query, params)
        cnxn.commit()
        cnxn.close()
        return
    
    def create_cookie(self, value):
        cnxn = self.connect_to_postgres()
        query = 'insert into public.cookies(value) VALUES (%s) returning id'
        cursor = cnxn.cursor()
        cursor.execute(query, (value,))
        cnxn.commit()
        id = cursor.fetchone()[0]
        cnxn.close()
        return id

    def delete_cookie(self, id):
        cnxn = self.connect_to_postgres()
        query = 'delete from public.cookies where id = %s'
        cursor = cnxn.cursor()
        cursor.execute(query, (id,))
        cnxn.commit()
        cnxn.close()
        return

    def get_cookie_value(self, id):
        cnxn = self.connect_to_postgres()
        query = 'select value from public.cookies where id = %s'
        cursor = cnxn.cursor()
        cursor.execute(query, (id,))
        value = cursor.fetchone()[0]
        cnxn.close()
        
        self.delete_cookie(id)
        return value   
    
    def get_activity_info_by_date(self, date):
        cnxn = self.connect_to_postgres()
        cnxn.autocommit = False
        cursor = cnxn.cursor()
        cursor.callproc('get_activity_info_by_date', (date,))

        session_curs, lap_curs = cursor.fetchone()

        session_info = pd.read_sql_query(f'FETCH ALL IN "{session_curs}"', cnxn)
        session_info = session_info
        lap_info = pd.read_sql_query(f'FETCH ALL IN "{lap_curs}"', cnxn)

        cnxn.close()
        return session_info, lap_info

    def get_activity_info_by_date_range(self, start_date, end_date):
        cnxn = self.connect_to_postgres()
        cnxn.autocommit = False
        cursor = cnxn.cursor()
        cursor.callproc('get_activity_info_by_date_range', (start_date, end_date))

        session_curs, lap_curs = cursor.fetchone()

        session_info = pd.read_sql_query(f'FETCH ALL IN "{session_curs}"', cnxn)
        session_info = session_info
        lap_info = pd.read_sql_query(f'FETCH ALL IN "{lap_curs}"', cnxn)
        cnxn.close()
        return session_info, lap_info
    
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
