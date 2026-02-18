# gdg_game

cd DuckHunt-JS-master/backend
source venv/bin/activate
pip install -r requirements.txt
flask --app main run --port 8000


# /var/www/<username>_pythonanywhere_com_wsgi.py
import sys
sys.path.insert(0, '/home/<username>/gdg_game/DuckHunt-JS-master/backend')
from main import app as application
