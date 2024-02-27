from flask import Flask
from routes import bp  # Assuming routes.py defines a Blueprint called bp
from dotenv import load_dotenv
load_dotenv()
import warnings
warnings.filterwarnings("ignore")

app = Flask(__name__)
app.register_blueprint(bp)

app.secret_key = 'your_secret'

if __name__ == '__main__':
    app.run(debug=True)