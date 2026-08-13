![Python](https://img.shields.io/badge/Python-3.11-blue)
![License](https://img.shields.io/badge/License-MIT-green)

# 🕵️ OSINT Framework

Инструмент для поиска информации в открытых источниках.

## Возможности

- 🔍 Поиск по email (утечки, соцсети, Gravatar)
- 👤 Поиск по нику (50+ платформ)
- 📱 Поиск по телефону
- 🌐 Поиск по IP (геолокация, провайдер)
- 🤖 Telegram OSINT боты

## Технологии

- Python 3.11
- requests, beautifulsoup4

## Установка

```bash
git clone https://github.com/Oncillaa/osint-framework.git
cd osint-framework
pip install -r requirements.txt
python osint_framework.py
```

⚠️ Только для легального использования

## 🔧 Как это работает

1. Выбираешь тип поиска (email, ник, телефон, IP, домен)
2. Программа отправляет запросы в открытые источники
3. Результаты собираются и выводятся
4. Опционально — сохранение отчёта

## ⚠️ Ограничения

- Некоторые API требуют ключи
- Google может блокировать частые запросы
- Не все источники доступны из России

## 🔜 Планы

- [ ] Добавить больше источников
- [ ] Telegram интеграция
- [ ] Веб-интерфейс
