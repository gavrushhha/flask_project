# Инструкция по запуску проекта

## Быстрый старт

1. Активировать виртуальное окружение:
```bash
source venv/bin/activate
```

2. Установить зависимости из requirements.txt:
```bash
pip install -r requirements.txt
```

3. Запустить сервер:
```bash
uvicorn main:app --reload
```

4. Открыть в браузере:
```
http://localhost:8000
```


## API Документация

После запуска доступна по адресам:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

## Запуск тестов

```bash
pytest test_main.py -v
