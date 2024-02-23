
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
        activity_ids = lap_df['activity_id'].unique()
        lap_html_list = []
        for activity_id in activity_ids:
            lap = lap_df[lap_df['activity_id'] == activity_id]
            if len(lap) == 0:
                lap_html_list.append(None)
            else:
                lap = lap.drop('activity_id', axis=1)
                lap_html = lap.to_html(index=False).replace(' style="text-align: right;"','').replace(' border="1"','')
                for col in lap.columns:
                    lap_html = lap_html.replace(f'<th>{col}</th>', f'<th class="colTitle">{col}</th>')
                lap_html_list.append(lap_html)
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

    def prepare_lap_info(self, df):
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