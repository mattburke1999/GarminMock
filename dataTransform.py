import pandas as pd
import folium

mile_dist = 1609.344

class DataTransform:
    
    def time_seconds_to_string(self, seconds):
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        seconds = seconds % 60
        if hours == 0:
            return f'{minutes} min {round(seconds,3)} sec'
        elif hours == 1:
            return f'{hours} hr {minutes} min {round(seconds,3)} sec'
        else:
            return f'{hours} hrs {minutes} min {round(seconds,3)} sec'

    def prepare_running(self, activity, activity_dict):
        distance = activity['total_distance']
        activity_dict['Distance'] = float(round(distance/mile_dist, 3))
        pace = activity['total_time'] / (distance/mile_dist)
        activity_dict['Pace'] = self.time_seconds_to_string(pace)
        elapsed_pace = activity['total_elapsed_time'] / (distance/mile_dist)
        activity_dict['Elapsed Pace'] = self.time_seconds_to_string(elapsed_pace)
        activity_dict['Avg Cadence'] = int(activity['avg_running_cadence'])
        activity_dict['Max Cadence'] = int(activity['max_running_cadence'])
        activity_dict['Steps'] = int(activity['total_strides'])
        stride_length = activity['total_distance'] / activity['total_strides']
        activity_dict['Avg Stride Length'] = round(stride_length, 2)
        return activity_dict

    def prepare_cycling(self, activity, activity_dict):
        distance = activity['total_distance']
        activity_dict['Distance'] = float(round(distance/mile_dist, 3))
        total_time = activity['total_time']
        total_elapsed_time = activity['total_elapsed_time']
        speed = (distance / mile_dist) / (total_time / 3600)
        elapsed_speed = (distance / mile_dist) / (total_elapsed_time / 3600)
        activity_dict['Speed'] = float(round(speed, 2))
        activity_dict['Elapsed Speed'] = float(round(elapsed_speed, 2))
        return activity_dict

    def prepare_rowing(self, activity, activity_dict):
        activity_dict['Distance'] = float(activity['total_distance'])
        #calculate pace min:sec/500m
        total_time = activity['total_time']
        elapsed_time = activity['total_elapsed_time']
        distance = activity['total_distance']
        pace = (total_time) / (distance / 500) if distance != 0 else 0
        elapsed_pace = (elapsed_time) / (distance / 500) if distance != 0 else 0
        activity_dict['Pace'] = self.time_seconds_to_string(pace)
        activity_dict['Elapsed Pace'] = self.time_seconds_to_string(elapsed_pace)
        total_cycles = activity['total_cycles']
        activity_dict['Total Strokes'] = int(total_cycles)
        total_time = activity['total_time']
        activity_dict['Stroke Rate'] = float(round((total_cycles / (total_time / 60)),2))
        elapsed_time = activity['total_elapsed_time']
        activity_dict['Elapsed Stroke Rate'] = float(round((total_cycles / (elapsed_time / 60)),2))
        return activity_dict

    def lap_dfs_to_htmls(self, lap_df):
        lap_html_list = []
        for activity_id in lap_df['activity_id'].unique():
            lap = lap_df[lap_df['activity_id'] == activity_id]
            if len(lap) == 0:
                lap_html_list.append(None)
            else:
                lap = lap.drop('activity_id', axis=1)
                lap_html = lap.to_html(index=False).replace(' style="text-align: right;"','').replace(' border="1"','')
                for col in lap.columns:
                    lap_html = lap_html.replace(f'<th>{col}</th>', f'<th class="colTitle">{col}</th>')
                lap_html_list.append(lap_html)
        if len(lap_html_list) == 0:
            return [None]
        else:
            return lap_html_list

    def time_seconds_to_string_lap(self, seconds):
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        seconds = seconds % 60
        if hours == 0:
            if seconds < 10:
                return f'{minutes}:0{round(seconds,3)}'
            return f'{minutes}:{round(seconds,3)}'
        else:
            if seconds < 10:
                return f'{hours}:{minutes}:0{round(seconds,3)}'
            return f'{hours}:{minutes}:{round(seconds,3)}'

    def prepare_lap_info(self, df, activity_id_list):
        # drop all rows where df['activity_id'] is not in activity_id_list
        df = df[df['activity_id'].isin(activity_id_list)]
        
        cols = df.columns.tolist()
        df['lap'] = df['lap_num']
        df['distance'] = df['total_distance'].apply(lambda x: round(x/mile_dist, 2))
        df['duration'] = df['total_time'].apply(lambda x: self.time_seconds_to_string_lap(x))
        df['elapsed time'] = df['total_elapsed_time'].apply(lambda x: self.time_seconds_to_string_lap(x))
        df['avg_speed'] = df['avg_speed'].apply(lambda x: round(mile_dist/(60*x), 2) if x > 0 else 0)
        df['pace_calc'] = df.apply(lambda row: row['total_time'] / (row['total_distance'] / mile_dist) if row['total_distance'] != 0 else 0, axis=1)    # set df['pace'] = df['avg_speed'] if avg_speed > 0 else pace_calc
        df['pace'] = df.apply(lambda row: row['avg_speed'] if row['avg_speed'] > 0 else row['pace_calc'], axis=1)
        df['pace'] = df['pace'].apply(lambda x: self.time_seconds_to_string_lap(x))
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
        html_list = self.lap_dfs_to_htmls(df)
        return html_list

    def prepare_multiple_activities(self, df):
        activity_list = []
        df = df.sort_values(by=['start_time'])
        for i in range(len(df)):
            activity_dict = {}
            activity = df.iloc[i]
            activity_dict['Activity Title'] = activity['activity_title'].title()
            activity_dict['Description'] = activity['description']
            activity_dict['activity_id'] = activity['activity_id']
            start_time = activity['start_time']
            date_part = start_time.strftime('%A, %B %d')
            time_part = start_time.strftime('%I:%M %p')
            activity_dict['date_edit'] = start_time.strftime('%Y-%m-%d')
            activity_dict['time_edit'] = start_time.strftime('%H:%M')
            if time_part[0] == '0':
                time_part = time_part[1:]
            activity_dict['Date'] = f'{date_part} @ {time_part}'
            sport = activity['sport']
            capitalSport = sport.title()        
            activity_dict['Sport'] = capitalSport
            sub_sport = activity['sub_sport']
            display_sport = sport if sport in ('running', 'cycling', 'rowing') and sub_sport == 'generic' else sub_sport
            display_sport = f'{display_sport.title()}'.replace('_', ' ')
            #capitalize all first letters of each word in display_sport
            display_sport_capital = display_sport.title()
            activity_dict['DisplaySport'] = display_sport_capital
            total_time = self.time_seconds_to_string(activity['total_time'])
            activity_dict['Duration'] = total_time
            elapsed_time = self.time_seconds_to_string(activity['total_elapsed_time'])
            activity_dict['Elapsed Time'] = elapsed_time
            activity_dict['Avg HR'] = int(activity['avg_hr'])
            activity_dict['Max HR'] = int(activity['max_hr'])
            activity_dict['Recovery HR'] = int(activity['recovery_hr'])
            activity_dict['Resting Calories'] = int(activity['resting_calories'])
            activity_dict['Total Calories'] = int(activity['total_calories'])
            activity_dict['Active Calories'] = int(activity['total_calories'] - activity['resting_calories'])
            activity_dict['Sweat Loss'] = int(activity['sweat_loss'])
            total_descent = activity['total_descent']
            activity_dict['Total Descent'] = round(float(total_descent * 3.28084), 3)
            total_ascent = activity['total_ascent']
            activity_dict['Total Ascent'] = round(float(total_ascent * 3.28084), 3)
            if sport == 'running':
                activity_dict = self.prepare_running(activity, activity_dict)
            elif sport == 'cycling':
                activity_dict = self.prepare_cycling(activity, activity_dict)
            elif sport == 'rowing':
                activity_dict = self.prepare_rowing(activity, activity_dict)
            activity_list.append(activity_dict)
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
        for activity_id in record_info['activity_id'].unique():
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
        df['DisplaySport'] = df[['sport','sub_sport']].apply(lambda x: x['sport'] if x['sport'] in ('running', 'cycling', 'rowing') and x['sub_sport'] == 'generic' else x['sub_sport'], axis=1)
        df['DisplaySport'] = df['DisplaySport'].apply(lambda x: x.title().replace('_', ' '))
        df['DisplaySport'] = df['DisplaySport'].apply(lambda x: x.title())
        df['Duration'] = df['total_time'].apply(lambda x: self.time_seconds_to_string(x))
        df['Distance'] = df.apply(lambda row: float(round(row['total_distance']/mile_dist, 3)) if row['sport'] in ('running', 'cycling') else float(row['total_distance']), axis=1)
        df['ActivityTitle'] = df['activity_title'].apply(lambda x: x.title())
        cols.remove('activity_id')
        
        df = df.drop(cols, axis=1)
        calendar = self.add_calendar_info(df, calendar)
        return calendar