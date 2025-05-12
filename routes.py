
from flask import Blueprint, request, jsonify, g, send_from_directory
from flask_bcrypt import Bcrypt
from models import User, SessionToken, db
import os
import io
from contextlib import redirect_stdout
from datetime import datetime, timedelta
import uuid  # Убедитесь, что uuid импортирован
from functools import wraps  # Импортируем wraps
from werkzeug.utils import secure_filename # Secure file uploads

api_bp = Blueprint('api', __name__)
bcrypt = Bcrypt()

UPLOAD_FOLDER = 'uploads' # Директория для загрузок
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Вспомогательная функция для аутентификации по токену ---
def token_required(f):
    """Декоратор для защиты эндпоинтов токеном сессии."""

    @wraps(f)  # ДОБАВЛЕНА ЭТА СТРОКА ДЛЯ ИСПРАВЛЕНИЯ ОШИБКИ
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'success': False, 'message': 'Authorization header missing'}), 401

        try:
            token = auth_header.split()[1]  # Ожидаем формат "Bearer <token>"
        except IndexError:
            return jsonify({'success': False, 'message': 'Invalid Authorization header format'}), 401

        session_token = SessionToken.query.filter_by(token=token).first()

        if not session_token or not session_token.is_valid():
            # Удаляем невалидные токены для очистки (опционально)
            if session_token:
                db.session.delete(session_token)
                db.session.commit()
            return jsonify({'success': False, 'message': 'Invalid or expired token'}), 401

        # Сохраняем пользователя в глобальном объекте запроса (g)
        # Теперь вы можете получить текущего пользователя через g.current_user
        g.current_user = session_token.user
        return f(*args, **kwargs)

    return decorated_function

# Маршрут для обслуживания статических файлов профиля
@api_bp.route('/uploads/<filename>')
def get_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# ------------------------------------------------------------

# Регистрация
@api_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        login = data.get('login')
        password = data.get('password')
        firstName = data.get('firstName')
        lastName = data.get('lastName')

        if not all([login, password, firstName, lastName]):
            return jsonify({'success': False, 'message': 'Missing registration data'}), 400

        if User.query.filter_by(login=login).first():
            return jsonify({'success': False, 'message': 'Login already exists'}), 400

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(login=login, password=hashed_pw, firstName=firstName, lastName=lastName)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'success': True, 'message': 'User registered successfully'}), 201
    except Exception as e:
        print(f"Error in register route: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'message': f"Registration failed: {str(e)}"}), 500

# Вход
@api_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        login = data.get('login')
        password = data.get('password')

        user = User.query.filter_by(login=login).first()

        if user and bcrypt.check_password_hash(user.password, password):
            # При успешном входе, создаем новый токен сессии
            # Удалим старые токены пользователя для простоты (опционально, можно управлять несколькими сессиями)
            # SessionToken.query.filter_by(user_id=user.id).delete() # Раскомментируйте, если хотите разрешить только одну активную сессию на пользователя
            # db.session.commit() # Раскомментируйте, если удаляете старые токены

            new_token = SessionToken(user_id=user.id)
            db.session.add(new_token)
            db.session.commit()

            return jsonify({'success': True, 'access_token': new_token.token}), 200
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    except Exception as e:
        print(f"Error in login route: {e}")
        db.session.rollback()  # Откатываем изменения, если создание токена не удалось
        return jsonify({'success': False, 'message': f"Login failed: {str(e)}"}), 500

# Выход
@api_bp.route('/logout', methods=['POST'])
@token_required  # Защищаем эндпоинт выхода токеном
def logout():
    try:
        # current_user доступен благодаря декоратору @token_required
        user_id = g.current_user.id
        # Удаляем токен, который был использован для этого запроса
        # Это более точный выход, чем удаление всех токенов пользователя
        auth_header = request.headers.get('Authorization')
        if auth_header:
            token = auth_header.split()[1]
            SessionToken.query.filter_by(token=token, user_id=user_id).delete()
            db.session.commit()

        return jsonify({'success': True, 'message': 'Logged out successfully'}), 200
    except Exception as e:
        print(f"Error in logout route: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'message': f"Logout failed: {str(e)}"}), 500

# Профиль
@api_bp.route('/profile', methods=['GET'])
@token_required  # Используем новый декоратор
def get_profile():
    try:
        # current_user доступен благодаря декоратору @token_required
        user = g.current_user
        print(f"Getting profile for user: {user.login}")  # Log user info

        return jsonify({
            'login': user.login,
            'firstName': user.firstName,
            'lastName': user.lastName,
            'profilePicture': user.profilePicture,
            # Удалены поля mathProgress и informaticsProgress
        }), 200

    except Exception as e:
        print(f"Error in get_profile route: {e}")
        return jsonify({'success': False, 'message': f"Failed to get profile: {str(e)}"}), 500

# Загрузка фото профиля
@api_bp.route('/upload_profile_picture', methods=['POST'])
@token_required
def upload_profile_picture():
    try:
        user = g.current_user
        print(f"Updating profile picture for user: {user.login}")

        if 'profilePicture' not in request.files:
            return jsonify({'success': False, 'message': 'No file part'}), 400

        file = request.files['profilePicture']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No selected file'}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            user.profilePicture = f'/uploads/{filename}'  # Store the path to the file

            db.session.commit()

            # Return updated user data
            return jsonify({
                'login': user.login,
                'firstName': user.firstName,
                'lastName': user.lastName,
                'profilePicture': user.profilePicture,
            }), 200
        else:
            return jsonify({'success': False, 'message': 'Allowed file types are png, jpg, jpeg, gif'}), 400

    except Exception as e:
        print(f"Error in upload_profile_picture route: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'message': f"Failed to upload profile picture: {str(e)}"}), 500

# Удаление фото профиля
@api_bp.route('/delete_profile_picture', methods=['DELETE'])
@token_required
def delete_profile_picture():
    try:
        user = g.current_user

        # Check if a profile picture exists
        if user.profilePicture:
            # Remove file from the filesystem
            filepath = os.path.join(os.getcwd(), 'frontend', 'build', user.profilePicture[1:]) # Adjust filepath
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except Exception as e:
                    print(f"Error deleting file: {e}")
                    # Log error but proceed to update database
            else:
                print(f"File not found: {filepath}")

            # Set profilePicture to null in the database
            user.profilePicture = None
            db.session.commit()

            # Return updated user data
            return jsonify({
                'login': user.login,
                'firstName': user.firstName,
                'lastName': user.lastName,
                'profilePicture': user.profilePicture,
            }), 200
        else:
            return jsonify({'success': False, 'message': 'No profile picture to delete'}), 400

    except Exception as e:
        print(f"Error in delete_profile_picture route: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'message': f"Failed to delete profile picture: {str(e)}"}), 500

# Теория по математике
@api_bp.route('/api/math_theory', methods=['GET'])
@token_required  # Используем декоратор
def get_math_theory():
    try:
        theory = [
            {
                'id': 1,
                'content': (
                    "<p><b>Математика</b> - это фундаментальная наука, изучающая абстрактные структуры, отношения и закономерности, которые могут быть применены для описания и понимания реального мира. Она является языком науки и техники, а также основой для многих других дисциплин.</p>"
                    "<p>Математика не ограничивается только числами и вычислениями. Она охватывает широкий спектр тем, от логики и теории множеств до анализа бесконечно малых и теории вероятностей. Её методы включают аксиоматический подход, доказательство теорем и моделирование сложных систем.</p>"
                    "<p><b>Пример:</b> Определение площади круга с помощью формулы πr² - это пример математического знания, которое применяется в геометрии и имеет практическое применение в инженерии и строительстве.</p>"
                )
            },
            {
                'id': 2,
                'content': (
                    "<p><b>Основные разделы математики:</b></p>"
                    "<ul>"
                    "<li><b>Алгебра:</b> Изучает операции, уравнения, неравенства и структуры, такие как группы, кольца и поля.  Алгебра абстрагируется от конкретных чисел и работает с символами и переменными.</li>"
                    "<li><b>Геометрия:</b> Изучает формы, размеры, положения и свойства пространственных объектов. Геометрия делится на евклидову (плоскую и пространственную) и неевклидову (например, сферическую).</li>"
                    "<li><b>Анализ (математический анализ):</b> Изучает непрерывные функции, пределы, производные, интегралы и бесконечные ряды.  Анализ является основой для математического моделирования и оптимизации.</li>"
                    "<li><b>Дискретная математика:</b> Изучает дискретные структуры, такие как графы, множества, комбинации и логические выражения. Дискретная математика важна для информатики и компьютерных наук.</li>"
                    "</ul>"
                    "<p>Эти разделы тесно связаны друг с другом и часто используются совместно для решения сложных задач. Например, алгебраические методы могут использоваться для решения геометрических задач, а анализ - для изучения свойств дискретных систем.</p>"
                    "<p><b>Пример:</b> Для решения задачи оптимизации (найти максимум или минимум функции) используются методы как анализа (нахождение производной), так и алгебры (решение уравнений).</p>"
                )
            },
            {
                'id': 3,
                'content': (
                    "<p><b>Алгебра</b> изучает операции (сложение, вычитание, умножение, деление и т. д.) и отношения (равенство, неравенство и т. д.) между числами и символами, а также структуры, такие как группы, кольца и поля.</p>"
                    "<p>Алгебра подразделяется на несколько областей: элементарная алгебра (изучение уравнений и неравенств), линейная алгебра (изучение векторов, матриц и линейных преобразований), абстрактная алгебра (изучение алгебраических структур). </p>"
                    "<p><b>Пример:</b> Решение квадратного уравнения ax² + bx + c = 0 с помощью формулы дискриминанта - это пример алгебраической задачи.</p>"
                )
            },
            {
                'id': 4,
                'content': (
                    "<p><b>Геометрия</b> изучает формы, размеры, положения и свойства пространственных объектов, таких как точки, линии, плоскости, фигуры и тела.</p>"
                    "<p>Геометрия делится на несколько областей: евклидова геометрия (изучение фигур на плоскости и в пространстве), аналитическая геометрия (использование координат для описания геометрических объектов), дифференциальная геометрия (изучение кривых и поверхностей с помощью методов анализа), топология (изучение свойств фигур, которые не меняются при непрерывных деформациях).</p>"
                    "<p><b>Пример:</b> Вычисление объема цилиндра или площади поверхности сферы - это пример геометрической задачи.</p>"
                )
            },
            {
                'id': 5,
                'content': (
                    "<p><b>Математический анализ</b> изучает непрерывные функции, пределы, производные, интегралы и бесконечные ряды. Он предоставляет инструменты для изучения изменений и движения.</p>"
                    "<p>Ключевые понятия математического анализа: предел (значение, к которому стремится функция), производная (скорость изменения функции), интеграл (площадь под графиком функции), ряд (бесконечная сумма чисел).</p>"
                    "<p><b>Пример:</b> Определение скорости и ускорения движущегося объекта, моделирование роста популяции, анализ колебаний - это примеры задач, решаемых с помощью математического анализа.</p>"
                )
            },
            {
                'id': 6,
                'content': (
                    "<p><b>Дискретная математика</b> изучает дискретные (непрерывные) структуры, такие как графы, множества, комбинации, логические выражения и алгоритмы. Она играет важную роль в информатике и компьютерных науках.</p>"
                    "<p>Основные области дискретной математики: теория множеств, теория графов, комбинаторика, математическая логика, теория чисел.</p>"
                    "<p><b>Пример:</b> Разработка алгоритма поиска кратчайшего пути в графе, анализ сложности алгоритма, проектирование баз данных - это примеры задач, решаемых с помощью дискретной математики.</p>"
                )
            },
            {
                'id': 7,
                'content': (
                    "<p><b>Теория вероятностей</b> изучает случайные события и их вероятности. Она предоставляет инструменты для анализа и моделирования случайных явлений.</p>"
                    "<p>Ключевые понятия теории вероятностей: вероятность (численная оценка возможности наступления события), случайная величина (величина, принимающая случайные значения), распределение вероятностей (описание вероятностей различных значений случайной величины).</p>"
                    "<p><b>Пример:</b> Оценка вероятности выигрыша в лотерее, анализ рисков в страховании, моделирование случайных процессов (например, броуновского движения) - это примеры задач, решаемых с помощью теории вероятностей.</p>"
                )
            }
        ]
        return jsonify(theory), 200
    except Exception as e:
        print(f"Error in get_math_theory route: {e}")
        return jsonify({'success': False, 'message': f"Failed to get math theory: {str(e)}"}), 500


# Практика по математике
@api_bp.route('/api/math_practice_questions', methods=['GET'])
@token_required  # Используем новый декоратор
def get_math_practice_questions():
    try:
        questions = [
            {'id': 1, 'question_text': 'Чему равно 2 + 2?', 'correct_answer': '4'},
            {'id': 2, 'question_text': 'Чему равно 5 * 5?', 'correct_answer': '25'},
            {'id': 3, 'question_text': 'Вычислите площадь прямоугольника со сторонами 4 и 6.', 'correct_answer': '24'},
            {'id': 4, 'question_text': 'Решите уравнение: x + 5 = 10', 'correct_answer': '5'},
            {'id': 5, 'question_text': 'Чему равен квадратный корень из 81?', 'correct_answer': '9'},
            {'id': 6, 'question_text': 'Если у вас есть 12 яблок и вы отдаете 5, сколько у вас останется?', 'correct_answer': '7'},
            {'id': 7, 'question_text': 'Найдите периметр квадрата со стороной 7.', 'correct_answer': '28'},
            {'id': 8, 'question_text': 'Сколько будет, если 3 умножить на 8?', 'correct_answer': '24'},
            {'id': 9, 'question_text': 'Чему равно 20 процентов от 100?', 'correct_answer': '20'},
            {'id': 10, 'question_text': 'Решите уравнение: 2x = 14', 'correct_answer': '7'},
            {'id': 11, 'question_text': 'Что такое теорема Пифагора?', 'correct_answer': 'a^2 + b^2 = c^2'},
            {'id': 12, 'question_text': 'Вычислите: 15 / 3 + 7', 'correct_answer': '12'},
            {'id': 13, 'question_text': 'Найдите значение x: 3x + 2 = 11', 'correct_answer': '3'},
            {'id': 14, 'question_text': 'Сколько градусов в прямом угле?', 'correct_answer': '90'},
            {'id': 15, 'question_text': 'Что такое число Пи?', 'correct_answer': '3.14159'},
            {'id': 16, 'question_text': 'Решите неравенство: x - 3 > 7', 'correct_answer': 'x > 10'},
            {'id': 17, 'question_text': 'Вычислите объем куба со стороной 5.', 'correct_answer': '125'},
            {'id': 18, 'question_text': 'Чему равна производная функции f(x) = x^2?', 'correct_answer': '2x'},
            {'id': 19, 'question_text': 'Найдите интеграл функции f(x) = 1.', 'correct_answer': 'x + C'},
            {'id': 20, 'question_text': 'Что такое мнимая единица в комплексных числах?', 'correct_answer': 'i'},
        ]
        return jsonify(questions), 200
    except Exception as e:
        print(f"Error in get_math_practice_questions route: {e}")
        return jsonify({'success': False, 'message': f"Failed to get math practice questions: {str(e)}"}), 500

# Теория по информатике
@api_bp.route('/api/informatics_theory', methods=['GET'])
@token_required  # Используем декоратор
def get_informatics_theory():
    try:
        theory = [
            {
                'id': 1,
                'content': (
                    "<p><b>Информатика</b> - это наука, изучающая структуру и общие свойства информации, а также закономерности ее создания, хранения, обработки, передачи и использования в различных сферах человеческой деятельности.  Она охватывает широкий спектр тем, от фундаментальных теоретических основ до практических приложений в технике и повседневной жизни.</p>"
                    "<p>Исторически, информатика выросла из математики, электротехники и лингвистики.  Первые попытки автоматизировать вычисления привели к созданию механических вычислительных устройств, а развитие электроники позволило создать более мощные и гибкие компьютеры.</p>"
                    "<p>Важно отметить, что информатика не сводится только к программированию или использованию компьютеров. Она изучает фундаментальные принципы, лежащие в основе информационных процессов, независимо от конкретной технологии их реализации.  Это делает ее актуальной и перспективной областью знаний.</p>"
                    "<p><b>Пример:</b>  Разработка эффективного алгоритма сортировки массива данных - это задача информатики.  Применение этого алгоритма в программе, написанной на Python, - это уже применение информатики в программировании.</p>"
                )
            },
            {
                'id': 2,
                'content': (
                    "<p><b>Основные понятия информатики</b> включают:</p>"
                    "<ul>"
                    "<li><b>Данные:</b>  Представление информации в формализованном виде, пригодном для обработки компьютером. Данные могут быть числами, текстом, изображениями, звуком и т.д.</li>"
                    "<li><b>Информация:</b>  Совокупность сведений, уменьшающих неопределенность знания о чем-либо.  Информация - это интерпретированные данные, имеющие смысл для получателя.</li>"
                    "<li><b>Алгоритмы:</b>  Точная, понятная и конечная последовательность действий (инструкций), необходимых для решения определенной задачи.  Алгоритм должен быть детерминированным, то есть при одинаковых входных данных всегда давать одинаковый результат.</li>"
                    "<li><b>Программы:</b>  Алгоритм, записанный на языке программирования, понятном для компьютера.  Программа представляет собой набор инструкций, которые компьютер выполняет для решения поставленной задачи.</li>"
                    "</ul>"
                    "<p>Важно различать данные и информацию. Данные - это просто факты, а информация - это интерпретация этих фактов. Например, число 37 - это данные. А фраза 'Температура тела 37 градусов Цельсия' - это информация, потому что она дает нам представление о состоянии здоровья.</p>"
                    "<p><b>Пример:</b>  Список имен студентов (данные) преобразуется в отсортированный по алфавиту список (информация) с помощью алгоритма сортировки, реализованного в виде программы на Python.</p>"
                )
            },
            {
                'id': 3,
                'content': (
                    "<p><b>Компьютер</b> состоит из двух основных частей: аппаратного (hardware) и программного (software) обеспечения.</p>"
                    "<ul>"
                    "<li><b>Аппаратное обеспечение (hardware):</b>  Физические компоненты компьютера, такие как процессор (CPU), память (RAM), жесткий диск (HDD/SSD), монитор, клавиатура, мышь и т.д.</li>"
                    "<li><b>Программное обеспечение (software):</b>  Набор программ, которые позволяют компьютеру выполнять определенные задачи.  Включает операционные системы, прикладные программы (текстовые редакторы, браузеры, игры и т.д.) и системные утилиты.</li>"
                    "</ul>"
                    "<p>Аппаратное обеспечение обеспечивает физическую возможность выполнения вычислений, а программное обеспечение определяет, какие именно вычисления должны быть выполнены.  Они работают в тесной взаимосвязи друг с другом.</p>"
                    "<p><b>Пример:</b>  Процессор (hardware) выполняет инструкции, содержащиеся в программе (software), чтобы отобразить веб-страницу в браузере.</p>"
                )
            },
            {
                'id': 4,
                'content': (
                    "<p><b>Алгоритм</b> - это четкая, конечная последовательность инструкций, предназначенная для решения конкретной задачи или достижения определенной цели.  Алгоритмы играют ключевую роль в информатике и программировании.</p>"
                    "<p><b>Основные свойства алгоритма:</b></p>"
                    "<ul>"
                    "<li><b>Детерминированность:</b>  При одинаковых входных данных алгоритм всегда выдает одинаковый результат.</li>"
                    "<li><b>Конечность:</b>  Алгоритм должен завершаться за конечное число шагов.</li>"
                    "<li><b>Понятность:</b>  Инструкции алгоритма должны быть понятны исполнителю (человеку или компьютеру).</li>"
                    "<li><b>Эффективность:</b>  Алгоритм должен решать задачу оптимальным образом, используя минимальное количество ресурсов (времени, памяти и т.д.).</li>"
                    "<li><b>Массовость:</b> Алгоритм должен быть применим для решения класса однотипных задач, а не только для конкретной задачи.</li>"
                    "</ul>"
                    "<p>Алгоритмы можно представлять различными способами: словесно, графически (в виде блок-схем) или на языке программирования.</p>"
                    "<p><b>Пример:</b> Алгоритм приготовления чая: 1. Вскипятить воду. 2. Положить чайный пакетик в чашку. 3. Залить кипятком. 4. Настоять 3-5 минут. 5. Добавить сахар и/или лимон по вкусу.</p>"
                )
            },
            {
                'id': 5,
                'content': (
                    "<p><b>Программа</b> - это алгоритм, записанный на формальном языке программирования, понятном для компьютера.  Программа представляет собой последовательность инструкций, которые компьютер выполняет для решения поставленной задачи.</p>"
                    "<p><b>Языки программирования</b> бывают разных типов: низкоуровневые (например, ассемблер) и высокоуровневые (например, Python, Java, C++).  Высокоуровневые языки более удобны для программирования, так как используют более абстрактные конструкции, близкие к человеческому языку.</p>"
                    "<p><b>Процесс создания программы</b> включает несколько этапов: определение задачи, разработка алгоритма, написание кода программы, отладка и тестирование.</p>"
                    "<p><b>Пример:</b> Программа на Python для вычисления суммы двух чисел:</p>"
                    "<pre><code>\n"
                    "a = 5\n"
                    "b = 3\n"
                    "sum = a + b\n"
                    "print(sum)\n"
                    "</code></pre>"
                )
            },
            {
                'id': 6,
                'content': (
                    "<p><b>Операционная система (ОС)</b> - это комплекс программ, который управляет аппаратными и программными ресурсами компьютера, обеспечивая интерфейс между пользователем и аппаратным обеспечением.</p>"
                    "<p><b>Основные функции операционной системы:</b></p>"
                    "<ul>"
                    "<li>Управление процессами: запуск, остановка и контроль выполнения программ.</li>"
                    "<li>Управление памятью: распределение и освобождение памяти для программ.</li>"
                    "<li>Управление файловой системой: организация хранения данных на дисках.</li>"
                    "<li>Управление устройствами ввода-вывода: взаимодействие с клавиатурой, мышью, принтером и другими устройствами.</li>"
                    "<li>Обеспечение безопасности: защита данных от несанкционированного доступа.</li>"
                    "<li>Предоставление пользовательского интерфейса: способ взаимодействия пользователя с компьютером (например, графический интерфейс или командная строка).</li>"
                    "</ul>"
                    "<p><b>Примеры операционных систем:</b> Windows, macOS, Linux, Android, iOS.</p>"
                    "<p><b>Пример:</b> Когда вы открываете браузер на своем компьютере, операционная система выделяет ему память, загружает программу браузера в эту память и позволяет ей взаимодействовать с сетью и отображать веб-страницы на экране.</p>"
                )
            },
            {
                'id': 7,
                'content': (
                    "<p><b>Сети компьютеров</b> позволяют обмениваться данными между устройствами. Компьютерные сети могут быть локальными (LAN), охватывающими небольшую территорию (например, офис или дом), или глобальными (WAN), охватывающими большие территории (например, Интернет).</p>"
                    "<p><b>Основные компоненты компьютерной сети:</b></p>"
                    "<ul>"
                    "<li>Компьютеры (хосты): устройства, подключенные к сети.</li>"
                    "<li>Сетевые устройства: маршрутизаторы, коммутаторы, модемы, точки доступа Wi-Fi, обеспечивающие передачу данных между компьютерами.</li>"
                    "<li>Кабели или беспроводные соединения: физическая среда передачи данных.</li>"
                    "<li>Сетевые протоколы: набор правил, определяющих формат и порядок обмена данными в сети (например, TCP/IP, HTTP).</li>"
                    "</ul>"
                    "<p><b>Интернет</b> - это глобальная компьютерная сеть, объединяющая миллионы компьютеров по всему миру.</p>"
                    "<p><b>Пример:</b> Когда вы отправляете электронное письмо, оно передается через различные сетевые устройства, используя протокол TCP/IP, пока не достигнет почтового сервера получателя. Затем получатель может прочитать письмо, используя почтовый клиент.</p>"
                )
            }
        ]
        return jsonify(theory), 200
    except Exception as e:
        print(f"Error in get_informatics_theory route: {e}")
        return jsonify({'success': False, 'message': f"Failed to get informatics theory: {str(e)}"}), 500


# Практика по информатике
@api_bp.route('/api/informatics_practice_questions', methods=['GET'])
@token_required  # Используем новый декоратор
def get_informatics_practice_questions():
    try:
        questions = [
            {'id': 1, 'question_text': 'Что такое CPU?', 'correct_answer': 'Центральный процессор'},
            {'id': 2, 'question_text': 'Что такое RAM?', 'correct_answer': 'Оперативная память'},
            {'id': 3, 'question_text': 'Что такое HTML?', 'correct_answer': 'Язык гипертекстовой разметки'},
            {'id': 4, 'question_text': 'Что такое CSS?', 'correct_answer': 'Каскадные таблицы стилей'},
            {'id': 5, 'question_text': 'Что такое JavaScript?', 'correct_answer': 'Язык программирования для веб'},
            {'id': 6, 'question_text': 'Что такое SQL?', 'correct_answer': 'Язык запросов к базам данных'},
            {'id': 7, 'question_text': 'Что такое HTTP?', 'correct_answer': 'Протокол передачи гипертекста'},
            {'id': 8, 'question_text': 'Что такое TCP/IP?', 'correct_answer': 'Набор сетевых протоколов'},
            {'id': 9, 'question_text': 'Что такое VPN?', 'correct_answer': 'Виртуальная частная сеть'},
            {'id': 10, 'question_text': 'Что такое API?', 'correct_answer': 'Интерфейс программирования приложений'},
            {'id': 11, 'question_text': 'Что такое BIOS?', 'correct_answer': 'Базовая система ввода-вывода'},
            {'id': 12, 'question_text': 'Что такое GUI?', 'correct_answer': 'Графический пользовательский интерфейс'},
            {'id': 13, 'question_text': 'Что такое IDE?', 'correct_answer': 'Интегрированная среда разработки'},
            {'id': 14, 'question_text': 'Что такое URL?', 'correct_answer': 'Унифицированный указатель ресурсов'},
            {'id': 15, 'question_text': 'Что такое DNS?', 'correct_answer': 'Система доменных имен'},
            {'id': 16, 'question_text': 'Что такое версия ОС?', 'correct_answer': 'Номер релиза операционной системы'},
            {'id': 17, 'question_text': 'Что такое компилятор?', 'correct_answer': 'Программа для перевода кода в машинный код'},
            {'id': 18, 'question_text': 'Что такое алгоритм сортировки?', 'correct_answer': 'Метод упорядочивания элементов'},
            {'id': 19, 'question_text': 'Что такое машинное обучение?', 'correct_answer': 'Обучение компьютера без явного программирования'},
            {'id': 20, 'question_text': 'Что такое блокчейн?', 'correct_answer': 'Распределенная база данных'},
        ]
        return jsonify(questions), 200
    except Exception as e:
        print(f"Error in get_informatics_practice_questions route: {e}")
        return jsonify({'success': False, 'message': f"Failed to get informatics practice questions: {str(e)}"}), 500

# Выполнение Python кода
@api_bp.route('/execute_python', methods=['POST'])
@token_required  # Используем новый декоратор
def execute_python():
    try:
        data = request.get_json()
        code = data.get('code')

        if not code:
            return jsonify({'output': 'No code provided.'}), 400

        f = io.StringIO()
        with redirect_stdout(f):
            # BE VERY CAREFUL WITH THIS - STILL APPLIES!
            # Consider using a secure sandbox like `restrictedpython` or similar
            # For a real application NEVER use `exec` directly with user input
            # Example: Restricted builtins
            restricted_builtins = {
                'print': print,
                'range': range,
                'len': len,
                'sum': sum,
                'max': max,
                'min': min,
                'abs': abs,
                'round': round,
                'list': list,
                'dict': dict,
                'set': set,
                'tuple': tuple,
                'str': str,
                'int': int,
                'float': float,
                'bool': bool,
                'complex': complex,
            }
            try:
                exec(code, {"__builtins__": restricted_builtins})  # Ограничиваем доступ к builtins
            except Exception as exec_err:
                # Перехватываем ошибки выполнения самого кода
                output = f"Execution error: {str(exec_err)}"
                # Возвращаем 200, чтобы показать ошибку выполнения, а не статус сервера
                return jsonify({'output': output}), 200

        output = f.getvalue()
        return jsonify({'output': output}), 200

    except Exception as e:
        # Перехватываем ошибки, не связанные с выполнением самого кода (например, JSON парсинг)
        print(f"Error in execute_python route: {e}")
        return jsonify({'success': False, 'message': f"Server error during execution: {str(e)}"}), 500

# Заглушка для C++
@api_bp.route('/execute_cpp', methods=['POST'])
@token_required  # Используем новый декоратор
def execute_cpp():
    try:
        # В реальном приложении здесь нужно было бы компилировать и запускать C++ код в безопасной среде
        return jsonify({'output': 'C++ execution is not implemented in this example.'}), 501  # 501 Not Implemented
    except Exception as e:
        print(f"Error in execute_cpp route: {e}")
        return jsonify({'success': False, 'message': f"Failed to execute C++: {str(e)}"}), 500
