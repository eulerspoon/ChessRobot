# Прикладной уровень — Шахматная роботизированная рука (Вариант 9)

## Описание

WebSocket-сервер прикладного уровня для системы обмена сообщениями и телеметрией в реальном времени.

**Тема:** Роботизированная рука играет в шахматы. Задаётся последовательность ходов в нотации. Транслируется положение захвата, координаты фигуры на доске и статус захвата.

**Прототип дизайна:** [lichess.org](https://lichess.org)

**Стек бекенда:** Python + FastAPI + Uvicorn

---

## Структура проекта

```
chess-robot-chat/
├── websocket_server/          # Бекенд (прикладной уровень)
│   ├── main.py                # Точка входа FastAPI (WebSocket + REST)
│   ├── models.py              # Pydantic-модели данных
│   ├── requirements.txt       # Python-зависимости
│   └── README.md              # Этот файл
└── frontend/                  # React-приложение (будет позже)
```

---

## Установка и запуск

### 1. Требования

- **Python 3.10+** (проверить: `python --version` или `python3 --version`)
- **pip** (проверить: `pip --version`)

Если Python не установлен:
- **Windows:** скачать с [python.org](https://www.python.org/downloads/), при установке поставить галочку "Add Python to PATH"
- **macOS:** `brew install python`
- **Linux:** `sudo apt install python3 python3-pip python3-venv`

### 2. Клонирование / загрузка

```bash
# если используете git
git clone <ваш-репозиторий>
cd chess-robot-chat/websocket_server
```

### 3. Создание виртуального окружения

```bash
# создаём виртуальное окружение
python -m venv venv

# активируем
# Windows (cmd):
venv\Scripts\activate
# Windows (PowerShell):
venv\Scripts\Activate.ps1
# macOS / Linux:
source venv/bin/activate
```

После активации в терминале появится `(venv)` перед строкой ввода.

### 4. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 5. Запуск сервера

```bash
# Вариант 1: через python
python main.py

# Вариант 2: через uvicorn напрямую (с горячей перезагрузкой)
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

Сервер запустится на `http://0.0.0.0:8001`

### 6. Открыть Swagger

После запуска доступны:
- **Swagger UI:** [http://localhost:8001/docs](http://localhost:8001/docs) — интерактивная документация
- **ReDoc:** [http://localhost:8001/redoc](http://localhost:8001/redoc) — альтернативный вид
- **OpenAPI JSON:** [http://localhost:8001/openapi.json](http://localhost:8001/openapi.json) — спецификация

---

## API эндпоинты

### WebSocket

**Подключение:** `ws://localhost:8001/ws?username=Player1`

При подключении передаётся `username` в query-параметре. Сервер держит словарь активных соединений.

**Формат JSON (Send → от клиента):**

```json
{
    "username": "Player1",
    "send_time": "2025-04-05T14:30:00",
    "type": "text",
    "data": "Ход выполнен",
    "move_notation": "e2e4",
    "grip_position": {
        "x": 150.0,
        "y": 200.0,
        "z": 50.0
    },
    "piece_coordinates": {
        "file": "e",
        "rank": 4
    },
    "grip_status": "closed"
}
```

**Формат JSON (Receive → клиенту):**

Тот же формат + поле `error`. Если `error` не пустое — в чате показывается иконка ошибки вместо текста.

### REST API

| Метод | Путь           | Описание                                           |
|-------|----------------|----------------------------------------------------|
| POST  | `/send`        | Отправить сообщение (дублирует WebSocket, для Postman) |
| POST  | `/receive`     | Принять сообщение от транспортного уровня          |
| GET   | `/health`      | Проверка состояния сервиса                         |
| GET   | `/connections` | Список активных пользователей                     |

---

## Тестирование в Postman

### 1. REST — отправка сообщения

- **Метод:** POST
- **URL:** `http://localhost:8001/send`
- **Body → raw → JSON:**

```json
{
    "username": "Player1",
    "type": "text",
    "data": "Пешка e2 перемещена на e4",
    "move_notation": "e2e4",
    "grip_position": {"x": 150.0, "y": 200.0, "z": 50.0},
    "piece_coordinates": {"file": "e", "rank": 4},
    "grip_status": "closed"
}
```

### 2. REST — приём от транспортного уровня

- **Метод:** POST
- **URL:** `http://localhost:8001/receive`
- **Body → raw → JSON:**

```json
{
    "username": "Player2",
    "send_time": "2025-04-05T14:31:00",
    "type": "text",
    "data": "Конь перемещён на f6",
    "error": "",
    "move_notation": "g8f6",
    "grip_position": {"x": 300.0, "y": 100.0, "z": 45.0},
    "piece_coordinates": {"file": "f", "rank": 6},
    "grip_status": "open"
}
```

### 3. WebSocket — в Postman

- Создать **New → WebSocket Request**
- URL: `ws://localhost:8001/ws?username=Player1`
- Нажать **Connect**
- Отправить JSON-сообщение (формат Send)

---

## Конфигурация сети (для демонстрации на 3 ПК)

В файле `main.py` задаются адреса:

```python
HOST = "0.0.0.0"                         # слушать на всех интерфейсах
PORT = 8001                              # порт этого сервера
TRANSPORT_LEVEL_HOST = "192.168.1.100"   # ← заменить на IP ПК с транспортным уровнем
TRANSPORT_LEVEL_PORT = 8002              # порт транспортного уровня
```

При демонстрации:
1. Узнать IP каждого ПК: `ipconfig` (Windows) / `ip a` (Linux)
2. Подставить реальные IP в конфигурации всех уровней
3. Убедиться, что все ПК в одной подсети и файрвол не блокирует порты

---

## Поля телеметрии (Вариант 9)

Эти поля специфичны для нашего варианта и отображаются в Swagger:

| Поле               | Тип    | Описание                                  | Пример              |
|--------------------|--------|-------------------------------------------|----------------------|
| `move_notation`    | string | Ход в шахматной нотации                   | `"e2e4"`, `"Nf3"`   |
| `grip_position`    | object | Координаты захвата {x, y, z} в мм        | `{x:150, y:200, z:50}` |
| `piece_coordinates`| object | Позиция фигуры на доске {file, rank}      | `{file:"e", rank:4}` |
| `grip_status`      | enum   | Статус захвата: `open`, `closed`, `moving` | `"closed"`          |
