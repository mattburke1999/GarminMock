import folium
import pandas as pd

mile_dist = 1609.344

class DataTransform:
    
    def time_seconds_to_string(self, seconds):
        if seconds:
            try:
                seconds = int(seconds)
            except ValueError:
                return '--'
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            seconds = seconds % 60
            seconds = round(seconds, 3) if seconds > 9 else f"0{round(seconds,3)}"
            if hours == 0:
                return f'{minutes}:{seconds}'
            else:
                return f'{hours}:{minutes if minutes > 9 else f"0{minutes}"}:{seconds}'
        return '--'
    
    def lap_dfs_to_htmls(self, lap_list):
        lap_html_list = []
        for lap_df in lap_list:
            if lap_df.empty:
                lap_html_list.append(None)
            else:
                lap_df = lap_df.drop(['activity_id'], axis=1)
                lap_html = lap_df.to_html(index=False).replace(' style="text-align: right;"','').replace(' border="1"','')
                for col in lap_df.columns:
                    lap_html = lap_html.replace(f'<th>{col}</th>', f'<th class="colTitle">{col}</th>')
                lap_html_list.append(lap_html)
        return lap_html_list    
    
    def prepare_lap_info(self, df, activity_id_list):
        df = df.rename(columns={'lap_num': 'lap', 'total_distance': 'distance', 'avg_speed': 'avg_speed', 'max_speed': 'max_speed', 'avg_hr': 'avg hr', 
                                'max_hr': 'max hr', 'avg_running_cadence': 'avg cadence', 'max_running_cadence': 'max cadence', 'total_strides': 'steps', 
                                'total_calories': 'calories', 'total_ascent': 'total ascent', 'total_descent': 'total descent', 'avg_stride_length': 'avg stride length',
                                'best_pace': 'best pace'})
        df['duration'] = df['total_time'].apply(lambda x: self.time_seconds_to_string(x))
        df['elapsed time'] = df['total_elapsed_time'].apply(lambda x: self.time_seconds_to_string(x))
        df['pace'] = df['pace'].apply(lambda x: self.time_seconds_to_string(x))
        # select only the columns we want and reorder them
        df = df[['lap', 'distance', 'duration', 'elapsed time', 'pace', 'best pace', 'avg hr', 'max hr', 'avg cadence', 'max cadence', 'steps', 'avg stride length', 'calories', 'total ascent', 'total descent', 'activity_id']]
        lap_list = [df[df['activity_id'] == activity_id] for activity_id in activity_id_list]
        lap_html_list = self.lap_dfs_to_htmls(lap_list)
        return lap_html_list
    
    def prepare_multiple_activities(self, df, desc_order):
        df['total_time'] = df['total_time'].apply(lambda x: self.time_seconds_to_string(x))
        df['total_elapsed_time'] = df['total_elapsed_time'].apply(lambda x: self.time_seconds_to_string(x))
        df['pace'] = df.apply(lambda row: self.time_seconds_to_string(row['pace']) if row['sport'] in ('Running', 'Rowing') else row['pace'], axis=1)
        df['elapsed_pace'] = df.apply(lambda row: self.time_seconds_to_string(row['elapsed_pace']) if row['sport'] in ('Running', 'Rowing') else row['elapsed_pace'], axis=1)
        df = df.sort_values(by=['start_time'], ascending = not desc_order)
        df = df.drop(['start_time'], axis=1)
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
                    df_for_day = df[df['day'] == day[0]]
                    df_for_day = df_for_day.sort_values('start_time')
                    for i in range(len(df_for_day)):
                        activity = df_for_day.iloc[i]
                        activity_dict = activity.to_dict()
                        day[1].append(activity_dict)
        return calendar
                    
    def prepare_calendar_info(self, df, calendar):
        df['day'] = df['start_time'].apply(lambda x: int(x.strftime('%d')))
        df['duration'] = df['total_time'].apply(lambda x: self.time_seconds_to_string(x))
        calendar = self.add_calendar_info(df, calendar)
        return calendar
    
    def merge_records(self, records1, records2):
        # find timedelta between the last record of the first activity and the first record of the second activity
        time_diff = (records2['timestamp'].iloc[0] - records1['timestamp'].iloc[-1])
        # add this timedelta to the second activity to remove the gap
        records2['timestamp'] = records2['timestamp'] - time_diff
        max_dist1 = records1['distance'].iloc[-1]
        # add the max distance of the first activity to the second activity to calculate the total distance
        records2['distance'] = records2['distance'] + max_dist1

        new_records = pd.concat([records1, records2], ignore_index=True)
        return new_records
    
    def calculate_lap_data_from_records(self, records, start_distance, start_time, start_lat, start_long, laps=[]):
        # start_distance = records['distance'].iloc[start_index]
        end_distance = start_distance + mile_dist
        num_full_laps = int(records['distance'].iloc[-1]/mile_dist)
        start_index = records['distance'].sub(start_distance).abs().idxmin()
        if end_distance < records['distance'].iloc[-1] and len(laps) < num_full_laps:
            end_index = records['distance'].sub(end_distance).abs().idxmin()
            dist1 = records['distance'].iloc[end_index-1] - start_distance
            dist2 = records['distance'].iloc[end_index] - start_distance
            time1 = records['timestamp'].iloc[end_index - 1]
            lat1 = records['position_lat'].iloc[end_index - 1]
            long1 = records['position_long'].iloc[end_index - 1]
            time2 = records['timestamp'].iloc[end_index]
            lat2 = records['position_lat'].iloc[end_index]
            long2 = records['position_long'].iloc[end_index]

            # Calculate the exact time at which the distance was exactly 1609.75 meters
            # We use linear interpolation
            mile_time = time1 + (time2 - time1) * (mile_dist - dist1) / (dist2 - dist1)
            
            # Calculate the exact latitude and longitude at which the distance was exactly 1609.75 meters
            calc_lat = lat1 + (lat2 - lat1) * (mile_dist - dist1) / (dist2 - dist1)
            calc_long = long1 + (long2 - long1) * (mile_dist - dist1) / (dist2 - dist1)
            
            # calculate avg heart rate
            avg_hr = records['heart_rate'].iloc[start_index:end_index].mean()
            max_hr = records['heart_rate'].iloc[start_index:end_index].max()
            
            # calculate avg cadence
            avg_cadence = records['cadence'].iloc[start_index:end_index].mean()
            max_cadence = records['cadence'].iloc[start_index:end_index].max()

            # Calculate the total mile time
            mile_duration = mile_time - start_time
            laps.append((mile_duration.total_seconds(), start_time, mile_dist, start_lat, start_long, calc_lat, calc_long, avg_hr, max_hr, avg_cadence, max_cadence))
            return self.calculate_lap_data_from_records(records, end_distance, mile_time, calc_lat, calc_long, laps)
        else:
            # get remainder time
            mile_duration = records['timestamp'].iloc[-1] - start_time
            partial_dist = records['distance'].iloc[-1] - start_distance
            
            avg_hr = records['heart_rate'].iloc[start_index:].mean()
            max_hr = records['heart_rate'].iloc[start_index:].max()
            avg_cadence = records['cadence'].iloc[start_index:].mean()
            max_cadence = records['cadence'].iloc[start_index:].max()
            
            laps.append((mile_duration.total_seconds(), start_time, partial_dist, start_lat, start_long, records['position_lat'].iloc[-1], records['position_long'].iloc[-1], avg_hr, max_hr, avg_cadence, max_cadence))
            return laps
        
    def finalize_lap_data(self, lap_data):
        pass