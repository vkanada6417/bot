import telebot
from config import *
from logic import *
import io
import sqlite3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Я бот, который может показывать города на карте. Напиши /help для списка команд.")

@bot.message_handler(commands=['help'])
def handle_help(message):
    help_text = """
    Доступные команды:
    /start - Начать работу с ботом.
    /help - Показать список доступных команд.
    /remember_city <название_города> - Сохранить город в ваш список.
    /show_city <название_города> <цвет_маркера> - Показать карту с указанным городом и цветом маркера.
    /show_my_cities <цвет_маркера> - Показать карту со всеми сохраненными городами.
    /show_features - Показать карту с различными географическими объектами.
    """
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(commands=['show_city'])
def handle_show_city(message):
    # Разбираем сообщение на название города и цвет маркера
    parts = message.text.split(maxsplit=2)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Пожалуйста, укажите название города.")
        return
    city_name = parts[1].strip()
    marker_color = parts[2].strip() if len(parts) > 2 else 'blue'

    # Создаем карту с одним городом
    try:
        map_buffer = manager.create_graph([city_name], marker_color=marker_color)
        bot.send_photo(message.chat.id, photo=map_buffer)
    except Exception as e:
        bot.send_message(message.chat.id, f"Не удалось найти город {city_name}. Убедитесь, что название написано правильно.")

@bot.message_handler(commands=['remember_city'])
def handle_remember_city(message):
    user_id = message.chat.id
    city_name = message.text.split(maxsplit=1)[-1].strip()
    if not city_name:
        bot.send_message(message.chat.id, "Пожалуйста, укажите название города.")
        return

    if manager.add_city(user_id, city_name):
        bot.send_message(message.chat.id, f'Город {city_name} успешно сохранен!')
    else:
        bot.send_message(message.chat.id, 'Такого города я не знаю. Убедись, что он написан правильно!')

@bot.message_handler(commands=['show_my_cities'])
def handle_show_visited_cities(message):
    user_id = message.chat.id
    cities = manager.select_cities(user_id)
    if cities:
        # Получаем цвет маркера из сообщения (по умолчанию синий)
        marker_color = message.text.split(maxsplit=1)[-1].strip() if len(message.text.split()) > 1 else 'blue'
        try:
            map_buffer = manager.create_graph(cities, marker_color=marker_color)
            bot.send_photo(message.chat.id, photo=map_buffer)
        except Exception as e:
            bot.send_message(message.chat.id, "Произошла ошибка при создании карты.")
    else:
        bot.send_message(message.chat.id, "У вас нет сохраненных городов.")
@bot.message_handler(commands=['cities_by_country'])
def handle_cities_by_country(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Укажите название страны.")
        return
    country = parts[1].strip()
    cities = manager.get_cities_by_country(country)
    if cities:
        map_buffer = manager.create_graph(cities)
        bot.send_photo(message.chat.id, photo=map_buffer)
    else:
        bot.send_message(message.chat.id, f"Городов из страны {country} не найдено.")
@bot.message_handler(commands=['cities_by_density'])
def handle_cities_by_density(message):
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        bot.send_message(message.chat.id, "Укажите минимальную и максимальную плотность населения.")
        return
    min_density = float(parts[1].strip())
    max_density = float(parts[2].strip()) if len(parts) > 2 else None
    cities = manager.get_cities_by_population_density(min_density, max_density)
    if cities:
        map_buffer = manager.create_graph(cities)
        bot.send_photo(message.chat.id, photo=map_buffer)
    else:
        bot.send_message(message.chat.id, "Городов с такой плотностью населения не найдено.")


@bot.message_handler(commands=['time'])
def handle_time(message):
    city_name = message.text.split(maxsplit=1)[-1].strip()
    if not city_name:
        bot.send_message(message.chat.id, "Укажите название города.")
        return
    time_info = manager.get_time_in_city(city_name)
    bot.send_message(message.chat.id, time_info)

@bot.message_handler(commands=['show_features'])
def handle_show_features(message):
    # Создаем карту с географическими объектами
    try:
        map_buffer = manager.create_map_with_features()
        bot.send_photo(message.chat.id, photo=map_buffer)
    except Exception as e:
        bot.send_message(message.chat.id, "Произошла ошибка при создании карты.")

if __name__ == "__main__":
    manager = DB_Map(DATABASE)
    bot.polling()