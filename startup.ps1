# Check if 'env\flask_env' directory exists
if (-not (Test-Path -Path env\flask_env)) {
    # create env folder
    mkdir env
    # change directory to env
    Set-Location env
    # create virtual environment
    python -m venv flask_env
    # go back to the root directory
    Set-Location ..
}

# activate the virtual environment
. .\env\flask_env\Scripts\activate
# install requirements.txt
pip install -r requirements.txt