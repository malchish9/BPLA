from flask import Flask, request, jsonify, send_from_directory
import random
import logging

# Создание экземпляра Flask приложения с указанием директории для статических файлов
app = Flask(__name__, static_folder='static')

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()


# --------------------------- Классы модели и бизнес-логики --------------------------- #

class DroneControlSystem:
    """
    Класс для управления данными дрона.
    Содержит информацию о состоянии дрона и методах управления.
    """

    def __init__(self):
        # Инициализация основных параметров дрона
        self.altitude = 0
        self.speed = 0
        self.position = (0, 0)
        self.battery = 100  # Процент заряда батареи
        self.direction = 0  # Направление движения дрона в градусах (0 - север)
        self.log = []  # Журнал для хранения истории действий

    def update_position(self, x, y):
        """Обновление позиции дрона по координатам x и y."""
        self.position = (x, y)
        self.log_action(f"Position updated to {self.position}")

    def change_altitude(self, altitude):
        """Изменение высоты дрона."""
        self.altitude = altitude
        self.log_action(f"Altitude changed to {self.altitude} meters")

    def update_speed(self, speed):
        """Обновление скорости дрона."""
        self.speed = speed
        self.log_action(f"Speed updated to {self.speed} m/s")

    def change_direction(self, direction):
        """Изменение направления движения дрона."""
        self.direction = direction
        self.log_action(f"Direction changed to {self.direction} degrees")

    def consume_battery(self, consumption):
        """Потребление заряда батареи, уменьшая его на заданное количество."""
        self.battery = max(0, self.battery - consumption)
        self.log_action(f"Battery consumed. Current level: {self.battery}%")

    def check_battery(self):
        """Возвращает уровень заряда батареи."""
        return self.battery

    def log_action(self, action):
        """Логирование действия дрона."""
        logger.info(action)  # Логируем действие с помощью логгера
        self.log.append(action)  # Сохраняем в историю

    def get_log(self):
        """Получение истории всех действий дрона."""
        return self.log


# --------------------------- Классы представления --------------------------- #

class DroneInterface:
    """
    Класс для отображения информации о дроне и взаимодействия с пользователем.
    """

    def show_status(self, drone_model):
        """Отображение текущего состояния дрона."""
        return {
            'altitude': drone_model.altitude,
            'speed': drone_model.speed,
            'position': drone_model.position,
            'battery': drone_model.battery,
            'direction': drone_model.direction
        }

    def display_alert(self, message):
        """Отображение предупреждающего сообщения."""
        return {"alert": message}


# --------------------------- Контроллер --------------------------- #

class DroneOperations:
    """
    Контроллер для управления поведением дрона.
    """

    def __init__(self, model, view):
        self.model = model
        self.view = view

    def adjust_position(self, x, y):
        """Изменение позиции дрона."""
        self.model.update_position(x, y)
        return self.view.show_status(self.model)

    def adjust_altitude(self, altitude):
        """Изменение высоты дрона."""
        self.model.change_altitude(altitude)
        return self.view.show_status(self.model)

    def adjust_speed(self, speed):
        """Изменение скорости дрона."""
        self.model.update_speed(speed)
        return self.view.show_status(self.model)

    def adjust_direction(self, direction):
        """Изменение направления движения дрона."""
        self.model.change_direction(direction)
        return self.view.show_status(self.model)

    def monitor_battery(self):
        """Проверка уровня заряда батареи и генерация предупреждений, если уровень низкий."""
        if self.model.check_battery() < 20:
            # Если заряд батареи ниже 20%, отправляем предупреждение
            return self.view.display_alert("Battery low! Returning to base.")
        return self.view.show_status(self.model)

    def get_log(self):
        """Получение истории всех действий дрона."""
        return {"log": self.model.get_log()}


# --------------------------- Симуляция сенсоров --------------------------- #

class SensorSimulation:
    """
    Класс для симуляции сенсоров.
    Генерирует случайные значения для имитации поведения сенсоров дрона.
    """

    def simulate_obstacle(self):
        """Симуляция обнаружения препятствия, возвращает расстояние до ближайшего объекта."""
        distance_to_obstacle = random.uniform(0, 50)  # Случайное расстояние до препятствия
        return distance_to_obstacle

    def simulate_weather_conditions(self):
        """Симуляция погодных условий, включая скорость ветра и тип погоды."""
        wind_speed = random.uniform(0, 20)  # Случайная скорость ветра
        weather_conditions = random.choice(["Clear", "Cloudy", "Stormy", "Rainy"])  # Случайное состояние погоды
        return {"wind_speed": wind_speed, "weather": weather_conditions}


# --------------------------- Инициализация дрона и контроллера --------------------------- #

drone_model = DroneControlSystem()  # Модель дрона
drone_view = DroneInterface()  # Интерфейс пользователя для отображения данных
drone_controller = DroneOperations(drone_model, drone_view)  # Контроллер для управления дроном
sensor_simulator = SensorSimulation()  # Симулятор сенсоров


# --------------------------- Маршруты API --------------------------- #

@app.route('/')
def index():
    """Отправка статического файла index.html в качестве домашней страницы."""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/status', methods=['GET'])
def get_status():
    """API для получения текущего статуса дрона."""
    return jsonify(drone_view.show_status(drone_model))


@app.route('/position', methods=['POST'])
def update_position():
    """API для обновления позиции дрона через POST-запрос."""
    data = request.get_json()
    x, y = data.get('x', 0), data.get('y', 0)
    return jsonify(drone_controller.adjust_position(x, y))


@app.route('/altitude', methods=['POST'])
def update_altitude():
    """API для обновления высоты дрона через POST-запрос."""
    data = request.get_json()
    altitude = data.get('altitude', 0)
    return jsonify(drone_controller.adjust_altitude(altitude))


@app.route('/speed', methods=['POST'])
def update_speed():
    """API для обновления скорости дрона через POST-запрос."""
    data = request.get_json()
    speed = data.get('speed', 0)
    return jsonify(drone_controller.adjust_speed(speed))


@app.route('/battery', methods=['GET'])
def check_battery():
    """API для проверки заряда батареи дрона."""
    return jsonify(drone_controller.monitor_battery())


@app.route('/simulate_obstacle', methods=['GET'])
def simulate_obstacle():
    """API для симуляции обнаружения препятствий."""
    obstacle_distance = sensor_simulator.simulate_obstacle()
    if obstacle_distance < 10:
        # Если препятствие ближе 10 метров, выдаём предупреждение
        return jsonify(
            drone_view.display_alert(f"Obstacle detected {obstacle_distance:.2f} meters away! Adjusting course..."))
    return jsonify({"obstacle_distance": obstacle_distance})


@app.route('/simulate_weather', methods=['GET'])
def simulate_weather():
    """API для симуляции погодных условий."""
    weather = sensor_simulator.simulate_weather_conditions()
    return jsonify(weather)


@app.route('/log', methods=['GET'])
def get_log():
    """API для получения истории действий дрона."""
    return jsonify(drone_controller.get_log())


# --------------------------- Запуск приложения --------------------------- #

if __name__ == '__main__':
    # Запуск Flask-сервера в режиме отладки
    app.run(debug=True)
