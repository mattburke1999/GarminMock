# create env folder
mkdir env
# change directory to env
cd env
# create virtual environment
python -m venv flask_env
# go back to the root directory
cd ..
# activate the virtual environment
env\flask_env\Scripts\activate
# install requirements.txt
pip install -r requirements.txt
