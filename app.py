from flask import Flask
from routes import bp  # Assuming routes.py defines a Blueprint called bp
from dotenv import load_dotenv
load_dotenv(override=True)
import warnings
warnings.filterwarnings("ignore")

from config import ProdConfig, DesktopConfig, LaptopConfig, FLASK_ENV, SECRET_KEY

app = Flask(__name__)
app.register_blueprint(bp)

app.secret_key = SECRET_KEY

if FLASK_ENV == 'desktop':
    app.config.from_object(DesktopConfig)
elif FLASK_ENV == 'laptop':
    app.config.from_object(LaptopConfig)
else:
    app.config.from_object(ProdConfig)

if __name__ == '__main__':
    app.run(debug=True)