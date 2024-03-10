if (-not (Test-Path -Path env\flask_env2)) {
    # create env folder
    mkdir env
    # change directory to env
    Set-Location env
    # create virtual environment with python 3.10
    py -3.10 -m venv flask_env2    
    # print venv has been created
    Write-Host "flask_env2 has been created"
    # go back to the root directory
    Set-Location ..
}
# activate the virtual environment
. .\env\flask_env2\Scripts\activate
Write-Host "Virtual environment has been activated...installing sqlacodegen"
pip install sqlacodegen
pip install psycopg2

# get env from .env file (..\.env) and set it to the current environment
Get-Content .env | ForEach-Object { 
    if ($_ -match '^([^=]+)=(.+)$') {
        $key = $matches[1]
        $value = $matches[2]
        [System.Environment]::SetEnvironmentVariable($key, $value)
    }
}
Write-Host "Environment variables have been set...generating models..."

# use sqlacodegen to generate models for the following tables in one command and save them in the models folder
# raw_garmin_data_session
# raw_garmin_data_laps
# raw_garmin_data_records
# session_view
# lap_view
# record_view
sqlacodegen $env:PostgreSQL_desktop_string --tables raw_garmin_data_session,raw_garmin_data_laps,raw_garmin_data_records,session_view,lap_view,record_view --outfile .\models.py



# sqlacodegen $env:PostgreSQL_desktop_string --tables raw_garmin_data_session --outfile .\models\raw_session_model.py
# sqlacodegen $env:PostgreSQL_desktop_string --tables raw_garmin_data_laps --outfile .\models\raw_laps_model.py
# sqlacodegen $env:PostgreSQL_desktop_string --tables raw_garmin_data_records --outfile .\models\raw_records_model.py
# sqlacodegen $env:PostgreSQL_desktop_string --tables session_view --outfile .\models\session_view_model.py
# sqlacodegen $env:PostgreSQL_desktop_string --tables lap_view --outfile .\models\laps_view_model.py
# sqlacodegen $env:PostgreSQL_desktop_string --tables record_view --outfile .\models\records_view_model.py
