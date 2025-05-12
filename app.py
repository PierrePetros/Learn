import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import sys

from models import db
from routes import api_bp
from flask_bcrypt import Bcrypt  # Для работы с паролями
from sqlalchemy import create_engine, text # Работа с SQL

# Загружаем переменные окружения
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    print(".env file not found. Make sure it exists and contains necessary configuration.", file=sys.stderr)
    sys.exit(1)

# Инициализация Flask
app = Flask(__name__, static_folder='frontend/build', static_url_path='')
CORS(app)
bcrypt = Bcrypt(app) # Инициализируем bcrypt
UPLOAD_FOLDER = 'uploads'  # Директория для загрузок
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Конфигурация базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+mysqlconnector://{os.environ.get('MYSQL_USER')}:{os.environ.get('MYSQL_PASSWORD')}@{os.environ.get('MYSQL_HOST')}/{os.environ.get('MYSQL_DB')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)  # Инициализируем SQLAlchemy

# Функция для создания и настройки базы данных
def create_db():
    with app.app_context():
        try:
            engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
            with engine.connect() as con:
                con.execute(text("SELECT 1"))
            db.create_all()  # Создаем таблицы
            # Создаем администратора, если пользователей еще нет
            from models import User
            if User.query.count() == 0:
                admin_login = os.environ.get('ADMIN_LOGIN', 'admin')
                admin_password = os.environ.get('ADMIN_PASSWORD', 'adminpass')
                hashed_pw = bcrypt.generate_password_hash(admin_password).decode('utf-8')
                admin = User(login=admin_login, password=hashed_pw, firstName='Admin', lastName='User')
                db.session.add(admin)
                db.session.commit()
                print("Admin user created.")
            print("Database initialized successfully.")
        except Exception as e:
            print(f"Error during DB setup: {e}")
            raise e  # Перебрасываем исключение для остановки приложения

# Регистрация blueprint
app.register_blueprint(api_bp)

# Маршрут для обслуживания статики
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_static(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    with app.app_context():
        try:
            create_db() # Создаем базу данных при запуске приложения
        except Exception as e:
            print(f"Failed to initialize database: {e}")
            sys.exit(1)
    app.run(debug=True)
