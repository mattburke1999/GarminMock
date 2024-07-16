import pandas as pd
import folium

mile_dist = 1609.344

class DataTransform:
    
    def time_seconds_to_string(self, seconds):
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        seconds = seconds % 60
        seconds = round(seconds, 3) if seconds > 9 else f"0{round(seconds,3)}"
        if hours == 0:
            return f'{minutes}:{seconds}'
        else:
            return f'{hours}:{minutes if minutes > 9 else f"0{minutes}"}:{seconds}'

    def prepare_running(self, df):
        df['Distance'] = df['total_distance'].apply(lambda x: float(round(x/mile_dist, 3)))
        df['Pace'] = df.apply(lambda row: self.time_seconds_to_string(row['total_time'] / (row['total_distance'] / mile_dist)), axis=1)
        df['Elapsed Pace'] = df.apply(lambda row: self.time_seconds_to_string(row['total_elapsed_time'] / (row['total_distance'] / mile_dist)), axis=1)
        df['Avg Cadence'] = df['avg_running_cadence'].apply(lambda x: int(x))
        df['Max Cadence'] = df['max_running_cadence'].apply(lambda x: int(x))
        df['Steps'] = df['total_strides'].apply(lambda x: int(x))
        df['Avg Stride Length'] = df.apply(lambda row: round(row['total_distance'] / row['total_strides'], 2), axis=1)
        return df
        
    def prepare_cycling(self, df):
        df['Distance'] = df['total_distance'].apply(lambda x: float(round(x/mile_dist, 3)))
        df['Speed'] = df.apply(lambda row: float(round((row['total_distance'] / mile_dist) / (row['total_time'] / 3600), 2)), axis=1)
        df['Elapsed Speed'] = df.apply(lambda row: float(round((row['total_distance'] / mile_dist) / (row['total_elapsed_time'] / 3600), 2)), axis=1)
        return df

    def prepare_rowing(self, df):
        df['Distance'] = df['total_distance'].apply(lambda x: float(x))
        df['Pace'] = df.apply(lambda row: self.time_seconds_to_string(row['total_time'] / (row['total_distance'] / 500) if row['total_distance']!=0 else 0), axis=1)
        df['Elapsed Pace'] = df.apply(lambda row: self.time_seconds_to_string(row['total_elapsed_time'] / (row['total_distance'] / 500) if row['total_distance']!=0 else 0), axis=1)
        df['Total Strokes'] = df['total_cycles'].apply(lambda x: int(x))
        df['Stroke Rate'] = df.apply(lambda row: float(round((row['total_cycles'] / (row['total_time'] / 60)),2)), axis=1)
        df['Elapsed Stroke Rate'] = df.apply(lambda row: float(round((row['total_cycles'] / (row['total_elapsed_time'] / 60)),2)), axis=1)
        return df
        
    def prepare_lap_info(self, df, activity_id_list):
        # drop all rows where df['activity_id'] is not in activity_id_list
        df = df[df['activity_id'].isin(activity_id_list)]
        cols = df.columns.tolist()
        df['lap'] = df['lap_num']
        df['distance'] = df['total_distance'].apply(lambda x: round(x/mile_dist, 2))
        df['duration'] = df['total_time'].apply(lambda x: self.time_seconds_to_string(x))
        df['elapsed time'] = df['total_elapsed_time'].apply(lambda x: self.time_seconds_to_string(x))
        df['avg_speed'] = df['avg_speed'].apply(lambda x: round(mile_dist/(60*x), 2) if x > 0 else 0)
        df['pace_calc'] = df.apply(lambda row: row['total_time'] / (row['total_distance'] / mile_dist) if row['total_distance'] != 0 else 0, axis=1)    # set df['pace'] = df['avg_speed'] if avg_speed > 0 else pace_calc
        df['pace'] = df.apply(lambda row: row['avg_speed'] if row['avg_speed'] > 0 else row['pace_calc'], axis=1)
        df['pace'] = df['pace'].apply(lambda x: self.time_seconds_to_string(x))
        df['max_speed'] = df['max_speed'].apply(lambda x: round(mile_dist/(60*x), 2) if x > 0 else 0)
        df['best pace'] = df['max_speed'].apply(lambda x: x if x > 0 else 0)
        df['avg hr'] = df['avg_hr']
        df['max hr'] = df['max_hr']
        df['avg cadence'] = df['avg_running_cadence']
        df['max cadence'] = df['max_running_cadence']
        df['steps'] = df['total_strides']
        df['avg stride length'] = df.apply(lambda row: round(row['total_distance'] / row['total_strides'], 2) if row['total_strides'] > 0 else 0, axis=1)
        df['calories'] = df['total_calories']
        df['total ascent'] = df['total_ascent']
        df['total descent'] = df['total_descent']
        cols.append('pace_calc')
        cols.remove('activity_id')
        df = df.sort_values(by=['start_time', 'lap'])
        df = df.drop(cols, axis=1)
        lap_list = []
        for activity_id in activity_id_list:
            lap_df = df[df['activity_id'] == activity_id]
            lap_list.append(lap_df.to_dict('records'))
        # html_list = self.lap_dfs_to_htmls(df)
        # print(list(df.columns))
        # return html_list
        return lap_list
    
    def set_display_sport(self, sport, sub_sport):
        display_sport = sport if sport in ('running', 'cycling', 'rowing') and sub_sport in ('generic', None) else sub_sport
        display_sport = display_sport.replace('_', ' ').title()
        return display_sport

    def prepare_multiple_activities(self, df):
        cols_to_remove = list(df.columns)
        df['Activity Title'] = df['activity_title'].apply(lambda x: x.title())
        df['Description'] = df['description']
        df['Date'] = df['start_time'].apply(lambda x: x.strftime('%A, %B %d %I:%M %p').replace(" 0", " "))
        df['Sport'] = df['sport'].apply(lambda x: x.title())
        df['DisplaySport'] = df.apply(lambda x: self.set_display_sport(x['sport'], x['sub_sport']), axis=1)
        df['Duration'] = df['total_time'].apply(lambda x: self.time_seconds_to_string(x))
        df['Elapsed Time'] = df['total_elapsed_time'].apply(lambda x: self.time_seconds_to_string(x))
        df['Avg HR'] = df['avg_hr'].apply(lambda x: int(x))
        df['Max HR'] = df['max_hr'].apply(lambda x: int(x))
        df['Recovery HR'] = df['recovery_hr'].apply(lambda x: int(x))
        df['Resting Calories'] = df['resting_calories'].apply(lambda x: int(x))
        df['Total Calories'] = df['total_calories'].apply(lambda x: int(x))
        df['Active Calories'] = df.apply(lambda row: int(row['total_calories'] - row['resting_calories']), axis=1)
        df['Sweat Loss'] = df['sweat_loss'].apply(lambda x: int(x))
        df['Total Descent'] = df['total_descent'].apply(lambda x: round(float(x * 3.28084), 3))
        df['Total Ascent'] = df['total_ascent'].apply(lambda x: round(float(x * 3.28084), 3))
        running_df = self.prepare_running(df[df['sport'] == 'running'])
        cycling_df = self.prepare_cycling(df[df['sport'] == 'cycling'])
        rowing_df = self.prepare_rowing(df[df['sport'] == 'rowing'])
        other_df = df[~df['sport'].isin(['running', 'cycling', 'rowing'])]
        df = pd.concat([running_df, cycling_df, rowing_df, other_df])
        df = df.sort_values(by=['start_time'])
        cols_to_remove.remove('activity_id')
        df = df.drop(cols_to_remove, axis=1)
        # convert to list of dictionaries
        activity_list = df.to_dict('records')
        return activity_list
    
    def build_map(self, record_info):
        record_info = record_info[(record_info['latitude'] != -1) & (record_info['longitude'] != -1)]
        # drop rows wher lat or long is na
        record_info = record_info.dropna(subset=['latitude', 'longitude'])
        map = None
        if len(record_info) > 0:
            min_lat = record_info['latitude'].min()
            min_long = record_info['longitude'].min()
            max_lat = record_info['latitude'].max()
            max_long = record_info['longitude'].max()


            avg_lat = (min_lat + max_lat) / 2
            avg_long = (min_long + max_long) / 2
            map = folium.Map(location=[avg_lat, avg_long])
            map.fit_bounds([[min_lat, min_long], [max_lat, max_long]])
            # creata a list of lat and long tuples
            points = list(zip(record_info['latitude'], record_info['longitude']))
            map.add_child(folium.PolyLine(points, color="blue", weight=2.5, opacity=1))
            # add markers for start and end of activity
            folium.Marker([record_info['latitude'].iloc[0], record_info['longitude'].iloc[0]], popup='Start').add_to(map)
            folium.Marker([record_info['latitude'].iloc[-1], record_info['longitude'].iloc[-1]], popup='End').add_to(map)
        return map
    
    def prepare_record_info(self, record_info, activity_id_list):
        map_htmls = []
        record_info = record_info[record_info['activity_id'].isin(activity_id_list)]
        record_info = record_info.sort_values('timestamp')
        for activity_id in activity_id_list:
            activity_df = record_info[record_info['activity_id'] == activity_id]
            map_folium = self.build_map(activity_df)
            if map_folium:
                map_html = map_folium._repr_html_().replace('padding-bottom:60%;', 'padding-bottom:30%;')
            else:
                map_html = None
            map_htmls.append(map_html)
        return map_htmls
    
    def add_calendar_info(self, df, calendar):
        for week in calendar:
            for day in week:
                if day[0] != '--':
                    # find all activities where the day part of df['Date'] ( is equal to day
                    df_for_day = df[df['Day'] == day[0]]
                    df_for_day = df_for_day.sort_values('DateTime')
                    for i in range(len(df_for_day)):
                        activity = df_for_day.iloc[i]
                        activity_dict = activity.to_dict()
                        day[1].append(activity_dict)
        return calendar
                    
    def prepare_calendar_info(self, df, calendar):
        cols = df.columns.tolist()
        
        #df['day'] =  integer day part of date ex: '2021-03-01' -> 1, '2021-03-02' -> 2
        df['DateTime'] = df['start_time']
        df['Day'] = df['start_time'].apply(lambda x: int(x.strftime('%d')))
        df['Sport'] = df['sport'].apply(lambda x: x.title())
        df['DisplaySport'] = df[['sport','sub_sport']].apply(lambda x: x['sport'] if x['sport'] in ('running', 'cycling', 'rowing') and x['sub_sport'] in ('generic', None) else x['sub_sport'], axis=1)
        df['DisplaySport'] = df['DisplaySport'].apply(lambda x: x.title().replace('_', ' '))
        df['DisplaySport'] = df['DisplaySport'].apply(lambda x: x.title())
        df['Duration'] = df['total_time'].apply(lambda x: self.time_seconds_to_string(x))
        df['Distance'] = df.apply(lambda row: float(round(row['total_distance']/mile_dist, 3)) if row['sport'] in ('running', 'cycling') else float(row['total_distance']), axis=1)
        df['ActivityTitle'] = df['activity_title'].apply(lambda x: x.title())
        cols.remove('activity_id')
        
        df = df.drop(cols, axis=1)
        calendar = self.add_calendar_info(df, calendar)
        return calendar