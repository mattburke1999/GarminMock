import pandas as pd
import numpy as np
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
        
    def prepare_lap_info(self, df, activity_id_list):
        df['total_time'] = df['total_time'].apply(lambda x: self.time_seconds_to_string(x))
        df['total_elapsed_time'] = df['total_elapsed_time'].apply(lambda x: self.time_seconds_to_string(x))
        df['pace'] = df['pace'].apply(lambda x: self.time_seconds_to_string(x))
        lap_list = [df[df['activity_id'] == activity_id].to_dict('records') for activity_id in activity_id_list]
        return lap_list
    
    def prepare_multiple_activities(self, df):
        df['total_time'] = df['total_time'].apply(lambda x: self.time_seconds_to_string(x))
        df['total_elapsed_time'] = df['total_elapsed_time'].apply(lambda x: self.time_seconds_to_string(x))
        df['pace'] = df.apply(lambda row: self.time_seconds_to_string(row) if row['sport'] in ('running', 'rowing') else row['pace'], axis=1)
        df['elapsed_pace'] = df.apply(lambda row: self.time_seconds_to_string(row) if row['sport'] in ('running', 'rowing') else row['pace'], axis=1)
        df = df.sort_values(by=['start_time'])
        df = df.fillna('--')
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