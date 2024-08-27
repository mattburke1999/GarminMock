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
        df['best pace'] = df['best pace'].apply(lambda x: self.time_seconds_to_string(x))
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
    
    def merge_records(self, records1, records2, new_activity_id):
        # find timedelta between the last record of the first activity and the first record of the second activity
        time_diff = (records2['timestamp'].iloc[0] - records1['timestamp'].iloc[-1])
        # add this timedelta to the second activity to remove the gap
        records2['timestamp'] = records2['timestamp'] - time_diff
        max_dist1 = records1['distance'].iloc[-1]
        # add the max distance of the first activity to the second activity to calculate the total distance
        records2['distance'] = records2['distance'] + max_dist1

        new_records = pd.concat([records1, records2], ignore_index=True)
        new_records['activity_id'] = new_activity_id
        return new_records
    
    def calculate_ascent_descent_for_lap(self, lap):
        ascent = 0
        descent = 0
        for i in range(1, len(lap)):
            diff = lap['enhanced_altitude'].iloc[i] - lap['enhanced_altitude'].iloc[i-1]
            if diff > 0:
                ascent += diff
            else:
                descent += abs(diff)
        return ascent, descent
    
    def calculate_lap_data_from_records(self, records, start_distance, start_time, start_lat, start_long, cs_list, lap_num=0, laps=None):
        if laps is None:
            laps = []
        # start_distance = records['distance'].iloc[start_index]
        end_distance = start_distance + mile_dist
        num_full_laps = records['distance'].iloc[-1]//mile_dist
        start_index = records['distance'].sub(start_distance).abs().idxmin()
        if end_distance < records['distance'].iloc[-1] and len(laps) < num_full_laps:
            end_index = records['distance'].sub(end_distance).abs().idxmin()
            
            this_lap = records.iloc[start_index:end_index]
            
            dist1 = this_lap['distance'].iloc[-2] - start_distance
            dist2 = this_lap['distance'].iloc[-1] - start_distance
            time1 = this_lap['timestamp'].iloc[-2]
            lat1 = this_lap['position_lat'].iloc[-2]
            long1 = this_lap['position_long'].iloc[-2]
            time2 = this_lap['timestamp'].iloc[-1]
            lat2 = this_lap['position_lat'].iloc[-1]
            long2 = this_lap['position_long'].iloc[-1]

            # We use linear interpolation
            mile_time = time1 + (time2 - time1) * (mile_dist - dist1) / (dist2 - dist1)
            
            # Calculate the exact latitude and longitude at which the distance was exactly 1609.75 meters
            calc_lat = lat1 + (lat2 - lat1) * (mile_dist - dist1) / (dist2 - dist1)
            calc_long = long1 + (long2 - long1) * (mile_dist - dist1) / (dist2 - dist1)
            
            # calculate avg heart rate
            avg_hr = this_lap['heart_rate'].mean()
            max_hr = this_lap['heart_rate'].max()
            
            # calculate avg cadence
            avg_cadence = this_lap['cadence'].mean()
            max_cadence = this_lap['cadence'].max()
            
            # calculate max speed
            max_speed = this_lap['enhanced_speed'].max()
            
            ascent, descent = self.calculate_ascent_descent_for_lap(this_lap)

            # Calculate the total mile time
            mile_duration = mile_time - start_time
            laps.append((mile_duration.total_seconds(), start_time, mile_dist, start_lat, start_long, calc_lat, calc_long, avg_hr, max_hr, cs_list[lap_num][0], cs_list[lap_num][1], avg_cadence, max_cadence, max_speed, ascent, descent, lap_num))
            return self.calculate_lap_data_from_records(records, end_distance, mile_time, calc_lat, calc_long, cs_list, lap_num+1, laps)
        else:
            this_lap = records.iloc[start_index:]
            # get remainder time
            mile_duration = this_lap['timestamp'].iloc[-1] - start_time
            partial_dist = this_lap['distance'].iloc[-1] - start_distance
            
            avg_hr = this_lap['heart_rate'].mean()
            max_hr = this_lap['heart_rate'].max()
            avg_cadence = this_lap['cadence'].mean()
            max_cadence = this_lap['cadence'].max()
            max_speed = this_lap['enhanced_speed'].max()
            
            ascent, descent = self.calculate_ascent_descent_for_lap(this_lap)
            
            laps.append((mile_duration.total_seconds(), start_time, partial_dist, start_lat, start_long, this_lap['position_lat'].iloc[-1], this_lap['position_long'].iloc[-1], avg_hr, max_hr, cs_list[lap_num][0], cs_list[lap_num][1], avg_cadence, max_cadence, max_speed, ascent, descent, lap_num))
            return laps
    
    def get_calories_strides_list(self, prev_distance, prev_calories, prev_strides, remaining_laps, cs_list=None):
        if cs_list is None:
            cs_list = []
        if len(remaining_laps) == 0:
            return cs_list
        dist0 = float(remaining_laps[0][0])
        cal0 = float(remaining_laps[0][1])
        stride0 = float(remaining_laps[0][2])
        if (dist0 + prev_distance) < mile_dist:
            if len(remaining_laps) > 1:
                return self.get_calories_strides_list(dist0+prev_distance, cal0+prev_calories, stride0+prev_calories, remaining_laps[1:], cs_list)
            cs_list.append((cal0+prev_calories, stride0+prev_strides))
            return cs_list
        elif (dist0 + prev_distance) > mile_dist:
            dist_remain = mile_dist - prev_distance
            cals_to_add = (dist_remain / dist0)*cal0
            strides_to_add = (dist_remain / dist0)*stride0
            cs_list.append((cals_to_add+prev_calories, strides_to_add+prev_strides))
            remaining_laps[0] = (dist0-dist_remain, cal0-cals_to_add, stride0-strides_to_add)
            return self.get_calories_strides_list(0, 0, 0, remaining_laps, cs_list)
        else:
            cs_list.append((cal0+prev_calories, stride0+prev_strides))
            return self.get_calories_strides_list(0, 0, 0, remaining_laps[1:], cs_list)
    
    def records_to_laps(self, new_record, session_data, lap1, lap2, new_activity_id):
        lap1c = lap1[['total_distance', 'total_calories', 'total_strides']]
        lap2c = lap2[['total_distance', 'total_calories', 'total_strides']]
        lapc = pd.concat([lap1c, lap2c], ignore_index=True)
        lap_t = [tuple(x) for x in lapc.to_numpy()]
        calories_strides = self.get_calories_strides_list(0, 0, 0, lap_t)
        lap_data = self.calculate_lap_data_from_records(new_record, new_record['distance'].iloc[0], new_record['timestamp'].iloc[0], new_record['position_lat'].iloc[0], new_record['position_long'].iloc[0], calories_strides)
        columns = ['total_timer_time', 'start_time', 'total_distance', 'start_position_lat', 'start_position_long', 'end_position_lat', 'end_position_long', 'avg_heart_rate', 'max_heart_rate', 'total_calories', 'total_strides', 'avg_running_cadence', 'max_running_cadence', 'enhanced_max_speed', 'total_ascent', 'total_descent','message_index']
        lap_df = pd.DataFrame(lap_data, columns=columns)
        lap_df['activity_id'] = new_activity_id
        lap_df['accountid'] = session_data['accountid'].iloc[0]
        lap_df['timestamp'] = lap_df['start_time'] + pd.to_timedelta(lap_df['total_timer_time'], unit='s')
        lap_df['total_elapsed_time'] = lap_df['total_timer_time']
        lap_df['sport'] = session_data['sport'].iloc[0]
        lap_df['sub_sport'] = session_data['sub_sport'].iloc[0]
        for col in lap1.columns:
            if col not in lap_df.columns:
                lap_df[col] = None
        return lap_df
    
    def adjust_lap_columns(self, df):
        for col in df.columns:
            if col not in ('start_time', 'timestamp'):
                df[col] = df[col].apply(lambda x: str(x) if pd.notnull(x) else None)
        return df
    
    def laps_to_session(self, new_laps, new_records, session1, session2, new_activity_id, new_temp_id):
        new_session = {}
        new_session['activity_id'] = new_activity_id
        new_session['start_time'] = session1['start_time'].iloc[0]
        new_session['timestamp'] = session2['timestamp'].iloc[0]
        new_session['sport'] = session1['sport'].iloc[0]
        new_session['sub_sport'] = session1['sub_sport'].iloc[0]
        new_session['total_timer_time'] = str(float(session1['total_timer_time'].iloc[0] or 0) + float(session2['total_timer_time'].iloc[0] or 0))
        new_session['total_elapsed_time'] = str(float(session1['total_elapsed_time'].iloc[0] or 0) + float(session2['total_elapsed_time'].iloc[0] or 0))
        new_session['total_distance'] = str(float(session1['total_distance'].iloc[0] or 0) + float(session2['total_distance'].iloc[0] or 0))
        new_session['total_cycles'] = str(float(session1['total_cycles'].iloc[0] or 0) + float(session2['total_cycles'].iloc[0] or 0))
        new_session['total_calories'] = str(float(session1['total_calories'].iloc[0] or 0) + float(session2['total_calories'].iloc[0] or 0))
        new_session['start_position_lat'] = session1['start_position_lat'].iloc[0]
        new_session['start_position_long'] = session1['start_position_long'].iloc[0]
        new_session['message_index'] = '0'
        new_session['first_lap_index'] = '0'
        new_session['num_laps'] = str(len(new_laps))
        new_session['event'] = 'lap'
        new_session['event_type'] = 'stop'
        new_session['avg_heart_rate'] = str(new_records['heart_rate'].mean())
        new_session['max_heart_rate'] = str(new_records['heart_rate'].max())
        new_session['avg_running_cadence'] = str(new_records['cadence'].mean())
        new_session['max_running_cadence'] = str(new_records['cadence'].max())
        new_session['trigger'] = 'activity_end'
        new_session['total_strides'] = str(float(session1['total_strides'].iloc[0] or 0) + float(session2['total_strides'].iloc[0] or 0))
        new_session['total_ascent'] = str(new_laps['total_ascent'].sum())
        new_session['total_descent'] = str(new_laps['total_descent'].sum())
        new_session['unknown_196'] = str(float(session1['unknown_196'].iloc[0] or 0) + float(session2['unknown_196'].iloc[0] or 0)) # resting calories
        new_session['unknown_178'] = str(float(session1['unknown_178'].iloc[0] or 0) + float(session2['unknown_178'].iloc[0] or 0)) # sweat loss
        new_session['unknown_184'] = '0'
        new_session['temp_id'] = str(new_temp_id)
        new_session['activity_title'] = session1['activity_title'].iloc[0]
        new_session['description'] = session1['description'].iloc[0]
        new_session['accountid'] = session1['accountid'].iloc[0]
        new_session['is_visible'] = True
        new_session['is_merged'] = True
        session_df = pd.DataFrame([new_session], index=[0])
        for cols in session1.columns:
            if cols not in session_df.columns:
                if cols in ('description', 'activity_title'):
                    session_df[cols] = ''
                else:
                    session_df[cols] = None
        return session_df