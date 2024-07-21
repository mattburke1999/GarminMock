# RUN THIS IN POWERSHELL
if (-not (Test-Path -Path env\flask_env)) {
    # create env folder
    mkdir env
    # change directory to env
    Set-Location env
    # create virtual environment
    python -m venv flask_env
    # print venv has been created
    Write-Host "flask_env has been created"
    # go back to the root directory
    Set-Location ..
}
Write-Host "Installing requirements"
# install requirements
. .\env\flask_env\Scripts\pip install -r requirements.txt

# activate virtual environment
. .\env\flask_env\Scripts\activate