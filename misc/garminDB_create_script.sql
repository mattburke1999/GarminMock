-- THIS IS A FULL DB CREATE SCRIPT FOR GARMINMOCK (python version)

-- 1. Tables ====================================================================
-- 1a. Optional Tables
-- these first 3 tables are for enabling a backlog
-- not necessary, if not enabling a backlog in the DB
CREATE TABLE IF NOT EXISTS public.backlog_categories
(
    id integer NOT NULL DEFAULT nextval('backlog_categories_id_seq'::regclass),
    name text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT backlog_categories_pkey PRIMARY KEY (id),
    CONSTRAINT backlog_categories_name_key UNIQUE (name)
);

CREATE TABLE IF NOT EXISTS public.backlog_groups
(
    id integer NOT NULL DEFAULT nextval('backlog_groups_id_seq'::regclass),
    name text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT backlog_groups_pkey PRIMARY KEY (id),
    CONSTRAINT backlog_groups_name_key UNIQUE (name)
);

CREATE TABLE IF NOT EXISTS public.backlog
(
    id serial,
    code_area text COLLATE pg_catalog."default" NOT NULL,
    files text COLLATE pg_catalog."default",
    description text COLLATE pg_catalog."default" NOT NULL,
    category_id integer NOT NULL,
    group_id integer,
    created_time timestamp without time zone NOT NULL,
    started_time timestamp without time zone,
    completed_time timestamp without time zone,
    CONSTRAINT backlog_pkey PRIMARY KEY (id),
    CONSTRAINT backlog_category_id_fkey FOREIGN KEY (category_id)
        REFERENCES public.backlog_categories (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT backlog_group_fkey FOREIGN KEY (group_id)
        REFERENCES public.backlog_groups (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE SET NULL
);

-- 1b. Required Tables

CREATE TABLE IF NOT EXISTS public.accounts
(
    firstname text COLLATE pg_catalog."default",
    lastname text COLLATE pg_catalog."default",
    userid text COLLATE pg_catalog."default",
    password bytea,
    creationdate timestamp without time zone,
    id serial NOT NULL,
    CONSTRAINT accounts_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.raw_garmin_data_session
(
    activity_id text COLLATE pg_catalog."default" NOT NULL,
    start_time timestamp with time zone,
    "timestamp" timestamp with time zone,
    sport text COLLATE pg_catalog."default",
    sub_sport text COLLATE pg_catalog."default",
    total_timer_time text COLLATE pg_catalog."default",
    total_elapsed_time text COLLATE pg_catalog."default",
    total_distance text COLLATE pg_catalog."default",
    total_cycles text COLLATE pg_catalog."default",
    total_calories text COLLATE pg_catalog."default",
    start_position_lat text COLLATE pg_catalog."default",
    start_position_long text COLLATE pg_catalog."default",
    message_index text COLLATE pg_catalog."default",
    enhanced_avg_speed text COLLATE pg_catalog."default",
    avg_speed text COLLATE pg_catalog."default",
    first_lap_index text COLLATE pg_catalog."default",
    num_laps text COLLATE pg_catalog."default",
    event text COLLATE pg_catalog."default",
    event_type text COLLATE pg_catalog."default",
    avg_heart_rate text COLLATE pg_catalog."default",
    max_heart_rate text COLLATE pg_catalog."default",
    avg_running_cadence text COLLATE pg_catalog."default",
    max_running_cadence text COLLATE pg_catalog."default",
    trigger text COLLATE pg_catalog."default",
    total_strides text COLLATE pg_catalog."default",
    total_moving_time text COLLATE pg_catalog."default",
    avg_pos_vertical_speed text COLLATE pg_catalog."default",
    unknown_33 text COLLATE pg_catalog."default",
    num_active_lengths text COLLATE pg_catalog."default",
    unknown_142 text COLLATE pg_catalog."default",
    unknown_157 text COLLATE pg_catalog."default",
    unknown_158 text COLLATE pg_catalog."default",
    avg_cadence text COLLATE pg_catalog."default",
    max_cadence text COLLATE pg_catalog."default",
    nec_lat text COLLATE pg_catalog."default",
    nec_long text COLLATE pg_catalog."default",
    swc_lat text COLLATE pg_catalog."default",
    swc_long text COLLATE pg_catalog."default",
    unknown_110 text COLLATE pg_catalog."default",
    enhanced_max_speed text COLLATE pg_catalog."default",
    max_speed text COLLATE pg_catalog."default",
    total_ascent text COLLATE pg_catalog."default",
    total_descent text COLLATE pg_catalog."default",
    total_training_effect text COLLATE pg_catalog."default",
    unknown_81 text COLLATE pg_catalog."default",
    avg_fractional_cadence text COLLATE pg_catalog."default",
    max_fractional_cadence text COLLATE pg_catalog."default",
    unknown_38 text COLLATE pg_catalog."default",
    unknown_39 text COLLATE pg_catalog."default",
    unknown_152 text COLLATE pg_catalog."default",
    unknown_151 text COLLATE pg_catalog."default",
    unknown_196 text COLLATE pg_catalog."default",
    unknown_178 text COLLATE pg_catalog."default",
    unknown_184 text COLLATE pg_catalog."default",
    unknown_202 text COLLATE pg_catalog."default",
    temp_id integer,
    activity_title text COLLATE pg_catalog."default",
    description text COLLATE pg_catalog."default",
    accountid integer,
    is_visible boolean DEFAULT true,
    is_merged boolean DEFAULT false,
    CONSTRAINT activity_id_pk PRIMARY KEY (activity_id),
    CONSTRAINT raw_garmin_data_session_accountid_fkey FOREIGN KEY (accountid)
        REFERENCES public.accounts (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);

CREATE TABLE IF NOT EXISTS public.merged_activities
(
    id integer NOT NULL DEFAULT nextval('merged_activities_id_seq'::regclass),
    merged_activity_id text COLLATE pg_catalog."default",
    activity1_id text COLLATE pg_catalog."default",
    activity2_id text COLLATE pg_catalog."default",
    merge_date timestamp with time zone,
    CONSTRAINT merged_activities_pkey PRIMARY KEY (id),
    CONSTRAINT merged_activities_activity1_id_fkey FOREIGN KEY (activity1_id)
        REFERENCES public.raw_garmin_data_session (activity_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT merged_activities_activity2_id_fkey FOREIGN KEY (activity2_id)
        REFERENCES public.raw_garmin_data_session (activity_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT merged_activities_merged_activity_id_fkey FOREIGN KEY (merged_activity_id)
        REFERENCES public.raw_garmin_data_session (activity_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);

CREATE TABLE IF NOT EXISTS public.raw_garmin_data_laps
(
    "timestamp" timestamp with time zone,
    start_time timestamp with time zone,
    start_position_lat text COLLATE pg_catalog."default",
    start_position_long text COLLATE pg_catalog."default",
    end_position_lat text COLLATE pg_catalog."default",
    end_position_long text COLLATE pg_catalog."default",
    total_elapsed_time text COLLATE pg_catalog."default",
    total_timer_time text COLLATE pg_catalog."default",
    total_distance text COLLATE pg_catalog."default",
    message_index text COLLATE pg_catalog."default",
    total_calories text COLLATE pg_catalog."default",
    enhanced_avg_speed text COLLATE pg_catalog."default",
    avg_speed text COLLATE pg_catalog."default",
    event text COLLATE pg_catalog."default",
    event_type text COLLATE pg_catalog."default",
    avg_heart_rate text COLLATE pg_catalog."default",
    max_heart_rate text COLLATE pg_catalog."default",
    avg_running_cadence text COLLATE pg_catalog."default",
    max_running_cadence text COLLATE pg_catalog."default",
    lap_trigger text COLLATE pg_catalog."default",
    sport text COLLATE pg_catalog."default",
    activity_id text COLLATE pg_catalog."default",
    total_strides text COLLATE pg_catalog."default",
    total_moving_time text COLLATE pg_catalog."default",
    avg_pos_vertical_speed text COLLATE pg_catalog."default",
    num_active_lengths text COLLATE pg_catalog."default",
    unknown_125 text COLLATE pg_catalog."default",
    unknown_126 text COLLATE pg_catalog."default",
    total_cycles text COLLATE pg_catalog."default",
    avg_cadence text COLLATE pg_catalog."default",
    max_cadence text COLLATE pg_catalog."default",
    unknown_27 text COLLATE pg_catalog."default",
    unknown_28 text COLLATE pg_catalog."default",
    unknown_29 text COLLATE pg_catalog."default",
    unknown_30 text COLLATE pg_catalog."default",
    enhanced_max_speed text COLLATE pg_catalog."default",
    max_speed text COLLATE pg_catalog."default",
    total_ascent text COLLATE pg_catalog."default",
    total_descent text COLLATE pg_catalog."default",
    wkt_step_index text COLLATE pg_catalog."default",
    sub_sport text COLLATE pg_catalog."default",
    avg_fractional_cadence text COLLATE pg_catalog."default",
    max_fractional_cadence text COLLATE pg_catalog."default",
    unknown_155 text COLLATE pg_catalog."default",
    unknown_145 text COLLATE pg_catalog."default",
    accountid integer,
    CONSTRAINT fk_laps_session_activity_id FOREIGN KEY (activity_id)
        REFERENCES public.raw_garmin_data_session (activity_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT raw_garmin_data_laps_accountid_fkey FOREIGN KEY (accountid)
        REFERENCES public.accounts (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);

CREATE TABLE IF NOT EXISTS public.raw_garmin_data_records
(
    "timestamp" timestamp with time zone,
    position_lat double precision,
    position_long double precision,
    distance double precision,
    enhanced_speed double precision,
    enhanced_altitude double precision,
    heart_rate double precision,
    cadence double precision,
    activity_id text COLLATE pg_catalog."default",
    accountid integer,
    CONSTRAINT fk_records_session_activity_id FOREIGN KEY (activity_id)
        REFERENCES public.raw_garmin_data_session (activity_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT raw_garmin_data_records_accountid_fkey FOREIGN KEY (accountid)
        REFERENCES public.accounts (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);

-- 2. Views ======================================================================

CREATE OR REPLACE VIEW public.session_view
 AS
 SELECT accountid,
    activity_id,
    COALESCE(start_time, '1980-01-01 00:00:00-06'::timestamp with time zone) AS start_time,
    COALESCE(replace(replace(to_char(start_time, 'FMDay, FMMonth DD YYYY FMHH12:MI AM'::text), ' 0'::text, ' '::text), to_char(CURRENT_DATE::timestamp with time zone, 'YYYY'::text), ''::text), 'Tuesday, January 1 1980 12:00 AM'::text) AS display_date,
    initcap(sport) AS sport,
    initcap(replace(
        CASE
            WHEN (sport = ANY (ARRAY['running'::text, 'cycling'::text, 'rowing'::text])) AND COALESCE(sub_sport, 'generic'::text) = 'generic'::text THEN sport
            ELSE sub_sport
        END, '_'::text, ' '::text)) AS display_sport,
    COALESCE(total_timer_time::double precision, 0::double precision) AS total_time,
    COALESCE(total_elapsed_time::double precision, 0::double precision) AS total_elapsed_time,
    COALESCE(round(
        CASE
            WHEN sport = ANY (ARRAY['running'::text, 'cycling'::text]) THEN total_distance::numeric / 1609.344
            ELSE total_distance::numeric
        END, 3), 0::numeric) AS total_distance,
        CASE
            WHEN sport = 'running'::text AND total_distance::numeric > 0::numeric THEN round(total_timer_time::numeric / (total_distance::numeric / 1609.344), 3)
            WHEN sport = 'cycling'::text AND total_distance::numeric > 0::numeric THEN round(total_distance::numeric / 1609.344 / (total_timer_time::numeric / 3600::numeric), 3)
            WHEN sport = 'rowing'::text AND total_distance::numeric > 0::numeric THEN round(total_timer_time::numeric / (total_distance::numeric / 500::numeric), 3)
            ELSE NULL::numeric
        END AS pace,
        CASE
            WHEN sport = 'running'::text AND total_distance::numeric > 0::numeric THEN round(total_elapsed_time::numeric / (total_distance::numeric / 1609.344), 3)
            WHEN sport = 'cycling'::text AND total_distance::numeric > 0::numeric THEN round(total_distance::numeric / 1609.344 / (total_elapsed_time::numeric / 3600::numeric), 3)
            WHEN sport = 'rowing'::text AND total_distance::numeric > 0::numeric THEN round(total_elapsed_time::numeric / (total_distance::numeric / 500::numeric), 3)
            ELSE NULL::numeric
        END AS elapsed_pace,
    COALESCE(avg_heart_rate::double precision::integer, 0) AS avg_hr,
    COALESCE(max_heart_rate::double precision::integer, 0) AS max_hr,
    COALESCE(unknown_202::double precision::integer, 0) AS recovery_hr,
    2 * COALESCE(avg_running_cadence::double precision::integer, 0) AS avg_running_cadence,
    2 * COALESCE(max_running_cadence::double precision::integer, 0) AS max_running_cadence,
    COALESCE(total_strides::double precision::integer, 0) AS total_strides,
        CASE
            WHEN total_strides::numeric > 0::numeric THEN round(total_distance::numeric / total_strides::numeric, 2)
            ELSE NULL::numeric
        END AS avg_stride_length,
        CASE
            WHEN total_timer_time::numeric > 0::numeric THEN round(total_cycles::numeric / (total_timer_time::numeric / 60::numeric), 3)
            ELSE NULL::numeric
        END AS stroke_rate,
        CASE
            WHEN total_elapsed_time::numeric > 0::numeric THEN round(total_cycles::numeric / (total_elapsed_time::numeric / 60::numeric), 3)
            ELSE NULL::numeric
        END AS elapsed_stroke_rate,
    COALESCE(unknown_196::double precision::integer, 0) AS resting_calories,
    COALESCE(total_calories::double precision::integer, 0) AS total_calories,
    COALESCE((total_calories::double precision - unknown_196::double precision)::integer, 0) AS active_calories,
    COALESCE(unknown_178::double precision::integer, 0) AS sweat_loss,
    COALESCE(round(3.28084 * total_descent::numeric, 3), 0::numeric) AS total_descent,
    COALESCE(round(3.28084 * total_ascent::numeric, 3), 0::numeric) AS total_ascent,
    COALESCE(total_cycles::double precision::integer, 0) AS total_cycles,
        CASE
            WHEN activity_title = ''::text THEN initcap(sport || ' activity'::text)
            ELSE activity_title
        END AS activity_title,
    description,
    is_visible,
    is_merged
   FROM raw_garmin_data_session rgd
;

CREATE OR REPLACE VIEW public.lap_view
 AS
 SELECT accountid,
    activity_id,
    COALESCE(start_time, '1980-01-01 00:00:00-06'::timestamp with time zone) AS start_time,
    COALESCE(sport, ''::text) AS sport,
    COALESCE(NULLIF(total_timer_time, ''::text)::double precision, 0::double precision) AS total_time,
    COALESCE(NULLIF(total_elapsed_time, ''::text)::double precision, 0::double precision) AS total_elapsed_time,
    COALESCE(round(NULLIF(total_distance, ''::text)::numeric / 1609.344, 3), 0::numeric) AS total_distance,
    COALESCE(NULLIF(message_index, ''::text)::double precision::integer + 1, 1) AS lap_num,
    COALESCE(NULLIF(total_calories, ''::text)::double precision::integer, 0) AS total_calories,
    round(COALESCE(NULLIF(
        CASE
            WHEN COALESCE(COALESCE(NULLIF(avg_speed, ''::text)::double precision, NULLIF(enhanced_avg_speed, ''::text)::double precision), 0::double precision) > 0::double precision THEN 1609.344 / COALESCE(NULLIF(avg_speed, ''::text)::numeric, NULLIF(enhanced_avg_speed, ''::text)::numeric)
            ELSE NULL::numeric
        END, 0::numeric),
        CASE
            WHEN NULLIF(total_distance, ''::text)::numeric > 0::numeric THEN total_timer_time::numeric / (total_distance::numeric / 1609.344)
            ELSE 0::numeric
        END), 2) AS pace,
    COALESCE(NULLIF(avg_heart_rate, ''::text)::double precision::integer, 0) AS avg_hr,
    COALESCE(NULLIF(max_heart_rate, ''::text)::double precision::integer, 0) AS max_hr,
    2 * COALESCE(NULLIF(avg_running_cadence, ''::text)::double precision::integer, 0) AS avg_running_cadence,
    2 * COALESCE(NULLIF(max_running_cadence, ''::text)::double precision::integer, 0) AS max_running_cadence,
    COALESCE(NULLIF(total_strides, ''::text)::double precision::integer, 0) AS total_strides,
    round(
        CASE
            WHEN COALESCE(NULLIF(total_strides, ''::text)::double precision::integer, 0) > 0 THEN NULLIF(total_distance, ''::text)::numeric / COALESCE(NULLIF(total_strides, ''::text)::numeric, 0::numeric)
            ELSE 0::numeric
        END, 2) AS avg_stride_length,
    COALESCE(NULLIF(total_moving_time, ''::text)::double precision::integer, 0) AS total_moving_time,
    COALESCE(NULLIF(total_cycles, ''::text)::double precision, 0::double precision) AS total_cycles,
    COALESCE(NULLIF(avg_cadence, ''::text)::double precision::integer, 0) AS avg_cadence,
    COALESCE(NULLIF(max_cadence, ''::text)::double precision::integer, 0) AS max_cadence,
    round(
        CASE
            WHEN COALESCE(COALESCE(NULLIF(max_speed, ''::text)::double precision, NULLIF(enhanced_max_speed, ''::text)::double precision), 0::double precision) > 0::double precision THEN NULLIF(total_distance, ''::text)::numeric / COALESCE(COALESCE(NULLIF(max_speed, ''::text)::numeric, NULLIF(enhanced_max_speed, ''::text)::numeric), 0::numeric)
            ELSE 0::numeric
        END, 2) AS best_pace,
    COALESCE(NULLIF(total_ascent, ''::text)::double precision::integer, 0) AS total_ascent,
    COALESCE(NULLIF(total_descent, ''::text)::double precision::integer, 0) AS total_descent
   FROM raw_garmin_data_laps rgd
;

CREATE OR REPLACE VIEW public.record_view
 AS
 SELECT accountid,
    activity_id,
    "timestamp",
        CASE
            WHEN position_lat = '-1'::integer::double precision THEN - 1::double precision
            ELSE position_lat * (180::double precision / (2::double precision ^ 31::double precision))
        END AS latitude,
        CASE
            WHEN position_long = '-1'::integer::double precision THEN - 1::double precision
            ELSE position_long * (180::double precision / (2::double precision ^ 31::double precision))
        END AS longitude,
    COALESCE(distance, 0::double precision) AS distance,
    COALESCE(enhanced_speed, 0::double precision) AS speed,
    COALESCE(enhanced_altitude, 0::double precision) AS altitude,
    COALESCE(heart_rate, 0::double precision) AS hr,
    COALESCE(cadence, 0::double precision) AS cadence
   FROM raw_garmin_data_records
;

-- 3. Functions ==================================================================
-- 3a. Info Functions

CREATE OR REPLACE FUNCTION public.session_info(
	_activity_id character varying DEFAULT NULL::character varying,
	_sport character varying DEFAULT NULL::character varying,
	_start_date timestamp with time zone DEFAULT NULL::timestamp with time zone,
	_end_date timestamp with time zone DEFAULT NULL::timestamp with time zone,
	_accountid integer DEFAULT NULL::integer)
    RETURNS SETOF session_view 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
BEGIN
    RETURN QUERY
    SELECT * FROM session_view
    WHERE 
        (_activity_id IS NULL OR activity_id = _activity_id)
        AND (_sport IS NULL OR sport = _sport)
		and (_start_date is null or start_time::date >= _start_date)
		and (_end_date is null or start_time::date <= _end_date)
		and is_visible
    ORDER BY 
        start_time;
END;
$BODY$
;

CREATE OR REPLACE FUNCTION public.lap_info(
	_activity_id character varying DEFAULT NULL::character varying,
	_sport character varying DEFAULT NULL::character varying,
	_start_date timestamp with time zone DEFAULT NULL::timestamp with time zone,
	_end_date timestamp with time zone DEFAULT NULL::timestamp with time zone,
	_accountid integer DEFAULT NULL::integer)
    RETURNS SETOF lap_view 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
BEGIN
    RETURN QUERY
	select * from lap_view rgd
	where rgd.sport in ('running', 'rowing', 'cycling')
	and (_activity_id IS NULL OR rgd.activity_id = _activity_id)
        AND (_sport IS NULL OR rgd.sport = _sport)
		and (_start_date is null or rgd.start_time::date >= _start_date)
		and (_end_date is null or rgd.start_time::date <= _end_date)
		and accountid = _accountid
	order by rgd.start_time::date desc, lap_num asc;
END;
$BODY$
;

CREATE OR REPLACE FUNCTION public.record_info(
	_activity_id character varying DEFAULT NULL::character varying,
	_start_date timestamp with time zone DEFAULT NULL::timestamp with time zone,
	_end_date timestamp with time zone DEFAULT NULL::timestamp with time zone,
	_accountid integer DEFAULT NULL::integer)
    RETURNS SETOF record_view 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
BEGIN
    RETURN QUERY
    SELECT * FROM record_view
    WHERE 
        (_activity_id IS NULL OR activity_id = _activity_id)
		and (_start_date is null or "timestamp"::date >= _start_date)
		and (_end_date is null or "timestamp"::date <= _end_date)
		and accountid = _accountid
    ORDER BY 
        "timestamp";
END;
$BODY$
;

-- 3b. DataAccess Helper Functions

CREATE OR REPLACE FUNCTION public.get_activity_info_by_date(
	_date date,
	_accountid integer,
	OUT s_curs refcursor,
	OUT l_curs refcursor,
	OUT r_curs refcursor)
    RETURNS record
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
DECLARE
    _start_date DATE;
    _end_date DATE;
BEGIN
    _start_date := _date - INTERVAL '1 day';
    _end_date := _date + INTERVAL '1 day';
	drop table if exists session_info_data;
	
	create temp table session_info_data as	
    SELECT * FROM public.session_info(NULL, NULL, _start_date, _end_date, _accountid) as "a"
    WHERE a.start_time::date = _date;

	open s_curs for
	select * from session_info_data;
	
	open l_curs for	
	select * from public.lap_info
	(NULL, NULL, _start_date, _end_date, _accountid) as "l"
    WHERE l.activity_id in (select distinct s.activity_id from session_info_data as "s");
	
	open r_curs for
	select * from public.record_info
	(null,_start_date,_end_date, _accountid) as "r"
	where r.activity_id in (select distinct s.activity_id from session_info_data as "s");
END;
$BODY$
;

CREATE OR REPLACE FUNCTION public.get_activity_info_by_date_range(
	_start_date date,
	_end_date date,
	_accountid integer,
	OUT s_curs refcursor,
	OUT l_curs refcursor,
	OUT r_curs refcursor)
    RETURNS record
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
DECLARE
	_start_date_func date;
	_end_date_func date;
BEGIN
    _start_date_func := _start_date - INTERVAL '1 day';
    _end_date_func := _end_date + INTERVAL '1 day';
	drop table if exists session_info_data;

	create temp table session_info_data as	
    SELECT * FROM session_info(NULL, NULL, _start_date_func, _end_date_func, _accountid) as "a"
    WHERE a.start_time::date between _start_date and _end_date
	order by a.start_time;
	
	open s_curs for
	select * from session_info_data;
	
	open l_curs for	
	select * from public.lap_info(NULL, NULL, _start_date_func, _end_date_func, _accountid) as "l"
    WHERE l.activity_id in (select distinct s.activity_id from session_info_data as "s");
	
	open r_curs for
	select * from public.record_info(NULL, _start_date_func, _end_date_func, _accountid) as "r"
	where r.activity_id in (select distinct s.activity_id from session_info_data as "s");
	
END;
$BODY$
;

CREATE OR REPLACE FUNCTION public.get_recent_posts(
	_accountid integer,
	_sport text,
	_offset integer,
	_limit integer DEFAULT 10,
	OUT s_curs refcursor,
	OUT l_curs refcursor,
	OUT r_curs refcursor)
    RETURNS record
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
	declare _otherSport boolean;
begin
	_otherSport:=False;

	if _sport = 'Other' then
		_sport:=null;
		_otherSport:=True;
	end if;
	
	drop table if exists session_data_table;

	create temp table session_data_table as
	select * from session_info(null,_sport,null,null, _accountid)
	WHERE ((_otherSport AND sport NOT IN ('Rowing', 'Running', 'Cycling'))
		or not _otherSport)
	order by start_time desc
	limit _limit offset _offset;
	
	open s_curs for
	select * from session_data_table;
	
	open l_curs for
	select * from lap_info(null, null, null, null, _accountid) as "l"
	where "l".activity_id in (select distinct activity_id from session_data_table);
	
	open r_curs for
	select * from record_info(null, null, null, _accountid) as "r"
	where "r".activity_id in (select distinct activity_id from session_data_table);
	
	
END;
$BODY$
;

CREATE OR REPLACE FUNCTION public.search_activities_for_edit(
	_date date,
	_title text,
	_accountid integer)
    RETURNS TABLE(activity_id text, start_time text, display_sport text, total_time double precision, total_distance numeric, activity_title text, description text) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
DECLARE
    _start_date DATE;
    _end_date DATE;
BEGIN
	drop table if exists session_info_data; 
	
	if _date is not null then
	    _start_date := _date - INTERVAL '1 day';
	    _end_date := _date + INTERVAL '1 day';

		create temp table session_info_data as	
		SELECT a.accountid, a.activity_id, a.start_time, a.display_sport, a.total_time, a.total_distance, a.activity_title, a.description
		FROM public.session_info(NULL, NULL, _start_date, _end_date, _accountid) as "a"
	    WHERE a.start_time::date = _date;
	else
	
		create temp table session_info_data as	
		SELECT a.accountid, a.activity_id, a.start_time, a.display_sport, a.total_time, a.total_distance, a.activity_title, a.description
		from session_view as "a"
		where lower(a.activity_title) like '%' || lower(_title) || '%';
	END IF;

	RETURN QUERY
	select a.activity_id, replace(replace(replace(to_char(a.start_time, 'FMMM/DD/YYYY FMHH12:MI AM'), 'PM', 'pm'), 'AM', 'am'), '/0', '/'), a.display_sport, a.total_time, round(a.total_distance, 2), a.activity_title, a.description 
	from session_info_data as "a"
	where a.accountid = _accountid
	order by a.start_time desc
	limit 100;

END;
$BODY$
;

CREATE OR REPLACE FUNCTION public.calendar_info(
	_month integer,
	_year integer)
    RETURNS TABLE(activity_id text, start_time timestamp with time zone, display_sport text, total_time double precision, total_distance numeric, activity_title text, sport text) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
DECLARE
    _start_date date;
    _end_date date;
BEGIN
    _start_date := (_year || '-' || _month || '-01')::date;
    _end_date := (_year || '-' || _month || '-01')::date + interval '1 month' - interval '1 day';
    
    RETURN QUERY
    SELECT "s".activity_id, "s".start_time, "s".display_sport, "s".total_time, "s".total_distance, "s".activity_title, "s".sport
    FROM session_info(null, null, _start_date, _end_date) as "s";
END;
$BODY$;

