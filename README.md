# Гостевая книга на Django (Reviews)

Пользователи могут оставлять отзывы с указанием имени автора и текста, просматривать опубликованные отзывы, а администраторы — управлять ими через панель управления с поиском по автору.

## Как запустить

Требуется **Python 3.10** или новее.

### 1. Клонирование и переход в папку проекта

```bash
cd guest-book-2
```

### 2. Создание и активация виртуального окружения

**macOS и Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Установка зависимостей

```bash
pip install -r requirements-dev.txt
```
*(Для работы только приложения без запуска тестов достаточно `pip install -r requirements.txt`)*

### 4. Применение миграций

Миграция уже включена в репозиторий в каталоге `reviews/migrations/`. Примените её:

```bash
python manage.py migrate
```

### 5. Создание суперпользователя (для доступа к админке)

```bash
python manage.py createsuperuser
```
Следуйте подсказкам в терминале (введите имя пользователя, email и пароль).

### 6. Запуск сервера разработки

```bash
python manage.py runserver
```

После запуска откройте в браузере:
- **Список отзывов и форма добавления:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/) (или [http://127.0.0.1:8000/reviews/](http://127.0.0.1:8000/reviews/))
- **Панель администратора:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

Остановка сервера: `Ctrl+C`.

---

## Запуск тестов

Для запуска полного набора автоматических тестов выполните:

```bash
pytest -v
```

Все тесты проверяют сценарии в изолированной базе данных:
- Перенаправление с корневого маршрута `/` на `/reviews/`;
- Рендеринг существующих отзывов через ORM;
- Успешная отправка формы с редиректом 302 (PRG);
- Отклонение пустых строк и строк из пробелов со статусом 400;
- Проверка максимальной длины имени автора;
- Экранирование спецсимволов и защита от XSS;
- Проверка обязательности CSRF-токена (403 при отсутствии);
- Доступ и поиск по автору в админке;
- Сохранение данных в базе данных SQLite.

---

## Структура проекта

| Каталог / Файл | Назначение |
| --- | --- |
| [manage.py](manage.py) | Точка входа для команд управления Django (`runserver`, `migrate` и т.д.) |
| [config/settings.py](config/settings.py) | Настройки проекта (приложения, middleware, шаблоны, SQLite) |
| [config/urls.py](config/urls.py) | Главная маршрутизация проекта |
| [reviews/models.py](reviews/models.py) | Модель отзыва `Review` (`author`, `text`, `created_at`) |
| [reviews/forms.py](reviews/forms.py) | Форма `ReviewForm` с валидацией пробелов и пустых строк |
| [reviews/views.py](reviews/views.py) | Обработка GET и POST, паттерн Post/Redirect/Get |
| [reviews/urls.py](reviews/urls.py) | Маршруты приложения отзывов |
| [reviews/admin.py](reviews/admin.py) | Настройка панели администратора и поиска по автору |
| [reviews/migrations/](reviews/migrations/) | Миграции базы данных приложения |
| [reviews/templates/reviews/](reviews/templates/reviews/) | HTML-шаблоны гостевой книги |
| [reviews/static/reviews/](reviews/static/reviews/) | CSS-стили интерфейса |
| [tests/test_reviews.py](tests/test_reviews.py) | Набор тестов `pytest` |
| [pytest.ini](pytest.ini) | Конфигурация для запуска `pytest` |
| [requirements.txt](requirements.txt) | Основные зависимости проекта |
| [requirements-dev.txt](requirements-dev.txt) | Зависимости для разработки и тестирования |
